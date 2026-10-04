"""Every label shown on the dashboard, in Vietnamese and English.

Wording follows logistics practice: contribution profit, on-time delivery (OTD), fleet utilization.
Database names (tables, columns, rule ids) never reach the screen: they are mapped to plain names
here (DQ_TABLES, DQ_COLUMNS, DQ_RULES).
"""

STATES = {  # US state codes → names (same in both languages)
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}  # fmt: skip

DQ_TABLES = {
    "vi": {
        "customers": "Khách hàng",
        "routes": "Tuyến",
        "facilities": "Kho, điểm giao nhận",
        "drivers": "Tài xế",
        "trucks": "Xe tải",
        "trailers": "Rơ-moóc",
        "loads": "Lô hàng",
        "trips": "Chuyến xe",
        "delivery_events": "Sự kiện lấy/giao hàng",
        "fuel_purchases": "Giao dịch mua nhiên liệu",
        "maintenance_records": "Phiếu bảo dưỡng",
        "safety_incidents": "Sự cố an toàn",
        "driver_monthly_metrics": "Chỉ số tài xế theo tháng",
        "truck_utilization_metrics": "Chỉ số sử dụng xe theo tháng",
    },
    "en": {
        "customers": "Customers",
        "routes": "Lanes",
        "facilities": "Facilities",
        "drivers": "Drivers",
        "trucks": "Trucks",
        "trailers": "Trailers",
        "loads": "Loads",
        "trips": "Trips",
        "delivery_events": "Pickup/delivery events",
        "fuel_purchases": "Fuel purchases",
        "maintenance_records": "Maintenance records",
        "safety_incidents": "Safety incidents",
        "driver_monthly_metrics": "Monthly driver metrics",
        "truck_utilization_metrics": "Monthly truck utilization",
    },
}
DQ_COLUMNS = {
    "vi": {
        "location_state": "bang",
        "facility_id": "mã kho",
        "driver_id": "mã tài xế",
        "truck_id": "mã xe",
        "trailer_id": "mã rơ-moóc",
        "actual_datetime": "thời điểm thực tế",
        "scheduled_datetime": "thời điểm hẹn",
        "utilization_rate": "hệ số sử dụng",
    },
    "en": {
        "location_state": "state",
        "facility_id": "facility code",
        "driver_id": "driver code",
        "truck_id": "truck code",
        "trailer_id": "trailer code",
        "actual_datetime": "actual time",
        "scheduled_datetime": "appointment time",
        "utilization_rate": "utilization rate",
    },
}
DQ_RULES = {  # {col} = the column's plain name
    "vi": {
        "geo_mismatch": "{col} không khớp với vị trí",
        "fk_missing": "{col} không có trong danh mục",
        "idle_exceeds_duration": "giờ chạy không tải vượt thời gian chuyến",
        "time_order": "{col} sai thứ tự thời gian",
        "range": "{col} ngoài khoảng hợp lệ",
        "pk_duplicate": "{col} bị trùng",
        "not_null": "{col} bị trống",
    },
    "en": {
        "geo_mismatch": "{col} doesn't match the location",
        "fk_missing": "{col} not in the master list",
        "idle_exceeds_duration": "idle hours longer than the trip",
        "time_order": "{col} out of time order",
        "range": "{col} out of the valid range",
        "pk_duplicate": "duplicate {col}",
        "not_null": "{col} missing",
    },
}

T = {
    "vi": {
        "app_title": "Logistics Ops · Dashboard điều hành",
        "lang": "Ngôn ngữ",
        "period": "Khoảng thời gian",
        "from": "Từ ngày",
        "to": "Đến ngày",
        "apply": "Áp dụng",
        "bad_range": "Ngày bắt đầu phải trước ngày kết thúc.",
        "applied": "Đang xem: {a} – {b}",
        "date_format": "DD/MM/YYYY",
        "loading": "Đang tải số liệu…",
        "locked": "Không mở được kho dữ liệu. Hãy ngắt kết nối DBeaver hoặc chương trình khác đang "
        "mở file `warehouse.duckdb`, rồi tải lại trang.",
        "no_warehouse": "Chưa có kho dữ liệu. Chạy `uv run logops build` trước.",
        "source_note": "Lợi nhuận trên dashboard là lợi nhuận đóng góp: chưa trừ lương tài xế và "
        "chi phí chung vì dữ liệu không có.",
        # pages
        "p_overview": "Tổng quan điều hành",
        "p_profit": "Kết quả kinh doanh",
        "p_regions": "Khách hàng & thị trường",
        "p_network": "Hiệu quả tuyến vận tải",
        "p_service": "Chất lượng giao hàng",
        "p_fleet": "Năng lực & khai thác đội xe",
        "p_fuel": "Quản lý nhiên liệu",
        "p_data": "Chất lượng dữ liệu & định nghĩa KPI",
        "d_overview": "Kết quả tài chính, chất lượng giao hàng, hiệu suất đội xe và các vấn đề cần "
        "xử lý.",
        "d_profit": "Doanh thu, chi phí và lợi nhuận đóng góp theo kỳ; nguyên nhân lợi nhuận thay "
        "đổi.",
        "d_regions": "Lợi nhuận theo bang, phân khúc khách hàng, loại hàng và mức độ phụ thuộc vào "
        "khách hàng lớn.",
        "d_network": "Đánh giá hiệu quả từng tuyến và độ cân đối hàng chiều đi – chiều về.",
        "d_service": "Tỷ lệ giao đúng hẹn theo các chuẩn đo, độ lệch thời điểm giao và thời gian "
        "chờ.",
        "d_fleet": "Số xe cần mỗi ngày so với quy mô đội xe, năng suất xe và các xe không được "
        "khai thác.",
        "d_fuel": "Lượng nhiên liệu mua vào so với tiêu thụ, giá và chi phí nhiên liệu.",
        "d_data": "Mức độ tin cậy của dữ liệu nguồn và định nghĩa của từng chỉ số.",
        # common
        "revenue": "Doanh thu",
        "contribution": "Lợi nhuận đóng góp",
        "margin": "Biên đóng góp",
        "fuel": "Chi phí nhiên liệu",
        "maintenance": "Chi phí bảo dưỡng",
        "claims": "Chi phí bồi thường sự cố",
        "trips": "Số chuyến",
        "year": "Năm",
        "month": "Tháng",
        "quarter": "Quý",
        "vs_last_year": "so với năm trước",
        "vs_year": "so với {y}",
        "points": "điểm %",
        "minutes": "phút",
        "hours": "giờ",
        "unit": "Đơn vị: {u}",
        "explain": "Diễn giải:",
        "row_no": "STT",
        "filter_all": "Tất cả",
        "rows_shown": "Hiển thị {n} / {total} dòng",
        "u_musd": "tr USD",
        "u_usd": "USD",
        "u_pct": "%",
        "u_trucks": "xe",
        "u_days": "ngày",
        "u_loads": "lô hàng",
        "u_deliveries": "lần giao",
        "u_gallons": "gallon",
        "u_usd_gallon": "USD/gallon",
        "u_times": "lần",
        "u_rows": "dòng dữ liệu",
        "u_minutes": "phút",
        "u_miles": "dặm",
        # overview
        "k_revenue": "Doanh thu",
        "k_contribution": "Lợi nhuận đóng góp",
        "k_op_cost": "Chi phí vận hành",
        "n_op_cost": "Nhiên liệu + bảo dưỡng + bồi thường sự cố",
        "k_margin": "Biên đóng góp",
        "k_cost_mile": "Chi phí vận hành mỗi dặm",
        "k_otd": "Giao hàng đúng hẹn (OTD)",
        "k_detention": "Thời gian chờ bình quân",
        "k_trips": "Chuyến hoàn thành",
        "k_fleet_use": "Hiệu suất sử dụng đội xe",
        "n_revenue": "Cước vận chuyển + phụ phí nhiên liệu + phụ phí khác",
        "n_contribution": "Doanh thu trừ chi phí nhiên liệu, bảo dưỡng, bồi thường sự cố",
        "n_margin": "Lợi nhuận đóng góp ÷ doanh thu",
        "n_cost_mile": "Chi phí nhiên liệu, bảo dưỡng, bồi thường ÷ tổng số dặm",
        "n_otd": "Trong ±2 giờ so với giờ hẹn · tính theo ngày hẹn: {day}",
        "n_detention": "Số phút xe chờ mỗi lần lấy hoặc giao hàng",
        "n_trips": "Mỗi chuyến chở một lô hàng",
        "n_fleet_use": "Bình quân {busy} trên {owned} xe có chuyến mỗi ngày",
        "view_period": "Kỳ xem",
        "all_period": "Cả giai đoạn",
        "period_only": "Số liệu từ {a} đến {b}.",
        "period_vs": "Số liệu từ {a} đến {b}, so với năm {y}.",
        "g_finance": "Tài chính",
        "g_operations": "Vận hành & dịch vụ",
        "key_points": "Điểm chính",
        "tone_legend": "Màu viền thể hiện đánh giá:",
        "findings_scope": "Nhận xét tính trên toàn khoảng thời gian chọn ở thanh bên.",
        "margin_vs_fuel": "Biên đóng góp và giá nhiên liệu theo tháng",
        "u_margin_fuel": "% (trên) · USD/gallon (dưới)",
        "margin_vs_fuel_note": "Biên đóng góp = (doanh thu − nhiên liệu − bảo dưỡng − bồi thường) "
        "÷ doanh thu, chưa trừ lương tài xế và chi phí chung. Hai biểu đồ chung trục thời gian: "
        "mỗi lần giá nhiên liệu giảm thì biên tăng lên (tương quan {corr}), vì phụ phí nhiên liệu "
        "thu của khách không đổi.",
        "monthly_margin": "Biên đóng góp (%)",
        "fuel_price": "Giá nhiên liệu bình quân (USD/gallon)",
        # profit
        "choose_period": "Kỳ báo cáo",
        "where_revenue_goes": "Cơ cấu doanh thu: chi phí và lợi nhuận đóng góp",
        "where_revenue_goes_note": "Mỗi cột là doanh thu của một kỳ, chia thành chi phí nhiên "
        "liệu, bảo dưỡng, bồi thường sự cố và phần còn lại là lợi nhuận đóng góp. Cột cao hơn là "
        "doanh thu lớn hơn; phần xanh lớn hơn là lợi nhuận tốt hơn.",
        "bridge": "Cầu lợi nhuận: vì sao lợi nhuận đóng góp thay đổi",
        "bridge_note": "Cột xám đầu và cuối là lợi nhuận đóng góp của hai năm. Mỗi cột ở giữa là "
        "phần thay đổi do một yếu tố: xanh là làm tăng lợi nhuận, đỏ là làm giảm. Các cột ở giữa "
        "cộng lại đúng bằng chênh lệch giữa hai năm.",
        "bridge_from": "Từ năm",
        "bridge_to": "Đến năm",
        "b_start": "Lợi nhuận {y}",
        "b_end": "Lợi nhuận {y}",
        "b_volume": "Sản lượng",
        "b_rate": "Giá cước mỗi chuyến",
        "b_fuel_price": "Giá nhiên liệu",
        "b_fuel_consumption": "Nhiên liệu tiêu hao mỗi chuyến",
        "b_maintenance": "Chi phí bảo dưỡng",
        "b_claims": "Chi phí bồi thường",
        "ytd": "Lợi nhuận đóng góp lũy kế từ đầu năm",
        "ytd_note": "Mỗi đường là một năm, cộng dồn lợi nhuận từ tháng 1. Đường nằm trên là năm có "
        "lợi nhuận tốt hơn tại cùng thời điểm.",
        "units": "Hiệu quả trên mỗi đơn vị",
        "u_rev_mile": "Doanh thu mỗi dặm",
        "u_contrib_mile": "Lợi nhuận đóng góp mỗi dặm",
        "u_rev_trip": "Doanh thu mỗi chuyến",
        "u_contrib_truck_week": "Lợi nhuận đóng góp mỗi xe mỗi tuần",
        "pnl_table": "Bảng kết quả kinh doanh theo kỳ",
        "pnl_cols": {
            "period": "Kỳ",
            "year": "Năm",
            "revenue": "Doanh thu (tr USD)",
            "fuel_cost": "Chi phí nhiên liệu (tr USD)",
            "maintenance_cost": "Chi phí bảo dưỡng (tr USD)",
            "claims": "Chi phí bồi thường (tr USD)",
            "contribution": "Lợi nhuận đóng góp (tr USD)",
            "margin_pct": "Biên đóng góp (%)",
            "contribution_vs_prev_pct": "Lợi nhuận so với kỳ trước (%)",
            "contribution_yoy_pct": "Lợi nhuận so với cùng kỳ năm trước (%)",
        },
        # regions
        "state_side": "Theo bang",
        "origin": "Bang xuất phát",
        "destination": "Bang nhận hàng",
        "state_map": "Lợi nhuận đóng góp theo bang",
        "state_map_note": "Màu càng đậm, bang càng mang về nhiều lợi nhuận đóng góp. Rê chuột lên "
        "từng bang để xem số tiền.",
        "margin_by_state": "Biên đóng góp theo bang",
        "state_margin_note": "Biên đóng góp = lợi nhuận đóng góp ÷ doanh thu của các chuyến thuộc "
        "bang. Cao nhất {hi_state} ({hi}), thấp nhất {lo_state} ({lo}). Bang biên thấp là nơi giá "
        "cước thấp hoặc chi phí cao so với mặt bằng chung: nên xem lại giá trước.",
        "segments": "Doanh thu theo phân khúc khách hàng",
        "load_types": "Doanh thu theo loại hàng",
        "pareto": "Mức độ tập trung khách hàng",
        "pareto_chart": "Đường Pareto: doanh thu lũy kế theo số khách hàng",
        "pareto_note": "Khách hàng xếp từ lớn đến nhỏ. Đường càng gần đường chéo, doanh thu càng "
        "phân tán đều, ít phụ thuộc vào vài khách lớn.",
        "pareto_x": "Số khách hàng (xếp theo doanh thu giảm dần)",
        "pareto_y": "Doanh thu lũy kế (%)",
        "top_customers": "15 khách hàng mang lại lợi nhuận đóng góp lớn nhất",
        "c_top10": "10 khách lớn nhất",
        "c_top20": "20 khách lớn nhất",
        "c_largest": "Khách lớn nhất",
        "c_n80": "Số khách tạo 80% doanh thu",
        "c_hhi": "Chỉ số tập trung HHI",
        "n_share": "Tỷ trọng trong tổng doanh thu",
        "n_hhi": "Dưới 1.000: không tập trung",
        "seg": {
            "Contract": "Hợp đồng vận chuyển",
            "Dedicated": "Xe chuyên trách",
            "Spot": "Thuê chuyến lẻ",
            "Dry Van": "Hàng khô",
            "Refrigerated": "Hàng lạnh",
            "Active": "Đang hoạt động",
            "Inactive": "Ngừng hoạt động",
            "Maintenance": "Đang bảo dưỡng",
        },
        # network
        "matrix": "Ma trận tuyến: sản lượng × biên đóng góp",
        "u_matrix": "chuyến (ngang) · % (dọc) · kích thước = doanh thu",
        "matrix_note": "Mỗi bong bóng là một tuyến. Các đường chấm chia tuyến thành ba mức sản "
        "lượng và ba mức biên. Góc trên bên phải là tuyến chủ lực; góc dưới là tuyến biên thấp cần "
        "xem lại giá.",
        "matrix_x": "Sản lượng (số chuyến)",
        "matrix_y": "Biên đóng góp (%)",
        "tier": {1: "Thấp", 2: "Vừa", 3: "Cao"},
        "margin_tier": "Mức biên",
        "lane_eval": "Bảng đánh giá tuyến",
        "lane_eval_note": "Tuyến được xếp theo mức ưu tiên xử lý. Chênh lệch biên là biên đóng góp "
        "của tuyến trừ biên chung của toàn bộ tuyến: số âm là tuyến lãi kém hơn mặt bằng. Mức "
        "Cao/Vừa/Thấp là so sánh giữa các tuyến (chia ba nhóm bằng nhau), không phải ngưỡng tốt "
        "xấu tuyệt đối: mọi tuyến đều có lãi đóng góp, nên biên thấp nghĩa là cần xem lại giá, "
        "chưa phải ngừng tuyến.",
        "segments_def": "Hợp đồng vận chuyển: giá cước ký trước theo tuyến và khối lượng, xe lấy "
        "từ đội chung. Xe chuyên trách: xe và tài xế dành riêng cho một khách trong suốt hợp đồng. "
        "Thuê chuyến lẻ: giá chốt theo từng chuyến. Dữ liệu chỉ ghi loại khách, không mô tả điều "
        "khoản hợp đồng.",
        "lane_cols": {
            "lane": "Tuyến",
            "origin": "Điểm đi",
            "destination": "Điểm đến",
            "trips": "Số chuyến",
            "revenue": "Doanh thu (tr USD)",
            "contribution": "Lợi nhuận đóng góp (tr USD)",
            "margin_pct": "Biên đóng góp (%)",
            "margin_gap_pts": "Chênh lệch biên (điểm %)",
            "volume": "Mức sản lượng",
            "margin_level": "Mức biên",
            "assessment": "Đánh giá",
            "action": "Hướng xử lý",
        },
        "actions": {
            "protect": "Giữ và bảo vệ",
            "maintain": "Duy trì",
            "reprice": "Đàm phán lại giá",
            "grow": "Tăng sản lượng",
            "review_price": "Rà soát giá và chi phí",
            "growth_opportunity": "Tìm thêm nguồn hàng",
            "monitor": "Theo dõi",
            "review_low": "Rà soát giá cước",
        },
        "assessments": {
            "protect": "Tuyến chủ lực: nhiều chuyến, biên cao",
            "maintain": "Hiệu quả ở mức trung bình",
            "reprice": "Nhiều chuyến nhưng biên thấp: mỗi chuyến lãi ít",
            "grow": "Biên cao, sản lượng trung bình",
            "review_price": "Sản lượng trung bình, biên thấp",
            "growth_opportunity": "Ít chuyến nhưng biên cao",
            "monitor": "Ít chuyến, biên trung bình",
            "review_low": "Ít chuyến, biên thấp hơn mặt bằng (vẫn có lãi)",
        },
        "balance": "Cân đối hàng chiều đi – chiều về theo thành phố",
        "balance_note": "Số dương: thành phố gửi đi nhiều hơn nhận về. Số âm: nhận về nhiều hơn "
        "gửi đi, xe giao xong không có hàng chở về và phải chạy rỗng đi nơi khác.",
        "net_loads": "Chênh lệch (lô gửi đi − lô nhận về)",
        "out_in": "Số lô gửi đi và nhận về theo thành phố",
        "loads_out": "Lô gửi đi",
        "loads_in": "Lô nhận về",
        "moves": "Tỷ lệ chuyến phải điều xe từ thành phố khác",
        "moves_note": "Tỷ lệ gần như không đổi ({moved}) vì bằng đúng mức kỳ vọng nếu giao chuyến "
        "ngẫu nhiên ({random}): điều phối chưa ghép lô theo vị trí xe. Đây là tỷ lệ chuyến mà xe "
        "bắt đầu ở thành phố khác nơi chuyến trước kết thúc, tức phải di chuyển xe (thường là chạy "
        "rỗng) trước khi nhận hàng.",
        # service
        "standards": "Tỷ lệ giao đúng hẹn theo bốn chuẩn đo",
        "s_window": "Trong khung ±2 giờ (OTD)",
        "s_not_late": "Không trễ giờ hẹn",
        "s_late_2h": "Trễ không quá 2 giờ",
        "s_by_day": "Đúng ngày hẹn",
        "n_window": "Chuẩn của dữ liệu: lệch không quá 2 giờ, đến sớm hay muộn đều tính",
        "n_not_late": "Đến trước hoặc đúng giờ hẹn",
        "n_late_2h": "Đến sớm vẫn đạt; chỉ tính trễ nếu muộn quá 2 giờ",
        "n_by_day": "Giao trong ngày hẹn hoặc sớm hơn",
        "standards_note": "Cùng một dữ liệu, tỷ lệ đạt từ {lo} đến {hi} tùy chuẩn đo. Khung ±2 giờ "
        "phù hợp để đo việc tuân thủ lịch hẹn tại kho nhận; với chuyến đường dài, cam kết với "
        "khách thường tính theo ngày hẹn. Nên thống nhất chuẩn đo trong hợp đồng trước khi đặt chỉ "
        "tiêu.",
        "spread": "Độ lệch thời điểm giao so với giờ hẹn",
        "spread_note": "Mọi lần giao đều rơi trong khoảng từ sớm {early} đến muộn {late} so với "
        "giờ hẹn, phân bố gần như đều nhau. Cột xanh nằm trong khung ±2 giờ (vùng tô nền), cột xám "
        "là đến sớm quá 2 giờ, cột đỏ là trễ quá 2 giờ: đây là phần cần cải thiện.",
        "spread_x": "Số giờ lệch so với giờ hẹn (âm = đến sớm, dương = đến muộn)",
        "window_band": "Khung ±2 giờ",
        "by_length": "Tỷ lệ đúng hẹn theo độ dài chuyến",
        "by_length_note": "Chuyến dài không bị đánh giá bất lợi: theo khung ±2 giờ, chuyến dưới 1 "
        "ngày đạt {a}, 1–2 ngày đạt {b}, trên 2 ngày đạt {c}. Độ trễ không tăng theo quãng đường.",
        "bands": {1: "Dưới 1 ngày", 2: "1–2 ngày", 3: "Trên 2 ngày"},
        "detention_title": "Thời gian chờ tại điểm lấy và giao hàng",
        "s_detention": "Thời gian chờ bình quân",
        "s_detention_hours": "Tổng thời gian chờ",
        "s_detention_note": "Mỗi lần lấy hoặc giao hàng",
        "s_detention_hours_note": "Cộng dồn cả khoảng thời gian",
        "detention_type": "Thời gian chờ bình quân: lấy hàng so với giao hàng",
        "detention_note": "So sánh thời gian xe chờ khi lấy hàng và khi giao hàng qua từng năm. "
        "Thời gian chờ dài làm giảm số chuyến mỗi xe chạy được và có thể tính phí lưu xe với "
        "khách.",
        "pickup": "Lấy hàng",
        "delivery": "Giao hàng",
        "on_time_city": "Tỷ lệ giao trong khung ±2 giờ theo thành phố nhận",
        "sensitivity_title": "Thử thay đổi độ rộng khung giờ",
        "window": "Độ rộng khung (± phút so với giờ hẹn)",
        "window_help": "Dữ liệu dùng ±120 phút. Kéo để xem tỷ lệ đạt thay đổi thế nào.",
        "sensitivity": "Tỷ lệ đạt theo độ rộng khung giờ",
        "sensitivity_note": "Khung càng rộng, tỷ lệ đạt càng cao. Vạch đứt là khung của dữ liệu "
        "(±120 phút).",
        "sensitivity_x": "Độ rộng khung (± phút)",
        "sensitivity_y": "Tỷ lệ đạt (%)",
        "data_window": "Khung của dữ liệu (±120 phút)",
        "selected_window": "Khung đang chọn",
        "on_time_month": "Tỷ lệ đạt theo tháng với khung đang chọn",
        # fleet
        "daily_trucks": "Số xe hoạt động mỗi ngày",
        "daily_trucks_note": "Bình quân mỗi ngày có {avg} xe hoạt động. 95% số ngày cần không quá "
        "{p95} xe, 99% số ngày không quá {p99} xe, ngày cao điểm nhất cần {max} xe. Trong khi đó "
        "công ty sở hữu {owned} xe ({in_use} xe từng chạy chuyến), tức {spare} xe chưa từng được "
        "cần đến kể cả vào ngày cao điểm nhất.",
        "p95": "Đủ cho 95% số ngày",
        "p99": "Đủ cho 99% số ngày",
        "in_use": "Xe từng chạy chuyến",
        "owned": "Xe sở hữu",
        "productivity": "Năng suất đội xe",
        "f_miles_month": "Quãng đường bình quân mỗi xe mỗi tháng",
        "n_miles_month": "Tổng số dặm ÷ số tháng-xe có chạy chuyến",
        "f_rev_truck_week": "Doanh thu bình quân mỗi xe mỗi tuần",
        "n_rev_truck_week": "Doanh thu ÷ số tuần-xe có chạy chuyến",
        "f_util": "Hiệu suất sử dụng đội xe",
        "f_downtime": "Thời gian dừng xe bảo dưỡng",
        "n_downtime": "Tổng số giờ xe ngừng hoạt động để bảo dưỡng, sửa chữa",
        "busy_dist": "Phân bố số xe hoạt động mỗi ngày",
        "busy_dist_note": "Mỗi cột là số ngày có cùng số xe hoạt động. Bình quân {avg} xe mỗi "
        "ngày; 95% số ngày không quá {p95} xe.",
        "busy_x": "Số xe hoạt động trong ngày",
        "days_y": "Số ngày",
        "util_dist": "Hệ số sử dụng xe theo báo cáo hệ thống",
        "util_note": "Hệ số do hệ thống nguồn tự báo cáo hằng tháng cho từng xe. Dữ liệu không mô "
        "tả cách tính và có giá trị trên 100%, nên chỉ dùng để so sánh các xe với nhau.",
        "util_x": "Hệ số sử dụng (%)",
        "trucks_y": "Số xe",
        "status": "Đội xe theo trạng thái",
        "ran_trips": "có chạy chuyến",
        "never_ran": "chưa chạy chuyến nào",
        "idle_trucks": "Danh sách {n} xe chưa chạy chuyến nào",
        "idle_note": "Các xe này không tạo ra doanh thu nhưng vẫn phát sinh {cost} chi phí bảo "
        "dưỡng. Đây là danh sách cần rà soát đầu tiên khi điều chỉnh quy mô đội xe.",
        "idle_cols": {
            "truck_id": "Mã xe",
            "make": "Hãng xe",
            "model_year": "Đời xe",
            "status": "Trạng thái",
            "maintenance_events": "Số lần bảo dưỡng",
            "maintenance_cost": "Chi phí bảo dưỡng (USD)",
        },
        # fuel
        "bought_vs_burned": "Nhiên liệu mua vào và nhiên liệu tiêu thụ theo chuyến",
        "bought_note": "Cột xanh là lượng mua theo giao dịch thẻ nhiên liệu; cột cam là lượng ghi "
        "nhận tiêu thụ trên các chuyến. Chênh lệch giữa hai cột cần được đối soát.",
        "bought": "Nhiên liệu mua vào",
        "burned": "Nhiên liệu tiêu thụ theo chuyến",
        "ratio": "Tỷ lệ nhiên liệu mua / tiêu thụ",
        "ratio_note": "Bằng 1 nghĩa là mua đúng bằng lượng tiêu thụ. Trên 1 là mua nhiều hơn lượng "
        "ghi nhận dùng cho chuyến.",
        "price_trend": "Giá nhiên liệu bình quân",
        "spend": "Chi phí nhiên liệu",
        "spend_note": "Chi phí nhiên liệu = lượng mua × giá. Đối chiếu với biểu đồ giá và biểu đồ "
        "lượng mua để thấy chi phí thay đổi do giá hay do lượng.",
        # optimization
        "p_optimize": "Khuyến nghị tối ưu",
        "d_optimize": "Các hành động giúp giảm chi phí hoặc tăng lợi nhuận, kèm số tiền mỗi năm và "
        "mức độ chắc chắn.",
        "o_scope": "Tính trên toàn bộ dữ liệu từ {a} đến {b}; không đổi theo khoảng thời gian ở "
        "thanh bên.",
        "proj_heading": "Đề tài và nguồn dữ liệu",
        "proj": {
            "title": "Đề tài",
            "goal": "Bài toán",
            "data": "Bộ dữ liệu",
            "company": "Doanh nghiệp",
            "source": "Nguồn dữ liệu",
        },
        "proj_title": "Phân tích và tối ưu hiệu quả vận hành vận tải hàng hóa đường bộ",
        "proj_goal": "Tìm cách giảm ít nhất 3% chi phí vận hành mỗi năm và nâng chất lượng giao "
        "hàng, từ dữ liệu vận hành của doanh nghiệp",
        "proj_data": "Logistics Operations Database: {tables} bảng, {rows} dòng, chuyến xe từ {a} "
        "đến {b}",
        "proj_company": "Doanh nghiệp vận tải hàng hóa đường bộ tại Mỹ; dữ liệu mô phỏng nên không "
        "nêu tên: {trucks} xe tải, {drivers} tài xế, {customers} khách hàng, {routes} tuyến, "
        "{trips} chuyến",
        "proj_source": "Kaggle, tác giả yogape: "
        "kaggle.com/datasets/yogape/logistics-operations-database",
        "o_tip_hint": "Rê chuột hoặc chạm vào từng ô để xem cách tính ra con số.",
        "o_tip_target": [
            "Mục tiêu = 3% chi phí vận hành đo được bình quân mỗi năm.",
            "Chi phí vận hành đo được: {base} mỗi năm (nhiên liệu, bảo dưỡng, bồi thường sự cố "
            "2022–2024, gồm cả bảo dưỡng của các xe không chạy chuyến).",
            "3% × {base} = {target} mỗi năm.",
        ],
        "o_tip_measured": "Chi phí bảo dưỡng mỗi năm của các xe chưa từng chạy chuyến; thanh lý "
        "thì khoản này mất hẳn:",
        "o_tip_measured_end": "Điều kiện: thanh lý hoặc dừng bảo dưỡng đủ {n} xe. Không ảnh hưởng "
        "vận hành vì các xe này chưa từng chạy chuyến nào.",
        "o_tip_upper": "Giá trị tối đa của các hành động cần quyết định nội bộ hoặc khách hàng "
        "chấp nhận:",
        "o_tip_upper_end": "Gọi là tối đa vì giả định khách chấp nhận đủ mức tăng mà không giảm "
        "sản lượng, và các xe còn lại gánh hết chuyến của xe được rút. Thực tế thường thấp hơn.",
        "o_tip_sum": "Tổng: {total} = {pct} mục tiêu.",
        "o_tip_total": "Tiết kiệm đo được {m} + tiềm năng tối đa {u} = {total} ({pct} mục tiêu).",
        "o_tip_gap": "Để đạt mục tiêu {target}: làm đủ phần đo được ({m}) và thu thêm ít nhất "
        "{gap} từ các hành động tiềm năng, tức {share} tiềm năng tối đa.",
        "o_tip_example": "Ví dụ: riêng việc nâng phụ phí nhiên liệu ({fsc}) đã đủ nếu khách chấp "
        "nhận ít nhất {fsc_share} mức nâng đề xuất.",
        "o_tip_done": "Riêng phần đo được đã đạt mục tiêu {target}.",
        "o_target": "Mục tiêu tiết kiệm",
        "n_target": "3% chi phí vận hành đo được, mỗi năm",
        "o_measured": "Tiết kiệm đo được",
        "n_measured": "{pct} mục tiêu · chi phí có sẵn trong dữ liệu, chắc chắn dừng khi thực hiện",
        "o_upper": "Tiềm năng tối đa",
        "n_upper": "Nếu khách hàng hoặc nội bộ chấp nhận thay đổi; thực tế thường thấp hơn",
        "o_total": "Tổng tiềm năng",
        "n_total": "{pct} mục tiêu nếu thực hiện tất cả",
        "o_unexplained": "Ngoài ra, {amount} mỗi năm tiền nhiên liệu chưa giải thích được (mua "
        "nhiều hơn lượng ghi nhận tiêu thụ). Khoản này không cộng vào tổng vì chưa chứng minh là "
        "thất thoát; cần đối soát trước.",
        "o_chart": "Giá trị mỗi năm của từng khuyến nghị",
        "o_chart_note": "Xanh lá là tiết kiệm đo được, xanh dương là tiềm năng tối đa. Mục tiêu là "
        "{target} mỗi năm.",
        "o_table": "Danh sách khuyến nghị",
        "o_cols": [
            "Lĩnh vực",
            "Hành động",
            "Phạm vi",
            "Giá trị mỗi năm",
            "Loại",
            "Căn cứ",
        ],
        "o_areas": {
            "Fleet": "Đội xe",
            "Lanes": "Giá cước tuyến",
            "Data": "Dữ liệu",
            "Network": "Mạng lưới",
            "Checked": "Đã kiểm tra",
        },
        "o_types": {
            "measured": "Tiết kiệm đo được",
            "upper bound": "Tiềm năng tối đa",
            "risk sharing": "Chia sẻ rủi ro",
            "unexplained": "Chưa giải thích được",
            "estimate": "Ước tính (giả thuyết)",
            "no signal": "Không có tín hiệu",
        },
        "o_checked": "Đã kiểm tra và không đề xuất",
        "o_checked_note": "Chỉ đề xuất khi tín hiệu lặp lại qua các năm. Các đòn bẩy dưới đây đã "
        "được kiểm tra trên dữ liệu và không đạt, hoặc đã được chủ dự án loại.",
        "o_checked_cols": ["Đòn bẩy", "Bằng chứng"],
        "o_fleet": "Quy mô đội xe",
        "o_growth": "Sản lượng chuyến giả định",
        "o_growth_now": "Như hiện tại",
        "o_growth_up": "Tăng {g}%",
        "o_growth_help": "Số xe cần nếu số chuyến mỗi ngày giữ nguyên như 2022–2024 hoặc tăng thêm "
        "5%, 10%, 20%. Các ô tổng tiết kiệm ở đầu trang dùng mức Như hiện tại.",
        "o_needed": "Số xe cần",
        "n_needed": "Đủ cho 99% số ngày, đã tính xe dừng bảo dưỡng và chuyến thiếu mã xe",
        "o_owned": "Xe sở hữu",
        "o_in_use": "Xe từng chạy chuyến",
        "o_surplus": "Xe dư so với nhu cầu",
        "o_needed_chart": "Số xe cần theo sản lượng chuyến",
        "o_needed_note": "So với {owned} xe sở hữu và {in_use} xe từng chạy chuyến. Ngày bận nhất "
        "cần {busiest} xe; {above} trên {days} ngày cần nhiều hơn mức đề xuất khi sản lượng như "
        "hiện tại, có thể thuê xe ngắn hạn cho những ngày này.",
        "o_tiers": "Lộ trình thanh lý theo bậc",
        "o_tier_cols": [
            "Bậc",
            "Nhóm xe",
            "Số xe",
            "Đưa lại vận hành",
            "Chi phí bảo dưỡng mỗi năm",
            "Loại",
        ],
        "o_tier_status": {
            "Inactive": "Ngừng hoạt động, chưa từng chạy",
            "Maintenance": "Đang bảo dưỡng, chưa từng chạy",
            "Active (lowest mileage)": "Đang chạy, ít dặm nhất",
        },
        "o_tiers_note": "Bậc 1–2 là xe chưa từng chạy chuyến nào: bỏ đi không ảnh hưởng vận hành "
        "nên tiết kiệm là chắc chắn. Bậc 3 là tiềm năng tối đa vì các xe còn lại phải gánh chuyến "
        "của xe bị bỏ. Giá bán lại xe không có trong dữ liệu nên chưa tính vào.",
        "o_lanes": "Giá cước tuyến",
        "o_cap": "Mức tăng cước tối đa mỗi tuyến",
        "o_cap_none": "Không giới hạn (lý thuyết)",
        "o_s1": "S1 · Chuẩn hóa phụ phí nhiên liệu",
        "n_s1": "Nâng phụ phí các tuyến thấp lên mức trung vị",
        "o_s2": "S2 · Tăng cước tuyến biên thấp",
        "n_s2": "Về gần biên trung vị, trong mức tăng tối đa đã chọn",
        "o_s12": "Tổng S1 + S2 mỗi năm",
        "n_s12": "{pct} mục tiêu",
        "o_loss": "Sụt sản lượng hòa vốn",
        "n_loss": "Trung vị: tuyến tăng giá có thể mất chừng này sản lượng mà lợi nhuận không thấp "
        "hơn hiện nay",
        "o_lane_table": "Kết quả theo tuyến",
        "o_lane_note": "Chi phí tài xế hòa vốn: tuyến chỉ lỗ nếu chi phí tài xế mỗi dặm vượt mức "
        "này (thay cho lương tài xế không có trong dữ liệu). Tuyến không cần điều chỉnh có S1, S2 "
        "bằng 0.",
        "o_lane_cols": {
            "lane": "Tuyến",
            "group": "Hướng xử lý",
            "margin": "Biên đóng góp (%)",
            "fsc_rate": "Phụ phí hiện tại (USD/dặm)",
            "s1": "S1 (USD/năm)",
            "s2": "S2 (USD/năm)",
            "increase": "Tăng cước (%)",
            "loss": "Sụt sản lượng hòa vốn (%)",
            "break_even": "Chi phí tài xế hòa vốn (USD/dặm)",
        },
        "o_s3": "S3 · Phụ phí theo giá nhiên liệu (mô phỏng)",
        "o_s3_group": "Phụ phí nhiên liệu theo giá",
        "o_chain": "Ghép chuyến: điều xe rảnh gần nhất (mô phỏng)",
        "o_chain_moved": "Chuyến phải điều xe",
        "n_chain_moved": "Như hiện tại {today} (thực tế {seen})",
        "o_chain_miles": "Dặm chạy rỗng",
        "n_chain_miles": "{near} so với {today} triệu dặm mỗi năm trong mô phỏng",
        "o_chain_move": "Quãng điều xe bình quân",
        "n_chain_move": "Khoảng {h} giờ lái; {day} số lần trong một ngày lái ({limit} giờ)",
        "o_chain_value": "Tiết kiệm nhiên liệu tối đa mỗi năm",
        "n_chain_value": "−{cut} × {fuel} nhiên liệu mua ngoài chuyến; ước tính, không cộng vào "
        "tổng",
        "o_chain_tip": [
            "Từ dữ liệu: tốc độ {speed} dặm/giờ, {mpg} dặm/gallon, giá {price}/gallon → "
            "mỗi dặm chạy rỗng {per_mile}.",
            "Mô hình: dặm chạy rỗng giảm {cut}, tức {model} nhiên liệu mỗi năm.",
            "Nhưng nhiên liệu mua ngoài chuyến chỉ có {off_trip} mỗi năm (khoảng {off_miles} triệu "
            "dặm), ít hơn số dặm rỗng của mô hình.",
            "Vì vậy chỉ áp tỷ lệ giảm: {cut} × {off_trip} = {saving} mỗi năm, là mức tối đa.",
        ],
        "o_chain_table": "Như hiện tại và điều xe gần nhất",
        "o_chain_note": "Mô phỏng lại {loads} lô với giờ lấy và giao thực tế. Mỗi lô được giao cho "
        "xe rảnh gần thành phố lấy hàng nhất, kịp chạy rỗng tới (xe đang ở đó được ưu tiên). Quãng "
        "đường lấy theo mạng tuyến của dữ liệu, đi vòng khi hai thành phố không có tuyến trực "
        "tiếp, nên dài hơn đường thực tế. Không đặt giới hạn cứng cho quãng chạy rỗng: xe dồn ở "
        "các thành phố ít hàng đi phải chạy xa, và mọi giới hạn đến 24 giờ đều cần thêm hàng nghìn "
        "xe. Quãng điều xe nên giữ trong một ngày lái ({h} giờ); xa hơn thì nên tìm hàng chiều về "
        "tại chỗ thay vì chạy rỗng.",
        "o_chain_cols": ["Chỉ số", "Như hiện tại", "Điều xe gần nhất"],
        "o_chain_rows": [
            "Chuyến phải điều xe",
            "Lần điều xe mỗi năm",
            "Dặm chạy rỗng mỗi năm",
            "Dặm mỗi lần điều xe",
            "Lần điều xe trong một ngày lái ({h} giờ)",
            "Số xe cần (mô phỏng)",
        ],
        "o_s3_note": "Phụ phí tính theo giá nhiên liệu hằng tháng, với giá cơ sở {base} mỗi gallon "
        "để tổng doanh thu 3 năm không đổi. Năm giá cao thu nhiều hơn, năm giá thấp thu ít hơn: "
        "lợi nhuận bớt phụ thuộc giá nhiên liệu. Không tính là tiết kiệm.",
        "o_s3_actual": "Phụ phí thực tế",
        "o_s3_indexed": "Phụ phí theo giá nhiên liệu",
        "o_gaps": "Cải tiến quy trình dữ liệu",
        "o_gaps_note": "Bậc 1 là thay đổi quy trình hoặc cấu hình trên hệ thống sẵn có, gần như "
        "không tốn tiền. Bậc 2 cần thiết bị telematics; giá là số tham khảo công khai, cần thay "
        "bằng báo giá thực tế.",
        "o_gap_cols": [
            "Lỗ hổng",
            "Bằng chứng",
            "Chi phí khi không làm",
            "Biện pháp bậc 1 (quy trình)",
            "Biện pháp bậc 2 (thiết bị)",
        ],
        "o_tele_cost": "Chi phí telematics mỗi năm",
        "n_tele_cost": "{trucks} xe đang chạy · thuê bao và thiết bị chia đều 3 năm",
        "o_tele_break": "Mức hòa vốn của telematics",
        "n_tele_break": "Phần chi phí nhiên liệu cần tiết kiệm để thiết bị tự hoàn vốn",
        "o_sources": "Nguồn giá tham khảo",
        # reports
        "r_export": "Xuất báo cáo",
        "r_title": "Báo cáo quản lý vận tải",
        "r_period": "Khoảng thời gian: {a} – {b}",
        "r_generated": "Ngày xuất: {d}",
        "r_page": "Trang",
        "r_toc": "Mục lục",
        "r_figs": "Danh mục hình",
        "r_tabs": "Danh mục bảng",
        "r_summary": "Tóm tắt điều hành",
        "r_sum_results": "Kết quả chính trong kỳ",
        "r_sum_act": "Cần hành động ngay",
        "r_sum_watch": "Cần theo dõi",
        "r_sum_savings": "Cơ hội tiết kiệm",
        "r_fig": "Hình",
        "r_tab": "Bảng",
        "r_running": "Đang tạo báo cáo… {pct}",
        "r_done": "Đã tạo xong · {name}",
        "r_format": "Định dạng",
        "r_make": "Tạo báo cáo",
        "r_download": "Tải về",
        "r_no_browser": "Không tìm thấy Microsoft Edge hoặc Google Chrome để tạo PDF. Hãy chọn "
        "định dạng HTML.",
        "r_note": "Số liệu do lớp phân tích tính từ dữ liệu. Lợi nhuận là lợi nhuận đóng góp, chưa "
        "trừ lương tài xế và chi phí chung vì dữ liệu không có.",
        "r_late": "Kiểm tra nguyên nhân giao trễ",
        "r_late_note": "{share} lần giao trễ quá 2 giờ. Một nguyên nhân chỉ đáng xử lý khi tỷ lệ "
        "trễ của nhóm lặp lại giữa 2022–2023 và năm cuối (tương quan từ 0,7).",
        "r_late_cols": [
            "Phân tích theo",
            "Số nhóm",
            "Chênh lệch tỷ lệ trễ (điểm %)",
            "Tương quan giữa hai giai đoạn",
            "Có tín hiệu",
        ],
        "r_dims": {
            "city": "Thành phố nhận",
            "customer": "Khách hàng",
            "appointment_hour": "Giờ hẹn",
            "lane": "Tuyến",
            "driver": "Tài xế",
        },
        "r_yes": "Có",
        "r_no": "Không",
        # data
        "d_tables": "Số bảng dữ liệu",
        "d_rows": "Số dòng dữ liệu",
        "d_rules": "Số quy tắc kiểm tra",
        "d_errors": "Dòng có lỗi nghiêm trọng",
        "findings": "Số dòng bị gắn cờ theo từng quy tắc kiểm tra",
        "findings_note": "Đỏ là lỗi nghiêm trọng (dòng không dùng cho phép tính liên quan); vàng "
        "là cảnh báo (dùng có điều kiện). Dòng bị gắn cờ được giữ lại, không xóa.",
        "severity": {"error": "Lỗi nghiêm trọng", "warn": "Cảnh báo"},
        "trust": "Dữ liệu tin được đến đâu",
        "trust_rows": [
            ("Quan hệ giữa các bảng, các khoản tiền, bảng tổng hợp tháng", "Tin cậy", "ok"),
            (
                "Mã tài xế/xe thiếu khoảng 2%; một số lần giao ghi trước khi lấy hàng; hệ số sử "
                "dụng xe trên 100%",
                "Dùng có điều kiện",
                "warn",
            ),
            (
                "Bang trên giao dịch nhiên liệu, mã kho trên sự kiện giao nhận, giờ chạy không tải",
                "Không sử dụng",
                "no",
            ),
        ],
        "trust_cols": ["Dữ liệu", "Mức tin cậy"],
        "glossary": "Định nghĩa KPI",
        "glossary_note": "Cột giá trị là kết quả của từng KPI cho toàn đội xe trong khoảng thời "
        "gian đang chọn, để đối chiếu định nghĩa với con số trên các trang.",
        "g_cols": {
            "area": "Nhóm",
            "kpi": "Chỉ số",
            "formula": "Định nghĩa và công thức",
            "unit": "Đơn vị",
            "value": "Giá trị toàn đội",
        },
    },
    "en": {
        "app_title": "Logistics Ops · Executive dashboard",
        "lang": "Language",
        "period": "Date range",
        "from": "From",
        "to": "To",
        "apply": "Apply",
        "bad_range": "The start date must come before the end date.",
        "applied": "Showing: {a} – {b}",
        "date_format": "YYYY-MM-DD",
        "loading": "Loading figures…",
        "locked": "Can't open the warehouse. Disconnect DBeaver or any other program that has "
        "`warehouse.duckdb` open, then reload the page.",
        "no_warehouse": "No warehouse yet. Run `uv run logops build` first.",
        "source_note": "Profit on this dashboard is contribution profit: before driver pay and "
        "overhead, which the data doesn't have.",
        "p_overview": "Executive overview",
        "p_profit": "Financial performance",
        "p_regions": "Customers & markets",
        "p_network": "Lane performance",
        "p_service": "Delivery performance",
        "p_fleet": "Fleet capacity & utilization",
        "p_fuel": "Fuel management",
        "p_data": "Data quality & KPI definitions",
        "d_overview": "Financial results, delivery quality, fleet performance and the issues to "
        "address.",
        "d_profit": "Revenue, costs and contribution profit by period; why profit changed.",
        "d_regions": "Profit by state, customer segment and load type, and dependence on large "
        "customers.",
        "d_network": "How each lane performs and how outbound and return loads balance.",
        "d_service": "On-time delivery under different standards, delivery timing and detention.",
        "d_fleet": "Trucks needed each day against fleet size, truck productivity and unused "
        "trucks.",
        "d_fuel": "Fuel bought against fuel used, fuel price and fuel cost.",
        "d_data": "How far the source data can be trusted, and what each KPI means.",
        "revenue": "Revenue",
        "contribution": "Contribution profit",
        "margin": "Contribution margin",
        "fuel": "Fuel cost",
        "maintenance": "Maintenance cost",
        "claims": "Incident claims",
        "trips": "Trips",
        "year": "Year",
        "month": "Month",
        "quarter": "Quarter",
        "vs_last_year": "vs last year",
        "vs_year": "vs {y}",
        "points": "pts",
        "minutes": "min",
        "hours": "h",
        "unit": "Unit: {u}",
        "explain": "How to read:",
        "row_no": "No.",
        "filter_all": "All",
        "rows_shown": "Showing {n} of {total} rows",
        "u_musd": "USD millions",
        "u_usd": "USD",
        "u_pct": "%",
        "u_trucks": "trucks",
        "u_days": "days",
        "u_loads": "loads",
        "u_deliveries": "deliveries",
        "u_gallons": "gallons",
        "u_usd_gallon": "USD per gallon",
        "u_times": "times",
        "u_rows": "rows",
        "u_minutes": "minutes",
        "u_miles": "miles",
        "k_revenue": "Revenue",
        "k_contribution": "Contribution profit",
        "k_op_cost": "Operating cost",
        "n_op_cost": "Fuel + maintenance + claims",
        "k_margin": "Contribution margin",
        "k_cost_mile": "Operating cost per mile",
        "k_otd": "On-time delivery (OTD)",
        "k_detention": "Average detention",
        "k_trips": "Trips completed",
        "k_fleet_use": "Fleet utilization",
        "n_revenue": "Linehaul + fuel surcharge + accessorial charges",
        "n_contribution": "Revenue minus fuel, maintenance and incident claims",
        "n_margin": "Contribution profit ÷ revenue",
        "n_cost_mile": "Fuel, maintenance and claims ÷ total miles",
        "n_otd": "Within ±2 hours of the appointment · by appointment date: {day}",
        "n_detention": "Minutes a truck waits at each pickup or delivery",
        "n_trips": "Each trip carries one load",
        "n_fleet_use": "On average {busy} of {owned} trucks have a trip each day",
        "view_period": "View",
        "all_period": "Whole period",
        "period_only": "Figures from {a} to {b}.",
        "period_vs": "Figures from {a} to {b}, compared with {y}.",
        "g_finance": "Finance",
        "g_operations": "Operations & service",
        "key_points": "Key findings",
        "tone_legend": "Edge colour shows the tone:",
        "findings_scope": "Findings cover the whole date range chosen in the sidebar.",
        "margin_vs_fuel": "Contribution margin and fuel price by month",
        "u_margin_fuel": "% (top) · USD per gallon (bottom)",
        "margin_vs_fuel_note": "Contribution margin = (revenue − fuel − maintenance − claims) ÷ "
        "revenue, before driver pay and overhead. Both charts share the time axis: every fall in "
        "fuel prices lifts the margin (correlation {corr}), because the fuel surcharge customers "
        "pay doesn't change.",
        "monthly_margin": "Contribution margin (%)",
        "fuel_price": "Average fuel price (USD per gallon)",
        "choose_period": "Reporting period",
        "where_revenue_goes": "Revenue breakdown: costs and contribution profit",
        "where_revenue_goes_note": "Each bar is one period's revenue, split into fuel, "
        "maintenance, incident claims and what remains as contribution profit. A taller bar is "
        "more revenue; a bigger blue part is better profit.",
        "bridge": "Profit bridge: why contribution profit changed",
        "bridge_note": "The grey bars are the two years' contribution profit. Each bar between "
        "them is the change caused by one factor: blue raises profit, red lowers it. Together they "
        "add up exactly to the difference between the two years.",
        "bridge_from": "From year",
        "bridge_to": "To year",
        "b_start": "Profit {y}",
        "b_end": "Profit {y}",
        "b_volume": "Volume",
        "b_rate": "Rate per trip",
        "b_fuel_price": "Fuel price",
        "b_fuel_consumption": "Fuel used per trip",
        "b_maintenance": "Maintenance cost",
        "b_claims": "Incident claims",
        "ytd": "Year-to-date contribution profit",
        "ytd_note": "Each line is one year, adding up profit from January. The higher line is the "
        "year with better profit at the same point.",
        "units": "Results per unit",
        "u_rev_mile": "Revenue per mile",
        "u_contrib_mile": "Contribution profit per mile",
        "u_rev_trip": "Revenue per trip",
        "u_contrib_truck_week": "Contribution profit per truck per week",
        "pnl_table": "Results by period",
        "pnl_cols": {
            "period": "Period",
            "year": "Year",
            "revenue": "Revenue (USD M)",
            "fuel_cost": "Fuel cost (USD M)",
            "maintenance_cost": "Maintenance cost (USD M)",
            "claims": "Incident claims (USD M)",
            "contribution": "Contribution profit (USD M)",
            "margin_pct": "Contribution margin (%)",
            "contribution_vs_prev_pct": "Profit vs previous period (%)",
            "contribution_yoy_pct": "Profit vs same period last year (%)",
        },
        "state_side": "By state",
        "origin": "Origin state",
        "destination": "Destination state",
        "state_map": "Contribution profit by state",
        "state_map_note": "The darker the state, the more contribution profit it brings. Hover "
        "over a state to see the amount.",
        "margin_by_state": "Contribution margin by state",
        "state_margin_note": "Contribution margin = contribution profit ÷ revenue of the state's "
        "trips. Highest {hi_state} ({hi}), lowest {lo_state} ({lo}). Low-margin states have low "
        "rates or high costs compared with the rest: review prices there first.",
        "segments": "Revenue by customer segment",
        "load_types": "Revenue by load type",
        "pareto": "Customer concentration",
        "pareto_chart": "Pareto curve: cumulative revenue by number of customers",
        "pareto_note": "Customers ranked from largest to smallest. The closer the curve is to the "
        "diagonal, the more evenly revenue is spread and the less it depends on a few customers.",
        "pareto_x": "Customers (ranked by revenue)",
        "pareto_y": "Cumulative revenue (%)",
        "top_customers": "Top 15 customers by contribution profit",
        "c_top10": "Top 10 customers",
        "c_top20": "Top 20 customers",
        "c_largest": "Largest customer",
        "c_n80": "Customers making 80% of revenue",
        "c_hhi": "Concentration index (HHI)",
        "n_share": "Share of total revenue",
        "n_hhi": "Below 1,000: not concentrated",
        "seg": {
            "Contract": "Contract",
            "Dedicated": "Dedicated fleet",
            "Spot": "Spot",
            "Dry Van": "Dry van",
            "Refrigerated": "Refrigerated",
            "Active": "Active",
            "Inactive": "Inactive",
            "Maintenance": "In maintenance",
        },
        "matrix": "Lane matrix: volume × contribution margin",
        "u_matrix": "trips (across) · % (up) · size = revenue",
        "matrix_note": "Each bubble is a lane. The dotted lines split lanes into three volume "
        "levels and three margin levels. Top right are the core lanes; the bottom row are "
        "low-margin lanes whose prices need review.",
        "matrix_x": "Volume (trips)",
        "matrix_y": "Contribution margin (%)",
        "tier": {1: "Low", 2: "Mid", 3: "High"},
        "margin_tier": "Margin level",
        "lane_eval": "Lane assessment",
        "lane_eval_note": "Lanes are ordered by how urgently they need attention. The margin gap "
        "is the lane's contribution margin minus the margin of all lanes together: negative means "
        "the lane earns less than average. High/Mid/Low compare lanes with each other (three equal "
        "groups), not an absolute good or bad line: every lane is profitable, so a low margin "
        "means review the rate, not drop the lane.",
        "segments_def": "Contract: rates agreed in advance by lane and volume, trucks from the "
        "shared fleet. Dedicated fleet: trucks and drivers reserved for one customer for the whole "
        "contract. Spot: price set trip by trip. The data records the customer type only, not the "
        "contract terms.",
        "lane_cols": {
            "lane": "Lane",
            "origin": "From",
            "destination": "To",
            "trips": "Trips",
            "revenue": "Revenue (USD M)",
            "contribution": "Contribution profit (USD M)",
            "margin_pct": "Contribution margin (%)",
            "margin_gap_pts": "Margin gap (pts)",
            "volume": "Volume level",
            "margin_level": "Margin level",
            "assessment": "Assessment",
            "action": "Action",
        },
        "actions": {
            "protect": "Protect",
            "maintain": "Maintain",
            "reprice": "Renegotiate rates",
            "grow": "Grow volume",
            "review_price": "Review rates and costs",
            "growth_opportunity": "Find more freight",
            "monitor": "Monitor",
            "review_low": "Review rates",
        },
        "assessments": {
            "protect": "Core lane: many trips, high margin",
            "maintain": "Average performance",
            "reprice": "Many trips but low margin: little profit per trip",
            "grow": "High margin, average volume",
            "review_price": "Average volume, low margin",
            "growth_opportunity": "Few trips but high margin",
            "monitor": "Few trips, average margin",
            "review_low": "Few trips, margin below average (still profitable)",
        },
        "balance": "Outbound vs return loads by city",
        "balance_note": "Positive: the city sends more loads than it receives. Negative: it "
        "receives more than it sends, so trucks unload with nothing to carry back and drive empty "
        "elsewhere.",
        "net_loads": "Net (loads sent − loads received)",
        "out_in": "Loads sent and received by city",
        "loads_out": "Loads sent",
        "loads_in": "Loads received",
        "moves": "Share of trips needing a truck from another city",
        "moves_note": "The share barely moves ({moved}) because it matches what random assignment "
        "of next trips would give ({random}): dispatch doesn't match loads to where trucks are. It "
        "is the share of trips where the truck starts in a different city from where its previous "
        "trip ended, so it has to be moved (usually empty) before loading.",
        "standards": "On-time delivery under four standards",
        "s_window": "Within ±2 hours (OTD)",
        "s_not_late": "Not late",
        "s_late_2h": "No more than 2 hours late",
        "s_by_day": "On the appointment date",
        "n_window": "The data's standard: off by no more than 2 hours, early or late",
        "n_not_late": "At or before the appointment",
        "n_late_2h": "Early counts as on time; late only after 2 hours",
        "n_by_day": "On or before the appointment date",
        "standards_note": "On the same data, the on-time rate ranges from {lo} to {hi} depending "
        "on the standard. A ±2-hour window suits measuring dock-appointment compliance; for "
        "long-haul trips, the customer promise is usually the appointment date. Agree the standard "
        "in the contract before setting a target.",
        "spread": "Delivery time against the appointment",
        "spread_note": "Every delivery lands between {early} early and {late} late, spread almost "
        "evenly. Blue bars fall within ±2 hours (the shaded band), grey bars are more than 2 hours "
        "early and red bars more than 2 hours late, which is what needs improving.",
        "spread_x": "Hours from the appointment (negative = early, positive = late)",
        "window_band": "±2-hour window",
        "by_length": "On-time rate by trip length",
        "by_length_note": "Long trips are not judged unfairly: within ±2 hours, trips under a day "
        "reach {a}, one to two days {b}, over two days {c}. Lateness does not grow with distance.",
        "bands": {1: "Under 1 day", 2: "1–2 days", 3: "Over 2 days"},
        "detention_title": "Waiting time at pickup and delivery",
        "s_detention": "Average detention",
        "s_detention_hours": "Total detention",
        "s_detention_note": "Per pickup or delivery",
        "s_detention_hours_note": "Summed over the whole range",
        "detention_type": "Average detention: pickup vs delivery",
        "detention_note": "Compares how long trucks wait at pickup and at delivery, year by year. "
        "Long waits cut the trips each truck can run and can be billed to customers as detention.",
        "pickup": "Pickup",
        "delivery": "Delivery",
        "on_time_city": "Deliveries within ±2 hours by delivery city",
        "sensitivity_title": "Try a different window width",
        "window": "Window width (± minutes from the appointment)",
        "window_help": "The data uses ±120 minutes. Drag to see how the on-time rate changes.",
        "sensitivity": "On-time rate by window width",
        "sensitivity_note": "The wider the window, the higher the rate. The dashed line is the "
        "data's window (±120 minutes).",
        "sensitivity_x": "Window width (± minutes)",
        "sensitivity_y": "On-time rate (%)",
        "data_window": "The data's window (±120 min)",
        "selected_window": "Selected window",
        "on_time_month": "On-time rate by month with the selected window",
        "daily_trucks": "Trucks working each day",
        "daily_trucks_note": "On an average day {avg} trucks are working. 95% of days need no more "
        "than {p95} trucks, 99% no more than {p99}, and the busiest day needed {max}. The company "
        "owns {owned} trucks ({in_use} have run trips), so {spare} trucks were never needed, not "
        "even on the busiest day.",
        "p95": "Enough on 95% of days",
        "p99": "Enough on 99% of days",
        "in_use": "Trucks that have run trips",
        "owned": "Trucks owned",
        "productivity": "Fleet productivity",
        "f_miles_month": "Average miles per truck per month",
        "n_miles_month": "Total miles ÷ truck-months with trips",
        "f_rev_truck_week": "Average revenue per truck per week",
        "n_rev_truck_week": "Revenue ÷ truck-weeks with trips",
        "f_util": "Fleet utilization",
        "f_downtime": "Maintenance downtime",
        "n_downtime": "Total hours trucks were out of service for maintenance or repair",
        "busy_dist": "How many trucks work each day",
        "busy_dist_note": "Each bar is the number of days with that many trucks working. On "
        "average {avg} trucks a day; 95% of days need no more than {p95}.",
        "busy_x": "Trucks working that day",
        "days_y": "Days",
        "util_dist": "Utilization reported by the source system",
        "util_note": "A rate the source system reports for each truck every month. The data "
        "doesn't say how it is calculated and it exceeds 100%, so it is only used to compare "
        "trucks.",
        "util_x": "Reported utilization (%)",
        "trucks_y": "Trucks",
        "status": "Fleet by status",
        "ran_trips": "ran trips",
        "never_ran": "never ran a trip",
        "idle_trucks": "The {n} trucks that never ran a trip",
        "idle_note": "These trucks bring no revenue but still cost {cost} in maintenance. They are "
        "the first list to review when resizing the fleet.",
        "idle_cols": {
            "truck_id": "Truck",
            "make": "Make",
            "model_year": "Model year",
            "status": "Status",
            "maintenance_events": "Maintenance jobs",
            "maintenance_cost": "Maintenance cost (USD)",
        },
        "bought_vs_burned": "Fuel bought vs fuel used on trips",
        "bought_note": "Blue is what fuel cards bought; orange is what trips recorded as used. The "
        "gap between them needs reconciling.",
        "bought": "Fuel bought",
        "burned": "Fuel used on trips",
        "ratio": "Fuel bought ÷ fuel used",
        "ratio_note": "1 means exactly as much was bought as used. Above 1 means more was bought "
        "than trips recorded.",
        "price_trend": "Average fuel price",
        "spend": "Fuel cost",
        "spend_note": "Fuel cost = gallons bought × price. Compare with the price and volume "
        "charts to see whether a change comes from price or from volume.",
        "p_optimize": "Optimization recommendations",
        "d_optimize": "Actions that cut cost or raise profit, with their yearly value and how "
        "certain each is.",
        "o_scope": "Computed over all the data from {a} to {b}; the sidebar date range doesn't "
        "change it.",
        "proj_heading": "Project and data source",
        "proj": {
            "title": "Project",
            "goal": "Problem",
            "data": "Dataset",
            "company": "Company",
            "source": "Data source",
        },
        "proj_title": "Analysing and optimizing the operations of a road freight carrier",
        "proj_goal": "Find ways to cut operating cost by at least 3% a year and improve delivery "
        "performance, from the company's operating data",
        "proj_data": "Logistics Operations Database: {tables} tables, {rows} rows, trips from {a} "
        "to {b}",
        "proj_company": "A US road freight carrier; the data is synthetic, so the company is not "
        "named: {trucks} trucks, {drivers} drivers, {customers} customers, {routes} lanes, {trips} "
        "trips",
        "proj_source": "Kaggle, by yogape: "
        "kaggle.com/datasets/yogape/logistics-operations-database",
        "o_tip_hint": "Hover over or tap each card to see how its figure is computed.",
        "o_tip_target": [
            "Target = 3% of the average measured operating cost per year.",
            "Measured operating cost: {base} a year (fuel, maintenance and claims in 2022–2024, "
            "including maintenance of trucks that never ran).",
            "3% × {base} = {target} a year.",
        ],
        "o_tip_measured": "Yearly maintenance of trucks that never ran a trip; it stops for good "
        "once they are disposed of:",
        "o_tip_measured_end": "Condition: dispose of, or stop maintaining, all {n} trucks. "
        "Operations are not affected since these trucks never ran a trip.",
        "o_tip_upper": "Maximum value of the actions that need an internal decision or customers "
        "to accept a change:",
        "o_tip_upper_end": "It is a maximum because it assumes customers accept the full increase "
        "without cutting volume, and the remaining trucks take over every trip of those withdrawn. "
        "In practice it is usually lower.",
        "o_tip_sum": "Total: {total} = {pct} of the target.",
        "o_tip_total": "Measured savings {m} + maximum potential {u} = {total} ({pct} of the "
        "target).",
        "o_tip_gap": "To reach the {target} target: do all of the measured part ({m}) and get at "
        "least {gap} more from the potential actions, i.e. {share} of the maximum potential.",
        "o_tip_example": "For example, raising the fuel surcharge ({fsc}) is enough on its own if "
        "customers accept at least {fsc_share} of the proposed increase.",
        "o_tip_done": "The measured part alone reaches the {target} target.",
        "o_target": "Savings target",
        "n_target": "3% of measured operating cost, per year",
        "o_measured": "Measured savings",
        "n_measured": "{pct} of target · costs in the data that stop for certain",
        "o_upper": "Maximum potential",
        "n_upper": "If customers or management accept the change; usually lower in practice",
        "o_total": "Total potential",
        "n_total": "{pct} of target if everything is done",
        "o_unexplained": "Besides, {amount} a year of fuel spend is unexplained (more bought than "
        "recorded as burned). It is not added to the total because it isn't proven loss; it needs "
        "reconciling first.",
        "o_chart": "Yearly value of each recommendation",
        "o_chart_note": "Green is a measured saving, blue a maximum potential. The target is "
        "{target} a year.",
        "o_table": "Recommendations",
        "o_cols": [
            "Area",
            "Action",
            "Scope",
            "Value per year",
            "Type",
            "Evidence",
        ],
        "o_areas": {
            "Fleet": "Fleet",
            "Network": "Network",
            "Lanes": "Lane pricing",
            "Data": "Data",
            "Checked": "Checked",
        },
        "o_types": {
            "measured": "Measured saving",
            "upper bound": "Maximum potential",
            "risk sharing": "Risk sharing",
            "unexplained": "Unexplained",
            "estimate": "Estimate (hypothesis)",
            "no signal": "No signal",
        },
        "o_checked": "Checked and not recommended",
        "o_checked_note": "A lever is recommended only if its signal repeats across years. These "
        "were checked on the data and failed, or were dropped by the project owner.",
        "o_checked_cols": ["Lever", "Evidence"],
        "o_fleet": "Fleet size",
        "o_growth": "Assumed trip volume",
        "o_growth_now": "Current volume",
        "o_growth_up": "+{g}%",
        "o_growth_help": "Trucks needed if trips per day stay at the 2022–2024 level or grow by "
        "5%, 10% or 20%. The savings totals at the top of the page use the current volume.",
        "o_needed": "Trucks needed",
        "n_needed": "Enough on 99% of days, after maintenance downtime and trips without a truck "
        "ID",
        "o_owned": "Trucks owned",
        "o_in_use": "Trucks that have run trips",
        "o_surplus": "Trucks above the need",
        "o_needed_chart": "Trucks needed by trip volume",
        "o_needed_note": "Against {owned} trucks owned and {in_use} that have run trips. The "
        "busiest day needed {busiest}; {above} of {days} days needed more than the recommendation "
        "at the current volume, which short-term rental can cover.",
        "o_tiers": "Disposal in tiers",
        "o_tier_cols": [
            "Tier",
            "Trucks",
            "Count",
            "Back to service",
            "Maintenance per year",
            "Type",
        ],
        "o_tier_status": {
            "Inactive": "Inactive, never ran",
            "Maintenance": "In maintenance, never ran",
            "Active (lowest mileage)": "In use, lowest mileage",
        },
        "o_tiers_note": "Tiers 1–2 never ran a trip: giving them up doesn't touch operations, so "
        "the saving is certain. Tier 3 is a maximum potential because the remaining trucks must "
        "take over its trips. Resale value isn't in the data and isn't counted.",
        "o_lanes": "Lane pricing",
        "o_cap": "Largest rate increase per lane",
        "o_cap_none": "No cap (theoretical)",
        "o_s1": "S1 · Standardize the fuel surcharge",
        "n_s1": "Raise low surcharges to the median",
        "o_s2": "S2 · Raise rates on low-margin lanes",
        "n_s2": "Toward the median margin, within the chosen cap",
        "o_s12": "S1 + S2 per year",
        "n_s12": "{pct} of target",
        "o_loss": "Break-even volume loss",
        "n_loss": "Median: a repriced lane can lose this much volume and still earn no less than "
        "today",
        "o_lane_table": "Results by lane",
        "o_lane_note": "Break-even driver cost: the lane loses money only if driver cost per mile "
        "exceeds it (instead of the driver pay the data lacks). Lanes that need no change show 0 "
        "for S1 and S2.",
        "o_lane_cols": {
            "lane": "Lane",
            "group": "Action",
            "margin": "Contribution margin (%)",
            "fsc_rate": "Current surcharge (USD/mile)",
            "s1": "S1 (USD/year)",
            "s2": "S2 (USD/year)",
            "increase": "Rate increase (%)",
            "loss": "Break-even volume loss (%)",
            "break_even": "Break-even driver cost (USD/mile)",
        },
        "o_s3": "S3 · Surcharge indexed to the fuel price (simulation)",
        "o_s3_group": "Fuel surcharge that follows the price",
        "o_chain": "Trip chaining: nearest free truck (simulation)",
        "o_chain_moved": "Trips needing a move",
        "n_chain_moved": "As today {today} (observed {seen})",
        "o_chain_miles": "Empty miles",
        "n_chain_miles": "{near} against {today} million miles a year in the replay",
        "o_chain_move": "Average empty move",
        "n_chain_move": "About {h} h of driving; {day} of moves within one driving day ({limit} h)",
        "o_chain_value": "Maximum fuel saving per year",
        "n_chain_value": "−{cut} × {fuel} of fuel bought off trips; an estimate, not in the total",
        "o_chain_tip": [
            "From the data: {speed} mph, {mpg} miles a gallon, {price} a gallon → an empty "
            "mile costs {per_mile}.",
            "Model: empty miles fall by {cut}, i.e. {model} of fuel a year.",
            "But the fuel bought off trips is only {off_trip} a year (about {off_miles} "
            "million miles), less than the model's empty miles.",
            "So only the cut is applied: {cut} × {off_trip} = {saving} a year, a maximum.",
        ],
        "o_chain_table": "Today's dispatching and the nearest truck",
        "o_chain_note": "Replays the {loads} loads at their actual pickup and delivery times. Each "
        "load goes to the free truck closest to its pickup city that can drive there in time (a "
        "truck already there first). Distances follow the data's lanes, detouring where two cities "
        "have no lane, so they are longer than real roads. No fixed limit on the empty drive: "
        "trucks piling up in cities that send little back must drive far, and any limit up to 24 h "
        "needs thousands of extra trucks. Keep moves within one driving day ({h} h); beyond that, "
        "look for a return load on the spot rather than driving empty.",
        "o_chain_cols": ["Measure", "As today", "Nearest truck"],
        "o_chain_rows": [
            "Trips needing a move",
            "Moves a year",
            "Empty miles a year",
            "Miles per move",
            "Moves within one driving day ({h} h)",
            "Trucks needed (replay)",
        ],
        "o_s3_note": "The surcharge follows the monthly fuel price, with a base of {base} per "
        "gallon so that 3-year revenue is unchanged. High-price years earn more, low-price years "
        "less: profit depends less on fuel prices. Not counted as a saving.",
        "o_s3_actual": "Actual surcharge",
        "o_s3_indexed": "Fuel-indexed surcharge",
        "o_gaps": "Data-process improvements",
        "o_gaps_note": "Tier 1 is a process or configuration change in existing systems, close to "
        "free. Tier 2 needs telematics devices; prices are indicative public figures, to be "
        "replaced by vendor quotes.",
        "o_gap_cols": [
            "Gap",
            "Evidence",
            "Cost of not doing",
            "Tier-1 measure (process)",
            "Tier-2 measure (device)",
        ],
        "o_tele_cost": "Telematics cost per year",
        "n_tele_cost": "{trucks} trucks in use · subscription and devices spread over 3 years",
        "o_tele_break": "Telematics break-even",
        "n_tele_break": "Share of fuel spend it must save to pay for itself",
        "o_sources": "Indicative price sources",
        "r_export": "Export report",
        "r_title": "Transport management report",
        "r_period": "Period: {a} – {b}",
        "r_generated": "Exported: {d}",
        "r_page": "Page",
        "r_toc": "Contents",
        "r_figs": "List of figures",
        "r_tabs": "List of tables",
        "r_summary": "Executive summary",
        "r_sum_results": "Key results for the period",
        "r_sum_act": "Act now",
        "r_sum_watch": "Keep watching",
        "r_sum_savings": "Savings opportunity",
        "r_fig": "Figure",
        "r_tab": "Table",
        "r_running": "Creating the report… {pct}",
        "r_done": "Done · {name}",
        "r_format": "Format",
        "r_make": "Create report",
        "r_download": "Download",
        "r_no_browser": "Microsoft Edge or Google Chrome was not found, so no PDF can be made. "
        "Choose HTML.",
        "r_note": "Figures computed from the data by the analysis layer. Profit is contribution "
        "profit, before driver pay and overhead, which the data doesn't have.",
        "r_late": "Is there a cause behind late deliveries?",
        "r_late_note": "{share} of deliveries are more than 2 hours late. A cause is worth acting "
        "on only if a group's late rate repeats between 2022–2023 and the last year (correlation "
        "0.7 or more).",
        "r_late_cols": [
            "By",
            "Groups",
            "Spread of late rates (pts)",
            "Correlation between periods",
            "Signal",
        ],
        "r_dims": {
            "city": "Delivery city",
            "customer": "Customer",
            "appointment_hour": "Appointment hour",
            "lane": "Lane",
            "driver": "Driver",
        },
        "r_yes": "Yes",
        "r_no": "No",
        "d_tables": "Data tables",
        "d_rows": "Data rows",
        "d_rules": "Quality rules",
        "d_errors": "Rows with a serious error",
        "findings": "Rows flagged by each quality rule",
        "findings_note": "Red is a serious error (the row is left out of the calculations it "
        "affects); amber is a warning (use with care). Flagged rows are kept, never deleted.",
        "severity": {"error": "Serious error", "warn": "Warning"},
        "trust": "How far the data can be trusted",
        "trust_rows": [
            ("Table relationships, money amounts, monthly aggregate tables", "Trusted", "ok"),
            (
                "About 2% of driver/truck codes missing; some deliveries recorded before pickup; "
                "utilization above 100%",
                "Use with care",
                "warn",
            ),
            (
                "State on fuel purchases, facility code on delivery events, idle hours",
                "Not used",
                "no",
            ),
        ],
        "trust_cols": ["Data", "Trust level"],
        "glossary": "KPI definitions",
        "glossary_note": "The value column is each KPI for the whole fleet over the selected "
        "range, so each definition can be checked against the numbers on the other pages.",
        "g_cols": {
            "area": "Area",
            "kpi": "KPI",
            "formula": "Definition and formula",
            "unit": "Unit",
            "value": "Fleet value",
        },
    },
}
