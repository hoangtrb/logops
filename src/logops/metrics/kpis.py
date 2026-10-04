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
    "load_type": "load_type",
    "origin_state": "origin_state",
    "destination_state": "destination_state",
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
            "en": "Revenue = linehaul + fuel surcharge + accessorial charges",
            "vi": "Doanh thu = cước vận chuyển + phụ phí nhiên liệu + phụ phí khác",
        },
        lambda s: s.get("revenue"),
    ),
    Kpi(
        "measured_cost",
        "Cost",
        "USD",
        {
            "en": "Measured operating cost = fuel + maintenance + incident claims (driver "
            "pay is not in the data)",
            "vi": "Chi phí vận hành đo được = nhiên liệu + bảo dưỡng + bồi thường sự cố "
            "(dữ liệu không có lương tài xế)",
        },
        _cost,
    ),
    Kpi(
        "cost_per_mile",
        "Cost",
        "USD/mile",
        {
            "en": "Operating cost per mile = measured operating cost ÷ total miles",
            "vi": "Chi phí vận hành mỗi dặm = chi phí vận hành đo được ÷ tổng số dặm",
        },
        lambda s: _div(_cost(s), s.get("miles")),
    ),
    Kpi(
        "fuel_cost_per_mile",
        "Cost",
        "USD/mile",
        {
            "en": "Fuel cost per mile = fuel cost ÷ total miles",
            "vi": "Chi phí nhiên liệu mỗi dặm = chi phí nhiên liệu ÷ tổng số dặm",
        },
        lambda s: _div(s.get("fuel_cost"), s.get("miles")),
    ),
    Kpi(
        "maintenance_cost_per_mile",
        "Cost",
        "USD/mile",
        {
            "en": "Maintenance cost per mile = maintenance cost ÷ total miles",
            "vi": "Chi phí bảo dưỡng mỗi dặm = chi phí bảo dưỡng ÷ tổng số dặm",
        },
        lambda s: _div(s.get("maintenance_cost"), s.get("miles")),
    ),
    Kpi(
        "safety_cost_per_mile",
        "Cost",
        "USD/mile",
        {
            "en": "Incident cost per mile = incident claims ÷ total miles",
            "vi": "Chi phí sự cố mỗi dặm = bồi thường sự cố ÷ tổng số dặm",
        },
        lambda s: _div(s.get("safety_cost"), s.get("miles")),
    ),
    Kpi(
        "revenue_per_mile",
        "Cost",
        "USD/mile",
        {
            "en": "Revenue per mile = revenue ÷ total miles",
            "vi": "Doanh thu mỗi dặm = doanh thu ÷ tổng số dặm",
        },
        lambda s: _div(s.get("revenue"), s.get("miles")),
    ),
    Kpi(
        "contribution",
        "Cost",
        "USD",
        {
            "en": "Contribution profit = revenue − measured operating cost (before driver pay)",
            "vi": "Lợi nhuận đóng góp = doanh thu − chi phí vận hành đo được (chưa trừ "
            "lương tài xế)",
        },
        _contribution,
    ),
    Kpi(
        "contribution_margin_pct",
        "Cost",
        "%",
        {
            "en": "Contribution margin = contribution profit ÷ revenue",
            "vi": "Biên đóng góp = lợi nhuận đóng góp ÷ doanh thu",
        },
        lambda s: _div(_contribution(s), s.get("revenue"), 100),
    ),
    Kpi(
        "out_of_route_pct",
        "Cost",
        "%",
        {
            "en": "Out-of-route miles = (actual miles − the lane's standard miles) ÷ "
            "standard miles",
            "vi": "Tỷ lệ chạy vượt quãng chuẩn = (số dặm thực tế − số dặm chuẩn của "
            "tuyến) ÷ số dặm chuẩn",
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
        {
            "en": "Fuel economy = total miles ÷ gallons burned",
            "vi": "Hiệu suất nhiên liệu = tổng số dặm ÷ số gallon tiêu thụ",
        },
        lambda s: _div(s.get("miles"), s.get("gallons_burned")),
    ),
    Kpi(
        "fuel_purchased_to_burned",
        "Fuel",
        "ratio",
        {
            "en": "Fuel bought vs burned = gallons bought ÷ gallons burned on trips "
            "(fuel-card control)",
            "vi": "Tỷ lệ nhiên liệu mua / tiêu thụ = số gallon mua ÷ số gallon tiêu thụ "
            "theo chuyến (kiểm soát thẻ nhiên liệu)",
        },
        lambda s: _div(s.get("gallons_purchased"), s.get("gallons_burned")),
    ),
    Kpi(
        "on_time_pct",
        "Reliability",
        "%",
        {
            "en": "On-time delivery (OTD) = deliveries within ±2 hours of the appointment "
            "÷ all deliveries",
            "vi": "Giao hàng đúng hẹn (OTD) = số lần giao trong ±2 giờ so với giờ hẹn ÷ "
            "tổng số lần giao",
        },
        lambda s: _div(s.get("on_time"), s.get("deliveries"), 100),
    ),
    Kpi(
        "not_late_pct",
        "Reliability",
        "%",
        {
            "en": "Not late = deliveries at or before the appointment ÷ all deliveries",
            "vi": "Giao không trễ hẹn = số lần giao đến trước hoặc đúng giờ hẹn ÷ tổng số lần giao",
        },
        lambda s: _div(s.get("not_late"), s.get("deliveries"), 100),
    ),
    Kpi(
        "avg_detention_min",
        "Reliability",
        "minutes",
        {
            "en": "Average detention = total waiting minutes ÷ pickups and deliveries",
            "vi": "Thời gian chờ bình quân = tổng số phút chờ ÷ số lần lấy và giao hàng",
        },
        lambda s: _div(s.get("detention_min"), s.get("events")),
    ),
    Kpi(
        "detention_hours",
        "Reliability",
        "hours",
        {
            "en": "Total detention = total waiting minutes ÷ 60",
            "vi": "Tổng thời gian chờ = tổng số phút chờ ÷ 60",
        },
        lambda s: _div(s.get("detention_min"), 60),
    ),
    Kpi(
        "miles_per_truck_month",
        "Assets",
        "miles",
        {
            "en": "Miles per truck per month = total miles ÷ truck-months with at least one trip",
            "vi": "Quãng đường mỗi xe mỗi tháng = tổng số dặm ÷ số tháng-xe có ít nhất một chuyến",
        },
        lambda s: _div(s.get("miles"), s.get("truck_months")),
    ),
    Kpi(
        "utilization",
        "Assets",
        "%",
        {
            "en": "Reported utilization = average of the monthly utilization each truck "
            "reports (the data doesn't define it and it can exceed 100%; use only "
            "to compare trucks)",
            "vi": "Hệ số sử dụng xe theo báo cáo = trung bình hệ số sử dụng hằng tháng "
            "của từng xe (dữ liệu không định nghĩa và có thể vượt 100%; chỉ dùng để "
            "so sánh các xe)",
        },
        lambda s: _div(s.get("utilization"), 1, 100),
    ),
    Kpi(
        "downtime_hours",
        "Assets",
        "hours",
        {
            "en": "Maintenance downtime = total hours trucks were out of service for "
            "maintenance or repair",
            "vi": "Thời gian dừng xe bảo dưỡng = tổng số giờ xe ngừng hoạt động để bảo "
            "dưỡng, sửa chữa",
        },
        lambda s: s.get("downtime_hours"),
    ),
    Kpi(
        "incidents_per_million_miles",
        "Safety",
        "per 1M miles",
        {
            "en": "Incident rate = incidents ÷ total miles × 1,000,000",
            "vi": "Tần suất sự cố = số sự cố ÷ tổng số dặm × 1.000.000",
        },
        lambda s: _div(s.get("incidents"), s.get("miles"), 1e6),
    ),
    Kpi(
        "preventable_pct",
        "Safety",
        "%",
        {
            "en": "Preventable incidents = preventable incidents ÷ all incidents",
            "vi": "Tỷ lệ sự cố phòng tránh được = số sự cố phòng tránh được ÷ tổng số sự cố",
        },
        lambda s: _div(s.get("preventable"), s.get("incidents"), 100),
    ),
]

TITLES = {  # display names, same order as CATALOG
    "revenue": {"en": "Revenue", "vi": "Doanh thu"},
    "measured_cost": {"en": "Measured operating cost", "vi": "Chi phí vận hành đo được"},
    "cost_per_mile": {"en": "Operating cost per mile", "vi": "Chi phí vận hành mỗi dặm"},
    "fuel_cost_per_mile": {"en": "Fuel cost per mile", "vi": "Chi phí nhiên liệu mỗi dặm"},
    "maintenance_cost_per_mile": {
        "en": "Maintenance cost per mile",
        "vi": "Chi phí bảo dưỡng mỗi dặm",
    },
    "safety_cost_per_mile": {"en": "Incident cost per mile", "vi": "Chi phí sự cố mỗi dặm"},
    "revenue_per_mile": {"en": "Revenue per mile", "vi": "Doanh thu mỗi dặm"},
    "contribution": {"en": "Contribution profit", "vi": "Lợi nhuận đóng góp"},
    "contribution_margin_pct": {"en": "Contribution margin", "vi": "Biên đóng góp"},
    "out_of_route_pct": {"en": "Out-of-route miles", "vi": "Tỷ lệ chạy vượt quãng chuẩn"},
    "mpg": {"en": "Fuel economy", "vi": "Hiệu suất nhiên liệu"},
    "fuel_purchased_to_burned": {
        "en": "Fuel bought vs burned",
        "vi": "Tỷ lệ nhiên liệu mua / tiêu thụ",
    },
    "on_time_pct": {"en": "On-time delivery (OTD)", "vi": "Giao hàng đúng hẹn (OTD)"},
    "not_late_pct": {"en": "Not late", "vi": "Giao không trễ hẹn"},
    "avg_detention_min": {"en": "Average detention", "vi": "Thời gian chờ bình quân"},
    "detention_hours": {"en": "Total detention", "vi": "Tổng thời gian chờ"},
    "miles_per_truck_month": {
        "en": "Miles per truck per month",
        "vi": "Quãng đường mỗi xe mỗi tháng",
    },
    "utilization": {"en": "Reported utilization", "vi": "Hệ số sử dụng xe theo báo cáo"},
    "downtime_hours": {"en": "Maintenance downtime", "vi": "Thời gian dừng xe bảo dưỡng"},
    "incidents_per_million_miles": {"en": "Incident rate", "vi": "Tần suất sự cố"},
    "preventable_pct": {"en": "Preventable incidents", "vi": "Tỷ lệ sự cố phòng tránh được"},
}
UNITS = {  # unit labels per language
    "USD": {"en": "USD", "vi": "USD"},
    "USD/mile": {"en": "USD per mile", "vi": "USD/dặm"},
    "%": {"en": "%", "vi": "%"},
    "miles/gallon": {"en": "miles per gallon", "vi": "dặm/gallon"},
    "ratio": {"en": "times", "vi": "lần"},
    "minutes": {"en": "minutes", "vi": "phút"},
    "hours": {"en": "hours", "vi": "giờ"},
    "miles": {"en": "miles", "vi": "dặm"},
    "per 1M miles": {"en": "per million miles", "vi": "lần/triệu dặm"},
}
AREAS = {
    "Cost": {"en": "Cost & profit", "vi": "Chi phí & lợi nhuận"},
    "Fuel": {"en": "Fuel", "vi": "Nhiên liệu"},
    "Reliability": {"en": "Delivery reliability", "vi": "Độ tin cậy giao hàng"},
    "Assets": {"en": "Assets", "vi": "Tài sản (xe)"},
    "Safety": {"en": "Safety", "vi": "An toàn"},
}

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
