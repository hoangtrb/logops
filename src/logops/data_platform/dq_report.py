"""Render docs/02-data-quality-report(.vi).md from the warehouse after the DQ step.

Every number is computed here by SQL and collected once (`collect`), then rendered twice with
two label dictionaries, so both languages always show the same figures. The output has no
timestamps: re-running on the same data produces byte-identical files.
"""

from collections.abc import Iterable
from pathlib import Path

import duckdb

from logops.data_platform.schema import TableSchema

LANGUAGES = ("en", "vi")

# Business baselines for docs/01 §5. (key, SQL, kind); kind decides the formatting.
BASELINES = [
    ("period_start", "SELECT min(dispatch_date) FROM trips", "date"),
    ("period_end", "SELECT max(dispatch_date) FROM trips", "date"),
    ("revenue", "SELECT sum(revenue + fuel_surcharge + accessorial_charges) FROM loads", "usd_m"),
    ("fuel_cost", "SELECT sum(total_cost) FROM fuel_purchases", "usd_m"),
    ("maintenance_cost", "SELECT sum(total_cost) FROM maintenance_records", "usd_m"),
    ("safety_cost", "SELECT sum(claim_amount) FROM safety_incidents", "usd_m"),
    (
        "operating_cost",
        "SELECT (SELECT sum(total_cost) FROM fuel_purchases) "
        "+ (SELECT sum(total_cost) FROM maintenance_records) "
        "+ (SELECT sum(claim_amount) FROM safety_incidents)",
        "usd_m",
    ),
    ("miles", "SELECT sum(actual_distance_miles) FROM trips", "int"),
    (
        "cost_per_mile",
        "SELECT ((SELECT sum(total_cost) FROM fuel_purchases) "
        "+ (SELECT sum(total_cost) FROM maintenance_records) "
        "+ (SELECT sum(claim_amount) FROM safety_incidents)) "
        "/ nullif((SELECT sum(actual_distance_miles) FROM trips), 0)",
        "usd",
    ),
    (
        "fleet_mpg",
        "SELECT sum(actual_distance_miles) / nullif(sum(fuel_gallons_used), 0) FROM trips",
        "num2",
    ),
    (
        "delivery_in_window",
        "SELECT avg(on_time_flag::INT) FROM delivery_events WHERE event_type = 'Delivery'",
        "pct",
    ),
    (
        "pickup_in_window",
        "SELECT avg(on_time_flag::INT) FROM delivery_events WHERE event_type = 'Pickup'",
        "pct",
    ),
    (
        "delivery_not_late",
        "SELECT avg((actual_datetime <= scheduled_datetime)::INT) FROM delivery_events "
        "WHERE event_type = 'Delivery'",
        "pct",
    ),
    ("detention_hours", "SELECT sum(detention_minutes) / 60 FROM delivery_events", "int"),
    ("utilization", "SELECT avg(utilization_rate) FROM truck_utilization_metrics", "pct"),
]

_LATE_MINUTES = "epoch(actual_datetime - scheduled_datetime) / 60"
_ROUTE_ENDPOINT = "CASE WHEN d.event_type = 'Pickup' THEN r.origin_city ELSE r.destination_city END"
_EVENTS_ON_ROUTES = (
    "FROM delivery_events d JOIN loads l USING (load_id) JOIN routes r USING (route_id) "
    "JOIN facilities f ON f.facility_id = d.facility_id"
)

# One-off consistency checks (results shown as %; `dup_rows` is added by `collect`).
CROSS_CHECKS = [
    (
        "driver_monthly_drift",
        "WITH r AS (SELECT t.driver_id, date_trunc('month', t.dispatch_date) AS m, count(*) AS n, "
        "sum(t.actual_distance_miles) AS miles, sum(l.revenue) AS rev "
        "FROM trips t JOIN loads l USING (load_id) WHERE t.driver_id IS NOT NULL GROUP BY ALL) "
        "SELECT avg((r.n IS NULL OR abs(d.trips_completed - r.n) > 0.02 * r.n "
        "OR abs(d.total_miles - r.miles) > 0.02 * r.miles "
        "OR abs(d.total_revenue - r.rev) > 0.02 * r.rev)::INT) "
        "FROM driver_monthly_metrics d LEFT JOIN r ON r.driver_id = d.driver_id AND r.m = d.month",
    ),
    (
        "truck_monthly_drift",
        "WITH r AS (SELECT t.truck_id, date_trunc('month', t.dispatch_date) AS m, count(*) AS n, "
        "sum(t.actual_distance_miles) AS miles, sum(l.revenue) AS rev "
        "FROM trips t JOIN loads l USING (load_id) WHERE t.truck_id IS NOT NULL GROUP BY ALL), "
        "mx AS (SELECT truck_id, date_trunc('month', maintenance_date) AS m, count(*) AS n, "
        "sum(total_cost) AS cost FROM maintenance_records GROUP BY ALL) "
        "SELECT avg((r.n IS NULL OR abs(u.trips_completed - r.n) > 0.02 * r.n "
        "OR abs(u.total_miles - r.miles) > 0.02 * r.miles "
        "OR abs(u.total_revenue - r.rev) > 0.02 * r.rev "
        "OR coalesce(mx.n, 0) <> u.maintenance_events "
        "OR abs(coalesce(mx.cost, 0) - u.maintenance_cost) > 0.02 * greatest(u.maintenance_cost, 1)"
        ")::INT) FROM truck_utilization_metrics u "
        "LEFT JOIN r ON r.truck_id = u.truck_id AND r.m = u.month "
        "LEFT JOIN mx ON mx.truck_id = u.truck_id AND mx.m = u.month",
    ),
    (
        "on_time_flag_is_2h_window",
        f"SELECT avg((on_time_flag = (abs({_LATE_MINUTES}) <= 120))::INT) FROM delivery_events",
    ),
    (
        "early_over_2h_not_on_time",
        f"SELECT avg(({_LATE_MINUTES} < -120)::INT) FROM delivery_events",
    ),
    (
        "event_city_is_route_endpoint",
        f"SELECT avg((d.location_city = {_ROUTE_ENDPOINT})::INT) {_EVENTS_ON_ROUTES}",
    ),
    (
        "facility_city_is_route_endpoint",
        f"SELECT avg((f.city = {_ROUTE_ENDPOINT})::INT) {_EVENTS_ON_ROUTES}",
    ),
]

LABELS = {
    "en": {
        "file": "02-data-quality-report.md",
        "title": "# 02 · Data Quality Report",
        "banner": "> CRISP-DM phase 2 (Data Understanding). Generated by `uv run logops build` "
        "from `data/warehouse.duckdb`; do not edit by hand. · Vietnamese: "
        "[02-data-quality-report.vi.md](02-data-quality-report.vi.md) · "
        "Analysis: [02-data-understanding.md](02-data-understanding.md)",
        "summary": "## 1. Summary",
        "period": "Period covered",
        "tables_rows": "Tables / rows",
        "rules_run": "Rules run / rules with violations",
        "flagged_rows": "Rows with at least one issue (warnings included)",
        "flagged_error_rows": "Rows with at least one error-level issue",
        "not_deleted": "No row was deleted. Every violation is recorded in that row's `dq_issues` "
        "column and summarized in the `dq_findings` table.",
        "baselines": "## 2. Business baselines",
        "baselines_intro": "Inputs for the success criteria in "
        "[01-business-understanding.md](01-business-understanding.md) §5. Operating cost "
        "covers fuel, maintenance and safety claims; driver pay is not in the data.",
        "metric": "Metric",
        "value": "Value",
        "findings": "## 3. Findings",
        "severity": "Severity",
        "rule": "Rule",
        "target": "Table.column",
        "rows": "Rows flagged",
        "share": "% of table",
        "samples": "Sample keys",
        "clean_rules": "Rules that found nothing",
        "rule_defs": "## 4. Rule definitions",
        "cross": "## 5. Cross-checks",
        "check": "Check",
        "result": "Result",
        "nulls": "## 6. Missing values",
        "nulls_intro": "Columns with at least one empty value. All other columns are complete.",
        "column": "Column",
        "empty": "Empty values",
        "to": "to",
    },
    "vi": {
        "file": "02-data-quality-report.vi.md",
        "title": "# 02 · Báo cáo chất lượng dữ liệu",
        "banner": "> CRISP-DM pha 2 (Hiểu dữ liệu). Sinh tự động bằng `uv run logops build` từ "
        "`data/warehouse.duckdb`; không sửa tay. · Bản tiếng Anh: "
        "[02-data-quality-report.md](02-data-quality-report.md) · "
        "Phân tích: [02-data-understanding.vi.md](02-data-understanding.vi.md)",
        "summary": "## 1. Tóm tắt",
        "period": "Giai đoạn dữ liệu",
        "tables_rows": "Số bảng / số dòng",
        "rules_run": "Số quy tắc đã chạy / số quy tắc có vi phạm",
        "flagged_rows": "Số dòng có ít nhất một vấn đề (kể cả cảnh báo)",
        "flagged_error_rows": "Số dòng có ít nhất một lỗi mức error",
        "not_deleted": "Không dòng nào bị xóa. Mọi vi phạm được ghi vào cột `dq_issues` của "
        "dòng đó và tổng hợp trong bảng `dq_findings`.",
        "baselines": "## 2. Số liệu nền kinh doanh",
        "baselines_intro": "Đầu vào cho tiêu chí thành công trong "
        "[01-business-understanding.vi.md](01-business-understanding.vi.md) §5. Chi phí vận hành "
        "gồm nhiên liệu, bảo dưỡng và bồi thường sự cố; dữ liệu không có lương tài xế.",
        "metric": "Chỉ số",
        "value": "Giá trị",
        "findings": "## 3. Phát hiện",
        "severity": "Mức độ",
        "rule": "Quy tắc",
        "target": "Bảng.cột",
        "rows": "Số dòng bị đánh dấu",
        "share": "% của bảng",
        "samples": "Khóa mẫu",
        "clean_rules": "Các quy tắc không phát hiện lỗi",
        "rule_defs": "## 4. Định nghĩa quy tắc",
        "cross": "## 5. Kiểm tra chéo",
        "check": "Kiểm tra",
        "result": "Kết quả",
        "nulls": "## 6. Giá trị thiếu",
        "nulls_intro": "Các cột có ít nhất một giá trị rỗng. Mọi cột khác đều đầy đủ.",
        "column": "Cột",
        "empty": "Số giá trị rỗng",
        "to": "đến",
    },
}

BASELINE_NAMES = {
    "en": {
        "revenue": "Revenue (linehaul + fuel surcharge + accessorials)",
        "operating_cost": "Operating cost (fuel + maintenance + safety claims)",
        "fuel_cost": "Fuel cost",
        "maintenance_cost": "Maintenance cost",
        "safety_cost": "Safety claims",
        "miles": "Miles driven",
        "cost_per_mile": "Operating cost per mile",
        "fleet_mpg": "Fleet MPG (total miles ÷ total gallons)",
        "delivery_in_window": "Deliveries within ±2 h of appointment (`on_time_flag`)",
        "pickup_in_window": "Pickups within ±2 h of appointment (`on_time_flag`)",
        "delivery_not_late": "Deliveries not late (actual ≤ scheduled)",
        "detention_hours": "Detention hours",
        "utilization": "Average truck utilization",
    },
    "vi": {
        "revenue": "Doanh thu (cước + phụ phí nhiên liệu + phụ phí khác)",
        "operating_cost": "Chi phí vận hành (nhiên liệu + bảo dưỡng + bồi thường sự cố)",
        "fuel_cost": "Chi phí nhiên liệu",
        "maintenance_cost": "Chi phí bảo dưỡng",
        "safety_cost": "Bồi thường sự cố",
        "miles": "Số dặm đã chạy",
        "cost_per_mile": "Chi phí vận hành mỗi dặm",
        "fleet_mpg": "MPG đội xe (tổng dặm ÷ tổng gallon)",
        "delivery_in_window": "Giao hàng trong khung ±2 giờ so với lịch hẹn (`on_time_flag`)",
        "pickup_in_window": "Lấy hàng trong khung ±2 giờ so với lịch hẹn (`on_time_flag`)",
        "delivery_not_late": "Giao hàng không trễ (thực tế ≤ lịch hẹn)",
        "detention_hours": "Số giờ chờ (detention)",
        "utilization": "Mức sử dụng xe trung bình",
    },
}

CHECK_NAMES = {
    "en": {
        "dup_rows": "Exact duplicate rows, all tables",
        "driver_monthly_drift": "`driver_monthly_metrics` months differing > 2% from values "
        "recomputed from trips + loads",
        "truck_monthly_drift": "`truck_utilization_metrics` months differing > 2% from trips, "
        "loads and maintenance",
        "on_time_flag_is_2h_window": "Events where `on_time_flag` = "
        "(|actual − scheduled| ≤ 120 min)",
        "early_over_2h_not_on_time": "Events more than 2 h early (counted as *not* on time)",
        "event_city_is_route_endpoint": "Delivery events whose `location_city` is the load's "
        "route origin (pickup) or destination (delivery)",
        "facility_city_is_route_endpoint": "Delivery events whose `facility_id` city is that "
        "route endpoint",
    },
    "vi": {
        "dup_rows": "Dòng trùng tuyệt đối, mọi bảng",
        "driver_monthly_drift": "Tháng trong `driver_monthly_metrics` lệch > 2% so với số tính "
        "lại từ trips + loads",
        "truck_monthly_drift": "Tháng trong `truck_utilization_metrics` lệch > 2% so với trips, "
        "loads và bảo dưỡng",
        "on_time_flag_is_2h_window": "Sự kiện có `on_time_flag` = "
        "(|thực tế − lịch hẹn| ≤ 120 phút)",
        "early_over_2h_not_on_time": "Sự kiện sớm hơn 2 giờ (bị tính là *không* đúng giờ)",
        "event_city_is_route_endpoint": "Sự kiện giao nhận có `location_city` là điểm đầu (lấy "
        "hàng) hoặc điểm cuối (giao hàng) của tuyến",
        "facility_city_is_route_endpoint": "Sự kiện giao nhận có thành phố của `facility_id` là "
        "điểm đầu/cuối tuyến đó",
    },
}

RULE_DEFS = {
    "en": {
        "pk_unique": "Primary key is duplicated or empty.",
        "fk_missing": "Foreign key is empty: the row can't be linked to its parent.",
        "fk_orphan": "Foreign key points to a parent row that doesn't exist.",
        "range": "Value outside its plausible range (e.g. MPG outside 3–12, negative cost, "
        "utilization above 100%).",
        "idle_exceeds_duration": "Idle hours greater than the trip's total duration.",
        "amount_mismatch": "Total differs by more than 1% from its parts (gallons × price; "
        "labor + parts; vehicle + cargo damage).",
        "time_order": "Dates in an impossible order (delivered before picked up; terminated "
        "before hired).",
        "geo_mismatch": "Location inconsistent: city/state pair not found among facilities "
        "and route endpoints, or event city differs from its facility's city.",
    },
    "vi": {
        "pk_unique": "Khóa chính bị trùng hoặc rỗng.",
        "fk_missing": "Khóa ngoại rỗng: dòng không nối được với bảng cha.",
        "fk_orphan": "Khóa ngoại trỏ tới dòng không tồn tại ở bảng cha.",
        "range": "Giá trị ngoài khoảng hợp lý (ví dụ MPG ngoài 3–12, chi phí âm, mức sử dụng "
        "trên 100%).",
        "idle_exceeds_duration": "Số giờ chạy không tải lớn hơn tổng thời gian chuyến.",
        "amount_mismatch": "Tổng lệch hơn 1% so với các thành phần (gallon × giá; công + phụ "
        "tùng; hư hại xe + hàng).",
        "time_order": "Thứ tự thời gian vô lý (giao trước khi lấy; nghỉ việc trước khi tuyển).",
        "geo_mismatch": "Địa điểm không nhất quán: cặp thành phố/bang không có trong danh sách "
        "kho và điểm đầu/cuối tuyến, hoặc thành phố của sự kiện khác thành phố của kho.",
    },
}


def report_path(docs_dir: Path, lang: str) -> Path:
    return docs_dir / LABELS[lang]["file"]


def collect(con: duckdb.DuckDBPyConnection, tables: Iterable[TableSchema]) -> dict:
    """Every number the report shows, computed once for both languages."""
    tables = list(tables)
    findings = con.execute(
        "SELECT table_name, rule_id, column_name, severity, violations, sample_keys "
        "FROM dq_findings ORDER BY severity, violations DESC, table_name, rule_id, column_name"
    ).fetchall()
    error_labels = sorted(
        {f"{rule}:{col}" if col else rule for _, rule, col, sev, *_ in findings if sev == "error"}
    )
    rows, flagged, flagged_error, dups, nulls = {}, {}, {}, 0, []
    for t in tables:
        cols = ", ".join(f'"{c}"' for c in t.columns)
        rows[t.name], flagged[t.name], flagged_error[t.name] = con.execute(
            f"SELECT count(*), count(*) FILTER (WHERE len(dq_issues) > 0), "
            f'count(*) FILTER (WHERE list_has_any(dq_issues, ?::VARCHAR[])) FROM "{t.name}"',
            [error_labels],
        ).fetchone()
        dups += (
            rows[t.name]
            - con.execute(
                f'SELECT count(*) FROM (SELECT DISTINCT {cols} FROM "{t.name}")'
            ).fetchone()[0]
        )
        counts = con.execute(
            "SELECT "
            + ", ".join(f'count(*) - count("{c}")' for c in t.columns)
            + f' FROM "{t.name}"'
        ).fetchone()
        nulls += [(t.name, c, n, rows[t.name]) for c, n in zip(t.columns, counts, strict=True) if n]
    return {
        "rows": rows,
        "flagged": flagged,
        "flagged_error": flagged_error,
        "findings": findings,
        "nulls": nulls,
        "baselines": {k: (con.execute(sql).fetchone()[0], kind) for k, sql, kind in BASELINES},
        "checks": {"dup_rows": (dups, "int")}
        | {k: (con.execute(sql).fetchone()[0], "pct") for k, sql in CROSS_CHECKS},
    }


def render(data: dict, lang: str) -> str:
    t = LABELS[lang]
    f = NumberFormatter(lang)
    total_rows = sum(data["rows"].values())
    with_violations = [x for x in data["findings"] if x[4] > 0]
    period = (
        f"{f.value(*data['baselines']['period_start'])} {t['to']} "
        f"{f.value(*data['baselines']['period_end'])}"
    )
    out = [t["title"], "", t["banner"], "", t["summary"], ""]
    out += [f"| {t['metric']} | {t['value']} |", "|---|---:|"]
    out += [
        f"| {t['period']} | {period} |",
        f"| {t['tables_rows']} | {len(data['rows'])} / {f.int(total_rows)} |",
        f"| {t['rules_run']} | {len(data['findings'])} / {len(with_violations)} |",
        f"| {t['flagged_rows']} | {f.int(sum(data['flagged'].values()))} "
        f"({f.pct(sum(data['flagged'].values()) / max(total_rows, 1))}) |",
        f"| {t['flagged_error_rows']} | {f.int(sum(data['flagged_error'].values()))} "
        f"({f.pct(sum(data['flagged_error'].values()) / max(total_rows, 1))}) |",
        "",
        t["not_deleted"],
        "",
        t["baselines"],
        "",
        t["baselines_intro"],
        "",
    ]
    out += [f"| {t['metric']} | {t['value']} |", "|---|---:|"]
    for key, name in BASELINE_NAMES[lang].items():
        out.append(f"| {name} | {f.value(*data['baselines'][key])} |")

    out += ["", t["findings"], ""]
    out += [
        f"| {t['severity']} | {t['rule']} | {t['target']} | {t['rows']} | {t['share']} "
        f"| {t['samples']} |",
        "|---|---|---|---:|---:|---|",
    ]
    for table, rule, column, severity, n, samples in with_violations:
        target = f"`{table}.{column}`" if column else f"`{table}`"
        keys = ", ".join(f"`{_cell(k)}`" for k in samples)
        out.append(
            f"| {severity} | `{rule}` | {target} | {f.int(n)} "
            f"| {f.pct(n / max(data['rows'][table], 1))} | {keys} |"
        )
    clean: dict[str, list[str]] = {}
    for table, rule, column, *_rest in (x for x in data["findings"] if x[4] == 0):
        clean.setdefault(table, []).append(f"`{rule}:{column}`" if column else f"`{rule}`")
    out += ["", f"**{t['clean_rules']}:**", ""]
    out += [f"- `{table}`: {', '.join(rules)}" for table, rules in sorted(clean.items())]

    out += ["", t["rule_defs"], ""]
    out += [f"- `{rule}`: {text}" for rule, text in RULE_DEFS[lang].items()]

    out += ["", t["cross"], "", f"| {t['check']} | {t['result']} |", "|---|---:|"]
    for key, name in CHECK_NAMES[lang].items():
        out.append(f"| {_cell(name)} | {f.value(*data['checks'][key])} |")

    out += ["", t["nulls"], "", t["nulls_intro"], ""]
    out += [f"| {t['column']} | {t['empty']} | % |", "|---|---:|---:|"]
    for table, column, n, total in data["nulls"]:
        out.append(f"| `{table}.{column}` | {f.int(n)} | {f.pct(n / max(total, 1))} |")
    return "\n".join(out) + "\n"


def write_report(db_path: Path, tables: Iterable[TableSchema], docs_dir: Path) -> list[Path]:
    with duckdb.connect(str(db_path), read_only=True) as con:
        data = collect(con, tables)
    paths = []
    for lang in LANGUAGES:
        path = report_path(docs_dir, lang)
        path.write_text(render(data, lang), encoding="utf-8", newline="\n")
        paths.append(path)
    return paths


def _cell(text: str) -> str:
    """Escape `|` so it doesn't split a Markdown table cell."""
    return text.replace("|", r"\|")


class NumberFormatter:
    """EN: 1,234.5 · VI: 1.234,5."""

    def __init__(self, lang: str) -> None:
        self.lang = lang

    def num(self, x: float, decimals: int) -> str:
        s = f"{x:,.{decimals}f}"
        return s if self.lang == "en" else s.translate(str.maketrans(",.", ".,"))

    def int(self, x: float) -> str:
        return self.num(round(x), 0)

    def pct(self, x: float) -> str:
        return f"{self.num(100 * x, 1)}%"

    def value(self, x, kind: str) -> str:
        if x is None:
            return "—"
        if kind == "date":
            return x.isoformat()
        if kind == "usd_m":
            m = self.num(x / 1e6, 2)
            return f"${m}M" if self.lang == "en" else f"{m} tr USD"
        if kind == "usd":
            return f"${self.num(x, 3)}" if self.lang == "en" else f"{self.num(x, 3)} USD"
        if kind == "num2":
            return self.num(x, 2)
        if kind == "pct":
            return self.pct(x)
        return self.int(x)
