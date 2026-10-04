# 03 · Định nghĩa KPI

> CRISP-DM pha 3 (Chuẩn bị dữ liệu). Sinh tự động bằng `uv run logops build` từ danh mục trong `src/logops/metrics/kpis.py`; không sửa tay. · Bản tiếng Anh: [03-kpi-definitions.md](03-kpi-definitions.md) · Spec: [SPEC-metrics.vi.md](../SPEC-metrics.vi.md)

Giá trị đội xe tính từ 2022-01-01 đến 2025-01-02. Mọi tỷ lệ là tổng chia tổng. Chi phí không gán được vào chuyến nằm ở dòng *Không gán được*, nên các nhóm luôn cộng lại bằng tổng đội xe. Dùng `uv run logops kpi --by route` để xem theo từng nhóm.

## Chi phí

| KPI | Đơn vị | Công thức | Giá trị đội xe |
|---|---|---|---:|
| Doanh thu (`revenue`) | USD | Doanh thu = cước vận chuyển + phụ phí nhiên liệu + phụ phí khác | 298.621.428,9 |
| Chi phí vận hành đo được (`measured_cost`) | USD | Chi phí vận hành đo được = nhiên liệu + bảo dưỡng + bồi thường sự cố (dữ liệu không có lương tài xế) | 103.976.737,1 |
| Chi phí vận hành mỗi dặm (`cost_per_mile`) | USD/dặm | Chi phí vận hành mỗi dặm = chi phí vận hành đo được ÷ tổng số dặm | 0,851 |
| Chi phí nhiên liệu mỗi dặm (`fuel_cost_per_mile`) | USD/dặm | Chi phí nhiên liệu mỗi dặm = chi phí nhiên liệu ÷ tổng số dặm | 0,783 |
| Chi phí bảo dưỡng mỗi dặm (`maintenance_cost_per_mile`) | USD/dặm | Chi phí bảo dưỡng mỗi dặm = chi phí bảo dưỡng ÷ tổng số dặm | 0,047 |
| Chi phí sự cố mỗi dặm (`safety_cost_per_mile`) | USD/dặm | Chi phí sự cố mỗi dặm = bồi thường sự cố ÷ tổng số dặm | 0,022 |
| Doanh thu mỗi dặm (`revenue_per_mile`) | USD/dặm | Doanh thu mỗi dặm = doanh thu ÷ tổng số dặm | 2,445 |
| Lợi nhuận đóng góp (`contribution`) | USD | Lợi nhuận đóng góp = doanh thu − chi phí vận hành đo được (chưa trừ lương tài xế) | 194.644.691,8 |
| Biên đóng góp (`contribution_margin_pct`) | % | Biên đóng góp = lợi nhuận đóng góp ÷ doanh thu | 65,2 |
| Tỷ lệ chạy vượt quãng chuẩn (`out_of_route_pct`) | % | Tỷ lệ chạy vượt quãng chuẩn = (số dặm thực tế − số dặm chuẩn của tuyến) ÷ số dặm chuẩn | 2,951 |

## Nhiên liệu

| KPI | Đơn vị | Công thức | Giá trị đội xe |
|---|---|---|---:|
| Hiệu suất nhiên liệu (`mpg`) | dặm/gallon | Hiệu suất nhiên liệu = tổng số dặm ÷ số gallon tiêu thụ | 6,448 |
| Tỷ lệ nhiên liệu mua / tiêu thụ (`fuel_purchased_to_burned`) | lần | Tỷ lệ nhiên liệu mua / tiêu thụ = số gallon mua ÷ số gallon tiêu thụ theo chuyến (kiểm soát thẻ nhiên liệu) | 1,294 |

## Độ tin cậy giao hàng

| KPI | Đơn vị | Công thức | Giá trị đội xe |
|---|---|---|---:|
| Giao hàng đúng hẹn (OTD) (`on_time_pct`) | % | Giao hàng đúng hẹn (OTD) = số lần giao trong ±2 giờ so với giờ hẹn ÷ tổng số lần giao | 44,6 |
| Giao không trễ hẹn (`not_late_pct`) | % | Giao không trễ hẹn = số lần giao đến trước hoặc đúng giờ hẹn ÷ tổng số lần giao | 33,3 |
| Thời gian chờ bình quân (`avg_detention_min`) | phút | Thời gian chờ bình quân = tổng số phút chờ ÷ số lần lấy và giao hàng | 91,5 |
| Tổng thời gian chờ (`detention_hours`) | giờ | Tổng thời gian chờ = tổng số phút chờ ÷ 60 | 260.607,1 |

## Tài sản

| KPI | Đơn vị | Công thức | Giá trị đội xe |
|---|---|---|---:|
| Quãng đường mỗi xe mỗi tháng (`miles_per_truck_month`) | dặm | Quãng đường mỗi xe mỗi tháng = tổng số dặm ÷ số tháng-xe có ít nhất một chuyến | 36.883,8 |
| Hệ số sử dụng xe theo báo cáo (`utilization`) | % | Hệ số sử dụng xe theo báo cáo = trung bình hệ số sử dụng hằng tháng của từng xe (dữ liệu không định nghĩa và có thể vượt 100%; chỉ dùng để so sánh các xe) | 83,0 |
| Thời gian dừng xe bảo dưỡng (`downtime_hours`) | giờ | Thời gian dừng xe bảo dưỡng = tổng số giờ xe ngừng hoạt động để bảo dưỡng, sửa chữa | 72.230,5 |

## An toàn

| KPI | Đơn vị | Công thức | Giá trị đội xe |
|---|---|---|---:|
| Tần suất sự cố (`incidents_per_million_miles`) | lần/triệu dặm | Tần suất sự cố = số sự cố ÷ tổng số dặm × 1.000.000 | 1,392 |
| Tỷ lệ sự cố phòng tránh được (`preventable_pct`) | % | Tỷ lệ sự cố phòng tránh được = số sự cố phòng tránh được ÷ tổng số sự cố | 37,6 |

## Cách gán chi phí vào chuyến

- **Nhiên liệu:** tiền mua nhiên liệu trong tháng, chia cho các chuyến trong tháng theo gallon tiêu thụ. Phiếu nhiên liệu không gán đúng chuyến (gallon mua nhiều hơn gallon tiêu thụ 29%).
- **Bảo dưỡng:** chi phí của xe trong tháng, chia cho các chuyến của xe trong tháng theo dặm. Bảo dưỡng của xe không chạy chuyến nào trong tháng là *Không gán được*.
- **Sự cố:** gán thẳng theo chuyến.
- **Lương tài xế:** dữ liệu không có nên không tính. Biên đóng góp là trước lương tài xế.

## Không đo, và vì sao

- **Thời gian chạy không tải:** `idle_time_hours` là nhiễu ngẫu nhiên (tương quan ≈ 0 với thời gian chuyến, quãng đường và nhiên liệu).
- **Giá nhiên liệu theo địa điểm:** giá giữa các thành phố chỉ chênh 0,02 USD/gallon.
- **Theo kho:** `facility_id` trên sự kiện giao nhận gần như ngẫu nhiên; dùng `location_city` thay thế.
