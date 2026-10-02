# Tasks: data-platform

> Plan: [plan.md](plan.md) · Vietnamese: [todo.vi.md](todo.vi.md) · This file is the source of truth for checkboxes.
> Commands use `uv`; if it's not on PATH, use `python -m uv`.

## Task 1: Project scaffold
**Description:** Create `pyproject.toml` (uv, Python 3.11, deps: duckdb, polars, typer; dev:
pytest, ruff), the `src/logops/` package, `config.py` with paths, and a `logops` CLI entry
point with a `build` command stub. Add a README with the dataset download instructions.

**Acceptance criteria:**
- [x] `uv sync` succeeds; `uv run logops --help` lists `build`
- [x] `config.py` resolves `dataset/` and `data/` relative to the repo root
- [x] README links the Kaggle dataset and shows the 3 setup steps

**Verification:** `uv run pytest` (one smoke test passes) · `uv run ruff check .`
**Dependencies:** None
**Files:** `pyproject.toml`, `src/logops/__init__.py`, `src/logops/cli.py`, `src/logops/config.py`, `README.md` (+ `README.vi.md`), `tests/test_smoke.py`
**Scope:** S

## Task 2: One-table vertical slice (`routes`)
**Description:** Define the `routes` schema in `schema.py`. `ingest.py` reads the CSV with
explicit types and writes Parquet; `warehouse.py` loads Parquet into DuckDB; `logops build`
runs both.

**Acceptance criteria:**
- [x] `logops build` creates `data/parquet/routes.parquet` and table `routes` in `data/warehouse.duckdb`
- [x] Column types match the schema exactly (no VARCHAR fallback for numerics)
- [x] A type mismatch in the CSV raises a clear error naming the table and column

**Verification:** fixture test `tests/data_platform/test_ingest.py` · manual: `duckdb data/warehouse.duckdb "describe routes"`
**Dependencies:** T1
**Files:** `data_platform/schema.py`, `data_platform/ingest.py`, `data_platform/warehouse.py`, `cli.py`, `tests/fixtures/routes.csv`, test file
**Scope:** M

## Task 3: All 14 tables
**Description:** Add schemas (types, PK, FKs) for the remaining 13 tables, including
timestamps with microseconds, booleans stored as "True"/"False", and nullable foreign keys.

**Acceptance criteria:**
- [x] Warehouse contains 14 tables; row counts equal the CSV line counts
- [x] Each schema declares its PK and FKs (used later by the key rules)

**Verification:** `uv run pytest -m slow` (row-count integration test on the real dataset)
**Dependencies:** T2
**Files:** `schema.py`, `tests/data_platform/test_build_integration.py`
**Scope:** M

## Checkpoint A: Warehouse builds
- [x] All tests + ruff green
- [x] Human review before DQ work

## Task 4: DQ engine + key rules
**Description:** `quality.py` with `Rule(table, id, severity, predicate)`. The engine adds
a `dq_issues` column to each table and writes a `dq_findings` table (table, rule, severity,
count, sample ids). Rules: `pk_unique`, `fk_missing`, `fk_orphan`, generated from the
PK/FK declarations in `schema.py`.

**Acceptance criteria:**
- [x] Fixture with a duplicate PK, a null FK and an orphan FK → each is flagged exactly once
- [x] Clean fixture rows have an empty `dq_issues`
- [x] No rows are deleted

**Verification:** `uv run pytest tests/data_platform/test_quality_keys.py`
**Dependencies:** T3
**Files:** `quality.py`, `warehouse.py`, fixtures, test file
**Scope:** M

## Task 5: Value rules
**Description:** Add `range`, `amount_mismatch`, `time_order` and `geo_mismatch` as
one-line rule entries.

**Acceptance criteria:**
- [ ] One fixture test per rule: it flags the defective row and passes the clean row
- [ ] `geo_mismatch` is severity `warn`, and its reference list is built from facilities + routes

**Verification:** `uv run pytest tests/data_platform/test_quality_values.py`
**Dependencies:** T4
**Files:** `quality.py`, fixtures, test file
**Scope:** M

## Task 6: `agg_drift` rule
**Description:** Recompute monthly trips, miles and revenue per driver and per truck from
`trips` + `loads`, and compare with `driver_monthly_metrics` / `truck_utilization_metrics`.
Flag rows that differ by more than 2%.

**Acceptance criteria:**
- [ ] Fixture with one drifted month → flagged; matching month → clean
- [ ] Findings include the drift distribution (median, p95), not only a count

**Verification:** `uv run pytest tests/data_platform/test_quality_agg.py`
**Dependencies:** T4
**Files:** `quality.py`, fixtures, test file
**Scope:** S

## Checkpoint B: Findings correct
- [ ] Run on the real data; review findings, especially the false-positive rate of `geo_mismatch`
- [ ] Human review

## Task 7: DQ report EN + VI with baselines
**Description:** `dq_report.py` renders `dq_findings` + per-column null % + baselines (total
operating cost, on-time %, fleet MPG, average utilization) into
`docs/02-data-quality-report.md` and `.vi.md`, from one template with two label dictionaries.

**Acceptance criteria:**
- [ ] Both files cover all 14 tables and every rule, with 3 sample rows per violation
- [ ] Baseline numbers are identical in both languages
- [ ] Re-running produces byte-identical files (no timestamps in the body)

**Verification:** `uv run pytest tests/data_platform/test_dq_report.py` · manual read of both files
**Dependencies:** T5, T6
**Files:** `dq_report.py`, `cli.py`, test file
**Scope:** M

## Task 8: Hardening
**Description:** Remove exact duplicate rows and log the count; add the `--skip-dq` flag;
make sure a second run is idempotent; measure the build time.

**Acceptance criteria:**
- [ ] Full build < 30 s on the laptop (timing printed by the CLI)
- [ ] Running twice gives identical row counts and findings
- [ ] `--skip-dq` builds the warehouse without the DQ step

**Verification:** `uv run pytest -m slow` · manual timed run
**Dependencies:** T3 (T7 for the full check)
**Files:** `ingest.py`, `cli.py`, test file
**Scope:** S

## Task 9: Data-understanding docs
**Description:** Read the generated report and write the analysis for interview storytelling:
what the data covers, key quality issues and how they're handled, baselines, and the
confirmed or adjusted success targets from doc 01 §5.

**Acceptance criteria:**
- [ ] `docs/02-data-understanding.md` + `.vi.md` exist and match each other
- [ ] Doc 01 §5 targets updated (both languages) if the baselines change them

**Verification:** human read-through
**Dependencies:** T7
**Files:** `docs/02-data-understanding.md`, `.vi.md`, `docs/01-*.md`
**Scope:** S

## Checkpoint C: Module complete
- [ ] All SPEC-data-platform success criteria met
- [ ] Ready to write `SPEC-metrics.md`
