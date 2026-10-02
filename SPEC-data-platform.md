# Spec: data-platform

> Module 1 of 6 · see [CAPABILITY-MAP.md](CAPABILITY-MAP.md) · CRISP-DM Phases 2–3 (Data Understanding, Data Preparation) · Vietnamese: [SPEC-data-platform.vi.md](SPEC-data-platform.vi.md)

## Objective

**Source data:** [Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database)
(Kaggle, by *yogape*), 14 CSVs. It is **not committed**: download it, unzip it into
`dataset/`, and run the build.

Turn the 14 raw CSVs in `dataset/` into a **validated, query-ready DuckDB warehouse** that every
other module reads from. The module also produces a **data-quality report**: the Phase 2
deliverable that shows the interviewer the data was checked and understood, not just loaded.

**Users:** downstream modules (`metrics`, `optimize`, …) and the project owner, who reads
the data-quality report.

**Acceptance criteria**
- One command rebuilds everything from raw CSVs: Parquet files, DuckDB database and DQ report.
- Every table is loaded with explicit, typed columns. No pandas type guessing.
- Bad rows are **flagged, not dropped** (`dq_issues` column). Only exact duplicate rows are
  removed, and the number removed is logged.
- The DQ report lists, per table: row count, null % per column, primary-key uniqueness,
  orphaned foreign keys, rule violations with counts and 3 sample rows each.
- Baselines needed by `docs/01-business-understanding.md` §5 (total operating cost, on-time %,
  fleet MPG, utilization) are printed in the report, so success targets can be confirmed.

## Tech Stack

| Purpose | Choice |
|---|---|
| Runtime | Python 3.11 (installed: 3.11.9) |
| Env / deps | `uv` (**not installed yet**; `pip install uv` or the official installer) |
| Engine | `duckdb` ≥ 1.1: reads CSV, writes Parquet, hosts the warehouse |
| DataFrames | `polars` (only where SQL is awkward) |
| CLI | `typer` |
| Tests / lint | `pytest`, `ruff` |

## Commands

```bash
uv sync                          # install deps
uv run logops build              # CSV → Parquet → DuckDB → DQ report (idempotent)
uv run logops build --skip-dq    # warehouse only (faster when iterating)
uv run pytest                    # all tests
uv run pytest -m "not slow"      # unit tests only (no real dataset)
uv run ruff check . && uv run ruff format .
```

## Project Structure

```
dataset/                    → raw Kaggle CSVs (git-ignored, read-only, never modified)
data/                       → GENERATED, git-ignored
  parquet/<table>.parquet
  warehouse.duckdb
src/logops/
  cli.py                    → typer app: `logops build`, later `report`, `dashboard`
  config.py                 → paths, constants
  data_platform/
    schema.py               → typed column definitions for the 14 tables (single source of truth)
    ingest.py               → CSV → typed Parquet
    quality.py              → DQ rules → dq_issues flags + findings
    warehouse.py            → Parquet → DuckDB tables + relationships
    dq_report.py            → findings → docs/02-data-quality-report.md
tests/
  fixtures/                 → tiny hand-made CSVs with known defects
  data_platform/
docs/
  02-data-quality-report.md     → GENERATED (English)
  02-data-quality-report.vi.md  → GENERATED (Vietnamese, same data with translated labels)
  02-data-understanding.md      → hand-written analysis of the report (EN)
  02-data-understanding.vi.md   → Vietnamese version
```

## Data-quality rules (initial set)

| Rule id | Check | Example table |
|---|---|---|
| `pk_unique` | Primary key unique and not null | all |
| `fk_orphan` | Foreign key exists in the parent table | trips→drivers, fuel→trips |
| `fk_missing` | Required foreign key is null | fuel_purchases.driver_id (seen in sample) |
| `geo_mismatch` | City/state pair not seen in facilities or routes | fuel "New York, AZ" |
| `amount_mismatch` | `total_cost ≠ gallons × price` (±1%); `total_cost ≠ labor + parts` | fuel, maintenance |
| `range` | Out-of-range values: mpg ∉ [3, 12], negative miles/costs, duration ≤ 0 | trips |
| `time_order` | Termination before hire; actual delivery before pickup | drivers, delivery_events |
| `agg_drift` | Pre-aggregated monthly metrics differ from values recomputed from trips by > 2% | driver/truck monthly |

Rules live in one list in `quality.py`. Each rule is a SQL predicate plus an id and a severity,
so adding a rule is one line.

## Code Style

```python
# quality.py: rules are data, not functions
RULES: list[Rule] = [
    Rule("fuel_purchases", "amount_mismatch", "warn",
         "abs(total_cost - gallons * price_per_gallon) > 0.01 * total_cost"),
    Rule("trips", "range", "error",
         "average_mpg NOT BETWEEN 3 AND 12 OR actual_distance_miles <= 0"),
]
```

- snake_case; type hints everywhere; small modules; SQL in DuckDB rather than pandas loops.
- Paths only via `config.py`; never hard-code `D:\...`.
- Ruff defaults, line length 100.

## Testing Strategy

- **Unit** (`tests/data_platform/`, fast): fixture CSVs with 5–10 rows, each containing one
  known defect. Each DQ rule has a test showing it flags the defect and ignores clean rows.
- **Integration** (`@pytest.mark.slow`): full build on the real `dataset/`; row counts match
  the CSVs; the build runs twice with identical results (idempotent).
- No coverage-% target for now. The bar is one test per rule plus a passing integration test.

## Boundaries

- **Always:** keep `dataset/` read-only; flag rather than delete; run `pytest` before commits;
  document every cleaning rule in the DQ report.
- **Ask first:** adding dependencies beyond the stack table; dropping or imputing data;
  changing a primary or foreign key definition.
- **Never:** commit `dataset/`, `data/` or `.env`; edit raw CSVs; silently coerce types (fail loudly
  instead).

## Success Criteria

1. `uv run logops build` finishes in **< 30 s** on the laptop and creates
   `data/warehouse.duckdb` containing 14 tables.
2. Row counts in the warehouse equal the CSV row counts, minus logged exact duplicates.
3. `docs/02-data-quality-report.md` and `.vi.md` are generated and cover all 14 tables and
   all rules above.
4. The report prints baselines: total operating cost, on-time %, fleet MPG, average
   utilization.
5. `uv run pytest` passes; `ruff check` is clean.

## Resolved Decisions

- **Dataset:** not redistributed; it is referenced by name and link only. `dataset/` is
  git-ignored.
- **Language:** every doc, spec, plan and generated report has separate EN (`name.md`) and VI
  (`name.vi.md`) files.
- **`uv`:** installed (0.12.21) but not yet on PATH. Until it is, use `python -m uv` in place
  of `uv`.

## Open Questions

None.
