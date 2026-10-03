# Logistics Ops Optimizer

> Vietnamese: [README.vi.md](README.vi.md) · Modules: [CAPABILITY-MAP.md](CAPABILITY-MAP.md) · Roadmap: [tasks/roadmap.md](tasks/roadmap.md)
> **Summary: [docs/SUMMARY.md](docs/SUMMARY.md)** · Progress: [docs/00-project-journal.md](docs/00-project-journal.md) · Methods: [docs/00-analytical-approach.md](docs/00-analytical-approach.md)

Turns raw fleet data into cost-saving decisions for a distribution network: cost-to-serve,
on-time delivery, fuel efficiency and fleet utilization, presented in a dashboard and in
one-click PDF/HTML reports.

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
