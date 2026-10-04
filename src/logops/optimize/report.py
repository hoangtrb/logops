"""Recommendations table + generated docs/04-data-process-improvements and docs/05-evaluation.

Everything is computed once in `collect()` and rendered in both languages, so EN and VI always
show the same figures. Impact types:
- measured: a cost that stops (maintenance of trucks given up);
- upper bound: revenue that depends on customers accepting a change, assuming volume is kept;
- unexplained: money the data can't account for yet (not proven loss), never added to totals;
- estimate: a model result the data can only partly confirm (trip chaining: the replay's cut in
  empty miles applied to the fuel bought off trips), never added to totals;
- no signal: checked and rejected, shown with its evidence.
"""

import datetime as dt
from pathlib import Path

import duckdb
import polars as pl

from logops.analysis.operations import lane_matrix
from logops.data_platform.dq_report import NumberFormatter
from logops.optimize.chaining import DRIVING_DAY_HOURS, chaining
from logops.optimize.data_gaps import GAPS, SOURCES, measure
from logops.optimize.fleet import cross_check, disposal_tiers, fleet_plan
from logops.optimize.lanes import LOW_MARGIN_TIER, indexed_surcharge, lane_table, scenarios
from logops.optimize.lateness import PERSISTENT_CORR, late_share, persistence

LANGUAGES = ("en", "vi")
PERIOD = (dt.date(2022, 1, 1), dt.date(2024, 12, 31))
DEFAULT_CAP_PCT = 5.0  # S2 linehaul increase cap shown in the headline (5/10/none in docs)
TARGET_SHARE = 0.03  # docs/01 §5: savings ≥ 3% of measured operating cost
DATASET_URL = "https://www.kaggle.com/datasets/yogape/logistics-operations-database"

NO_SIGNAL = [  # (key, evidence en, evidence vi)
    (
        "delay_model",
        "On-time by driver/customer/lane/truck: correlation 2022-23 vs 2024 = 0.01–0.09",
        "Đúng giờ theo tài xế/khách hàng/tuyến/xe: tương quan 2022-23 với 2024 = 0,01–0,09",
    ),
    (
        "mpg",
        "MPG by driver/truck: correlation across years 0.003 / −0.068; range 6.37–6.54",
        "MPG theo tài xế/xe: tương quan qua các năm 0,003 / −0,068; chênh 6,37–6,54",
    ),
    (
        "idle",
        "Idle hours vs duration, distance, fuel: correlation ≈ 0",
        "Giờ không tải với thời gian, quãng đường, nhiên liệu: tương quan ≈ 0",
    ),
    (
        "fuel_price_location",
        "Average fuel price differs by $0.02/gallon across cities",
        "Giá nhiên liệu trung bình giữa các thành phố chênh 0,02 USD/gallon",
    ),
    (
        "customer_profitability",
        "Customer margin: correlation across years 0.03",
        "Biên theo khách hàng: tương quan qua các năm 0,03",
    ),
    (
        "truck_age",
        "Maintenance cost per mile: no trend with model year; correlation across years 0.12",
        "Chi phí bảo dưỡng/dặm: không tăng theo đời xe; tương quan qua các năm 0,12",
    ),
    (
        "bottlenecks",
        "Maintenance-shop waiting and dock detention: signal found, dropped by the "
        "project owner as not practical",
        "Chờ ở xưởng và chờ ở cửa nhận hàng: có tín hiệu, chủ dự án bỏ vì chưa thực tế",
    ),
    (
        "consolidation_detention",
        "Load consolidation and detention billing: dropped by the project "
        "owner (urgent loads can't wait; billing not reasonable)",
        "Ghép hàng và tính phí chờ: chủ dự "
        "án bỏ (hàng gấp không chờ ghép được; tính phí chờ không hợp lý)",
    ),
]
NO_SIGNAL_NAMES = {
    "en": {
        "late_deliveries": "Late deliveries (more than 2 h)",
        "delay_model": "Delay-risk model (ML)",
        "mpg": "MPG coaching by driver/truck",
        "idle": "Idle-time reduction",
        "fuel_price_location": "Buying fuel where it's cheaper",
        "customer_profitability": "Customer profitability",
        "truck_age": "Replacing old trucks",
        "bottlenecks": "Bottlenecks",
        "consolidation_detention": "Consolidation, detention billing",
    },
    "vi": {
        "late_deliveries": "Giao trễ quá 2 giờ",
        "delay_model": "Mô hình dự báo trễ (ML)",
        "mpg": "Cải thiện MPG theo tài xế/xe",
        "idle": "Giảm chạy không tải",
        "fuel_price_location": "Đổ nhiên liệu ở nơi rẻ hơn",
        "customer_profitability": "Lợi nhuận theo khách hàng",
        "truck_age": "Thay xe cũ",
        "bottlenecks": "Điểm nghẽn",
        "consolidation_detention": "Ghép hàng, tính phí chờ",
    },
}


def _late_evidence(data: dict, lang: str) -> str:
    """O4 result in words: the late share and the strongest repetition found."""
    f = NumberFormatter(lang)
    corr = data["lateness"]["persistence"].max()
    if lang == "vi":
        return (
            f"{f.pct(data['late_share'] / 100)} lần giao trễ quá 2 giờ; theo thành phố, khách "
            f"hàng, giờ hẹn, tuyến, tài xế tương quan giữa hai giai đoạn cao nhất {f.num(corr, 2)}"
            f" (cần {f.num(PERSISTENT_CORR, 1)})"
        )
    return (
        f"{f.pct(data['late_share'] / 100)} of deliveries more than 2 h late; by city, customer, "
        f"appointment hour, lane, driver the correlation between periods is at most "
        f"{f.num(corr, 2)} (needs {f.num(PERSISTENT_CORR, 1)})"
    )


def _margin_persistence(con: duckdb.DuckDBPyConnection) -> float:
    """Correlation of lane margins between the earlier years and the last year."""
    split = dt.date(PERIOD[1].year, 1, 1)
    early = classify_margins(lane_table(con, PERIOD[0], split - dt.timedelta(days=1)))
    late = classify_margins(lane_table(con, split, PERIOD[1]))
    joined = early.join(late, on="lane", suffix="_late")
    return joined.select(pl.corr("margin", "margin_late")).item()


def classify_margins(df: pl.DataFrame) -> pl.DataFrame:
    revenue = pl.col("linehaul") + pl.col("surcharge")
    return df.select("lane", margin=(revenue - pl.col("measured_cost")) / revenue)


def collect(con: duckdb.DuckDBPyConnection, growth: float = 0.0) -> dict:
    """Every figure the recommendations and both documents use."""
    years = (PERIOD[1] - PERIOD[0]).days / 365.25
    tiers = lane_matrix(con, *PERIOD).select("lane", "volume_tier", "margin_tier")
    lanes = lane_table(con, *PERIOD).join(tiers, on="lane")  # same groups as the dashboard
    by_cap = {cap: scenarios(lanes, years, cap_pct=cap) for cap in (5.0, 10.0, None)}
    headline = by_cap[DEFAULT_CAP_PCT]
    measured_cost = con.execute(
        "SELECT sum(measured_cost) FROM trip_economics WHERE dispatch_date BETWEEN ? AND ?",
        list(PERIOD),
    ).fetchone()[0]
    unattributed_maintenance = con.execute(
        "SELECT sum(maintenance_cost) FROM truck_economics WHERE trips = 0"
    ).fetchone()[0]
    ix = indexed_surcharge(con).with_columns(year=pl.col("month").dt.year())
    return {
        "years": years,
        "growth": growth,
        "plan": fleet_plan(con),
        "tiers": disposal_tiers(con, growth),
        "cross_check": cross_check(con),
        "lanes": headline,
        "lane_scenarios": by_cap,  # per-lane results for each linehaul cap (5, 10, None)
        "by_cap": {
            cap: (
                r["s1_uplift"].sum(),
                r["s2_uplift"].sum(),
                r.filter(pl.col("s2_uplift") > 0)["max_volume_loss_pct"].median(),
            )
            for cap, r in by_cap.items()
        },
        "groups": headline.group_by("group")
        .agg(
            pl.len().alias("lanes"),
            pl.col("revenue").sum(),
            pl.col("contribution").sum(),
            pl.col("margin").min().alias("margin_min"),
            pl.col("margin").max().alias("margin_max"),
        )
        .sort("group"),
        "indexed_by_year": ix.group_by("year")
        .agg(pl.col("actual").sum(), pl.col("indexed").sum(), pl.col("price").mean())
        .sort("year"),
        "indexed_base": ix["base_price"][0],
        "target_per_year": TARGET_SHARE * (measured_cost + unattributed_maintenance) / years,
        "margin_persistence": _margin_persistence(con),
        "late_share": late_share(con, *PERIOD),
        "lateness": persistence(con, *PERIOD),
        "gaps": measure(con, headline["break_even_driver_cost_per_mile"].min()),
        "chaining": chaining(con, *PERIOD),
    }


REC_TEXT = {
    "en": {
        "dispose": "Dispose of {n} {status} trucks that never ran",
        "review_active": "Review the {n} lowest-mileage trucks in use",
        "return": "; return {n} to service",
        "fleet_evidence": "Annual maintenance cost of these trucks",
        "trucks": "{n} trucks",
        "status": {"Inactive": "inactive", "Maintenance": "in-maintenance"},
        "s1_item": "{n} lanes",
        "s1_action": "Raise the fuel-surcharge rate to the median ({rate} per mile)",
        "s1_evidence": "Fuel cost per mile is the same on every lane, but surcharge rates range "
        "from {lo} to {hi} per mile",
        "s2_item": "{n} of {low} lowest-margin lanes",
        "s2_action": "Raise linehaul toward the median margin ({median}), at most +{cap}%",
        "s2_evidence": "Lane margins repeat across years (correlation {corr} between 2022–23 and "
        "2024)",
        "s3_item": "All lanes",
        "s3_action": "Index the fuel surcharge to the fuel price",
        "s3_evidence": "Revenue-neutral over the period; customers share the fuel-price risk",
        "fuel_item": "Fuel reconciliation",
        "fuel_action": "Monthly bought-vs-burned check per truck",
        "fuel_evidence": "Gallons bought are {ratio} times the gallons burned on trips",
        "chain_item": "{miles} fewer empty miles a year ({cut})",
        "chain_action": "Send the nearest free truck to each load (one already in the pickup city "
        "first)",
        "chain_evidence": "Replay of {loads} loads at actual times, distances over the lanes, an "
        "empty mile at {per_mile} ({price} a gallon ÷ {mpg} miles a gallon): empty miles {cut}. "
        "The model's {model} a year is above the fuel actually bought off trips, so the cut is "
        "applied to that fuel ({off_trip}): a maximum",
        "no_action": "No action",
    },
    "vi": {
        "dispose": "Thanh lý {n} xe {status} chưa từng chạy chuyến",
        "review_active": "Rà soát {n} xe đang chạy ít dặm nhất",
        "return": "; đưa {n} xe trở lại vận hành",
        "fleet_evidence": "Chi phí bảo dưỡng mỗi năm của các xe này",
        "trucks": "{n} xe",
        "status": {"Inactive": "ngừng hoạt động", "Maintenance": "đang bảo dưỡng"},
        "s1_item": "{n} tuyến",
        "s1_action": "Nâng mức phụ phí nhiên liệu lên trung vị ({rate} mỗi dặm)",
        "s1_evidence": "Chi phí nhiên liệu mỗi dặm như nhau trên mọi tuyến, nhưng phụ phí dao động "
        "từ {lo} đến {hi} mỗi dặm",
        "s2_item": "{n} trên {low} tuyến biên thấp nhất",
        "s2_action": "Tăng cước về gần biên trung vị ({median}), tối đa +{cap}%",
        "s2_evidence": "Biên của tuyến lặp lại qua các năm (tương quan {corr} giữa 2022–23 và "
        "2024)",
        "s3_item": "Mọi tuyến",
        "s3_action": "Gắn phụ phí nhiên liệu với giá nhiên liệu",
        "s3_evidence": "Tổng doanh thu không đổi trong kỳ; khách hàng chia sẻ rủi ro giá nhiên "
        "liệu",
        "fuel_item": "Đối soát nhiên liệu",
        "fuel_action": "Đối chiếu hằng tháng lượng mua với lượng tiêu thụ theo từng xe",
        "fuel_evidence": "Lượng mua bằng {ratio} lần lượng ghi nhận tiêu thụ trên chuyến",
        "chain_item": "Bớt {miles} dặm chạy rỗng mỗi năm ({cut})",
        "chain_action": "Điều xe rảnh gần nhất cho mỗi lô (ưu tiên xe đang ở thành phố lấy hàng)",
        "chain_evidence": "Mô phỏng lại {loads} lô theo giờ thực tế, quãng đường theo mạng tuyến, "
        "mỗi dặm chạy rỗng {per_mile} ({price} mỗi gallon ÷ {mpg} dặm mỗi gallon): dặm chạy rỗng "
        "{cut}. Mô hình tính ra {model} mỗi năm, vượt lượng nhiên liệu thực mua ngoài chuyến, nên "
        "chỉ áp tỷ lệ giảm lên phần nhiên liệu đó ({off_trip}): là mức tối đa",
        "no_action": "Không đề xuất",
    },
}


def recommendations(data: dict, lang: str = "en") -> pl.DataFrame:
    """One row per recommendation in `lang`; `area` and `impact_type` stay as English keys."""
    r, f = REC_TEXT[lang], NumberFormatter(lang)
    usd_mile = lambda x: f.value(x, "usd")  # noqa: E731
    rows = []
    for t in data["tiers"].iter_rows(named=True):
        if t["trucks"] == 0 and t["return_to_service"] == 0:
            continue
        if t["tier"] == 3:
            action = r["review_active"].format(n=t["trucks"])
        else:
            action = r["dispose"].format(n=t["trucks"], status=r["status"][t["status"]])
        if t["return_to_service"]:
            action += r["return"].format(n=t["return_to_service"])
        rows.append(
            (
                "Fleet",
                r["trucks"].format(n=t["trucks"]),
                action,
                t["maintenance_per_year"],
                t["saving_type"],
                r["fleet_evidence"],
            )
        )
    lanes = data["lanes"]
    s1 = lanes.filter(pl.col("s1_uplift") > 0)
    s2 = lanes.filter(pl.col("s2_uplift") > 0)
    low = lanes.filter(pl.col("margin_tier") == LOW_MARGIN_TIER)
    rows.append(
        (
            "Lanes",
            r["s1_item"].format(n=s1.height),
            r["s1_action"].format(rate=usd_mile(lanes["fsc_rate"].median())),
            s1["s1_uplift"].sum(),
            "upper bound",
            r["s1_evidence"].format(
                lo=usd_mile(lanes["fsc_rate"].min()), hi=usd_mile(lanes["fsc_rate"].max())
            ),
        )
    )
    rows.append(
        (
            "Lanes",
            r["s2_item"].format(n=s2.height, low=low.height),
            r["s2_action"].format(
                median=f.pct(lanes["margin"].median()), cap=f.num(DEFAULT_CAP_PCT, 0)
            ),
            s2["s2_uplift"].sum(),
            "upper bound",
            r["s2_evidence"].format(corr=f.num(data["margin_persistence"], 3)),
        )
    )
    rows.append(("Lanes", r["s3_item"], r["s3_action"], 0.0, "risk sharing", r["s3_evidence"]))
    g = data["gaps"]
    rows.append(
        (
            "Data",
            r["fuel_item"],
            r["fuel_action"],
            g.unreconciled_value_per_year,
            "unexplained",
            r["fuel_evidence"].format(ratio=f.num(g.gallons_purchased / g.gallons_burned, 2)),
        )
    )
    c = data["chaining"]
    k = c["costs"]
    rows.append(
        (
            "Network",
            r["chain_item"].format(
                miles=f.int(
                    c["today"]["empty_miles_per_year"] - c["nearest"]["empty_miles_per_year"]
                ),
                cut=f"−{f.pct(c['empty_miles_cut'])}",
            ),
            r["chain_action"],
            c["saving_per_year"],
            "estimate",
            r["chain_evidence"].format(
                loads=f.int(c["loads"]),
                per_mile=f.value(k["cost_per_mile"], "usd"),
                price=f.value(k["fuel_price"], "usd"),
                mpg=f.num(k["mpg"], 2),
                cut=f"−{f.pct(c['empty_miles_cut'])}",
                model=f.value(c["model_fuel_saving"], "usd_m"),
                off_trip=f.value(k["off_trip_fuel_per_year"], "usd_m"),
            ),
        )
    )
    rows.append(
        (
            "Checked",
            NO_SIGNAL_NAMES[lang]["late_deliveries"],
            r["no_action"],
            0.0,
            "no signal",
            _late_evidence(data, lang),
        )
    )
    for key, en, vi in NO_SIGNAL:
        rows.append(
            (
                "Checked",
                NO_SIGNAL_NAMES[lang][key],
                r["no_action"],
                0.0,
                "no signal",
                en if lang == "en" else vi,
            )
        )
    return pl.DataFrame(
        rows,
        schema=["area", "item", "action", "annual_impact_usd", "impact_type", "evidence"],
        orient="row",
    )


def totals(data: dict) -> dict:
    rec = recommendations(data)
    measured = rec.filter(pl.col("impact_type") == "measured")["annual_impact_usd"].sum()
    upper = rec.filter(pl.col("impact_type") == "upper bound")["annual_impact_usd"].sum()
    return {"measured": measured, "upper": upper, "target": data["target_per_year"]}


def write_recommendations_table(con: duckdb.DuckDBPyConnection, data: dict) -> None:
    rec = recommendations(data)
    con.execute(
        "CREATE OR REPLACE TABLE recommendations (area VARCHAR, item VARCHAR, "
        "action VARCHAR, annual_impact_usd DOUBLE, impact_type VARCHAR, evidence VARCHAR)"
    )
    con.executemany("INSERT INTO recommendations VALUES (?, ?, ?, ?, ?, ?)", rec.rows())


# ---------------------------------------------------------------- documents

T = {
    "en": {
        "eval_file": "05-evaluation.md",
        "gaps_file": "04-data-process-improvements.md",
        "eval_title": "# 05 · Evaluation: Savings vs Target",
        "gaps_title": "# 04 · Data Gaps → Process Improvements",
        "banner": "> Generated by `uv run logops build` from `src/logops/optimize/`; do not edit "
        "by hand. · Vietnamese: [{vi}]({vi}) · Spec: [SPEC-optimize.md](../SPEC-optimize.md)",
        "verdict": "## 1. Verdict",
        "verdict_rows": [
            "Target (3% of measured operating cost)",
            "Measured savings",
            "Upper bound (pricing, if volume is kept)",
            "Measured + upper bound",
        ],
        "per_year": "per year",
        "of_target": "of target",
        "verdict_note": "Measured savings alone don't reach the target; they rest on giving up "
        "trucks that never ran. The pricing scenarios can exceed it, but only if customers accept "
        "the changes. The two are kept separate on purpose.",
        "fleet": "## 2. Fleet size",
        "fleet_intro": "Daily demand counts the trucks working each day (a trip occupies its truck "
        "for ⌈duration ÷ 24 h⌉ days), as on the dashboard. Trucks needed = ⌈p99 of daily demand × "
        "(1 + share of trips without a truck ID) × (1 + growth) ÷ availability⌉. Availability = 1 "
        "− maintenance downtime ÷ hours of the trucks in use.",
        "fleet_cols": [
            "Growth",
            "Design demand",
            "Availability",
            "Trucks needed",
            "Fleet",
            "In use",
            "Surplus",
        ],
        "tiers_title": "**Recommendation at {g}% growth** (most expensive trucks go first):",
        "tier_cols": [
            "Tier",
            "Trucks",
            "Status",
            "Return to service",
            "Maintenance per year",
            "Type",
        ],
        "cross": "**Cross-check:** busiest day {busiest} trucks; at most {monthly} trucks active "
        "in any month (monthly truck utilization table). At 0% growth the fleet needs {needed}; "
        "{above} of {days} days needed more, coverable by short-term rental.",
        "resale": "Resale value of disposed trucks isn't in the data: an unquantified extra "
        "benefit.",
        "lanes": "## 3. Lane profitability",
        "lanes_intro": "All 58 lanes are profitable on measured cost; margins are before driver "
        "pay. The weakest lane loses money if driver cost exceeds {weakest} per mile.",
        "group_cols": ["Group", "Lanes", "Revenue per year", "Margin range"],
        "groups": {
            "protect": "Protect (high volume, high margin)",
            "grow": "Grow volume (mid volume, high margin)",
            "growth_opportunity": "Find more freight (low volume, high margin)",
            "maintain": "Maintain (mid margin)",
            "monitor": "Monitor (low volume, mid margin)",
            "reprice": "Renegotiate rates (high volume, low margin)",
            "review_price": "Review rates and costs (mid volume, low margin)",
            "review_low": "Review rates (low volume, low margin)",
        },
        "scen_title": "**Scenarios** (upper bounds; median break-even volume loss = how much "
        "volume the repriced lanes could lose before earning less than today):",
        "scen_cols": [
            "Linehaul cap",
            "S1 surcharge",
            "S2 linehaul",
            "Total per year",
            "Median break-even volume loss",
        ],
        "no_cap": "none (theoretical)",
        "index_title": "**S3 – index the surcharge to the fuel price** (revenue-neutral base "
        "{base}/gallon; not counted as a saving):",
        "index_cols": ["Year", "Average price", "Actual surcharge", "Indexed surcharge"],
        "checked": "## 4. Checked and rejected",
        "checked_cols": ["Lever", "Evidence"],
        "chain_title": "### Trip chaining: nearest truck (simulation, estimate)",
        "chain_intro": "All {loads} loads replayed at their actual times under two dispatch rules: "
        "as today (truck idle longest, anywhere) and nearest truck. Distances come from the lanes "
        "(shortest path where two cities have no lane), an empty mile costs {per_mile} ({price} a "
        "gallon ÷ {mpg} miles a gallon). The model's empty miles are about three times what the "
        "fuel bought off trips allows, so only its cut ({cut}) is applied to that fuel "
        "({off_trip}): {saving} a year, a maximum, never added to the totals. No fixed limit on "
        "the empty drive: trucks in cities that send little back must drive far, and any limit up "
        "to 24 h needs thousands of extra trucks.",
        "chain_cols": ["", "As today", "Nearest truck"],
        "chain_rows": [
            "Trips needing a move",
            "Moves a year",
            "Empty miles a year",
            "Miles per move",
            "Moves within one driving day ({h} h)",
            "Trucks needed",
        ],
        "gaps_intro": "Each gap: the measured cost of leaving it, and feasible fixes. Tier 1 = "
        "process or configuration in existing systems. Tier 2 = devices. Device prices are "
        "indicative public figures, to be replaced by vendor quotes.",
        "gap_cols": ["#", "Gap", "Evidence", "Cost of not doing", "Tier 1", "Tier 2"],
        "tele_title": "## Telematics (tier 2 for rows {rows}): cost vs benefit",
        "tele_rows": [
            "Trucks in use",
            "Cost per year (subscription + hardware over {life} years)",
            "Break-even: share of fuel spend it must save",
            "Industry benchmark for fuel-card misuse alone",
        ],
        "tele_note": "One device serves rows {rows}. It pays for itself if it prevents "
        "{break_even} of fuel spend; the misuse benchmark alone is 2–5%.",
        "sources": "## Sources",
    },
    "vi": {
        "eval_file": "05-evaluation.vi.md",
        "gaps_file": "04-data-process-improvements.vi.md",
        "eval_title": "# 05 · Đánh giá: tiết kiệm so với mục tiêu",
        "gaps_title": "# 04 · Lỗ hổng dữ liệu → cải tiến quy trình",
        "banner": "> Sinh tự động bằng `uv run logops build` từ `src/logops/optimize/`; không sửa "
        "tay. · Bản tiếng Anh: [{en}]({en}) · Spec: [SPEC-optimize.vi.md](../SPEC-optimize.vi.md)",
        "verdict": "## 1. Kết luận",
        "verdict_rows": [
            "Mục tiêu (3% chi phí vận hành đo được)",
            "Tiết kiệm đo được",
            "Tiềm năng tối đa (điều chỉnh giá, nếu giữ sản lượng)",
            "Đo được + tiềm năng tối đa",
        ],
        "per_year": "mỗi năm",
        "of_target": "của mục tiêu",
        "verdict_note": "Riêng tiết kiệm đo được thì chưa đạt mục tiêu; phần này đến từ việc bỏ "
        "các xe không chạy. Các kịch bản giá có thể vượt mục tiêu, nhưng chỉ khi khách hàng chấp "
        "nhận. Hai loại được tách riêng có chủ đích.",
        "fleet": "## 2. Quy mô đội xe",
        "fleet_intro": "Nhu cầu mỗi ngày đếm số xe hoạt động trong ngày (một chuyến chiếm xe ⌈thời "
        "gian ÷ 24 giờ⌉ ngày), giống trên dashboard. Số xe cần = ⌈p99 nhu cầu mỗi ngày × (1 + tỷ "
        "lệ chuyến thiếu mã xe) × (1 + tăng trưởng) ÷ hệ số sẵn sàng⌉. Hệ số sẵn sàng = 1 − giờ "
        "dừng bảo dưỡng ÷ tổng giờ của các xe đang chạy.",
        "fleet_cols": [
            "Tăng trưởng",
            "Nhu cầu thiết kế",
            "Hệ số sẵn sàng",
            "Số xe cần",
            "Đội xe",
            "Đang chạy",
            "Dư",
        ],
        "tiers_title": "**Đề xuất ở mức tăng trưởng {g}%** (xe tốn bảo dưỡng nhất được thanh lý "
        "trước):",
        "tier_cols": [
            "Bậc",
            "Số xe",
            "Trạng thái",
            "Đưa lại vận hành",
            "Bảo dưỡng mỗi năm",
            "Loại",
        ],
        "cross": "**Đối chiếu:** ngày bận nhất {busiest} xe; tháng đông nhất có {monthly} xe chạy "
        "(bảng chỉ số sử dụng xe theo tháng). Ở mức tăng trưởng 0% đội xe cần {needed} xe; {above} "
        "trên {days} ngày cần nhiều hơn, có thể thuê xe ngắn hạn.",
        "resale": "Tiền bán xe không có trong dữ liệu: là lợi ích thêm chưa định lượng.",
        "lanes": "## 3. Lợi nhuận tuyến",
        "lanes_intro": "Cả 58 tuyến đều có lời trên chi phí đo được; biên là trước lương tài xế. "
        "Tuyến yếu nhất lỗ nếu chi phí tài xế vượt {weakest}/dặm.",
        "group_cols": ["Nhóm", "Số tuyến", "Doanh thu mỗi năm", "Khoảng biên"],
        "groups": {
            "protect": "Giữ và bảo vệ (sản lượng cao, biên cao)",
            "grow": "Tăng sản lượng (sản lượng vừa, biên cao)",
            "growth_opportunity": "Tìm thêm nguồn hàng (sản lượng thấp, biên cao)",
            "maintain": "Duy trì (biên vừa)",
            "monitor": "Theo dõi (sản lượng thấp, biên vừa)",
            "reprice": "Đàm phán lại giá (sản lượng cao, biên thấp)",
            "review_price": "Rà soát giá và chi phí (sản lượng vừa, biên thấp)",
            "review_low": "Rà soát giá cước (sản lượng thấp, biên thấp)",
        },
        "scen_title": "**Kịch bản** (tiềm năng tối đa; mất khách hòa vốn trung vị = các tuyến điều "
        "chỉnh giá có thể mất bao nhiêu sản lượng trước khi thu ít hơn hiện tại):",
        "scen_cols": [
            "Trần tăng cước",
            "S1 phụ phí",
            "S2 cước",
            "Tổng mỗi năm",
            "Mất khách hòa vốn (trung vị)",
        ],
        "no_cap": "không giới hạn (lý thuyết)",
        "index_title": "**S3 – phụ phí theo chỉ số giá nhiên liệu** (giá cơ sở trung hòa doanh thu "
        "{base}/gallon; không tính là tiết kiệm):",
        "index_cols": ["Năm", "Giá trung bình", "Phụ phí thực tế", "Phụ phí theo chỉ số"],
        "checked": "## 4. Đã kiểm tra và loại bỏ",
        "checked_cols": ["Đòn bẩy", "Bằng chứng"],
        "chain_title": "### Ghép chuyến: điều xe gần nhất (mô phỏng, ước tính)",
        "chain_intro": "Mô phỏng lại toàn bộ {loads} lô theo giờ thực tế với hai cách điều phối: "
        "như hiện tại (xe rảnh lâu nhất, ở đâu cũng được) và điều xe gần nhất. Quãng đường lấy từ "
        "mạng tuyến (đường ngắn nhất khi hai thành phố không có tuyến trực tiếp), mỗi dặm chạy "
        "rỗng {per_mile} ({price} mỗi gallon ÷ {mpg} dặm mỗi gallon). Số dặm chạy rỗng của mô hình "
        "gấp khoảng ba lần mức mà nhiên liệu mua ngoài chuyến cho phép, nên chỉ áp tỷ lệ giảm "
        "({cut}) lên phần nhiên liệu đó ({off_trip}): {saving} mỗi năm, là mức tối đa, không cộng "
        "vào tổng. Không đặt giới hạn cứng cho quãng chạy rỗng: xe ở các thành phố ít hàng đi phải "
        "chạy xa, và mọi giới hạn đến 24 giờ đều cần thêm hàng nghìn xe.",
        "chain_cols": ["", "Như hiện tại", "Điều xe gần nhất"],
        "chain_rows": [
            "Chuyến phải điều xe",
            "Lần điều xe mỗi năm",
            "Dặm chạy rỗng mỗi năm",
            "Dặm mỗi lần điều xe",
            "Lần điều xe trong một ngày lái ({h} giờ)",
            "Số xe cần",
        ],
        "gaps_intro": "Mỗi lỗ hổng: chi phí đo được nếu để nguyên, và biện pháp khả thi. Mức 1 = "
        "quy trình hoặc cấu hình trên hệ thống sẵn có. Mức 2 = thiết bị. Giá thiết bị là số liệu "
        "công khai tham khảo, cần thay bằng báo giá thực tế.",
        "gap_cols": ["#", "Lỗ hổng", "Bằng chứng", "Chi phí khi không làm", "Mức 1", "Mức 2"],
        "tele_title": "## Telematics (mức 2 cho các dòng {rows}): chi phí so với lợi ích",
        "tele_rows": [
            "Số xe đang chạy",
            "Chi phí mỗi năm (thuê bao + thiết bị chia đều {life} năm)",
            "Hòa vốn: phần chi phí nhiên liệu cần tiết kiệm",
            "Chuẩn ngành riêng cho lạm dụng thẻ nhiên liệu",
        ],
        "tele_note": "Một thiết bị phục vụ các dòng {rows}. Thiết bị tự hoàn vốn nếu ngăn được "
        "{break_even} chi phí nhiên liệu; riêng chuẩn ngành về lạm dụng thẻ đã là 2–5%.",
        "sources": "## Nguồn",
    },
}


LABELS = {
    "en": {
        "Inactive": "Inactive",
        "Maintenance": "Maintenance",
        "Active (lowest mileage)": "Active (lowest mileage)",
        "measured": "measured",
        "upper bound": "upper bound",
    },
    "vi": {
        "Inactive": "Ngừng hoạt động",
        "Maintenance": "Đang bảo dưỡng",
        "Active (lowest mileage)": "Đang chạy (ít dặm nhất)",
        "measured": "đo được",
        "upper bound": "tiềm năng tối đa",
    },
}


def _dollars(f: NumberFormatter, lang: str, x: float) -> str:
    return f"${f.int(x)}" if lang == "en" else f"{f.int(x)} USD"


def _table(header: list[str], rows: list[list[str]], right: set[int] = frozenset()) -> list[str]:
    align = ["---:" if i in right else "---" for i in range(len(header))]
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(align) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", r"\|") for c in r) + " |" for r in rows]
    return out


def render_evaluation(data: dict, lang: str) -> str:
    t, f = T[lang], NumberFormatter(lang)
    usd = lambda x: f.value(x, "usd_m")  # noqa: E731
    tot = totals(data)
    out = [
        t["eval_title"],
        "",
        t["banner"].format(en="05-evaluation.md", vi="05-evaluation.vi.md"),
        "",
        t["verdict"],
        "",
    ]
    values = [tot["target"], tot["measured"], tot["upper"], tot["measured"] + tot["upper"]]
    out += _table(
        ["", t["per_year"], t["of_target"]],
        [
            [name, usd(v), f.pct(v / tot["target"])]
            for name, v in zip(t["verdict_rows"], values, strict=True)
        ],
        {1, 2},
    )
    out += ["", t["verdict_note"], "", t["fleet"], "", t["fleet_intro"], ""]
    out += _table(
        t["fleet_cols"],
        [
            [
                f"+{f.num(r['growth_pct'], 0)}%",
                f.num(r["design_demand"], 1),
                f.pct(r["availability"]),
                r["trucks_needed"],
                r["fleet_size"],
                r["trucks_in_use"],
                r["surplus"],
            ]
            for r in data["plan"].iter_rows(named=True)
        ],
        {1, 2, 3, 4, 5, 6},
    )
    out += ["", t["tiers_title"].format(g=f.num(100 * data["growth"], 0)), ""]
    out += _table(
        t["tier_cols"],
        [
            [
                r["tier"],
                r["trucks"],
                LABELS[lang][r["status"]],
                r["return_to_service"],
                usd(r["maintenance_per_year"]),
                LABELS[lang][r["saving_type"]],
            ]
            for r in data["tiers"].iter_rows(named=True)
        ],
        {1, 3, 4},
    )
    cc = data["cross_check"]
    out += [
        "",
        t["cross"].format(
            busiest=cc["busiest_day_trucks"],
            monthly=cc["max_trucks_active_in_a_month"],
            needed=data["plan"]["trucks_needed"][0],
            above=cc["days_above_need"],
            days=cc["days"],
        ),
        "",
        t["resale"],
        "",
        t["lanes"],
        "",
        t["lanes_intro"].format(
            weakest=f.value(data["gaps"].weakest_lane_break_even_driver_cost, "usd")
        ),
        "",
    ]
    out += _table(
        t["group_cols"],
        [
            [
                t["groups"][r["group"]],
                r["lanes"],
                usd(r["revenue"] / data["years"]),
                f"{f.pct(r['margin_min'])} – {f.pct(r['margin_max'])}",
            ]
            for r in data["groups"].iter_rows(named=True)
        ],
        {1, 2},
    )
    out += ["", t["scen_title"], ""]
    out += _table(
        t["scen_cols"],
        [
            [
                t["no_cap"] if cap is None else f"+{f.num(cap, 0)}%",
                usd(s1),
                usd(s2),
                usd(s1 + s2),
                f.pct(loss / 100),
            ]
            for cap, (s1, s2, loss) in data["by_cap"].items()
        ],
        {1, 2, 3, 4},
    )
    out += ["", t["index_title"].format(base=f.value(data["indexed_base"], "usd")), ""]
    out += _table(
        t["index_cols"],
        [
            [r["year"], f.value(r["price"], "usd"), usd(r["actual"]), usd(r["indexed"])]
            for r in data["indexed_by_year"].iter_rows(named=True)
        ],
        {1, 2, 3},
    )
    c, k = data["chaining"], data["chaining"]["costs"]
    out += [
        "",
        t["chain_title"],
        "",
        t["chain_intro"].format(
            loads=f.int(c["loads"]),
            per_mile=f.value(k["cost_per_mile"], "usd"),
            price=f.value(k["fuel_price"], "usd"),
            mpg=f.num(k["mpg"], 2),
            cut=f"−{f.pct(c['empty_miles_cut'])}",
            off_trip=usd(k["off_trip_fuel_per_year"]),
            saving=usd(c["saving_per_year"]),
        ),
        "",
    ]
    cells = [
        lambda x: f.pct(x["moved_pct"] / 100),
        lambda x: f.int(x["moves_per_year"]),
        lambda x: f.int(x["empty_miles_per_year"]),
        lambda x: f.int(x["miles_per_move"]),
        lambda x: f.pct(x["within_a_day_pct"] / 100),
        lambda x: f.int(x["trucks"]),
    ]
    out += _table(
        t["chain_cols"],
        [
            [name.format(h=DRIVING_DAY_HOURS), cell(c["today"]), cell(c["nearest"])]
            for name, cell in zip(t["chain_rows"], cells, strict=True)
        ],
        {1, 2},
    )
    out += ["", t["checked"], ""]
    out += _table(
        t["checked_cols"],
        [[NO_SIGNAL_NAMES[lang]["late_deliveries"], _late_evidence(data, lang)]]
        + [[NO_SIGNAL_NAMES[lang][k], en if lang == "en" else vi] for k, en, vi in NO_SIGNAL],
    )
    return "\n".join(out) + "\n"


def gap_values(data: dict, lang: str) -> dict:
    """The figures the gap texts refer to, formatted for `lang`."""
    f, g = NumberFormatter(lang), data["gaps"]
    usd = lambda x: f.value(x, "usd_m")  # noqa: E731
    return {
        "unreconciled_gallons_m": f.num(g.unreconciled_gallons / 1e6, 2),
        "unreconciled_value": usd(g.unreconciled_value_per_year),
        "misuse_low": usd(g.misuse_benchmark_per_year[0]),
        "misuse_high": usd(g.misuse_benchmark_per_year[1]),
        "unattributable_fuel": usd(g.unattributable_fuel_per_year),
        "margin": f.pct(g.contribution_margin_pct / 100),
        "break_even": f.value(g.weakest_lane_break_even_driver_cost, "usd"),
        "outside_window": f.int(g.deliveries_outside_window_per_year),
        "outside_share": f.pct(g.deliveries_outside_window_per_year / g.deliveries_per_year),
        "detention_hours": f.int(g.detention_hours_per_year),
        "moved": f.pct(g.moved_pct / 100),
        "moved_random": f.pct(g.moved_random_pct / 100),
        "late_share": f.pct(g.late_share_pct / 100),
        "late_corr": f.num(g.late_persistence_max, 2),
    }


def gap_rows(data: dict, lang: str) -> list[dict]:
    """One dict per data gap, priority order, texts filled in for `lang`."""
    values = gap_values(data, lang)
    return [
        {"priority": gap["priority"], **{k: v.format(**values) for k, v in gap[lang].items()}}
        for gap in sorted(GAPS, key=lambda x: x["priority"])
    ]


def render_gaps(data: dict, lang: str) -> str:
    t, f, g = T[lang], NumberFormatter(lang), data["gaps"]
    values = gap_values(data, lang)
    out = [
        t["gaps_title"],
        "",
        t["banner"].format(
            en="04-data-process-improvements.md", vi="04-data-process-improvements.vi.md"
        ),
        "",
        t["gaps_intro"],
        "",
    ]
    rows = []
    for gap in sorted(GAPS, key=lambda x: x["priority"]):
        text = {k: v.format(**values) for k, v in gap[lang].items()}
        rows.append(
            [
                gap["priority"],
                text["gap"],
                text["evidence"],
                text["not_doing"],
                text["tier1"],
                text["tier2"],
            ]
        )
    out += _table(t["gap_cols"], rows)
    tele_rows = ", ".join(str(x["priority"]) for x in GAPS if x["uses_telematics"])
    low, high = g.telematics_cost_per_year
    out += ["", t["tele_title"].format(rows=tele_rows), ""]
    out += _table(
        ["", ""],
        [
            [t["tele_rows"][0], g.trucks_in_use],
            [
                t["tele_rows"][1].format(life=3),
                f"{_dollars(f, lang, low)} – {_dollars(f, lang, high)}",
            ],
            [t["tele_rows"][2], f.pct(g.telematics_break_even_share)],
            [t["tele_rows"][3], f"2–5% = {values['misuse_low']} – {values['misuse_high']}"],
        ],
        {1},
    )
    out += [
        "",
        t["tele_note"].format(rows=tele_rows, break_even=f.pct(g.telematics_break_even_share)),
        "",
        t["sources"],
        "",
    ]
    out += [f"- {text} — <{url}>" for text, url in SOURCES.values()]
    return "\n".join(out) + "\n"


def write_optimize_docs(con: duckdb.DuckDBPyConnection, docs_dir: Path, data: dict) -> list[Path]:
    paths = []
    for lang in LANGUAGES:
        for key, render in (("eval_file", render_evaluation), ("gaps_file", render_gaps)):
            path = docs_dir / T[lang][key]
            path.write_text(render(data, lang), encoding="utf-8", newline="\n")
            paths.append(path)
    return paths


def write_optimize_outputs(db_path: Path, docs_dir: Path) -> list[Path]:
    """Build step: the recommendations table in the warehouse + docs 04 and 05."""
    with duckdb.connect(str(db_path)) as con:
        data = collect(con)
        write_recommendations_table(con, data)
        return write_optimize_docs(con, docs_dir, data)
