# Review · Module 1: `data-platform`

> CRISP-DM phases 2–3 · Vietnamese: [01-data-platform.vi.md](01-data-platform.vi.md) · Spec:
> [SPEC-data-platform.md](../../SPEC-data-platform.md) · Summary: [SUMMARY.md](../SUMMARY.md)
> **Status:** completed 2026-10-03 · Commits: `61e34a7`, `01a9afa`, `53e0967`, `618a91f`
> **Rule for this file:** only facts verified by code or a query.

## 1. Outputs vs the spec

| Output in the spec | Delivered | Evidence |
|---|---|---|
| One command rebuilds everything from the CSVs | ✅ `logops build`: CSV → typed Parquet → DuckDB → quality checks → report | 14 tables, 549,706 rows; row counts match the CSVs (integration test) |
| Explicit types, loud failure on a mismatch | ✅ `schema.py` + `ingest.py`; errors name the exact `table.column` | Test with `"about 700"` in a numeric column |
| Bad rows flagged, never deleted | ✅ `dq_issues` column on every table + `dq_findings` table | Test: row counts equal before and after the checks |
| DQ report EN/VI with baselines | ✅ `docs/02-data-quality-report` (generated; re-runs are byte-identical) | Integration test: covers 14 tables and every rule |
| Build < 30 s | ✅ 4.2 s (14 tables), 5.4 s (with key rules), 8.0 s (all 69 rules + report) | Timing printed by `logops build` |
| Beyond the spec | ER diagram (`02-data-model`), threshold rationale (`02-dq-rule-thresholds`), data analysis (`02-data-understanding`) | Added at the project owner's request |

## 2. Measured figures

| Metric | Value |
|---|---|
| Data-quality rules | 69 (50 key rules + 19 value rules; 43 errors, 26 warnings) |
| Rules with violations | 14 / 69 |
| Rows with an error-level issue | 8,084 (1.5%) |
| Rows with at least one issue, warnings included | 365,147 (66.4%). Of these, 344,331 rows (62.6% of all rows) are flagged **only** for the two broken location columns; their measurements are fine |
| Tests | 47, all passing |

## 3. Data evaluation: what can be trusted

| Level | Item | Evidence |
|---|---|---|
| ✅ Trust | Relationships between tables | 0 duplicate keys, 0 orphan keys |
| ✅ | Money amounts | Totals equal their parts; largest gap $0.005 |
| ✅ | Monthly aggregate tables | 100% match with recomputed values |
| ✅ | No duplicates | 0 exact duplicate rows |
| ⚠️ With conditions | Empty driver/truck/trailer IDs (~2%) | Missing at random (MCAR); 0 rows recoverable from other tables |
| ⚠️ | Delivered before picked up | 486 trips (actual), 175 trips (scheduled) |
| ⚠️ | Truck utilization > 100% | 436 truck-months (13.2%) |
| ❌ Don't use | State on fuel purchases and incidents | 95.3% and 95.9% wrong state |
| ❌ | `facility_id` on delivery events | Matches the lane 3.4% of the time; `location_city` matches 100% |
| ❌ | `idle_time_hours` | Correlation with trip duration 0.006, distance 0.007, fuel per mile 0.000: random noise. 7,450 trips (8.7%) have more idle time than trip time |
| ❌ | Fuel price by location | Average price differs by $0.02/gallon across cities |

**`on_time_flag`** = \|actual − appointment\| ≤ 120 minutes, matching 100% of 170,820 events. The
boundary is sharp: every `True` is within ±120.00 minutes, every `False` beyond it. The dataset's
documentation doesn't define the flag, and there's no external source for the 120.

## 4. Not done, and why

| Item | Reason |
|---|---|
| Task 6 `agg_drift` (cut) | A one-off check found 0% drift; the result is in the report's cross-checks |
| Task 8 hardening (cut) | 0 duplicate rows; the build was already stable and fast |
| Hiring-age rule (removed) | Project owner's decision: focus on productivity and quality |
| 7 rules without their own test | Every rule *type* is tested; the list is in `02-dq-rule-thresholds` §5 |
| Deriving the correct state from the city | Proposed (25 cities ↔ 25 states, 100% repairable), not approved |
| Separating column-level from row-level issues in the report summary | Proposed, not approved; the summary still shows 66.4% |

## 5. Impact on later modules

- Location analysis uses `location_city`, not `facility_id`.
- No savings are claimed from idling or from fuel price by location.
- Driver/truck rankings exclude rows missing the ID; fleet totals keep every row.
- Savings target: ≥ $3.1M over 3 years (3% of $104.0M measured cost).

## 6. Reproduce

```powershell
python -m uv run logops build      # build the warehouse, run the checks, write the report
python -m uv run pytest            # this module's 47 tests (76 including module 2)
```
