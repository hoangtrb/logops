# Đánh giá · Module 5: `optimize`

> CRISP-DM pha 4–5 (Mô hình hóa, Đánh giá) · Bản tiếng Anh: [05-optimize.md](05-optimize.md) · Spec:
> [SPEC-optimize.vi.md](../../SPEC-optimize.vi.md) · Kết quả: [05-evaluation.vi.md](../05-evaluation.vi.md),
> [04-data-process-improvements.vi.md](../04-data-process-improvements.vi.md) · Tổng quan: [SUMMARY.vi.md](../SUMMARY.vi.md)
> **Trạng thái:** xong 04/10/2026, chưa commit · **Quy tắc:** chỉ ghi sự thật đã kiểm chứng.

## 1. Bối cảnh

Làm lại từ nhánh `feature/optimize` sau module phân tích và dashboard. Phạm vi đã thống nhất với chủ
dự án: O1 đội xe, O2 giá cước tuyến, O4 giao trễ, O5 quy trình dữ liệu, O6 khuyến nghị và trang
dashboard; O3 ghép chuyến chỉ làm nếu còn thời gian (đã làm 04/10/2026, chủ dự án bỏ 05/10/2026). Mục tiêu 3,1 tr USD/3 năm được phép
vượt.

## 2. Output so với spec

| Output | Kết quả | Bằng chứng |
|---|---|---|
| O1 quy mô đội xe và thanh lý theo bậc | ✅ Nhu cầu mỗi ngày lấy từ số xe hoạt động của lớp phân tích, cộng phần bù chuyến thiếu mã xe (2,0%) | Test: nhu cầu mỗi ngày bằng số trên dashboard; số xe cần tăng theo tăng trưởng; thanh lý không làm thiếu xe |
| O2 giá cước tuyến S1/S2/S3 | ✅ Nhóm tuyến lấy từ ma trận 3×3 của dashboard; S2 áp cho nhóm biên thấp nhất (20 tuyến) | Doanh thu và lợi nhuận các tuyến khớp KPI toàn đội; nhóm trùng hướng xử lý của ma trận tuyến |
| O4 giao trễ | ✅ Không có nguyên nhân lặp lại: tương quan giữa hai giai đoạn từ −0,23 đến 0,14 (cần 0,7) theo thành phố, khách hàng, giờ hẹn, tuyến, tài xế | Test trên dữ liệu thật |
| O5 cải tiến quy trình dữ liệu | ✅ 7 lỗ hổng; mới: chuyến điều xe giữa hai chuyến không được ghi | Mọi chi phí thiết bị có nguồn |
| O6 khuyến nghị, tài liệu, trang | ✅ Bảng `recommendations`, lệnh `logops optimize`, `docs/04`, `docs/05`, trang dashboard "Khuyến nghị tối ưu" (VI/EN), một trang đặt trước trang dữ liệu (04/10/2026) | Trang chạy ở cả hai ngôn ngữ, tải lại dưới 3 giây |
| O3 ghép chuyến | ❌ Đã làm, rồi chủ dự án bỏ (05/10/2026) | Kết quả phụ thuộc quá nhiều vào giả định mà dữ liệu không trả lời được: xe thùng khô và xe lạnh, xe chuyên trách (50% số lô: dặm chạy rỗng giảm 59,5% → 35,2%), quãng đường theo mạng tuyến dài hơn đường thật, và số dặm rỗng mô phỏng gấp khoảng ba lần mức nhiên liệu mua ngoài chuyến cho phép. Dễ bị chất vấn nên không trình bày |

**Test:** 26 trong `tests/optimize` + 2 lượt chạy trang; tổng 148, tất cả pass; `ruff` sạch.

## 3. Kết quả (mỗi năm, dữ liệu 2022–2024)

| Loại | Số tiền | So với mục tiêu (1,04 tr USD) |
|---|---:|---:|
| **Tiết kiệm đo được:** thanh lý 13 xe ngừng hoạt động + 15 xe đang bảo dưỡng chưa từng chạy | 0,47 tr USD | 45% |
| **Mức trần:** rà soát 13 xe ít dặm nhất (0,20 tr USD), phụ phí về trung vị (0,96 tr USD), tăng cước tuyến biên thấp tối đa +5% (1,26 tr USD) | 2,42 tr USD | 233% |
| **Tổng tiềm năng** | 2,89 tr USD | 278% |
| Chưa giải thích được, không cộng: nhiên liệu mua nhưng không ghi nhận tiêu thụ | 7,24 tr USD | — |

- **Đội xe:** cần 79 / 83 / 87 / 94 xe ở mức tăng trưởng 0 / 5 / 10 / 20%, so với 120 xe sở hữu và 92
  xe từng chạy; tỷ lệ sẵn sàng 97,7%; 8 trên 1.096 ngày cần hơn 79 xe (thuê ngắn hạn).
- **Tuyến:** mọi tuyến có lãi trên chi phí đo được; tuyến yếu nhất chỉ lỗ khi chi phí tài xế vượt
  0,857 USD/dặm. Trần +10%: S1 + S2 = 3,45 tr USD/năm; không giới hạn (lý thuyết) 6,62 tr USD. Sụt
  sản lượng hòa vốn trung vị 9,6% ở mức +5%.
- **Phụ phí theo giá nhiên liệu (S3):** giá cơ sở trung hòa doanh thu 2,318 USD/gallon; trình bày là
  chia sẻ rủi ro, không tính là tiết kiệm.
- **Giao trễ:** 44,4% lần giao trễ quá 2 giờ nhưng không có nguyên nhân lặp lại trong dữ liệu: không
  đề xuất, thay vào đó đề xuất ghi mã lý do (O5).

## 4. Lưu ý khi trình bày


- Riêng tiết kiệm đo được đạt 45% mục tiêu; vượt mục tiêu chỉ khi có các đòn bẩy giá, cần khách hàng
  chấp nhận.
- Biên là trước lương tài xế và chi phí chung.
- Giá telematics là số tham khảo công khai.

## 5. Chạy lại

```powershell
python -m uv run logops build          # bảng khuyến nghị + docs/04, docs/05
python -m uv run logops optimize       # khuyến nghị so với mục tiêu
python -m uv run pytest tests/optimize -m "slow or not slow"
```
