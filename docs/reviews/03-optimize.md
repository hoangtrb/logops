# Review · Module 3: `optimize`

> CRISP-DM phases 4–5 · Vietnamese: [03-optimize.vi.md](03-optimize.vi.md) · Spec:
> [SPEC-optimize.md](../../SPEC-optimize.md) · Detailed results:
> [05-evaluation.md](../05-evaluation.md), [04-data-process-improvements.md](../04-data-process-improvements.md)
> · Summary: [SUMMARY.md](../SUMMARY.md)
> **Status:** completed 2026-10-03, not yet committed · **Rule:** only verified facts.

## 1. Scope: from the original plan to the final one

Before writing the spec, each lever's signal was checked. The test: the signal must **persist**
between 2022–23 and 2024. Most levers in the original plan failed it.

| Lever | Check result | Decision |
|---|---|---|
| Fleet size | Busiest day 82 trucks, p99 78; fleet of 120 | ✅ P1 |
| Lane profitability + fuel surcharge | Lane margins persist (correlation 0.946); surcharge is fixed per lane, not tied to fuel price | ✅ P2 |
| Data gaps → process | Measured impact | ✅ P4 |
| ML delay-risk model | Correlation across years 0.01–0.09 | ❌ Dropped (the AUC criterion in `docs/01` is withdrawn) |
| MPG by driver/truck | 0.003 / −0.068 | ❌ Dropped |
| Idling, fuel price by location, customer profitability, replacing old trucks | Noise or not persistent | ❌ Dropped |
| Bottlenecks (maintenance shop, receiving dock) | Signal exists | ❌ Dropped by the project owner: not practical enough |
| Load consolidation, detention billing | Signal exists | ❌ Dropped by the project owner: urgent loads can't wait; billing not reasonable |

## 2. Outputs vs the spec

| Output | Delivered | Evidence |
|---|---|---|
| P1 `fleet_plan`, `disposal_tiers`, `cross_check` | ✅ 0/5/10/20% scenarios; tiered disposal; a shortfall brings `Maintenance` trucks back first | 7 fixture tests; integration test: no scenario leaves the fleet short |
| P2 `lane_pricing` (`classify`, `scenarios`, `indexed_surcharge`) | ✅ 4 lane groups, break-even driver cost, S1/S2 with 5%/10%/no cap, S3 simulation | 7 fixture tests; reconciles with the fleet KPIs |
| P4 data gaps | ✅ 6 gaps, cost of not doing (measured) vs cost of doing (cited) | 4 tests; integration test checks sources are present |
| P5 recommendations + docs | ✅ `recommendations` table in the warehouse; `logops optimize`; generated `docs/04`, `docs/05` EN/VI | Integration test: measured total = sum of the measured tiers |
| Document updates | ✅ `CAPABILITY-MAP`, `00-analytical-approach` §5–§7, `docs/01` §5 | — |

**Tests:** 23 new; 99 in total, all passing; `ruff` clean. Build 8.3–8.4 s.

## 3. Results

**Against the target of $1.04M per year** (3% of measured operating cost):

| Type | Per year | % of target |
|---|---:|---:|
| **Measured saving** (maintenance of the 28 trucks that never ran) | $466,949 | 45% |
| Upper bound: surcharge S1 + linehaul S2 (5% cap) + review of the 12 lowest-mileage trucks | $2,646,153 | 255% |

**P1 – fleet:** 80 / 84 / 88 / 96 trucks needed at 0 / 5 / 10 / 20% growth, vs 120 owned and 92 in
use. Dispose of 13 `Inactive` trucks ($219,927/year) and 15 `Maintenance` trucks ($247,022/year). At
+20%, bring 4 `Maintenance` trucks back to service. Availability 97.7%.

**P2 – lanes:**

| Group | Lanes | Margin range |
|---|---:|---|
| Core (high margin, high volume) | 12 | 65.8–72.7% |
| Profitable niche (high margin, low volume) | 17 | 66.1–72.2% |
| Reprice (low margin, high volume) | 18 | 50.4–65.0% |
| Review (low margin, low volume) | 11 | 54.8–65.2% |

- No lane loses money on measured cost. The weakest lane loses money if driver cost exceeds
  **$0.857/mile**.
- S1 surcharge standardization: +$0.96M/year (29 lanes).
- S2 with a 5% / 10% / no cap: +$1.50M / +$2.81M / +$5.99M per year.
- Median break-even volume loss: 6.9% / 12.9% / 19.9%.
- S3, index-linked surcharge (revenue-neutral, base $2.318/gallon): earns more when prices are high
  (2022: +$1.89M), less when they're low (2024: −$1.58M). Not counted as a saving.

**P4 – data:**
- 5.57M gallons bought but not reconciled with consumption: $7.24M/year *unexplained*, not proven loss.
- Industry benchmark for card misuse (2–5% of fuel spend): $0.64–1.59M/year.
- Telematics for 92 trucks: $25,147–65,013/year. It pays for itself if it prevents **0.2%** of fuel spend.

## 4. Findings and caveats

- **"Profitable niche" earns more revenue than "Core"** ($104.4M vs $80.9M over 3 years). Volume is
  measured in trips, and the niche lanes are long, with high revenue per trip.
- **The busiest day (82 trucks) exceeds the p99 need (80).** 11 of 1,096 days (about 4 per year) needed
  more than 80 trucks, coverable by short-term rental. Never running short would take 84 trucks.
- **Uncapped S2 is theoretical:** some lanes would need a 44% linehaul increase, which is why the
  headline uses the 5% cap.
- **Margins are before driver pay.** If pay is per mile, the bottom lanes can only get worse, so the
  "reprice" conclusion holds.

## 5. Limits, and what wasn't done

| Item | Reason |
|---|---|
| Resale value, insurance, parking of disposed trucks | Not in the data; labelled an unquantified benefit |
| Demand elasticity when prices rise | Not in the data; replaced by the break-even volume loss |
| Cost of tier-1 measures (process, configuration) | Internal effort on existing systems; no price claimed |
| Telematics prices | Indicative public figures (GPS Insight), to be replaced by vendor quotes |

## 6. Handed over to the next modules

`insights`, `dashboard` and `reports` read the `recommendations` table and the functions in
`src/logops/optimize/`. The dashboard needs a growth slider (P1), a linehaul-cap slider (P2), and a
clear distinction between *measured*, *upper bound* and *unexplained*.

## 7. Reproduce

```powershell
python -m uv run logops build                  # recommendations table + docs/04, docs/05
python -m uv run logops optimize --growth 10   # recommendations at +10%
python -m uv run pytest tests/optimize         # this module's 23 tests
```
