# Spec: optimize

> Module 5/6 · CRISP-DM pha 4 (Mô hình hóa) và pha 5 (Đánh giá) · Bản tiếng Anh:
> [SPEC-optimize.md](SPEC-optimize.md) · Đầu vào: lớp KPI (module 2), lớp phân tích (module 3) · Làm
> lại từ nhánh `feature/optimize` sau module phân tích và dashboard.

## Mục tiêu

Biến các phát hiện thành **khuyến nghị có hành động và số tiền**, so với mục tiêu **ít nhất 3,1 tr
USD trong 3 năm** (1,04 tr USD/năm, 3% chi phí vận hành đo được). Vượt mục tiêu càng tốt, nhưng mọi
con số vẫn phải bảo vệ được trước Giám đốc Logistics.

**Nguyên tắc**
- Chỉ ra số tiền khi tín hiệu **lặp lại qua các năm** (2022–23 so với 2024).
- **Không dùng dữ liệu bên ngoài.** Ngoại lệ duy nhất là chi phí triển khai các biện pháp cải tiến
  dữ liệu (O5), lấy từ nguồn công khai có trích dẫn và ghi rõ là ước tính.
- Ba loại số tiền: **tiết kiệm đo được** (có sẵn trong dữ liệu), **mức trần** (cần một quyết định
  hoặc khách hàng chấp nhận thay đổi), **chưa giải thích được** (tiền dữ liệu chưa giải thích
  được). Đo được và mức trần hiển thị riêng, tổng của chúng ghi rõ là "tổng tiềm năng"; khoản
  chưa giải thích được không bao giờ cộng vào tổng nào.
- Mọi thứ hiển thị theo chuẩn trình bày: đơn vị, diễn giải dễ hiểu, tên theo VI/EN.

## Output

### O1. Quy mô đội xe (`optimize/fleet.py`)

- **Số xe cần** = ⌈nhu cầu xe mỗi ngày ở mức đảm bảo (mặc định đủ cho 99% số ngày) × (1 + tỷ lệ
  chuyến thiếu mã xe) × (1 + tăng trưởng) ÷ tỷ lệ xe sẵn sàng⌉. Nhu cầu mỗi ngày lấy từ "số xe hoạt
  động mỗi ngày" của lớp phân tích, nên dashboard và module này cùng một con số. Tỷ lệ sẵn sàng = 1 −
  giờ dừng bảo dưỡng ÷ tổng giờ của các xe đang chạy. Kịch bản tăng trưởng 0 / 5 / 10 / 20%.
- **Thanh lý theo bậc:** (1) 13 xe `Ngừng hoạt động` chưa từng chạy, (2) 15 xe `Đang bảo dưỡng` chưa
  từng chạy, (3) xe đang chạy vượt nhu cầu, ưu tiên xe chạy ít dặm nhất. Nếu kịch bản cần nhiều xe hơn
  số đang chạy, xe `Đang bảo dưỡng` được đưa trở lại trước.
- **Tiền:** bậc 1–2 = chi phí bảo dưỡng mỗi năm của các xe đó (**đo được**); bậc 3 = mức trần. Giá
  bán lại không có trong dữ liệu: lợi ích chưa định lượng.
- **Đối chiếu:** ngày bận nhất và số ngày vượt nhu cầu.

### O2. Giá cước tuyến (`optimize/lanes.py`)

- Từng tuyến: số chuyến, doanh thu, lợi nhuận đóng góp, biên, mức bù chi phí nhiên liệu của phụ phí
  nhiên liệu, và **chi phí tài xế hòa vốn mỗi dặm** (lợi nhuận đóng góp ÷ số dặm): tuyến chỉ lỗ khi
  chi phí tài xế vượt mức này. Thay cho việc đoán lương tài xế không có trong dữ liệu.
- **S1** phụ phí nhiên liệu: tuyến có mức phụ phí dưới trung vị được nâng lên trung vị.
- **S2** giá cước: sau S1, tuyến đông chuyến biên thấp ("Đàm phán lại giá") và tuyến ít chuyến biên
  thấp ("Rà soát giá cước") được đưa về gần biên trung vị, mức tăng giới hạn 5% (con số chính), 10%
  hoặc không giới hạn (lý thuyết) của cước vận chuyển.
- **S3** mô phỏng: phụ phí theo giá nhiên liệu hằng tháng, tổng doanh thu không đổi trong kỳ. Cho
  thấy rủi ro giá nhiên liệu được chia sẻ thế nào; không tính là tiết kiệm.
- Mỗi tuyến có **mức sụt sản lượng tối đa** trước khi thay đổi làm lợi nhuận thấp hơn hiện tại.
- **Tiền:** S1 và S2 là **mức trần** (khách hàng phải chấp nhận).

### O4. Giao trễ (`optimize/lateness.py`)

- Tỷ lệ giao trễ quá 2 giờ theo thành phố nhận, khách hàng, giờ hẹn, tuyến và tài xế; chỉ coi là tín
  hiệu khi tỷ lệ của nhóm lặp lại giữa 2022–23 và 2024 (tương quan ≥ 0,7) và chênh lệch giữa các nhóm
  đủ lớn.
- **Dự kiến:** không có nguyên nhân lặp lại (độ lệch trải đều từ sớm 3 giờ đến muộn 6 giờ ở mọi độ
  dài chuyến). Khi đó **không đề xuất**: hiển thị bằng chứng và bỏ đòn bẩy này.

### O5. Cải tiến quy trình dữ liệu (`optimize/data_gaps.py`)

Mỗi lỗ hổng một dòng (đối soát nhiên liệu, chuyến điều xe không được ghi, thiếu mã xe và tài xế, sai
bang và mã kho, giờ chạy không tải không dùng được): bằng chứng, **chi phí khi không làm** (tính từ
dữ liệu), biện pháp bậc 1 (quy trình, cấu hình, gần như không tốn tiền) và bậc 2 (thiết bị), **chi
phí triển khai ước tính** kèm nguồn, mức ưu tiên.

### O6. Khuyến nghị, đánh giá, trang dashboard

- Bảng `recommendations` trong kho dữ liệu và hàm `optimize.recommendations()`: lĩnh vực, hạng mục,
  hành động, số tiền mỗi năm, loại (đo được / mức trần / chưa giải thích được), bằng chứng.
- `logops optimize [--growth 0.05] [--cap 5]` in danh sách khuyến nghị.
- Sinh `docs/05-evaluation` (EN/VI): tổng so với mục tiêu, tách riêng đo được và mức trần.
- Trang dashboard **"Khuyến nghị tối ưu"**: tổng so với mục tiêu, kịch bản đội xe (thanh trượt tăng
  trưởng), kịch bản giá tuyến (chọn mức giới hạn tăng giá), bảng cải tiến dữ liệu, các đòn bẩy đã bỏ
  kèm bằng chứng.

### O3. Ghép chuyến (nếu còn thời gian)

Mô phỏng theo ngày: mỗi lô ưu tiên giao cho xe đang rảnh ở đúng thành phố lấy hàng. Kết quả: số lần
điều xe giữa các thành phố tránh được và số xe cần. Dữ liệu không có dặm chạy rỗng nên tiền chỉ tính
qua chi phí mỗi lần điều xe do người xem nhập, ghi rõ là ước tính.

## Không làm

| Không làm | Lý do |
|---|---|
| Mô hình ML dự báo trễ, MPG theo tài xế/xe, chạy không tải, giá nhiên liệu theo địa điểm, lợi nhuận theo khách, thay xe cũ | Không lặp lại qua các năm hoặc là nhiễu (đã kiểm tra ở lần optimize đầu) |
| Ghép hàng, tính phí lưu xe, điểm nghẽn xưởng và kho nhận | Chủ dự án đã bỏ (03/10/2026) |
| Lương tài xế, chi phí chung, giá bán lại xe, độ co giãn nhu cầu | Không có trong dữ liệu: dùng số hòa vốn thay thế |

## Tiêu chí thành công

1. Mọi số tiền truy được về câu truy vấn và có loại; không cộng chung các loại.
2. Đội xe: đúng trên dữ liệu mẫu tính tay được; số xe cần tăng theo tăng trưởng; nhu cầu mỗi ngày
   bằng của lớp phân tích.
3. Tuyến: doanh thu và lợi nhuận các tuyến cộng lại bằng tổng toàn đội; mỗi tuyến đúng một nhóm;
   tuyến đạt chuẩn không bị tăng giá.
4. Giao trễ: áp dụng kiểm tra lặp lại và hiển thị kết quả dù ra sao.
5. Lỗ hổng dữ liệu: mọi chi phí triển khai có nguồn; mọi chi phí khi không làm có câu truy vấn.
6. Trang dashboard chạy ở cả hai ngôn ngữ; `ruff` sạch; test pass.

## Kế hoạch

| Bước | Nội dung |
|---|---|
| 1 | Chuyển `fleet.py`, `lanes.py`, `data_gaps.py` từ `feature/optimize`; đồng bộ nhu cầu xe mỗi ngày với lớp phân tích; test dữ liệu mẫu |
| 2 | Kiểm tra lặp lại cho giao trễ (`lateness.py`) |
| 3 | `recommendations()`, bảng trong kho, lệnh CLI, `docs/05-evaluation` |
| 4 | Trang dashboard, bản dịch, test, ảnh chụp |
| 5 | O3 ghép chuyến nếu còn thời gian |
| 6 | Đánh giá `docs/reviews/05-optimize`, SUMMARY, nhật ký, CAPABILITY-MAP |

> **O3 đã làm 04/10/2026:** mốc so sánh là mô phỏng cách điều phối hiện tại, không dùng cách gán xe
> trong dữ liệu (các chuyến chồng thời gian); tiền thuộc loại "ước tính" (giả thuyết), không cộng vào tổng.
> **O3 sửa 04/10/2026 (chủ dự án):** xe rảnh gần nhất, quãng đường theo mạng tuyến, nhiên liệu
> mỗi dặm từ dữ liệu; tiền = tỷ lệ giảm dặm chạy rỗng × nhiên liệu mua ngoài chuyến (mức tối đa).
