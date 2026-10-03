# 02 · Data Understanding

> CRISP-DM phase 2 · Vietnamese: [02-data-understanding.vi.md](02-data-understanding.vi.md) ·
> Figures from [02-data-quality-report.md](02-data-quality-report.md) (generated) · Thresholds and
> sources: [02-dq-rule-thresholds.md](02-dq-rule-thresholds.md) · Table relationships: [02-data-model.md](02-data-model.md)

**In one sentence:** the data is reliable enough to analyze cost and service level, provided we
**avoid 3 columns** (state on fuel purchases and incidents, `facility_id` on delivery events) and
**exclude some rows** for specific analyses. No row is deleted.

---

## 1. What the data covers

A US freight carrier over **3 years, 2022-01-01 to 2024-12-31**: 14 tables and 549,706 rows.

| Group | Tables | Size |
|---|---|---|
| Assets and people | `trucks`, `trailers`, `drivers` | 120 trucks, 180 trailers, 150 drivers |
| Market | `customers`, `routes`, `facilities` | 200 customers, 58 lanes, 50 facilities |
| Operations | `loads`, `trips` | 85,410 loads, each with exactly one trip |
| Events | `delivery_events`, `fuel_purchases`, `maintenance_records`, `safety_incidents` | 170,820 pickups/deliveries, 196,442 fuel purchases, 2,920 maintenance jobs, 170 incidents |
| Pre-aggregated | `driver_monthly_metrics`, `truck_utilization_metrics` | 4,464 driver-months, 3,312 truck-months |

The data forms a **star schema**: `trips` at the center, linked to drivers, trucks, trailers and
loads, with the event tables around it (see the diagram in [02-data-model.md](02-data-model.md)).

## 2. Where the business stands (baselines)

| Metric | Value | What it means |
|---|---|---|
| Revenue | $298.6M | |
| Measured operating cost | $104.0M | Fuel + maintenance + claims. Driver pay isn't in the data |
| ↳ Fuel | $95.6M (**92%**) | **The biggest cost lever**: every 1% fuel saving ≈ $0.96M |
| ↳ Maintenance | $5.7M (5.5%) | |
| ↳ Safety claims | $2.7M (2.5%) | |
| Cost per mile | $0.851 | Over 122.2M miles |
| Fleet MPG | 6.45 | Normal for tractor-trailers |
| Deliveries within the ±2 h window | **44.6%** | Low: more than half of deliveries miss their window |
| Deliveries not late (≤ appointment) | 33.3% | |
| Detention hours | 260,607 h | About 1.5 h per pickup or delivery on average |
| Average truck utilization | 83.0% | |

## 3. How far the data can be trusted

| Trust level | Item | Evidence |
|---|---|---|
| ✅ **Trust** | Relationships between tables | 0 duplicate keys, 0 orphan keys in all 14 tables |
| ✅ | Money amounts | Totals equal their parts for fuel, maintenance and incidents (largest gap $0.005) |
| ✅ | Monthly aggregate tables | 100% match with values recomputed from trips, loads and maintenance |
| ✅ | No duplicates | 0 exact duplicate rows |
| ✅ | Delivery events' `location_city` | Matches the route endpoint 100% |
| ⚠️ **Use with conditions** | Empty foreign keys (~2%: driver, truck, trailer) | Missing at random (MCAR); keep for totals, exclude from rankings. See `00-analytical-approach` §3.4 |
| ⚠️ | Idle time > trip duration | 7,450 trips (8.7%): **exclude from idle-time analysis** |
| ⚠️ | Delivered before picked up | 486 trips (actual times), 175 (scheduled): exclude from transit-time analysis |
| ⚠️ | Truck utilization > 100% | 436 months (13.2%): likely a definitional effect; use to *compare* trucks, not as an absolute percentage |
| ❌ **Don't use** | State (`location_state`) on fuel purchases and incidents | 95–96% wrong state (e.g. "Denver, TX"). Use the city instead |
| ❌ | `facility_id` on delivery events | Matches the lane only 3.4% of the time, the same as random assignment. Location analysis uses `location_city` |
| ❌ | Fuel price differences by location | Average price differs by only $0.02/gallon across cities ($3.886–$3.907): **no signal** |

Overall, only **1.5% of rows** have an *error*-level issue. The 66.4% with "at least one issue"
comes mostly from the unusable columns above, not from errors in the measurements.

## 4. Key finding: what `on_time_flag` actually measures

The on-time flag **matches 100%** with the rule "*arrived within ±120 minutes of the appointment*".
Windows of 60, 90, 119, 120 and 121 minutes were tested; only 120 matches exactly. As a result:

- Arriving **up to 2 hours late still counts as on time**.
- Arriving **more than 2 hours early counts as not on time** (5.5% of events).

It's an **appointment-window compliance** measure, not a lateness measure. For a distribution
center that makes sense: a truck that turns up far too early congests the dock just like a late
one. The reports will show both views: window compliance (44.6%) and not late (33.3%).

## 5. What this changes downstream

| Module | Adjustment driven by the data |
|---|---|
| `metrics` | Cost per mile uses every row. The on-time KPI has two definitions (±2 h window, not late). Location analysis uses `location_city`, not `facility_id` |
| `optimize` · fuel | **Drop the "buy fuel where it's cheaper" lever**: there's no price signal. Focus on MPG and idling. Idle analysis excludes the 7,450 defective trips |
| `optimize` · delivery | The delay model uses the delivery's `on_time_flag` as its label (55.4% miss, so the classes are nearly balanced). Location features use `location_city` |
| `optimize` · fleet | Utilization is used to rank trucks relative to each other. The monthly tables can be used directly since they reconcile 100% |
| Driver/truck rankings | Exclude rows missing the ID; reports add an "Unattributed" line so totals always reconcile |

## 6. Success criteria check (`docs/01` §5)

| Criterion | Before | After measuring | Verdict |
|---|---|---|---|
| Savings ≥ 3% of operating cost | Provisional | 3% × $104.0M = **≥ $3.1M over 3 years** (≈ $1.04M/year) | Keep. Conservative because driver pay is missing. Fuel alone is 92%, so a 3.3% fuel reduction meets the target |
| Delay model ROC-AUC ≥ 0.70 | Provisional | Classes nearly balanced (55.4% / 44.6%), so AUC is an appropriate metric | Keep |
| DQ report covers 100% of tables | Provisional | 14/14 tables, 69 rules | **Met** |

`docs/01` §5 has been updated to match this table.

## 7. Interview talking points

1. **"I check before I trust."** 69 rules run automatically on every build; bad data is flagged,
   not deleted, and every threshold has a documented source.
2. **"I found what the metric really means."** The on-time flag is a ±2-hour window, not "not
   late". Without that, a report to the director would misstate the service level.
3. **"I know which data not to use, and why."** The facility ID on events is random, so detention
   by location must use the city; fuel prices don't vary by location, so I don't promise a saving
   that isn't there.
4. **"Fuel is 92% of measured cost."** That's the first place to look for savings.
