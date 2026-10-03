# Đánh giá · Module 3: `analysis`

> CRISP-DM pha 2–3 (mô tả và chẩn đoán) · Bản tiếng Anh: [03-analysis.md](03-analysis.md) · Spec:
> [SPEC-analysis.vi.md](../../SPEC-analysis.vi.md) · Kết quả: [03-analysis-insights.vi.md](../03-analysis-insights.vi.md)
> · Tổng kết: [SUMMARY.vi.md](../SUMMARY.vi.md)
> **Trạng thái:** hoàn tất ngày 03/10/2026, chưa commit · **Nguyên tắc:** chỉ ghi điều đã kiểm chứng.

## 1. Bối cảnh

Module này **thay vị trí của `optimize`**: phần optimize đã làm được tạm dừng ở nhánh `feature/optimize`
và sẽ làm lại sau, dựa trên các phát hiện ở đây. Phạm vi được chốt cùng chủ dự án:
- Lợi nhuận phân tích **theo cách doanh nghiệp theo dõi** (kỳ, cầu lợi nhuận, đơn vị kinh tế, chiều kinh
  doanh), không theo thứ trong tuần hay mùa vụ.
- **Không dùng dữ liệu bên ngoài**, kể cả tọa độ.
- Điều gì không rõ ràng thì bỏ: giả thuyết chạy rỗng ↔ nhiên liệu đã bỏ; nhiên liệu chỉ thống kê.
- Tham khảo notebook [Route_optimization](https://www.kaggle.com/code/yogape/route-optimization) của
  tác giả bộ dữ liệu, giữ phần đúng và sửa phần sai.

## 2. Output so với spec

| Output | Đã giao | Bằng chứng |
|---|---|---|
| P1 lãi lỗ theo tháng/quý/năm, so kỳ trước, cùng kỳ, lũy kế | ✅ `profit.pnl` | Tổng khớp KPI đội xe ở cả 3 mức kỳ (test tích hợp) |
| P2 cầu lợi nhuận | ✅ `profit.bridge`, 6 thành phần | Các phần cộng lại đúng bằng tổng thay đổi (test) |
| P3 đơn vị kinh tế | ✅ trên dặm, chuyến, xe-tuần | — |
| P4 theo chiều kinh doanh + tập trung khách hàng | ✅ 8 chiều qua `kpi()`; HHI, top 10/20, Pareto | Tổng các nhóm khớp đội xe (test) |
| P5 biên so với giá nhiên liệu | ✅ theo tháng, kèm tương quan | — |
| F1 nhiên liệu tháng/quý/năm (chỉ thống kê) | ✅ | — |
| C1–C2 số xe mỗi ngày, kế hoạch theo mức đảm bảo | ✅ kèm bằng chứng không dự báo được thời điểm | p95 ≤ p99 ≤ cao nhất ≤ số xe đang chạy (test) |
| N1–N4 ma trận 3×3, cân bằng hàng đi/về, đổi điểm xuất phát, đối chiếu notebook | ✅ | Tổng lô đi = tổng lô đến (test); 58 tuyến |
| Bộ nhận xét | ✅ 12 quy tắc EN/VI, 12 ngưỡng có lý do và nguồn | Test: câu mẫu không có chữ số; ngưỡng đổi thì mức độ đổi |
| Lệnh, tài liệu | ✅ `logops insights`, `analysis_bundle()`, `docs/03-analysis-insights` tự sinh | Tài liệu ổn định qua các lần chạy (test) |

**Test:** 12 test mới (7 đơn vị, 5 tích hợp); tổng 93 test qua; `ruff` sạch. Build 16,3–17,6 giây (mục
tiêu < 30 giây).

## 3. Phát hiện chính

| Chủ đề | Phát hiện | Mức |
|---|---|---|
| **Lợi nhuận** | Biên tăng 62,7% → 67,2% (2022 → 2024). Doanh thu/dặm đứng yên (2,444 → 2,447 USD). Giá nhiên liệu giảm đóng góp **+4,12 trong +4,42 triệu USD (93%)** | cần hành động |
| | Biên hằng tháng đi ngược giá nhiên liệu (tương quan −0,92), vì phụ phí cố định | cần theo dõi |
| | Sản lượng không đổi (28.589 → 28.656 chuyến); các phân khúc có biên như nhau (65,5–65,8%) | thông tin |
| | Texas đóng góp nhiều nhất (23,33 triệu USD, 12%); biên theo bang 56,5–69,9% | thông tin |
| | Không có rủi ro tập trung khách hàng: khách lớn nhất 0,6%, HHI 50 | thông tin |
| **Nhiên liệu** | Năm nào gallon mua cũng nhiều hơn gallon tiêu thụ ghi nhận (1,28–1,30 lần), chưa đối soát | cần theo dõi |
| **Đội xe** | 95% số ngày cần ≤ 73 xe, 99% ≤ 75, ngày bận nhất 80; có 92 xe đang chạy, 120 xe sở hữu | cần theo dõi |
| | Không dự báo được ngày cao điểm (tương quan ngày-ngày 0,18; theo quý 0,04; trung bình năm 66,0–66,2) | thông tin |
| **Mạng lưới** | 33% số lô (28.178) kết thúc ở nơi không có hàng về; 16/20 thành phố lệch quá 20%; ổn định (0,997). Los Angeles và Indianapolis chỉ nhận hàng | cần hành động |
| | 95,4% số lần chuyển, xe bắt đầu chuyến mới ở thành phố khác; quãng di chuyển không được ghi | cần theo dõi |

## 4. Đối chiếu với notebook

| Notebook | Vấn đề | Đã sửa |
|---|---|---|
| Ma trận tuyến | Giá nhiên liệu cố định $3,80 (thực tế 3,899); doanh thu thiếu phụ phí; trung bình của tỷ lệ | Chi phí thật, tổng ÷ tổng |
| Hàng đi/về | Cộng chênh lệch của mọi thành phố luôn ra 0 → chi phí điều xe luôn $0 | Đo phần dư chiều đến theo từng thành phố |
| Mùa vụ | Đếm theo tháng nên tháng 31 ngày luôn "đỉnh" | Tính theo ngày: không có mùa vụ |
| Dặm rỗng | Giả định 15%, $0,85/dặm | Chỉ đếm tần suất; không tính dặm |
| Tập trung khách hàng | — | Giữ nguyên, thêm HHI |

## 5. Lưu ý khi trình bày

- **Biên năm ở đây (62,7% → 67,2%) khác con số 63,2% → 67,6% nêu trong trao đổi trước** vì báo cáo lãi
  lỗ ghi mọi chi phí theo ngày phát sinh, kể cả 1,40 triệu USD bảo dưỡng của 28 xe không chạy. Báo cáo
  lãi lỗ là con số đúng.
- Lợi nhuận là **đóng góp trước lương tài xế và chi phí chung**.
- Ngưỡng HHI lấy từ hướng dẫn sáp nhập của Hoa Kỳ, ở đây **áp dụng tương tự** cho danh mục khách hàng.

## 6. Đã bỏ (theo quyết định của chủ dự án)

Thứ trong tuần, mùa vụ, *operating ratio*, dặm chạy rỗng, tọa độ bổ sung, giả thuyết chạy rỗng ↔ nhiên
liệu, ước tính tiền tiết kiệm.

## 7. Chuyển sang module sau

- **Dashboard** đọc `analysis_bundle()`: nhận xét, lãi lỗ, cầu lợi nhuận, bang, ma trận tuyến, cân bằng
  mạng lưới, năng lực đội xe.
- **Optimize** (làm lại từ nhánh `feature/optimize`): mất cân bằng mạng lưới và việc xe đổi điểm xuất phát
  là đầu vào mới cho bài toán ghép hàng chiều về; ma trận tuyến là đầu vào cho điều chỉnh giá.

## 8. Tái lập

```powershell
python -m uv run logops build              # tạo docs/03-analysis-insights
python -m uv run logops insights --lang vi # in nhận xét
python -m uv run pytest tests/analysis     # 12 test của module này
```
