"""Profit the way a business tracks it: P&L by period, profit bridge, unit economics, dimensions.

Costs are booked on the date they occur (fuel on purchase date, maintenance on service date, claims
on the trip's date), revenue on the trip's dispatch date, so period totals reconcile with the KPI
layer's fleet totals for the same range.
"""

import datetime as dt

import duckdb
import polars as pl

from logops.metrics.kpis import FLEET, UNATTRIBUTED, kpi

PERIODS = ("month", "quarter", "year")
_LAGS = {"month": 12, "quarter": 4, "year": 1}  # periods back to the same period last year


def _period(column: str, period: str) -> str:
    if period == "month":
        return f"strftime(date_trunc('month', {column}), '%Y-%m')"
    if period == "quarter":
        return f"CAST(year({column}) AS VARCHAR) || '-Q' || CAST(quarter({column}) AS VARCHAR)"
    if period == "year":
        return f"CAST(year({column}) AS VARCHAR)"
    raise ValueError(f"period must be one of {PERIODS}")


def _sums(
    con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date, period: str
) -> pl.DataFrame:
    p = _period
    sql = f"""
        WITH trips_p AS (
            SELECT {p("te.dispatch_date", period)} AS period, count(*) AS trips,
                   sum(te.miles) AS miles, sum(te.gallons_burned) AS gallons_burned,
                   sum(l.revenue) AS linehaul, sum(l.fuel_surcharge) AS fuel_surcharge,
                   sum(l.accessorial_charges) AS accessorials,
                   count(DISTINCT (te.truck_id, date_trunc('week', te.dispatch_date)))
                       FILTER (WHERE te.truck_id IS NOT NULL) AS truck_weeks
            FROM trip_economics te JOIN loads l ON l.load_id = te.load_id
            WHERE te.dispatch_date BETWEEN $start AND $end GROUP BY ALL
        ),
        fuel_p AS (
            SELECT {p("purchase_date", period)} AS period, sum(total_cost) AS fuel_cost
            FROM fuel_purchases WHERE purchase_date::DATE BETWEEN $start AND $end GROUP BY ALL
        ),
        maint_p AS (
            SELECT {p("maintenance_date", period)} AS period, sum(total_cost) AS maintenance_cost
            FROM maintenance_records WHERE maintenance_date BETWEEN $start AND $end GROUP BY ALL
        ),
        claims_p AS (
            SELECT {p("t.dispatch_date", period)} AS period, sum(s.claim_amount) AS claims
            FROM safety_incidents s JOIN trips t ON t.trip_id = s.trip_id
            WHERE t.dispatch_date BETWEEN $start AND $end GROUP BY ALL
        )
        SELECT period,
               coalesce(trips, 0) AS trips, coalesce(miles, 0) AS miles,
               coalesce(gallons_burned, 0) AS gallons_burned,
               coalesce(truck_weeks, 0) AS truck_weeks,
               coalesce(linehaul, 0) AS linehaul, coalesce(fuel_surcharge, 0) AS fuel_surcharge,
               coalesce(accessorials, 0) AS accessorials,
               coalesce(fuel_cost, 0) AS fuel_cost,
               coalesce(maintenance_cost, 0) AS maintenance_cost,
               coalesce(claims, 0) AS claims
        FROM trips_p
        FULL JOIN fuel_p USING (period) FULL JOIN maint_p USING (period)
        FULL JOIN claims_p USING (period)
        ORDER BY period
    """
    cur = con.execute(sql, {"start": start, "end": end})
    return pl.DataFrame(cur.fetchall(), schema=[d[0] for d in cur.description], orient="row")


def _with_totals(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        revenue=pl.col("linehaul") + pl.col("fuel_surcharge") + pl.col("accessorials"),
        measured_cost=pl.col("fuel_cost") + pl.col("maintenance_cost") + pl.col("claims"),
    ).with_columns(
        contribution=pl.col("revenue") - pl.col("measured_cost"),
        margin_pct=100 * (pl.col("revenue") - pl.col("measured_cost")) / pl.col("revenue"),
    )


def pnl(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date, period: str) -> pl.DataFrame:
    """P&L per period, with change vs the previous period and vs the same period last year.

    For months and quarters, year-to-date contribution and the prior year's YTD are included.
    """
    df = _with_totals(_sums(con, start, end, period))
    lag = _LAGS[period]
    change = lambda c, n: 100 * (pl.col(c) / pl.col(c).shift(n) - 1)  # noqa: E731
    df = df.with_columns(
        revenue_vs_prev_pct=change("revenue", 1),
        contribution_vs_prev_pct=change("contribution", 1),
        revenue_yoy_pct=change("revenue", lag),
        contribution_yoy_pct=change("contribution", lag),
    )
    if period != "year":
        df = (
            df.with_columns(year=pl.col("period").str.slice(0, 4))
            .with_columns(contribution_ytd=pl.col("contribution").cum_sum().over("year"))
            .with_columns(contribution_ytd_prior=pl.col("contribution_ytd").shift(lag))
            .drop("year")
        )
    return df


def unit_economics(df: pl.DataFrame) -> pl.DataFrame:
    """Per mile, per trip and per truck-week, from a pnl() table."""
    return df.select(
        "period",
        revenue_per_mile=pl.col("revenue") / pl.col("miles"),
        cost_per_mile=pl.col("measured_cost") / pl.col("miles"),
        contribution_per_mile=pl.col("contribution") / pl.col("miles"),
        revenue_per_trip=pl.col("revenue") / pl.col("trips"),
        contribution_per_trip=pl.col("contribution") / pl.col("trips"),
        revenue_per_truck_week=pl.col("revenue") / pl.col("truck_weeks"),
        contribution_per_truck_week=pl.col("contribution") / pl.col("truck_weeks"),
    )


BRIDGE_PARTS = ("volume", "rate", "fuel_price", "fuel_consumption", "maintenance", "claims")


def bridge(
    con: duckdb.DuckDBPyConnection, a: tuple[dt.date, dt.date], b: tuple[dt.date, dt.date]
) -> dict:
    """Split the change in contribution from period a to period b into additive parts.

    C = trips × (revenue/trip − price × gallons/trip − maintenance/trip − claims/trip), with
    price = fuel cost per gallon burned. Volume uses a's contribution per trip; every per-trip
    change is weighted by b's trips, so the parts add up exactly to C_b − C_a.
    """
    sa, sb = (_with_totals(_sums(con, *rng, "year")).sum() for rng in (a, b))
    sa, sb = sa.row(0, named=True), sb.row(0, named=True)
    t_a, t_b = sa["trips"], sb["trips"]
    per = lambda s, c: s[c] / s["trips"]  # noqa: E731
    price_a = sa["fuel_cost"] / sa["gallons_burned"]
    price_b = sb["fuel_cost"] / sb["gallons_burned"]
    gpt_a, gpt_b = per(sa, "gallons_burned"), per(sb, "gallons_burned")
    parts = {
        "volume": (t_b - t_a) * per(sa, "contribution"),
        "rate": (per(sb, "revenue") - per(sa, "revenue")) * t_b,
        "fuel_price": -(price_b - price_a) * gpt_b * t_b,
        "fuel_consumption": -price_a * (gpt_b - gpt_a) * t_b,
        "maintenance": -(per(sb, "maintenance_cost") - per(sa, "maintenance_cost")) * t_b,
        "claims": -(per(sb, "claims") - per(sa, "claims")) * t_b,
    }
    return {
        "start": sa["contribution"],
        "end": sb["contribution"],
        "parts": parts,
        "fuel_price_a": price_a,
        "fuel_price_b": price_b,
    }


def by_dimension(
    con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date, by: str
) -> pl.DataFrame:
    """Revenue, cost, contribution and shares per group, from the KPI layer (one definition).

    Shares are of the attributed total (all groups except Unattributed and the fleet row), so the
    groups' shares add up to 100%.
    """
    cols = ["group", "revenue", "measured_cost", "contribution", "contribution_margin_pct"]
    table = (
        kpi(con, start, end, by=by)
        .select(cols)
        .with_columns(is_total=pl.col("group").is_in([FLEET, UNATTRIBUTED]))
    )
    groups = table.filter(~pl.col("is_total"))
    return table.with_columns(
        revenue_share_pct=100 * pl.col("revenue") / groups["revenue"].sum(),
        contribution_share_pct=100 * pl.col("contribution") / groups["contribution"].sum(),
    )


def concentration(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> dict:
    """Customer revenue concentration: top-10/20 share, largest share, customers for 80%, HHI."""
    shares = [
        s
        for (s,) in con.execute(
            "SELECT sum(revenue) / (SELECT sum(revenue) FROM trip_economics "
            "WHERE dispatch_date BETWEEN $start AND $end) AS share "
            "FROM trip_economics WHERE dispatch_date BETWEEN $start AND $end "
            "GROUP BY customer_id ORDER BY share DESC",
            {"start": start, "end": end},
        ).fetchall()
    ]
    cumulative, n80 = 0.0, len(shares)
    for i, s in enumerate(shares, start=1):
        cumulative += s
        if cumulative >= 0.8:
            n80 = i
            break
    return {
        "customers": len(shares),
        "top10_pct": 100 * sum(shares[:10]),
        "top20_pct": 100 * sum(shares[:20]),
        "largest_pct": 100 * shares[0],
        "customers_for_80pct": n80,
        "hhi": sum((100 * s) ** 2 for s in shares),
        "pareto": [100 * sum(shares[:i]) for i in range(1, len(shares) + 1)],
    }


def margin_vs_fuel(
    con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date
) -> tuple[pl.DataFrame, float]:
    """Monthly margin next to the monthly average fuel price, and their correlation."""
    months = pnl(con, start, end, "month").select(
        "period", "margin_pct", fuel_price=pl.col("fuel_cost") / pl.col("gallons_burned")
    )
    price = con.execute(
        "SELECT strftime(date_trunc('month', purchase_date), '%Y-%m') AS period, "
        "sum(total_cost) / sum(gallons) AS avg_price FROM fuel_purchases "
        "WHERE purchase_date::DATE BETWEEN $start AND $end GROUP BY ALL",
        {"start": start, "end": end},
    ).fetchall()
    table = months.drop("fuel_price").join(
        pl.DataFrame(price, schema=["period", "avg_fuel_price"], orient="row"), on="period"
    )
    return table, table.select(pl.corr("margin_pct", "avg_fuel_price")).item()
