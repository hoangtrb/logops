# Spec: reports

> Module 6/6 · CRISP-DM pha 6 (Triển khai) · Bản tiếng Anh: [SPEC-reports.md](SPEC-reports.md) · Đầu
> vào: lớp phân tích (module 3), module optimize (module 5), biểu đồ và component của dashboard
> (module 4)

## Mục tiêu

Một cú bấm (dashboard) hoặc một lệnh (CLI) biến **loại báo cáo**, **khoảng thời gian** và **ngôn
ngữ** thành một file Giám đốc Logistics có thể lưu, in hoặc gửi email: **HTML tự chứa** (mở được khi
không có mạng, biểu đồ vẫn tương tác) hoặc **PDF**.

**Nguyên tắc**
- **Báo cáo không tính thêm gì mới.** Dùng chung các hàm phân tích và optimize với dashboard, dùng lại
  biểu đồ và component của dashboard, nên báo cáo luôn khớp với màn hình.
- Cùng chuẩn trình bày với dashboard: đơn vị trên mọi biểu đồ, có diễn giải, tên dễ hiểu, VI/EN.
- **Không thêm thư viện.** PDF dùng chế độ in headless của Microsoft Edge hoặc Google Chrome có sẵn
  trên Windows; nếu không có trình duyệt nào, người dùng nhận thông báo rõ ràng và HTML vẫn dùng được.

## Output

### Các loại báo cáo

| Loại | Nội dung |
|---|---|
| **Tổng quan điều hành** | 8 ô KPI, điểm chính theo mức độ, tiết kiệm so với mục tiêu và các khuyến nghị, biểu đồ biên và giá nhiên liệu |
| **Kết quả kinh doanh & tuyến** | Lãi lỗ theo quý (biểu đồ + bảng), cầu lợi nhuận, hiệu quả trên mỗi đơn vị, đánh giá tuyến (tuyến ưu tiên), kịch bản giá cước |
| **Chất lượng giao hàng** | Tỷ lệ đúng hẹn theo bốn chuẩn, phân bố độ lệch giờ giao, đúng hẹn theo độ dài chuyến, thời gian chờ, kiểm tra giao trễ |
| **Nhiên liệu** | Nhận xét nhiên liệu, mua vào so với tiêu thụ, tỷ lệ mua ÷ tiêu thụ, giá bình quân, chi phí nhiên liệu, lỗ hổng đối soát |
| **Đội xe** | Số xe hoạt động mỗi ngày, năng suất, quy mô đội xe theo kịch bản, lộ trình thanh lý, các xe chưa từng chạy |

Bỏ loại "An toàn & tài xế" trong kế hoạch cũ: tiêu chí tài xế và tuân thủ nằm ngoài phạm vi (quyết
định của chủ dự án).

### Giao diện

- `logops report --type executive --from 2022-01-01 --to 2024-12-31 --lang vi --format html|pdf`
  → file trong `reports/output/` (đã git-ignore).
- Thanh bên dashboard: **Xuất báo cáo** (loại, định dạng) → nút tải về. Dùng khoảng thời gian và
  ngôn ngữ đang chọn.
- `reports.build_html(type, start, end, lang)` → chuỗi HTML; `reports.to_pdf(html)` → bytes PDF.

### Bố cục

Băng bìa (tên báo cáo, khoảng thời gian, ngày tạo), rồi các phần theo kiểu thẻ của dashboard; biểu
đồ nhúng bằng Plotly (thư viện nhúng một lần để mở offline); bảng ngắt dòng; ngắt trang giữa các phần
trong PDF.

## Không làm

| Không làm | Lý do |
|---|---|
| Nhận xét do Claude viết | Bộ nhận xét theo quy tắc đã đủ; không tốn phí API |
| Báo cáo định kỳ hoặc gửi email tự động | Không có tác vụ định kỳ (quyết định của dự án) |
| Báo cáo An toàn & tài xế | Ngoài phạm vi (chỉ năng suất và chất lượng) |

## Tiêu chí thành công

1. Mọi loại báo cáo tạo được ở hai ngôn ngữ cho cả giai đoạn và cho một năm; có test.
2. Một con số trong báo cáo bằng đúng con số đó trên dashboard (test trên báo cáo tổng quan).
3. HTML mở được khi không có mạng; PDF mở được và mỗi phần có ít nhất một trang.
4. Không có trình duyệt → thông báo rõ ràng, không lỗi; `ruff` sạch; test pass.

## Kế hoạch

| Bước | Nội dung |
|---|---|
| 1 | `reports/build.py`: lấy dữ liệu dùng chung, các phần theo loại, khuôn HTML |
| 2 | `reports/pdf.py`: in headless bằng Edge/Chrome |
| 3 | Lệnh CLI `logops report`, nút xuất báo cáo trên dashboard |
| 4 | Test, ảnh chụp từng báo cáo, đánh giá `docs/reviews/06-reports`, SUMMARY, nhật ký |

## Điều chỉnh 04/10/2026 (chủ dự án quyết định): một báo cáo gồm mọi trang

Thay cho năm loại báo cáo ở trên và đề xuất v2.

| Hạng mục | Quyết định |
|---|---|
| Nội dung | Một báo cáo gồm **toàn bộ các trang dashboard** (tổng quan, kết quả kinh doanh, khách hàng & thị trường, tuyến, giao hàng, đội xe, nhiên liệu, khuyến nghị tối ưu, dữ liệu & KPI) |
| Bố cục | Đầu trang: "Báo cáo quản lý vận tải", ngày xuất, khoảng thời gian. Bên dưới mỗi trang là một tab như dashboard nhiều trang; tab Tổng quan mở đầu tiên với doanh thu, chi phí vận hành, lợi nhuận đóng góp, biên, chi phí mỗi dặm và các KPI vận hành |
| Nguồn | Chính các trang vẽ báo cáo: lệnh `st.*` của trang được chuyển sang bộ dựng HTML (`reports/static.py`) qua `dashboard/output.py`, riêng cho từng luồng, nên số liệu, diễn giải và bảng là của dashboard; mỗi trang ở góc nhìn mặc định (ghi bằng nhãn "Kỳ xem: …") |
| HTML | Tự chứa, responsive (thanh tab cuộn ngang, lưới xếp dọc trên điện thoại; bảng dài cuộn trong thẻ) |
| PDF | Mỗi trang dashboard bắt đầu một tờ A4 mới; chân trang có tên báo cáo, ngày xuất và "Trang x / y" (CSS page margin boxes); bảng dài in 40 dòng đầu kèm ghi chú xem bản HTML; bỏ bản đồ Mỹ (đường viền cần tải từ internet) |
| Dashboard | Thanh bên "Xuất báo cáo": định dạng, nút Tạo, dòng trạng thái kèm %, nút Tải về đổ dần màu xanh lá khi đang tạo và xanh đầy khi xong; báo cáo tạo trên luồng riêng |
| CLI | `logops report --from --to --lang --format html\|pdf` |

### Điều chỉnh 04/10/2026 (tối)

- Bỏ mọi icon (menu dashboard, tab báo cáo, dòng trạng thái); tab trang của báo cáo chia hai hàng
  (5 + 4), không thanh cuộn; tab điểm chính không thanh cuộn.
- Đề tài và nguồn dữ liệu (đề tài, bài toán, bộ dữ liệu, doanh nghiệp, đường dẫn Kaggle) ở trang
  Tổng quan và bìa báo cáo. Dữ liệu không nêu tên công ty (dữ liệu mô phỏng) nên không tự đặt tên.
- PDF: bố cục in riêng trong cùng file (bìa có mục lục; mục đánh số, mỗi mục sang tờ mới; hình và
  bảng đánh số, không khung thẻ; bảng in đủ, bảng từ 8 cột in trang ngang ngay tại chỗ; đầu trang
  ghi khoảng thời gian; chân trang có tên, ngày xuất, trang x / y). Giữ công cụ in Edge/Chrome
  headless (Chromium, cũng là lõi của Playwright và Puppeteer); đã cân nhắc WeasyPrint nhưng cần
  cài GTK trên Windows và không chạy được script biểu đồ (phải thêm thư viện xuất ảnh).
- Kiểu chữ PDF (chủ dự án, 04/10/2026): Times New Roman, chữ đen, thân bài 11 pt, tiêu đề xanh
  đậm, lề 20 mm; điểm chính và KPI dạng văn bản và bảng, không khung.
- Phần đầu PDF (chủ dự án, 04/10/2026): ảnh bìa, mục lục, danh mục hình và bảng có số trang, tóm
  tắt điều hành; điểm chính có mức độ tô màu, gạch đầu dòng và dòng đề xuất nổi bật.
