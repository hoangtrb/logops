# Capability Map: Logistics Ops Optimizer

> Vietnamese: [CAPABILITY-MAP.vi.md](CAPABILITY-MAP.vi.md) · Data source: [Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database) (Kaggle, not committed)

**Goal:** A portfolio project to show a logistics director (Saigon Co.op) in a job interview.
It turns raw fleet data into cost-saving decisions, presented in a dashboard and
in reports the user can export with one click.

**Audience lens:** A retail-distribution logistics director cares about **cost-to-serve, on-time
delivery, fuel, and fleet utilization**. Every module must answer *"what should I do, and how
much does it save?"*, not just *"what happened?"*

## Modules

| Module id | Responsibility | Depends on |
|---|---|---|
| `data-platform` | CSV → validated Parquet → DuckDB warehouse; data-quality report | — |
| `metrics` | KPI layer (SQL views): cost/mile, on-time %, detention, MPG, idle, utilization, maintenance & safety cost | data-platform |
| `analysis` | Profit, fuel, fleet-capacity and network analyses with rule-based commentary (added 2026-10-03) | metrics |
| `optimize` | Fleet size, lane pricing, late-delivery check, data-process improvements; recommendations table and dashboard page, measured vs upper bound (built 2026-10-04) | metrics, analysis |
| `insights` | Claude API: written summary of KPIs and anomalies per report; questions in plain English → SQL | metrics, optimize |
| `dashboard` | Streamlit + Plotly: 8 pages with commentary next to each chart, VI/EN toggle, responsive (built 2026-10-03); recommendations page and report-export button come with `optimize` and `reports` | metrics, analysis |
| `reports` | One report with every dashboard page as a tab × date range × VI/EN → self-contained responsive HTML or paged PDF with footer, from the CLI or the dashboard (built 2026-10-04) | analysis, optimize, dashboard |

Build order (revised 2026-10-03): `data-platform` → `metrics` → `analysis` → `dashboard` → `optimize` → `reports`. The rule-based commentary in `analysis` covers what `insights` was for; a Claude layer is optional.

## Focus areas (`optimize`) — ranked by director priority

1. **Cost-to-serve & lane profitability.** Cost/mile split into fuel, maintenance, driver and
   empty miles, by route and by customer. Flags loss-making lanes and estimates the rate change
   each one needs.
2. **On-time delivery & detention.** On-time %, detention hours by facility/route/time-of-day.
   An ML model predicts delay risk, with its main drivers explained (the factors that most
   cause delays).
3. **Fuel efficiency.** Outliers in MPG and idle time by truck and by driver. Estimates savings
   ($) if outliers improved to the fleet median. *(Fuel price variance by location was dropped
   after phase 2: prices differ by only $0.02/gallon across cities. See
   `docs/02-data-understanding.md` §3.)*
4. **Fleet utilization & maintenance.** Underused trucks (fleet right-sizing: how many trucks
   are really needed), high-cost/high-downtime trucks, and flags for trucks due for
   maintenance or replacement.

*Stretch (only if time allows):* an LP-based truck/driver-to-load assignment demo (OR-Tools).

## Report types (`reports`)

Built (2026-10-04): one "Transport management report" with every dashboard page as a tab
(overview first), for a date range and a language → responsive HTML or PDF (one sheet per page,
footer with name, export date, page number). Safety & drivers dropped (out of scope).

## CRISP-DM framing

The project is presented as a full CRISP-DM cycle. Each phase produces a visible deliverable:

| CRISP-DM phase | Deliverable | Module |
|---|---|---|
| 1. Business Understanding | `docs/01-business-understanding.md`: director's pain points → KPIs → success criteria (target $ savings) | — (doc) |
| 2. Data Understanding | Data profiling + data-quality report (nulls, inconsistencies such as "New York, AZ", orphan keys) | `data-platform` |
| 3. Data Preparation | Cleaned Parquet + DuckDB star schema + KPI views | `data-platform`, `metrics` |
| 4. Modeling | Optimization / ML recommendation engines | `optimize` |
| 5. Evaluation | Model metrics (e.g. delay model AUC) + savings checked against the business criteria from phase 1 | `optimize`, `docs/05-evaluation.md` |
| 6. Deployment | Dashboard + one-click PDF/HTML reports + Claude narratives | `insights`, `dashboard`, `reports` |

## Decisions

- Keep the dataset as-is (US data: miles, USD). No conversion to km/VND. Framing: the method
  transfers to any distribution network.

- Stack: Python 3.11+, `uv`, DuckDB + Parquet + Polars, Streamlit + Plotly, pytest, git.
  This is not Spark; at ~55 MB that would be overhead with no benefit.
- No scheduled job. Reports are generated on demand.
- LLM: Claude API. Revisit with the user if cost becomes a concern. Cache narratives so
  re-running a report doesn't call the API again.
- Report formats: PDF + HTML.
- Every doc has separate English (`name.md`) and Vietnamese (`name.vi.md`) files.
