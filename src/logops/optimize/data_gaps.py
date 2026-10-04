"""Data gaps → process improvements: measured cost of not fixing each gap vs the cost of fixing.

"Cost of not doing" is measured from the warehouse. Implementation costs for devices come from
cited public sources (SOURCES) and are indicative only; tier-1 measures are process or
configuration changes in existing systems, so no external price is claimed for them.
"""

from dataclasses import dataclass

import duckdb

from logops.analysis.operations import repositioning
from logops.optimize.lateness import late_share, persistence

SOURCES = {
    "telematics": (
        "GPS Insight, “How Much Does Telematics Cost”: “$20 – $45 per vehicle per month for "
        "software and connectivity, plus $100–$500 in upfront hardware per vehicle”",
        "https://www.gpsinsight.com/blog/what-is-the-cost-of-telematics/",
    ),
    "fuel_misuse": (
        "Automotive Fleet, citing Shell Fleet Solutions: “At a minimum, we have seen 2-5% of fuel "
        "spend lost to misuse every year”",
        "https://www.automotive-fleet.com/articles/fuel-fraud-prevention-strategies-reducing-costs-and-risks-for-fleets",
    ),
}
TELEMATICS_MONTHLY = (20.0, 45.0)  # USD per vehicle per month (SOURCES["telematics"])
TELEMATICS_HARDWARE = (100.0, 500.0)  # USD per vehicle, one-off (SOURCES["telematics"])
FUEL_MISUSE_SHARE = (0.02, 0.05)  # share of fuel spend (SOURCES["fuel_misuse"])
HARDWARE_LIFE_YEARS = 3  # hardware cost spread over 3 years to compare with annual figures


@dataclass(frozen=True)
class Measures:
    years: float
    trucks_in_use: int
    fuel_spend_per_year: float
    gallons_purchased: float
    gallons_burned: float
    avg_price: float
    unattributable_fuel_per_year: float
    deliveries_per_year: float
    deliveries_outside_window_per_year: float
    detention_hours_per_year: float
    contribution_margin_pct: float
    weakest_lane_break_even_driver_cost: float
    moved_pct: float
    moved_random_pct: float
    late_share_pct: float
    late_persistence_max: float

    @property
    def unreconciled_gallons(self) -> float:
        return self.gallons_purchased - self.gallons_burned

    @property
    def unreconciled_value_per_year(self) -> float:
        return self.unreconciled_gallons * self.avg_price / self.years

    @property
    def misuse_benchmark_per_year(self) -> tuple[float, float]:
        return tuple(s * self.fuel_spend_per_year for s in FUEL_MISUSE_SHARE)

    @property
    def telematics_cost_per_year(self) -> tuple[float, float]:
        """Subscription + hardware spread over its life, for the trucks in use."""
        return tuple(
            self.trucks_in_use * (12 * m + h / HARDWARE_LIFE_YEARS)
            for m, h in zip(TELEMATICS_MONTHLY, TELEMATICS_HARDWARE, strict=True)
        )

    @property
    def telematics_break_even_share(self) -> float:
        """Share of fuel spend telematics must save to pay for itself (high cost estimate)."""
        return self.telematics_cost_per_year[1] / self.fuel_spend_per_year


def _fleet_margin(con) -> float:
    """The fleet contribution margin as defined by the KPI layer (unattributed costs included)."""
    from logops.metrics.kpis import FLEET, kpi

    start, end = con.execute(
        "SELECT min(dispatch_date), (SELECT max(purchase_date)::DATE FROM fuel_purchases) "
        "FROM trips"
    ).fetchone()
    (row,) = [r for r in kpi(con, start, end).iter_rows(named=True) if r["group"] == FLEET]
    return row["contribution_margin_pct"]


def measure(con: duckdb.DuckDBPyConnection, weakest_break_even: float) -> Measures:
    days = con.execute(
        "SELECT datediff('day', min(dispatch_date), max(dispatch_date)) + 1 FROM trips"
    ).fetchone()[0]
    years = days / 365.25
    first, last = con.execute("SELECT min(dispatch_date), max(dispatch_date) FROM trips").fetchone()
    moves = repositioning(con, first, last)
    one = lambda sql: con.execute(sql).fetchone()[0]  # noqa: E731
    return Measures(
        years=years,
        trucks_in_use=one("SELECT count(DISTINCT truck_id) FROM trips WHERE truck_id IS NOT NULL"),
        fuel_spend_per_year=one("SELECT sum(total_cost) FROM fuel_purchases") / years,
        gallons_purchased=one("SELECT sum(gallons) FROM fuel_purchases"),
        gallons_burned=one("SELECT sum(fuel_gallons_used) FROM trips"),
        avg_price=one("SELECT sum(total_cost) / sum(gallons) FROM fuel_purchases"),
        unattributable_fuel_per_year=one(
            "SELECT sum(total_cost) FROM fuel_purchases WHERE driver_id IS NULL OR truck_id IS NULL"
        )
        / years,
        deliveries_per_year=one(
            "SELECT count(*) FROM delivery_events WHERE event_type = 'Delivery'"
        )
        / years,
        deliveries_outside_window_per_year=one(
            "SELECT count(*) FROM delivery_events "
            "WHERE event_type = 'Delivery' AND NOT on_time_flag"
        )
        / years,
        detention_hours_per_year=one("SELECT sum(detention_minutes) / 60 FROM delivery_events")
        / years,
        contribution_margin_pct=_fleet_margin(con),
        weakest_lane_break_even_driver_cost=weakest_break_even,
        moved_pct=moves["moved_pct"],
        moved_random_pct=moves["random_pct"],
        late_share_pct=late_share(con, first, last),
        late_persistence_max=persistence(con, first, last)["persistence"].max(),
    )


# Gap catalog. Each gap: what's missing, what it blocks, tier-1 (process/configuration) and
# tier-2 (device/integration) measures, and which Measures fields quantify it.
GAPS = [
    {
        "id": "fuel_reconciliation",
        "priority": 1,
        "uses_telematics": True,
        "en": {
            "gap": "Fuel bought is not reconciled with fuel burned",
            "evidence": "{unreconciled_gallons_m} M gallons more bought than burned in 3 years "
            "(ratio 1.29, similar on every truck)",
            "not_doing": "{unreconciled_value} per year of fuel purchases unexplained. Industry "
            "benchmark for card misuse: 2–5% of fuel spend = {misuse_low}–{misuse_high} per year",
            "tier1": "Monthly purchased-vs-burned report per truck (already computed by this "
            "project: the fuel bought vs burned KPI); investigate trucks above a threshold; "
            "require truck ID, driver ID and odometer at every card swipe",
            "tier2": "Telematics fuel-level and location matched to each card transaction",
        },
        "vi": {
            "gap": "Nhiên liệu mua chưa được đối soát với nhiên liệu tiêu thụ",
            "evidence": "Mua nhiều hơn tiêu thụ {unreconciled_gallons_m} triệu gallon trong 3 năm "
            "(tỷ lệ 1,29, như nhau ở mọi xe)",
            "not_doing": "{unreconciled_value} mỗi năm tiền nhiên liệu chưa giải thích được. Chuẩn "
            "ngành về lạm dụng thẻ: 2–5% chi phí nhiên liệu = {misuse_low}–{misuse_high} mỗi năm",
            "tier1": "Báo cáo hằng tháng gallon mua so với tiêu thụ theo từng xe (dự án đã tính "
            "sẵn: KPI tỷ lệ nhiên liệu mua / tiêu thụ); điều tra xe vượt ngưỡng; bắt buộc nhập mã "
            "xe, mã tài xế và số đồng hồ km mỗi lần quẹt thẻ",
            "tier2": "Telematics đo mức nhiên liệu và vị trí, khớp với từng giao dịch thẻ",
        },
    },
    {
        "id": "repositioning",
        "priority": 2,
        "uses_telematics": True,
        "en": {
            "gap": "Moves between trips are not recorded",
            "evidence": "{moved} of trips start in another city than where the truck stood; random "
            "assignment would give {moved_random}: dispatch doesn't use where trucks are",
            "not_doing": "Empty running can't be measured or reduced, and its fuel and driver time "
            "are hidden in the cost of loaded trips",
            "tier1": "Record every move between trips in the TMS (from, to, time, reason) and show "
            "dispatchers which trucks are already in or near each pickup city",
            "tier2": "GPS position and distance per move from telematics (same device as row 1)",
        },
        "vi": {
            "gap": "Chuyến điều xe giữa hai chuyến không được ghi nhận",
            "evidence": "{moved} số chuyến bắt đầu ở thành phố khác nơi xe đang đứng; giao chuyến "
            "ngẫu nhiên cũng ra {moved_random}: điều phối chưa dùng vị trí xe",
            "not_doing": "Không đo và không giảm được chạy rỗng; nhiên liệu và giờ tài xế của nó "
            "bị lẫn vào chi phí các chuyến có hàng",
            "tier1": "Ghi mọi lần điều xe giữa hai chuyến trên TMS (đi, đến, thời gian, lý do) và "
            "cho điều phối viên thấy xe nào đang ở hoặc gần thành phố lấy hàng",
            "tier2": "Vị trí GPS và quãng đường mỗi lần điều xe từ telematics (dùng chung thiết bị "
            "ở dòng 1)",
        },
    },
    {
        "id": "missing_ids",
        "priority": 3,
        "uses_telematics": False,
        "en": {
            "gap": "Driver and truck IDs missing on ~2% of trips and fuel purchases",
            "evidence": "Missing at random; 0 rows recoverable from other tables",
            "not_doing": "{unattributable_fuel} per year of fuel spend can't be assigned to a "
            "driver or truck, so rankings and accountability are incomplete",
            "tier1": "Make driver and truck ID mandatory fields in dispatch and on fuel cards "
            "(system validation: no ID, no dispatch)",
            "tier2": "Not needed",
        },
        "vi": {
            "gap": "Thiếu mã tài xế và mã xe ở khoảng 2% chuyến và phiếu nhiên liệu",
            "evidence": "Thiếu ngẫu nhiên; khôi phục từ bảng khác được 0 dòng",
            "not_doing": "{unattributable_fuel} mỗi năm chi phí nhiên liệu không gán được cho tài "
            "xế hay xe, nên xếp hạng và trách nhiệm không đầy đủ",
            "tier1": "Bắt buộc nhập mã tài xế và mã xe khi điều phối và trên thẻ nhiên liệu (hệ "
            "thống chặn: không có mã thì không điều phối)",
            "tier2": "Không cần",
        },
    },
    {
        "id": "driver_cost",
        "priority": 4,
        "uses_telematics": False,
        "en": {
            "gap": "No driver pay or overhead in the data",
            "evidence": "Contribution margin {margin} is before driver pay",
            "not_doing": "Lane profitability can't be confirmed: the weakest lane loses money if "
            "driver cost exceeds {break_even} per mile, and that can't be checked",
            "tier1": "Monthly export of driver pay (per driver, per month) from payroll into the "
            "warehouse",
            "tier2": "Not needed",
        },
        "vi": {
            "gap": "Dữ liệu không có lương tài xế và chi phí chung",
            "evidence": "Biên đóng góp {margin} là trước lương tài xế",
            "not_doing": "Không xác nhận được tuyến lời hay lỗ: tuyến yếu nhất lỗ nếu chi phí tài "
            "xế vượt {break_even}/dặm, và hiện không kiểm tra được",
            "tier1": "Xuất dữ liệu lương tài xế (theo tài xế, theo tháng) từ hệ thống lương vào "
            "kho dữ liệu hằng tháng",
            "tier2": "Không cần",
        },
    },
    {
        "id": "delay_reasons",
        "priority": 5,
        "uses_telematics": False,
        "en": {
            "gap": "No reason recorded when a delivery misses its window",
            "evidence": "{late_share} of deliveries are more than 2 h late, but the rate doesn't "
            "repeat by city, customer, appointment hour, lane or driver (correlation between "
            "periods at most {late_corr}, a signal needs 0.7): the cause isn't in the data",
            "not_doing": "{outside_window} deliveries per year outside the ±2 h window "
            "({outside_share}) with no way to diagnose why",
            "tier1": "A short reason-code list in the driver app or TMS at each delivery (traffic, "
            "waiting at dock, paperwork, late pickup, other)",
            "tier2": "Geofenced arrival/departure times from telematics",
        },
        "vi": {
            "gap": "Không ghi lý do khi giao hàng lệch khung giờ",
            "evidence": "{late_share} lần giao trễ quá 2 giờ, nhưng tỷ lệ không lặp lại theo thành "
            "phố, khách hàng, giờ hẹn, tuyến hay tài xế (tương quan giữa hai giai đoạn cao nhất "
            "{late_corr}, cần 0,7 mới là tín hiệu): nguyên nhân không có trong dữ liệu",
            "not_doing": "{outside_window} lần giao mỗi năm lệch khung ±2 giờ ({outside_share}) mà "
            "không chẩn đoán được nguyên nhân",
            "tier1": "Danh sách mã lý do ngắn trên ứng dụng tài xế hoặc TMS ở mỗi lần giao (kẹt "
            "xe, chờ cửa, giấy tờ, lấy hàng trễ, khác)",
            "tier2": "Giờ đến/đi theo hàng rào định vị (geofence) từ telematics",
        },
    },
    {
        "id": "location_master_data",
        "priority": 6,
        "uses_telematics": True,
        "en": {
            "gap": "Facility and state fields unreliable",
            "evidence": "The facility code matches the lane 3.4% of the time; state wrong on 95% "
            "of fuel purchases",
            "not_doing": "{detention_hours} detention hours per year that can't be attributed to a "
            "facility; no analysis by facility or state",
            "tier1": "Facility and city→state master lists; validate entries against them",
            "tier2": "Geofenced check-in at facilities (same telematics device as row 1)",
        },
        "vi": {
            "gap": "Trường kho và bang không đáng tin",
            "evidence": "Mã kho khớp với tuyến ở 3,4%; bang sai ở 95% phiếu nhiên liệu",
            "not_doing": "{detention_hours} giờ chờ mỗi năm không gán được cho kho nào; không phân "
            "tích được theo kho hay theo bang",
            "tier1": "Danh mục kho và danh mục thành phố → bang chuẩn; kiểm tra dữ liệu nhập theo "
            "danh mục",
            "tier2": "Check-in tại kho bằng hàng rào định vị (dùng chung thiết bị telematics ở "
            "dòng 1)",
        },
    },
    {
        "id": "idle_time",
        "priority": 7,
        "uses_telematics": True,
        "en": {
            "gap": "Idle time is noise",
            "evidence": "Correlation ≈ 0 with trip duration, distance and fuel",
            "not_doing": "Idling waste can't be measured at all",
            "tier1": "None: idle time needs engine data",
            "tier2": "Engine idle hours from telematics (same device as row 1)",
        },
        "vi": {
            "gap": "Thời gian chạy không tải là nhiễu",
            "evidence": "Tương quan ≈ 0 với thời gian chuyến, quãng đường và nhiên liệu",
            "not_doing": "Hoàn toàn không đo được lãng phí do nổ máy chờ",
            "tier1": "Không có: cần dữ liệu từ động cơ",
            "tier2": "Giờ nổ máy chờ từ telematics (dùng chung thiết bị ở dòng 1)",
        },
    },
]
