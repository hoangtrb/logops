# Spec: optimize

> Module 3/6 · CRISP-DM pha 4 (Mô hình hóa) và pha 5 (Đánh giá) · Bản tiếng Anh:
> [SPEC-optimize.md](SPEC-optimize.md) · Đầu vào: lớp KPI của module 2
> ([reviews/02-metrics.vi.md](docs/reviews/02-metrics.vi.md) §6)

## Mục tiêu

Biến KPI thành **khuyến nghị có hành động cụ thể và số tiền**, chỉ cho những đòn bẩy **có tín hiệu
thật**, rồi đối chiếu với mục tiêu ≥ 3,1 triệu USD / 3 năm (khoảng 1,04 triệu USD/năm).

**Nguyên tắc**
- Chỉ đưa ra số tiền khi tín hiệu **lặp lại qua các năm** (2022–23 so với 2024).
- Không giả định thứ dữ liệu không có. Điều chưa biết thì để thành **tham số do người xem nhập**,
  hoặc lấy từ **nguồn công khai có trích dẫn** và ghi rõ là ước tính tham khảo.
- Tách rõ **tiết kiệm đo được** khỏi **cận trên** (phụ thuộc vào việc khách hàng chấp nhận).

## Kiểm tra tín hiệu (đã chạy trên dữ liệu thật)

| Hướng | Bằng chứng | Quyết định |
|---|---|---|
| Quy mô đội xe | Số xe bận mỗi ngày: trung vị 66, p99 75, cao nhất 80; đội có 120 xe (92 xe chạy); sản lượng theo năm 28.589 / 28.165 / 28.656 | ✅ P1 |
| Lợi nhuận tuyến | Biên 50,4–72,7%, lặp lại qua các năm (tương quan 0,946) | ✅ P2 |
| Phụ phí nhiên liệu | Đơn giá cố định theo tuyến 0,15–0,34 USD/dặm, không theo giá nhiên liệu; chi phí nhiên liệu/dặm giống nhau ở mọi tuyến (0,601–0,607) | ✅ Trong P2 |
| Chất lượng dữ liệu → quy trình | Lỗ hổng dữ liệu có tác động đo được (ví dụ 5,57 triệu gallon mua chưa đối soát với tiêu thụ) | ✅ P4 |
| Điểm nghẽn xưởng bảo dưỡng và cửa nhận hàng | Có tín hiệu, nhưng chủ dự án đánh giá chưa thực tế | ❌ Bỏ (quyết định 03/10) |
| Ghép hàng, tính phí chờ | Hàng gấp không chờ ghép được; phí chờ không hợp lý | ❌ Bỏ (quyết định 03/10) |
| Mô hình ML dự báo trễ, MPG theo tài xế/xe, chạy không tải, giá nhiên liệu theo địa điểm, lợi nhuận theo khách hàng, thay xe cũ | Không lặp lại qua các năm, hoặc là nhiễu | ❌ Bỏ, trình bày kèm bằng chứng |

## Output

### P1. `fleet_plan`: đánh giá quy mô đội xe → đề xuất → đối chiếu

**Đánh giá:**

| Bước | Cách tính | Nguồn |
|---|---|---|
| Nhu cầu xe mỗi ngày | Mỗi chuyến chiếm xe từ ngày xuất phát, trong ⌈thời gian chuyến ÷ 24 giờ⌉ ngày | `trips` |
| Nhu cầu thiết kế | Phân vị `percentile` (mặc định p99) × (1 + tăng trưởng) | Kịch bản 0 / +5 / +10 / +20% |
| Hệ số sẵn sàng | 1 − giờ dừng bảo dưỡng ÷ tổng giờ của các xe đang chạy | `maintenance_records` |
| Số xe cần | ⌈nhu cầu thiết kế ÷ hệ số sẵn sàng⌉ | |

**Đề xuất cải tiến theo bậc:**
1. Thanh lý 13 xe `Inactive`.
2. Thanh lý hoặc sửa và đưa vào dùng 15 xe `Maintenance`, tùy kịch bản tăng trưởng.
3. Xem lại số xe đang chạy vượt nhu cầu thiết kế.

Mỗi bậc có **tiết kiệm đo được** (chi phí bảo dưỡng mỗi năm của các xe đó). Tiền bán xe không có trong
dữ liệu, ghi là *lợi ích chưa định lượng*.

**Đối chiếu:** so số xe cần với (a) số xe có chạy ít nhất một chuyến mỗi tháng, theo `truck_utilization_metrics`, và (b) ngày bận nhất trong 3 năm.

### P2. `lane_pricing`: lợi nhuận tuyến → phân loại → kịch bản cải tiến

**Đánh giá mỗi tuyến (58 tuyến):** số chuyến, doanh thu (cước và phụ phí), chi phí đo được, biên đóng
góp, mức bù nhiên liệu của phụ phí, và **chi phí tài xế hòa vốn** = đóng góp ÷ dặm, tức tuyến lỗ nếu
chi phí tài xế vượt mức này. Dữ liệu không có lương, nên đây là cách trả lời "lời hay lỗ" mà không cần
giả định.

**Phân loại** theo biên (so với trung vị) × sản lượng (so với trung vị):

| Nhóm | Biên | Sản lượng | Hướng xử lý |
|---|---|---|---|
| Chủ lực | Cao | Cao | Giữ, ưu tiên năng lực xe |
| Cần tăng giá | Thấp | Cao | Ưu tiên điều chỉnh giá |
| Ngách có lời | Cao | Thấp | Giữ, cân nhắc mở rộng |
| Xem xét lại | Thấp | Thấp | Tăng giá hoặc giảm ưu tiên |

**Kịch bản cải tiến** (mỗi kịch bản có lợi nhuận tăng thêm mỗi năm và **mức mất khách tối đa trước khi
lỗ** so với hiện tại):
- **S1:** chuẩn hóa phụ phí nhiên liệu, đưa các tuyến dưới trung vị lên 0,245 USD/dặm.
- **S2:** S1 + điều chỉnh cước các tuyến "Cần tăng giá" và "Xem xét lại" lên biên trung vị.
- **S3 (mô phỏng):** phụ phí theo chỉ số giá nhiên liệu, *phụ phí/dặm = (giá − giá cơ sở) ÷ MPG*,
  chạy trên giá thực tế 2022–2024. Giá cơ sở là tham số. Mục đích là cho thấy rủi ro giá được chia
  sẻ ra sao, không phải để cộng vào tiết kiệm.

S2 được tính *sau* S1 để không cộng trùng.

### P4. Đánh giá dữ liệu → quy trình cải tiến: chi phí làm so với chi phí không làm

Mỗi lỗ hổng dữ liệu một dòng:
- vấn đề và bằng chứng (từ module 1–2);
- **chi phí khi không làm**, đo từ dữ liệu, ví dụ giá trị nhiên liệu chưa đối soát, chi phí không gán
  được;
- biện pháp khả thi, chia **mức 1** (quy trình hoặc cấu hình, gần như không tốn tiền) và **mức 2**
  (thiết bị hoặc tích hợp);
- **chi phí thực hiện ước tính**, từ nguồn công khai có trích dẫn, ghi rõ là tham khảo;
- thứ tự ưu tiên.

Tài liệu tự sinh: `docs/04-data-process-improvements.md` / `.vi.md`.

### P5. Khuyến nghị, đánh giá, tài liệu

- Bảng `recommendations` trong kho và hàm `recommendations()`: đầu vào chung cho `insights`,
  `dashboard` và `reports`.
- Lệnh `uv run logops optimize [--growth 5]`.
- `docs/05-evaluation` (tự sinh): tổng tác động so với mục tiêu, tách tiết kiệm đo được khỏi cận trên.
- `docs/reviews/03-optimize`, cập nhật `SUMMARY`, `CAPABILITY-MAP`, `00-analytical-approach` (ghi lý
  do bỏ mô hình trễ, MPG, điểm nghẽn, ghép hàng, phí chờ), và `docs/01` §5 (tiêu chí AUC).

## Tiêu chí thành công

1. Mọi con số tiền truy về được truy vấn tạo ra nó; tách tiết kiệm đo được khỏi cận trên.
2. `fleet_plan` đúng trên dữ liệu mẫu tính tay; số xe cần tăng khi tăng trưởng tăng; có phần đối chiếu.
3. `lane_pricing`: tổng doanh thu và đóng góp của các tuyến khớp KPI đội xe; mỗi tuyến thuộc đúng một
   nhóm; tuyến đạt chuẩn có mức tăng giá = 0.
4. P4: mỗi chi phí thực hiện có nguồn trích dẫn; mỗi chi phí khi không làm có truy vấn tạo ra nó.
5. Test trên dữ liệu mẫu + test tích hợp; `ruff` sạch.
