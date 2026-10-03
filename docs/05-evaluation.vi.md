# 05 · Đánh giá: tiết kiệm so với mục tiêu

> Sinh tự động bằng `uv run logops build` từ `src/logops/optimize/`; không sửa tay. · Bản tiếng Anh: [05-evaluation.md](05-evaluation.md) · Spec: [SPEC-optimize.vi.md](../SPEC-optimize.vi.md)

## 1. Kết luận

|  | mỗi năm | của mục tiêu |
|---|---:|---:|
| Mục tiêu (3% chi phí vận hành đo được) | 1,04 triệu USD | 100,0% |
| Tiết kiệm đo được | 0,47 triệu USD | 44,9% |
| Cận trên (điều chỉnh giá, nếu giữ sản lượng) | 2,65 triệu USD | 254,5% |
| Đo được + cận trên | 3,11 triệu USD | 299,5% |

Riêng tiết kiệm đo được thì chưa đạt mục tiêu; phần này đến từ việc bỏ các xe không chạy. Các kịch bản giá có thể vượt mục tiêu, nhưng chỉ khi khách hàng chấp nhận. Hai loại được tách riêng có chủ đích.

## 2. Quy mô đội xe

Nhu cầu mỗi ngày đếm số xe bận trong ngày (một chuyến chiếm xe ⌈thời gian ÷ 24 giờ⌉ ngày). Số xe cần = ⌈p99 nhu cầu mỗi ngày × (1 + tăng trưởng) ÷ hệ số sẵn sàng⌉. Hệ số sẵn sàng = 1 − giờ dừng bảo dưỡng ÷ tổng giờ của các xe đang chạy.

| Tăng trưởng | Nhu cầu thiết kế | Hệ số sẵn sàng | Số xe cần | Đội xe | Đang chạy | Dư |
|---|---:|---:|---:|---:|---:|---:|
| +0% | 78,0 | 97,7% | 80 | 120 | 92 | 40 |
| +5% | 82,0 | 97,7% | 84 | 120 | 92 | 36 |
| +10% | 85,9 | 97,7% | 88 | 120 | 92 | 32 |
| +20% | 93,7 | 97,7% | 96 | 120 | 92 | 24 |

**Đề xuất ở mức tăng trưởng 0%** (xe tốn bảo dưỡng nhất được thanh lý trước):

| Bậc | Số xe | Trạng thái | Đưa lại vận hành | Bảo dưỡng mỗi năm | Loại |
|---|---:|---|---:|---:|---|
| 1 | 13 | Inactive (ngừng hoạt động) | 0 | 0,22 triệu USD | đo được |
| 2 | 15 | Maintenance (đang sửa) | 0 | 0,25 triệu USD | đo được |
| 3 | 12 | Đang chạy (ít dặm nhất) | 0 | 0,19 triệu USD | cận trên |

**Đối chiếu:** ngày bận nhất 82 xe; tháng đông nhất có 92 xe chạy (`truck_utilization_metrics`). Ở mức tăng trưởng 0% đội xe cần 80 xe; 11 trên 1096 ngày cần nhiều hơn, có thể thuê xe ngắn hạn.

Tiền bán xe không có trong dữ liệu: là lợi ích thêm chưa định lượng.

## 3. Lợi nhuận tuyến

Cả 58 tuyến đều có lời trên chi phí đo được; biên là trước lương tài xế. Tuyến yếu nhất lỗ nếu chi phí tài xế vượt 0,857 USD/dặm.

| Nhóm | Số tuyến | Doanh thu mỗi năm | Khoảng biên |
|---|---:|---:|---|
| Chủ lực (biên cao, sản lượng cao) | 12 | 27,00 triệu USD | 65,8% – 72,7% |
| Ngách có lời (biên cao, sản lượng thấp) | 17 | 34,82 triệu USD | 66,1% – 72,2% |
| Cần tăng giá (biên thấp, sản lượng cao) | 18 | 24,19 triệu USD | 50,4% – 65,0% |
| Xem xét lại (biên thấp, sản lượng thấp) | 11 | 13,60 triệu USD | 54,8% – 65,2% |

**Kịch bản** (cận trên; mất khách hòa vốn trung vị = các tuyến điều chỉnh giá có thể mất bao nhiêu sản lượng trước khi thu ít hơn hiện tại):

| Trần tăng cước | S1 phụ phí | S2 cước | Tổng mỗi năm | Mất khách hòa vốn (trung vị) |
|---|---:|---:|---:|---:|
| +5% | 0,96 triệu USD | 1,50 triệu USD | 2,46 triệu USD | 6,9% |
| +10% | 0,96 triệu USD | 2,81 triệu USD | 3,77 triệu USD | 12,9% |
| không giới hạn (lý thuyết) | 0,96 triệu USD | 5,99 triệu USD | 6,95 triệu USD | 19,9% |

**S3 – phụ phí theo chỉ số giá nhiên liệu** (giá cơ sở trung hòa doanh thu 2,318 USD/gallon; không tính là tiết kiệm):

| Năm | Giá trung bình | Phụ phí thực tế | Phụ phí theo chỉ số |
|---|---:|---:|---:|
| 2022 | 4,198 USD | 10,03 triệu USD | 11,92 triệu USD |
| 2023 | 3,850 USD | 9,94 triệu USD | 9,63 triệu USD |
| 2024 | 3,650 USD | 10,01 triệu USD | 8,43 triệu USD |

## 4. Đã kiểm tra và loại bỏ

| Đòn bẩy | Bằng chứng |
|---|---|
| Mô hình dự báo trễ (ML) | Đúng giờ theo tài xế/khách hàng/tuyến/xe: tương quan 2022-23 với 2024 = 0,01–0,09 |
| Cải thiện MPG theo tài xế/xe | MPG theo tài xế/xe: tương quan qua các năm 0,003 / −0,068; chênh 6,37–6,54 |
| Giảm chạy không tải | Giờ không tải với thời gian, quãng đường, nhiên liệu: tương quan ≈ 0 |
| Đổ nhiên liệu ở nơi rẻ hơn | Giá nhiên liệu trung bình giữa các thành phố chênh 0,02 USD/gallon |
| Lợi nhuận theo khách hàng | Biên theo khách hàng: tương quan qua các năm 0,03 |
| Thay xe cũ | Chi phí bảo dưỡng/dặm: không tăng theo đời xe; tương quan qua các năm 0,12 |
| Điểm nghẽn | Chờ ở xưởng và chờ ở cửa nhận hàng: có tín hiệu, chủ dự án bỏ vì chưa thực tế |
| Ghép hàng, tính phí chờ | Ghép hàng và tính phí chờ: chủ dự án bỏ (hàng gấp không chờ ghép được; tính phí chờ không hợp lý) |
