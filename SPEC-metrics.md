# Spec: metrics

> Module 2 of 6 · see [CAPABILITY-MAP.md](CAPABILITY-MAP.md) · CRISP-DM phase 3 (Data Preparation) ·
> Vietnamese: [SPEC-metrics.vi.md](SPEC-metrics.vi.md) · Inputs: module 1's warehouse and
> [docs/02-data-understanding.md](docs/02-data-understanding.md) §5

## Objective

Build **one KPI layer** that every later module (`optimize`, `dashboard`, `reports`) reads from, so
each number has exactly one definition. KPIs follow SCOR: **cost, delivery reliability, asset
efficiency**, plus fuel and safety.

**Principles**
- **No invention:** compute only what the data supports. What the data lacks (driver pay) is left
  out and labelled as missing.
- **Ratios = sum of numerators ÷ sum of denominators**, never an average of ratios.
- **Totals always reconcile:** the groups (lanes, customers, trucks…) plus an "Unattributed" line
  add up to the fleet total.

## Outputs (the module's contract)

### O1. Three base views in DuckDB (created by `logops build`)

| View | One row per | Rows | Main contents |
|---|---|---:|---|
| `trip_economics` | trip | 85,410 | lane, customer, truck, driver, month; miles; revenue (linehaul, fuel surcharge, accessorials); fuel, maintenance and incident cost (allocated, see below); **contribution** = revenue − measured cost |
| `delivery_performance` | pickup or delivery | 170,820 | deviation from appointment (minutes), `on_time_flag`, detention minutes, `location_city`, appointment hour of day, weekday, lane, customer |
| `truck_economics` | truck | 120 | miles, trips, revenue, maintenance cost, downtime, maintenance cost per mile, average utilization, model year, gallons purchased ÷ gallons burned |

**Cost allocation** (checked on the real data):

| Cost | How it's assigned to a trip | Why |
|---|---|---|
| Fuel | Fuel spend *in the month* × (trip gallons burned ÷ total gallons burned in the month) | Fuel purchases aren't reliably linked to trips: 29% more gallons were bought than burned, and per trip the ratio ranges from 0.32 to 9. Allocating by actual consumption keeps total spend exact |
| Maintenance | Truck's maintenance cost *in the month* ÷ truck's miles in the month × trip miles | For the 92 trucks that run, every month with maintenance also has trips, so truck-month allocation reconciles at any date filter. The other 690 records ($1.40M, 24% of maintenance cost) belong to the 28 trucks that never ran a trip: 13 `Inactive`, 15 `Maintenance` |
| Incidents | Directly by `trip_id` | Incident records carry the trip ID |
| Driver pay | **Not included** | Not in the data. Contribution is labelled *before driver pay* |

Whatever can't be assigned to a trip (maintenance of the 28 trucks that never ran a trip, fuel spend
in a month with no trips) goes to an **"Unattributed"** line, so totals always reconcile.

### O2. KPI function: `kpi(con, start, end, by=None, on_time_window_min=120)`

Returns a table: one row per group (`by`) plus the fleet total. `by` can be `None`, `month`, `route`,
`customer`, `customer_type`, `truck`, `driver`, or `location_city` (delivery KPIs only).

**KPI catalog (21)**

| SCOR area | KPI | Formula |
|---|---|---|
| Cost | `revenue` | Σ linehaul + fuel surcharge + accessorials |
| | `measured_cost` | Σ fuel + maintenance + incidents |
| | `cost_per_mile` | `measured_cost` ÷ Σ miles |
| | `fuel_cost_per_mile`, `maintenance_cost_per_mile`, `safety_cost_per_mile` | Each component ÷ Σ miles |
| | `revenue_per_mile` | `revenue` ÷ Σ miles |
| | `contribution`, `contribution_margin_pct` | `revenue` − `measured_cost`; divided by `revenue` |
| | `out_of_route_pct` | Σ (actual miles − lane's typical miles) ÷ Σ typical miles |
| Fuel | `mpg` | Σ miles ÷ Σ gallons burned |
| | `fuel_purchased_to_burned` | Σ gallons purchased ÷ Σ gallons burned (fuel-card control) |
| Reliability | `on_time_pct` | % of deliveries with \|deviation\| ≤ window (default 120 min = `on_time_flag`) |
| | `not_late_pct` | % of deliveries with actual ≤ appointment |
| | `avg_detention_min`, `detention_hours` | Mean and total detention |
| Assets | `miles_per_truck_month` | Σ miles ÷ truck-months with activity |
| | `utilization` | Mean `utilization_rate` (for comparing trucks only) |
| | `downtime_hours` | Σ maintenance downtime |
| Safety | `incidents_per_million_miles`, `preventable_pct` | Incidents ÷ Σ miles × 10⁶; % of incidents that were preventable |

### O3. `logops kpi` command

`uv run logops kpi --by route --from 2024-01-01 --to 2024-12-31 --window 60` prints the KPI table
in the terminal, for quick checks and for the demo.

### O4. Documents

- `docs/03-kpi-definitions.md` / `.vi.md`: **generated** from the KPI catalog in code (name, formula,
  unit, source, fleet value), so it can never drift from the code.
- `docs/reviews/02-metrics.md` / `.vi.md`: the end-of-module review (see below).

## Out of scope

| Not done | Why |
|---|---|
| Idle-time KPI | `idle_time_hours` is random noise: correlation ≈ 0 with trip duration, distance and fuel |
| Fuel price by location | $0.02/gallon difference across cities: no signal |
| KPIs by `facility_id` | The column is essentially random; `location_city` is used |
| Driver pay, net profit | Not in the data |
| Savings estimates, recommendations | Belong to the `optimize` module. Example: whether to keep the 28 trucks that never ran a trip, given current volume and its trend. This module only supplies the figures (`truck_economics`); the recommendation appears on the dashboard for the viewer to weigh |
| Charts | Belong to `dashboard` and `reports` |

## Success criteria

1. **Matches the DQ report:** total revenue $298.62M, fuel $95.59M, maintenance $5.73M, incidents
   $2.65M; cost per mile $0.851; MPG 6.45; on time 44.6% (120-minute window).
2. **Totals reconcile:** for every `by`, groups + "Unattributed" = fleet total, for every additive KPI.
3. **On-time window is a parameter:** 120 minutes reproduces `on_time_flag`; changing the window changes `on_time_pct`. The not-late rate is a separate KPI (`not_late_pct`).
4. **Date filter is correct:** filtering to 2024 gives exactly the 2024 totals.
5. Each KPI group has at least one fixture test, plus one integration test against the real figures;
   `ruff` clean.
6. The build gets no more than 5 s slower.

## End-of-module review (applies to every module)

At the end, write `docs/reviews/02-metrics.md` / `.vi.md`: outputs delivered vs the spec, actual
measured figures, what was **not** achieved and why, and new data findings. Only verified facts.
Also update `docs/SUMMARY.md` / `.vi.md` (the project-wide summary).

## Plan (6 tasks)

| Task | Content | Verification |
|---|---|---|
| M1 | `trip_economics` view + cost allocation | Totals match the DQ report (criterion 1) |
| M2 | `delivery_performance` view + on-time window | 44.6% at 120 min; not late 33.3% |
| M3 | `kpi()` function: 21-KPI catalog, `by`, date filter, "Unattributed" line | Criteria 2 and 4 |
| M4 | `truck_economics` view + asset and safety KPIs | Fixture tests |
| M5 | `logops kpi` command + `docs/03-kpi-definitions` | Run the command on the real data |
| M6 | Reviews for modules 1 and 2 + `docs/SUMMARY` | Read-through; every number has a source |

## Open questions

None. Driver pay is out of scope rather than assumed.
