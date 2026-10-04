# Spec: optimize

> Module 5 of 6 · CRISP-DM phases 4 (Modeling) and 5 (Evaluation) · Vietnamese:
> [SPEC-optimize.vi.md](SPEC-optimize.vi.md) · Inputs: the KPI layer (module 2), the analysis layer
> (module 3) · Redone from branch `feature/optimize` after the analysis and dashboard modules.

## Objective

Turn the findings into **recommendations with an action and a dollar figure**, compared with the
target of **at least $3.1M over 3 years** ($1.04M per year, 3% of measured operating cost). Exceeding
the target is better; every figure must still be defensible in front of the Logistics Director.

**Principles**
- A dollar figure only where the signal **persists across years** (2022–23 vs 2024).
- **No external data.** The only exceptions are implementation costs for data-process measures
  (O5), from cited public sources and labelled indicative.
- Three kinds of figures: **measured saving** (comes from the data as is), **upper bound** (needs
  a decision or a customer to accept a change), **unexplained** (money the data can't account for
  yet). Measured and upper bound are shown separately and their sum is labelled "total
  potential"; unexplained money is never added to any total.
- Everything shown follows the presentation standards: units, a plain reading note, VI/EN names.

## Outputs

### O1. Fleet size (`optimize/fleet.py`)

- **Trucks needed** = ⌈daily demand at the service level (default: enough on 99% of days) × (1 +
  share of trips without a truck ID) × (1 + growth) ÷ availability⌉. Daily demand is the analysis
  layer's trucks working per day, so the dashboard and this module show the same numbers.
  Availability = 1 − maintenance downtime ÷ hours of the trucks in use. Growth scenarios 0 / 5 /
  10 / 20%.
- **Disposal in tiers:** (1) the 13 `Inactive` trucks that never ran, (2) the 15 `Maintenance`
  trucks that never ran, (3) trucks in use beyond the need, lowest mileage first. If a scenario needs
  more trucks than are in use, `Maintenance` trucks return to service first.
- **Money:** tiers 1–2 = their maintenance cost per year (**measured**); tier 3 = upper bound.
  Resale value isn't in the data: an unquantified benefit.
- **Cross-check:** busiest day and days above the need.

### O2. Lane pricing (`optimize/lanes.py`)

- Per lane: trips, revenue, contribution, margin, the fuel surcharge's fuel-cost recovery, and the
  **break-even driver cost per mile** (contribution ÷ miles): the lane loses money only if driver
  cost exceeds it. This replaces a guess at the missing driver pay.
- **S1** fuel surcharge: lanes below the median surcharge rate raised to the median.
- **S2** rates: after S1, high-volume low-margin lanes ("Renegotiate rates") and low-volume
  low-margin lanes ("Review rates") brought toward the median margin, with the increase capped at
  5% (headline), 10% or uncapped (theoretical) of linehaul.
- **S3** simulation: a surcharge indexed to the monthly fuel price, revenue-neutral over the period.
  Shows how fuel risk would be shared; not counted as a saving.
- Each lane also gets the **largest volume loss** before the change earns less than today.
- **Money:** S1 and S2 are **upper bounds** (customers must accept the change).

### O4. Late deliveries (`optimize/lateness.py`)

- Share of deliveries more than 2 hours late, by delivery city, customer, appointment hour, lane and
  driver; a signal counts only if the group's rate persists between 2022–23 and 2024
  (correlation ≥ 0.7) and the spread between groups is meaningful.
- **Expected outcome:** no persistent driver (lateness is spread evenly from 3 h early to 6 h late
  on every trip length). If so, **no recommendation**: the evidence is shown and the lever dropped.

### O5. Data-process improvements (`optimize/data_gaps.py`)

One row per gap (fuel reconciliation, moves between trips not recorded, missing truck and driver
IDs, wrong state and facility codes, idle hours unusable): evidence, **cost of not doing** (from the
data), tier-1 measures (process or configuration, near zero cost) and tier-2 measures (devices),
**indicative implementation cost** with its source, priority.

### O6. Recommendations, evaluation, dashboard page

- `recommendations` table in the warehouse and `optimize.recommendations()`: area, item, action,
  amount per year, type (measured / upper bound / unexplained), evidence.
- `logops optimize [--growth 0.05] [--cap 5]` prints the recommendations.
- Generated `docs/05-evaluation` (EN/VI): total vs target, measured and upper bound kept apart.
- Dashboard page **"Optimization recommendations"**: total vs target, fleet scenarios (growth
  slider), lane scenarios (cap choice), data-process table, the dropped levers with their evidence.

### O3. Trip chaining (if time allows)

Day-by-day simulation: each load goes first to a free truck already in its pickup city. Output:
moves between cities avoided and trucks needed. No empty miles in the data, so money only through a
viewer-entered cost per move, labelled an estimate.

## Out of scope

| Not done | Why |
|---|---|
| ML delay model, MPG by driver or truck, idling, fuel price by location, customer profitability, truck replacement | Not persistent across years, or noise (checked in the first optimize pass) |
| Load consolidation, detention billing, shop and dock bottlenecks | Dropped by the project owner (2026-10-03) |
| Driver pay, overhead, resale value, demand elasticity | Not in the data: break-even figures instead |

## Success criteria

1. Every dollar figure traces to a query and carries its type; types are never summed together.
2. Fleet: correct on hand-computable fixture data; trucks needed rises with growth; the daily demand
   equals the analysis layer's.
3. Lanes: lane revenue and contribution add up to the fleet totals; every lane in exactly one group;
   lanes at or above the benchmark get no increase.
4. Late deliveries: the persistence test is applied and its result shown, whichever way it goes.
5. Data gaps: every implementation cost has a source; every cost of not doing has its query.
6. The dashboard page runs in both languages; `ruff` clean; tests pass.

## Plan

| Step | Content |
|---|---|
| 1 | Port `fleet.py`, `lanes.py`, `data_gaps.py` from `feature/optimize`; align daily demand with the analysis layer; fixture tests |
| 2 | `lateness.py` persistence check |
| 3 | `recommendations()`, warehouse table, CLI, `docs/05-evaluation` |
| 4 | Dashboard page, translations, tests, screenshots |
| 5 | O3 trip chaining if time allows |
| 6 | Review `docs/reviews/05-optimize`, SUMMARY, journal, CAPABILITY-MAP |

> **O3 done 2026-10-04:** baseline is a replay of today's dispatching, not the data's own truck
> assignment (its trips overlap in time); money typed "estimate" (hypothesis), never in totals.
> **O3 revised 2026-10-04 (owner):** nearest free truck, distances over the lanes, fuel per mile
> from the data; money = the replay's cut in empty miles × fuel bought off trips (a maximum).
