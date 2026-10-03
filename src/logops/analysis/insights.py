"""Rule-based commentary: each rule reads computed facts and writes an EN/VI sentence.

Templates contain no digits (tested): every number comes from the facts, formatted per language.
Every threshold lives in THRESHOLDS with its reason and source. Levels: info, watch, act.
"""

from collections.abc import Callable
from dataclasses import dataclass

from logops.analysis.operations import MATRIX_TIERS
from logops.data_platform.dq_report import NumberFormatter

THRESHOLDS = {
    "persistent_corr": (
        0.7,
        "A pattern counts as real if its correlation between 2022–23 and "
        "2024 is at least this; the rule used throughout the project",
        "project",
    ),
    "flat_change_pct": (
        2.0,
        "A change below ±2% is treated as flat; same tolerance as the data-quality cross-checks",
        "project",
    ),
    "driver_share": (
        0.5,
        "One factor 'drives' a change when it explains at least half of it",
        "project",
    ),
    "segment_spread_pts": (
        1.0,
        "Margins within one percentage point are treated as equal",
        "project",
    ),
    "hhi_moderate": (
        1000.0,
        "HHI 1,000–1,800 = moderately concentrated (applied here to the "
        "customer portfolio by analogy)",
        "US DOJ/FTC Merger Guidelines 2023",
    ),
    "hhi_high": (
        1800.0,
        "HHI above 1,800 = highly concentrated",
        "US DOJ/FTC Merger Guidelines 2023",
    ),
    "customer_share_risk_pct": (
        10.0,
        "A single customer above 10% of revenue is a concentration risk",
        "Dataset author's notebook (Route_optimization)",
    ),
    "city_imbalance_pct": (
        20.0,
        "A city whose loads out and in differ by more than 20% is imbalanced",
        "Dataset author's notebook (Route_optimization)",
    ),
    "surplus_act_pct": (
        20.0,
        "Act when more than 20% of loads end where there's no return load; "
        "same level as the city threshold",
        "project",
    ),
    "predictable_autocorr": (
        0.5,
        "Below 0.5, one day explains under 25% of the next day's variation: too weak to plan on",
        "project",
    ),
    "moved_watch_pct": (
        50.0,
        "Watch when most transitions (over half) need a move between cities",
        "project",
    ),
    "fuel_gap_pct": (5.0, "A bought-vs-burned gap above 5% is worth reconciling", "project"),
}
REASONS_VI = {
    "persistent_corr": "Một mẫu hình được coi là có thật nếu tương quan giữa 2022–23 và 2024 đạt "
    "mức này; quy tắc dùng xuyên suốt dự án",
    "flat_change_pct": "Thay đổi dưới ±2% được coi là không đổi; cùng dung sai với kiểm tra chéo "
    "chất lượng dữ liệu",
    "driver_share": "Một yếu tố được coi là nguyên nhân chính khi giải thích ít nhất một nửa mức "
    "thay đổi",
    "segment_spread_pts": "Các biên chênh nhau dưới một điểm phần trăm được coi là bằng nhau",
    "hhi_moderate": "HHI 1.000–1.800 = tập trung vừa (ở đây áp dụng tương tự cho danh mục khách "
    "hàng)",
    "hhi_high": "HHI trên 1.800 = tập trung cao",
    "customer_share_risk_pct": "Một khách hàng chiếm trên 10% doanh thu là rủi ro tập trung",
    "city_imbalance_pct": "Thành phố có lô đi và lô đến chênh nhau quá 20% là mất cân bằng",
    "surplus_act_pct": "Cần hành động khi trên 20% số lô kết thúc ở nơi không có hàng về; cùng mức "
    "với ngưỡng theo thành phố",
    "predictable_autocorr": "Dưới 0,5, một ngày giải thích dưới 25% biến động của ngày sau: quá "
    "yếu để lập kế hoạch",
    "moved_watch_pct": "Cần theo dõi khi phần lớn (trên một nửa) số lần chuyển phải di chuyển giữa "
    "các thành phố",
    "fuel_gap_pct": "Chênh lệch mua so với tiêu thụ trên 5% đáng để đối soát",
}
SOURCES = {
    "US DOJ/FTC Merger Guidelines 2023": "https://www.ftc.gov/system/files/ftc_gov/pdf/2023_merger_guidelines_final_12.18.2023.pdf",
    "Dataset author's notebook (Route_optimization)": "https://www.kaggle.com/code/yogape/route-optimization",
}
SERVICE_LEVELS = (95, 99)
LEVELS = {
    "en": {"info": "info", "watch": "watch", "act": "act"},
    "vi": {"info": "thông tin", "watch": "cần theo dõi", "act": "cần hành động"},
}


def t(name: str) -> float:
    return THRESHOLDS[name][0]


@dataclass(frozen=True)
class Rule:
    id: str
    topic: str
    level: Callable[[dict], str | None]  # None = rule doesn't apply
    templates: dict[str, str]
    values: Callable[[dict, NumberFormatter], dict]


def _pp(f: NumberFormatter, x: float) -> str:
    """A value already in percent, e.g. 65.2 → 65.2%."""
    return f.pct(x / 100)


def _usd(f: NumberFormatter, x: float) -> str:
    return f.value(x, "usd_m")


RULES = [
    Rule(
        "margin_driver",
        "profit",
        lambda x: (
            "act"
            if x["bridge_fuel_share"] >= t("driver_share")
            and abs(x["rpm_change_pct"]) < t("flat_change_pct")
            else None
        ),
        {
            "en": "Margin rose from {m_a} to {m_b} ({y_a} → {y_b}) while revenue per mile stayed "
            "flat ({rpm_a} → {rpm_b}). Falling fuel prices account for {fuel_part} of the "
            "{delta} gain in contribution ({share}). If fuel prices rise again, margin falls.",
            "vi": "Biên tăng từ {m_a} lên {m_b} ({y_a} → {y_b}) trong khi doanh thu/dặm gần như "
            "không đổi ({rpm_a} → {rpm_b}). Giá nhiên liệu giảm đóng góp {fuel_part} trong "
            "mức tăng {delta} của đóng góp ({share}). Nếu giá nhiên liệu tăng lại, biên sẽ giảm.",
        },
        lambda x, f: {
            "m_a": _pp(f, x["margin_first"]),
            "m_b": _pp(f, x["margin_last"]),
            "y_a": x["year_first"],
            "y_b": x["year_last"],
            "rpm_a": f.value(x["rpm_first"], "usd"),
            "rpm_b": f.value(x["rpm_last"], "usd"),
            "fuel_part": _usd(f, x["bridge_fuel"]),
            "delta": _usd(f, x["bridge_delta"]),
            "share": f.pct(x["bridge_fuel_share"]),
        },
    ),
    Rule(
        "margin_fuel_corr",
        "profit",
        lambda x: "watch" if abs(x["margin_fuel_corr"]) >= t("persistent_corr") else None,
        {
            "en": "Monthly margin moves against the fuel price (correlation {corr}): margin is "
            "exposed to fuel prices because the fuel surcharge is fixed.",
            "vi": "Biên hằng tháng đi ngược giá nhiên liệu (tương quan {corr}): biên phụ thuộc giá "
            "nhiên liệu vì phụ phí nhiên liệu là cố định.",
        },
        lambda x, f: {"corr": f.num(x["margin_fuel_corr"], 2)},
    ),
    Rule(
        "volume_flat",
        "profit",
        lambda x: "info" if abs(x["trips_change_pct"]) < t("flat_change_pct") else None,
        {
            "en": "Volume is flat: {t_a} trips in {y_a}, {t_b} in {y_b} ({chg}).",
            "vi": "Sản lượng gần như không đổi: {t_a} chuyến năm {y_a}, {t_b} chuyến năm {y_b} "
            "({chg}).",
        },
        lambda x, f: {
            "t_a": f.int(x["trips_first"]),
            "t_b": f.int(x["trips_last"]),
            "y_a": x["year_first"],
            "y_b": x["year_last"],
            "chg": _pp(f, x["trips_change_pct"]),
        },
    ),
    Rule(
        "segments_equal",
        "profit",
        lambda x: "info" if x["segment_margin_spread"] < t("segment_spread_pts") else None,
        {
            "en": "Customer segments earn almost the same margin ({lo} to {hi}): profit "
            "differences come from lanes, not from contract type.",
            "vi": "Các phân khúc khách hàng có biên gần như bằng nhau ({lo} đến {hi}): khác biệt "
            "lợi nhuận đến từ tuyến, không đến từ loại hợp đồng.",
        },
        lambda x, f: {"lo": _pp(f, x["segment_margin_min"]), "hi": _pp(f, x["segment_margin_max"])},
    ),
    Rule(
        "state_leader",
        "profit",
        lambda x: "info",
        {
            "en": "{state} contributes the most ({amount}, {share} of contribution); margins by "
            "origin state range from {lo} to {hi}.",
            "vi": "{state} đóng góp nhiều nhất ({amount}, {share} tổng đóng góp); biên theo bang "
            "đi từ {lo} đến {hi}.",
        },
        lambda x, f: {
            "state": x["top_state"],
            "amount": _usd(f, x["top_state_contribution"]),
            "share": _pp(f, x["top_state_share"]),
            "lo": _pp(f, x["state_margin_min"]),
            "hi": _pp(f, x["state_margin_max"]),
        },
    ),
    Rule(
        "concentration",
        "profit",
        lambda x: (
            "act"
            if x["largest_customer_pct"] >= t("customer_share_risk_pct")
            or x["hhi"] >= t("hhi_high")
            else "watch"
            if x["hhi"] >= t("hhi_moderate")
            else "info"
        ),
        {
            "en": "Customer concentration: largest customer {largest} of revenue, top ten {top10}, "
            "{n80} of {n} customers make up eighty percent; HHI {hhi} (moderate from "
            "{hhi_mod}, high from {hhi_high}).",
            "vi": "Tập trung khách hàng: khách lớn nhất {largest} doanh thu, mười khách lớn nhất "
            "{top10}, cần {n80} trên {n} khách để đạt tám mươi phần trăm doanh thu; HHI "
            "{hhi} (mức vừa từ {hhi_mod}, cao từ {hhi_high}).",
        },
        lambda x, f: {
            "largest": _pp(f, x["largest_customer_pct"]),
            "top10": _pp(f, x["top10_pct"]),
            "n80": x["customers_for_80pct"],
            "n": x["customers"],
            "hhi": f.int(x["hhi"]),
            "hhi_mod": f.int(t("hhi_moderate")),
            "hhi_high": f.int(t("hhi_high")),
        },
    ),
    Rule(
        "fuel_gap",
        "fuel",
        lambda x: "watch" if (x["fuel_ratio_min"] - 1) * 100 > t("fuel_gap_pct") else None,
        {
            "en": "Every year, gallons bought exceed gallons recorded as burned on trips ({lo} to "
            "{hi} times). The gap has not been reconciled.",
            "vi": "Năm nào lượng nhiên liệu mua cũng nhiều hơn lượng ghi nhận tiêu thụ trên chuyến "
            "({lo} đến {hi} lần). Chênh lệch này chưa được đối soát.",
        },
        lambda x, f: {"lo": f.num(x["fuel_ratio_min"], 2), "hi": f.num(x["fuel_ratio_max"], 2)},
    ),
    Rule(
        "capacity",
        "fleet",
        lambda x: "watch" if x["trucks_owned"] > x["cap_max"] else "info",
        {
            "en": "Trucks busy per day: {s1} of days need at most {p95}, {s2} need at most {p99}, "
            "the busiest day needed {mx}. The fleet has {in_use} trucks in use and {owned} "
            "owned.",
            "vi": "Số xe bận mỗi ngày: {s1} số ngày cần tối đa {p95} xe, {s2} số ngày cần tối đa "
            "{p99} xe, ngày bận nhất cần {mx} xe. Đội có {in_use} xe đang chạy và {owned} xe "
            "sở hữu.",
        },
        lambda x, f: {
            "s1": f"{SERVICE_LEVELS[0]}%",
            "s2": f"{SERVICE_LEVELS[1]}%",
            "p95": f.int(x["cap_p95"]),
            "p99": f.int(x["cap_p99"]),
            "mx": x["cap_max"],
            "in_use": x["trucks_in_use"],
            "owned": x["trucks_owned"],
        },
    ),
    Rule(
        "capacity_unpredictable",
        "fleet",
        lambda x: (
            "info"
            if x["lag1"] < t("predictable_autocorr")
            and abs(x["quarter_persistence"]) < t("persistent_corr")
            else None
        ),
        {
            "en": "Peak days can't be predicted: one day barely predicts the next (correlation "
            "{lag1}), no quarter is busier year after year ({qp}), and the yearly average is "
            "flat ({lo} to {hi} trucks). Plan capacity by service level, not by calendar.",
            "vi": "Không dự báo được ngày cao điểm: ngày này gần như không báo trước ngày sau "
            "(tương quan {lag1}), không có quý nào bận hơn lặp lại qua các năm ({qp}), và "
            "trung bình năm không đổi ({lo} đến {hi} xe). Nên lập kế hoạch năng lực theo mức "
            "đảm bảo, không theo lịch.",
        },
        lambda x, f: {
            "lag1": f.num(x["lag1"], 2),
            "qp": f.num(x["quarter_persistence"], 2),
            "lo": f.num(x["yearly_mean_min"], 1),
            "hi": f.num(x["yearly_mean_max"], 1),
        },
    ),
    Rule(
        "lane_matrix",
        "network",
        lambda x: "info",
        {
            "en": "Lane portfolio ({grid} by volume and margin): {protect} lanes to protect (high "
            "volume, high margin), {reprice} to reprice (high volume, low margin), {exit} "
            "to consider exiting (low volume, low margin).",
            "vi": "Danh mục tuyến ({grid} theo sản lượng và biên): {protect} tuyến cần bảo vệ (sản "
            "lượng và biên cao), {reprice} tuyến nên xem lại giá (sản lượng cao, biên thấp), "
            "{exit} tuyến cân nhắc rút lui (sản lượng và biên thấp).",
        },
        lambda x, f: {
            "protect": x["lanes_protect"],
            "reprice": x["lanes_reprice"],
            "exit": x["lanes_exit"],
            "grid": f"{MATRIX_TIERS}×{MATRIX_TIERS}",
        },
    ),
    Rule(
        "imbalance",
        "network",
        lambda x: (
            "act"
            if x["surplus_pct"] > t("surplus_act_pct")
            and x["balance_persistence"] >= t("persistent_corr")
            else "watch"
        ),
        {
            "en": "{surplus_pct} of loads ({surplus}) end in a city with no matching return load; "
            "{cities} of {n} cities are imbalanced by more than {th}, and the pattern is "
            "stable across years (correlation {pers}). {only_in} receive loads but send none.",
            "vi": "{surplus_pct} số lô ({surplus}) kết thúc ở thành phố không có hàng về "
            "tương ứng; "
            "{cities} trên {n} thành phố lệch quá {th}, và mức lệch ổn định qua các năm "
            "(tương quan {pers}). {only_in} chỉ nhận hàng, không gửi lô nào.",
        },
        lambda x, f: {
            "surplus_pct": _pp(f, x["surplus_pct"]),
            "surplus": f.int(x["surplus"]),
            "cities": x["cities_imbalanced"],
            "n": x["cities"],
            "th": f"{f.int(t('city_imbalance_pct'))}%",
            "pers": f.num(x["balance_persistence"], 3),
            "only_in": ", ".join(x["receive_only_cities"]),
        },
    ),
    Rule(
        "repositioning",
        "network",
        lambda x: "watch" if x["moved_pct"] > t("moved_watch_pct") else None,
        {
            "en": "In {moved} of transitions, a truck's next trip starts in a different city from "
            "where its last trip ended. The movement between the two isn't recorded in the "
            "data.",
            "vi": "Ở {moved} số lần chuyển, chuyến tiếp theo của xe bắt đầu ở thành phố khác nơi "
            "chuyến trước kết thúc. Quãng di chuyển giữa hai chuyến không được ghi trong dữ liệu.",
        },
        lambda x, f: {"moved": _pp(f, x["moved_pct"])},
    ),
]


def generate(facts: dict, lang: str) -> list[dict]:
    f = NumberFormatter(lang)
    out = []
    for rule in RULES:
        level = rule.level(facts)
        if level is None:
            continue
        out.append(
            {
                "id": rule.id,
                "topic": rule.topic,
                "level": level,
                "level_label": LEVELS[lang][level],
                "text": rule.templates[lang].format(**rule.values(facts, f)),
            }
        )
    return out
