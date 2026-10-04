# Review · Module 5: `optimize`

> CRISP-DM phases 4–5 (Modeling, Evaluation) · Vietnamese: [05-optimize.vi.md](05-optimize.vi.md)
> · Spec: [SPEC-optimize.md](../../SPEC-optimize.md) · Results: [05-evaluation.md](../05-evaluation.md),
> [04-data-process-improvements.md](../04-data-process-improvements.md) · Summary: [SUMMARY.md](../SUMMARY.md)
> **Status:** completed 2026-10-04, not yet committed · **Rule:** only verified facts.

## 1. Context

Redone from branch `feature/optimize` after the analysis and dashboard modules. Scope agreed with
the project owner: O1 fleet, O2 lane pricing, O4 late deliveries, O5 data process, O6
recommendations and dashboard page; O3 trip chaining only if time allows (built 2026-10-04, dropped by the owner 2026-10-05). The target
of $3.1M over 3 years may be exceeded.

## 2. Outputs vs the spec

| Output | Delivered | Evidence |
|---|---|---|
| O1 fleet size and disposal tiers | ✅ Daily demand is the analysis layer's trucks working per day, plus an allowance for trips without a truck ID (2.0%) | Test: daily demand equals the dashboard's; trucks needed rise with growth; disposal never leaves the fleet short |
| O2 lane pricing S1/S2/S3 | ✅ Lane groups are the dashboard's 3×3 matrix; S2 applies to the lowest-margin third (20 lanes) | Lane revenue and contribution reconcile with the fleet KPIs; groups equal the lane matrix's actions |
| O4 late deliveries | ✅ No persistent cause: correlation between periods −0.23 to 0.14 (needs 0.7) for city, customer, appointment hour, lane and driver | Test on the real data |
| O5 data-process improvements | ✅ 7 gaps; new: moves between trips not recorded | Every device cost cites a source |
| O6 recommendations, docs, page | ✅ `recommendations` table, `logops optimize`, `docs/04`, `docs/05`, dashboard page "Optimization recommendations" (VI/EN), one page placed before the data page (2026-10-04) | The page runs in both languages and reloads under 3 s |
| O3 trip chaining | ❌ Built, then dropped by the owner (2026-10-05) | Results depended too much on assumptions the data can't settle: dry-van vs refrigerated trucks, dedicated trucks (50% of loads: cut in empty miles 59.5% → 35.2%), lane-based distances longer than real roads, and replayed empty miles about three times what the fuel bought off trips allows. Too easy to challenge, so not presented |

**Tests:** 26 in `tests/optimize` + 2 page runs; 148 in total, all passing; `ruff` clean.

## 3. Results (per year, 2022–2024 data)

| Type | Amount | vs target ($1.04M) |
|---|---:|---:|
| **Measured saving:** dispose of 13 inactive + 15 in-maintenance trucks that never ran | $0.47M | 45% |
| **Upper bound:** review 13 lowest-mileage trucks ($0.20M), surcharge to the median ($0.96M), rates on low-margin lanes capped at +5% ($1.26M) | $2.42M | 233% |
| **Total potential** | $2.89M | 278% |
| Unexplained, not counted: fuel bought but not recorded as burned | $7.24M | — |

- **Fleet:** 79 / 83 / 87 / 94 trucks needed at 0 / 5 / 10 / 20% growth vs 120 owned and 92 in use;
  availability 97.7%; 8 of 1,096 days needed more than 79 trucks (short-term rental).
- **Lanes:** every lane profitable on measured cost; the weakest loses money only if driver cost
  exceeds $0.857 per mile. With a +10% cap, S1 + S2 = $3.45M per year; uncapped (theoretical) $6.62M.
  Median break-even volume loss 9.6% at +5%.
- **Fuel-indexed surcharge (S3):** revenue-neutral base $2.318 per gallon; shown as risk sharing, not
  a saving.
- **Late deliveries:** 44.4% more than 2 h late, with no repeatable cause in the data: no
  recommendation, reason codes proposed instead (O5).

## 4. Caveats for presenting


- Measured savings alone reach 45% of the target; the target is exceeded only with the pricing
  levers, which need customers to accept them.
- Margins are before driver pay and overhead.
- Telematics prices are indicative public figures.

## 5. Reproduce

```powershell
python -m uv run logops build          # recommendations table + docs/04, docs/05
python -m uv run logops optimize       # recommendations vs target
python -m uv run pytest tests/optimize -m "slow or not slow"
```
