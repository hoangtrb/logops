# Spec: optimize

> Module 3 of 6 · CRISP-DM phase 4 (Modeling) and phase 5 (Evaluation) · Vietnamese:
> [SPEC-optimize.vi.md](SPEC-optimize.vi.md) · Input: module 2's KPI layer
> ([reviews/02-metrics.md](docs/reviews/02-metrics.md) §6)

## Objective

Turn the KPIs into **recommendations with a concrete action and a dollar figure**, only for levers
with a **real signal**, and compare them with the target of ≥ $3.1M over 3 years (about $1.04M per
year).

**Principles**
- A dollar figure only where the signal **persists across years** (2022–23 vs 2024).
- Nothing the data lacks is assumed. Unknowns become **viewer-entered parameters** or come from
  **cited public sources**, labelled as indicative estimates.
- **Measured savings** are kept separate from **upper bounds** (which depend on customers accepting
  a change).

## Signal check (run on the real data)

| Area | Evidence | Decision |
|---|---|---|
| Fleet size | Trucks busy per day: median 66, p99 75, max 80; fleet of 120 (92 in use); trips per year 28,589 / 28,165 / 28,656 | ✅ P1 |
| Lane profitability | Margins 50.4–72.7%, persistent across years (correlation 0.946) | ✅ P2 |
| Fuel surcharge | Fixed rate per lane, $0.15–0.34/mile, not tied to fuel price; fuel cost per mile is the same on every lane (0.601–0.607) | ✅ Part of P2 |
| Data quality → process | Data gaps with measured impact (e.g. 5.57M gallons bought but not reconciled with consumption) | ✅ P4 |
| Maintenance-shop and receiving-dock bottlenecks | Signal exists, but the project owner judged it not practical enough | ❌ Dropped (decision 2026-10-03) |
| Load consolidation, detention billing | Urgent loads can't wait to be combined; detention billing not reasonable | ❌ Dropped (decision 2026-10-03) |
| ML delay model, MPG by driver/truck, idling, fuel price by location, customer profitability, replacing old trucks | Not persistent across years, or noise | ❌ Dropped, shown with evidence |

## Outputs

### P1. `fleet_plan`: assess fleet size → recommend → cross-check

**Assessment:**

| Step | Calculation | Source |
|---|---|---|
| Daily truck demand | Each trip occupies its truck from the dispatch day for ⌈trip duration ÷ 24 h⌉ days | `trips` |
| Design demand | `percentile` (default p99) × (1 + growth) | Scenarios 0 / +5 / +10 / +20% |
| Availability | 1 − maintenance downtime ÷ total hours of the trucks in use | `maintenance_records` |
| Trucks needed | ⌈design demand ÷ availability⌉ | |

**Tiered recommendations:**
1. Dispose of the 13 `Inactive` trucks.
2. Dispose of, or repair and return to service, the 15 `Maintenance` trucks, depending on the growth
   scenario.
3. Review active trucks beyond the design demand.

Each tier has a **measured saving** (those trucks' annual maintenance cost). Resale value isn't in the
data and is labelled an *unquantified benefit*.

**Cross-check:** compare trucks needed with (a) trucks running at least one trip per month, from `truck_utilization_metrics`, and (b) the busiest day in the 3 years.

### P2. `lane_pricing`: lane profitability → classification → improvement scenarios

**Per-lane assessment (58 lanes):** trips, revenue (linehaul and surcharge), measured cost,
contribution margin, the surcharge's fuel recovery, and the **break-even driver cost** = contribution ÷
miles, i.e. the lane loses money if driver cost exceeds this per mile. With no wage data, this answers
"profitable or not" without an assumption.

**Classification** by margin (vs median) × volume (vs median):

| Group | Margin | Volume | Direction |
|---|---|---|---|
| Core | High | High | Keep; prioritize truck capacity |
| Reprice | Low | High | First priority for a rate change |
| Profitable niche | High | Low | Keep; consider growing |
| Review | Low | Low | Reprice or deprioritize |

**Improvement scenarios** (each with the extra contribution per year and the **largest volume loss
before it loses money** vs today):
- **S1:** standardize the fuel surcharge: lanes below the median raised to $0.245/mile.
- **S2:** S1 + linehaul repricing of "Reprice" and "Review" lanes to the median margin.
- **S3 (simulation):** an index-linked surcharge, *surcharge per mile = (price − base price) ÷ MPG*,
  run on actual 2022–2024 prices. The base price is a parameter. This shows how price risk is shared;
  it isn't added to savings.

S2 is computed *after* S1 so nothing is double counted.

### P4. Data assessment → process improvements: cost of doing vs cost of not doing

One row per data gap:
- the problem and its evidence (from modules 1–2);
- the **cost of not doing**, measured from the data, e.g. the value of unreconciled fuel, unattributable cost;
- feasible measures in **tier 1** (process or configuration, nearly free) and **tier 2** (devices or integration);
- the **estimated implementation cost**, from cited public sources, labelled indicative;
- priority.

Generated document: `docs/04-data-process-improvements.md` / `.vi.md`.

### P5. Recommendations, evaluation, documents

- A `recommendations` table in the warehouse and a `recommendations()` function: the shared input for
  `insights`, `dashboard` and `reports`.
- The `uv run logops optimize [--growth 5]` command.
- `docs/05-evaluation` (generated): total impact vs the target, measured savings kept separate from
  upper bounds.
- `docs/reviews/03-optimize`, plus updates to `SUMMARY`, `CAPABILITY-MAP`, `00-analytical-approach`
  (why the delay model, MPG, bottlenecks, consolidation and detention billing were dropped), and
  `docs/01` §5 (the AUC criterion).

## Success criteria

1. Every dollar figure traces back to its query; measured savings are separate from upper bounds.
2. `fleet_plan` is correct on hand-computable fixture data; trucks needed rises with growth; the
   cross-check is included.
3. `lane_pricing`: lane revenue and contribution add up to the fleet KPIs; each lane is in exactly one
   group; lanes at or above the benchmark need a 0% increase.
4. P4: every implementation cost has a cited source; every cost of not doing has its query.
5. Fixture tests + integration tests; `ruff` clean.
