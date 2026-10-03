# 03 · Định nghĩa KPI

> CRISP-DM pha 3 (Chuẩn bị dữ liệu). Sinh tự động bằng `uv run logops build` từ danh mục trong `src/logops/metrics/kpis.py`; không sửa tay. · Bản tiếng Anh: [03-kpi-definitions.md](03-kpi-definitions.md) · Spec: [SPEC-metrics.vi.md](../SPEC-metrics.vi.md)

Giá trị đội xe tính từ 2022-01-01 đến 2025-01-02. Mọi tỷ lệ là tổng chia tổng. Chi phí không gán được vào chuyến nằm ở dòng *Không gán được*, nên các nhóm luôn cộng lại bằng tổng đội xe. Dùng `uv run logops kpi --by route` để xem theo từng nhóm.

## Chi phí

| KPI | Đơn vị | Công thức | Giá trị đội xe |
|---|---|---|---:|
| `revenue` | USD | Σ cước + phụ phí nhiên liệu + phụ phí khác | 298.621.428,9 |
| `measured_cost` | USD | Σ nhiên liệu + bảo dưỡng + sự cố (dữ liệu không có lương tài xế) | 103.976.737,1 |
| `cost_per_mile` | USD/mile | measured_cost ÷ Σ dặm | 0,851 |
| `fuel_cost_per_mile` | USD/mile | Σ chi phí nhiên liệu ÷ Σ dặm | 0,783 |
| `maintenance_cost_per_mile` | USD/mile | Σ chi phí bảo dưỡng ÷ Σ dặm | 0,047 |
| `safety_cost_per_mile` | USD/mile | Σ bồi thường sự cố ÷ Σ dặm | 0,022 |
| `revenue_per_mile` | USD/mile | revenue ÷ Σ dặm | 2,445 |
| `contribution` | USD | revenue − measured_cost (trước lương tài xế) | 194.644.691,8 |
| `contribution_margin_pct` | % | contribution ÷ revenue | 65,2 |
| `out_of_route_pct` | % | Σ (dặm thực tế − dặm chuẩn của tuyến) ÷ Σ dặm chuẩn | 2,951 |

## Nhiên liệu

| KPI | Đơn vị | Công thức | Giá trị đội xe |
|---|---|---|---:|
| `mpg` | miles/gallon | Σ dặm ÷ Σ gallon tiêu thụ | 6,448 |
| `fuel_purchased_to_burned` | ratio | Σ gallon mua ÷ Σ gallon tiêu thụ (kiểm soát thẻ nhiên liệu) | 1,294 |

## Độ tin cậy giao hàng

| KPI | Đơn vị | Công thức | Giá trị đội xe |
|---|---|---|---:|
| `on_time_pct` | % | lần giao có \|thực tế − giờ hẹn\| ≤ cửa sổ ÷ số lần giao (cửa sổ 120 phút = on_time_flag) | 44,6 |
| `not_late_pct` | % | lần giao có thực tế ≤ giờ hẹn ÷ số lần giao | 33,3 |
| `avg_detention_min` | minutes | Σ phút chờ ÷ số lần lấy và giao | 91,5 |
| `detention_hours` | hours | Σ phút chờ ÷ 60 | 260.607,1 |

## Tài sản

| KPI | Đơn vị | Công thức | Giá trị đội xe |
|---|---|---|---:|
| `miles_per_truck_month` | miles | Σ dặm ÷ số tháng-xe có ít nhất một chuyến | 36.883,8 |
| `utilization` | % | trung bình utilization_rate (chỉ để so sánh xe; có thể vượt 100%) | 83,0 |
| `downtime_hours` | hours | Σ giờ dừng do bảo dưỡng | 72.230,5 |

## An toàn

| KPI | Đơn vị | Công thức | Giá trị đội xe |
|---|---|---|---:|
| `incidents_per_million_miles` | per 1M miles | số sự cố ÷ Σ dặm × 1.000.000 | 1,392 |
| `preventable_pct` | % | sự cố phòng tránh được ÷ số sự cố | 37,6 |

## Cách gán chi phí vào chuyến

- **Nhiên liệu:** tiền mua nhiên liệu trong tháng, chia cho các chuyến trong tháng theo gallon tiêu thụ. Phiếu nhiên liệu không gán đúng chuyến (gallon mua nhiều hơn gallon tiêu thụ 29%).
- **Bảo dưỡng:** chi phí của xe trong tháng, chia cho các chuyến của xe trong tháng theo dặm. Bảo dưỡng của xe không chạy chuyến nào trong tháng là *Không gán được*.
- **Sự cố:** gán thẳng theo chuyến.
- **Lương tài xế:** dữ liệu không có nên không tính. Biên đóng góp là trước lương tài xế.

## Không đo, và vì sao

- **Thời gian chạy không tải:** `idle_time_hours` là nhiễu ngẫu nhiên (tương quan ≈ 0 với thời gian chuyến, quãng đường và nhiên liệu).
- **Giá nhiên liệu theo địa điểm:** giá giữa các thành phố chỉ chênh 0,02 USD/gallon.
- **Theo kho:** `facility_id` trên sự kiện giao nhận gần như ngẫu nhiên; dùng `location_city` thay thế.
