# Tổng kết dự án: Logistics Ops Optimizer

> Bản tiếng Anh: [SUMMARY.md](SUMMARY.md) · Cập nhật cuối mỗi module · **Lần cập nhật cuối:**
> 03/10/2026, sau module 2 · **Nguyên tắc:** chỉ ghi điều đã kiểm chứng; chi tiết và bằng chứng nằm
> trong từng file đánh giá ở `docs/reviews/`.

## 1. Dự án là gì

Biến dữ liệu vận hành đội xe thành **quyết định tiết kiệm chi phí có số tiền cụ thể**, trình bày
trên dashboard và báo cáo. Dự án dùng để trình bày với Giám đốc Logistics của Saigon Co.op trong buổi
phỏng vấn ngày **05/10/2026**, và làm theo khung CRISP-DM.

**Dữ liệu:** [Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database)
(Kaggle, dữ liệu tổng hợp). 14 bảng, 549.706 dòng, 01/2022–12/2024. 120 xe, 150 tài xế, 200 khách
hàng, 58 tuyến.

## 2. Tiến độ

| # | Module | Pha CRISP-DM | Trạng thái | Đánh giá |
|---|---|---|---|---|
| — | Hiểu nghiệp vụ | 1 | ✅ | `docs/01-business-understanding` |
| 1 | `data-platform` | 2, 3 | ✅ 47 test | [01-data-platform.vi.md](reviews/01-data-platform.vi.md) |
| 2 | `metrics` | 3 | ✅ 29 test | [02-metrics.vi.md](reviews/02-metrics.vi.md) |
| 3 | `optimize` | 4, 5 | ⏳ | |
| 4 | `insights` | 6 | ⏳ | |
| 5 | `dashboard` | 6 | ⏳ | |
| 6 | `reports` | 6 | ⏳ | |

## 3. Hiện trạng kinh doanh (số liệu nền đã kiểm chứng)

| Chỉ số | Giá trị |
|---|---|
| Doanh thu | 298,6 triệu USD |
| Chi phí đo được (nhiên liệu + bảo dưỡng + sự cố) | 104,0 triệu USD; **nhiên liệu chiếm 92%** |
| Chi phí / dặm · doanh thu / dặm | 0,851 USD · 2,445 USD |
| MPG đội xe | 6,45 |
| Giao trong khung ±2 giờ · không trễ | 44,6% · 33,3% |
| Thời gian chờ | 260.607 giờ; trung bình 91,5 phút mỗi lần lấy/giao |
| Đội xe | 92 xe chạy; **28 xe không chạy chuyến nào trong 3 năm**, tốn 1,40 triệu USD bảo dưỡng |
| **Mục tiêu tiết kiệm** | **≥ 3,1 triệu USD trong 3 năm** (3% chi phí đo được) |

## 4. Dữ liệu tin được đến đâu

- **Tin được:** quan hệ giữa các bảng, các khoản tiền, bảng tổng hợp tháng, không trùng lặp. Chỉ
  1,5% số dòng có lỗi mức error.
- **Không dùng được:** bang trên phiếu nhiên liệu và sự cố, `facility_id` trên sự kiện giao nhận,
  `idle_time_hours` (nhiễu ngẫu nhiên), giá nhiên liệu theo địa điểm (không có tín hiệu).
- **Không có trong dữ liệu:** lương tài xế, chi phí chung. Biên đóng góp 65,2% vì thế **cao hơn biên
  thực tế**.
- **`on_time_flag`** = lệch ≤ ±120 phút so với giờ hẹn, suy ra từ dữ liệu (khớp 100%). Không có nguồn
  bên ngoài cho con số 120, nên cửa sổ đúng giờ là một tham số.

## 5. Đã giao

| Sản phẩm | Lệnh / file |
|---|---|
| Kho dữ liệu kiểm tra được, dựng lại bằng một lệnh | `logops build` (khoảng 7 giây) |
| 69 quy tắc chất lượng dữ liệu, báo cáo EN/VI | `docs/02-data-quality-report` |
| 3 view nền + 21 KPI theo SCOR | `logops kpi --by …`, `docs/03-kpi-definitions` |
| Tài liệu phương pháp, ngưỡng, mô hình dữ liệu | `docs/00-analytical-approach`, `docs/02-*` |

## 6. Đòn bẩy cho module `optimize`

| Đòn bẩy | Có tín hiệu trong dữ liệu? |
|---|---|
| Quy mô đội xe (28 xe không chạy) | ✅ 1,40 triệu USD bảo dưỡng; sản lượng gần như không đổi (+1,3%) |
| Lợi nhuận tuyến | ✅ Biên từ 50,4% đến 72,7% giữa các tuyến |
| Giao hàng đúng giờ | ✅ 44,6%; sẽ kiểm tra bằng mô hình dự báo trễ |
| MPG theo xe/tài xế | Chưa kiểm tra |
| Chạy không tải; giá nhiên liệu theo địa điểm | ❌ Không có tín hiệu: không đưa ra số tiết kiệm |

## 7. Quyết định của chủ dự án

- Tập trung vào **năng suất và chất lượng vận hành**; không xét tiêu chí tuân thủ nhân sự.
- Không làm những gì dữ liệu không có (ví dụ lương tài xế).
- Mỗi module bắt đầu bằng spec định nghĩa output, và kết thúc bằng một file đánh giá cùng việc cập
  nhật file này.
