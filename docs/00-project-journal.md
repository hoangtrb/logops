# 00 · Project Journal

> Vietnamese: [00-project-journal.vi.md](00-project-journal.vi.md) · Analytical approach: [00-analytical-approach.md](00-analytical-approach.md)
> **Last updated:** Fri 2026-10-02, after Task 9: module `data-platform` complete.

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
│   ├── 02-data-model.*             (generated) ER diagram + data dictionary, from schema.py
│   ├── 02-data-quality-report.*    (generated) data-quality report + baselines
│   ├── 02-dq-rule-thresholds.*     The numbers in the rules and tests: why, and their sources
│   └── 02-data-understanding.*     CRISP-DM phase 2: data analysis, interview talking points
├── tasks/
│   ├── roadmap.md / .vi.md         3-day schedule for all 6 modules
│   ├── plan.md / .vi.md            Plan for the current module (data-platform)
│   └── todo.md / .vi.md            Task list; todo.md (English) is the source of truth for checkboxes
├── src/logops/
│   ├── cli.py                      `logops build` and `logops docs` commands
│   ├── config.py                   All paths, resolved from the repo root
│   └── data_platform/
│       ├── schema.py               Column types, primary and foreign keys of the 14 tables (single source of truth)
│       ├── ingest.py               CSV → typed Parquet, clear error on a type mismatch
│       ├── warehouse.py            Parquet → DuckDB warehouse
│       ├── quality.py              Data-quality rules → `dq_issues` column + `dq_findings` table
│       ├── data_model_doc.py       Generates `docs/02-data-model` from schema.py
│       └── dq_report.py            Generates `docs/02-data-quality-report` from the warehouse
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
- **You commit and push** (repo: https://github.com/hoangtrb/logops). Claude only runs `git add`
  and suggests a message after each task.
- Raw data is never edited. Bad rows are **flagged, not deleted**.
- Lean modules: one test per rule or engine, one integration test per module.
- Commands use `uv`. If `uv` isn't on PATH, use `python -m uv`.

## 4. Overall status

| # | Module | CRISP-DM phase | Planned | Status |
|---|---|---|---|---|
| — | Business understanding (`docs/01`) | 1 | Thu 10-01 | ✅ Done |
| 1 | `data-platform` | 2, 3 | Fri 10-02 | ✅ Done (7 tasks; Tasks 6 and 8 cut). Awaiting Checkpoint C review |
| 2 | `metrics` | 3 | Sat 10-03 AM | ⏳ Not started |
| 3 | `optimize` | 4, 5 | Sat 10-03 PM | ⏳ |
| 4 | `insights` | 6 | Sun 10-04 AM | ⏳ |
| 5 | `dashboard` | 6 | Sun 10-04 AM | ⏳ |
| 6 | `reports` | 6 | Sun 10-04 PM | ⏳ |
| — | Demo, evaluation, freeze | 5 | Sun 10-04 evening | ⏳ |

Module 1 progress: █████████ complete (7 tasks done, 2 cut with reasons).

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

### Fri 10-02 · Checkpoint A and first commit ✅
- The warehouse passed Checkpoint A. The first commit `61e34a7` is pushed to
  [github.com/hoangtrb/logops](https://github.com/hoangtrb/logops).
- `*.html` Markdown previews were added to `.gitignore`.

### Fri 10-02 · Task 4: Data-quality engine + key rules ✅
- **Done:**
  - `quality.py`: each rule is data, `Rule(table, id, severity, predicate, column)`, where
    `predicate` is a SQL condition that is TRUE when a row violates the rule.
  - The 3 key rules are **generated** from the primary and foreign keys declared in `schema.py`:
    `pk_unique` (error), `fk_missing` (warn), `fk_orphan` (error). 50 rules across the 14 tables (14 primary keys, 18 foreign keys × 2).
  - Every table gets a `dq_issues` column listing the row's problems (empty when clean). The
    `dq_findings` table records each rule's violation count and 3 sample keys, including rules
    with 0 violations.
  - `logops build` runs this step and prints a summary.
- **Result:** 17 tests green. Building all 14 tables with the checks takes 5.4 s. No rows deleted.
- **Findings on the real data:**
  - **No duplicate primary keys and no orphan foreign keys** in any of the 14 tables: the
    relationships between tables are intact.
  - Only empty foreign keys (warnings):

    | Column | Empty rows |
    |---|---:|
    | `fuel_purchases.driver_id` | 3,988 |
    | `fuel_purchases.truck_id` | 3,880 |
    | `trips.driver_id` | 1,714 |
    | `trips.trailer_id` | 1,680 |
    | `trips.truck_id` | 1,672 |
    | `safety_incidents.truck_id` / `driver_id` | 1 / 1 |

  - **The pattern looks random**, about 2% per column: 4,838 trips miss one ID, 114 miss two,
    none miss all three. That's typical of deliberate noise in synthetic data, not a systemic
    error.
  - Missing drivers on fuel purchases **can't be recovered** from the trip: every fuel purchase
    without a driver belongs to a trip that also has no driver.
  - **Impact:** $3.76M of the $95.6M fuel spend (3.9%) can't be attributed to a driver or truck.
- **Decisions:**
  - `fk_missing` is a *warn*, while `pk_unique` and `fk_orphan` are *errors*. A missing ID is
    missing information; a duplicate key or an orphan ID is wrong data.
  - Later modules will **keep** these rows when totalling fleet costs but **exclude** them when
    ranking drivers and trucks. That's exactly why rows are flagged instead of deleted.
  - Each run sorts tables by primary key, so results are stable between builds.

### Sat 10-03 · Data model diagram (addition) ✅
- **Why:** DBeaver shows no primary/foreign keys because the warehouse deliberately declares no
  physical constraints. A test showed that DuckDB constraints stop the build on a bad row and
  block rebuilding parent tables.
- **Done:** `logops docs` generates `docs/02-data-model.md` / `.vi.md` from `schema.py`: a Mermaid
  diagram (rendered by GitHub) and a data dictionary. A test fails if the doc drifts from
  `schema.py`.
- **Rejected:** real PK/FK constraints in DuckDB (kept for Task 8 if time allows); DBeaver virtual
  keys (manual, one machine only).
- **Docs addition:** `00-analytical-approach` §3.4 on missing data (Rubin: MCAR/MAR/MNAR). The
  check shows missing `driver_id` is MCAR, so rows are kept and handled per analysis.

### Sat 10-03 · Tasks 6 and 8 cut ✂️
- **Why:** a one-off check showed both would only report "0 errors". The monthly tables match
  recomputed values 100% (drivers and trucks, maintenance included); 0 duplicate rows; the build is
  already stable and takes 5.4 s.
- **Instead:** both checks appear in the DQ report (Cross-checks section), recomputed by SQL on
  every build.

### Sat 10-03 · Task 5: Value rules ✅
- **Done:** 20 value rules in `VALUE_RULES` (`range`, `amount_mismatch`, `time_order`,
  `geo_mismatch`, `idle_exceeds_duration`); `all_rules()` combines them with the key rules for 70
  rules in total. `logops build` explains clearly when DBeaver is holding the warehouse file.
- **Result:** 47 tests green; load + checks take 2.8 s. 14 of 70 rules found violations.
- **Key findings:**
  - `on_time_flag` = arrival within **±2 hours** of the appointment (100% match). More than 2 hours
    early counts as not on time.
  - `delivery_events.facility_id` is essentially random (3.4% match with the lane);
    `location_city` matches 100%.
  - The state on fuel purchases is wrong 95% of the time ("Denver, TX"); fuel prices differ by only
    $0.02/gallon across cities.
  - 7,450 trips (8.7%) have idle time longer than the trip itself.
- **Decisions:** every threshold's source is documented in `docs/02-dq-rule-thresholds`. (The
  hiring-age rule was later removed; see the entry below.)

### Sat 10-03 · Task 7: Data-quality report ✅
- **Done:** `dq_report.py` computes every number once with SQL and renders both languages:
  `docs/02-data-quality-report.md` / `.vi.md`. Summary, baselines, findings with 3 sample keys,
  rule definitions, cross-checks, missing values. Re-runs are byte-identical.
- **Result:** measured operating cost $104.0M (fuel 92%), $0.851/mile, MPG 6.45, 44.6% of
  deliveries within the window, and only **1.5% of rows with an error-level issue**.
- **Problems:** `|` broke Markdown tables (now escaped); "66.4% of rows have an issue" was
  misleading, so error-level rows are now counted separately.

### Sat 10-03 · Thresholds and sources doc ✅
- **Done:** `docs/02-dq-rule-thresholds` explains every number in the rules and tests: where it's used,
  why, and its source (data profile, regulation, definition, spec, test design).

### Sat 10-03 · Task 9: Data understanding ✅
- **Done:** `docs/02-data-understanding` (EN/VI): what the data covers, baselines, a trust table,
  the real meaning of `on_time_flag`, downstream impact, the success-criteria check, interview
  talking points.
- **Also updated:**
  - `docs/01` §3 and §5: savings target = **≥ $3.1M over 3 years**.
  - `00-analytical-approach` §5 and §6: location analysis uses `location_city`; the fuel-price-by-
    location lever is dropped.
  - `CAPABILITY-MAP`: note on the dropped lever.

### Sat 10-03 · Hiring-age rule removed ✅
- **Why:** the project owner decided the project focuses on **operational productivity and
  quality**, not HR compliance (the 18-vs-21 question no longer needs an answer).
- **Done:** removed `time_order:date_of_birth` from `quality.py`; **69 rules** remain (19 value
  rules; 43 errors, 26 warnings). Updated the report definitions, tests, `02-dq-rule-thresholds`
  (including the line numbers in its verification table) and `02-data-understanding`.
- **Result:** the project owner disconnected DBeaver and ran the build; the re-run after the change
  takes 8.0 s, 47 tests green. The DQ report changed in exactly the 3 related lines.

## 6. In progress

**Checkpoint C: module 1 complete.** The warehouse has been rebuilt with all 69 rules; the hiring-age
question is closed (rule removed). What's left: review using the checklist below, then commit.

### Review checklist (saved 10-03, for you to check on 10-04)

All changes from Task 5 to Task 9 are **staged, not committed**. Check them in this order, then commit.

- [ ] **`docs/02-data-understanding.md`**: read first. Are the trust table (§3), the `on_time_flag`
      definition (§4) and the 4 interview talking points (§7) convincing?
- [ ] **`docs/02-dq-rule-thresholds.md`**: each threshold with its reason and source. §6 maps every
      number to its line of code. Look closely at the rules *without their own test* (§5).
- [ ] **`docs/02-data-quality-report.md`** (generated): do the §2 baselines look reasonable?
- [ ] **`docs/01-business-understanding.md`** §3 and §5: target ≥ $3.1M over 3 years.
- [ ] **`docs/00-analytical-approach.md`** §5–§6: `location_city` used; fuel-price lever dropped.
- [ ] **Code:** `src/logops/data_platform/quality.py` (19 value rules) and `dq_report.py`.
- [x] ~~Disconnect DBeaver and build~~ (done 10-03). **Re-run while reviewing:** `python -m uv run logops build` → `python -m uv run pytest`
      (expect 47 passing) → `git status` (the DQ report should be unchanged).
- [ ] **Commit + push** (message suggested in the 10-03 conversation, or write your own).

## 7. Next

**Module 2 `metrics`** (SQL KPI views): spec → plan → build, applying the adjustments in
`docs/02-data-understanding` §5.

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
| `.duckdb` file locked while open in the UI, PyCharm or DBeaver | Disconnect before `logops build` (the command now says why), or open in `-readonly` mode |
| `\|` broke Markdown table cells | Escaped as `\\|` when rendering the report (`_cell`) |
| Windows terminal can't print DuckDB's box characters | Set `PYTHONIOENCODING=utf-8` |

## 10. Running and checking

```powershell
python -m uv sync                        # install dependencies
python -m uv run logops build            # rebuild the warehouse from dataset/
python -m uv run logops docs             # regenerate the data model diagram
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
