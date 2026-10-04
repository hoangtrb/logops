"""Delivery service and fleet-asset figures for the dashboard (computed here, only drawn there)."""

import datetime as dt

import duckdb
import polars as pl

from logops.analysis.operations import daily_trucks
from logops.analysis.profit import totals
from logops.metrics.kpis import FLEET, UNATTRIBUTED, kpi

SENSITIVITY_WINDOWS = tuple(range(0, 241, 15))  # minutes


def _frame(cur) -> pl.DataFrame:
    return pl.DataFrame(cur.fetchall(), schema=[d[0] for d in cur.description], orient="row")


def _fleet_row(table: pl.DataFrame) -> dict:
    return table.filter(pl.col("group") == FLEET).row(0, named=True)


def service_summary(
    con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date, window: float = 120
) -> dict:
    """Fleet delivery KPIs for one on-time window (from the KPI layer)."""
    row = _fleet_row(kpi(con, start, end, on_time_window_min=window))
    keys = ("on_time_pct", "not_late_pct", "avg_detention_min", "detention_hours")
    return {k: row[k] for k in keys}


_TIMING = """
    WITH d AS (
        SELECT p.deviation_min / 60.0 AS dev_h,
               CAST(p.actual_datetime AS DATE) <= CAST(p.scheduled_datetime AS DATE) AS by_day,
               t.actual_duration_hours AS hours, t.actual_distance_miles AS miles
        FROM delivery_performance p JOIN trips t ON t.trip_id = p.trip_id
        WHERE p.event_type = 'Delivery' AND p.deviation_min IS NOT NULL
          AND p.dispatch_date BETWEEN $start AND $end
    )
"""
TRIP_LENGTH_BANDS = (24, 48)  # trip hours: under one day, one to two days, longer


def delivery_timing(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> dict:
    """When deliveries arrive against the appointment, and on-time under four standards.

    - window: within ±2 hours (the data's own on_time_flag)
    - not_late: at or before the appointment
    - late_le_2h: no more than 2 hours late (early counts as on time)
    - by_day: on or before the appointment date
    Also the spread of the deviation in whole hours, and the same rates by trip length, to see
    whether long trips are judged unfairly.
    """
    params = {"start": start, "end": end}
    standards = con.execute(
        _TIMING
        + """
        SELECT 100 * avg((abs(dev_h) <= 2)::INT), 100 * avg((dev_h <= 0)::INT),
               100 * avg((dev_h <= 2)::INT), 100 * avg(by_day::INT),
               min(dev_h), max(dev_h), count(*)
        FROM d
        """,
        params,
    ).fetchone()
    spread = _frame(
        con.execute(
            _TIMING + "SELECT floor(dev_h)::INT AS hour, count(*) AS deliveries FROM d "
            "GROUP BY ALL ORDER BY hour",
            params,
        )
    )
    a, b = TRIP_LENGTH_BANDS
    by_length = _frame(
        con.execute(
            _TIMING
            + f"""
            SELECT CASE WHEN hours < {a} THEN 1 WHEN hours < {b} THEN 2 ELSE 3 END AS band,
                   count(*) AS deliveries, avg(miles) AS avg_miles,
                   100 * avg((abs(dev_h) <= 2)::INT) AS window_pct,
                   100 * avg((dev_h <= 2)::INT) AS late_le_2h_pct,
                   100 * avg(by_day::INT) AS by_day_pct
            FROM d GROUP BY ALL ORDER BY band
            """,
            params,
        )
    )
    keys = ("window", "not_late", "late_le_2h", "by_day", "min_dev_h", "max_dev_h", "deliveries")
    return dict(zip(keys, standards, strict=True)) | {"spread": spread, "by_length": by_length}


def scorecard(
    con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date, window: float = 120
) -> dict:
    """Headline logistics KPIs for one period.

    Money comes from the P&L (each cost booked on its own date), delivery from the KPI layer, and
    fleet use is the average number of trucks busy per day over the trucks owned.
    """
    money = totals(con, start, end)
    service = service_summary(con, start, end, window)
    busy = daily_trucks(con, start, end)["trucks_busy"].mean()
    owned = con.execute("SELECT count(*) FROM trucks").fetchone()[0]
    return {
        "revenue": money["revenue"],
        "contribution": money["contribution"],
        "margin_pct": money["margin_pct"],
        "cost_per_mile": money["measured_cost"] / money["miles"] if money["miles"] else None,
        "trips": money["trips"],
        "otd_pct": service["on_time_pct"],
        "otd_by_day_pct": delivery_timing(con, start, end)["by_day"],
        "revenue_per_truck_week": (
            money["revenue"] / money["truck_weeks"] if money["truck_weeks"] else None
        ),
        "not_late_pct": service["not_late_pct"],
        "avg_detention_min": service["avg_detention_min"],
        "avg_trucks_busy": busy,
        "trucks_owned": owned,
        "fleet_use_pct": 100 * busy / owned if owned else None,
    }


def on_time_sensitivity(
    con: duckdb.DuckDBPyConnection,
    start: dt.date,
    end: dt.date,
    windows: tuple[int, ...] = SENSITIVITY_WINDOWS,
) -> pl.DataFrame:
    """% of deliveries within ±window minutes of the appointment, for each window."""
    cols = ", ".join(f"100 * avg((abs(deviation_min) <= {w})::INT) AS w{w}" for w in windows)
    row = con.execute(
        f"SELECT {cols} FROM delivery_performance "
        "WHERE event_type = 'Delivery' AND dispatch_date BETWEEN $start AND $end",
        {"start": start, "end": end},
    ).fetchone()
    return pl.DataFrame({"window_min": list(windows), "on_time_pct": list(row)})


def service_by(
    con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date, by: str, window: float = 120
) -> pl.DataFrame:
    """On-time %, not-late % and detention per month or per delivery city."""
    table = kpi(con, start, end, by=by, on_time_window_min=window)
    return (
        table.filter(~pl.col("group").is_in([FLEET, UNATTRIBUTED]))
        .select("group", "on_time_pct", "not_late_pct", "avg_detention_min")
        .drop_nulls("on_time_pct")
    )


def detention_by_type(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> pl.DataFrame:
    """Average detention minutes per year for pickups and for deliveries."""
    return _frame(
        con.execute(
            "SELECT year(dispatch_date) AS year, event_type, avg(detention_minutes) AS avg_minutes "
            "FROM delivery_performance WHERE dispatch_date BETWEEN $start AND $end "
            "GROUP BY ALL ORDER BY year, event_type",
            {"start": start, "end": end},
        )
    )


def fleet_status(con: duckdb.DuckDBPyConnection) -> pl.DataFrame:
    """Trucks by status, split into trucks that ran trips and trucks that never did."""
    return _frame(
        con.execute(
            "SELECT status, trips > 0 AS used, count(*) AS trucks FROM truck_economics "
            "GROUP BY ALL ORDER BY used DESC, status"
        )
    )


def idle_trucks(con: duckdb.DuckDBPyConnection) -> pl.DataFrame:
    """Trucks that never ran a trip, with what they cost (descriptive only)."""
    return _frame(
        con.execute(
            "SELECT truck_id, make, model_year, status, maintenance_events, maintenance_cost, "
            "downtime_hours FROM truck_economics WHERE trips = 0 ORDER BY maintenance_cost DESC"
        )
    )


def truck_productivity(con: duckdb.DuckDBPyConnection) -> pl.DataFrame:
    """Per truck in use: miles, trips, revenue, active months, average utilization."""
    return _frame(
        con.execute(
            "SELECT truck_id, trips, miles, revenue, active_months, avg_utilization, "
            "miles / nullif(active_months, 0) AS miles_per_active_month "
            "FROM truck_economics WHERE trips > 0 ORDER BY miles DESC"
        )
    )


def fleet_productivity(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> dict:
    row = _fleet_row(kpi(con, start, end))
    return {k: row[k] for k in ("miles_per_truck_month", "utilization", "downtime_hours")}


def customer_names(con: duckdb.DuckDBPyConnection) -> dict[str, str]:
    return dict(con.execute("SELECT customer_id, customer_name FROM customers").fetchall())


def data_bounds(con: duckdb.DuckDBPyConnection) -> tuple[dt.date, dt.date]:
    """First and last dispatch date in the warehouse."""
    return con.execute("SELECT min(dispatch_date), max(dispatch_date) FROM trips").fetchone()
