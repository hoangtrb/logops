# Tổng kết dự án: Logistics Ops Optimizer

> Bản tiếng Anh: [SUMMARY.md](SUMMARY.md) · Cập nhật cuối mỗi module · **Lần cập nhật cuối:**
> 03/10/2026, sau module 4 `dashboard` · **Nguyên tắc:** chỉ ghi điều đã kiểm chứng; chi tiết và bằng chứng nằm
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
| 3 | `analysis` | 2, 3 | ✅ 12 test | [03-analysis.vi.md](reviews/03-analysis.vi.md) |
| 4 | `dashboard` | 6 | ✅ 26 test | [04-dashboard.vi.md](reviews/04-dashboard.vi.md) |
| 5 | `optimize` | 4, 5 | ⏸️ Tạm dừng ở nhánh `feature/optimize`, làm lại sau phân tích | |
| 6 | `reports` | 6 | ⏳ | |

## 3. Hiện trạng kinh doanh (số liệu nền đã kiểm chứng)

| Chỉ số | Giá trị |
|---|---|
| Doanh thu | 298,6 triệu USD |
| Chi phí đo được (nhiên liệu + bảo dưỡng + sự cố) | 104,0 triệu USD; **nhiên liệu chiếm 92%** |
| Chi phí / dặm · doanh thu / dặm | 0,851 USD · 2,445 USD |
| MPG đội xe | 6,45 |
| Giao hàng đúng hẹn (OTD, trong ±2 giờ so với giờ hẹn) · không trễ · đúng ngày hẹn | 44,6% · 33,3% · 91,2% |
| Hiệu suất sử dụng đội xe (số xe có chuyến bình quân mỗi ngày ÷ số xe sở hữu) | 55,1% (66 trên 120) |
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
| Phân tích lợi nhuận, nhiên liệu, đội xe, mạng lưới + nhận xét theo quy tắc | `logops insights`, `docs/03-analysis-insights` |
| Dashboard 8 trang, nút chuyển VI/EN, responsive (27 biểu đồ, nhận xét cạnh từng biểu đồ) | `logops dashboard` → http://localhost:8501 |
| Tài liệu phương pháp, ngưỡng, mô hình dữ liệu | `docs/00-analytical-approach`, `docs/02-*` |

## 6. Phát hiện chính (module 3 `analysis`)

| Chủ đề | Phát hiện |
|---|---|
| **Lợi nhuận** | Biên tăng 62,7% → 67,2% (2022 → 2024) nhưng doanh thu/dặm đứng yên. **93% mức tăng đóng góp (+4,12 trong +4,42 triệu USD) đến từ giá nhiên liệu giảm**; biên đi ngược giá nhiên liệu (tương quan −0,92) vì phụ phí cố định |
| | Sản lượng không đổi; các phân khúc khách hàng có biên như nhau; không có rủi ro tập trung khách hàng (HHI 50) |
| **Mạng lưới** | **33% số lô kết thúc ở nơi không có hàng về**; 16/20 thành phố lệch quá 20%; ổn định qua các năm (0,997). Los Angeles và Indianapolis chỉ nhận hàng. 95,4% số lần xe bắt đầu chuyến mới ở thành phố khác |
| **Đội xe** | 95% số ngày cần ≤ 73 xe, ngày bận nhất 80; 92 xe đang chạy, 120 xe sở hữu. Không dự báo được thời điểm cao điểm, nên lập kế hoạch theo mức đảm bảo |
| **Nhiên liệu** | Gallon mua nhiều hơn gallon tiêu thụ ghi nhận 1,28–1,30 lần mỗi năm; chưa đối soát |

Các con số trên do bộ quy tắc tự sinh từ dữ liệu, xem [03-analysis-insights.vi.md](03-analysis-insights.vi.md).

## 7. Quyết định của chủ dự án

- Tập trung vào **năng suất và chất lượng vận hành**; không xét tiêu chí tuân thủ nhân sự.
- Không làm những gì dữ liệu không có (ví dụ lương tài xế).
- Mỗi module bắt đầu bằng spec định nghĩa output, và kết thúc bằng một file đánh giá cùng việc cập
  nhật file này.
