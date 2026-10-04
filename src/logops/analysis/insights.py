"""Rule-based commentary: each rule reads computed facts and writes an EN/VI finding.

A finding has a title, whether it is good or bad news (tone), what happened, its impact (or what
it means) and, for priority and watch findings, a recommended action.

Templates contain no digits (tested): every number comes from the facts, formatted per language.
Every threshold lives in THRESHOLDS with its reason and source.
Levels: act (priority), watch, info (for reference).
"""

from collections.abc import Callable
from dataclasses import dataclass, field

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
        "Priority when more than 20% of loads end where there's no return load; "
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
    "surplus_act_pct": "Ưu tiên xử lý khi trên 20% số lô kết thúc ở nơi không có hàng về; cùng mức "
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
    "en": {"act": "Priority", "watch": "Watch", "info": "For reference"},
    "vi": {"act": "Ưu tiên xử lý", "watch": "Cần theo dõi", "info": "Tham khảo"},
}
TONES = {  # is the finding good or bad news for the business
    "en": {"good": "Positive", "bad": "Negative", "risk": "Risk", "neutral": "Neutral"},
    "vi": {"good": "Tích cực", "bad": "Tiêu cực", "risk": "Rủi ro", "neutral": "Trung tính"},
}
TOPICS = {
    "en": {"profit": "Profit", "network": "Network", "fleet": "Fleet", "fuel": "Fuel"},
    "vi": {"profit": "Lợi nhuận", "network": "Mạng lưới", "fleet": "Đội xe", "fuel": "Nhiên liệu"},
}
PARTS = {  # labels for the parts of a finding; info findings explain meaning instead of impact
    "en": {
        "what": "What happened",
        "impact": "Impact",
        "meaning": "What it means",
        "action": "Recommended",
    },
    "vi": {"what": "Diễn biến", "impact": "Ảnh hưởng", "meaning": "Ý nghĩa", "action": "Đề xuất"},
}


def t(name: str) -> float:
    return THRESHOLDS[name][0]


@dataclass(frozen=True)
class Rule:
    """One finding: when it fires, whether it is good or bad news, and its EN/VI text.

    `templates[lang]` has a title, what happened, the impact (or meaning) and, optionally, a
    recommended action. `by_level` overrides parts of the text for a given level, for rules whose
    message changes with the level (e.g. concentration is good news when low).
    """

    id: str
    topic: str
    level: Callable[[dict], str | None]  # None = rule doesn't apply
    tone: Callable[[str], str]  # level → good | bad | risk | neutral
    templates: dict[str, dict[str, str]]
    values: Callable[[dict, NumberFormatter], dict]
    by_level: dict[str, dict[str, dict[str, str]]] = field(default_factory=dict)


def _pp(f: NumberFormatter, x: float) -> str:
    """A value already in percent, e.g. 65.2 → 65.2%."""
    return f.pct(x / 100)


def _usd(f: NumberFormatter, x: float) -> str:
    return f.value(x, "usd_m")


def _always(tone: str) -> Callable[[str], str]:
    return lambda _level: tone


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
        _always("risk"),
        {
            "en": {
                "title": "Profit grew because fuel got cheaper, not because operations improved",
                "what": "Contribution margin rose from {m_a} to {m_b} ({y_a} → {y_b}) while "
                "revenue per mile stayed flat ({rpm_a} → {rpm_b}).",
                "impact": "Lower fuel prices brought {fuel_part} of the {delta} gain in "
                "contribution ({share}). The company doesn't control this: if fuel prices go "
                "back to {y_a} levels, contribution falls by about {fuel_part} a year.",
                "action": "Link the fuel surcharge to the actual fuel price (an index-based "
                "surcharge) instead of a fixed amount, and look for gains the company controls: "
                "rates, lane mix and truck productivity.",
            },
            "vi": {
                "title": "Lợi nhuận tăng nhờ nhiên liệu rẻ đi, không nhờ vận hành tốt hơn",
                "what": "Biên đóng góp tăng từ {m_a} lên {m_b} ({y_a} → {y_b}) trong khi doanh "
                "thu mỗi dặm gần như không đổi ({rpm_a} → {rpm_b}).",
                "impact": "Giá nhiên liệu giảm mang lại {fuel_part} trong {delta} lợi nhuận đóng "
                "góp tăng thêm ({share}). Đây là yếu tố công ty không kiểm soát được: nếu giá "
                "nhiên liệu quay về mức năm {y_a}, lợi nhuận đóng góp giảm khoảng {fuel_part} "
                "mỗi năm.",
                "action": "Gắn phụ phí nhiên liệu với giá nhiên liệu thực tế (phụ phí thả nổi "
                "theo chỉ số giá) thay vì mức cố định; tìm nguồn tăng lợi nhuận công ty chủ động "
                "được: giá cước, cơ cấu tuyến, năng suất xe.",
            },
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
        "imbalance",
        "network",
        lambda x: (
            "act"
            if x["surplus_pct"] > t("surplus_act_pct")
            and x["balance_persistence"] >= t("persistent_corr")
            else "watch"
        ),
        _always("bad"),
        {
            "en": {
                "title": "{surplus_pct} of loads end where there is no return load",
                "what": "{surplus} loads end in cities that receive more loads than they send; "
                "{cities} of {n} cities are imbalanced by more than {th}. {only_in} receive "
                "loads but send none. The pattern repeats every year (correlation {pers}).",
                "impact": "After these deliveries the truck has nothing to carry back and drives "
                "empty to its next pickup: fuel, driver hours and wear with no revenue. The data "
                "doesn't record those empty miles, so their cost can't be put in dollars yet.",
                "action": "Find return loads in the cities that receive more than they send, "
                "starting with {only_in}: approach shippers there, or price return trips lower "
                "to fill them.",
            },
            "vi": {
                "title": "{surplus_pct} số lô kết thúc ở nơi không có hàng chiều về",
                "what": "{surplus} lô kết thúc ở các thành phố nhận hàng nhiều hơn gửi đi; "
                "{cities} trên {n} thành phố lệch quá {th}. {only_in} chỉ nhận hàng, không gửi "
                "lô nào. Tình trạng này lặp lại qua các năm (tương quan {pers}).",
                "impact": "Sau khi giao những lô này, xe không có hàng chở về và phải chạy rỗng "
                "đến điểm lấy hàng kế tiếp: tốn nhiên liệu, giờ tài xế và hao mòn xe mà không có "
                "doanh thu. Dữ liệu không ghi quãng chạy rỗng nên chưa quy được ra tiền.",
                "action": "Tìm nguồn hàng chiều về tại các thành phố nhận nhiều hơn gửi, bắt đầu "
                "từ {only_in}: tiếp cận chủ hàng tại đó, hoặc giảm giá cước chiều về để lấp đầy "
                "xe.",
            },
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
        "margin_fuel_corr",
        "profit",
        lambda x: "watch" if abs(x["margin_fuel_corr"]) >= t("persistent_corr") else None,
        _always("risk"),
        {
            "en": {
                "title": "Margin moves up and down with the fuel price",
                "what": "Month by month, cheaper fuel means a higher margin and dearer fuel a "
                "lower one (correlation {corr}, close to a perfect mirror image).",
                "impact": "The fuel surcharge customers pay doesn't change with the fuel price, "
                "so every change in fuel cost goes straight into profit.",
                "action": "Review the margin next to the fuel price every month, and review the "
                "surcharge terms in customer contracts.",
            },
            "vi": {
                "title": "Biên lợi nhuận lên xuống theo giá nhiên liệu",
                "what": "Theo từng tháng, nhiên liệu rẻ đi thì biên tăng, đắt lên thì biên giảm "
                "(tương quan {corr}, gần như ngược chiều hoàn toàn).",
                "impact": "Phụ phí nhiên liệu thu của khách không đổi theo giá nhiên liệu, nên "
                "mọi biến động chi phí nhiên liệu đi thẳng vào lợi nhuận.",
                "action": "Theo dõi biên cùng giá nhiên liệu hằng tháng và xem lại điều khoản phụ "
                "phí nhiên liệu trong hợp đồng với khách.",
            },
        },
        lambda x, f: {"corr": f.num(x["margin_fuel_corr"], 2)},
    ),
    Rule(
        "capacity",
        "fleet",
        lambda x: "watch" if x["trucks_owned"] > x["cap_max"] else "info",
        lambda level: "bad" if level == "watch" else "neutral",
        {
            "en": {
                "title": "The fleet is larger than demand needs",
                "what": "On {s1} of days at most {p95} trucks are working at once, on {s2} at most "
                "{p99}, and the busiest day needed {mx}. {in_use} trucks have run trips; the "
                "company owns {owned}.",
                "impact": "{spare} trucks were not needed even on the busiest day, yet they still "
                "cost money: {idle} trucks never ran a single trip and still took {idle_cost} in "
                "maintenance.",
                "action": "Review the trucks above peak need, starting with the {idle} that never "
                "ran: sell, transfer or stop servicing them, while keeping enough trucks for "
                "{s2} of days.",
            },
            "vi": {
                "title": "Đội xe lớn hơn nhu cầu thực tế",
                "what": "{s1} số ngày chỉ cần tối đa {p95} xe chạy cùng lúc, {s2} số ngày tối đa "
                "{p99} xe, ngày bận nhất cần {mx} xe. {in_use} xe từng chạy chuyến; công ty sở "
                "hữu {owned} xe.",
                "impact": "{spare} xe không cần đến kể cả vào ngày bận nhất nhưng vẫn phát sinh "
                "chi phí: {idle} xe chưa chạy chuyến nào mà vẫn tốn {idle_cost} bảo dưỡng.",
                "action": "Rà soát số xe vượt nhu cầu, bắt đầu từ {idle} xe chưa từng chạy: thanh "
                "lý, điều chuyển hoặc dừng bảo dưỡng định kỳ; vẫn giữ đủ xe cho {s2} số ngày.",
            },
        },
        lambda x, f: {
            "s1": f"{SERVICE_LEVELS[0]}%",
            "s2": f"{SERVICE_LEVELS[1]}%",
            "p95": f.int(x["cap_p95"]),
            "p99": f.int(x["cap_p99"]),
            "mx": x["cap_max"],
            "in_use": x["trucks_in_use"],
            "owned": x["trucks_owned"],
            "spare": x["trucks_owned"] - x["cap_max"],
            "idle": x["trucks_never_ran"],
            "idle_cost": _usd(f, x["never_ran_maintenance"]),
        },
        by_level={
            "info": {
                "en": {
                    "title": "Fleet size matches peak demand",
                    "impact": "No truck is spare even on the busiest day.",
                    "action": "",
                },
                "vi": {
                    "title": "Quy mô đội xe khớp với nhu cầu cao điểm",
                    "impact": "Không có xe dư kể cả vào ngày bận nhất.",
                    "action": "",
                },
            }
        },
    ),
    Rule(
        "fuel_gap",
        "fuel",
        lambda x: "watch" if (x["fuel_ratio_min"] - 1) * 100 > t("fuel_gap_pct") else None,
        _always("bad"),
        {
            "en": {
                "title": "More fuel is bought than trips record as used",
                "what": "Every year, gallons bought are {lo} to {hi} times the gallons recorded "
                "as burned on trips.",
                "impact": "Nobody can yet say where the difference goes, legitimate use outside "
                "trips or losses: until fuel cards are reconciled with trips, the two can't be "
                "told apart.",
                "action": "Reconcile fuel-card purchases with trips per truck and per month, and "
                "record the odometer at every fill-up.",
            },
            "vi": {
                "title": "Nhiên liệu mua vào nhiều hơn lượng ghi nhận dùng cho chuyến",
                "what": "Năm nào lượng nhiên liệu mua cũng bằng {lo} đến {hi} lần lượng ghi nhận "
                "tiêu thụ trên các chuyến.",
                "impact": "Chưa xác định được phần chênh lệch đi đâu, dùng hợp lý ngoài chuyến "
                "hay thất thoát: khi chưa đối soát thẻ nhiên liệu với chuyến thì không phân biệt "
                "được hai trường hợp này.",
                "action": "Đối soát giao dịch thẻ nhiên liệu với chuyến theo từng xe, từng tháng; "
                "ghi số đồng hồ quãng đường mỗi lần đổ nhiên liệu.",
            },
        },
        lambda x, f: {"lo": f.num(x["fuel_ratio_min"], 2), "hi": f.num(x["fuel_ratio_max"], 2)},
    ),
    Rule(
        "repositioning",
        "network",
        lambda x: "watch" if x["moved_pct"] > t("moved_watch_pct") else None,
        _always("bad"),
        {
            "en": {
                "title": "Next trips are not chained to where trucks finish",
                "what": "In {moved} of cases, a truck's next trip starts in a different city from "
                "where its previous trip ended. Picking next trips at random would give {random}: "
                "the data shows no sign of dispatch matching loads to where trucks already are.",
                "impact": "Almost every trip is preceded by a move to another city, usually "
                "empty. Those moves aren't recorded, so their time and fuel are hidden from cost "
                "reports and from the profit of each trip.",
                "action": "Record every move between trips (time, distance, reason), and assign "
                "next loads to trucks already in or near the pickup city; how many moves this "
                "saves is worked out in the optimization module.",
            },
            "vi": {
                "title": "Chuyến kế tiếp không được ghép với nơi xe vừa giao xong",
                "what": "Ở {moved} số trường hợp, chuyến kế tiếp của xe bắt đầu ở thành phố khác "
                "nơi chuyến trước kết thúc. Nếu giao chuyến hoàn toàn ngẫu nhiên, tỷ lệ này là "
                "{random}: dữ liệu không cho thấy việc điều phối ghép hàng theo vị trí xe.",
                "impact": "Gần như mọi chuyến đều phải điều xe sang thành phố khác trước, thường "
                "là chạy rỗng. Quãng di chuyển này không được ghi lại, nên thời gian và nhiên liệu "
                "bị ẩn khỏi báo cáo chi phí và lợi nhuận từng chuyến.",
                "action": "Ghi nhận mọi lần điều xe giữa hai chuyến (thời gian, quãng đường, lý "
                "do), và giao lô kế tiếp cho xe đang ở hoặc gần điểm lấy hàng; số lần điều xe "
                "tiết kiệm được sẽ tính ở module tối ưu.",
            },
        },
        lambda x, f: {"moved": _pp(f, x["moved_pct"]), "random": _pp(f, x["moved_random_pct"])},
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
        lambda level: "good" if level == "info" else "risk",
        {
            "en": {
                "title": "No dependence on any single customer",
                "what": "The largest customer brings {largest} of revenue, the top ten {top10}, "
                "and it takes {n80} of {n} customers to reach eighty percent of revenue "
                "(HHI {hhi}).",
                "impact": "Losing any one customer would cost at most {largest} of revenue. HHI "
                "is below {hhi_mod}, where concentration starts to matter.",
            },
            "vi": {
                "title": "Không phụ thuộc vào khách hàng nào",
                "what": "Khách lớn nhất chiếm {largest} doanh thu, mười khách lớn nhất {top10}, "
                "cần {n80} trên {n} khách mới đạt tám mươi phần trăm doanh thu (HHI {hhi}).",
                "impact": "Mất một khách bất kỳ chỉ ảnh hưởng tối đa {largest} doanh thu. HHI "
                "dưới {hhi_mod}, mức bắt đầu đáng lo về tập trung.",
            },
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
        by_level={
            level: {
                "en": {
                    "title": "Revenue depends on a few customers",
                    "impact": "Losing the largest customer would cost {largest} of revenue. HHI "
                    "{hhi}: moderate from {hhi_mod}, high from {hhi_high}.",
                    "action": "Spread revenue over more customers, and secure the largest "
                    "accounts with longer contracts.",
                },
                "vi": {
                    "title": "Doanh thu phụ thuộc vào một số ít khách hàng",
                    "impact": "Mất khách lớn nhất sẽ mất {largest} doanh thu. HHI {hhi}: mức vừa "
                    "từ {hhi_mod}, cao từ {hhi_high}.",
                    "action": "Mở rộng tệp khách để giảm phụ thuộc, giữ chân các khách lớn bằng "
                    "hợp đồng dài hạn.",
                },
            }
            for level in ("watch", "act")
        },
    ),
    Rule(
        "volume_flat",
        "profit",
        lambda x: "info" if abs(x["trips_change_pct"]) < t("flat_change_pct") else None,
        _always("neutral"),
        {
            "en": {
                "title": "Volume is flat",
                "what": "{t_a} trips in {y_a}, {t_b} in {y_b} ({chg}).",
                "impact": "Profit growth did not come from more business. Truck demand is stable, "
                "so capacity can be planned on today's level.",
            },
            "vi": {
                "title": "Sản lượng đi ngang",
                "what": "{t_a} chuyến năm {y_a}, {t_b} chuyến năm {y_b} ({chg}).",
                "impact": "Lợi nhuận tăng không đến từ tăng sản lượng. Nhu cầu xe ổn định nên có "
                "thể lập kế hoạch năng lực theo mức hiện tại.",
            },
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
        _always("neutral"),
        {
            "en": {
                "title": "Customer segments earn the same margin",
                "what": "Every customer segment earns a margin between {lo} and {hi}.",
                "impact": "To improve profit, look at lanes and rates rather than contract type.",
            },
            "vi": {
                "title": "Các phân khúc khách hàng có biên như nhau",
                "what": "Mọi phân khúc khách hàng đều có biên từ {lo} đến {hi}.",
                "impact": "Muốn cải thiện lợi nhuận nên xét theo tuyến và giá cước, không theo "
                "loại hợp đồng.",
            },
        },
        lambda x, f: {"lo": _pp(f, x["segment_margin_min"]), "hi": _pp(f, x["segment_margin_max"])},
    ),
    Rule(
        "state_leader",
        "profit",
        lambda x: "info",
        _always("neutral"),
        {
            "en": {
                "title": "{state} is the largest profit contributor",
                "what": "{state} brings {amount} ({share} of contribution). Margin by origin "
                "state ranges from {lo} to {hi}.",
                "impact": "Margins differ by {gap} points between states: low-margin states are "
                "the first place to review rates or costs.",
            },
            "vi": {
                "title": "{state} đóng góp lợi nhuận lớn nhất",
                "what": "{state} mang về {amount} ({share} tổng đóng góp). Biên theo bang đi từ "
                "{lo} đến {hi}.",
                "impact": "Biên giữa các bang chênh nhau {gap} điểm: các bang biên thấp là nơi "
                "nên xem lại giá cước hoặc chi phí trước.",
            },
        },
        lambda x, f: {
            "state": x["top_state"],
            "amount": _usd(f, x["top_state_contribution"]),
            "share": _pp(f, x["top_state_share"]),
            "lo": _pp(f, x["state_margin_min"]),
            "hi": _pp(f, x["state_margin_max"]),
            "gap": f.num(x["state_margin_max"] - x["state_margin_min"], 1),
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
        _always("neutral"),
        {
            "en": {
                "title": "Truck demand varies at random from day to day, not by season",
                "what": "On an average day {lo} to {hi} trucks are working, the same every year. "
                "Busy days come at random: no quarter is busier year after year.",
                "impact": "Trucks can't be planned season by season. Size the fleet by how many "
                "days it must cover, for example enough trucks on {s1} of days, rather than by "
                "calendar.",
            },
            "vi": {
                "title": "Nhu cầu xe biến động ngẫu nhiên theo ngày, không theo mùa vụ",
                "what": "Bình quân mỗi ngày có {lo} đến {hi} xe hoạt động, ổn định qua các năm. "
                "Ngày cao điểm đến ngẫu nhiên: không có quý nào năm nào cũng bận hơn.",
                "impact": "Không thể chuẩn bị xe theo mùa cao điểm. Quy mô đội xe nên tính theo "
                "số ngày cần đảm bảo đủ xe, ví dụ đủ cho {s1} số ngày, thay vì theo lịch.",
            },
        },
        lambda x, f: {
            "lo": f.num(x["yearly_mean_min"], 1),
            "hi": f.num(x["yearly_mean_max"], 1),
            "s1": f"{SERVICE_LEVELS[0]}%",
        },
    ),
    Rule(
        "lane_matrix",
        "network",
        lambda x: "info",
        _always("neutral"),
        {
            "en": {
                "title": "Lane portfolio: {protect} core lanes, {reprice} to renegotiate, {exit} "
                "low-margin lanes to review",
                "what": "Lanes are split {grid} by volume and margin: {protect} lanes with high "
                "volume and high margin, {reprice} with high volume and low margin, {exit} with "
                "low volume and low margin. Even the lowest-margin lane earns {lo}, so every lane "
                "is profitable at contribution level.",
                "impact": "Driver pay and overhead are not in the data, so there is no ground to "
                "drop a lane yet. Renegotiate first where trips are many and margin is low: a "
                "rate change there reaches the most trips.",
            },
            "vi": {
                "title": "Danh mục tuyến: {protect} tuyến chủ lực, {reprice} tuyến cần đàm phán "
                "lại giá, {exit} tuyến biên thấp cần rà soát",
                "what": "Tuyến được chia {grid} theo sản lượng và biên: {protect} tuyến sản lượng "
                "cao biên cao, {reprice} tuyến sản lượng cao biên thấp, {exit} tuyến sản lượng "
                "thấp biên thấp. Tuyến biên thấp nhất vẫn đạt {lo}, tức mọi tuyến đều có lãi "
                "đóng góp.",
                "impact": "Dữ liệu chưa có lương tài xế và chi phí chung nên chưa đủ căn cứ để "
                "ngừng tuyến nào. Ưu tiên đàm phán giá ở tuyến đông chuyến nhưng biên thấp: điều "
                "chỉnh giá ở đó tác động đến nhiều chuyến nhất.",
            },
        },
        lambda x, f: {
            "protect": x["lanes_protect"],
            "reprice": x["lanes_reprice"],
            "exit": x["lanes_review_low"],
            "lo": _pp(f, x["lane_margin_min"]),
            "grid": f"{MATRIX_TIERS}×{MATRIX_TIERS}",
        },
    ),
]


def generate(facts: dict, lang: str) -> list[dict]:
    """Every finding that applies, with its parts in `lang`.

    `text` joins the parts into one paragraph for the CLI and plain documents.
    """
    f = NumberFormatter(lang)
    out = []
    for rule in RULES:
        level = rule.level(facts)
        if level is None:
            continue
        parts = rule.templates[lang] | rule.by_level.get(level, {}).get(lang, {})
        values = rule.values(facts, f)
        text = {k: v.format(**values) for k, v in parts.items() if v}
        tone = rule.tone(level)
        out.append(
            {
                "id": rule.id,
                "topic": rule.topic,
                "topic_label": TOPICS[lang][rule.topic],
                "level": level,
                "level_label": LEVELS[lang][level],
                "tone": tone,
                "tone_label": TONES[lang][tone],
                "title": text["title"],
                "what": text["what"],
                "impact": text["impact"],
                "action": text.get("action"),
                "text": " ".join(
                    [text["title"] + "."]
                    + [text[k] for k in ("what", "impact", "action") if k in text]
                ),
            }
        )
    return out
