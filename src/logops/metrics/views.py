"""Base views of the KPI layer. Every later module reads these instead of the raw tables.

Cost allocation (see SPEC-metrics.md, "Cost allocation"):
- fuel: the month's fuel spend, split across that month's trips by gallons burned. Fuel purchases
  aren't reliably linked to trips (29% more gallons bought than burned fleet-wide).
- maintenance: a truck's cost in a month, split across its trips that month by miles. Maintenance
  of trucks that ran no trip that month stays unallocated (it's the "Unattributed" line in kpi()).
- incidents: directly by trip_id.
Driver pay isn't in the data, so contribution is before driver pay.
"""

import duckdb

VIEWS = {
    "trip_economics": """
        WITH trips_m AS (
            SELECT *, date_trunc('month', dispatch_date)::DATE AS month FROM trips
        ),
        fuel_month AS (
            SELECT date_trunc('month', purchase_date)::DATE AS month, sum(total_cost) AS spend
            FROM fuel_purchases GROUP BY ALL
        ),
        burned_month AS (
            SELECT month, sum(fuel_gallons_used) AS gallons FROM trips_m GROUP BY ALL
        ),
        maintenance_truck_month AS (
            SELECT truck_id, date_trunc('month', maintenance_date)::DATE AS month,
                   sum(total_cost) AS cost
            FROM maintenance_records GROUP BY ALL
        ),
        miles_truck_month AS (
            SELECT truck_id, month, sum(actual_distance_miles) AS miles
            FROM trips_m WHERE truck_id IS NOT NULL GROUP BY ALL
        ),
        purchased AS (
            SELECT trip_id, sum(gallons) AS gallons FROM fuel_purchases GROUP BY ALL
        ),
        incidents AS (
            SELECT trip_id, sum(claim_amount) AS cost, count(*) AS n,
                   count(*) FILTER (WHERE preventable_flag) AS preventable
            FROM safety_incidents GROUP BY ALL
        ),
        base AS (
            SELECT
                t.trip_id, t.load_id, t.dispatch_date, t.month,
                l.route_id, r.origin_city || ' → ' || r.destination_city AS lane,
                r.origin_state, r.destination_state,
                l.customer_id, c.customer_type, l.booking_type, l.load_type,
                t.driver_id, t.truck_id,
                t.actual_distance_miles AS miles, r.typical_distance_miles AS typical_miles,
                t.fuel_gallons_used AS gallons_burned,
                coalesce(p.gallons, 0) AS gallons_purchased,
                l.revenue + l.fuel_surcharge + l.accessorial_charges AS revenue,
                coalesce(t.fuel_gallons_used * fm.spend / bm.gallons, 0) AS fuel_cost,
                coalesce(t.actual_distance_miles * mt.cost / mm.miles, 0) AS maintenance_cost,
                coalesce(i.cost, 0) AS safety_cost,
                coalesce(i.n, 0) AS incidents,
                coalesce(i.preventable, 0) AS preventable_incidents
            FROM trips_m t
            JOIN loads l USING (load_id)
            JOIN routes r ON r.route_id = l.route_id
            JOIN customers c ON c.customer_id = l.customer_id
            JOIN burned_month bm ON bm.month = t.month
            LEFT JOIN fuel_month fm ON fm.month = t.month
            LEFT JOIN maintenance_truck_month mt ON mt.truck_id = t.truck_id AND mt.month = t.month
            LEFT JOIN miles_truck_month mm ON mm.truck_id = t.truck_id AND mm.month = t.month
            LEFT JOIN purchased p ON p.trip_id = t.trip_id
            LEFT JOIN incidents i ON i.trip_id = t.trip_id
        )
        SELECT *,
               fuel_cost + maintenance_cost + safety_cost AS measured_cost,
               revenue - (fuel_cost + maintenance_cost + safety_cost) AS contribution
        FROM base
    """,
    "delivery_performance": """
        SELECT
            d.event_id, d.trip_id, d.load_id, d.event_type,
            te.dispatch_date, te.month,
            d.scheduled_datetime, d.actual_datetime,
            epoch(d.actual_datetime - d.scheduled_datetime) / 60 AS deviation_min,
            d.on_time_flag, d.detention_minutes, d.location_city,
            hour(d.scheduled_datetime) AS appointment_hour,
            dayname(d.scheduled_datetime) AS weekday,
            te.route_id, te.lane, te.customer_id, te.customer_type, te.driver_id, te.truck_id,
            te.load_type, te.origin_state, te.destination_state
        FROM delivery_events d
        JOIN trip_economics te ON te.trip_id = d.trip_id
    """,
    "truck_economics": """
        WITH trip_totals AS (
            SELECT truck_id, count(*) AS trips, sum(miles) AS miles, sum(revenue) AS revenue,
                   sum(gallons_burned) AS gallons_burned, count(DISTINCT month) AS active_months
            FROM trip_economics WHERE truck_id IS NOT NULL GROUP BY ALL
        ),
        maintenance AS (
            SELECT truck_id, count(*) AS events, sum(total_cost) AS cost,
                   sum(downtime_hours) AS downtime
            FROM maintenance_records GROUP BY ALL
        ),
        purchased AS (
            SELECT truck_id, sum(gallons) AS gallons
            FROM fuel_purchases WHERE truck_id IS NOT NULL GROUP BY ALL
        ),
        utilization AS (
            SELECT truck_id, avg(utilization_rate) AS rate
            FROM truck_utilization_metrics GROUP BY ALL
        )
        SELECT
            k.truck_id, k.make, k.model_year, k.status, k.acquisition_date,
            coalesce(t.trips, 0) AS trips, coalesce(t.miles, 0) AS miles,
            coalesce(t.revenue, 0) AS revenue, coalesce(t.active_months, 0) AS active_months,
            coalesce(m.events, 0) AS maintenance_events,
            coalesce(m.cost, 0) AS maintenance_cost,
            coalesce(m.downtime, 0) AS downtime_hours,
            m.cost / nullif(t.miles, 0) AS maintenance_cost_per_mile,
            u.rate AS avg_utilization,
            p.gallons / nullif(t.gallons_burned, 0) AS fuel_purchased_to_burned
        FROM trucks k
        LEFT JOIN trip_totals t ON t.truck_id = k.truck_id
        LEFT JOIN maintenance m ON m.truck_id = k.truck_id
        LEFT JOIN purchased p ON p.truck_id = k.truck_id
        LEFT JOIN utilization u ON u.truck_id = k.truck_id
    """,
}


def create_views(con: duckdb.DuckDBPyConnection) -> None:
    """Create (or replace) the base views, in dependency order."""
    for name, sql in VIEWS.items():
        con.execute(f'CREATE OR REPLACE VIEW "{name}" AS {sql}')
