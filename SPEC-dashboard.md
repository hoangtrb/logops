# Spec: dashboard

> Module 4 of 6 · CRISP-DM phase 6 (Deployment) · Vietnamese: [SPEC-dashboard.vi.md](SPEC-dashboard.vi.md)
> · Inputs: `analysis_bundle()` (module 3) and `kpi()` (module 2)

## Objective

A dashboard the **Logistics Director can explore alone**: figures, charts, and the **generated
commentary** next to the chart it explains. No documents to read, no commands to run.

**Principles**
- **The dashboard computes nothing.** Every number comes from `analysis_bundle()` or `kpi()`, so the
  dashboard always matches the documents and the tests. The dashboard code contains no SQL (tested).
- **Comments sit next to the chart they refer to**, not in one pile.
- Two languages: Vietnamese or English.

## Technology

| Choice | Why |
|---|---|
| **Streamlit** + **Plotly** | Chosen in `CAPABILITY-MAP`. Python, so it calls `analysis_bundle()` directly; interactive charts (hover to see values) |
| **2 new dependencies**: `streamlit`, `plotly` | Approved by the project owner (2026-10-03) |

Started with `uv run logops dashboard`, then opened in the browser at `http://localhost:8501`.

## Outputs: the pages

> **Revised after the component draft was approved (2026-10-03):** 8 pages instead of 7 (a *Delivery
> & service* page was added, and the data page also holds the KPI definitions); a **VI/EN toggle
> button**; every page and component **responsive** (desktop to phone). Margin and fuel price are two
> stacked panels on one time axis, not one chart with two y-axes.

> **Revised again after the second review (2026-10-04):** pages renamed to *Executive overview*,
> *Financial performance*, *Customers & markets*, *Lane performance*, *Delivery performance*,
> *Fleet capacity & utilization*, *Fuel management*, *Data quality & KPI definitions*. Every chart
> shows its unit and a reading note; every table is numbered and filterable by its category
> columns; findings are always tabs; no database names on screen. The daily contribution chart
> was removed (it added noise, not meaning); the lane-count grid became a lane assessment table;
> the delivery page compares four on-time standards; dates are applied with a button.

**Sidebar (every page):** language toggle (Tiếng Việt / English), date range (default 2022–2024,
DD/MM/YYYY).

| # | Page | Content | Comments shown |
|---|---|---|---|
| 1 | **Overview** | Period: whole period or one year (vs the year before). 8 KPI cards with definitions. Finance: revenue, contribution profit, contribution margin, operating cost per mile. Operations & service: OTD, average detention, trips completed, fleet utilization. One findings card. Contribution margin and fuel price, monthly, in two stacked panels | All, in one card with three tabs: Priority, Watch, For reference |
| 2 | **Profit** | Period (month / quarter / year) → where revenue goes (stacked bars), daily contribution with a 30-day mean, **profit-bridge waterfall** between two chosen years, YTD by year, unit economics vs the first year, P&L table | Profit (*Priority*, *Watch*) |
| 3 | **Customers & regions** | Origin / destination toggle → **US map** and margin by state; segments and load types; concentration tiles (largest customer, top 10, top 20, customers for 80%, HHI), Pareto curve, top 15 customers | Profit (*info*) |
| 4 | **Lanes & network** | **Lane-matrix bubbles** (volume × margin, size = revenue, 3 margin tiers) + count per cell; **balance per city** (diverging bars); loads out and in per city; trips starting elsewhere per year; lane table | Network |
| 5 | **Delivery & service** | On-time window slider (0–240 min) → 4 tiles; on-time vs window curve; on-time by month; detention pickup vs delivery by year; on-time by city | — |
| 6 | **Fleet & productivity** | Trucks busy per day with p95, p99, in use, owned; productivity tiles; distribution of trucks busy; utilization per truck; fleet by status; trucks that never ran (description only) | Fleet |
| 7 | **Fuel** | Period → gallons bought vs burned, ratio, average price, spend | Fuel |
| 8 | **Data & definitions** | DQ tiles, findings per rule, how far the data can be trusted, KPI definitions with the fleet value | — |

**Responsive:** tiles and chart pairs sit in columns that stack on narrow screens; every chart
stretches to its container; long category lists use horizontal bars so every label stays readable on
a phone; wide tables scroll sideways.

## Out of scope

| Not done | Why |
|---|---|
| Recommendations with savings | Belong to `optimize` (later); a page is added when it's done |
| PDF/HTML export button | Belongs to `reports` |
| Login, server deployment | Runs locally for the demo |
| LLM commentary | The rules already cover it |

## Success criteria

1. **Every page runs without errors**: an automated test opens each page with Streamlit's testing tool.
2. **No SQL in the dashboard code** (tested).
3. **Dashboard numbers match the documents**: e.g. the revenue tile equals the sum of the yearly P&L (tested).
4. **Each page loads in under 3 s** after the first load (criterion in `docs/01` §5), thanks to caching.
5. Every label in both languages; `ruff` clean.

## Plan

| Task | Content |
|---|---|
| D1 | Dependencies, app skeleton (sidebar, language, cache), `logops dashboard` command |
| D2 | Overview + Profit pages |
| D3 | Segments & regions + Lanes & network pages |
| D4 | Fleet + Fuel + Data quality pages |
| D5 | Tests (each page opens, no SQL, numbers match), load-time check |
| D6 | Module review, `SUMMARY`, journal, page screenshots for the demo |
