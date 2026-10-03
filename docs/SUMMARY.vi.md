# Tổng kết dự án: Logistics Ops Optimizer

> Bản tiếng Anh: [SUMMARY.md](SUMMARY.md) · Cập nhật cuối mỗi module · **Lần cập nhật cuối:**
> 03/10/2026, sau module 3 · **Nguyên tắc:** chỉ ghi điều đã kiểm chứng; chi tiết và bằng chứng nằm
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
| 3 | `optimize` | 4, 5 | ✅ 23 test | [03-optimize.vi.md](reviews/03-optimize.vi.md) |
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
| Kho dữ liệu kiểm tra được, dựng lại bằng một lệnh | `logops build` (khoảng 8 giây) |
| 69 quy tắc chất lượng dữ liệu, báo cáo EN/VI | `docs/02-data-quality-report` |
| 3 view nền + 21 KPI theo SCOR | `logops kpi --by …`, `docs/03-kpi-definitions` |
| Quy mô đội xe, lợi nhuận tuyến, khuyến nghị | `logops optimize --growth …`, `docs/05-evaluation` |
| Lỗ hổng dữ liệu → cải tiến quy trình | `docs/04-data-process-improvements` |
| Tài liệu phương pháp, ngưỡng, mô hình dữ liệu | `docs/00-analytical-approach`, `docs/02-*` |

## 6. Kết quả tối ưu (module 3)

**So với mục tiêu 1,04 triệu USD/năm:**

| Loại | Mỗi năm | % mục tiêu |
|---|---:|---:|
| **Tiết kiệm đo được**: thanh lý 28 xe không chạy (13 `Inactive`, 15 `Maintenance`) | 0,47 triệu USD | 45% |
| Cận trên: chuẩn hóa phụ phí nhiên liệu (0,96) + điều chỉnh cước tối đa 5% (1,50) + xem lại 12 xe ít dặm nhất (0,19) | 2,65 triệu USD | 255% |

- **Đội xe:** cần 80 xe khi sản lượng không đổi, 96 xe nếu tăng 20%; đang sở hữu 120 xe.
- **Tuyến:** 58 tuyến chia 4 nhóm. Không tuyến nào lỗ trên chi phí đo được; tuyến yếu nhất lỗ nếu chi
  phí tài xế vượt 0,857 USD/dặm. Phụ phí nhiên liệu cố định theo tuyến (0,15–0,34 USD/dặm), không theo
  giá nhiên liệu.
- **Dữ liệu:** 7,24 triệu USD/năm nhiên liệu mua chưa đối soát với tiêu thụ (chưa giải thích được,
  không phải thất thoát đã chứng minh). Telematics cho 92 xe: 25–65 nghìn USD/năm, hoàn vốn nếu ngăn
  được 0,2% chi phí nhiên liệu.
- **Đã kiểm tra và loại bỏ, kèm bằng chứng:** mô hình dự báo trễ (tiêu chí AUC rút lại), MPG theo tài
  xế/xe, chạy không tải, giá nhiên liệu theo địa điểm, lợi nhuận theo khách hàng, thay xe cũ. Chủ dự án
  bỏ thêm: điểm nghẽn, ghép hàng, tính phí chờ.

## 7. Quyết định của chủ dự án

- Tập trung vào **năng suất và chất lượng vận hành**; không xét tiêu chí tuân thủ nhân sự.
- Không làm những gì dữ liệu không có (ví dụ lương tài xế).
- Mỗi module bắt đầu bằng spec định nghĩa output, và kết thúc bằng một file đánh giá cùng việc cập
  nhật file này.
