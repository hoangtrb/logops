# Review · Module 3: `analysis`

> CRISP-DM phases 2–3 (descriptive and diagnostic) · Vietnamese: [03-analysis.vi.md](03-analysis.vi.md)
> · Spec: [SPEC-analysis.md](../../SPEC-analysis.md) · Results: [03-analysis-insights.md](../03-analysis-insights.md)
> · Summary: [SUMMARY.md](../SUMMARY.md)
> **Status:** completed 2026-10-03, not yet committed · **Rule:** only verified facts.

## 1. Context

This module **takes the place of `optimize`**: the optimize work done so far is parked on branch
`feature/optimize` and will be redone later, building on the findings here. Scope agreed with the
project owner:
- Profit is analysed **the way businesses track it** (periods, profit bridge, unit economics, business
  dimensions), not by weekday or season.
- **No external data**, not even coordinates.
- Anything unclear is dropped: the empty-running ↔ fuel hypothesis is out; fuel is statistics only.
- The dataset author's notebook [Route_optimization](https://www.kaggle.com/code/yogape/route-optimization)
  is used as a reference: what's right is kept, what's wrong is fixed.

## 2. Outputs vs the spec

| Output | Delivered | Evidence |
|---|---|---|
| P1 P&L by month/quarter/year, vs previous, vs last year, YTD | ✅ `profit.pnl` | Totals match the fleet KPIs at all 3 period levels (integration test) |
| P2 profit bridge | ✅ `profit.bridge`, 6 parts | Parts add up exactly to the total change (test) |
| P3 unit economics | ✅ per mile, trip, truck-week | — |
| P4 business dimensions + customer concentration | ✅ 8 dimensions via `kpi()`; HHI, top 10/20, Pareto | Groups add up to the fleet (test) |
| P5 margin vs fuel price | ✅ monthly, with correlation | — |
| F1 fuel by month/quarter/year (statistics only) | ✅ | — |
| C1–C2 trucks per day, capacity by service level | ✅ with the evidence that peak timing can't be forecast | p95 ≤ p99 ≤ max ≤ trucks in use (test) |
| N1–N4 3×3 matrix, headhaul/backhaul balance, changed start points, notebook comparison | ✅ | Loads out = loads in (test); 58 lanes |
| Commentary | ✅ 12 EN/VI rules, 12 thresholds with reasons and sources | Tests: templates have no digits; levels follow thresholds |
| Command, docs | ✅ `logops insights`, `analysis_bundle()`, generated `docs/03-analysis-insights` | Docs are deterministic (test) |

**Tests:** 12 new (7 unit, 5 integration); 93 in total, all passing; `ruff` clean. Build 16.3–17.6 s
(target < 30 s).

## 3. Key findings

| Topic | Finding | Level |
|---|---|---|
| **Profit** | Margin rose 62.7% → 67.2% (2022 → 2024). Revenue per mile flat ($2.444 → $2.447). Falling fuel prices account for **+$4.12M of +$4.42M (93%)** | act |
| | Monthly margin moves against the fuel price (correlation −0.92), because the surcharge is fixed | watch |
| | Volume flat (28,589 → 28,656 trips); segments earn the same margin (65.5–65.8%) | info |
| | Texas contributes most ($23.33M, 12%); margins by state 56.5–69.9% | info |
| | No customer concentration risk: largest customer 0.6%, HHI 50 | info |
| **Fuel** | Every year, gallons bought exceed gallons recorded as burned (1.28–1.30×), not reconciled | watch |
| **Fleet** | 95% of days need ≤ 73 trucks, 99% ≤ 75, busiest day 80; 92 in use, 120 owned | watch |
| | Peak days can't be predicted (day-to-day correlation 0.18; by quarter 0.04; yearly average 66.0–66.2) | info |
| **Network** | 33% of loads (28,178) end where there's no return load; 16 of 20 cities imbalanced by over 20%; stable (0.997). Los Angeles and Indianapolis only receive | act |
| | In 95.4% of transitions a truck starts its next trip in another city; that movement isn't recorded | watch |

## 4. Comparison with the notebook

| Notebook | Issue | Fixed |
|---|---|---|
| Lane matrix | Fuel at a fixed $3.80 (actual 3.899); revenue without surcharges; mean of ratios | Real costs, sum ÷ sum |
| Headhaul/backhaul | Summing net loads over all cities always gives 0 → repositioning cost always $0 | Inbound surplus measured per city |
| Seasonality | Counted per month, so 31-day months always "peak" | Counted per day: no seasonality |
| Empty miles | 15% and $0.85/mile assumed | Frequency counted only; no miles |
| Customer concentration | — | Kept; HHI added |

## 5. Caveats for presenting

- **The yearly margin here (62.7% → 67.2%) differs from the 63.2% → 67.6% mentioned earlier in
  conversation** because the P&L books every cost on its date, including the $1.40M maintenance of the
  28 trucks that never ran. The P&L figure is the correct one.
- Profit is **contribution before driver pay and overhead**.
- The HHI thresholds come from US merger guidelines and are **applied by analogy** to the customer
  portfolio.

## 6. Dropped (project owner's decisions)

Weekday, seasonality, *operating ratio*, empty miles, extra coordinates, the empty-running ↔ fuel
hypothesis, savings figures.

## 7. Handed over

- **Dashboard** reads `analysis_bundle()`: commentary, P&L, bridge, states, lane matrix, network
  balance, fleet capacity.
- **Optimize** (redone from `feature/optimize`): the network imbalance and changed start points are new
  inputs for backhaul matching; the lane matrix feeds repricing.

## 8. Reproduce

```powershell
python -m uv run logops build              # generates docs/03-analysis-insights
python -m uv run logops insights --lang en # prints the commentary
python -m uv run pytest tests/analysis     # this module's 12 tests
```
