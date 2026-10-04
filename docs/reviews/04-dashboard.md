# Review · Module 4: `dashboard`

> CRISP-DM phase 6 (Deployment) · Vietnamese: [04-dashboard.vi.md](04-dashboard.vi.md)
> · Spec: [SPEC-dashboard.md](../../SPEC-dashboard.md) · Summary: [SUMMARY.md](../SUMMARY.md)
> **Status:** completed 2026-10-03, not yet committed · **Rule:** only verified facts.

## 1. Context

A Streamlit + Plotly dashboard the Logistics Director can explore alone. The project owner approved
the component draft with three changes: **Vietnamese by default with a VI/EN toggle button**, **every
page and component responsive**, and both the *Delivery & service* page and the KPI definitions kept.
Layout details will be adjusted by the project owner after seeing the finished product.

## 2. Outputs vs the spec

| Output | Delivered | Evidence |
|---|---|---|
| 8 pages: Overview, Profit, Customers & regions, Lanes & network, Delivery & service, Fleet & productivity, Fuel, Data & definitions | ✅ 27 charts, 6 tables, tiles on every page | Every page runs in both languages (16 tests) |
| Commentary next to the chart it explains | ✅ Overview shows all (filter by level); each page shows its topic | — |
| VI/EN toggle | ✅ Sidebar button; 174 labels per language, numbers formatted per language (1.234,5 / 1,234.5), VI date ticks as MM/YYYY | Same label keys in both languages (test) |
| Responsive | ✅ Columns stack on narrow screens; charts stretch; long lists as horizontal bars; wide tables scroll | Screenshots at 1440 px and 390 px reviewed page by page |
| The dashboard computes nothing | ✅ Reads `analysis_bundle()`, `kpi()` and the new `analysis/service.py`; the read-only connection is opened only in `dashboard/data.py` | No SQL in the dashboard code (test) |
| Numbers match the analysis layer | ✅ | Revenue, contribution and margin tiles equal the yearly P&L read separately (test) |
| Each page under 3 s once cached | ✅ | Each page re-run timed in the test, all 16 page × language runs under 3 s |
| `logops dashboard` command | ✅ Opens the browser on port 8501 | — |

**Tests:** 21 new (20 dashboard, 1 analysis); 114 in total, all passing; `ruff` clean.

**Added to the analysis layer for the dashboard** (so the dashboard keeps holding no SQL):
`analysis/service.py` (on-time by window, by month and city, detention by type, fleet status, trucks
that never ran, truck productivity, daily contribution with a 30-day mean, data bounds) and a *day*
period in `profit.py`.

## 3. Visual check: problems found and fixed

Every page was screenshotted at desktop (1440 px) and phone (390 px) widths and read before closing.

| Problem | Fix |
|---|---|
| Margin and fuel lines zigzagged | The join scrambled the month order: sorted in the analysis layer, plus a test that time series are in time order |
| P&L table showed "None" for comparisons with no earlier period | Shown as "—" |
| Unit-economics tiles said "vs last year" while comparing with the first year | Now "vs 2022" (the first year in range) |
| English month names on Vietnamese date axes | VI date axes use MM/YYYY |
| Value labels cut off at the end of horizontal bars; Los Angeles' label overlapped its name | Axis range padded beyond the longest bar |
| p95 and p99 labels (73 and 75 trucks) printed on top of each other, under the data line | Reference lines named in the legend instead |
| City names skipped on phones in the loads out/in chart | Changed to horizontal bars |
| Truck status, SCOR area and segment names shown in English on the VI page | Translated |
| Trucks tile used the delta arrow to show text | Value shown as "73 / 120" with an explanation |

## 4. Caveats for presenting

- **The first load takes about 10 s** (computing `analysis_bundle()` measured 10.2–10.3 s); after
  that each page loads in under 3 s. Picking a **new date range** recomputes (about 10 s again).
  **Open the dashboard once before the demo.**
- **The US map needs an internet connection**: Plotly downloads the state shapes when the map is
  drawn. The other charts work offline.
- The overview tiles show **the last year in the chosen range** compared with the year before (the
  caption says which year), not the whole range.
- Profit is still **contribution before driver pay and overhead** (the data has neither).

## 5. Not done (by design)

| Not done | Why |
|---|---|
| Recommendations with savings | Belong to `optimize` (redone later); a page will be added |
| PDF/HTML export button | Belongs to `reports` |
| Login, server deployment | Runs locally for the demo |

## 6. Handed over

- **Optimize** (redone from `feature/optimize`): a recommendations page plugs into the same
  `pages.py` / `i18n.py` pattern.
- **Reports**: can reuse `charts.py` (same palette and number formatting) for the HTML reports.

## 7. Reproduce

```powershell
python -m uv run logops build        # once, if data/warehouse.duckdb is missing
python -m uv run logops dashboard    # opens http://localhost:8501
python -m uv run pytest tests/dashboard -m "slow or not slow"   # this module's 20 tests
```

## 8. Changes after the project owner's first review (2026-10-03)

| Feedback | Change |
|---|---|
| Overview only showed the last year | Period selector: *Whole period* or one year; a year is compared with the year before when both are whole years in the range |
| Cards had different sizes | KPI cards are now an HTML grid (`dashboard/ui.py`): same size per row, 4 → 2 → 1 columns as the screen narrows |
| "Within ±2 h" and "trucks busy (95% of days)" were unclear | Logistics KPI names with a one-line definition on each card: **On-time delivery (OTD)**, average detention, trips completed, **fleet utilization** (average trucks with a trip per day ÷ trucks owned, 55.1%). OTIF is not shown: the data has no delivered vs ordered quantity, so *in full* can't be measured |
| What "margin" means | Named **contribution margin** everywhere, with its formula under the chart: (revenue − fuel − maintenance − claims) ÷ revenue, before driver pay and overhead |
| Comments in many coloured boxes | One findings card per page, most urgent first, *info* rows folded under "show more" |
| Layout not tidy | Charts in white cards with the title inside; lighter page background; toolbar hidden; heading sizes set in `.streamlit/config.toml`; value labels inside the bar end when they fit |

The overview figures come from a new `analysis/service.scorecard()` (money from the P&L, delivery
from the KPI layer, fleet utilization from trucks busy per day), so the dashboard still computes
nothing. On the fleet page, the dataset's `utilization_rate` column is labelled as a column of
unknown definition (it exceeds 100%), used only to compare trucks.

**Tests:** 116 in total, all passing (scorecard reconciles with the yearly P&L and capacity; cards
match the scorecard; findings card and KPI grid tested on their own).

## 9. Findings rewritten (2026-10-04)

Feedback: the findings list repeated "act" on every row, didn't say whether a finding was good or
bad news or what it changes, and "act" was a vague name.

| Change | Detail |
|---|---|
| Three tabs | **Priority** · **Watch** · **For reference**, with counts; the level is no longer repeated on each finding. A page with one level shows it as a caption instead of a single tab |
| Each finding is explicit | A plain title, a **tone** (positive, negative, risk, neutral), then *what happened*, *impact* (*what it means* for reference items) and, for priority and watch items, a *recommended* action |
| Impact in money where the data allows | Fleet: 40 trucks above the busiest day's need, 28 never ran a trip yet cost $1.40M in maintenance (new facts in the bundle). Profit: if fuel prices return to 2022 levels, contribution falls by about $4.12M a year (the bridge's fuel-price part) |
| Checked before writing | "The fuel surcharge doesn't follow the fuel price": surcharge per mile $0.245 in 2022, 2023 and 2024 while the average fuel price fell from $4.20 to $3.65 per gallon |
| One source for the text | Level, tone, topic and part labels live in `analysis/insights.py`, used by the dashboard, the CLI and `docs/03-analysis-insights` (now one block per finding) |

Not quantified on purpose: empty running after one-way loads and between trips, because the data
doesn't record those miles. **Tests:** 118 in total, all passing (every finding has a tone, what,
impact, and an action when it is priority or watch; the message changes with the level).

## 10. Second review: wording, units, tables, delivery standards (2026-10-04)

A reference executive report shared by the project owner was used for layout ideas only (a unit chip
on each chart, a reading note under it, assessment columns in tables); none of its data or branding
was copied.

| Feedback | Change |
|---|---|
| Date range picker misbehaved | A form with *From*, *To* and **Apply**: picking dates no longer reloads the page; tested with Streamlit's AppTest (picking alone changes nothing, Apply does) |
| Findings not tabbed on every page | Every page uses the same tabbed findings card |
| Margin by state had no unit or meaning | Unit chip, full state names, and a note naming the highest and lowest state |
| Daily contribution and 30-day line unclear | Removed: day-level noise added nothing the period and YTD charts don't show |
| "Lanes per cell" grid said nothing actionable | Replaced by a **lane assessment table**: each lane's trips, revenue, contribution, margin, gap to the average margin, volume and margin level, assessment and action, sorted by urgency, filterable |
| Charts without units | Every chart card shows "Unit: …" and has axis titles where axes carry values |
| Is ±2 h fair for 3–4 day trips? | Checked in the data: deliveries land between 3 h early and 6 h late, evenly spread, **the same for trips under one day, one to two days and over two days** (44.5% / 44.8% / 43.9% within ±2 h). The page now shows four standards side by side: within ±2 h 44.6%, not late 33.3%, no more than 2 h late 55.6%, on the appointment date 91.2% |
| Page names | Renamed (see the spec) |
| Fleet "for reference" finding obscure | Rewritten in plain words (demand varies at random, not by season; size the fleet by days covered) |
| "How to read" → plain interpretation; "busy" trucks | Notes are now "Diễn giải" with a full sentence using the figures; "trucks busy" → "trucks working" |
| Productivity labels unclear | Full names with a definition line (e.g. average miles per truck per month = total miles ÷ truck-months with trips); revenue per truck-week now covers the selected range |
| Variable names on screen (`utilization_rate`, table and rule ids) | Mapped to plain names everywhere (data-quality chart, fleet chart, KPI glossary) |
| No Excel-like filter | Each table has a multi-choice filter per category column and a "showing n of N rows" line; numbers stay numeric so sorting works (shown in the browser's number format) |
| Idle trucks table | Numbered rows; downtime column dropped (not meaningful for trucks that never ran); title states the count; note states the maintenance cost and why the list matters |
| Wording | Professional terms (fuel cost instead of fuel spend, incident claims, contribution profit…) |
| KPI glossary | KPI names follow the language toggle; formulas written in words; value column explained (the KPI for the whole fleet over the selected range) and shown with its unit |

**Tests:** 119 in total, all passing; `ruff` clean.

## 11. Third review (2026-10-04)

| Question | Answer and change |
|---|---|
| What is "Dedicated" vs "Contract"? | Industry meaning, since the data records only the type: *Contract* = rates agreed in advance, trucks from the shared fleet; *Dedicated fleet* = trucks and drivers reserved for one customer. Renamed and explained under the chart. In this data the three segments earn the same revenue per mile and margin |
| Why does the repositioning share stay at ~95%? | It does vary a little (95.0–95.6% by range), but it equals what **random assignment** of next trips would give (95.4% expected vs 95.5% observed): the data shows no trip chaining. Added the benchmark to the analysis, the finding and the chart note |
| Why "consider exiting" lanes with >50% margin? | The High/Mid/Low tiers are relative, and every lane is profitable at contribution level (lowest 50.4%). The action was renamed **Review rates**, the finding now states the lowest lane margin, and the table note explains the tiers. The margin columns stay: they are the basis of the assessment |
| Empty running: fix now or in optimization? | Moved to `optimize`: the data has no empty miles or coordinates, so the saving must come from a dispatch simulation (assign next loads to trucks already in the pickup city) |
| Deviation chart axis "-3…-2" | Real hour axis (−3 … +6) with the ±2 h window shaded |

**Tests:** 119, all passing.

## 12. Layout fixes (2026-10-04)

- **Overflow:** checked automatically at 1440, 1280, 1024, 768 and 390 px; values spilled out of KPI cards at ~1024 px with the sidebar open. KPI and finding grids now size by the width of the content area (CSS container queries) and long values wrap; bar labels show numbers only (the unit is in the card header); text-heavy tables (KPI definitions, data trust) are HTML tables that wrap instead of truncating; the lane table gives its text columns more room.
- **Tabs:** the selected tab is kept when the page reruns (it used to jump back to the first tab).
- **Findings:** collapsible, with counts per level in the header and a legend: the coloured edge shows the tone (red negative, amber risk, green positive, grey neutral), the tab shows the level. Checked: every finding's edge matches its tone chip.
- **Units:** "triệu USD" shortened to "tr USD" everywhere (dashboard and generated documents).
- **Bug fixed:** the KPI definitions table had its headers in a different order from its cells (now tested).
