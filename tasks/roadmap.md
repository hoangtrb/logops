# Roadmap: Logistics Ops Optimizer

> Vietnamese: [roadmap.vi.md](roadmap.vi.md) · Modules: [CAPABILITY-MAP.md](../CAPABILITY-MAP.md)
> **Deadline: interview on Monday 2026-10-05.** Freeze Sunday 2026-10-04 evening.
> **Status (Sat 2026-10-03):** order revised to `data-platform` → `metrics` → `analysis` → `dashboard`
> → `optimize` → `reports`. Modules 1–4 done; `optimize` parked on branch `feature/optimize`. Live
> progress: [docs/00-project-journal.md](../docs/00-project-journal.md) §4.

## Rules for the weekend

- **Lean modules.** Key tests only (one fixture test per rule/engine, one integration test per
  module). Stretch items are cut first.
- **One spec → plan → build cycle per module**, but the spec and plan stay short (one page each).
- **Demo first.** If time runs out, a working dashboard + one report type beats a perfect
  data-quality layer.
- **Each module ends at a checkpoint**: tests + ruff green, a short human review, then move on.

## Schedule

| When | Module | CRISP-DM phase | Must ship | Cut if late |
|---|---|---|---|---|
| **Fri 10-02** | `data-platform` | 2 Data Understanding, 3 Data Preparation | `logops build` → 14 typed tables in DuckDB; key + value DQ rules; DQ report EN/VI with baselines | `agg_drift` (T6), dedup/perf hardening (T8) |
| **Sat 10-03 AM** | `metrics` | 3 Data Preparation | KPI SQL views: cost/mile (fuel, maintenance, driver, empty miles), on-time %, detention, MPG, idle, utilization, maintenance & safety cost | safety-cost view |
| **Sat 10-03 PM** | `optimize` | 4 Modeling, 5 Evaluation | 4 engines, each with a $ savings estimate: loss-making lanes, delay-risk model (+ main drivers, AUC), fuel outliers vs fleet median, fleet right-sizing + maintenance flags | LP assignment demo (stretch) |
| **Sun 10-04 AM** | `insights` | 6 Deployment | Claude narrative per report (cached); plain-English question → SQL | question → SQL |
| **Sun 10-04 AM** | `dashboard` | 6 Deployment | Streamlit: overview page + one page per focus area + export button | per-page filters beyond date range |
| **Sun 10-04 PM** | `reports` | 6 Deployment | Report type + date range → PDF / HTML; Executive Summary first, then the other 5 types | PDF (keep HTML only) |
| **Sun 10-04 PM** | Demo & docs | 5 Evaluation | `docs/05-evaluation.md`, README (EN/VI), 5-minute demo script, final commit | — |
| **Sun 10-04 evening** | **Freeze** | | Rehearse the demo; no new features | |

## Module task outlines

Detailed tasks live in each module's `tasks/` plan once its spec is written. Module 1 is
already broken down in [todo.md](todo.md).

### 1. data-platform (Fri) — [plan.md](plan.md) · [todo.md](todo.md)
T1 scaffold · T2 one-table slice · T3 all 14 tables · T4 key rules · T5 value rules ·
T6 agg_drift · T7 DQ report EN/VI · T8 hardening · T9 data-understanding docs

### 2. metrics (Sat AM)
1. Spec + plan (short)
2. Cost views: cost/mile split by fuel, maintenance, driver pay, empty miles; by route and customer
3. Service views: on-time %, detention hours by facility / route / time of day
4. Asset views: MPG, idle time, utilization, maintenance cost and downtime per truck
5. Date-range parameter shared by all views; one test per view on fixture data

### 3. optimize (Sat PM)
1. Spec + plan (short)
2. Lane profitability: flag loss-making lanes, required rate change, $ impact
3. Delay risk: gradient-boosting model, AUC, top drivers (feature importance)
4. Fuel: MPG / idle outliers by truck and driver; savings if moved to fleet median
5. Fleet: underused trucks → right-sized fleet count; high-cost / due-for-maintenance flags
6. `recommendations` table (area, item, action, est. savings $) feeding dashboard and reports

### 4. insights (Sun AM)
1. Claude client + narrative prompt per report type; cache by (report, date range, data hash)
2. Plain-English question → SQL against the KPI views (read-only, row-limited)
3. Cost guard: confirm model choice and expected spend with the user before the first real run

### 5. dashboard (Sun AM)
1. Overview: headline KPIs + total estimated savings
2. One page per focus area (cost & lanes, delivery, fuel, fleet & maintenance)
3. Date-range filter, Claude narrative panel, report-export button

### 6. reports (Sun PM)
1. HTML template (self-contained: inline CSS + charts) per report type
2. PDF export from the same HTML
3. CLI `logops report --type ... --from ... --to ... --format pdf|html` + dashboard button

## Daily exit criteria

- **Fri night:** `logops build` works on the real data; DQ report EN/VI generated.
- **Sat night:** KPI views + 4 recommendation engines with $ savings; delay model AUC recorded.
- **Sun evening:** dashboard runs, Executive Summary report exports as PDF + HTML, demo
  script rehearsed, everything committed.
