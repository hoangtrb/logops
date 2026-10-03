# Review · Module 2: `metrics`

> CRISP-DM phase 3 · Vietnamese: [02-metrics.vi.md](02-metrics.vi.md) · Spec:
> [SPEC-metrics.md](../../SPEC-metrics.md) · KPI definitions:
> [03-kpi-definitions.md](../03-kpi-definitions.md) · Summary: [SUMMARY.md](../SUMMARY.md)
> **Status:** completed 2026-10-03, not yet committed · **Rule:** only verified facts.

## 1. Outputs vs the spec

| Output in the spec | Delivered | Evidence |
|---|---|---|
| O1. Three base views | ✅ `trip_economics` (85,410 rows), `delivery_performance` (170,820), `truck_economics` (120) | Row counts match the source tables; cost-allocation tests on fixture data |
| O2. `kpi()` function | ✅ 21 KPIs; groups by month, lane, customer, customer type, truck, driver, city; date filter; on-time window as a parameter | 13 tests on hand-computable fixture data |
| O3. `logops kpi` command | ✅ `--by`, `--from`, `--to`, `--window`, `--kpis` | Run on the real data; CLI tests |
| O4. Generated KPI doc | ✅ `docs/03-kpi-definitions` EN/VI, written by `logops build` | Test: all 21 KPIs, both languages, deterministic |
| Reviews + summary | ✅ This file, `01-data-platform` and `SUMMARY` | — |

## 2. Success criteria

| Criterion | Result | Evidence |
|---|---|---|
| 1. Matches the DQ report | ✅ Revenue $298,621,428.94; measured cost $103,976,737.14; MPG 6.448; on time 44.6% | Integration test against the source tables |
| 2. Groups + "Unattributed" = fleet total | ✅ | Tests on real data (5 groupings) and fixture data (6 groupings) |
| 3. On-time window is a parameter | ✅ 120 minutes reproduces `on_time_flag` | Test: 0 min → 0%, 200 min → 100% on fixture data |
| 4. Date filter is correct | ✅ 2024: revenue and maintenance cost match the source tables | Integration test |
| 5. Tests + ruff | ✅ 29 new tests; 76 in total, all passing; ruff clean | `pytest`, `ruff check` |
| 6. Build ≤ 5 s slower | ✅ 6.6–7.4 s after the module, vs 8.0 s on the last build before it (timings vary between runs) | Timing printed by `logops build` |

## 3. Fleet KPIs (Jan 2022 – Jan 2025)

| Area | KPI | Value |
|---|---|---|
| Cost | Measured cost per mile | $0.851 (fuel 0.783; maintenance 0.047; incidents 0.022) |
| | Revenue per mile | $2.445 |
| | Contribution margin (before driver pay) | 65.2%; by lane from 50.4% to 72.7% |
| | Out-of-route miles vs the lane's typical distance | 2.95% |
| Fuel | MPG | 6.448 |
| | Gallons purchased ÷ gallons burned | 1.294 (per truck: 1.20 to 1.41) |
| Delivery | On time (±120 min) / not late | 44.6% / 33.3% |
| | Average detention | 91.5 minutes per pickup or delivery; 260,607 hours in total |
| Assets | Miles per active truck-month | 36,884 |
| | Utilization (for comparison only) | 83.0% |
| | Maintenance downtime | 72,231 hours |
| Safety | Incidents per million miles; preventable share | 1.39; 37.6% |

## 4. Data evaluation: new findings in this module

| Finding | Figures | What it means |
|---|---|---|
| **28 of 120 trucks ran no trip in 3 years** | 13 `Inactive`, 15 `Maintenance`; 690 maintenance records, **$1.40M (24% of maintenance cost)**, 17,418 downtime hours | A question for `optimize`: does the fleet need these trucks? |
| Volume is nearly flat | Average 2,361 trips/month (first half of 2022) vs 2,391 (second half of 2024), +1.3% | All trips over the 3 years were run by 92 trucks (about 2% of trips have no truck ID). Peak daily demand still needs to be computed in `optimize` |
| 29% more gallons bought than burned | Uniform across trucks (1.20–1.41) | The gap is systemic, not concentrated in a few trucks. It may come from how the data was generated; there's not enough evidence to conclude fuel-card fraud |
| Customer segments are nearly identical | Contract / dedicated / spot: cost per mile $0.84 for each, on time 44.2–44.9% | Little leverage by customer type; the clearer differences are by lane (margin 50.4–72.7%) |
| $93,269 of fuel bought in Jan 2025 | No trips that month | In the "Unattributed" line; totals still reconcile |

## 5. Limits, and what wasn't done

| Item | Reason |
|---|---|
| Driver pay, net profit | Not in the data. **The 65.2% contribution margin is therefore higher than the true margin**; say so when presenting |
| Idle-time KPI, fuel price by location, by `facility_id` | No signal (see the module 1 review) |
| Truck utilization | For comparing trucks only, since some months exceed 100% |
| Date ranges that cut through a month | Fuel and maintenance are allocated by month, so whole-month or whole-year filters are the most accurate |

## 6. Handed over to module 3 `optimize`

1. **Fleet size:** keep or dispose of the 28 trucks that never ran, given nearly flat volume and peak demand. Shown on the dashboard as a recommendation for the viewer to weigh.
2. **Lane profitability:** margins from 50.4% to 72.7%; rank lanes and compute the rate change each needs.
3. **Delivery:** the delay-risk model uses `delivery_performance`.
4. **Fuel:** the remaining lever is MPG by truck and driver. The purchased-vs-burned gap is shown only as a control indicator.

## 7. Reproduce

```powershell
python -m uv run logops build                       # create the views + docs/03-kpi-definitions
python -m uv run logops kpi --by route --kpis all   # KPIs by lane
python -m uv run pytest tests/metrics               # this module's 29 tests
```
