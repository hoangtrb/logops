# 00 · Project Journal

> Vietnamese: [00-project-journal.vi.md](00-project-journal.vi.md) · Analytical approach: [00-analytical-approach.md](00-analytical-approach.md)
> **Last updated:** Fri 2026-10-02, after Task 3 (module `data-platform`).

**How to use this file**
- First read: §1–§4 explain what the project is, what's in the folder, which workflow it
  follows and where it stands.
- Day to day: §5 (done), §6 (in progress), §7 (next).
- To understand *why* the analysis is done this way, read
  [00-analytical-approach.md](00-analytical-approach.md).
- After each finished task, add an entry to §5 using the template in §11, and update §4, §6
  and §7.

---

## 1. What the project is

**Logistics Ops Optimizer** turns fleet operations data (trips, fuel, deliveries, maintenance,
incidents) into **cost-saving decisions** with an estimated $ figure each. The results are
shown in a dashboard and in PDF/HTML reports exported in one step.

- **Purpose:** a portfolio project to present to the Logistics Director of Saigon Co.op at the
  interview on **Monday 2026-10-05**.
- **The audience is a manager, not an engineer.** Every result must answer *"what should I do,
  and how much does it save?"*
- **Data:** [Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database)
  (Kaggle). 14 tables, about 58 MB and about 550 thousand rows, covering 2022-01-01 to
  2024-12-31. The data is US-based (miles, USD) and kept as-is, because the method transfers to
  any distribution network.
- **Framework:** CRISP-DM, 6 phases. Each phase produces a visible deliverable (see §4).

## 2. Folder map

```
logistics-ops/
├── README.md / .vi.md              Intro + 3 setup steps
├── CAPABILITY-MAP.md / .vi.md      6 modules, 4 focus areas, 6 report types, CRISP-DM mapping
├── SPEC-data-platform.md / .vi.md  Spec for module 1 (later module specs sit alongside)
├── pyproject.toml, uv.lock         Dependencies (managed by uv)
├── docs/
│   ├── 00-project-journal.*        ← this file: progress log
│   ├── 00-analytical-approach.*    Theory and reasons behind each method
│   ├── 01-business-understanding.* CRISP-DM phase 1: director's questions → KPIs → success criteria
│   └── 02-…                        (coming) data-quality report + data analysis
├── tasks/
│   ├── roadmap.md / .vi.md         3-day schedule for all 6 modules
│   ├── plan.md / .vi.md            Plan for the current module (data-platform)
│   └── todo.md / .vi.md            Task list; todo.md (English) is the source of truth for checkboxes
├── src/logops/
│   ├── cli.py                      `logops` command (has `build` so far)
│   ├── config.py                   All paths, resolved from the repo root
│   └── data_platform/
│       ├── schema.py               Column types, primary and foreign keys of the 14 tables (single source of truth)
│       ├── ingest.py               CSV → typed Parquet, clear error on a type mismatch
│       └── warehouse.py            Parquet → DuckDB warehouse
├── tests/
│   ├── fixtures/                   Tiny hand-made CSVs with deliberate defects
│   ├── test_smoke.py               CLI and paths
│   └── data_platform/              Ingest, schema, and integration tests on the real data
├── dataset/          (not committed) 14 raw Kaggle CSVs, read-only
└── data/             (not committed) Generated: parquet/ and warehouse.duckdb
```

## 3. Workflow and conventions

**Each module follows the loop spec → plan → build → checkpoint.**
1. **Spec** (`SPEC-<module>.md`): objective, stack, structure, success criteria.
2. **Plan + todo** (`tasks/`): small tasks, each with acceptance criteria and a verification step.
3. **Build** in *vertical slices*: the first task takes **one table** through the whole pipeline
   (CSV → Parquet → DuckDB → CLI → test) before widening. Tests are written first.
4. **Checkpoint:** tests and ruff green, then your review, then the next phase.

**Conventions**
- Every doc has two files: English `name.md` and Vietnamese `name.vi.md`.
- **You commit.** Claude only runs `git add` and suggests a message. Planning docs are committed
  together with the README at the end of the project.
- Raw data is never edited. Bad rows are **flagged, not deleted**.
- Lean modules: one test per rule or engine, one integration test per module.
- Commands use `uv`. If `uv` isn't on PATH, use `python -m uv`.

## 4. Overall status

| # | Module | CRISP-DM phase | Planned | Status |
|---|---|---|---|---|
| — | Business understanding (`docs/01`) | 1 | Thu 10-01 | ✅ Done |
| 1 | `data-platform` | 2, 3 | Fri 10-02 | 🔄 In progress: Tasks 1–3 done, at Checkpoint A |
| 2 | `metrics` | 3 | Sat 10-03 AM | ⏳ Not started |
| 3 | `optimize` | 4, 5 | Sat 10-03 PM | ⏳ |
| 4 | `insights` | 6 | Sun 10-04 AM | ⏳ |
| 5 | `dashboard` | 6 | Sun 10-04 AM | ⏳ |
| 6 | `reports` | 6 | Sun 10-04 PM | ⏳ |
| — | Demo, evaluation, freeze | 5 | Sun 10-04 evening | ⏳ |

Module 1 progress: ███░░░░░░ 3/9 tasks.

## 5. Done (chronological)

### Thu 10-01 · Business understanding and planning
- **Wrote `docs/01-business-understanding`** (CRISP-DM phase 1). It maps the director's 5
  questions to KPIs and analysis techniques, and sets the success criteria: savings
  opportunities ≥ 3% of total operating cost, delay model AUC ≥ 0.70, report export in ≤ 2 clicks.
- **Wrote `CAPABILITY-MAP`.** It splits the project into 6 modules in dependency order and ranks
  the 4 focus areas by the director's priority.
- **Wrote `SPEC-data-platform`, `tasks/plan` and `tasks/todo`** for module 1: 9 tasks and 3 checkpoints.

### Fri 10-02 · Roadmap
- **Wrote `tasks/roadmap`.** A 3-day schedule for the 6 modules, with a "cut if late" column and
  end-of-day exit criteria.

### Fri 10-02 · Task 1: Project scaffold ✅
- **Done:** `uv` project (Python 3.11; duckdb, polars, typer; pytest, ruff), `src/logops/`
  package, `config.py`, a stub `logops build` command, README EN/VI.
- **Result:** 2 tests pass, ruff clean.
- **Note:** recent ruff versions also format code inside Markdown files, so `*.md` is excluded
  from ruff.

### Fri 10-02 · Task 2: One-table slice (`routes`) ✅
- **Done:**
  - `schema.py` declares each column's type.
  - `ingest.py` reads the CSV as text, checks that every value converts to its declared type,
    and only then writes Parquet.
  - `warehouse.py` loads Parquet into DuckDB with `CREATE OR REPLACE`, so re-running always
    gives the same result.
- **Result:** 58 rows in 0.1 s. A bad value stops the build with an error such as
  `routes.typical_distance_miles: 1 value(s) are not INTEGER, e.g. 'about 700'`.
- **Why read as text first:** if DuckDB guesses the types, one dirty cell silently turns a whole
  column into text. The spec requires *fail loudly, never coerce silently*.

### Fri 10-02 · Task 3: All 14 tables ✅
- **Done:** declared all 14 tables with types, primary keys and foreign keys. Added a schema
  test, a fixture test, and an integration test on the real data.
- **Result:** 14 tables load in 4.2 s (target < 30 s). Row counts match the CSVs. 11 tests green.
- **Decisions:**
  - The two monthly metrics tables have two-column primary keys: `(driver_id, month)` and
    `(truck_id, month)`.
  - `unit_number` and `trailer_number` are identifiers, so they stay text. `accessorial_charges`
    is money, so it's DOUBLE.
  - Empty foreign keys stay NULL for Task 4 to flag (`trips.driver_id` is empty in 1,714 rows,
    `fuel_purchases.driver_id` in 3,988 rows).
- **Preliminary figures** (not the official baselines; Task 7 recomputes them):

  | Metric | Value |
  |---|---|
  | Revenue (revenue + surcharges) | ≈ $298.6M |
  | Fuel cost | ≈ $95.6M |
  | Maintenance cost | ≈ $5.7M |
  | Total distance | ≈ 122M miles |
  | Average MPG | 6.5 |
  | On-time event rate (pickups and deliveries) | 55.7% |

  The on-time rate is unusually low. Tasks 7 and 9 need to check whether that's an artefact of
  the synthetic data or a real improvement opportunity.

## 6. In progress

**Checkpoint A: the warehouse builds.** Tests and ruff are green. It's waiting for your review of
the warehouse, for example with `duckdb -ui data/warehouse.duckdb`, before the data-quality work
starts.

## 7. Next

**Rest of module 1 (Fri evening):**

| Task | Content | Cut if late? |
|---|---|---|
| 4 | DQ engine + key rules: `pk_unique`, `fk_missing`, `fk_orphan` | No |
| 5 | Value rules: `range`, `amount_mismatch`, `time_order`, `geo_mismatch` | No |
| 6 | `agg_drift`: compare monthly metrics with values recomputed from trips | **Yes** |
| 7 | DQ report EN/VI + baselines (total cost, on-time %, MPG, utilization) | No |
| 8 | Hardening: drop exact duplicates, `--skip-dq` flag, identical re-runs | **Yes** |
| 9 | Write `docs/02-data-understanding` for the interview story | No |

**Later modules** (details in [roadmap.md](../tasks/roadmap.md)):
- **Saturday:** `metrics` (SQL KPI views) → `optimize` (4 recommendation engines, each with $ savings).
- **Sunday:** `insights` (Claude narratives) → `dashboard` (Streamlit) → `reports` (PDF/HTML) →
  demo script → freeze.

## 8. Key decisions

Full reasoning for each is in [00-analytical-approach.md](00-analytical-approach.md).

| Decision | Short reason |
|---|---|
| CRISP-DM as the framework | Starts from the business question and ends in deployment, which is how a manager thinks |
| DuckDB + Parquet, not Spark | 58 MB runs on a laptop in seconds; Spark would only add overhead |
| Flag bad rows, don't delete them | Keeps the audit trail; downstream users decide whether to exclude rows |
| Savings estimated against the fleet *median* | Conservative and achievable, no over-promising |
| Claude only explains numbers computed by code | Stops the LLM from inventing numbers |
| Keep US units | The method is what's being demonstrated, not the units |

## 9. Problems hit and how they were solved

| Problem | Solution |
|---|---|
| `uv` installed but not on PATH | Use `python -m uv`, or add Python's Scripts folder to PATH |
| `uv` warns "Failed to hardlink" | Harmless: cache on C:, project on D:. Set `UV_LINK_MODE=copy` to hide it |
| ruff formats code inside Markdown | Added `extend-exclude = ["*.md"]` |
| DuckDB rejects `?` parameters in `CREATE VIEW` | Inline the path as an escaped SQL string (`sql_path`) |
| `.duckdb` file locked while open in the UI or PyCharm | Close the connection before `logops build`, or open in `-readonly` mode |
| Windows terminal can't print DuckDB's box characters | Set `PYTHONIOENCODING=utf-8` |

## 10. Running and checking

```powershell
python -m uv sync                        # install dependencies
python -m uv run logops build            # rebuild the warehouse from dataset/
python -m uv run pytest                  # all tests (including real-data tests)
python -m uv run pytest -m "not slow"    # unit tests only
python -m uv run ruff check .            # lint
duckdb -ui data/warehouse.duckdb         # browse the data in a browser (needs the DuckDB CLI)
```

## 11. Update template (add to §5 after each task)

```markdown
### <Day date> · Task N: <name> ✅
- **Done:** <concrete outputs: files, commands, tables>
- **Result:** <measured numbers: tests, time, rows, findings>
- **Decisions:** <what was chosen, why, what was rejected>
- **Problems:** <if any, and the fix; also add to §9>
```

Then update the "Last updated" line, the §4 table, and §6 and §7.
