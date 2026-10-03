"""The KPI catalog and kpi(): one definition per number, ratios always computed as sums ÷ sums.

kpi() aggregates the base views (see views.py) into sums per group, then derives every KPI from
those sums. Costs that can't be tied to a trip (fuel bought in a month with no trips; maintenance
of a truck that ran no trip that month) go to the "Unattributed" row, so groups always add up to
the fleet total. The date filter applies to the trip's dispatch date; unattributed costs use their
own date.
"""

import datetime as dt
from collections.abc import Callable
from dataclasses import dataclass

import duckdb
import polars as pl

FLEET = "Fleet total"
UNATTRIBUTED = "Unattributed"

# by= option → grouping column. location_city exists only for delivery events.
DIMENSIONS = {
    "month": "strftime(month, '%Y-%m')",
    "route": "lane",
    "customer": "customer_id",
    "customer_type": "customer_type",
    "truck": "truck_id",
    "driver": "driver_id",
    "location_city": "location_city",
}
ASSET_DIMENSIONS = {None, "month", "truck"}  # utilization and downtime exist per truck-month


@dataclass(frozen=True)
class Kpi:
    name: str
    area: str  # SCOR area
    unit: str
    formula: dict[str, str]  # language → human-readable formula
    compute: Callable[[dict], float | None]


def _div(a, b, scale: float = 1.0):
    return None if a is None or not b else scale * a / b


def _add(*xs):
    present = [x for x in xs if x is not None]
    return sum(present) if present else None


def _cost(s):
    return _add(s.get("fuel_cost"), s.get("maintenance_cost"), s.get("safety_cost"))


def _contribution(s):
    return None if s.get("revenue") is None else s["revenue"] - (_cost(s) or 0)


CATALOG: list[Kpi] = [
    Kpi(
        "revenue",
        "Cost",
        "USD",
        {
            "en": "Σ linehaul + fuel surcharge + accessorials",
            "vi": "Σ cước + phụ phí nhiên liệu + phụ phí khác",
        },
        lambda s: s.get("revenue"),
    ),
    Kpi(
        "measured_cost",
        "Cost",
        "USD",
        {
            "en": "Σ fuel + maintenance + incident cost (driver pay not in the data)",
            "vi": "Σ nhiên liệu + bảo dưỡng + sự cố (dữ liệu không có lương tài xế)",
        },
        _cost,
    ),
    Kpi(
        "cost_per_mile",
        "Cost",
        "USD/mile",
        {"en": "measured_cost ÷ Σ miles", "vi": "measured_cost ÷ Σ dặm"},
        lambda s: _div(_cost(s), s.get("miles")),
    ),
    Kpi(
        "fuel_cost_per_mile",
        "Cost",
        "USD/mile",
        {"en": "Σ fuel cost ÷ Σ miles", "vi": "Σ chi phí nhiên liệu ÷ Σ dặm"},
        lambda s: _div(s.get("fuel_cost"), s.get("miles")),
    ),
    Kpi(
        "maintenance_cost_per_mile",
        "Cost",
        "USD/mile",
        {"en": "Σ maintenance cost ÷ Σ miles", "vi": "Σ chi phí bảo dưỡng ÷ Σ dặm"},
        lambda s: _div(s.get("maintenance_cost"), s.get("miles")),
    ),
    Kpi(
        "safety_cost_per_mile",
        "Cost",
        "USD/mile",
        {"en": "Σ incident claims ÷ Σ miles", "vi": "Σ bồi thường sự cố ÷ Σ dặm"},
        lambda s: _div(s.get("safety_cost"), s.get("miles")),
    ),
    Kpi(
        "revenue_per_mile",
        "Cost",
        "USD/mile",
        {"en": "revenue ÷ Σ miles", "vi": "revenue ÷ Σ dặm"},
        lambda s: _div(s.get("revenue"), s.get("miles")),
    ),
    Kpi(
        "contribution",
        "Cost",
        "USD",
        {
            "en": "revenue − measured_cost (before driver pay)",
            "vi": "revenue − measured_cost (trước lương tài xế)",
        },
        _contribution,
    ),
    Kpi(
        "contribution_margin_pct",
        "Cost",
        "%",
        {"en": "contribution ÷ revenue", "vi": "contribution ÷ revenue"},
        lambda s: _div(_contribution(s), s.get("revenue"), 100),
    ),
    Kpi(
        "out_of_route_pct",
        "Cost",
        "%",
        {
            "en": "Σ (actual miles − lane's typical miles) ÷ Σ typical miles",
            "vi": "Σ (dặm thực tế − dặm chuẩn của tuyến) ÷ Σ dặm chuẩn",
        },
        lambda s: _div(
            _add(s.get("miles"), -(s.get("typical_miles") or 0))
            if s.get("miles") is not None
            else None,
            s.get("typical_miles"),
            100,
        ),
    ),
    Kpi(
        "mpg",
        "Fuel",
        "miles/gallon",
        {"en": "Σ miles ÷ Σ gallons burned", "vi": "Σ dặm ÷ Σ gallon tiêu thụ"},
        lambda s: _div(s.get("miles"), s.get("gallons_burned")),
    ),
    Kpi(
        "fuel_purchased_to_burned",
        "Fuel",
        "ratio",
        {
            "en": "Σ gallons purchased ÷ Σ gallons burned (fuel-card control)",
            "vi": "Σ gallon mua ÷ Σ gallon tiêu thụ (kiểm soát thẻ nhiên liệu)",
        },
        lambda s: _div(s.get("gallons_purchased"), s.get("gallons_burned")),
    ),
    Kpi(
        "on_time_pct",
        "Reliability",
        "%",
        {
            "en": "deliveries with |actual − appointment| ≤ window ÷ deliveries "
            "(window 120 min = on_time_flag)",
            "vi": "lần giao có |thực tế − giờ hẹn| ≤ cửa sổ ÷ số lần giao "
            "(cửa sổ 120 phút = on_time_flag)",
        },
        lambda s: _div(s.get("on_time"), s.get("deliveries"), 100),
    ),
    Kpi(
        "not_late_pct",
        "Reliability",
        "%",
        {
            "en": "deliveries with actual ≤ appointment ÷ deliveries",
            "vi": "lần giao có thực tế ≤ giờ hẹn ÷ số lần giao",
        },
        lambda s: _div(s.get("not_late"), s.get("deliveries"), 100),
    ),
    Kpi(
        "avg_detention_min",
        "Reliability",
        "minutes",
        {
            "en": "Σ detention minutes ÷ pickups and deliveries",
            "vi": "Σ phút chờ ÷ số lần lấy và giao",
        },
        lambda s: _div(s.get("detention_min"), s.get("events")),
    ),
    Kpi(
        "detention_hours",
        "Reliability",
        "hours",
        {"en": "Σ detention minutes ÷ 60", "vi": "Σ phút chờ ÷ 60"},
        lambda s: _div(s.get("detention_min"), 60),
    ),
    Kpi(
        "miles_per_truck_month",
        "Assets",
        "miles",
        {
            "en": "Σ miles ÷ truck-months with at least one trip",
            "vi": "Σ dặm ÷ số tháng-xe có ít nhất một chuyến",
        },
        lambda s: _div(s.get("miles"), s.get("truck_months")),
    ),
    Kpi(
        "utilization",
        "Assets",
        "%",
        {
            "en": "mean utilization_rate (compare trucks only; can exceed 100%)",
            "vi": "trung bình utilization_rate (chỉ để so sánh xe; có thể vượt 100%)",
        },
        lambda s: _div(s.get("utilization"), 1, 100),
    ),
    Kpi(
        "downtime_hours",
        "Assets",
        "hours",
        {"en": "Σ maintenance downtime hours", "vi": "Σ giờ dừng do bảo dưỡng"},
        lambda s: s.get("downtime_hours"),
    ),
    Kpi(
        "incidents_per_million_miles",
        "Safety",
        "per 1M miles",
        {"en": "incidents ÷ Σ miles × 1,000,000", "vi": "số sự cố ÷ Σ dặm × 1.000.000"},
        lambda s: _div(s.get("incidents"), s.get("miles"), 1e6),
    ),
    Kpi(
        "preventable_pct",
        "Safety",
        "%",
        {"en": "preventable incidents ÷ incidents", "vi": "sự cố phòng tránh được ÷ số sự cố"},
        lambda s: _div(s.get("preventable"), s.get("incidents"), 100),
    ),
]

_TRIP_SUMS = """
    SELECT {key} AS grp, count(*) AS trips, sum(miles) AS miles,
           sum(typical_miles) AS typical_miles,
           sum(gallons_burned) AS gallons_burned, sum(gallons_purchased) AS gallons_purchased,
           sum(revenue) AS revenue, sum(fuel_cost) AS fuel_cost,
           sum(maintenance_cost) AS maintenance_cost, sum(safety_cost) AS safety_cost,
           sum(incidents) AS incidents, sum(preventable_incidents) AS preventable,
           count(DISTINCT (truck_id, month)) FILTER (WHERE truck_id IS NOT NULL) AS truck_months
    FROM trip_economics WHERE dispatch_date BETWEEN $start AND $end GROUP BY ALL
"""
_SERVICE_SUMS = """
    SELECT {key} AS grp,
           count(*) FILTER (WHERE event_type = 'Delivery') AS deliveries,
           count(*) FILTER (WHERE event_type = 'Delivery' AND abs(deviation_min) <= $window)
               AS on_time,
           count(*) FILTER (WHERE event_type = 'Delivery' AND deviation_min <= 0) AS not_late,
           count(*) AS events, sum(detention_minutes) AS detention_min
    FROM delivery_performance WHERE dispatch_date BETWEEN $start AND $end GROUP BY ALL
"""
_UTILIZATION = """
    SELECT {key} AS grp, avg(utilization_rate) AS utilization FROM truck_utilization_metrics
    WHERE month BETWEEN date_trunc('month', $start::DATE) AND $end GROUP BY ALL
"""
_DOWNTIME = """
    SELECT {key} AS grp, sum(downtime_hours) AS downtime_hours
    FROM (SELECT *, date_trunc('month', maintenance_date)::DATE AS month FROM maintenance_records)
    WHERE maintenance_date BETWEEN $start AND $end GROUP BY ALL
"""
_UNATTRIBUTED_FUEL = """
    SELECT coalesce(sum(total_cost), 0) FROM fuel_purchases
    WHERE purchase_date::DATE BETWEEN $start AND $end
      AND date_trunc('month', purchase_date)::DATE
          NOT IN (SELECT DISTINCT month FROM trip_economics)
"""
_UNATTRIBUTED_MAINTENANCE = """
    SELECT coalesce(sum(m.total_cost), 0) FROM maintenance_records m
    WHERE m.maintenance_date BETWEEN $start AND $end
      AND NOT EXISTS (SELECT 1 FROM trip_economics t WHERE t.truck_id = m.truck_id
                      AND t.month = date_trunc('month', m.maintenance_date)::DATE)
"""


def kpi(
    con: duckdb.DuckDBPyConnection,
    start: dt.date,
    end: dt.date,
    by: str | None = None,
    on_time_window_min: float = 120,
) -> pl.DataFrame:
    """KPIs per group (one row each) plus the fleet total. See CATALOG for the definitions."""
    if by is not None and by not in DIMENSIONS:
        raise ValueError(f"by must be one of {sorted(DIMENSIONS)} or None, not {by!r}")
    params = {"start": start, "end": end}
    groups: dict[str, dict] = {}
    if by is not None:
        _collect(con, groups, by, params, on_time_window_min)
        extra = groups.setdefault(UNATTRIBUTED, {})
        _add_unattributed(con, extra, params)
    fleet: dict[str, dict] = {}
    _collect(con, fleet, None, params, on_time_window_min)
    _add_unattributed(con, fleet[FLEET], params)

    names = sorted(g for g in groups if g != UNATTRIBUTED)
    if UNATTRIBUTED in groups:
        names.append(UNATTRIBUTED)
    rows = [_row(name, groups[name]) for name in names] + [_row(FLEET, fleet[FLEET])]
    schema = {"group": pl.Utf8} | {k.name: pl.Float64 for k in CATALOG}
    return pl.DataFrame(rows, schema=schema, orient="row")


def _collect(con, out: dict, by: str | None, params: dict, window: float) -> None:
    if by is None:
        key = f"'{FLEET}'"
    else:
        key = f"coalesce(CAST({DIMENSIONS[by]} AS VARCHAR), '{UNATTRIBUTED}')"
    queries = [(_SERVICE_SUMS, params | {"window": window})]
    if by != "location_city":
        queries.insert(0, (_TRIP_SUMS, params))
    if by in ASSET_DIMENSIONS:
        queries += [(_UTILIZATION, params), (_DOWNTIME, params)]
    for sql, p in queries:
        cur = con.execute(sql.format(key=key), p)
        columns = [d[0] for d in cur.description]
        for values in cur.fetchall():
            record = dict(zip(columns, values, strict=True))
            out.setdefault(record.pop("grp"), {}).update(record)


def _add_unattributed(con, sums: dict, params: dict) -> None:
    fuel = con.execute(_UNATTRIBUTED_FUEL, params).fetchone()[0]
    maintenance = con.execute(_UNATTRIBUTED_MAINTENANCE, params).fetchone()[0]
    sums["fuel_cost"] = (sums.get("fuel_cost") or 0) + fuel
    sums["maintenance_cost"] = (sums.get("maintenance_cost") or 0) + maintenance
    sums.setdefault("revenue", 0)
    sums.setdefault("safety_cost", 0)


def _row(name: str, sums: dict) -> list:
    return [name] + [_as_float(k.compute(sums)) for k in CATALOG]


def _as_float(x):
    return None if x is None else float(x)
