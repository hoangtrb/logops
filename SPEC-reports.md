# Spec: reports

> Module 6 of 6 · CRISP-DM phase 6 (Deployment) · Vietnamese: [SPEC-reports.vi.md](SPEC-reports.vi.md)
> · Inputs: the analysis layer (module 3), the optimize module (module 5), the dashboard's charts and
> components (module 4)

## Objective

One click (dashboard) or one command (CLI) turns a **report type**, a **date range** and a
**language** into a file the Logistics Director can keep, print or email: **self-contained HTML**
(opens offline, charts stay interactive) or **PDF**.

**Principles**
- **The report computes nothing new.** It reads the same analysis and optimize functions as the
  dashboard and reuses its charts and components, so a report always matches the screen.
- Same presentation standards as the dashboard: unit on every chart, a reading note, plain names,
  VI/EN.
- **No new dependency.** PDF uses the headless print mode of Microsoft Edge or Google Chrome, already
  installed on Windows; if neither is found the user gets a clear message and the HTML still works.

## Outputs

### Report types

| Type | Content |
|---|---|
| **Executive summary** | 8 KPI cards, key findings by level, savings vs target and the recommendations, margin and fuel price chart |
| **Financial performance & lanes** | P&L by quarter (chart + table), profit bridge, unit economics, lane assessment (priority lanes), lane pricing scenarios |
| **Delivery performance** | On-time under four standards, delivery-time spread, on-time by trip length, detention, late-delivery check |
| **Fuel** | Fuel findings, bought vs burned, bought ÷ burned ratio, average price, fuel cost, fuel reconciliation gap |
| **Fleet** | Trucks working per day, productivity, fleet size by growth scenario, disposal tiers, trucks that never ran |

The planned "Safety & drivers" report is dropped: driver and compliance criteria are out of scope
(project owner's decision).

### Interfaces

- `logops report --type executive --from 2022-01-01 --to 2024-12-31 --lang vi --format html|pdf`
  → file in `reports/output/` (git-ignored).
- Dashboard sidebar: **Export report** (type, format) → download button. Uses the sidebar's date range
  and language.
- `reports.build_html(type, start, end, lang)` → HTML string; `reports.to_pdf(html)` → PDF bytes.

### Layout

A cover band (report title, date range, generation date), then sections in the dashboard's card
style; charts embedded with Plotly (its library inlined once, so the file opens offline); tables
wrap; page breaks between sections in the PDF.

## Out of scope

| Not done | Why |
|---|---|
| Claude-written narrative | The rule-based findings already cover it; no API cost |
| Scheduled or emailed reports | No scheduled jobs (project decision) |
| Safety & drivers report | Out of scope (productivity and quality only) |

## Success criteria

1. Every report type builds in both languages for the full range and a single year; tested.
2. A figure in a report equals the same figure on the dashboard (tested on the executive summary).
3. The HTML opens without internet; the PDF opens and has one page or more per section.
4. Missing browser → clear message, no crash; `ruff` clean; tests pass.

## Plan

| Step | Content |
|---|---|
| 1 | `reports/build.py`: shared data fetch, sections per type, HTML template |
| 2 | `reports/pdf.py`: Edge/Chrome headless print |
| 3 | CLI `logops report`, dashboard export button |
| 4 | Tests, screenshots of each report, review `docs/reviews/06-reports`, SUMMARY, journal |

## Revision 2026-10-04 (decided by the owner): one report with every page

Replaces the five report types above and the v2 proposal.

| Item | Decision |
|---|---|
| Content | One report, **every dashboard page** (overview, financial performance, customers & markets, lanes, delivery, fleet, fuel, optimization, data & KPIs) |
| Layout | Header: "Transport management report", export date, period. Below it one tab per page, like the multi-page dashboard; the overview tab opens first with revenue, operating cost, contribution profit, margin, cost per mile and the operating KPIs |
| Source | The pages draw the report themselves: their `st.*` calls go to an HTML builder (`reports/static.py`) through `dashboard/output.py`, per thread, so the figures, notes and tables are the dashboard's; each page in the view it opens with (shown as a "view: …" chip) |
| HTML | Self-contained, responsive (tabs scroll sideways and grids stack on a phone; long tables scroll inside their card) |
| PDF | Every page starts on a new A4 sheet; footer with report name, export date and "Page x / y" (CSS page margin boxes); long tables keep their first 40 rows with a note pointing to the HTML; the US map is left out (its outline needs the internet) |
| Dashboard | Sidebar "Export report": format, Create, a status line with the progress, and Download, which fills with green as the report is made and turns solid green when ready; the report is made on a worker thread |
| CLI | `logops report --from --to --lang --format html\|pdf` |

### Revision 2026-10-04 (evening)

- No icons anywhere (dashboard navigation, report tabs, status lines); report page tabs in two
  rows (5 + 4) without scrollbars; findings tabs without scrollbars.
- Project and data source (project, problem, dataset, company, Kaggle link) on the overview page
  and the report cover. The data names no company (synthetic), so none is invented.
- PDF: its own print layout in the same file (cover with contents; numbered sections, each on a
  new sheet; numbered figures and tables without card frames; full tables, those with 8+ columns
  on a landscape sheet in place; header with the period; footer with name, export date, page
  x / y). Engine unchanged: headless Edge/Chrome (Chromium, the engine behind Playwright and
  Puppeteer); WeasyPrint was considered but needs a GTK runtime on Windows and cannot run the
  chart scripts (charts would need a further image dependency).
- PDF typography (owner, 2026-10-04): Times New Roman, black text, 11 pt body, dark blue headings,
  20 mm margins; findings and KPIs as text and tables, no boxes.
- PDF front matter (owner, 2026-10-04): cover photo, contents and lists of figures and tables with
  page numbers, executive summary; findings with coloured levels, bullets and the action set off.
