# Spec: analysis

> Module 3 of 6 (reordered 2026-10-03: analysis first, `optimize` later, parked on branch
> `feature/optimize`) · CRISP-DM phases 2–3: **descriptive and diagnostic** · Vietnamese:
> [SPEC-analysis.vi.md](SPEC-analysis.vi.md) · Input: module 2's KPI layer · Reference: the dataset
> author's notebook [Route_optimization](https://www.kaggle.com/code/yogape/route-optimization)

## Objective

Answer **"what is happening and why"** the way businesses track their results, then **generate written
commentary from rules**. The dashboard (module 4) shows the figures and the commentary. The `optimize`
module (module 5) takes the findings here as input.

**Principles** (agreed with the project owner)
- Only figures that are in the data. **No external data**, not even coordinates: imprecise numbers are a
  distortion.
- Anything unclear is **left open or dropped**; no hypotheses in the results.
- Every comment is generated from a computed figure by rules whose thresholds have a documented reason.
  No hand-written comments, no LLM.

## Outputs

### Group 1: Profit (the way businesses track it)

| # | Analysis | Content |
|---|---|---|
| P1 | **P&L by period** | Month / quarter / year. Revenue (linehaul, fuel surcharge, accessorials) → costs (fuel, maintenance, claims) → contribution → margin. Vs the previous period, the same period last year, and **year-to-date** vs the prior year-to-date. Costs are booked on the date they occur, so totals reconcile |
| P2 | **Profit bridge** | Between any two periods: the change in contribution split into volume, rate, fuel price, fuel consumption, maintenance and claims. The parts add up exactly to the total change |
| P3 | **Unit economics** | Revenue, cost and contribution per mile, per trip, per truck-week |
| P4 | **By business dimension** | Customer segment (contract / dedicated / spot), customer (top N + concentration: top-10/20 share, largest customer, customers making 80%, HHI), load type, origin state, destination state, lane, truck, driver |
| P5 | **Margin vs fuel price** | Monthly margin and fuel price, with their correlation |

### Group 2: Fuel (statistics only)

| # | Analysis | Content |
|---|---|---|
| F1 | **Fuel by month / quarter / year** | Gallons bought, spend, average price, gallons burned on trips, bought ÷ burned. No interpretation of the gap |

### Group 3: Fleet

| # | Analysis | Content |
|---|---|---|
| C1 | **Trucks busy per day** | By day and by year; vs trucks in use and trucks owned |
| C2 | **Capacity plan by service level** | Trucks enough for 95% / 99% of days and for the busiest day. With the evidence for why the *timing* of peaks can't be forecast (no trend, no recurring quarter or month, one day doesn't predict the next) |

### Group 4: Network (from the notebook, corrected)

| # | Analysis | Content |
|---|---|---|
| N1 | **3×3 lane matrix** | 3 volume × 3 margin tiers (thirds by rank), each cell with a direction: protect, grow, reprice, consider exiting… Bubble-chart data. Real costs from the KPI layer |
| N2 | **Headhaul / backhaul imbalance** | Per city: loads out, loads in, net, imbalance %, persistence across years. Total inbound surplus |
| N3 | **How often trucks change starting point** | From each truck's trip sequence: % of times the next trip starts in a different city from where the previous one ended, by year and by city. **Counted only, no miles** |
| N4 | **Comparison with the notebook** | What the notebook does, where it goes wrong, how it's fixed, how the result differs |

### Group 5: Rule-based commentary, and outputs

- **Rules** (`insights.py`): each rule reads the figures and produces an EN/VI sentence at level *info*,
  *watch* or *act*. Templates contain no digits: every number is filled in from the figures (tested).
  Every threshold has a reason and a source.
- **`analysis_bundle(con, start, end)`** returns every table and comment; the dashboard reads only from it.
- KPI-layer additions: origin/destination state in `trip_economics`; `kpi(by=…)` gains `origin_state`,
  `destination_state`, `load_type`.
- The **`logops insights`** command; the generated **`docs/03-analysis-insights`** EN/VI; the module
  review; updates to `SUMMARY` and the journal.

## Dropped (decided 2026-10-03)

| Dropped | Why |
|---|---|
| Weekday, seasonality | Not how businesses track results; the data has no pattern either |
| *Operating ratio* | Without wages and overhead it comes out around 35%, misleading next to industry norms |
| Empty miles, extra coordinates | 4 lane cities have no coordinates; external coordinates would be a distortion |
| Empty-running ↔ excess-fuel hypothesis | Not clear enough; fuel is reported as statistics only |
| Savings figures | Belong to `optimize` |

## Success criteria

1. **Totals reconcile:** period P&L adds up to the KPI layer's fleet totals; bridge parts add up to the
   total change; totals by business dimension + "Unattributed" equal the fleet total.
2. **No digits in comment templates** (tested).
3. Every threshold has a reason and a source.
4. Fixture tests for the main calculations + integration tests on the real data; `ruff` clean.

## Plan

| Task | Content |
|---|---|
| A1 | KPI-layer additions (states, load type) |
| A2 | Profit P1–P5 |
| A3 | Fuel F1, fleet C1–C2 |
| A4 | Network N1–N4 |
| A5 | Rules + `analysis_bundle` + `docs/03-analysis-insights` + `logops insights` |
| A6 | Module review, `SUMMARY`, journal, `CAPABILITY-MAP`, roadmap |
