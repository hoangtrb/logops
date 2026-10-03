# Spec: metrics

> Module 2/6 · Xem [CAPABILITY-MAP.vi.md](CAPABILITY-MAP.vi.md) · CRISP-DM pha 3 (Chuẩn bị dữ liệu) ·
> Bản tiếng Anh: [SPEC-metrics.md](SPEC-metrics.md) · Đầu vào: kho dữ liệu của module 1 và
> [docs/02-data-understanding.vi.md](docs/02-data-understanding.vi.md) §5

## Mục tiêu

Tạo **một lớp KPI duy nhất** mà mọi module sau (`optimize`, `dashboard`, `reports`) đều đọc từ đó,
để một con số chỉ có một định nghĩa. KPI bám theo SCOR: **chi phí, độ tin cậy giao hàng, hiệu quả
tài sản**, cộng thêm nhiên liệu và an toàn.

**Nguyên tắc**
- **Không bịa:** chỉ tính những gì dữ liệu có. Thứ dữ liệu không có (lương tài xế) thì không đưa
  vào, và ghi rõ là không có.
- **Tỷ lệ = tổng tử số ÷ tổng mẫu số**, không lấy trung bình của các tỷ lệ.
- **Luôn khớp tổng:** cộng các nhóm (tuyến, khách hàng, xe…) cộng dòng "Không gán được" phải bằng
  tổng đội xe.

## Output (hợp đồng của module)

### O1. Ba view nền trong DuckDB (tạo bởi `logops build`)

| View | Một dòng là | Số dòng | Nội dung chính |
|---|---|---:|---|
| `trip_economics` | một chuyến | 85.410 | tuyến, khách hàng, xe, tài xế, tháng; dặm; doanh thu (cước, phụ phí nhiên liệu, phụ phí khác); chi phí nhiên liệu, bảo dưỡng, sự cố (phân bổ, xem dưới); **biên đóng góp** = doanh thu − chi phí đo được |
| `delivery_performance` | một lần lấy/giao | 170.820 | độ lệch so với giờ hẹn (phút), `on_time_flag`, số phút chờ, `location_city`, giờ hẹn trong ngày, thứ trong tuần, tuyến, khách hàng |
| `truck_economics` | một xe | 120 | dặm, số chuyến, doanh thu, chi phí bảo dưỡng, giờ dừng, chi phí bảo dưỡng/dặm, mức sử dụng trung bình, năm sản xuất, gallon mua ÷ gallon tiêu thụ |

**Cách phân bổ chi phí** (đã kiểm trên dữ liệu thật):

| Chi phí | Cách gán vào chuyến | Vì sao |
|---|---|---|
| Nhiên liệu | Tiền mua nhiên liệu *trong tháng* × (gallon chuyến tiêu thụ ÷ tổng gallon tiêu thụ trong tháng) | Phiếu nhiên liệu không gán đúng chuyến: tổng gallon mua lớn hơn gallon tiêu thụ 29%, ở từng chuyến lệch từ 0,32 đến 9 lần. Phân bổ theo lượng tiêu thụ thực tế mà vẫn giữ đúng tổng chi tiêu |
| Bảo dưỡng | Chi phí bảo dưỡng của xe *trong tháng* ÷ tổng dặm của xe trong tháng × dặm của chuyến | Với 92 xe có chạy, mọi tháng có bảo dưỡng đều có chuyến, nên phân bổ theo xe-tháng khớp tổng ở mọi mức lọc thời gian. 690 phiếu còn lại (1,40 triệu USD, 24% chi phí bảo dưỡng) thuộc 28 xe không chạy chuyến nào: 13 xe `Inactive`, 15 xe `Maintenance` |
| Sự cố | Gán thẳng theo `trip_id` | Phiếu sự cố có mã chuyến |
| Lương tài xế | **Không tính** | Dữ liệu không có. Biên đóng góp được ghi rõ là *chưa trừ lương tài xế* |

Phần không gán được vào chuyến nào (bảo dưỡng của 28 xe không chạy chuyến, tiền nhiên liệu của tháng
không có chuyến) nằm trong dòng **"Không gán được"**, để tổng luôn khớp.

### O2. Hàm KPI: `kpi(con, start, end, by=None, on_time_window_min=120)`

Trả về một bảng: mỗi nhóm (`by`) một dòng, cộng dòng tổng đội xe. `by` có thể là `None`, `month`,
`route`, `customer`, `customer_type`, `truck`, `driver`, hoặc `location_city` (chỉ cho KPI giao hàng).

**Danh mục KPI (21)**

| Nhóm SCOR | KPI | Công thức |
|---|---|---|
| Chi phí | `revenue` | Σ cước + phụ phí nhiên liệu + phụ phí khác |
| | `measured_cost` | Σ nhiên liệu + bảo dưỡng + sự cố |
| | `cost_per_mile` | `measured_cost` ÷ Σ dặm |
| | `fuel_cost_per_mile`, `maintenance_cost_per_mile`, `safety_cost_per_mile` | Từng thành phần ÷ Σ dặm |
| | `revenue_per_mile` | `revenue` ÷ Σ dặm |
| | `contribution`, `contribution_margin_pct` | `revenue` − `measured_cost`; chia cho `revenue` |
| | `out_of_route_pct` | Σ (dặm thực tế − dặm chuẩn của tuyến) ÷ Σ dặm chuẩn |
| Nhiên liệu | `mpg` | Σ dặm ÷ Σ gallon tiêu thụ |
| | `fuel_purchased_to_burned` | Σ gallon mua ÷ Σ gallon tiêu thụ (kiểm soát thẻ nhiên liệu) |
| Độ tin cậy | `on_time_pct` | % lần giao có \|lệch\| ≤ cửa sổ (mặc định 120 phút = `on_time_flag`) |
| | `not_late_pct` | % lần giao có thực tế ≤ giờ hẹn |
| | `avg_detention_min`, `detention_hours` | Trung bình và tổng số phút chờ |
| Tài sản | `miles_per_truck_month` | Σ dặm ÷ số tháng-xe có chạy |
| | `utilization` | Trung bình `utilization_rate` (chỉ để so sánh giữa các xe) |
| | `downtime_hours` | Σ giờ dừng do bảo dưỡng |
| An toàn | `incidents_per_million_miles`, `preventable_pct` | Số sự cố ÷ Σ dặm × 10⁶; % sự cố phòng tránh được |

### O3. Lệnh `logops kpi`

`uv run logops kpi --by route --from 2024-01-01 --to 2024-12-31 --window 60` in bảng KPI ra
terminal. Dùng để kiểm tra nhanh và để demo.

### O4. Tài liệu

- `docs/03-kpi-definitions.md` / `.vi.md`: **sinh tự động** từ danh mục KPI trong code (tên, công
  thức, đơn vị, nguồn, giá trị đội xe), nên không bao giờ lệch khỏi code.
- `docs/reviews/02-metrics.md` / `.vi.md`: đánh giá cuối module (xem phần Đánh giá cuối module).

## Không làm trong module này

| Không làm | Lý do |
|---|---|
| KPI chạy không tải | `idle_time_hours` là nhiễu ngẫu nhiên: tương quan ≈ 0 với thời gian chuyến, quãng đường và nhiên liệu |
| Giá nhiên liệu theo địa điểm | Chênh 0,02 USD/gallon giữa các thành phố, không có tín hiệu |
| KPI theo `facility_id` | Cột gần như ngẫu nhiên; dùng `location_city` |
| Lương tài xế, lợi nhuận ròng | Không có trong dữ liệu |
| Ước tính tiết kiệm, khuyến nghị | Thuộc module `optimize`. Ví dụ: có nên giữ 28 xe không chạy chuyến nào, so với sản lượng hiện tại và xu hướng tương lai. Module này chỉ cung cấp số liệu (`truck_economics`); đề xuất hiển thị trên dashboard để người xem cân nhắc |
| Biểu đồ | Thuộc `dashboard` và `reports` |

## Tiêu chí thành công

1. **Khớp với báo cáo DQ:** tổng doanh thu 298,62 triệu, nhiên liệu 95,59 triệu, bảo dưỡng 5,73
   triệu, sự cố 2,65 triệu USD; chi phí/dặm 0,851 USD; MPG 6,45; đúng giờ 44,6% (cửa sổ 120 phút).
2. **Khớp tổng:** với mọi `by`, tổng các nhóm + "Không gán được" = tổng đội xe, cho mọi KPI dạng tổng.
3. **Cửa sổ đúng giờ là tham số:** cửa sổ 120 phút cho đúng `on_time_flag`; đổi cửa sổ thì `on_time_pct` đổi theo. Tỷ lệ không trễ là KPI riêng (`not_late_pct`).
4. **Bộ lọc thời gian đúng:** lọc 2024 cho ra đúng tổng của năm 2024.
5. Mỗi nhóm KPI có ít nhất một test trên dữ liệu mẫu, cộng một test tích hợp đối chiếu số thật;
   `ruff` sạch.
6. Build tăng không quá 5 giây.

## Đánh giá cuối module (áp dụng cho mọi module)

Khi kết thúc, viết `docs/reviews/02-metrics.md` / `.vi.md` gồm: output đã giao so với spec, số liệu
thực tế đo được, những gì **không** làm được và vì sao, và phát hiện mới về dữ liệu. Chỉ ghi điều đã
kiểm chứng. Đồng thời cập nhật `docs/SUMMARY.md` / `.vi.md` (tổng kết toàn dự án).

## Kế hoạch (6 việc)

| Việc | Nội dung | Kiểm chứng |
|---|---|---|
| M1 | View `trip_economics` + phân bổ chi phí | Tổng khớp báo cáo DQ (tiêu chí 1) |
| M2 | View `delivery_performance` + cửa sổ đúng giờ | 44,6% ở 120 phút; không trễ 33,3% |
| M3 | Hàm `kpi()`: danh mục 21 KPI, `by`, lọc thời gian, dòng "Không gán được" | Tiêu chí 2 và 4 |
| M4 | View `truck_economics` + KPI tài sản và an toàn | Test trên dữ liệu mẫu |
| M5 | Lệnh `logops kpi` + `docs/03-kpi-definitions` | Chạy lệnh trên dữ liệu thật |
| M6 | Đánh giá module 1 và 2 + `docs/SUMMARY` | Đọc lại, mọi số có nguồn |

## Câu hỏi mở

Không có. Lương tài xế được loại khỏi phạm vi thay vì giả định một mức lương.
