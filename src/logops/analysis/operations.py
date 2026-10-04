"""Fuel statistics, fleet capacity, and network analyses (lane matrix, balance, repositioning).

Fuel is reported as statistics only (no interpretation of the bought-vs-burned gap). Fleet capacity
is planned by service level (how many trucks cover 95% / 99% of days), because the timing of
peaks is not predictable in this data. Network analyses follow the dataset author's notebook,
corrected: real costs, ratios as sums ÷ sums, and imbalance measured per city.
"""

import datetime as dt
import math

import duckdb
import polars as pl

from logops.analysis.profit import _period
from logops.metrics.kpis import FLEET, UNATTRIBUTED, kpi


def _frame(cur) -> pl.DataFrame:
    return pl.DataFrame(cur.fetchall(), schema=[d[0] for d in cur.description], orient="row")


# ------------------------------------------------------------------ fuel (statistics only)


def fuel_by_period(
    con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date, period: str
) -> pl.DataFrame:
    sql = f"""
        WITH bought AS (
            SELECT {_period("purchase_date", period)} AS period, sum(gallons) AS gallons_bought,
                   sum(total_cost) AS spend
            FROM fuel_purchases WHERE purchase_date::DATE BETWEEN $start AND $end GROUP BY ALL
        ),
        burned AS (
            SELECT {_period("dispatch_date", period)} AS period,
                   sum(fuel_gallons_used) AS gallons_burned
            FROM trips WHERE dispatch_date BETWEEN $start AND $end GROUP BY ALL
        )
        SELECT period, gallons_bought, spend, spend / gallons_bought AS avg_price,
               gallons_burned, gallons_bought / gallons_burned AS bought_to_burned
        FROM bought FULL JOIN burned USING (period) ORDER BY period
    """
    return _frame(con.execute(sql, {"start": start, "end": end}))


# ------------------------------------------------------------------ fleet capacity


_DAILY = """
    WITH occupied AS (
        SELECT truck_id,
               unnest(range(dispatch_date,
                            dispatch_date + greatest(ceil(actual_duration_hours / 24), 1)::INT
                                * INTERVAL 1 DAY,
                            INTERVAL 1 DAY))::DATE AS day
        FROM trips WHERE truck_id IS NOT NULL
    ),
    days AS (
        SELECT unnest(range($start::DATE, $end::DATE + INTERVAL 1 DAY, INTERVAL 1 DAY))::DATE AS day
    )
    SELECT d.day, count(DISTINCT o.truck_id) AS trucks_busy
    FROM days d LEFT JOIN occupied o ON o.day = d.day
    GROUP BY ALL ORDER BY d.day
"""


def daily_trucks(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> pl.DataFrame:
    """Trucks busy each day: a trip occupies its truck from dispatch for ⌈hours ÷ 24⌉ days.

    Trips without a truck ID (about 2%) can't be counted here.
    """
    return _frame(con.execute(_DAILY, {"start": start, "end": end}))


def _percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    pos = p * (len(ordered) - 1)
    lo = math.floor(pos)
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def capacity_plan(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> dict:
    """Trucks needed by service level, plus the evidence on whether peaks are predictable."""
    daily = daily_trucks(con, start, end).with_columns(
        year=pl.col("day").dt.year(), quarter=pl.col("day").dt.quarter()
    )
    busy = daily["trucks_busy"].to_list()
    by_year = (
        daily.group_by("year")
        .agg(
            mean=pl.col("trucks_busy").mean(),
            p95=pl.col("trucks_busy").quantile(0.95, "linear"),
            max=pl.col("trucks_busy").max(),
        )
        .sort("year")
    )
    last = daily["year"].max()
    by_quarter = daily.group_by("quarter").agg(
        earlier=pl.col("trucks_busy").filter(pl.col("year") < last).mean(),
        latest=pl.col("trucks_busy").filter(pl.col("year") == last).mean(),
    )
    lag1 = daily.select(pl.corr("trucks_busy", pl.col("trucks_busy").shift(1))).item()
    in_use, owned = con.execute(
        "SELECT (SELECT count(DISTINCT truck_id) FROM trips WHERE truck_id IS NOT NULL), "
        "(SELECT count(*) FROM trucks)"
    ).fetchone()
    return {
        "daily": daily.select("day", "trucks_busy"),
        "by_year": by_year,
        "mean": sum(busy) / len(busy),
        "p95": _percentile(busy, 0.95),
        "p99": _percentile(busy, 0.99),
        "max": max(busy),
        "days": len(busy),
        "trucks_in_use": in_use,
        "trucks_owned": owned,
        "lag1_autocorrelation": lag1,
        "quarter_persistence": by_quarter.select(pl.corr("earlier", "latest")).item(),
        "yearly_mean_range": (by_year["mean"].min(), by_year["mean"].max()),
    }


# ------------------------------------------------------------------ network

MATRIX_TIERS = 3
# 3×3 lane matrix: (volume tier, margin tier) → direction. Tiers: 1 = low, 2 = mid, 3 = high.
MATRIX_ACTIONS = {
    (3, 3): "protect",
    (3, 2): "maintain",
    (3, 1): "reprice",
    (2, 3): "grow",
    (2, 2): "maintain",
    (2, 1): "review_price",
    (1, 3): "growth_opportunity",
    (1, 2): "monitor",
    (1, 1): "review_low",
}

# Most urgent first: where a decision on price or the lane itself is due.
ACTION_PRIORITY = (
    "reprice",
    "review_low",
    "review_price",
    "grow",
    "growth_opportunity",
    "protect",
    "maintain",
    "monitor",
)


def _thirds(values: pl.Series) -> pl.Series:
    """Tier 1/2/3 by rank: the lowest third, middle third, highest third."""
    n = len(values)
    ranks = values.rank("ordinal")
    return ((ranks - 1) * MATRIX_TIERS // n + 1).cast(pl.Int64)


def lane_matrix(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> pl.DataFrame:
    """Per lane: trips, revenue, margin (and its gap to all lanes), the 3×3 tiers, the action."""
    margins = (
        kpi(con, start, end, by="route")
        .filter(~pl.col("group").is_in([FLEET, UNATTRIBUTED]))
        .select(
            lane="group",
            revenue="revenue",
            contribution="contribution",
            margin_pct="contribution_margin_pct",
        )
    )
    trips = _frame(
        con.execute(
            "SELECT lane, count(*) AS trips FROM trip_economics "
            "WHERE dispatch_date BETWEEN $start AND $end GROUP BY ALL",
            {"start": start, "end": end},
        )
    )
    df = margins.join(trips, on="lane")
    overall = 100 * df["contribution"].sum() / df["revenue"].sum()
    df = df.with_columns(
        volume_tier=_thirds(df["trips"]),
        margin_tier=_thirds(df["margin_pct"]),
        margin_gap_pts=pl.col("margin_pct") - overall,  # vs the margin of all lanes together
    )
    return df.with_columns(
        action=pl.struct("volume_tier", "margin_tier").map_elements(
            lambda r: MATRIX_ACTIONS[(r["volume_tier"], r["margin_tier"])], return_dtype=pl.Utf8
        )
    ).sort("lane")


def network_balance(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> dict:
    """Loads out vs loads in per city; total inbound surplus; persistence of each city's net."""
    sql = """
        WITH lanes AS (
            SELECT r.origin_city, r.destination_city, year(te.dispatch_date) AS yr
            FROM trip_economics te JOIN routes r ON r.route_id = te.route_id
            WHERE te.dispatch_date BETWEEN $start AND $end
        ),
        flows AS (
            SELECT origin_city AS city, yr, 1 AS out_n, 0 AS in_n FROM lanes
            UNION ALL SELECT destination_city, yr, 0, 1 FROM lanes
        )
        SELECT city, yr, sum(out_n) AS loads_out, sum(in_n) AS loads_in FROM flows GROUP BY ALL
    """
    by_year = _frame(con.execute(sql, {"start": start, "end": end}))
    cities = by_year.group_by("city").agg(pl.col("loads_out").sum(), pl.col("loads_in").sum())
    cities = (
        cities.with_columns(net=pl.col("loads_out") - pl.col("loads_in"))
        .with_columns(
            imbalance_pct=100
            * pl.col("net").abs()
            / ((pl.col("loads_out") + pl.col("loads_in")) / 2)
        )
        .sort("imbalance_pct", descending=True)
    )
    last = by_year["yr"].max()
    nets = (
        by_year.with_columns(net=pl.col("loads_out") - pl.col("loads_in"))
        .group_by("city")
        .agg(
            earlier=pl.col("net").filter(pl.col("yr") < last).sum(),
            latest=pl.col("net").filter(pl.col("yr") == last).sum(),
        )
    )
    total_loads = int(cities["loads_out"].sum())
    surplus = int(cities.select((pl.col("loads_in") - pl.col("loads_out")).clip(0).sum()).item())
    return {
        "cities": cities,
        "total_loads": total_loads,
        "inbound_surplus_loads": surplus,
        "inbound_surplus_pct": 100 * surplus / total_loads,
        "cities_over_20pct": int((cities["imbalance_pct"] > 20).sum()),
        "persistence": nets.select(pl.corr("earlier", "latest")).item(),
    }


def repositioning(con: duckdb.DuckDBPyConnection, start: dt.date, end: dt.date) -> dict:
    """How often a truck's next trip starts in a different city from where the last one ended,
    against the share expected if next trips were assigned at random (no trip chaining).

    Counted only: no distances (4 lane cities have no coordinates in the data).
    """
    sql = """
        WITH seq AS (
            SELECT te.truck_id, year(te.dispatch_date) AS yr, r.origin_city,
                   lag(r.destination_city) OVER (
                       PARTITION BY te.truck_id ORDER BY te.dispatch_date, te.trip_id
                   ) AS previous_end
            FROM trip_economics te JOIN routes r ON r.route_id = te.route_id
            WHERE te.truck_id IS NOT NULL AND te.dispatch_date BETWEEN $start AND $end
        )
        SELECT yr, previous_end AS city, count(*) AS transitions,
               count(*) FILTER (WHERE origin_city <> previous_end) AS moved
        FROM seq WHERE previous_end IS NOT NULL GROUP BY ALL
    """
    # Benchmark: the share that would need a move if each next trip were picked at random
    # (origin independent of where the truck stands) = 1 − Σ P(start city) × P(end city).
    random_sql = """
        WITH x AS (
            SELECT r.origin_city AS o, r.destination_city AS d
            FROM trip_economics te JOIN routes r ON r.route_id = te.route_id
            WHERE te.truck_id IS NOT NULL AND te.dispatch_date BETWEEN $start AND $end
        ),
        po AS (SELECT o AS city, count(*) / sum(count(*)) OVER () AS p FROM x GROUP BY o),
        pd AS (SELECT d AS city, count(*) / sum(count(*)) OVER () AS p FROM x GROUP BY d)
        SELECT 100 * (1 - coalesce(sum(po.p * pd.p), 0)) FROM po JOIN pd USING (city)
    """
    params = {"start": start, "end": end}
    df = _frame(con.execute(sql, params))
    random_pct = con.execute(random_sql, params).fetchone()[0]
    pct = lambda d: 100 * d["moved"].sum() / d["transitions"].sum()  # noqa: E731
    by_year = (
        df.group_by("yr")
        .agg(pl.col("transitions").sum(), pl.col("moved").sum())
        .with_columns(moved_pct=100 * pl.col("moved") / pl.col("transitions"))
        .sort("yr")
    )
    by_city = (
        df.group_by("city")
        .agg(pl.col("transitions").sum(), pl.col("moved").sum())
        .with_columns(moved_pct=100 * pl.col("moved") / pl.col("transitions"))
        .sort("moved_pct", descending=True)
    )
    return {
        "transitions": int(df["transitions"].sum()),
        "moved": int(df["moved"].sum()),
        "moved_pct": pct(df),
        "random_pct": random_pct,
        "by_year": by_year,
        "by_city": by_city,
    }
