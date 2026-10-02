# Lộ trình: Logistics Ops Optimizer

> Bản tiếng Anh: [roadmap.md](roadmap.md) · Các module: [CAPABILITY-MAP.vi.md](../CAPABILITY-MAP.vi.md)
> **Hạn chót: phỏng vấn thứ Hai 05/10/2026.** Đóng băng tối Chủ nhật 04/10/2026.

## Nguyên tắc cho cuối tuần

- **Module gọn nhẹ.** Chỉ test trọng yếu (mỗi quy tắc/engine một test trên dữ liệu mẫu, mỗi
  module một test tích hợp). Hạng mục mở rộng bị cắt trước tiên.
- **Mỗi module một vòng spec → plan → build**, nhưng spec và plan ngắn (mỗi loại một trang).
- **Ưu tiên demo.** Nếu thiếu thời gian, một dashboard chạy được + một loại báo cáo có giá trị hơn
  một lớp kiểm tra chất lượng dữ liệu hoàn hảo.
- **Mỗi module kết thúc ở một điểm kiểm tra**: test + ruff xanh, rà soát nhanh, rồi chuyển tiếp.

## Lịch làm việc

| Thời gian | Module | Pha CRISP-DM | Bắt buộc hoàn thành | Cắt nếu trễ |
|---|---|---|---|---|
| **Thứ 6 02/10** | `data-platform` | 2 Hiểu dữ liệu, 3 Chuẩn bị dữ liệu | `logops build` → 14 bảng có kiểu trong DuckDB; quy tắc DQ về khóa và giá trị; báo cáo DQ EN/VI kèm số liệu nền | `agg_drift` (T6), gia cố dedup/hiệu năng (T8) |
| **Sáng Thứ 7 03/10** | `metrics` | 3 Chuẩn bị dữ liệu | View KPI bằng SQL: chi phí/dặm (nhiên liệu, bảo dưỡng, tài xế, dặm rỗng), % đúng giờ, thời gian chờ, MPG, chạy không tải, mức sử dụng, chi phí bảo dưỡng & an toàn | view chi phí an toàn |
| **Chiều Thứ 7 03/10** | `optimize` | 4 Mô hình hóa, 5 Đánh giá | 4 engine, mỗi engine có ước tính tiết kiệm $: tuyến lỗ, mô hình rủi ro trễ (+ yếu tố chính, AUC), xe/tài xế tốn nhiên liệu so với trung vị đội xe, tối ưu quy mô đội xe + cảnh báo bảo dưỡng | demo phân công bằng LP (mở rộng) |
| **Sáng CN 04/10** | `insights` | 6 Triển khai | Nhận xét bằng Claude cho từng báo cáo (có cache); câu hỏi tiếng thường → SQL | câu hỏi → SQL |
| **Sáng CN 04/10** | `dashboard` | 6 Triển khai | Streamlit: trang tổng quan + một trang cho mỗi lĩnh vực trọng tâm + nút xuất báo cáo | bộ lọc riêng từng trang ngoài khoảng ngày |
| **Chiều CN 04/10** | `reports` | 6 Triển khai | Loại báo cáo + khoảng ngày → PDF / HTML; làm Executive Summary trước, rồi 5 loại còn lại | PDF (chỉ giữ HTML) |
| **Chiều CN 04/10** | Demo & tài liệu | 5 Đánh giá | `docs/05-evaluation.md`, README (EN/VI), kịch bản demo 5 phút, commit cuối | — |
| **Tối CN 04/10** | **Đóng băng** | | Tập dượt demo; không thêm tính năng | |

## Phác thảo công việc từng module

Danh sách việc chi tiết nằm trong plan của từng module sau khi viết spec. Module 1 đã được
chia nhỏ trong [todo.vi.md](todo.vi.md).

### 1. data-platform (Thứ 6) — [plan.vi.md](plan.vi.md) · [todo.vi.md](todo.vi.md)
T1 khung dự án · T2 lát cắt một bảng · T3 đủ 14 bảng · T4 quy tắc khóa · T5 quy tắc giá trị ·
T6 agg_drift · T7 báo cáo DQ EN/VI · T8 gia cố · T9 tài liệu hiểu dữ liệu

### 2. metrics (sáng Thứ 7)
1. Spec + plan (ngắn)
2. View chi phí: chi phí/dặm tách theo nhiên liệu, bảo dưỡng, lương tài xế, dặm rỗng; theo tuyến và khách hàng
3. View dịch vụ: % đúng giờ, số giờ chờ theo kho / tuyến / khung giờ
4. View tài sản: MPG, thời gian chạy không tải, mức sử dụng, chi phí bảo dưỡng và thời gian dừng mỗi xe
5. Tham số khoảng ngày dùng chung cho mọi view; mỗi view một test trên dữ liệu mẫu

### 3. optimize (chiều Thứ 7)
1. Spec + plan (ngắn)
2. Lợi nhuận tuyến: đánh dấu tuyến lỗ, mức điều chỉnh giá cần thiết, tác động $
3. Rủi ro trễ: mô hình gradient boosting, AUC, các yếu tố chính (feature importance)
4. Nhiên liệu: MPG / chạy không tải bất thường theo xe và tài xế; tiết kiệm nếu đưa về trung vị đội xe
5. Đội xe: xe ít dùng → số xe tối ưu; cảnh báo xe chi phí cao / đến hạn bảo dưỡng
6. Bảng `recommendations` (lĩnh vực, đối tượng, hành động, ước tính tiết kiệm $) cấp dữ liệu cho dashboard và báo cáo

### 4. insights (sáng CN)
1. Client Claude + prompt nhận xét cho từng loại báo cáo; cache theo (báo cáo, khoảng ngày, hash dữ liệu)
2. Câu hỏi tiếng thường → SQL trên các view KPI (chỉ đọc, giới hạn số dòng)
3. Kiểm soát chi phí: xác nhận model và chi phí dự kiến với người dùng trước lần chạy thật đầu tiên

### 5. dashboard (sáng CN)
1. Tổng quan: KPI chính + tổng tiết kiệm ước tính
2. Mỗi lĩnh vực trọng tâm một trang (chi phí & tuyến, giao hàng, nhiên liệu, đội xe & bảo dưỡng)
3. Bộ lọc khoảng ngày, khung nhận xét của Claude, nút xuất báo cáo

### 6. reports (chiều CN)
1. Template HTML (tự chứa: CSS + biểu đồ nội tuyến) cho từng loại báo cáo
2. Xuất PDF từ cùng HTML đó
3. CLI `logops report --type ... --from ... --to ... --format pdf|html` + nút trên dashboard

## Tiêu chí kết thúc mỗi ngày

- **Tối Thứ 6:** `logops build` chạy trên dữ liệu thật; tạo được báo cáo DQ EN/VI.
- **Tối Thứ 7:** View KPI + 4 engine khuyến nghị có ước tính tiết kiệm $; đã ghi nhận AUC của mô hình trễ.
- **Tối CN:** dashboard chạy, báo cáo Executive Summary xuất được PDF + HTML, đã tập kịch bản
  demo, mọi thứ đã commit.
