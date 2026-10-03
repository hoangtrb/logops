# Project Summary: Logistics Ops Optimizer

> Vietnamese: [SUMMARY.vi.md](SUMMARY.vi.md) · Updated at the end of each module · **Last updated:**
> 2026-10-03, after module 2 · **Rule:** verified facts only; details and evidence are in each review
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
| 2 | `metrics` | 3 | ✅ 29 tests | [02-metrics.md](reviews/02-metrics.md) |
| 3 | `optimize` | 4, 5 | ⏳ | |
| 4 | `insights` | 6 | ⏳ | |
| 5 | `dashboard` | 6 | ⏳ | |
| 6 | `reports` | 6 | ⏳ | |

## 3. Where the business stands (verified baselines)

| Metric | Value |
|---|---|
| Revenue | $298.6M |
| Measured cost (fuel + maintenance + incidents) | $104.0M; **fuel is 92%** |
| Cost per mile · revenue per mile | $0.851 · $2.445 |
| Fleet MPG | 6.45 |
| Deliveries within ±2 h · not late | 44.6% · 33.3% |
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
| Method, threshold and data-model documentation | `docs/00-analytical-approach`, `docs/02-*` |

## 6. Levers for the `optimize` module

| Lever | Signal in the data? |
|---|---|
| Fleet size (28 unused trucks) | ✅ $1.40M maintenance; volume nearly flat (+1.3%) |
| Lane profitability | ✅ Margins from 50.4% to 72.7% across lanes |
| On-time delivery | ✅ 44.6%; to be examined with the delay-risk model |
| MPG by truck/driver | Not yet checked |
| Idling; fuel price by location | ❌ No signal: no savings claimed |

## 7. Project owner's decisions

- Focus on **operational productivity and quality**; no HR-compliance criteria.
- Don't build anything the data can't support (e.g. driver pay).
- Each module starts with a spec that defines its outputs and ends with a review plus an update to
  this file.
