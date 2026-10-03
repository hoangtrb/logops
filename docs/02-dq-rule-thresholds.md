# 02 · Data-Quality Rule Thresholds: Why, Sources, Verification

> Vietnamese: [02-dq-rule-thresholds.vi.md](02-dq-rule-thresholds.vi.md) · Rules live in
> `src/logops/data_platform/quality.py` · Results: [02-data-quality-report.md](02-data-quality-report.md)
> **Last verified:** 2026-10-03. Every number below was checked against the code (§6) and re-run
> on the real data through the rule engine itself. If a threshold changes, update this file too.

Each number answers three questions: **where it's used**, **why that value**, and **its source**.

**Source types**

| Mark | Source | Meaning |
|---|---|---|
| 📊 | Data profile | Measured directly on this dataset |
| 📘 | Industry / regulation | An external industry standard or legal text |
| 📐 | Definition / logic | True by definition, no threshold needed (e.g. a rate lies in 0–1) |
| 📝 | Project decision | Written in the spec; a deliberate choice |
| 🧪 | Test design | A value chosen to sit clearly on one side of a threshold |

**Overview:** 69 rules = 50 key rules (generated from `schema.py`) + 19 value rules. By severity:
43 *errors*, 26 *warnings*.

---

## 1. Key rules (`pk_unique`, `fk_missing`, `fk_orphan`)

These rules have **no numeric threshold**: a key is either duplicated, empty or dangling, or it isn't.

| Number / choice | Why | Source |
|---|---|---|
| `pk_unique` and `fk_orphan` are **errors** | A duplicate key or a key pointing to a non-existent record is *wrong* data | 📝 |
| `fk_missing` is a **warning** | An empty ID is *missing information*; the row still counts toward fleet totals | 📝 See `00-analytical-approach` §3.4 |
| 3 sample keys per rule (`SAMPLE_SIZE = 3`) | Enough for a reader to look up the bad rows without bloating the report | 📝 Spec acceptance criterion |

## 2. Value rules (`range`)

Ranges written "within a–b" use `BETWEEN`, which is **inclusive**: an MPG of exactly 3 or 12 is valid.

| Threshold | Table | Why | Source | Evidence (📊) |
|---|---|---|---|---|
| MPG within **3–12** | `trips`, `driver_monthly_metrics` | Class 8 tractor-trailers run at about 6 MPG. 3–12 spans half to double that: it only catches *impossible* values (typos, wrong units), not trucks that are merely inefficient | 📘 U.S. DOE, Alternative Fuels Data Center + 📝 | Trips: 5.5–7.5 (median 6.5). Monthly table: 6.01–7.07. 0 violations. A narrower band was rejected: it would flag genuinely poor trucks, which is the `optimize` module's job |
| Trip distance, duration, fuel **> 0**; idle time **≥ 0** | `trips` | A completed trip can't be 0 miles or 0 hours; zero idling is valid | 📐 | Minimums: 90 miles, 1.4 h, 12 gallons |
| Trips per month **≥ 0** | `driver_monthly_metrics` | A count can't be negative | 📐 | Minimum: 5 |
| Revenue, weight, pieces **> 0** | `loads` | A real load always has a size and a price | 📐 | Minimums: $125.93, 10,000 lbs, 1 piece |
| Fuel surcharge, accessorials **≥ 0** | `loads` | No surcharge is valid | 📐 | 32,186 loads have `accessorial_charges = 0` |
| Gallons, fuel price **> 0** | `fuel_purchases` | A fuel purchase always has a quantity and a price | 📐 | 50–200 gallons; $3.15–$5.00/gallon |
| Labor hours, costs, downtime **≥ 0** | `maintenance_records` | Negative is impossible; zero is valid | 📐 | 0 violations |
| Damage costs, claim **≥ 0** | `safety_incidents` | Negative is impossible; zero is valid (e.g. no cargo damage) | 📐 | 122 incidents have `cargo_damage_cost = 0` |
| Detention minutes **≥ 0** | `delivery_events` | No waiting is normal | 📐 | 22,472 events with 0 minutes; maximum 239 minutes |
| On-time rate within **0–1** | `driver_monthly_metrics` | A rate lies in 0–100% by definition | 📐 | 0.0–0.833 |
| Truck utilization within **0–1**, as a **warning** | `truck_utilization_metrics` | Normally ≤ 100%. A warning because > 100% may come from the definition (e.g. dividing by a standard 8–10 h day while trucks run multiple shifts), not necessarily wrong data | 📐 + 📝 | **436 months (13.2%)** above 1; median 0.833; p95 1.129; max 1.484 |

## 3. Consistency rules

| Number | Rule | Why | Source | Evidence (📊) |
|---|---|---|---|---|
| **1%** tolerance | `amount_mismatch` (fuel, maintenance, incidents) | A total must equal its parts: gallons × price; labor + parts; vehicle + cargo damage. Some slack is needed for rounding to the cent. 1% catches material errors (e.g. billing 120 gallons for 100) but ignores rounding. For incidents the 1% is of `claim_amount`; for the other two, of `total_cost` | 📝 Spec | Largest gap: $0.005 (0.003%) for fuel; maintenance and incidents show only floating-point noise (~10⁻¹²). 0 violations |
| Idle time **≤ trip duration** | `idle_exceeds_duration` | Idle time is *part* of the trip's time | 📐 | **7,450 trips (8.7%)** violate it, by a median of 3.1 h and up to 10.5 h |
| Delivery **after** pickup, actual and scheduled | `time_order` | Goods can't be delivered before they're picked up. The delivery is compared with the latest pickup on the same trip | 📐 | **486** trips (actual), **175** trips (scheduled) |
| Termination **not before** hire | `time_order` | Required order | 📐 | 0 violations |
| City/state among the **25 reference pairs** | `geo_mismatch:location_state` (fuel, incidents, delivery events) | The reference holds places *known to be real*: the 50 facilities plus the origins and destinations of the 58 lanes, which together give 25 pairs. No city appears under two states. A warning because the state column is unusable but the city column is fine | 📊 | Fuel **95.3%** wrong state (e.g. "Denver, TX"); incidents **95.9%**; delivery events **0%** |
| Event city = its facility's city | `geo_mismatch:facility_id` | An event at facility X must take place in facility X's city | 📐 | **96.6%** mismatch. The cross-check shows `location_city` matches the lane endpoint 100% and `facility_id` only 3.4%, so `facility_id` is the wrong column |

*The hiring-age rule was removed on 2026-10-03 at the project owner's request: the project focuses on operational productivity and quality, not HR compliance.*

## 4. Cross-checks in the report (`dq_report.py`)

| Number | Why | Source | Evidence (📊) |
|---|---|---|---|
| Drift **> 2%** between the monthly tables and recomputed values (trips, miles, revenue; maintenance cost) | Monthly tables may be rounded. 2% allows rounding but catches a month with missing or extra trips | 📝 Spec | 0% of months drift, for both the driver and truck tables |
| Maintenance event counts must match **exactly** | Counts have no rounding error | 📐 | 100% match |
| A **$1 floor** when comparing maintenance cost (`greatest(maintenance_cost, 1)`) | A month without maintenance has cost 0, so a 2% × 0 = 0 tolerance would flag any difference, even one cent. The $1 floor keeps a minimum tolerance | 📐 | — |
| The **±120-minute** window behind `on_time_flag` | **Not a threshold chosen by the project**: it's the definition *discovered* in the data. Windows of 60, 90, 119, 120 and 121 minutes were tested; only 120 matches 100% | 📊 | Agreement: 72.31% at 60 min; 86.10% at 90; 99.53% at 119; **100%** at 120; 99.71% at 121 |

## 5. Numbers in the tests

Test values sit **clearly on one side** of each threshold, never right at the boundary, so a test
checks what the rule *means* independent of rounding. "Clean" values are close to the real data so
the fixtures look realistic.

### `test_quality_values.py`

| Case | Clean value | Defective value | Why |
|---|---|---|---|
| MPG | 6.5 (500 miles ÷ 77 gallons ≈ 6.49, self-consistent) | 40 | 6.5 is the real median; 40 is far above the 12 ceiling, like a typo or unit mix-up |
| Idle time | 2 h on a 10 h trip | 5 h on a 3 h trip | 2 h over, close to the real median excess (3.1 h) |
| Load revenue | 1,000 | −5 | Negative is plainly impossible |
| Fuel amount | 100 gal × $4 = 400 | 480 | 20% off, 20 times the 1% tolerance |
| Maintenance amount | 100 + 50 = 150 | 300 | 100% off |
| Incident claim | 10 + 5 = 15 | 99 | 560% off |
| Fuel location | Atlanta, GA | Atlanta, AZ | Mirrors the real defect: right city, wrong state |
| Driver | Hired 2015, left 2020 | Hired 2015, left 2010 | Left five years before being hired |
| Truck utilization | 0.7 | 1.4 | 0.7 is near the median (0.83); 1.4 is near the real maximum (1.484) |
| Delivery events | Pickup 08:00, delivery 12:00 | Pickup 12:00, delivery 08:00 | Order reversed by 4 h, in both actual and scheduled times |
| Event facility | Event in Atlanta, facility F1 in Atlanta | Event in Chicago, facility F1 in Atlanta | Chicago, IL is itself a valid pair, so the test catches only the *facility* error, not a *state* error |

**Rules without their own test** (same logic as tested rules, but no dedicated defective fixture row yet):

| Rule | Tables |
|---|---|
| `range` | `fuel_purchases`, `maintenance_records`, `safety_incidents`, `delivery_events`, `driver_monthly_metrics` |
| `geo_mismatch:location_state` | `safety_incidents`, `delivery_events` |

Every rule *type* (`range`, `amount_mismatch`, `time_order`, `geo_mismatch`, `idle_exceeds_duration`)
has at least one test, which meets the todo's "one test per rule" criterion. Covering each table
listed above would take about 15 minutes if wanted.

### `test_quality_keys.py`

| Row | Deliberate defect | Expected result |
|---|---|---|
| `T1 → D1` | None | Empty `dq_issues` |
| `T2` (2 rows) | Duplicate primary key | Both rows `pk_unique` |
| `T3 → NULL` | Empty foreign key | `fk_missing:driver_id` |
| `T4 → D9` | `D9` doesn't exist in `drivers` | `fk_orphan:driver_id` |
| `D1, 2022-02-01` (2 rows) | Duplicate two-column primary key | Both rows `pk_unique`; the sample key shows `D1\|2022-02-01` |

### `test_ingest.py` and `test_schema.py`

| Value | Why |
|---|---|
| `"about 700"` instead of `697` in an integer column | Text in a numeric column: exactly the defect that silent type guessing would hide |
| Renaming the column `base_rate_per_mile` → `rate` | A wrong header must stop the build, never load shifted columns |
| An empty `typical_distance_miles` for `RTE00004` | Must become NULL, not 0 |
| `2022-01-01 20:58:55.918185` | Taken from the first row of the real data: checks the microseconds survive |
| `17:41:02.5` | A fraction shorter than 6 digits must still parse correctly (as 500,000 microseconds) |

These two sample events also fit the ±2-hour definition: the first is 179 minutes late, so
`on_time_flag = False`; the second is 19 minutes early, so `True`.

### `test_dq_report.py`

The sample figures (e.g. revenue $298.6M, MPG 6.5) are close to the real ones so they're easy to
recognize. The test checks **formatting** only (commas and dots per language, escaped `|`), not
business values.

## 6. Verification table: number ↔ location in code

Checked on 2026-10-03 against the files in `src/logops/data_platform/`.

| Number | Location | Match |
|---|---|---|
| `SAMPLE_SIZE = 3` | `quality.py:18` | ✅ |
| The 25 reference pairs (facilities ∪ lane origins ∪ lane destinations) | `quality.py:40–43` | ✅ |
| MPG 3–12, `> 0` / `< 0` for trips | `quality.py:64–65` | ✅ |
| Idle > trip duration | `quality.py:67` | ✅ |
| Loads `> 0` / `< 0` | `quality.py:72–73` | ✅ |
| Fuel `> 0`; 1% tolerance | `quality.py:75`, `quality.py:80` | ✅ |
| Maintenance `< 0`; 1% tolerance | `quality.py:87`, `quality.py:93` | ✅ |
| Incidents `< 0`; 1% of `claim_amount` | `quality.py:99`, `quality.py:105` | ✅ |
| Detention minutes `< 0` | `quality.py:108` | ✅ |
| Delivered before pickup (actual, scheduled) | `quality.py:53`, `quality.py:109–122` | ✅ |
| Event facility | `quality.py:129` | ✅ |
| Terminated before hired | `quality.py:133` | ✅ |
| Driver monthly table: rate 0–1, MPG 3–12, trips ≥ 0 | `quality.py:138–139` | ✅ |
| Utilization 0–1 (warning) | `quality.py:145–146` | ✅ |
| 2% monthly drift; exact maintenance count; $1 floor | `dq_report.py:80–96` | ✅ |
| ±120-minute window; more than 120 minutes early | `dq_report.py:103`, `dq_report.py:107` | ✅ |

*Line numbers may shift if the files are edited after the verification date.*

---

## References

- U.S. Department of Energy, Alternative Fuels Data Center. *Average Fuel Economy by Major Vehicle Category*.
