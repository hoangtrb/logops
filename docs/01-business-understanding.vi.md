# 01 · Hiểu bài toán kinh doanh (Business Understanding)

> CRISP-DM Giai đoạn 1 · Dự án: Logistics Ops Optimizer · Bản tiếng Anh: [01-business-understanding.md](01-business-understanding.md)

## 1. Bối cảnh

Một đơn vị vận tải vận hành khoảng 120 xe tải, 180 rơ-moóc và 150 tài xế. Từ năm 2022 đến nay, đơn vị đã vận chuyển khoảng 85.000 lô hàng cho khoảng 200 khách hàng, trên 58 tuyến và 50 kho bãi. Mỗi chuyến xe đều để lại dữ liệu: mua nhiên liệu, sự kiện giao nhận, bảo dưỡng, sự cố an toàn. Hiện tại dữ liệu này chỉ dùng để báo cáo *điều đã xảy ra*, chưa được dùng để quyết định *cần thay đổi điều gì*.

Bài toán tương tự cũng áp dụng cho mạng lưới phân phối bán lẻ, chẳng hạn đội xe giao hàng từ trung tâm phân phối (DC) đến cửa hàng của một chuỗi bán lẻ. Vận tải là một trong những khoản chi phí lớn nhất có thể kiểm soát được, và mức độ phục vụ (hàng có đến đúng giờ không) quyết định trực tiếp việc cửa hàng có đủ hàng hay không.

## 2. Mục tiêu kinh doanh

Các câu hỏi của Giám đốc Logistics, theo thứ tự ưu tiên:

| # | Câu hỏi của Giám đốc | Mục tiêu kinh doanh |
|---|---|---|
| 1 | *"Tuyến nào, khách hàng nào đang làm mình lỗ?"* | Giảm **chi phí phục vụ (cost-to-serve)**; điều chỉnh hoặc định giá lại các tuyến không có lãi |
| 2 | *"Giao hàng trễ ở đâu và vì sao?"* | Tăng **tỷ lệ giao đúng giờ**; giảm thời gian chờ tại kho (detention) |
| 3 | *"Mình có đang lãng phí nhiên liệu không?"* | Giảm **chi phí nhiên liệu trên mỗi dặm** (MPG, thời gian nổ máy chờ, giá mua) |
| 4 | *"Số xe hiện tại có phù hợp không, xe nào quá tốn kém để giữ lại?"* | Tăng **hiệu suất sử dụng đội xe**; giảm chi phí bảo dưỡng và thời gian xe nằm chờ sửa |
| 5 | *"Tôi có thể tự lấy báo cáo mà không cần nhờ chuyên viên phân tích không?"* | **Báo cáo tự phục vụ** chỉ trong một bước |

## 3. Đánh giá hiện trạng

**Nguồn lực:** 14 bảng dữ liệu có quan hệ với nhau, lấy từ
[Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database)
trên Kaggle (CSV, khoảng 55 MB, khoảng 600 nghìn
dòng); bộ công cụ dữ liệu Python; Claude API để viết nhận định.

**Ràng buộc**
- Chỉ có dữ liệu lịch sử, không có dữ liệu GPS hay telematics theo thời gian thực. Vì vậy các
  khuyến nghị mang tính chiến lược và chiến thuật, không phải điều phối xe theo thời gian thực.
- Dữ liệu không có lương tài xế và chi phí quản lý chung. Chi phí phục vụ gồm nhiên liệu,
  bảo dưỡng và chi phí an toàn; chi phí tài xế được ước tính theo thời gian chạy chuyến.
- Dữ liệu của Mỹ (đơn vị dặm, USD). Phương pháp áp dụng được cho mọi mạng lưới mà không cần
  thay đổi.

**Giả định**
- `revenue` trong bảng loads là giá tính cho khách hàng (hoặc giá chuyển nội bộ, nếu là đội
  xe nội bộ).
- `on_time_flag` trong bảng delivery events là thước đo chính thức của mức độ phục vụ. *Đã xác
  nhận ở Giai đoạn 2:* cờ này nghĩa là đến trong khung **±2 giờ** so với lịch hẹn (khớp 100% sự
  kiện), nên đến sớm hơn 2 giờ cũng bị tính là không đạt.

**Rủi ro & cách giảm thiểu**

| Rủi ro | Cách giảm thiểu |
|---|---|
| Dữ liệu giả lập hoặc bị lỗi (ví dụ: thành phố không khớp với bang, thiếu mã tài xế) | Báo cáo chất lượng dữ liệu ở Giai đoạn 2; ghi lại mọi quy tắc làm sạch |
| Ước tính tiết kiệm quá lạc quan | Dùng mốc so sánh thận trọng (đưa các trường hợp bất thường về mức *trung vị* của đội xe, không phải mức tốt nhất) |
| LLM đưa ra số liệu sai ("ảo giác") | Claude chỉ diễn giải các con số đã được code tính sẵn, không tự tính toán |
| Chi phí gọi API LLM | Lưu đệm (cache) phần nhận định; theo dõi số token mỗi báo cáo; trao đổi với chủ dự án nếu chi phí cao |

## 4. Mục tiêu khai phá dữ liệu

| Mục tiêu kinh doanh | Mục tiêu phân tích | Kỹ thuật |
|---|---|---|
| Chi phí phục vụ | Chi phí/dặm theo tuyến và khách hàng, chia thành nhiên liệu, bảo dưỡng, tài xế và an toàn; biên lợi nhuận theo tuyến | Tổng hợp bằng SQL, xếp hạng lợi nhuận |
| Giao hàng đúng giờ | Tìm các yếu tố gây giao trễ và chờ tại kho; dự đoán rủi ro trễ cho từng lô hàng | Mô hình phân loại (gradient boosting) + mức độ quan trọng của từng yếu tố |
| Nhiên liệu | Phát hiện xe/tài xế có MPG hoặc thời gian nổ máy chờ bất thường; chênh lệch giá nhiên liệu theo địa điểm | Phát hiện bất thường bằng thống kê, so sánh với mốc chuẩn |
| Đội xe & bảo dưỡng | Hiệu suất sử dụng từng xe; xác định quy mô đội xe hợp lý; cảnh báo xe có chi phí/dặm cao | Phân tích hiệu suất sử dụng, chấm điểm xu hướng chi phí |
| Báo cáo tự phục vụ | Xuất báo cáo theo loại và khoảng thời gian | Mẫu PDF/HTML kèm phần nhận định do LLM viết |

## 5. Tiêu chí thành công

*Số liệu hiện trạng đã được đo ở Giai đoạn 2 ([02-data-quality-report.vi.md](02-data-quality-report.vi.md))
và các mục tiêu dưới đây đã được xác nhận theo đó ([02-data-understanding.vi.md](02-data-understanding.vi.md) §6).*

**Kinh doanh**
- Tìm ra các cơ hội tiết kiệm có giá trị **≥ 3% tổng chi phí vận hành**. Mỗi cơ hội có hành
  động cụ thể, người phụ trách và số tiền ước tính ($). Chi phí vận hành đo được giai đoạn
  2022–2024 là **104,0 triệu USD** (nhiên liệu, bảo dưỡng, bồi thường sự cố), nên mục tiêu là
  **≥ 3,1 triệu USD trong ba năm (khoảng 1,04 triệu USD mỗi năm)**. Dữ liệu không có lương tài xế,
  nên chi phí thật lớn hơn và mục tiêu này là thận trọng.
- Mọi khuyến nghị đều truy ngược được về dữ liệu gốc.

**Phân tích**
- ~~Mô hình dự đoán rủi ro trễ: ROC-AUC ≥ 0,70 trên tập kiểm tra chia theo thời gian.~~ **Rút lại sau module 3:** không có tác động nào của tài xế, tuyến, khách hàng hay xe lên việc trễ lặp lại qua các năm, nên mô hình không thể hơn mốc so sánh. Thay bằng: *mọi khoản tiết kiệm đều dựa trên tín hiệu lặp lại qua các năm* (`docs/05-evaluation` §4).
- Báo cáo chất lượng dữ liệu bao phủ 100% các bảng và ghi lại đầy đủ mọi quy tắc làm sạch.

**Triển khai**
- Xuất bất kỳ loại báo cáo nào ra PDF hoặc HTML trong **≤ 2 cú nhấp chuột hoặc 1 lệnh**,
  mất dưới 60 giây.
- Mỗi trang dashboard tải dưới 3 giây trên laptop.

## 6. Kế hoạch dự án (CRISP-DM)

| Giai đoạn | Sản phẩm |
|---|---|
| 1. Hiểu bài toán kinh doanh | Tài liệu này |
| 2. Hiểu dữ liệu | Hồ sơ dữ liệu + báo cáo chất lượng dữ liệu |
| 3. Chuẩn bị dữ liệu | Dữ liệu Parquet đã làm sạch + kho dữ liệu DuckDB + các view KPI |
| 4. Mô hình hóa | Bốn bộ máy khuyến nghị (chi phí, giao hàng, nhiên liệu, đội xe) |
| 5. Đánh giá | Chỉ số đánh giá mô hình + đối chiếu số tiền tiết kiệm với mục 5 |
| 6. Triển khai | Dashboard Streamlit + báo cáo một cú nhấp + nhận định do Claude viết |
