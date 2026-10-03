# Đánh giá · Module 3: `optimize`

> CRISP-DM pha 4–5 · Bản tiếng Anh: [03-optimize.md](03-optimize.md) · Spec:
> [SPEC-optimize.vi.md](../../SPEC-optimize.vi.md) · Kết quả chi tiết:
> [05-evaluation.vi.md](../05-evaluation.vi.md), [04-data-process-improvements.vi.md](../04-data-process-improvements.vi.md)
> · Tổng kết: [SUMMARY.vi.md](../SUMMARY.vi.md)
> **Trạng thái:** hoàn tất ngày 03/10/2026, chưa commit · **Nguyên tắc:** chỉ ghi điều đã kiểm chứng.

## 1. Phạm vi: từ kế hoạch ban đầu đến bản cuối

Trước khi viết spec, mình kiểm tra tín hiệu của từng đòn bẩy. Tiêu chí: tín hiệu phải **lặp lại** giữa
2022–23 và 2024. Phần lớn đòn bẩy trong kế hoạch ban đầu không đạt.

| Đòn bẩy | Kết quả kiểm tra | Quyết định |
|---|---|---|
| Quy mô đội xe | Ngày bận nhất 82 xe, p99 78; đội có 120 xe | ✅ P1 |
| Lợi nhuận tuyến + phụ phí nhiên liệu | Biên tuyến lặp lại (tương quan 0,946); phụ phí cố định theo tuyến, không theo giá nhiên liệu | ✅ P2 |
| Lỗ hổng dữ liệu → quy trình | Tác động đo được | ✅ P4 |
| Mô hình ML dự báo trễ | Tương quan qua các năm 0,01–0,09 | ❌ Bỏ (tiêu chí AUC trong `docs/01` đã rút lại) |
| MPG theo tài xế/xe | 0,003 / −0,068 | ❌ Bỏ |
| Chạy không tải, giá nhiên liệu theo địa điểm, lợi nhuận theo khách hàng, thay xe cũ | Nhiễu hoặc không lặp lại | ❌ Bỏ |
| Điểm nghẽn (xưởng bảo dưỡng, cửa nhận hàng) | Có tín hiệu | ❌ Chủ dự án bỏ: chưa thực tế |
| Ghép hàng, tính phí chờ | Có tín hiệu | ❌ Chủ dự án bỏ: hàng gấp không chờ ghép; tính phí chờ không hợp lý |

## 2. Output so với spec

| Output | Đã giao | Bằng chứng |
|---|---|---|
| P1 `fleet_plan`, `disposal_tiers`, `cross_check` | ✅ Kịch bản 0/5/10/20%; thanh lý theo bậc; thiếu xe thì lấy lại xe `Maintenance` trước | 7 test trên dữ liệu mẫu; test tích hợp: không kịch bản nào làm đội xe thiếu xe |
| P2 `lane_pricing` (`classify`, `scenarios`, `indexed_surcharge`) | ✅ 4 nhóm tuyến, chi phí tài xế hòa vốn, S1/S2 với trần 5/10%/không giới hạn, S3 mô phỏng | 7 test trên dữ liệu mẫu; khớp tổng với KPI đội xe |
| P4 lỗ hổng dữ liệu | ✅ 6 lỗ hổng, chi phí khi không làm (đo được) so với chi phí khi làm (có nguồn trích dẫn) | 4 test; test tích hợp kiểm tra có nguồn |
| P5 khuyến nghị + tài liệu | ✅ Bảng `recommendations` trong kho; lệnh `logops optimize`; `docs/04`, `docs/05` tự sinh EN/VI | Test tích hợp: tổng tiết kiệm = tổng các bậc đo được |
| Cập nhật tài liệu | ✅ `CAPABILITY-MAP`, `00-analytical-approach` §5–§7, `docs/01` §5 | — |

**Test:** 23 test mới; tổng 99 test qua; `ruff` sạch. Build 8,3–8,4 giây.

## 3. Kết quả

**So với mục tiêu 1,04 triệu USD/năm** (3% chi phí vận hành đo được):

| Loại | Mỗi năm | % mục tiêu |
|---|---:|---:|
| **Tiết kiệm đo được** (bảo dưỡng của 28 xe không chạy) | 466.949 USD | 45% |
| Cận trên: phụ phí S1 + cước S2 (trần 5%) + xem lại 12 xe ít dặm nhất | 2.646.153 USD | 255% |

**P1 – đội xe:** cần 80 / 84 / 88 / 96 xe ở mức tăng trưởng 0 / 5 / 10 / 20%, so với 120 xe sở hữu
và 92 xe đang chạy. Thanh lý 13 xe `Inactive` (219.927 USD/năm) và 15 xe `Maintenance` (247.022
USD/năm). Ở +20%, đưa 4 xe `Maintenance` trở lại vận hành. Hệ số sẵn sàng 97,7%.

**P2 – tuyến:**

| Nhóm | Số tuyến | Khoảng biên |
|---|---:|---|
| Chủ lực (biên cao, sản lượng cao) | 12 | 65,8–72,7% |
| Ngách có lời (biên cao, sản lượng thấp) | 17 | 66,1–72,2% |
| Cần tăng giá (biên thấp, sản lượng cao) | 18 | 50,4–65,0% |
| Xem xét lại (biên thấp, sản lượng thấp) | 11 | 54,8–65,2% |

- Không tuyến nào lỗ trên chi phí đo được. Tuyến yếu nhất lỗ nếu chi phí tài xế vượt **0,857 USD/dặm**.
- S1 chuẩn hóa phụ phí: +0,96 triệu USD/năm (29 tuyến).
- S2 với trần 5% / 10% / không giới hạn: +1,50 / +2,81 / +5,99 triệu USD/năm.
- Mất khách hòa vốn (trung vị): 6,9% / 12,9% / 19,9%.
- S3, phụ phí theo chỉ số giá (trung hòa doanh thu, giá cơ sở 2,318 USD/gallon): thu nhiều hơn khi giá
  cao (2022: +1,89 triệu USD), ít hơn khi giá thấp (2024: −1,58 triệu USD). Không tính là tiết kiệm.

**P4 – dữ liệu:**
- 5,57 triệu gallon mua chưa đối soát với tiêu thụ: 7,24 triệu USD/năm *chưa giải thích được*, không
  phải thất thoát đã chứng minh.
- Chuẩn ngành về lạm dụng thẻ (2–5% chi phí nhiên liệu): 0,64–1,59 triệu USD/năm.
- Telematics cho 92 xe: 25.147–65.013 USD/năm. Hoàn vốn nếu ngăn được **0,2%** chi phí nhiên liệu.

## 4. Phát hiện và lưu ý

- **"Ngách có lời" có doanh thu lớn hơn "Chủ lực"** (104,4 so với 80,9 triệu USD trong 3 năm). Lý do:
  sản lượng được đo bằng số chuyến, và các tuyến ngách là tuyến dài, doanh thu mỗi chuyến cao.
- **Ngày bận nhất (82 xe) vượt số xe cần ở p99 (80).** Có 11/1.096 ngày (khoảng 4 ngày mỗi năm)
  cần nhiều hơn 80 xe, có thể thuê xe ngắn hạn. Nếu muốn không bao giờ thiếu xe thì cần 84 xe.
- **S2 không giới hạn là con số lý thuyết:** có tuyến cần tăng cước tới 44%. Vì vậy con số chính dùng
  trần 5%.
- **Biên là trước lương tài xế.** Nếu lương trả theo dặm, các tuyến cuối bảng chỉ có thể tệ hơn, nên
  kết luận "cần tăng giá" không đổi.

## 5. Giới hạn, và điều không làm

| Hạng mục | Lý do |
|---|---|
| Tiền bán xe, bảo hiểm, chỗ đỗ của xe thanh lý | Không có trong dữ liệu; ghi là lợi ích chưa định lượng |
| Độ co giãn của cầu khi tăng giá | Không có; thay bằng "mất khách hòa vốn" |
| Chi phí thực hiện mức 1 (quy trình, cấu hình) | Là công sức nội bộ trên hệ thống sẵn có; không gán giá |
| Giá telematics | Số liệu công khai tham khảo (GPS Insight), cần báo giá thực tế |

## 6. Chuyển sang module sau

`insights`, `dashboard` và `reports` đọc bảng `recommendations` cùng các hàm trong `src/logops/optimize/`.
Dashboard cần: thanh chọn tăng trưởng (P1), thanh chọn trần tăng cước (P2), và phân biệt rõ *đo được*,
*cận trên* và *chưa giải thích được*.

## 7. Tái lập

```powershell
python -m uv run logops build                  # tạo bảng recommendations + docs/04, docs/05
python -m uv run logops optimize --growth 10   # khuyến nghị ở kịch bản +10%
python -m uv run pytest tests/optimize         # 23 test của module này
```
