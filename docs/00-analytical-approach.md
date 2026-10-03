# 00 · Analytical Approach and Optimization Rationale

> Vietnamese: [00-analytical-approach.vi.md](00-analytical-approach.vi.md) · Project journal: [00-project-journal.md](00-project-journal.md)
> **Status:** the data section (§3) is implemented. Sections §4–§10 are the methods *chosen and
> to be implemented*. If the data forces a change of direction during the build, this file is
> updated with the reason.

For each analysis step, this document answers four questions:
1. Which **theory or framework** is it based on?
2. Which **model or technique** does it use?
3. **Why** was it chosen?
4. **Why not** an alternative?

---

## One-page summary

| Director's question | Theory / framework | Model / technique | Why not an alternative |
|---|---|---|---|
| What sequence does the project follow? | **CRISP-DM** + analytics ladder (descriptive → diagnostic → predictive → prescriptive) | 6 phases, each with a deliverable | KDD/SEMMA lack the business-understanding and deployment phases |
| What do we measure? | **SCOR** (reliability, cost, asset efficiency) + **KPI tree** | SQL KPI views | Ad-hoc KPIs tend to miss areas or double up |
| Can the data be trusted? | **DAMA's 6 data-quality dimensions** | SQL rules; rows *flagged*, never deleted | Deleting bad rows loses the audit trail and skews totals |
| Which lanes/customers lose money? | **Activity-based costing (ABC)**, **cost-to-serve**, **contribution margin** | Lane profitability ranking, "whale curve", Pareto | Full ABC needs overhead costs the data doesn't have |
| Why are deliveries late? | **Root-cause analysis** + **supervised learning** | **Gradient boosting** + SHAP/permutation importance, time-based train/test split | Neural nets underperform on tabular data; logistic regression is kept as the baseline |
| Are we wasting fuel? | **Benchmarking** + **robust statistics** | Median + MAD/IQR, compared within peer groups | Mean ± standard deviation is pulled by the very outliers it should find |
| Is the fleet too big; which trucks should go? | **Asset utilization**, **life-cycle cost / economic life** | Fleet size from a demand percentile; cost-per-mile trend by truck age | ML predictive maintenance needs sensor data the dataset doesn't have |
| How much can we save? | **Conservative estimation** | Move underperformers to the *median*, not best-in-class; no double counting | Best-in-class benchmarks over-promise |
| What does AI add? | **Grounded LLM** | Claude explains numbers computed by code; question → read-only SQL | Letting the LLM compute numbers invites made-up figures |

---

## 1. Overall framework

### 1.1 CRISP-DM

CRISP-DM (Cross-Industry Standard Process for Data Mining, Chapman et al., 2000) has 6 phases:

| Phase | Project deliverable |
|---|---|
| Business understanding | `docs/01` |
| Data understanding | DQ report |
| Data preparation | DuckDB warehouse + KPI views |
| Modeling | 4 engines |
| Evaluation | `docs/05` |
| Deployment | dashboard + reports |

**Why it was chosen:**
- The first phase is *business understanding*: it starts from the director's question, not from
  the data. The last phase is *deployment*: results must reach the user. That's exactly what a
  logistics director cares about.
- The process is iterative. If phase 2 numbers change the goals, you go back to phase 1, which
  is why the targets in `docs/01` §5 are marked *provisional*.

**Why not another framework:**
- **KDD** (Fayyad, 1996) and **SEMMA** (SAS) focus on the mining itself: sampling, exploring,
  modeling. Neither has an explicit business phase or deployment phase.
- **TDSP** (Microsoft) is thorough but built around team process and Azure infrastructure, which
  is too heavy for a 3-day project.

### 1.2 The analytics value ladder

The project climbs all four rungs of the analytics ladder. The ladder was popularized by
Gartner, and Davenport & Harris (2007) describe it in similar terms.

| Rung | Question | Example in this project |
|---|---|---|
| Descriptive | What happened? | KPIs: cost/mile, on-time % |
| Diagnostic | Why? | Cost breakdown, delay drivers |
| Predictive | What will happen? | Delay risk per load |
| Prescriptive | What should we do? | Recommendations with $ savings |

**This is the difference from a typical reporting dashboard.** Most dashboards stop at the
descriptive rung. This project ends at the prescriptive rung: each recommendation comes with a
concrete action and a dollar figure.

---

## 2. KPI framework: what to measure and why

### 2.1 The SCOR model

The SCOR model (Supply Chain Operations Reference, maintained by ASCM/APICS) splits supply-chain
performance into 5 attributes. The project's 4 focus areas map onto them:

| SCOR attribute | Project focus area | Main KPIs |
|---|---|---|
| **Reliability** | On-time delivery | On-time %, detention hours |
| **Cost** | Cost-to-serve, fuel | Cost/mile, fuel cost/mile, lane margin |
| **Asset management efficiency** | Fleet & maintenance | Truck utilization, maintenance cost/mile, downtime hours |
| Responsiveness | Indirectly, via transit time | Trip duration vs plan |
| Agility | Not covered | The data has no demand-shock scenarios |

**Why SCOR:** it's the shared language of the supply-chain profession. When a director hears
"reliability and cost-to-serve", they know immediately what is meant. A home-made KPI set tends
to miss something (such as asset efficiency) or double up (two metrics measuring the same thing).

### 2.2 KPI tree (DuPont-style decomposition)

Instead of reporting only "cost per mile went up", it's split into additive components:

```
Cost / mile  =  fuel/mile  +  maintenance/mile  +  driver/mile  +  safety/mile
                   │                                   │
          fuel price ÷ MPG                 hours × hourly rate (estimated)
                   │
          MPG ← idle time, truck type, lane
```

**Why:** the tree points straight at the *lever* to pull. If cost per mile is high because of
the fuel price, the fix is a fuel-purchasing policy. If it's high because of low MPG, the fix is
driver coaching or less idling. The approach borrows from DuPont decomposition in financial
analysis.

---

## 3. Data understanding and preparation (implemented)

### 3.1 Data-quality dimensions

The DAMA-DMBOK framework defines the dimensions of data quality. Each of the project's DQ rules
checks one of them:

| Dimension | Question | Project rule |
|---|---|---|
| Completeness | Are required values missing? | `fk_missing`, null % per column |
| Uniqueness | Are there duplicate records? | `pk_unique`, exact-duplicate removal |
| Validity | Are values in a plausible domain? | Types (at ingest), `range` |
| Consistency | Do the tables agree with each other? | `fk_orphan`, `amount_mismatch`, `agg_drift`, `geo_mismatch` |
| Accuracy | Does it match reality? | `time_order` (delivered before picked up is impossible) |
| Timeliness | Is the data stale? | Not covered: the data is a historical snapshot |

**Flag, don't delete.** Each row gets a `dq_issues` column listing its problems, and the
`dq_findings` table summarizes them all.
- **Why:** deleting bad rows skews totals without anyone noticing. For example, deleting trips
  without a `driver_id` would understate total fuel cost. Flagging lets each downstream use
  decide: keep the row when totalling costs, exclude it when ranking drivers.
- The only exception is exact duplicate rows. They are dropped, and the count is logged.

**Fail loudly on a type mismatch; never coerce silently.** At ingest, every value is checked
against its declared type. One bad value stops the build and names the exact `table.column`.
- **Why:** if a tool guesses types (pandas' default behavior), one dirty cell turns a whole
  numeric column into text. Calculations downstream then go wrong or slow down with no warning.

### 3.2 Dimensional modeling (Kimball)

The data is organized as a **star schema** (Kimball & Ross, 2013):

- **Fact tables** hold the numbers that occur over time:
  `trips`, `loads`, `fuel_purchases`, `delivery_events`, `maintenance_records`, `safety_incidents`.
- **Dimension tables** hold the descriptive attributes used to filter and group:
  `drivers`, `trucks`, `trailers`, `routes`, `customers`, `facilities`, plus a date dimension.

**Why:** business questions almost always take the form *"measure X, by Y, over period Z"*, for
example cost by lane by month. A star schema answers that shape directly, is easy for
non-specialists to read, and is the standard that BI tools expect.

**Why not a deeply normalized (3NF) model or one big flat table:**
- 3NF is optimized for *writing* data, not *analyzing* it, and every query needs many joins.
- One flat table repeats data and is hard to extend.

### 3.3 Data technology

| Choice | Why | Why not the alternatives |
|---|---|---|
| **DuckDB** | An in-process analytical database with no server. Reads CSV/Parquet directly. Builds all 14 tables in 4.2 s | **Spark** is for hundreds of GB on a cluster; at 58 MB it only adds start-up overhead. **PostgreSQL** needs a server and is slower for aggregation queries. **pandas** is memory-hungry and guesses types silently |
| **Parquet** | Columnar, well compressed, keeps types | CSV stores no types and is slow to read |
| **SQL for KPIs** | Anyone who knows SQL can audit the formulas | Logic buried in Python code is hard to audit |

**Interview talking point:** the same pattern (Parquet + a SQL engine) scales to a real retail
chain's data by swapping the engine for Spark, Databricks or BigQuery. The SQL logic stays almost
unchanged.

### 3.4 Handling missing data

**Theory:** Rubin (1976) distinguishes 3 kinds of missing data. The right treatment depends on
the kind:

| Kind | Meaning | Does dropping the missing rows bias the result? |
|---|---|---|
| **MCAR**: missing completely at random | Missingness is unrelated to anything | No bias, just slightly less data |
| **MAR**: missing at random | Missingness depends on an *observed* variable (e.g. one year, one lane) | Can bias; adjust for that variable |
| **MNAR**: missing not at random | Missingness depends on the missing value itself (e.g. poor drivers "forget" to log their name) | Biased, and the data alone can't fix it |

**Evidence in the data:** about 2% of trips have no `driver_id`, and the missingness is **MCAR**:

| Check | Trips with a driver | Trips without a driver |
|---|---|---|
| Missing rate by year 2022 / 2023 / 2024 | — | 2.01% / 1.98% / 2.03% |
| Missing rate across the 58 lanes | — | 1.1% to 2.9% (within random variation for ~1,500 trips per lane) |
| Average MPG | 6.50 | 6.49 |
| Average distance | 1,430 miles | 1,439 miles |
| On-time delivery % | 44.6% | 44.2% |

Trips without a driver look exactly like the others on every measured dimension. So leaving them
out of driver rankings does not bias those rankings.

**Policy: keep the rows, decide per analysis**

| Analysis | Treatment | Reason |
|---|---|---|
| Fleet totals: cost, fuel, miles, revenue | **Keep** every row | Dropping would understate fuel by $3.76M (3.9%) |
| Fleet-wide rate KPIs (MPG, on-time %) | **Keep** | The trip's values are valid even if the driver is unknown |
| Rankings and savings per driver/truck | **Exclude** rows missing the ID (complete-case analysis) | They can't be attributed. No bias because the data is MCAR. Each driver loses only ~14 of ~675 trips |
| Delay-risk model | **Keep** rows; treat a missing ID as an "unknown" category | Gradient boosting handles missing values natively |
| Reports by driver/truck | Add an **"Unattributed"** line | Drivers + "unattributed" = fleet total, so the numbers always reconcile |

**Why not impute:** `driver_id` is an identifier, not a measurement. Filling in the "most likely"
driver would **invent accountability** for someone who didn't drive that trip, and would corrupt
the very ranking it's meant to support. Imputation only makes sense for measurements (a missing
MPG, say), and this data has no such case.

---

## 4. Focus area 1: cost-to-serve and lane profitability

**Theory**
- **Activity-based costing** (ABC, Kaplan & Cooper, 1998): costs are assigned by the *activities
  that actually consume resources* (miles driven, driver hours, maintenance events) instead of
  being spread evenly by revenue.
- **Cost-to-serve and the "whale curve"** (Kaplan & Narayanan, 2001): rank customers by
  cumulative profit. The curve usually rises above 100% and then falls back, which means a small
  group of customers eats the profit the others generate.
- **Contribution margin** = revenue − variable costs. A lane with a negative margin is one where
  *every extra trip loses more money*.

**Techniques**
- Compute cost per mile with the KPI tree from §2.2, then the contribution margin for each lane
  and each customer.
- Apply the **Pareto principle** (ABC classification): see which ~20% of lanes generate ~80% of
  the profit or the losses.
- For each loss-making lane, compute the **break-even rate** = cost/mile ÷ (1 − target margin),
  which gives the gap to the current price.

**Recommended actions:** reprice, renegotiate surcharges, consolidate loads, or exit the lane.

**Why not full ABC:** the data has no driver wages and no overhead (offices, depreciation). So:
- Driver cost is *estimated* as hours × an hourly rate, and that is a **documented assumption**.
- The result is called *contribution margin*, not *net profit*, to avoid over-promising.

---

## 5. Focus area 2: on-time delivery and detention

> **Result after module 3 (2026-10-03): the delay-risk model was not built.** On-time rates by driver, customer, lane and truck don't persist from 2022–23 to 2024 (correlation 0.01–0.09), and delays don't propagate from pickup to delivery (−0.003). With no persistent signal, a model couldn't beat a coin flip (AUC ≈ 0.5). The method below stays as the plan for when reason codes are captured (`docs/04-data-process-improvements`, row 4).

**Theory**
- **OTIF** (On-Time In-Full) is the standard retail measure of delivery reliability.
- **Root-cause analysis:** is the delay caused by the facility (waiting at the dock), the lane
  (distance), the time window, or the driver/truck?

**Techniques**
- **Descriptive and diagnostic:** on-time % and detention hours by facility, lane, time of day
  and day of week. Detention is converted to money: detention hours × the hourly cost of truck
  and driver.
  - *Adjusted after phase 2:* "by facility" uses the event's **`location_city`**, not
    `facility_id`, because `facility_id` matches the lane only 3.4% of the time (essentially
    random) while `location_city` matches 100%.
  - *On-time definition:* `on_time_flag` = arrival within **±2 hours** of the appointment
    (100% match). Reports show both window compliance and the not-late rate. See
    `02-data-understanding` §4.
- **Predictive:** a **gradient boosting** classifier (Friedman, 2001) predicts each load's
  delay probability, using only information *known before dispatch*: lane, facility, appointment
  window, load type, weight, driver, truck age.
- **Explanation:** **permutation importance** and **SHAP** (Lundberg & Lee, 2017) answer "which
  factors cause the most delays".

**Why gradient boosting:**
- The data is tabular, mixes numeric and categorical columns, and has non-linear effects and
  interactions (for example, facility X is late only in the afternoon). Gradient boosting
  handles this well with little preprocessing.
- On tabular data, tree-based models still beat neural networks (Grinsztajn et al., 2022).

**Why not the alternatives:**

| Alternative | Reason |
|---|---|
| Neural networks | Need more data, hard to explain, no better on tabular data |
| Logistic regression | Easy to explain but misses interactions. **Still used as the baseline**: gradient boosting must beat it |
| Random forest | Usually slightly weaker than gradient boosting, with no explainability advantage |

**Model evaluation**
- **Time-based train/test split:** train on earlier months, test on later months. A random split
  lets "the future" leak into training and makes the score look better than it is.
- **No data leakage:** no information that is only known *after* delivery, such as the actual
  delivery time or detention minutes.
- **Metrics:**
  - ROC-AUC (target ≥ 0.70) against a naive baseline (predicting the overall late rate).
  - Precision in the highest-risk group, because dispatchers can only act on a few loads per day.

**Limitation to state openly:** the model shows *correlation*, not *causation*. "Facility X
causes delays" is a hypothesis to verify on the ground, not a fact.

**Note:** scikit-learn isn't in the dependency list yet. You'll be asked before it's added, per
the spec's "ask first before adding dependencies" rule.

---

## 6. Focus area 3: fuel efficiency

> **Result after module 3:** MPG by driver and truck doesn't persist across years (correlation 0.003 and −0.068; range 6.37–6.54), so no MPG savings are claimed. The fuel lever that does have a signal is the **fuel surcharge**: a fixed rate per lane ($0.15–0.34/mile) while fuel cost per mile is the same on every lane. See `docs/05-evaluation` §3.

**Theory**
- **Internal benchmarking:** compare each truck and driver with the company's own fleet.
- **Robust statistics:** use the median and **MAD** (median absolute deviation), or the **IQR**
  (Tukey's rule, 1977), to detect outliers.

**Why not mean ± 3 standard deviations:** the outliers themselves pull the mean and standard
deviation towards them, so they mask each other (Leys et al., 2013). MPG and idle-time
distributions are usually skewed, not normal. The median and MAD aren't moved by a few extreme
values.

**Compare within peer groups.** For example, compare MPG only between trips with the same load
type and distance band. Compared across the whole fleet, a driver who always runs heavy loads on
mountain lanes would be judged unfairly. This avoids **Simpson's paradox**: an overall trend can
reverse the trend inside each group.

**Savings estimates**
- **Fuel lost to low MPG:** (actual gallons − gallons at the group's median MPG) × fuel price.
  Only trucks or drivers *below* the median are counted.
- **Idling:** idle hours above the median × fuel burned per idle hour. That burn rate is a
  **documented assumption**, because the data doesn't include it.
- ~~**Fuel purchase price:** price variance by location.~~ **Dropped after phase 2:** the average
  price differs by only $0.02/gallon across cities ($3.886–$3.907), and the state on fuel
  purchases is wrong 95% of the time. There's no signal to support a savings claim, so this lever
  is left out.
- **Data filter for idle analysis:** exclude the 7,450 trips (8.7%) whose idle time exceeds the
  trip duration (rule `idle_exceeds_duration`).

---

## 7. Focus area 4: fleet utilization and maintenance

> **Implemented in module 3** with the **p99** of daily demand rather than p90: the fleet already has spare capacity, so a high percentile costs little and avoids running short. Result: 80 trucks needed at flat volume vs 120 owned. See `docs/05-evaluation` §2.

**Theory**
- **Asset utilization:** a parked truck still costs depreciation, insurance and parking.
- **Fleet sizing:** balance the *cost of holding spare trucks* against the *risk of running
  short*. This is the same trade-off as the newsvendor problem in inventory management.
- **Life-cycle cost and economic life:** as a truck ages, its maintenance cost per mile rises.
  The right time to replace it is when its marginal operating cost exceeds the cost of owning a
  new one. This is equipment replacement theory.

**Techniques**
- **Required fleet size:** count *trucks in use per day*, then take a **high percentile (e.g.
  p90)** as the recommended fleet size. Not the peak, which would keep trucks for a few rare busy
  days. Not the average, which would leave the fleet short half the time. The gap to the current
  fleet is the number of trucks that could be sold or redeployed.
- **Trucks to replace:** rank trucks by maintenance cost per mile, downtime hours, and the share
  of unplanned repairs versus scheduled maintenance, taking the trend with truck age into account.

**Why not ML predictive maintenance:** it needs sensor data (engine temperature, vibration, fault
codes). The dataset has only 2,920 maintenance records and no sensors. A failure-prediction model
on that data wouldn't be trustworthy. Scoring trucks on cost and trend is transparent and enough
to make the decision.

---

## 8. Estimating savings: principles

1. **Benchmark is the median, not best-in-class.** Bringing underperformers up to the fleet's
   own *normal* level is achievable. A best-in-class benchmark would over-promise.
2. **No double counting.** For example, fuel saved by selling trucks and fuel saved by better MPG
   can't simply be added together. Each saving is assigned to exactly one focus area.
3. **Traceable.** Every $ figure leads back to the query and data rows behind it.
4. **Assumptions stated.** Estimated inputs (driver hourly rate, idle fuel burn) are listed and
   adjustable, and the reports display them.
5. **Checked against the target.** Total savings are compared with the ≥ 3% of total operating
   cost target in `docs/01` §5. That comparison belongs to CRISP-DM phase 5 (`docs/05-evaluation`).

---

## 9. Optimization (stretch, only if time allows)

**Truck/driver-to-load assignment** with **linear programming (LP)** in OR-Tools: minimize cost
(empty miles, per-truck cost) subject to each load getting exactly one truck and each truck doing
one job at a time.

**Why not a vehicle routing problem (VRP):** a VRP needs stop-level data (store coordinates,
receiving windows, a distance matrix). This dataset has only 58 long-haul lanes, and each trip is
one origin–destination pair.

**Interview talking point:** for Saigon Co.op, which delivers from distribution centers (DCs) to
hundreds of stores within tight time windows, a **VRP with time windows (VRPTW)** is the natural
next step. The data and KPI layers in this project are the foundation for it.

---

## 10. The role of the LLM (Claude)

**Principle: the LLM explains, the code calculates.** Every number is computed by SQL/Python.
Claude only receives tables of computed numbers and writes the commentary. This is **grounding**.

- **Why:** an LLM can state wrong numbers with full confidence (hallucination). In a report for a
  director, one wrong number discredits the whole report.
- **Plain-English question → SQL:** runs only against the KPI views, read-only, with a row limit.
  The SQL is shown so the user can check it.
- **Cost control:** narratives are cached by (report type, date range, data hash), so re-running
  the same report doesn't call the API again.

**Why not let the LLM analyze the raw data:** the results aren't reproducible (different on every
run), are hard to audit, cost tokens, and are prone to arithmetic errors.

---

## 11. Presentation technology

| Choice | Why | Why not the alternatives |
|---|---|---|
| **Streamlit + Plotly** | Written in Python, so it uses the models and optimization engines directly. Free and reproducible from code | **Power BI / Tableau** are strong BI tools but hard to embed Python models in, need licences, and don't fit well in git |
| **Self-contained HTML/PDF reports** | Can be emailed and opened with nothing installed | Reports that live only in the dashboard can't be shared outside it |

---

## 12. Limitations and presenting them honestly

- **Synthetic Kaggle data.** Some patterns may not look realistic; the preliminary on-time rate,
  for example, is only 55.7%. How to say it in the interview: the *method* is the product, and
  the numbers illustrate how it works.
- **Correlation, not causation.** The delay drivers are hypotheses to verify in the field.
- **Missing cost data** (wages, overhead): contribution margin and documented assumptions are
  used instead.
- **Transfer to the Co.op context:** many stops per trip (DC → stores), cold chain for fresh
  goods, store receiving windows. The KPI framework and workflow stay the same. What's needed in
  addition is stop-level data and a VRPTW model.

---

## References

- Chapman, P. et al. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. SPSS.
- Fayyad, U., Piatetsky-Shapiro, G., Smyth, P. (1996). From data mining to knowledge discovery in databases. *AI Magazine*, 17(3).
- ASCM/APICS. *SCOR Digital Standard* (Supply Chain Operations Reference model).
- DAMA International (2017). *DAMA-DMBOK: Data Management Body of Knowledge*, 2nd ed.
- Kimball, R., Ross, M. (2013). *The Data Warehouse Toolkit*, 3rd ed. Wiley.
- Kaplan, R. S., Cooper, R. (1998). *Cost & Effect: Using Integrated Cost Systems to Drive Profitability and Performance*. HBS Press.
- Kaplan, R. S., Narayanan, V. G. (2001). Measuring and managing customer profitability. *Journal of Cost Management*, 15(5).
- Davenport, T. H., Harris, J. G. (2007). *Competing on Analytics*. HBS Press.
- Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *Annals of Statistics*, 29(5).
- Lundberg, S. M., Lee, S.-I. (2017). A unified approach to interpreting model predictions. *NeurIPS*.
- Grinsztajn, L., Oyallon, E., Varoquaux, G. (2022). Why do tree-based models still outperform deep learning on typical tabular data? *NeurIPS Datasets and Benchmarks*.
- Rubin, D. B. (1976). Inference and missing data. *Biometrika*, 63(3).
- Tukey, J. W. (1977). *Exploratory Data Analysis*. Addison-Wesley.
- Leys, C. et al. (2013). Detecting outliers: Do not use standard deviation around the mean, use absolute deviation around the median. *Journal of Experimental Social Psychology*, 49(4).
