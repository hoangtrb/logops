# Đánh giá · Module 2: `metrics`

> CRISP-DM pha 3 · Bản tiếng Anh: [02-metrics.md](02-metrics.md) · Spec:
> [SPEC-metrics.vi.md](../../SPEC-metrics.vi.md) · Định nghĩa KPI:
> [03-kpi-definitions.vi.md](../03-kpi-definitions.vi.md) · Tổng kết: [SUMMARY.vi.md](../SUMMARY.vi.md)
> **Trạng thái:** hoàn tất ngày 03/10/2026, chưa commit · **Nguyên tắc:** chỉ ghi điều đã kiểm chứng.

## 1. Output so với spec

| Output trong spec | Đã giao | Bằng chứng |
|---|---|---|
| O1. 3 view nền | ✅ `trip_economics` (85.410 dòng), `delivery_performance` (170.820), `truck_economics` (120) | Số dòng khớp bảng gốc; test phân bổ chi phí trên dữ liệu mẫu |
| O2. Hàm `kpi()` | ✅ 21 KPI; nhóm theo tháng, tuyến, khách hàng, loại khách hàng, xe, tài xế, thành phố; lọc ngày; cửa sổ đúng giờ là tham số | 13 test trên dữ liệu mẫu tính tay được |
| O3. Lệnh `logops kpi` | ✅ `--by`, `--from`, `--to`, `--window`, `--kpis` | Chạy trên dữ liệu thật; test CLI |
| O4. Tài liệu KPI tự sinh | ✅ `docs/03-kpi-definitions` EN/VI, sinh bởi `logops build` | Test: đủ 21 KPI, 2 ngôn ngữ, kết quả ổn định |
| Đánh giá + tổng kết | ✅ File này, `01-data-platform` và `SUMMARY` | — |

## 2. Tiêu chí thành công

| Tiêu chí | Kết quả | Bằng chứng |
|---|---|---|
| 1. Khớp báo cáo chất lượng dữ liệu | ✅ Doanh thu 298.621.428,94 USD; chi phí đo được 103.976.737,14 USD; MPG 6,448; đúng giờ 44,6% | Test tích hợp so với bảng gốc |
| 2. Nhóm + "Không gán được" = tổng đội xe | ✅ | Test trên dữ liệu thật (5 kiểu nhóm) và dữ liệu mẫu (6 kiểu nhóm) |
| 3. Cửa sổ đúng giờ là tham số | ✅ 120 phút cho đúng `on_time_flag` | Test: 0 phút → 0%, 200 phút → 100% trên dữ liệu mẫu |
| 4. Lọc thời gian đúng | ✅ Năm 2024: doanh thu và chi phí bảo dưỡng khớp bảng gốc | Test tích hợp |
| 5. Test + ruff | ✅ 29 test mới; tổng 76 test qua; ruff sạch | `pytest`, `ruff check` |
| 6. Build chậm thêm ≤ 5 giây | ✅ 6,6–7,4 giây sau khi thêm module, so với 8,0 giây ở lần build cuối trước đó (thời gian dao động giữa các lần chạy) | Thời gian in ra bởi `logops build` |

## 3. KPI đội xe (01/2022 – 01/2025)

| Nhóm | KPI | Giá trị |
|---|---|---|
| Chi phí | Chi phí đo được / dặm | 0,851 USD (nhiên liệu 0,783; bảo dưỡng 0,047; sự cố 0,022) |
| | Doanh thu / dặm | 2,445 USD |
| | Biên đóng góp (trước lương tài xế) | 65,2%; theo tuyến từ 50,4% đến 72,7% |
| | Dặm chạy vượt so với tuyến chuẩn | 2,95% |
| Nhiên liệu | MPG | 6,448 |
| | Gallon mua ÷ gallon tiêu thụ | 1,294 (từng xe: 1,20 đến 1,41) |
| Giao hàng | Đúng giờ (±120 phút) / không trễ | 44,6% / 33,3% |
| | Thời gian chờ trung bình | 91,5 phút mỗi lần lấy/giao; tổng 260.607 giờ |
| Tài sản | Dặm mỗi tháng-xe có chạy | 36.884 |
| | Mức sử dụng (chỉ để so sánh) | 83,0% |
| | Giờ dừng do bảo dưỡng | 72.231 giờ |
| An toàn | Sự cố / triệu dặm; tỷ lệ phòng tránh được | 1,39; 37,6% |

## 4. Đánh giá dữ liệu: phát hiện mới trong module này

| Phát hiện | Số liệu | Ý nghĩa |
|---|---|---|
| **28/120 xe không chạy chuyến nào trong 3 năm** | 13 xe `Inactive`, 15 xe `Maintenance`; 690 phiếu bảo dưỡng, **1,40 triệu USD (24% chi phí bảo dưỡng)**, 17.418 giờ dừng | Câu hỏi cho module `optimize`: có cần giữ các xe này không |
| Sản lượng gần như không đổi | Trung bình 2.361 chuyến/tháng (6 tháng đầu 2022) so với 2.391 (6 tháng cuối 2024), +1,3% | Toàn bộ chuyến trong 3 năm do 92 xe thực hiện (khoảng 2% chuyến không ghi mã xe). Nhu cầu cao điểm theo ngày cần được tính ở module `optimize` |
| Gallon mua nhiều hơn gallon tiêu thụ 29% | Đều ở mọi xe (1,20–1,41) | Chênh lệch có tính hệ thống, không tập trung ở vài xe. Có thể do cách sinh dữ liệu; chưa đủ căn cứ để kết luận gian lận thẻ nhiên liệu |
| Các phân khúc khách hàng gần như giống hệt nhau | Hợp đồng / chuyên tuyến / thuê lẻ: chi phí/dặm đều 0,84 USD, đúng giờ 44,2–44,9% | Ít khả năng có đòn bẩy theo loại khách hàng; khác biệt rõ hơn nằm ở cấp tuyến (biên 50,4–72,7%) |
| 93.269 USD nhiên liệu mua vào tháng 1/2025 | Không có chuyến nào trong tháng đó | Nằm ở dòng "Không gán được", tổng vẫn khớp |

## 5. Giới hạn, và điều không làm

| Hạng mục | Lý do |
|---|---|
| Lương tài xế, lợi nhuận ròng | Dữ liệu không có. **Biên đóng góp 65,2% vì thế cao hơn biên thực tế**; phải nói rõ khi trình bày |
| KPI chạy không tải, giá nhiên liệu theo địa điểm, theo `facility_id` | Không có tín hiệu (xem đánh giá module 1) |
| Mức sử dụng xe | Chỉ dùng để so sánh giữa các xe, vì có tháng vượt 100% |
| Lọc khoảng ngày không trọn tháng | Chi phí nhiên liệu và bảo dưỡng phân bổ theo tháng, nên lọc theo tháng hoặc năm cho kết quả chính xác nhất |

## 6. Chuyển sang module 3 `optimize`

1. **Quy mô đội xe:** giữ hay thanh lý 28 xe không chạy, so với sản lượng hiện tại (gần như không đổi) và nhu cầu cao điểm. Đưa lên dashboard như một đề xuất để người xem cân nhắc.
2. **Lợi nhuận tuyến:** biên từ 50,4% đến 72,7%; xếp hạng tuyến và tính mức giá cần điều chỉnh.
3. **Giao hàng:** mô hình dự báo trễ dùng `delivery_performance`.
4. **Nhiên liệu:** đòn bẩy còn lại là MPG theo xe và tài xế. Chênh lệch gallon mua/tiêu thụ chỉ trình bày như một chỉ số kiểm soát.

## 7. Tái lập

```powershell
python -m uv run logops build                       # tạo view + docs/03-kpi-definitions
python -m uv run logops kpi --by route --kpis all   # KPI theo tuyến
python -m uv run pytest tests/metrics               # 29 test của module này
```
