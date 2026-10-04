# Kịch bản trình bày (phỏng vấn 05/10/2026)

> Bản tiếng Anh: [demo-script.md](demo-script.md) · Số liệu: [SUMMARY.vi.md](SUMMARY.vi.md) ·
> Đánh giá: [reviews/](reviews/) · Mọi con số dưới đây lấy từ dashboard, giai đoạn 01/01/2022 –
> 31/12/2024.

## 0. Chuẩn bị (trước giờ hẹn)

- [ ] `uv run logops dashboard` → mở http://localhost:8501, chọn **Vi**, chạy qua từng trang một lần
  để dữ liệu được nạp sẵn (lần đầu mỗi trang mất vài giây, sau đó dưới 3 giây).
- [ ] Đóng mọi chương trình đang mở kho `data/warehouse.duckdb` (DBeaver, notebook).
- [ ] Có sẵn bản dự phòng trong `reports/output/`: `bao-cao-van-tai-2022-01-01-2024-12-31.pdf` và
  `.html` (mở được khi không có mạng).
- [ ] Thu nhỏ thanh bên nếu chiếu màn hình nhỏ; phóng to trình duyệt 110%.

## 1. Mở đầu (30 giây)

> "Em lấy một bộ dữ liệu vận hành của doanh nghiệp vận tải đường bộ (Kaggle, dữ liệu mô phỏng: 120
> xe, 200 khách hàng, 85 nghìn chuyến trong 3 năm) và đặt bài toán như một giám đốc vận tải: giảm
> ít nhất 3% chi phí vận hành mỗi năm và nâng chất lượng giao hàng. Em làm theo CRISP-DM qua sáu
> module, từ làm sạch dữ liệu đến dashboard và báo cáo xuất được."

Trang: **Tổng quan điều hành** (thẻ "Đề tài và nguồn dữ liệu" ở đầu trang).

## 2. Tổng quan điều hành (1 phút)

- Doanh thu **298,62 tr USD**, chi phí vận hành **103,88 tr USD**, lợi nhuận đóng góp **194,74 tr
  USD**, biên **65,2%** (chưa trừ lương tài xế và chi phí chung: dữ liệu không có).
- Giao hàng đúng hẹn **44,6%** theo khung ±2 giờ, nhưng **91,2%** nếu tính theo ngày hẹn: cùng một
  dữ liệu, chuẩn đo quyết định câu chuyện.
- Điểm chính "Ưu tiên xử lý": **lợi nhuận tăng nhờ nhiên liệu rẻ đi, không nhờ vận hành tốt hơn**:
  93% mức tăng (4,12 trong 4,42 tr USD) đến từ giá nhiên liệu, vì phụ phí nhiên liệu thu của khách
  đứng yên. Đây là rủi ro khi giá nhiên liệu tăng lại.

## 3. Hiệu quả tuyến vận tải (1 phút)

- **33% số lô kết thúc ở nơi không có hàng chiều về**; 16/20 thành phố lệch quá 20%.
- Ở 95,4% số lần, chuyến kế tiếp của xe bắt đầu ở thành phố khác: đúng bằng mức điều phối ngẫu
  nhiên, nghĩa là dữ liệu không cho thấy việc ghép chuyến theo vị trí xe.
- Bảng đánh giá tuyến: mọi tuyến đều có lãi đóng góp; tuyến biên thấp là việc **đàm phán lại giá**,
  không phải ngừng tuyến.

## 4. Năng lực đội xe (45 giây)

- 92 xe từng chạy, sở hữu 120; 99% số ngày chỉ cần tối đa 75 xe chạy cùng lúc.
- **28 xe chưa chạy chuyến nào trong 3 năm** vẫn tốn 1,40 tr USD bảo dưỡng.

## 5. Khuyến nghị tối ưu (2 phút): trọng tâm

Rê chuột vào từng ô để hiện cách tính.

| Ô | Số | Câu nói |
|---|---:|---|
| Mục tiêu | 1,04 tr USD/năm | 3% × 34,65 tr USD chi phí vận hành đo được mỗi năm |
| Tiết kiệm đo được | 0,47 tr USD | Thanh lý 28 xe chưa từng chạy: chắc chắn, không ảnh hưởng vận hành |
| Tiềm năng tối đa | 2,42 tr USD | Phụ phí nhiên liệu về trung vị, tăng cước tối đa +5% cho 20 tuyến biên thấp, rà soát 13 xe ít chạy: cần khách chấp nhận |
| Tổng | 2,89 tr USD (278%) | Đạt mục tiêu khi làm phần chắc chắn và thu thêm 0,57 tr USD, ví dụ khách chấp nhận 59,6% mức nâng phụ phí |

- **Ghép chuyến (mô phỏng):** điều xe rảnh gần nhất cho mỗi lô → chuyến phải điều xe giảm từ
  89,5% xuống 41,1%, dặm chạy rỗng giảm 59,5%. Quãng đường lấy từ mạng tuyến, mỗi dặm chạy
  rỗng 0,605 USD (giá nhiên liệu ÷ số dặm mỗi gallon, đều từ dữ liệu). Rê chuột vào ô: riêng mô
  hình tính ra 12,56 tr USD, vượt lượng nhiên liệu mua ngoài chuyến, nên em chỉ áp tỷ lệ giảm
  lên phần nhiên liệu đó: **tối đa 4,27 tr USD mỗi năm**, không cộng vào tổng.
- **Quãng điều xe bao lâu là hợp lý?** Nên trong một ngày lái (11 giờ, khoảng 630 dặm); xa hơn
  thì tìm hàng chiều về tại chỗ. Không đặt giới hạn cứng được: một phần ba số lô kết thúc ở nơi
  ít hàng đi, và mọi giới hạn đến 24 giờ đều cần thêm hàng nghìn xe.
- **Đã kiểm tra và không đề xuất:** giao trễ không có nguyên nhân lặp lại theo khách, tuyến, tài xế,
  giờ hẹn (tương quan giữa các năm ≤ 0,14): em không bịa ra giải pháp mà đề xuất ghi mã lý do trễ.

## 6. Xuất báo cáo (45 giây)

- Thanh bên → **Xuất báo cáo** → PDF → **Tạo báo cáo**: chạy nền, vẫn thao tác dashboard; xong thì
  nút Tải về đầy màu xanh.
- Mở PDF: bìa (đề tài, nguồn dữ liệu) → mục lục, danh mục hình và bảng có số trang → **Tóm tắt điều
  hành** một trang (cần hành động ngay, cần theo dõi, cơ hội tiết kiệm).

## 7. Kết (30 giây)

> "Với Co.op, cùng khung này dùng được ngay cho dữ liệu chuyến, xe, nhiên liệu, giao nhận nội bộ.
> Ba việc em sẽ đề xuất làm trước, gần như không tốn tiền: đối soát thẻ nhiên liệu với chuyến theo
> từng xe mỗi tháng; ghi lại mọi lần điều xe giữa hai chuyến; ghi mã lý do khi giao trễ. Có ba thứ
> đó thì các con số 'chưa giải thích được' và 'giả thuyết' hôm nay sẽ đo được."

## 8. Câu hỏi có thể gặp

| Câu hỏi | Trả lời ngắn |
|---|---|
| Dữ liệu mô phỏng thì áp dụng thực tế được không? | Phương pháp và quy trình kiểm tra dữ liệu áp dụng được; con số cụ thể phải tính lại trên dữ liệu thật. Em cũng ghi rõ chỗ dữ liệu mô phỏng không nhất quán (ví dụ 54% chuyến của cùng một xe chồng thời gian). |
| Biên 65% có cao bất thường? | Đó là lợi nhuận đóng góp, chưa trừ lương tài xế và chi phí chung (không có trong dữ liệu). Em thay bằng "chi phí tài xế hòa vốn": tuyến yếu nhất chỉ lỗ nếu chi phí tài xế vượt 0,857 USD/dặm. |
| Vì sao OTD chỉ 44,6%? | Cờ đúng giờ của dữ liệu là ±2 giờ, tính cả đến sớm. Theo ngày hẹn là 91,2%. Độ lệch phân bố đều từ −3 đến +6 giờ, không phụ thuộc độ dài chuyến. |
| Tăng giá có mất khách? | Mỗi tuyến có "sụt sản lượng hòa vốn": trung vị 9,6% ở mức +5%, tức tuyến có thể mất chừng đó sản lượng mà lợi nhuận không thấp hơn hiện nay. Vì vậy tăng giá là tiềm năng tối đa, không phải tiết kiệm chắc chắn. |
| Tiết kiệm từ ghép chuyến tính thế nào? | Quãng đường giữa các thành phố lấy từ mạng tuyến (đường ngắn nhất khi không có tuyến trực tiếp), nhiên liệu mỗi dặm = 3,899 USD/gallon ÷ 6,45 dặm/gallon, đều từ dữ liệu. Mô phỏng giảm 59,5% dặm chạy rỗng; áp lên 7,18 tr USD nhiên liệu mua ngoài chuyến thì tối đa 4,27 tr USD mỗi năm. Quãng đường theo mạng tuyến dài hơn đường thật, có tọa độ thật sẽ chính xác hơn. |
| Vì sao không đề xuất về tài xế, nhân sự? | Phạm vi tập trung vào năng suất và chất lượng vận hành; dữ liệu cũng không có lương tài xế. |
| Công cụ? | Python, DuckDB, Polars, Streamlit, Plotly; 160 test tự động; chạy trên một laptop, không cần máy chủ. |
| Triển khai cho Co.op cần gì? | Trích xuất dữ liệu chuyến, xe, nhiên liệu, giao nhận từ TMS/ERP vào cùng cấu trúc; chạy lại bộ quy tắc chất lượng dữ liệu trước, rồi mới đến KPI và khuyến nghị. |
