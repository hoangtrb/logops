# Demo script (interview, 2026-10-05)

> Vietnamese: [demo-script.vi.md](demo-script.vi.md) · Figures: [SUMMARY.md](SUMMARY.md) ·
> Reviews: [reviews/](reviews/) · Every figure below comes from the dashboard, period
> 2022-01-01 – 2024-12-31.

## 0. Before the meeting

- [ ] `uv run logops dashboard` → open http://localhost:8501, choose **Vi**, visit every page once
  so the data is cached (first visit takes a few seconds, then under 3 s).
- [ ] Close anything holding `data/warehouse.duckdb` open (DBeaver, notebooks).
- [ ] Keep the fallback copies in `reports/output/`: `bao-cao-van-tai-2022-01-01-2024-12-31.pdf`
  and `.html` (opens offline).
- [ ] Collapse the sidebar on a small screen; zoom the browser to 110%.

## 1. Opening (30 s)

> "I took the operating data of a road freight carrier (Kaggle, synthetic: 120 trucks, 200
> customers, 85 thousand trips over 3 years) and set the problem as a transport director would:
> cut operating cost by at least 3% a year and improve delivery performance. I followed CRISP-DM
> in six modules, from cleaning the data to the dashboard and exportable reports."

Page: **Executive overview** (the "Project and data source" card at the top).

## 2. Executive overview (1 min)

- Revenue **$298.62M**, operating cost **$103.88M**, contribution profit **$194.74M**, margin
  **65.2%** (before driver pay and overhead: not in the data).
- On-time **44.6%** within ±2 h, but **91.2%** by appointment day: same data, the standard decides
  the story.
- Priority finding: **profit rose because fuel got cheaper, not because operations improved**: 93% of
  the gain ($4.12M of $4.42M) comes from fuel prices, since the fuel surcharge charged to customers
  stayed flat. A risk when fuel prices rise again.

## 3. Lane performance (1 min)

- **33% of loads end where there is no return load**; 16 of 20 cities are imbalanced by over 20%.
- In 95.4% of cases a truck's next trip starts in another city: exactly the random-dispatch level,
  so the data shows no chaining by truck position.
- Lane assessment: every lane has a positive contribution; low-margin lanes call for **renegotiating
  rates**, not closing lanes.

## 4. Fleet capacity (45 s)

- 92 trucks have run trips, 120 owned; on 99% of days at most 75 run at the same time.
- **28 trucks never ran a trip in 3 years** yet cost $1.40M in maintenance.

## 5. Optimization recommendations (2 min): the core

Hover over each card to show how it is computed.

| Card | Figure | What to say |
|---|---:|---|
| Target | $1.04M/yr | 3% × $34.65M of measured operating cost a year |
| Measured saving | $0.47M | Dispose of the 28 trucks that never ran: certain, no effect on operations |
| Maximum potential | $2.42M | Fuel surcharge to the median, up to +5% on 20 low-margin lanes, review 13 little-used trucks: needs customers to accept |
| Total | $2.89M (278%) | The target is reached with the certain part plus $0.57M more, e.g. customers accepting 59.6% of the surcharge increase |

- **Trip chaining (simulation):** send the nearest free truck to each load → trips needing a
  move fall from 89.5% to 41.1%, empty miles by 59.5%. Distances come from the lanes and an
  empty mile costs $0.605 (fuel price ÷ miles per gallon, both from the data). Hover the card:
  the model alone says $12.56M, more than the fuel bought off trips, so I apply only the cut to
  that fuel: **up to $4.27M a year**, kept out of the total.
- **How long should an empty move be?** Keep it within one driving day (11 h, about 630 miles);
  beyond that, find a return load on the spot. A hard limit doesn't work here: a third of loads
  end in cities that send little back, and any limit up to 24 h needs thousands more trucks.
- **Checked and not recommended:** late deliveries have no repeatable cause by customer, lane,
  driver or appointment hour (year-to-year correlation ≤ 0.14): instead of inventing a fix, record a
  reason code for every late delivery.

## 6. Report export (45 s)

- Sidebar → **Export report** → PDF → **Create report**: runs in the background, the dashboard stays
  usable; the Download button turns solid green when done.
- Open the PDF: cover (project, data source) → contents, lists of figures and tables with page
  numbers → one-page **executive summary** (act now, keep watching, savings).

## 7. Close (30 s)

> "For Co.op the same framework works on internal trip, truck, fuel and delivery data. Three things
> I would start with, at almost no cost: reconcile fuel cards with trips per truck every month;
> record every move between trips; record a reason code for late deliveries. With those, today's
> 'unexplained' and 'hypothesis' figures become measured."

## 8. Likely questions

| Question | Short answer |
|---|---|
| Synthetic data: does it apply to real operations? | The method and the data checks do; the figures must be recomputed on real data. The inconsistencies of the synthetic data are stated (e.g. 54% of a truck's consecutive trips overlap in time). |
| Isn't a 65% margin unusually high? | It is contribution profit, before driver pay and overhead (not in the data). A break-even driver cost replaces it: the weakest lane loses money only above $0.857 per mile. |
| Why is on-time only 44.6%? | The data's on-time flag is ±2 h, early arrivals included. By appointment day it is 91.2%. Deviations are spread evenly from −3 to +6 h whatever the trip length. |
| Won't higher rates lose customers? | Each lane has a break-even volume loss: median 9.6% at +5%, the volume it can lose and still earn as much as today. That is why pricing is a maximum potential, not a certain saving. |
| How is the trip-chaining saving computed? | Distance between cities from the lanes (shortest path where there is no direct lane), fuel per mile = $3.899 a gallon ÷ 6.45 miles a gallon, both from the data. The replay cuts empty miles by 59.5%; applied to the $7.18M of fuel bought off trips that is $4.27M a year at most. The lane-based distances are longer than real roads, so real coordinates would sharpen it. |
| Why nothing on drivers or staffing? | The scope is operational productivity and quality; the data has no driver pay either. |
| Tools? | Python, DuckDB, Polars, Streamlit, Plotly; 160 automated tests; runs on one laptop, no server. |
| What would Co.op need? | Extract trip, truck, fuel and delivery data from the TMS/ERP into the same structure; run the data-quality rules first, then the KPIs and recommendations. |
