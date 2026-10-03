"""Fleet sizing: how many trucks the observed demand needs, and which ones the fleet can do without.

Daily demand: a trip occupies its truck from the dispatch day for ceil(duration / 24 h) days. Busy
trucks are counted per day; a trip with no truck ID counts as one more truck (conservative).
Trucks needed = ceil(percentile of daily demand × (1 + growth) ÷ availability), where availability
is 1 − maintenance downtime ÷ total hours of the trucks in use.
Savings are measured as the maintenance the surplus trucks cost per year. Resale value isn't in
the data and is not counted.
"""

import math
from collections.abc import Iterable

import duckdb
import polars as pl

GROWTH_SCENARIOS = (0.0, 0.05, 0.10, 0.20)

_PERIOD = """
    SELECT min(dispatch_date) AS first_day, max(dispatch_date) AS last_day,
           datediff('day', min(dispatch_date), max(dispatch_date)) + 1 AS days
    FROM trips
"""
_DAILY_DEMAND = """
    WITH occupied AS (
        SELECT trip_id, truck_id,
               unnest(range(dispatch_date,
                            dispatch_date + greatest(ceil(actual_duration_hours / 24), 1)::INT
                                * INTERVAL 1 DAY,
                            INTERVAL 1 DAY))::DATE AS day
        FROM trips
    ),
    period AS (
        SELECT unnest(range(min(dispatch_date), max(dispatch_date) + INTERVAL 1 DAY,
                            INTERVAL 1 DAY))::DATE AS day
        FROM trips
    )
    SELECT p.day,
           count(DISTINCT o.truck_id) + count(o.trip_id) FILTER (WHERE o.truck_id IS NULL) AS busy
    FROM period p LEFT JOIN occupied o ON o.day = p.day
    GROUP BY ALL ORDER BY p.day
"""
_TRUCKS_IN_USE = "SELECT count(DISTINCT truck_id) FROM trips WHERE truck_id IS NOT NULL"
_DOWNTIME_IN_USE = """
    SELECT coalesce(sum(downtime_hours), 0) FROM maintenance_records
    WHERE truck_id IN (SELECT truck_id FROM trips WHERE truck_id IS NOT NULL)
"""


def _years(con) -> float:
    days = con.execute(_PERIOD).fetchone()[2]
    return days / 365.25


def daily_demand(con: duckdb.DuckDBPyConnection) -> list[int]:
    """Trucks busy on each day of the period, idle days included (as 0)."""
    return [busy for _, busy in con.execute(_DAILY_DEMAND).fetchall()]


def availability(con: duckdb.DuckDBPyConnection) -> float:
    """Share of time the trucks in use were not down for maintenance."""
    days = con.execute(_PERIOD).fetchone()[2]
    trucks = con.execute(_TRUCKS_IN_USE).fetchone()[0]
    downtime = con.execute(_DOWNTIME_IN_USE).fetchone()[0]
    return 1 - downtime / (trucks * days * 24)


def trucks_needed(design_demand: float, availability: float) -> int:
    return math.ceil(design_demand / availability - 1e-9)


def _percentile(values: list[int], p: float) -> float:
    """Linear-interpolation percentile (same method as DuckDB's quantile_cont)."""
    ordered = sorted(values)
    position = p * (len(ordered) - 1)
    low = math.floor(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def fleet_plan(
    con: duckdb.DuckDBPyConnection,
    growths: Iterable[float] = GROWTH_SCENARIOS,
    percentile: float = 0.99,
) -> pl.DataFrame:
    """Trucks needed per growth scenario, compared with the fleet and the trucks in use."""
    base = _percentile(daily_demand(con), percentile)
    avail = availability(con)
    fleet_size = con.execute("SELECT count(*) FROM trucks").fetchone()[0]
    in_use = con.execute(_TRUCKS_IN_USE).fetchone()[0]
    rows = []
    for g in growths:
        design = base * (1 + g)
        needed = trucks_needed(design, avail)
        rows.append(
            {
                "growth_pct": 100 * g,
                "design_demand": design,
                "availability": avail,
                "trucks_needed": needed,
                "fleet_size": fleet_size,
                "trucks_in_use": in_use,
                "surplus": fleet_size - needed,
            }
        )
    return pl.DataFrame(rows)


def disposal_tiers(con: duckdb.DuckDBPyConnection, growth: float = 0.0) -> pl.DataFrame:
    """Which trucks to give up, in order, with the maintenance each tier costs per year.

    If the scenario needs more trucks than are in use, the shortfall is first returned to service
    from the Maintenance trucks, then from the Inactive ones (column `return_to_service`).
    Tier 1: Inactive trucks never used. Tier 2: Maintenance-status trucks never used. Within a
    tier the most expensive to maintain go first; both savings are measured.
    Tier 3: trucks in use beyond the need, lowest mileage first; an upper bound, since the
    remaining trucks take over their trips.
    """
    years = _years(con)
    plan = fleet_plan(con, growths=(growth,))
    needed, in_use = plan["trucks_needed"][0], plan["trucks_in_use"][0]
    shortfall = max(0, needed - in_use)
    rows = []
    for tier, status in ((2, "Maintenance"), (1, "Inactive")):  # Maintenance trucks return first
        costs = [
            c
            for (c,) in con.execute(
                "SELECT maintenance_cost FROM truck_economics WHERE trips = 0 AND status = ? "
                "ORDER BY maintenance_cost DESC",
                [status],
            ).fetchall()
        ]
        returned = min(shortfall, len(costs))
        shortfall -= returned
        disposed = costs[: len(costs) - returned]
        rows.append(
            {
                "tier": tier,
                "status": status,
                "trucks": len(disposed),
                "return_to_service": returned,
                "maintenance_per_year": sum(disposed) / years,
                "saving_type": "measured",
            }
        )
    excess = max(0, in_use - needed)
    cost = con.execute(
        "SELECT coalesce(sum(maintenance_cost), 0) FROM (SELECT maintenance_cost FROM "
        "truck_economics WHERE trips > 0 ORDER BY miles LIMIT ?)",
        [excess],
    ).fetchone()[0]
    rows.append(
        {
            "tier": 3,
            "status": "Active (lowest mileage)",
            "trucks": excess,
            "return_to_service": 0,
            "maintenance_per_year": cost / years,
            "saving_type": "upper bound",
        }
    )
    return pl.DataFrame(rows).sort("tier")


def cross_check(con: duckdb.DuckDBPyConnection) -> dict:
    """Independent views of the same question, to compare with trucks_needed."""
    demand = daily_demand(con)
    monthly = con.execute(
        "SELECT max(n) FROM (SELECT month, count(DISTINCT truck_id) n "
        "FROM truck_utilization_metrics GROUP BY 1)"
    ).fetchone()[0]
    needed = fleet_plan(con, growths=(0.0,))["trucks_needed"][0]
    avail = availability(con)
    return {
        "busiest_day_trucks": max(demand),
        "max_trucks_active_in_a_month": monthly,
        "days": len(demand),
        "days_above_need": sum(1 for d in demand if d / avail > needed),
    }
