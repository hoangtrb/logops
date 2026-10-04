"""Late deliveries: is there a cause the company could act on?

For each dimension (delivery city, customer, appointment hour, lane, driver) the share of deliveries
more than 2 hours late is computed per group, separately for the earlier years and the last year.
A dimension is a lever only if the group rates repeat (correlation ≥ PERSISTENT_CORR, the project
rule) — otherwise the differences between groups are chance, and acting on them would not pay.
"""

import datetime as dt

import duckdb
import polars as pl

LATE_MINUTES = 120  # more than 2 hours late (early deliveries are never counted as late)
PERSISTENT_CORR = 0.7  # same rule as insights.THRESHOLDS["persistent_corr"]
MIN_DELIVERIES = 30  # per group and period, so a rate is not one or two deliveries
DIMENSIONS = {
    "city": "location_city",
    "customer": "customer_id",
    "appointment_hour": "appointment_hour",
    "lane": "lane",
    "driver": "driver_id",
}

_RATES = """
    SELECT CAST({col} AS VARCHAR) AS grp, year(dispatch_date) = $last AS recent,
           count(*) AS deliveries, avg((deviation_min > $late)::INT) AS late
    FROM delivery_performance
    WHERE event_type = 'Delivery' AND deviation_min IS NOT NULL AND {col} IS NOT NULL
      AND dispatch_date BETWEEN $start AND $end
    GROUP BY ALL
"""


def _frame(cur) -> pl.DataFrame:
    return pl.DataFrame(cur.fetchall(), schema=[d[0] for d in cur.description], orient="row")


def late_share(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> float:
    """Share of deliveries more than 2 hours late, in percent."""
    return con.execute(
        "SELECT 100 * avg((deviation_min > $late)::INT) FROM delivery_performance "
        "WHERE event_type = 'Delivery' AND deviation_min IS NOT NULL "
        "AND dispatch_date BETWEEN $start AND $end",
        {"late": LATE_MINUTES, "start": start, "end": end},
    ).fetchone()[0]


def persistence(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> pl.DataFrame:
    """Per dimension: groups compared, spread of late rates, correlation earlier vs last year."""
    params = {"start": start, "end": end, "last": end.year, "late": LATE_MINUTES}
    rows = []
    for name, col in DIMENSIONS.items():
        df = _frame(con.execute(_RATES.format(col=col), params))
        wide = (
            df.filter(pl.col("deliveries") >= MIN_DELIVERIES)
            .pivot(on="recent", index="grp", values="late")
            .drop_nulls()
        )
        if wide.height < 3 or "true" not in wide.columns or "false" not in wide.columns:
            rows.append((name, wide.height, None, None, False))
            continue
        corr = wide.select(pl.corr("false", "true")).item()
        spread = 100 * (wide["false"].max() - wide["false"].min())  # earlier years
        rows.append((name, wide.height, spread, corr, corr is not None and corr >= PERSISTENT_CORR))
    return pl.DataFrame(
        rows,
        schema=["dimension", "groups", "spread_pts", "persistence", "signal"],
        orient="row",
    )
