# Moving the project to another computer

> Vietnamese: [handoff.vi.md](handoff.vi.md) · Demo script: [demo-script.md](demo-script.md) ·
> Summary: [SUMMARY.md](SUMMARY.md) · Updated 2026-10-05, after the module 6 commit.

## 1. Install (once)

| Needed | Note |
|---|---|
| Git | To get the code |
| Python 3.11 or later | `pyproject.toml`: `requires-python >= 3.11` |
| [uv](https://docs.astral.sh/uv/) | Dependencies; the old machine runs it as `python -m uv` (uv 0.12) |
| Microsoft Edge or Google Chrome | Required for **PDF** (printed by the browser, no extra library). Without one, HTML only |
| Times New Roman font | Ships with Windows; the PDF uses it |

```powershell
git clone https://github.com/hoangtrb/logops.git
cd logops
python -m uv sync
```

## 2. Not in the repo: copy by hand

| What | From | To |
|---|---|---|
| Dataset (14 CSV files) | [Kaggle: Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database), unzipped | `dataset/` |
| Report cover photo | Old machine: `reports/assets/cover.jpg` (shows a truck maker's logo, so kept out of the repo) | `reports/assets/cover.jpg`; without it the PDF cover has no photo, everything else works |
| Your reference report | Old machine: `Bao_Cao_Tong_Hop_Van_Tai_Kho_va_TPTS_*.html` (layout reference only, never committed) | Repo root, if needed |
| Fallback reports | Old machine: `reports/output/*.pdf, *.html` | Or rebuild them in step 4 |

## 3. Build the warehouse and check

```powershell
python -m uv run logops build                      # about 20 s: Parquet, DuckDB, generated docs
python -m uv run pytest -m "slow or not slow" -q   # 160 tests, about 2 min
```

After `logops build`, `git status` should be clean (generated docs carry no timestamps and a fixed
order). If a file changed, review it before committing.

## 4. Run

```powershell
python -m uv run logops dashboard                       # http://localhost:8501
python -m uv run logops report --format pdf --lang vi   # → reports/output/bao-cao-van-tai-...pdf
python -m uv run logops report --format html --lang en  # → reports/output/transport-report-...html
python -m uv run logops optimize                        # prints the recommendations
```

On the dashboard: sidebar → **Export report** → HTML/PDF → **Create report** (runs in the
background) → **Download**.

## 5. Before presenting

- [ ] Open the dashboard, choose **Vi**, visit all 9 pages once (a few seconds the first time, then
  under 3 s).
- [ ] Export one PDF from the sidebar (about 30 s).
- [ ] Keep the fallback PDF and HTML from `reports/output/` open.
- [ ] Reread [demo-script.md](demo-script.md) (7 minutes + likely questions).

## 6. Common problems

| Symptom | Fix |
|---|---|
| Dashboard says the warehouse is locked | Close whatever holds `data/warehouse.duckdb` (DBeaver, a notebook, another dashboard), then reload |
| `logops build` can't write | Same: stop the dashboard before building |
| Port 8501 in use | `python -m uv run logops dashboard --port 8502` |
| PDF export says no browser | Install Edge or Chrome, or choose HTML |
| Code changed but the dashboard didn't | Stop the dashboard (Ctrl+C) and start it again |
| The state map doesn't show | It needs the internet; reports leave it out on purpose |
| "No runtime found" warnings from `logops report` | Harmless: dashboard functions running outside Streamlit |

## 7. Key figures (to say without looking)

| | |
|---|---|
| Revenue · operating cost · contribution profit | $298.62M · $103.88M · $194.74M (2022–2024); margin 65.2% |
| On-time delivery | 44.6% (±2 h) · 91.2% (by appointment day) |
| Margin 2022 → 2024 | 62.7% → 67.2%; 93% of the gain from fuel prices |
| Network | 33% of loads end where there is no return load; 95.4% of next trips start in another city |
| Fleet | 120 owned, 92 have run, ≤ 75 needed on 99% of days; 28 trucks never ran yet cost $1.40M in maintenance |
| Savings target | $1.04M a year (3% × $34.65M) |
| Measured · maximum potential · total | $0.47M · $2.42M · $2.89M (278% of the target) |
| Not in the total | $7.24M of fuel to reconcile |

## 8. Working with Claude on the new machine

Claude on the new machine does not remember earlier agreements. In a new session ask Claude to read
this file, or copy this section into `CLAUDE.md` at the repo root (Claude reads that file every
session).

- **Language:** answer in Vietnamese. Every doc comes as `name.md` (English) and `name.vi.md`
  (Vietnamese), linked at the top, including specs, plans and generated docs.
- **Git:** Claude only stages files and proposes the commit message; **the owner commits and pushes**.
  Never stage `dataset/`, `data/`, `.env`, `reports/output/`, `Bao_Cao_*.html`,
  `reports/assets/cover.jpg`.
- **Data:** no outside data (public coordinates were rejected); distances between cities come from the
  data's lanes. Don't build what the data lacks (driver pay, overhead, resale value). The data is
  synthetic: never invent a company name.
- **Scope:** operational productivity and quality (cost, fuel, on-time, truck use, data quality); no
  HR or legal-compliance criteria.
- **Money:** three kinds never added together: measured saving, maximum potential (needs customers
  or management to accept), estimate/unexplained (never in the total). Only figures measured from the
  data; a signal needs to repeat across years before it gets a dollar figure.
- **Each finished task:** update `docs/00-project-journal.md` + `.vi.md`. Each finished module:
  `docs/reviews/NN-*.md` + `.vi.md` and `docs/SUMMARY` (verified facts only). A new module starts with
  a spec that defines its outputs first.
- **Dependencies:** ask before adding a library.
- **Presentation (dashboard and reports):**
  - every chart shows its unit and a "Diễn giải" note written as sentences with figures;
  - professional Vietnamese logistics wording (chi phí nhiên liệu, lợi nhuận đóng góp, xe hoạt động,
    OTD…), never variable or table names; the Vi/En toggle covers KPI names;
  - tables have row numbers and Excel-like filters; findings in three groups (Ưu tiên xử lý / Cần theo
    dõi / Tham khảo), each with tone, what happened, impact, action;
  - no icons or emoji; levels as coloured text;
  - millions as "tr USD"; no jargon like "mức trần" (use "tiềm năng tối đa");
  - a result card that isn't self-evident explains on hover how it is computed, with figures and the
    condition to reach the target;
  - scenarios in words ("Như hiện tại", not 0%); drop a chart that isn't clear rather than explain it;
  - the optimization page is one page, before the data page;
  - long jobs (report export) run in the background with a status line and a Download button that
    fills with green.
- **Report:** one file with every dashboard page. HTML responsive, one tab per page, tab bar in two
  rows (5 + 4), no scrollbars. The PDF is typeset like a document:
  - Times New Roman, black 11 pt text, dark blue headings, 20 mm margins;
  - cover (report name, project, data source, photo at the bottom), contents, lists of figures and
    tables with page numbers, executive summary;
  - each section on a new sheet; numbered figures and tables without frames; wide tables on landscape
    sheets, data never cut;
  - footer: report name, export date, page x / y.
- **Visual checks:** after each change, screenshot and look (dashboard at 1440 px and 390 px, every
  PDF page), not only the tests.
