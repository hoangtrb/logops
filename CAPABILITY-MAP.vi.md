# Bản đồ năng lực: Logistics Ops Optimizer

> Bản tiếng Anh: [CAPABILITY-MAP.md](CAPABILITY-MAP.md)

**Mục tiêu:** Dự án portfolio để trình bày với Giám đốc Logistics (Saigon Co.op) trong buổi
phỏng vấn xin việc. Dự án biến dữ liệu thô của đội xe thành các quyết định tiết kiệm chi phí,
được trình bày qua dashboard và các báo cáo xuất được chỉ với một cú nhấp.

**Góc nhìn người xem:** Giám đốc logistics của một chuỗi phân phối bán lẻ quan tâm đến **chi
phí phục vụ, giao hàng đúng giờ, nhiên liệu và hiệu suất sử dụng đội xe**. Mọi module phải trả
lời được câu hỏi *"tôi nên làm gì, và tiết kiệm được bao nhiêu?"*, không chỉ *"đã xảy ra
chuyện gì?"*

**Nguồn dữ liệu:** [Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database)
(Kaggle), không đưa lên git.

## Các module

| Mã module | Trách nhiệm | Phụ thuộc |
|---|---|---|
| `data-platform` | CSV → Parquet đã kiểm tra → kho dữ liệu DuckDB; báo cáo chất lượng dữ liệu | — |
| `metrics` | Lớp KPI (SQL view): chi phí/dặm, % đúng giờ, thời gian chờ tại kho, MPG, thời gian nổ máy chờ, hiệu suất sử dụng, chi phí bảo dưỡng và an toàn | data-platform |
| `optimize` | Các bộ máy khuyến nghị cho 4 lĩnh vực trọng tâm bên dưới, mỗi khuyến nghị kèm số tiền tiết kiệm ước tính | metrics |
| `insights` | Claude API: viết phần nhận định về KPI và điểm bất thường cho từng báo cáo; đặt câu hỏi bằng ngôn ngữ tự nhiên → SQL | metrics, optimize |
| `dashboard` | Streamlit + Plotly: mỗi lĩnh vực trọng tâm một trang, kèm nút xuất báo cáo | metrics, optimize, insights |
| `reports` | Người dùng chọn **loại báo cáo** và khoảng thời gian → ra file PDF hoặc HTML trong một bước (dòng lệnh hoặc nút trên dashboard) | metrics, optimize, insights |

Thứ tự xây dựng: `data-platform` → `metrics` → `optimize` → `insights` → `dashboard` ∥ `reports`

## Các lĩnh vực trọng tâm (`optimize`), xếp theo mức ưu tiên của Giám đốc

1. **Chi phí phục vụ & lợi nhuận theo tuyến.** Chi phí/dặm chia thành nhiên liệu, bảo dưỡng,
   tài xế và quãng chạy rỗng, theo tuyến và theo khách hàng. Đánh dấu các tuyến lỗ và ước tính
   mức giá cần điều chỉnh cho từng tuyến.
2. **Giao hàng đúng giờ & thời gian chờ tại kho.** % đúng giờ, số giờ chờ theo kho/tuyến/khung
   giờ. Mô hình ML dự đoán rủi ro trễ, kèm giải thích các yếu tố chính gây trễ.
3. **Hiệu quả nhiên liệu.** Xe và tài xế có MPG hoặc thời gian nổ máy chờ bất thường, chênh lệch
   giá nhiên liệu theo địa điểm. Ước tính số tiền tiết kiệm ($) nếu các trường hợp bất thường đạt
   mức trung vị của đội xe.
4. **Hiệu suất sử dụng đội xe & bảo dưỡng.** Xe ít được dùng (xác định quy mô đội xe hợp lý: thực
   sự cần bao nhiêu xe), xe có chi phí cao hoặc nằm chờ sửa nhiều, và cảnh báo xe đến lúc cần
   bảo dưỡng hoặc thay thế.

*Mở rộng (nếu còn thời gian):* demo phân công xe/tài xế cho lô hàng bằng quy hoạch tuyến tính
(OR-Tools).

## Các loại báo cáo (`reports`)

Tổng quan cho lãnh đạo · Chi phí & Tuyến · Hiệu suất giao hàng · Nhiên liệu · Đội xe & Bảo dưỡng · An toàn & Tài xế
Mỗi báo cáo: lọc theo khoảng thời gian, gồm KPI + biểu đồ + khuyến nghị + nhận định do Claude viết → PDF hoặc HTML.

## Khung CRISP-DM

Dự án được trình bày như một vòng CRISP-DM đầy đủ. Mỗi giai đoạn có một sản phẩm cụ thể để
trình bày:

| Giai đoạn CRISP-DM | Sản phẩm | Module |
|---|---|---|
| 1. Hiểu bài toán kinh doanh | `docs/01-business-understanding.vi.md`: vấn đề của Giám đốc → KPI → tiêu chí thành công (số tiền tiết kiệm mục tiêu) | — (tài liệu) |
| 2. Hiểu dữ liệu | Hồ sơ dữ liệu + báo cáo chất lượng dữ liệu (giá trị thiếu, dữ liệu không nhất quán như "New York, AZ", khóa ngoại không khớp) | `data-platform` |
| 3. Chuẩn bị dữ liệu | Parquet đã làm sạch + lược đồ hình sao DuckDB + các view KPI | `data-platform`, `metrics` |
| 4. Mô hình hóa | Các bộ máy khuyến nghị dùng tối ưu hóa / ML | `optimize` |
| 5. Đánh giá | Chỉ số mô hình (ví dụ AUC của mô hình dự đoán trễ) + đối chiếu số tiền tiết kiệm với tiêu chí kinh doanh ở giai đoạn 1 | `optimize`, `docs/05-evaluation.md` |
| 6. Triển khai | Dashboard + báo cáo PDF/HTML một cú nhấp + nhận định do Claude viết | `insights`, `dashboard`, `reports` |

## Các quyết định

- Giữ nguyên dữ liệu gốc (dữ liệu Mỹ: dặm, USD), không quy đổi sang km/VND. Cách trình bày:
  phương pháp áp dụng được cho bất kỳ mạng lưới phân phối nào.
- Công nghệ: Python 3.11+, `uv`, DuckDB + Parquet + Polars, Streamlit + Plotly, pytest, git.
  Không dùng Spark; với khoảng 55 MB dữ liệu thì Spark chỉ thêm phức tạp mà không có lợi ích.
- Không có tác vụ chạy theo lịch. Báo cáo được tạo khi người dùng yêu cầu.
- LLM: Claude API. Trao đổi lại với chủ dự án nếu chi phí trở thành vấn đề. Lưu đệm phần nhận
  định để chạy lại báo cáo không phải gọi API lần nữa.
- Định dạng báo cáo: PDF + HTML.
- Mọi tài liệu đều có hai file riêng: tiếng Anh (`name.md`) và tiếng Việt (`name.vi.md`).
