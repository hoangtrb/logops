# 02 · Báo cáo chất lượng dữ liệu

> CRISP-DM pha 2 (Hiểu dữ liệu). Sinh tự động bằng `uv run logops build` từ `data/warehouse.duckdb`; không sửa tay. · Bản tiếng Anh: [02-data-quality-report.md](02-data-quality-report.md) · Phân tích: [02-data-understanding.vi.md](02-data-understanding.vi.md)

## 1. Tóm tắt

| Chỉ số | Giá trị |
|---|---:|
| Giai đoạn dữ liệu | 2022-01-01 đến 2024-12-31 |
| Số bảng / số dòng | 14 / 549.706 |
| Số quy tắc đã chạy / số quy tắc có vi phạm | 69 / 14 |
| Số dòng có ít nhất một vấn đề (kể cả cảnh báo) | 365.147 (66,4%) |
| Số dòng có ít nhất một lỗi mức error | 8.084 (1,5%) |

Không dòng nào bị xóa. Mọi vi phạm được ghi vào cột `dq_issues` của dòng đó và tổng hợp trong bảng `dq_findings`.

## 2. Số liệu nền kinh doanh

Đầu vào cho tiêu chí thành công trong [01-business-understanding.vi.md](01-business-understanding.vi.md) §5. Chi phí vận hành gồm nhiên liệu, bảo dưỡng và bồi thường sự cố; dữ liệu không có lương tài xế.

| Chỉ số | Giá trị |
|---|---:|
| Doanh thu (cước + phụ phí nhiên liệu + phụ phí khác) | 298,62 triệu USD |
| Chi phí vận hành (nhiên liệu + bảo dưỡng + bồi thường sự cố) | 103,98 triệu USD |
| Chi phí nhiên liệu | 95,59 triệu USD |
| Chi phí bảo dưỡng | 5,73 triệu USD |
| Bồi thường sự cố | 2,65 triệu USD |
| Số dặm đã chạy | 122.159.201 |
| Chi phí vận hành mỗi dặm | 0,851 USD |
| MPG đội xe (tổng dặm ÷ tổng gallon) | 6,45 |
| Giao hàng trong khung ±2 giờ so với lịch hẹn (`on_time_flag`) | 44,6% |
| Lấy hàng trong khung ±2 giờ so với lịch hẹn (`on_time_flag`) | 66,7% |
| Giao hàng không trễ (thực tế ≤ lịch hẹn) | 33,3% |
| Số giờ chờ (detention) | 260.607 |
| Mức sử dụng xe trung bình | 83,0% |

## 3. Phát hiện

| Mức độ | Quy tắc | Bảng.cột | Số dòng bị đánh dấu | % của bảng | Khóa mẫu |
|---|---|---|---:|---:|---|
| error | `idle_exceeds_duration` | `trips` | 7.450 | 8,7% | `TRIP00000016`, `TRIP00000030`, `TRIP00000033` |
| error | `time_order` | `delivery_events.actual_datetime` | 486 | 0,3% | `EVT00000216`, `EVT00000268`, `EVT00000950` |
| error | `time_order` | `delivery_events.scheduled_datetime` | 175 | 0,1% | `EVT00001640`, `EVT00003132`, `EVT00003258` |
| warn | `geo_mismatch` | `fuel_purchases.location_state` | 187.229 | 95,3% | `FUEL00000001`, `FUEL00000002`, `FUEL00000003` |
| warn | `geo_mismatch` | `delivery_events.facility_id` | 164.935 | 96,6% | `EVT00000001`, `EVT00000002`, `EVT00000003` |
| warn | `fk_missing` | `fuel_purchases.driver_id` | 3.988 | 2,0% | `FUEL00000002`, `FUEL00000005`, `FUEL00000024` |
| warn | `fk_missing` | `fuel_purchases.truck_id` | 3.880 | 2,0% | `FUEL00000012`, `FUEL00000038`, `FUEL00000112` |
| warn | `fk_missing` | `trips.driver_id` | 1.714 | 2,0% | `TRIP00000067`, `TRIP00000104`, `TRIP00000257` |
| warn | `fk_missing` | `trips.trailer_id` | 1.680 | 2,0% | `TRIP00000251`, `TRIP00000272`, `TRIP00000317` |
| warn | `fk_missing` | `trips.truck_id` | 1.672 | 2,0% | `TRIP00000070`, `TRIP00000074`, `TRIP00000088` |
| warn | `range` | `truck_utilization_metrics.utilization_rate` | 436 | 13,2% | `TRK00001\|2022-03-01`, `TRK00001\|2022-06-01`, `TRK00001\|2022-10-01` |
| warn | `geo_mismatch` | `safety_incidents.location_state` | 163 | 95,9% | `INC00000001`, `INC00000002`, `INC00000003` |
| warn | `fk_missing` | `safety_incidents.driver_id` | 1 | 0,6% | `INC00000086` |
| warn | `fk_missing` | `safety_incidents.truck_id` | 1 | 0,6% | `INC00000060` |

**Các quy tắc không phát hiện lỗi:**

- `customers`: `pk_unique`
- `delivery_events`: `fk_orphan:facility_id`, `fk_orphan:load_id`, `fk_orphan:trip_id`, `pk_unique`, `range`, `fk_missing:facility_id`, `fk_missing:load_id`, `fk_missing:trip_id`, `geo_mismatch:location_state`
- `driver_monthly_metrics`: `fk_orphan:driver_id`, `pk_unique`, `range`, `fk_missing:driver_id`
- `drivers`: `pk_unique`, `time_order:termination_date`
- `facilities`: `pk_unique`
- `fuel_purchases`: `fk_orphan:driver_id`, `fk_orphan:trip_id`, `fk_orphan:truck_id`, `pk_unique`, `range`, `amount_mismatch`, `fk_missing:trip_id`
- `loads`: `fk_orphan:customer_id`, `fk_orphan:route_id`, `pk_unique`, `range`, `fk_missing:customer_id`, `fk_missing:route_id`
- `maintenance_records`: `fk_orphan:truck_id`, `pk_unique`, `range`, `amount_mismatch`, `fk_missing:truck_id`
- `routes`: `pk_unique`
- `safety_incidents`: `fk_orphan:driver_id`, `fk_orphan:trip_id`, `fk_orphan:truck_id`, `pk_unique`, `range`, `amount_mismatch`, `fk_missing:trip_id`
- `trailers`: `pk_unique`
- `trips`: `fk_orphan:driver_id`, `fk_orphan:load_id`, `fk_orphan:trailer_id`, `fk_orphan:truck_id`, `pk_unique`, `range`, `fk_missing:load_id`
- `truck_utilization_metrics`: `fk_orphan:truck_id`, `pk_unique`, `fk_missing:truck_id`
- `trucks`: `pk_unique`

## 4. Định nghĩa quy tắc

- `pk_unique`: Khóa chính bị trùng hoặc rỗng.
- `fk_missing`: Khóa ngoại rỗng: dòng không nối được với bảng cha.
- `fk_orphan`: Khóa ngoại trỏ tới dòng không tồn tại ở bảng cha.
- `range`: Giá trị ngoài khoảng hợp lý (ví dụ MPG ngoài 3–12, chi phí âm, mức sử dụng trên 100%).
- `idle_exceeds_duration`: Số giờ chạy không tải lớn hơn tổng thời gian chuyến.
- `amount_mismatch`: Tổng lệch hơn 1% so với các thành phần (gallon × giá; công + phụ tùng; hư hại xe + hàng).
- `time_order`: Thứ tự thời gian vô lý (giao trước khi lấy; nghỉ việc trước khi tuyển).
- `geo_mismatch`: Địa điểm không nhất quán: cặp thành phố/bang không có trong danh sách kho và điểm đầu/cuối tuyến, hoặc thành phố của sự kiện khác thành phố của kho.

## 5. Kiểm tra chéo

| Kiểm tra | Kết quả |
|---|---:|
| Dòng trùng tuyệt đối, mọi bảng | 0 |
| Tháng trong `driver_monthly_metrics` lệch > 2% so với số tính lại từ trips + loads | 0,0% |
| Tháng trong `truck_utilization_metrics` lệch > 2% so với trips, loads và bảo dưỡng | 0,0% |
| Sự kiện có `on_time_flag` = (\|thực tế − lịch hẹn\| ≤ 120 phút) | 100,0% |
| Sự kiện sớm hơn 2 giờ (bị tính là *không* đúng giờ) | 5,5% |
| Sự kiện giao nhận có `location_city` là điểm đầu (lấy hàng) hoặc điểm cuối (giao hàng) của tuyến | 100,0% |
| Sự kiện giao nhận có thành phố của `facility_id` là điểm đầu/cuối tuyến đó | 3,4% |

## 6. Giá trị thiếu

Các cột có ít nhất một giá trị rỗng. Mọi cột khác đều đầy đủ.

| Cột | Số giá trị rỗng | % |
|---|---:|---:|
| `drivers.termination_date` | 124 | 82,7% |
| `trips.driver_id` | 1.714 | 2,0% |
| `trips.truck_id` | 1.672 | 2,0% |
| `trips.trailer_id` | 1.680 | 2,0% |
| `fuel_purchases.truck_id` | 3.880 | 2,0% |
| `fuel_purchases.driver_id` | 3.988 | 2,0% |
| `safety_incidents.truck_id` | 1 | 0,6% |
| `safety_incidents.driver_id` | 1 | 0,6% |
