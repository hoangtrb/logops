# Review · Module 6: `reports`

> CRISP-DM phase 6 (Deployment) · Vietnamese: [06-reports.vi.md](06-reports.vi.md) · Spec:
> [SPEC-reports.md](../../SPEC-reports.md) · Summary: [SUMMARY.md](../SUMMARY.md)
> **Status:** completed 2026-10-04, not yet committed · **Rule:** only verified facts.

## 1. Outputs vs the spec

| Output | Delivered | Evidence |
|---|---|---|
| 5 report types: executive summary, financial performance & lanes, delivery performance, fuel, fleet | ✅ | Every type builds (test) |
| Self-contained HTML | ✅ Plotly inlined once (~4.7 MB per file); no external script | Test: no `<script src=` |
| PDF without a new dependency | ✅ Headless print of Edge or Chrome, charts laid out at A4 width; clear message if no browser | Test (skipped when no browser); PDFs checked page by page |
| Same figures as the dashboard | ✅ Same analysis and optimize functions, same charts and cards | Test: executive report shows the dashboard's revenue and OTD for 2024 in English |
| CLI `logops report` | ✅ Writes to `reports/output/` (git-ignored) | Used to make the reports below |
| Dashboard export | ✅ Sidebar "Export report": type, HTML/PDF, current range and language → download | Test: the sidebar builds an HTML report |
| Safety & drivers report | ❌ Dropped (out of scope) | — |

**Tests:** 9 new (8 reports, 1 dashboard export); 157 in total, all passing; `ruff` clean.

## 2. Measured

- Building a report takes 10–15 s (the analysis bundle); the PDF print adds about 2 s.
- PDF layout: charts kept whole, tables run onto the next page with their header repeated, each
  section starts on a new page.

## 3. Caveats

- PDF needs Microsoft Edge or Google Chrome on the machine (both present on this laptop).
- Recommendations in the reports cover the whole 2022–2024 data, not the report period (stated in
  the report).

## 4. Reproduce

```powershell
python -m uv run logops report --type executive --lang vi --format pdf
python -m uv run pytest tests/reports -m "slow or not slow"
```

## 5. Revision 2026-10-04: one report with every page

- One report replaces the five types: every dashboard page as a tab, drawn by the page code
  itself through an HTML builder, so it cannot differ from the dashboard.
- Checked: HTML at 1366 px and 390 px (no sideways scroll); PDF 48 A4 pages for 2022–2024, each
  dashboard page on a new sheet, footer with report name, export date and page x / y.
- Dashboard export runs on a worker thread with a progress-filled Download button.
- Evening: print layout rebuilt (cover, contents, numbered sections, landscape sheets for wide
  tables, nothing cut): 43 pages. Tests: 156 in total after the savings-tips test; before it: 155, all passing (report tests rewritten for the single report; a test checks
  that drawing a report never reaches Streamlit from another thread).
