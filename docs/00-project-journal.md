# 00 · Project Journal

> Vietnamese: [00-project-journal.vi.md](00-project-journal.vi.md) · Analytical approach: [00-analytical-approach.md](00-analytical-approach.md)
> **Last updated:** Sun 2026-10-04, dashboard second review. One-page overview: [SUMMARY.md](SUMMARY.md).

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
├── SPEC-data-platform.md / .vi.md  Spec for module 1
├── SPEC-metrics.md / .vi.md        Spec for module 2: outputs defined before coding
├── SPEC-analysis.md / .vi.md       Spec for module 3
├── SPEC-dashboard.md / .vi.md      Spec for module 4: the 8 pages
├── .streamlit/config.toml          Dashboard theme (light, project palette)
├── pyproject.toml, uv.lock         Dependencies (managed by uv)
├── docs/
│   ├── 00-project-journal.*        ← this file: progress log
│   ├── 00-analytical-approach.*    Theory and reasons behind each method
│   ├── 01-business-understanding.* CRISP-DM phase 1: director's questions → KPIs → success criteria
│   ├── 02-data-model.*             (generated) ER diagram + data dictionary, from schema.py
│   ├── 02-data-quality-report.*    (generated) data-quality report + baselines
│   ├── 02-dq-rule-thresholds.*     The numbers in the rules and tests: why, and their sources
│   ├── 02-data-understanding.*     CRISP-DM phase 2: data analysis, interview talking points
│   ├── 03-kpi-definitions.*        (generated) 21 KPIs: formula, unit, fleet value
│   ├── reviews/NN-<module>.*       End-of-module review: outputs, real figures, what wasn't done
│   └── SUMMARY.*                   Project-wide summary, updated at the end of each module
├── tasks/
│   ├── roadmap.md / .vi.md         3-day schedule for all 6 modules
│   ├── plan.md / .vi.md            Plan for the current module (data-platform)
│   └── todo.md / .vi.md            Task list; todo.md (English) is the source of truth for checkboxes
├── src/logops/
│   ├── cli.py                      `logops build`, `docs`, `kpi`, `insights`, `dashboard` commands
│   ├── config.py                   All paths, resolved from the repo root
│   └── data_platform/
│       ├── schema.py               Column types, primary and foreign keys of the 14 tables (single source of truth)
│       ├── ingest.py               CSV → typed Parquet, clear error on a type mismatch
│       ├── warehouse.py            Parquet → DuckDB warehouse
│       ├── quality.py              Data-quality rules → `dq_issues` column + `dq_findings` table
│       ├── data_model_doc.py       Generates `docs/02-data-model` from schema.py
│       └── dq_report.py            Generates `docs/02-data-quality-report` from the warehouse
│   └── metrics/
│       ├── views.py                3 base views: trip_economics, delivery_performance, truck_economics
│       ├── kpis.py                 The 21-KPI catalog + kpi()
│       └── kpi_doc.py              Generates `docs/03-kpi-definitions`
│   └── analysis/
│       ├── profit.py, operations.py  P&L, bridge, dimensions; fuel, capacity, lanes, network
│       ├── service.py              On-time, detention, fleet status and daily views for the dashboard
│       ├── insights.py             Rule-based EN/VI commentary
│       └── bundle.py, doc.py       analysis_bundle(); generates `docs/03-analysis-insights`
│   └── dashboard/
│       ├── app.py                  Streamlit entry: sidebar (language, dates) + navigation
│       ├── data.py                 The only module that opens the warehouse (read-only, cached)
│       ├── charts.py               Plotly builders: one palette, one number format
│       ├── pages.py                The 8 pages
│       └── i18n.py                 Every label in VI and EN
├── tests/
│   ├── fixtures/                   Tiny hand-made CSVs with deliberate defects
│   ├── test_smoke.py               CLI and paths
│   ├── data_platform/              Ingest, schema, and integration tests on the real data
│   ├── metrics/                    Hand-computable fixture warehouse + real-data reconciliation tests
│   ├── analysis/                   Unit and real-data tests for the analyses and commentary
│   └── dashboard/                  Every page runs (VI/EN), no SQL, numbers match, load time
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
| 1 | `data-platform` | 2, 3 | Fri 10-02 | ✅ Done (7 tasks; Tasks 6 and 8 cut) |
| 2 | `metrics` | 3 | Sat 10-03 AM | ✅ Done (29 tests), commit `e99d12a` |
| 3 | `analysis` | 2, 3 | Sat 10-03 evening | ✅ Done (12 tests), commit `fc4b1ed` |
| 4 | `dashboard` | 6 | Sun 10-04 AM | ✅ Done Sat 10-03 (26 tests); revised after two reviews. Awaiting commit |
| 5 | `optimize` | 4, 5 | After the analysis | ⏸️ On branch `feature/optimize` |
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

### Sat 10-03 · Module 2 `metrics` ✅
- **Spec first:** `SPEC-metrics` defines the outputs (3 views, 21 KPIs, a command, docs), an
  out-of-scope list and success criteria. Approved before coding.
- **Done:** `views.py` (3 base views; fuel allocated by gallons burned within the month,
  maintenance by truck-month miles); `kpis.py` (21 KPIs, 7 groupings, date filter, "Unattributed"
  line); the `logops kpi` command; the generated `docs/03-kpi-definitions`.
- **Result:** all 6 success criteria met. Totals match the source tables; 76 tests pass; build
  6.6–7.4 s.
- **Findings:** 28 of 120 trucks ran no trip ($1.40M maintenance); 29% more gallons bought than
  burned, on every truck; volume nearly flat (+1.3%); lane margins 50.4–72.7%.
- **Problems:** `|` in a formula broke a table (now escaped); module 1's old CLI test had to stub
  the steps that need all 14 tables.
- **Reviews:** [reviews/02-metrics.md](reviews/02-metrics.md); module 1:
  [reviews/01-data-platform.md](reviews/01-data-platform.md).

### Sat 10-03 · Reordered: analysis first, optimize later
- The project owner decided to do the analysis first. The optimize work so far moved to branch
  `feature/optimize` (pushed), to be redone once the analysis is in.

### Sat 10-03 · Module 3 `analysis` ✅
- **Spec agreed with the project owner:** profit tracked the way businesses do; no external data (not
  even coordinates); weekday, seasonality, operating ratio, empty miles and the fuel hypothesis dropped.
- **Done:** `src/logops/analysis/` with `profit.py` (P&L by period, profit bridge, unit economics,
  business dimensions, customer concentration), `operations.py` (fuel, fleet capacity, lane matrix,
  network balance, changed start points), `insights.py` (12 rules), `bundle.py`, `doc.py`; the
  `logops insights` command; generated `docs/03-analysis-insights`; state and load-type dimensions
  added to the KPI layer.
- **Result:** 93 tests pass. 93% of the profit gain comes from fuel prices; 33% of loads end where
  there's no return load; peak days can't be forecast.
- **Notebook check:** found the repositioning cost that is always $0, seasonality caused by month
  length, and the assumed figures.
- **Fixed along the way:** group shares adding up to over 100% (denominator changed); a hard-coded
  digit in a comment template (caught by the test).
- **Review:** [reviews/03-analysis.md](reviews/03-analysis.md).

### Sat 10-03 · Module 4 `dashboard` ✅
- **Agreed with the project owner:** component draft approved; Vietnamese by default with a VI/EN
  toggle; every page and component responsive; Delivery & service page and KPI definitions kept;
  `streamlit` and `plotly` added (approved). Layout tweaks come after the finished product.
- **Done:** `src/logops/dashboard/` (`app.py` navigation and sidebar, `data.py` the only module that
  opens the warehouse, read-only and cached, `charts.py` 19 Plotly builders on the validated palette,
  `pages.py` 8 pages, `i18n.py` 174 labels per language); `analysis/service.py` for service, fleet and
  daily views; the `logops dashboard` command; `.streamlit/config.toml` (light theme).
- **Result:** 8 pages, 27 charts, 6 tables. 114 tests pass (21 new), `ruff` clean. First load about
  10 s (the analysis bundle), then each page under 3 s (tested).
- **Visual check:** every page screenshotted at 1440 px and 390 px; 9 problems found and fixed (list in
  the review), e.g. scrambled month order, clipped bar labels, overlapping reference labels.
- **Review:** [reviews/04-dashboard.md](reviews/04-dashboard.md).

### Sat 10-03 · Dashboard: overview redesign after review ✅
- **Feedback:** overview stuck on the last year, uneven cards, unclear KPI names (±2 h window, trucks
  busy at p95), unclear "margin", comments split into many boxes, layout not tidy.
- **Done:** period selector (whole period / each year, compared with the year before); equal-size
  HTML KPI cards (`dashboard/ui.py`) grouped as Finance and Operations & service; KPIs renamed to
  OTD, detention, trips, fleet utilization, each with a definition; one findings card per page;
  charts in white cards; theme and toolbar settings; `analysis/service.scorecard()`.
- **Decisions:** OTIF not shown (no delivered vs ordered quantity in the data); fleet utilization =
  average trucks with a trip per day ÷ trucks owned (55.1%); the dataset's `utilization_rate` kept
  only for comparing trucks.
- **Result:** 116 tests pass, `ruff` clean; screenshots checked at desktop and phone widths, VI and EN.

### Sun 10-04 · Findings rewritten: three tabs, explicit good/bad, impact and action ✅
- **Feedback:** findings repeated "act" on every row and didn't say whether they were good or bad,
  what they change, or what to do; "act" was a vague name.
- **Done:** levels renamed **Priority / Watch / For reference** and shown as tabs; each finding now
  has a title, a tone (positive / negative / risk / neutral), what happened, impact (or meaning) and a
  recommended action for priority and watch items; idle-truck facts added to the bundle;
  `docs/03-analysis-insights` regenerated with one block per finding; CLI prints the tone.
- **Checked:** fuel surcharge per mile is flat ($0.245) in all three years while fuel fell from $4.20
  to $3.65 per gallon, so "the surcharge doesn't follow fuel prices" holds.
- **Result:** 118 tests pass, `ruff` clean; screenshots checked on desktop and phone.

### Sun 10-04 · Dashboard second review: units, wording, tables, delivery standards ✅
- **Feedback:** date picker misbehaving; findings not tabbed everywhere; missing units; unclear
  daily chart, lane-count grid, fleet notes and productivity labels; database names on screen; no
  Excel-like filters; unprofessional wording; is ±2 h fair for multi-day trips?
- **Done:** date form with Apply (AppTest); tabbed findings on every page; unit chip and reading
  note on every chart (idea from the project owner's reference report); lane assessment table;
  four on-time standards with lateness spread and by-trip-length view (`service.delivery_timing`);
  pages renamed; plain names for KPIs (`kpis.TITLES`, formulas in words), data-quality tables,
  columns and rules; numbered, filterable tables; daily chart removed.
- **Finding:** delivery timing is spread evenly from 3 h early to 6 h late and doesn't depend on
  trip length; on the appointment date 91.2% are on time vs 44.6% within ±2 h.
- **Result:** 119 tests pass, `ruff` clean; screenshots checked on desktop and phone.

### Sun 10-04 · Dashboard third review ✅
- Segments renamed and defined (contract, dedicated fleet, spot); lane action "consider exiting"
  replaced by "review rates" (every lane is profitable; tiers are relative); repositioning compared
  with random assignment (95.4% expected vs 95.5% observed: no trip chaining); delivery deviation
  chart on a real hour axis. Empty running moved to `optimize`. 119 tests pass.

### Sun 10-04 · Dashboard look made distinct from the reference report ✅
- UI accent changed to deep teal `#0F5257` on warm paper; page banner is a white card with a teal edge (no blue gradient); charts now use Streamlit's own Source Sans, so the whole page shares one font. Chart data colors unchanged (validated palette).

### Sun 10-04 · Dashboard layout fixes ✅
- No overflow at 1440/1280/1024/768/390 px (container-query grids, wrapping tables, unit-free bar labels); tabs keep their selection; findings collapsible with a tone legend; "tr USD"; KPI table column order fixed. 120 tests pass.

### Sun 10-04 · Module 5 `optimize` (redone) ✅
- **Scope agreed:** O1 fleet, O2 lane pricing, O4 late deliveries, O5 data process, O6
  recommendations and dashboard page; O3 trip chaining optional (not done). Target may be exceeded.
- **Done:** ported `optimize/` from `feature/optimize`; daily demand and lane groups aligned with
  the analysis layer and dashboard; new `lateness.py` (no persistent cause); new gap "moves between
  trips not recorded"; bilingual recommendations with evidence computed from the data; dashboard
  page "Optimization recommendations"; `logops optimize`; generated `docs/04`, `docs/05`.
- **Result:** measured $0.47M/year (45% of target), upper bound $2.42M, total potential $2.89M
  (278%); unexplained fuel $7.24M not counted. 148 tests pass.
- **Review:** [reviews/05-optimize.md](reviews/05-optimize.md).

### Sun 10-04 · Module 6 `reports` ✅
- **Done:** `src/logops/reports/` (`build.py` five report types from the dashboard's charts and
  components, `pdf.py` headless Edge/Chrome print); `logops report`; sidebar "Export report".
- **Result:** HTML self-contained (~4.7 MB), PDF in about 2 s after a 10–15 s build; 157 tests pass.
- **Review:** [reviews/06-reports.md](reviews/06-reports.md).

### Sun 10-04 · Dashboard and report follow-ups ✅
- **Done:** optimization details moved next to their topic (fleet plan → fleet, lane pricing →
  lanes, lateness check → delivery, indexed surcharge → fuel, data-process gaps → data); the
  optimization page keeps the summary with a "details on page" column. Volume scenario renamed
  ("Current volume", "+5%"…). Language buttons "Vi"/"En". Report export runs on a worker thread:
  the dashboard stays usable, a toast and a green Download button appear when done. Report
  findings show as tabs (printed: all levels).
- **Open:** report content proposal v2 in [SPEC-reports.md](../SPEC-reports.md), awaiting review.

### Sun 10-04 · Optimization page and the single report ✅
- **Done:** optimization back on one page, placed before the data page. Report export reworked as
  the owner asked: one report with every dashboard page as a tab (header with title, export date
  and period), drawn by the page code through an HTML builder; responsive HTML; PDF with one sheet
  per page and a footer (name, export date, page x / y). Sidebar export shows a status line and a
  Download button that fills with green while the report is made. Overview adds operating cost.
- **Result:** 155 tests pass; PDF for 2022–2024 is 48 pages.

### Sun 10-04 · Project card, savings explained, print layout ✅
- **Done:** project and data-source card (overview, report cover); icons removed; report tabs in
  two rows; trust levels as coloured text; "upper bound" renamed "maximum potential" and the four
  savings cards explain their figures on hover (printed in the PDF), including what it takes to
  reach the target ($0.57M more, 23.7% of the potential); PDF print layout rebuilt (cover,
  contents, numbered sections, figures and tables, landscape sheets for wide tables, no cut).
- **Result:** 156 tests pass; PDF for 2022–2024 is 43 pages.

### Sun 10-04 · PDF as a written report ✅
- **Done:** the PDF is typeset as a document: Times New Roman, black text, dark blue headings,
  11 pt body, 20 mm margins; findings as numbered paragraphs, KPI cards as a table (with how each
  figure is computed), tables with thin horizontal rules, no boxes; charts use the same typeface.
  The HTML report and the dashboard keep their cards.
- **Result:** 156 tests pass; PDF for 2022–2024 is 49 pages.

### Sun 10-04 · PDF front matter ✅
- **Done:** cover with a photo (reports/assets/cover.jpg, optional) and the project facts set off;
  contents, list of figures and list of tables with page numbers and links (two prints: the first
  one's named destinations give the pages); executive summary page (results, act now, keep
  watching, savings); findings with coloured level headings, bullets and the action set off.
- **Result:** 157 tests pass; PDF for 2022–2024 is 55 pages (31 figures, 11 tables).

### Sun 10-04 · O3 trip chaining ✅
- **Done:** `optimize/chaining.py` replays every load at its actual times under two dispatch rules
  (as today: truck idle longest; chaining: a truck already in the pickup city first), 12/24/48 h
  allowed to reach another city; recommendation of type "estimate"; dashboard section with a
  cost-per-move input; evaluation doc section. Report cover photo moved below the project facts.
- **Result:** as-today replay 95.3% of trips needing a move (observed 95.4%); chaining 35.4%,
  17,018 fewer moves a year, trucks needed −14.6%; $4.63M a year at $272 a move (hypothesis, not
  in totals). 159 tests pass.

### Sun 10-04 · Interview preparation ✅
- **Done:** README (at a glance, how to use, modules) and `docs/demo-script` (7-minute walk-through,
  checklist, likely questions) in EN/VI; fallback reports (VI/EN, PDF/HTML) in `reports/output/`.
- **Result:** 159 tests pass, `ruff` clean.

### Sun 10-04 · O3 reworked: nearest truck, distances and fuel ✅
- **Changed (owner):** no $272-a-move hypothesis. Each load goes to the nearest free truck;
  distances over the lanes (shortest path), an empty mile at $0.605 (fuel price ÷ mpg, from the data).
  No fixed limit on the empty drive (any limit up to 24 h needs thousands of extra trucks); moves
  within one 11-hour driving day are reported (33%).
- **Result:** trips needing a move 89.5% → 41.1%, empty miles −59.5%, trucks 211 → 195 in the replay;
  the model's $12.56M exceeds the fuel bought off trips, so the cut is applied to that fuel: up to
  $4.27M a year (estimate, not in totals). 160 tests pass.

### Mon 10-05 · Handoff, report wording, chaining check ✅
- **Done:** `docs/handoff` (EN/VI): setup on another computer, files to copy by hand, run, checklist,
  common problems, key figures, working rules for Claude. Report: the "sidebar" sentence removed (the
  report says the recommendations use all the data only when its period is shorter). Lane balance
  order fixed for ties (rebuilds leave the docs unchanged). Trip chaining checked: dry-van and
  refrigerated fleets apart 63.4% cut; dedicated loads kept as today 33.0% ($2.37M).
- **Result:** 160 tests pass; `logops build` 20.5 s; PDF export about 28 s from the CLI.

### Mon 10-05 · Trip chaining dropped ✅
- **Decided (owner):** O3 trip chaining removed from code, dashboard, reports and docs: its result
  swings with dry-van vs refrigerated trucks, dedicated trucks (50% of loads) and distances the data
  can't give. The repositioning finding now recommends recording every move between trips first.
- **Result:** 157 tests pass; savings figures unchanged ($0.47M measured, $2.42M maximum potential,
  $2.89M total).

## 6. In progress

**Module 4 `dashboard` is done and awaits your review, then a commit.**
1. Run: `python -m uv run logops dashboard` (first load about 10 s), try the VI/EN button and a
   phone-width window.
2. Read [reviews/04-dashboard.md](reviews/04-dashboard.md): outputs vs the spec, what was fixed,
   caveats for the demo.
3. Note the layout changes you want; they are applied after your review.

## 7. Next

**Sunday:** your dashboard layout changes → `optimize` (redone from branch `feature/optimize`,
adding backhaul matching; a recommendations page in the dashboard) → `reports` → demo script → freeze.

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
| Running dashboard kept showing old charts after a code change | Restart `logops dashboard` (Streamlit doesn't always reload imported modules) |
| A chart's lines zigzagged | A join scrambled the row order: sort time series in the analysis layer (now tested) |

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
