# Logistics Ops Optimizer

> Vietnamese: [README.vi.md](README.vi.md) · Modules: [CAPABILITY-MAP.md](CAPABILITY-MAP.md) · Roadmap: [tasks/roadmap.md](tasks/roadmap.md)
> **Summary: [docs/SUMMARY.md](docs/SUMMARY.md)** · Progress: [docs/00-project-journal.md](docs/00-project-journal.md) · Methods: [docs/00-analytical-approach.md](docs/00-analytical-approach.md)

Turns raw fleet data into cost-saving decisions for a distribution network: cost-to-serve,
on-time delivery, fuel efficiency and fleet utilization, presented in a dashboard and in
one-click PDF/HTML reports.

## At a glance

| | |
|---|---|
| **Problem** | Cut operating cost by at least 3% a year ($1.04M) and improve delivery performance, from the company's own operating data |
| **Data** | [Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database) (Kaggle, synthetic): a US road freight carrier, 14 tables, 549,706 rows, 85,410 trips in 2022–2024, 120 trucks, 200 customers, 58 lanes |
| **Method** | CRISP-DM in six modules: data platform → KPIs → analysis → dashboard → optimization → reports |
| **Result** | Measured saving $0.47M a year (45% of the target); maximum potential $2.42M more if customers accept the pricing changes; total $2.89M (278%). Not counted: $7.24M of fuel to reconcile, trip chaining up to $4.27M of fuel (estimate) |

## Use

```bash
uv run logops dashboard          # dashboard at http://localhost:8501 (VI/EN, 9 pages)
uv run logops report --format pdf --lang vi          # report → reports/output/
uv run logops report --format html --from 2024-01-01 --to 2024-12-31 --lang en
uv run logops optimize           # recommendations against the savings target
```

The report (every dashboard page) can also be exported from the dashboard sidebar, **Export
report**: it is built in the background. HTML opens offline; PDF needs Microsoft Edge or Google
Chrome.

## Modules

| # | Module | What it gives |
|---|---|---|
| 1 | `data_platform` | Parquet + DuckDB warehouse, 69 data-quality rules, data-quality report |
| 2 | `metrics` | 21 KPIs (SCOR) by period and group, definitions in words |
| 3 | `analysis` | Profit bridge, lane matrix, fleet capacity, delivery standards, rule-based findings |
| 4 | `dashboard` | Streamlit: 9 pages, findings by priority, units and reading notes on every chart |
| 5 | `optimize` | Fleet size, lane pricing, late-delivery check, data-process gaps, trip chaining |
| 6 | `reports` | One report with every page: responsive HTML or a typeset PDF (cover, contents, lists of figures and tables, executive summary) |

Reviews per module: [docs/reviews/](docs/reviews/). Interview walk-through:
[docs/demo-script.md](docs/demo-script.md).

## Setup

1. **Install [uv](https://docs.astral.sh/uv/)** and the dependencies:
   ```bash
   uv sync
   ```
2. **Download the dataset** — [Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database)
   on Kaggle — and unzip the 14 CSV files into `dataset/` (the data is not redistributed in this repo).
3. **Build the warehouse:**
   ```bash
   uv run logops build
   ```

## Development

```bash
uv run pytest                    # all tests
uv run pytest -m "not slow"      # unit tests only (no real dataset needed)
uv run ruff check . && uv run ruff format .
```
