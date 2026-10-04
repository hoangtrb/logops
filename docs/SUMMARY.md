# Project Summary: Logistics Ops Optimizer

> Vietnamese: [SUMMARY.vi.md](SUMMARY.vi.md) · Updated at the end of each module · **Last updated:**
> 2026-10-04, after module 6 `reports` · **Rule:** verified facts only; details and evidence are in each review
> under `docs/reviews/`.

## 1. What the project is

Turns fleet operations data into **cost-saving decisions with a dollar figure**, presented in a
dashboard and in reports. It will be presented to the Logistics Director of Saigon Co.op at the
interview on **2026-10-05**, and follows the CRISP-DM framework.

**Data:** [Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database)
(Kaggle, synthetic). 14 tables, 549,706 rows, Jan 2022–Dec 2024. 120 trucks, 150 drivers, 200
customers, 58 lanes.

## 2. Progress

| # | Module | CRISP-DM phase | Status | Review |
|---|---|---|---|---|
| — | Business understanding | 1 | ✅ | `docs/01-business-understanding` |
| 1 | `data-platform` | 2, 3 | ✅ 47 tests | [01-data-platform.md](reviews/01-data-platform.md) |
| 2 | `metrics` | 3 | ✅ 28 tests | [02-metrics.md](reviews/02-metrics.md) |
| 3 | `analysis` | 2, 3 | ✅ 12 tests | [03-analysis.md](reviews/03-analysis.md) |
| 4 | `dashboard` | 6 | ✅ 26 tests | [04-dashboard.md](reviews/04-dashboard.md) |
| 5 | `optimize` | 4, 5 | ✅ 28 tests | [05-optimize.md](reviews/05-optimize.md) |
| 6 | `reports` | 6 | ✅ 7 tests | [06-reports.md](reviews/06-reports.md) |

## 3. Where the business stands (verified baselines)

| Metric | Value |
|---|---|
| Revenue | $298.6M |
| Measured cost (fuel + maintenance + incidents) | $104.0M; **fuel is 92%** |
| Cost per mile · revenue per mile | $0.851 · $2.445 |
| Fleet MPG | 6.45 |
| On-time delivery (OTD, within ±2 h of the appointment) · not late · on the appointment date | 44.6% · 33.3% · 91.2% |
| Fleet utilization (average trucks with a trip per day ÷ trucks owned) | 55.1% (66 of 120) |
| Detention | 260,607 hours; 91.5 minutes per pickup or delivery on average |
| Fleet | 92 trucks in use; **28 trucks ran no trip in 3 years**, costing $1.40M in maintenance |
| **Savings target** | **≥ $3.1M over 3 years** (3% of measured cost) |

## 4. How far the data can be trusted

- **Trustworthy:** relationships between tables, money amounts, monthly aggregate tables, no
  duplicates. Only 1.5% of rows have an error-level issue.
- **Unusable:** state on fuel purchases and incidents, `facility_id` on delivery events,
  `idle_time_hours` (random noise), fuel price by location (no signal).
- **Not in the data:** driver pay, overhead. The 65.2% contribution margin is therefore **higher than
  the true margin**.
- **`on_time_flag`** = within ±120 minutes of the appointment, inferred from the data (100% match).
  There's no external source for the 120, so the on-time window is a parameter.

## 5. Delivered

| Product | Command / file |
|---|---|
| A checked warehouse, rebuilt with one command | `logops build` (about 7 s) |
| 69 data-quality rules, EN/VI report | `docs/02-data-quality-report` |
| 3 base views + 21 SCOR KPIs | `logops kpi --by …`, `docs/03-kpi-definitions` |
| Profit, fuel, fleet and network analyses + rule-based commentary | `logops insights`, `docs/03-analysis-insights` |
| Dashboard, VI/EN toggle, responsive, commentary next to each chart | `logops dashboard` → http://localhost:8501 |
| Recommendations vs the savings target, dashboard page, `docs/04`, `docs/05` | `logops optimize` |
| One report with every dashboard page as a tab, self-contained HTML or paged PDF, from the CLI or the dashboard | `logops report` |
| Method, threshold and data-model documentation | `docs/00-analytical-approach`, `docs/02-*` |

## 6. Savings vs target (module 5 `optimize`, per year)

| Type | Amount | vs target ($1.04M) |
|---|---:|---:|
| Measured: dispose of the 28 trucks that never ran | $0.47M | 45% |
| Upper bound: 13 lowest-mileage trucks, fuel surcharge to the median, +5% rates on low-margin lanes | $2.42M | 233% |
| Total potential | $2.89M | 278% |
| Unexplained, not counted: fuel bought but not recorded as burned | $7.24M | — |


Late deliveries (44.4% more than 2 h late) have no repeatable cause in the data, so no recommendation is made for them. Details: [05-evaluation.md](05-evaluation.md).

## 7. Key findings (module 3 `analysis`)

| Topic | Finding |
|---|---|
| **Profit** | Margin rose 62.7% → 67.2% (2022 → 2024) while revenue per mile stayed flat. **93% of the contribution gain (+$4.12M of +$4.42M) comes from falling fuel prices**; margin moves against fuel prices (correlation −0.92) because the surcharge is fixed |
| | Volume flat; customer segments earn the same margin; no customer concentration risk (HHI 50) |
| **Network** | **33% of loads end where there's no return load**; 16 of 20 cities imbalanced by over 20%; stable across years (0.997). Los Angeles and Indianapolis only receive. In 95.4% of transitions trucks start the next trip in another city |
| **Fleet** | 95% of days need ≤ 73 trucks, busiest day 80; 92 in use, 120 owned. Peak timing can't be forecast, so plan by service level |
| **Fuel** | Gallons bought exceed gallons recorded as burned by 1.28–1.30× every year; not reconciled |

These figures are generated from the data by the rules; see [03-analysis-insights.md](03-analysis-insights.md).

## 8. Project owner's decisions

- Focus on **operational productivity and quality**; no HR-compliance criteria.
- Don't build anything the data can't support (e.g. driver pay).
- Each module starts with a spec that defines its outputs and ends with a review plus an update to
  this file.
