# Spec: analysis

> Module 3/6 (đổi thứ tự ngày 03/10/2026: phân tích đi trước, `optimize` làm sau, đang ở nhánh
> `feature/optimize`) · CRISP-DM pha 2–3: **mô tả và chẩn đoán** · Bản tiếng Anh:
> [SPEC-analysis.md](SPEC-analysis.md) · Đầu vào: lớp KPI của module 2 · Tham khảo: notebook
> [Route_optimization](https://www.kaggle.com/code/yogape/route-optimization) của tác giả bộ dữ liệu

## Mục tiêu

Trả lời câu hỏi **"chuyện gì đang xảy ra và vì sao"** theo cách doanh nghiệp theo dõi kết quả kinh doanh,
rồi **tự sinh nhận xét bằng lời theo quy tắc**. Dashboard (module 4) hiển thị số liệu và nhận xét. Module
`optimize` (module 5) dùng các phát hiện ở đây làm đầu vào.

**Nguyên tắc** (đã chốt với chủ dự án)
- Chỉ dùng số liệu có trong dữ liệu. **Không bổ sung dữ liệu từ bên ngoài**, kể cả tọa độ, vì số không
  chính xác là sai lệch.
- Điều gì không rõ ràng thì **để ngỏ hoặc bỏ**, không đưa giả thuyết vào kết quả.
- Mỗi câu nhận xét sinh từ con số đã tính, theo quy tắc có ngưỡng ghi rõ lý do. Không viết tay, không
  dùng LLM.

## Output

### Nhóm 1: Lợi nhuận (theo cách doanh nghiệp theo dõi)

| # | Phân tích | Nội dung |
|---|---|---|
| P1 | **Lãi lỗ theo kỳ** | Tháng / quý / năm. Doanh thu (cước, phụ phí nhiên liệu, phụ phí khác) → chi phí (nhiên liệu, bảo dưỡng, bồi thường) → đóng góp → biên. So với kỳ trước, cùng kỳ năm trước, và **lũy kế từ đầu năm** so với cùng kỳ. Chi phí ghi theo ngày phát sinh, nên tổng khớp với báo cáo |
| P2 | **Cầu lợi nhuận** | Giữa hai kỳ bất kỳ: tách mức thay đổi đóng góp thành sản lượng, giá cước, giá nhiên liệu, lượng nhiên liệu tiêu hao, bảo dưỡng, bồi thường. Các phần cộng lại đúng bằng tổng thay đổi |
| P3 | **Đơn vị kinh tế** | Doanh thu, chi phí, đóng góp trên dặm, trên chuyến, trên xe mỗi tuần |
| P4 | **Theo chiều kinh doanh** | Phân khúc khách hàng (hợp đồng / chuyên tuyến / thuê lẻ), từng khách hàng (top N + mức tập trung: thị phần top 10/20, khách lớn nhất, số khách chiếm 80%, HHI), loại hàng, bang đi, bang đến, tuyến, xe, tài xế |
| P5 | **Biên so với giá nhiên liệu** | Biên và giá nhiên liệu theo tháng, kèm tương quan |

### Nhóm 2: Nhiên liệu (chỉ thống kê)

| # | Phân tích | Nội dung |
|---|---|---|
| F1 | **Nhiên liệu theo tháng / quý / năm** | Gallon mua, chi tiêu, giá trung bình, gallon tiêu thụ theo chuyến, tỷ lệ mua ÷ tiêu thụ. Không diễn giải nguyên nhân chênh lệch |

### Nhóm 3: Đội xe

| # | Phân tích | Nội dung |
|---|---|---|
| C1 | **Số xe bận mỗi ngày** | Theo ngày, theo năm; so với số xe đang chạy và số xe sở hữu |
| C2 | **Kế hoạch năng lực theo mức đảm bảo** | Số xe đủ cho 95% / 99% số ngày và ngày cao nhất. Kèm bằng chứng vì sao *không* dự báo được thời điểm cao điểm (không có xu hướng, không có quý hay tháng nào lặp lại, ngày trước không báo trước ngày sau) |

### Nhóm 4: Mạng lưới (từ notebook, đã sửa)

| # | Phân tích | Nội dung |
|---|---|---|
| N1 | **Ma trận tuyến 3×3** | 3 mức sản lượng × 3 mức biên (chia ba theo thứ hạng), mỗi ô một hướng xử lý: bảo vệ, mở rộng, điều chỉnh giá, cân nhắc rút lui… Dữ liệu cho biểu đồ bong bóng. Chi phí thật từ lớp KPI |
| N2 | **Mất cân bằng hàng đi / hàng về** | Theo thành phố: lô đi, lô đến, chênh lệch, % lệch, mức ổn định qua các năm. Tổng phần dư chiều đến |
| N3 | **Tần suất xe đổi điểm xuất phát** | Theo chuỗi chuyến của từng xe: % số lần chuyến sau xuất phát ở thành phố khác nơi chuyến trước kết thúc, theo năm và theo thành phố. **Chỉ đếm, không tính dặm** |
| N4 | **Đối chiếu với notebook** | Notebook làm gì, sai ở đâu, sửa thế nào, kết quả khác ra sao |

### Nhóm 5: Nhận xét theo quy tắc, và đầu ra

- **Bộ quy tắc** (`insights.py`): mỗi quy tắc đọc số liệu và sinh câu nhận xét EN/VI, mức *thông tin*,
  *cần theo dõi* hoặc *cần hành động*. Câu mẫu không chứa chữ số nào: mọi con số được điền từ số liệu (có
  test). Mỗi ngưỡng có lý do và nguồn.
- **`analysis_bundle(con, start, end)`**: trả mọi bảng và nhận xét; dashboard chỉ đọc từ đây.
- Bổ sung lớp KPI: bang đi/đến trong `trip_economics`; `kpi(by=…)` thêm `origin_state`,
  `destination_state`, `load_type`.
- Lệnh **`logops insights`**; tài liệu tự sinh **`docs/03-analysis-insights`** EN/VI; file đánh giá
  module; cập nhật `SUMMARY` và nhật ký.

## Đã bỏ (quyết định ngày 03/10/2026)

| Bỏ | Lý do |
|---|---|
| Thứ trong tuần, mùa vụ | Không phù hợp cách doanh nghiệp theo dõi; dữ liệu cũng không có mẫu hình |
| *Operating ratio* | Thiếu lương và chi phí chung nên ra khoảng 35%, gây hiểu lầm so với chuẩn ngành |
| Dặm chạy rỗng, tọa độ bổ sung | 4 thành phố trên tuyến không có tọa độ; dùng tọa độ ngoài là sai lệch |
| Giả thuyết chạy rỗng ↔ nhiên liệu mua dư | Không rõ ràng; nhiên liệu chỉ thống kê |
| Tính tiền tiết kiệm | Thuộc `optimize` |

## Tiêu chí thành công

1. **Khớp tổng:** lãi lỗ theo kỳ cộng lại bằng tổng đội xe của lớp KPI; các phần của cầu lợi nhuận cộng
   lại bằng tổng thay đổi; tổng theo chiều kinh doanh + "Không gán được" bằng tổng đội xe.
2. **Không có chữ số trong câu mẫu nhận xét** (có test).
3. Mỗi ngưỡng có lý do và nguồn.
4. Test trên dữ liệu mẫu cho các phép tính chính + test tích hợp trên dữ liệu thật; `ruff` sạch.

## Kế hoạch

| Việc | Nội dung |
|---|---|
| A1 | Bổ sung lớp KPI (bang, loại hàng) |
| A2 | Lợi nhuận P1–P5 |
| A3 | Nhiên liệu F1, đội xe C1–C2 |
| A4 | Mạng lưới N1–N4 |
| A5 | Bộ nhận xét + `analysis_bundle` + `docs/03-analysis-insights` + lệnh `logops insights` |
| A6 | Đánh giá module, `SUMMARY`, nhật ký, `CAPABILITY-MAP`, roadmap |
