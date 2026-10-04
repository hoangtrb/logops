# Spec: dashboard

> Module 4/6 · CRISP-DM pha 6 (Triển khai) · Bản tiếng Anh: [SPEC-dashboard.md](SPEC-dashboard.md) ·
> Đầu vào: `analysis_bundle()` (module 3) và `kpi()` (module 2)

## Mục tiêu

Một dashboard để **Giám đốc Logistics tự xem** tình hình kinh doanh và vận hành: số liệu, biểu đồ, và
**nhận xét tự sinh** ngay cạnh biểu đồ. Không cần đọc tài liệu hay chạy lệnh.

**Nguyên tắc**
- **Dashboard không tự tính số.** Mọi con số lấy từ `analysis_bundle()` hoặc `kpi()`, nên số trên
  dashboard luôn khớp với tài liệu và với test. Code dashboard không chứa câu SQL nào (có test kiểm tra).
- **Nhận xét đặt cạnh biểu đồ liên quan**, không gom một chỗ.
- Hai ngôn ngữ: chọn tiếng Việt hoặc tiếng Anh.

## Công nghệ

| Chọn | Lý do |
|---|---|
| **Streamlit** + **Plotly** | Đã chọn trong `CAPABILITY-MAP`. Viết bằng Python nên gọi thẳng `analysis_bundle()`; biểu đồ tương tác (rê chuột xem số) |
| **Thêm 2 thư viện** `streamlit`, `plotly` | Đã được chủ dự án đồng ý (03/10/2026) |

Mở bằng lệnh `uv run logops dashboard`, rồi xem trên trình duyệt ở `http://localhost:8501`.

## Output: các trang

> **Điều chỉnh sau khi bản nháp component được duyệt (03/10/2026):** 8 trang thay vì 7 (thêm trang
> *Giao hàng & dịch vụ*; trang dữ liệu có thêm định nghĩa KPI); **nút chuyển tiếng Việt/tiếng Anh**;
> mọi trang và component **responsive** (từ máy tính đến điện thoại). Biên và giá nhiên liệu là hai ô
> biểu đồ xếp chồng chung trục thời gian, không gộp một biểu đồ hai trục tung.

> **Điều chỉnh lần hai sau rà soát (04/10/2026):** đổi tên trang thành *Tổng quan điều hành*, *Kết
> quả kinh doanh*, *Khách hàng & thị trường*, *Hiệu quả tuyến vận tải*, *Chất lượng giao hàng*,
> *Năng lực & khai thác đội xe*, *Quản lý nhiên liệu*, *Chất lượng dữ liệu & định nghĩa KPI*. Mọi biểu
> đồ có đơn vị và hộp diễn giải; mọi bảng có số thứ tự và bộ lọc theo cột phân loại; nhận xét luôn
> chia tab; không hiện tên biến cơ sở dữ liệu. Bỏ biểu đồ đóng góp theo ngày (nhiễu, không thêm ý
> nghĩa); thay lưới đếm tuyến bằng bảng đánh giá tuyến; trang giao hàng so sánh bốn chuẩn đo đúng
> hẹn; chọn ngày bằng nút Áp dụng.

**Thanh bên (mọi trang):** nút chọn ngôn ngữ (Tiếng Việt / English), khoảng thời gian (mặc định
2022–2024, DD/MM/YYYY).

| # | Trang | Nội dung | Nhận xét hiển thị |
|---|---|---|---|
| 1 | **Tổng quan** | Chọn kỳ: cả giai đoạn hoặc từng năm (so với năm trước). 8 ô KPI có định nghĩa. Tài chính: doanh thu, lợi nhuận đóng góp, biên đóng góp, chi phí vận hành/dặm. Vận hành & dịch vụ: OTD, thời gian chờ bình quân, chuyến hoàn thành, hiệu suất sử dụng đội xe. Một khung nhận xét. Biên đóng góp và giá nhiên liệu theo tháng, hai ô xếp chồng | Toàn bộ, trong một khung có ba tab: Ưu tiên xử lý, Cần theo dõi, Tham khảo |
| 2 | **Lợi nhuận** | Chọn kỳ (tháng / quý / năm) → doanh thu chia cho chi phí và đóng góp (cột chồng), đóng góp mỗi ngày kèm trung bình 30 ngày, **thác nước cầu lợi nhuận** giữa hai năm tùy chọn, lũy kế theo năm, đơn vị kinh tế so với năm đầu, bảng lãi lỗ | Lợi nhuận (*Ưu tiên xử lý*, *Cần theo dõi*) |
| 3 | **Khách hàng & khu vực** | Chọn bang đi / bang đến → **bản đồ Hoa Kỳ** và biên theo bang; phân khúc và loại hàng; các ô tập trung khách hàng (lớn nhất, top 10, top 20, số khách chiếm 80%, HHI), đường Pareto, 15 khách hàng lớn nhất | Lợi nhuận (*thông tin*) |
| 4 | **Tuyến & mạng lưới** | **Bong bóng ma trận tuyến** (sản lượng × biên, kích thước = doanh thu, 3 mức biên) + số tuyến mỗi ô; **cân bằng theo thành phố** (cột hai chiều); lô đi và lô đến theo thành phố; chuyến xuất phát nơi khác theo năm; bảng tuyến | Mạng lưới |
| 5 | **Giao hàng & dịch vụ** | Thanh trượt khung đúng giờ (0–240 phút) → 4 ô; đường tỷ lệ đúng giờ theo độ rộng khung; đúng giờ theo tháng; thời gian chờ lấy hàng so với giao hàng theo năm; đúng giờ theo thành phố | — |
| 6 | **Đội xe & năng suất** | Số xe bận mỗi ngày với p95, p99, xe đang chạy, xe sở hữu; các ô năng suất; phân bố số xe bận; mức sử dụng theo xe; đội xe theo trạng thái; các xe không chạy chuyến nào (chỉ mô tả) | Đội xe |
| 7 | **Nhiên liệu** | Chọn kỳ → gallon mua và tiêu thụ, tỷ lệ, giá trung bình, chi tiêu | Nhiên liệu |
| 8 | **Dữ liệu & định nghĩa** | Các ô chất lượng dữ liệu, phát hiện theo quy tắc, mức tin cậy của dữ liệu, định nghĩa KPI kèm giá trị đội xe | — |

**Responsive:** các ô số và cặp biểu đồ nằm trong cột, tự xếp chồng trên màn hẹp; mọi biểu đồ giãn
theo khung chứa; danh sách dài dùng cột ngang để mọi nhãn đọc được trên điện thoại; bảng rộng cuộn
ngang.

## Không làm trong module này

| Không làm | Lý do |
|---|---|
| Khuyến nghị có số tiền tiết kiệm | Thuộc `optimize` (làm sau); sẽ thêm một trang khi module đó xong |
| Nút xuất báo cáo PDF/HTML | Thuộc `reports` |
| Đăng nhập, triển khai lên máy chủ | Chạy trên máy để demo |
| Nhận xét bằng LLM | Đã có bộ quy tắc |

## Tiêu chí thành công

1. **Mọi trang chạy không lỗi**: test tự động mở từng trang bằng công cụ kiểm thử của Streamlit.
2. **Không có SQL trong code dashboard** (test).
3. **Số trên dashboard khớp với tài liệu**: ví dụ ô doanh thu bằng tổng của lãi lỗ năm (test).
4. **Mỗi trang tải dưới 3 giây** sau lần đầu (tiêu chí trong `docs/01` §5), nhờ cache kết quả.
5. Đủ hai ngôn ngữ cho mọi nhãn; `ruff` sạch.

## Kế hoạch

| Việc | Nội dung |
|---|---|
| D1 | Thêm thư viện, khung app (thanh bên, chọn ngôn ngữ, cache), lệnh `logops dashboard` |
| D2 | Trang Tổng quan + Lợi nhuận |
| D3 | Trang Phân khúc & khu vực + Tuyến & mạng lưới |
| D4 | Trang Đội xe + Nhiên liệu + Chất lượng dữ liệu |
| D5 | Test (mở từng trang, không SQL, khớp số), đo thời gian tải |
| D6 | Đánh giá module, `SUMMARY`, nhật ký, ảnh chụp các trang cho buổi demo |
