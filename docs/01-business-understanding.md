# 01 · Business Understanding

> CRISP-DM Phase 1 · Project: Logistics Ops Optimizer · Vietnamese version: [01-business-understanding.vi.md](01-business-understanding.vi.md)

## 1. Background

A fleet operator runs ~120 trucks, ~180 trailers and ~150 drivers. Over 2022 onward it moved
~85,000 loads for ~200 customers across 58 lanes and 50 facilities. Every trip leaves data
behind: fuel purchases, delivery events, maintenance records, safety incidents. Today this
data is only used to report what happened. It is not used to decide what to change.

The same situation applies to a retail distribution network, such as a retailer's fleet
running distribution-center-to-store deliveries. Transport is one of the largest
controllable costs, and service level (did goods arrive on time) directly drives store
availability.

## 2. Business objectives

The logistics director's questions, in priority order:

| # | Director's question | Business objective |
|---|---|---|
| 1 | *"Which routes and customers lose us money?"* | Lower **cost-to-serve**; fix or reprice unprofitable lanes |
| 2 | *"Why are deliveries late, and where?"* | Raise **on-time delivery %**; cut detention time |
| 3 | *"Are we wasting fuel?"* | Reduce **fuel cost per mile** (MPG, idle time, purchase price) |
| 4 | *"Do we have the right number of trucks, and which are too costly to keep?"* | Improve **fleet utilization**; reduce maintenance cost & downtime |
| 5 | *"Can I get a report without asking the analyst?"* | **Self-service reporting** in one step |

## 3. Situation assessment

**Resources:** 14 relational tables from the Kaggle
[Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database)
(CSV, ~55 MB, ~600k rows); Python data stack; Claude API
for written insights.

**Constraints**
- Historical snapshot only. No live GPS or telematics feed, so recommendations are strategic
  and tactical, not real-time dispatch.
- Driver pay and overhead costs are not in the data, so cost-to-serve covers fuel,
  maintenance and safety costs, and driver cost is estimated from duration.
- US data (miles, USD). The method transfers to any network unchanged.

**Assumptions**
- `revenue` on loads is the price charged to the customer (or, for an in-house fleet, the
  internal transfer price).
- `on_time_flag` on delivery events is the authoritative service measure. *Confirmed in Phase 2:*
  it means arrival within **±2 hours** of the appointment (matches 100% of events), so arriving
  more than 2 hours early also counts as a miss.

**Risks & mitigations**

| Risk | Mitigation |
|---|---|
| Synthetic or dirty data (e.g. city/state mismatches, missing driver IDs) | Data-quality report in Phase 2; document every cleaning rule |
| Savings estimates over-promise | Use conservative benchmarks (move outliers to fleet *median*, not best-in-class) |
| LLM states numbers that are wrong (hallucination) | Claude only explains numbers computed by code; it never calculates them |
| LLM API cost | Cache narratives; track tokens per report; review with owner if costly |

## 4. Data-mining goals

| Business objective | Analytical goal | Technique |
|---|---|---|
| Cost-to-serve | Cost/mile per lane & customer, split into fuel, maintenance, driver and safety costs; margin per lane | SQL aggregation, profitability ranking |
| On-time delivery | Find the factors behind late delivery and detention; predict delay risk per load | Classification model (gradient boosting) + feature importance |
| Fuel | Flag MPG/idle outliers by truck & driver; fuel price variance by location | Statistical outlier detection, benchmarking |
| Fleet & maintenance | Utilization per truck; right-size fleet; flag high cost-per-mile trucks | Utilization analysis, cost-trend scoring |
| Self-service reporting | Generate a report by type and date range | Templated PDF/HTML with LLM-written narrative |

## 5. Success criteria

*Baselines were measured in Phase 2 ([02-data-quality-report.md](02-data-quality-report.md)) and
the targets below are confirmed against them ([02-data-understanding.md](02-data-understanding.md) §6).*

**Business**
- Identify savings opportunities worth **≥ 3% of total operating cost**, each with an owner
  action and a $ estimate. Measured operating cost for 2022–2024 is **$104.0M** (fuel, maintenance
  and safety claims), so the target is **≥ $3.1M over three years (≈ $1.04M per year)**. Driver
  pay isn't in the data, so the real cost base is larger and this target is conservative.
- Every recommendation can be traced back to the data behind it.

**Analytical**
- Delay-risk model beats the naive baseline. Target ROC-AUC ≥ 0.70 on a time-based
  hold-out set (trained on earlier months, tested on later months).
- Data-quality report covers 100% of tables, with every cleaning rule documented.

**Deployment**
- Any report type is exported to PDF or HTML in **≤ 2 clicks / 1 command**, in under 60 s.
- Dashboard pages load in under 3 s on a laptop.

## 6. Project plan (CRISP-DM)

| Phase | Deliverable |
|---|---|
| 1. Business Understanding | This document |
| 2. Data Understanding | Data profile + data-quality report |
| 3. Data Preparation | Clean Parquet + DuckDB warehouse + KPI views |
| 4. Modeling | Four recommendation engines (cost, delivery, fuel, fleet) |
| 5. Evaluation | Model metrics + savings checked against §5 |
| 6. Deployment | Streamlit dashboard + one-click reports + Claude narratives |
