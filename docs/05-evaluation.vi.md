# 05 · Đánh giá: tiết kiệm so với mục tiêu

> Sinh tự động bằng `uv run logops build` từ `src/logops/optimize/`; không sửa tay. · Bản tiếng Anh: [05-evaluation.md](05-evaluation.md) · Spec: [SPEC-optimize.vi.md](../SPEC-optimize.vi.md)

## 1. Kết luận

|  | mỗi năm | của mục tiêu |
|---|---:|---:|
| Mục tiêu (3% chi phí vận hành đo được) | 1,04 tr USD | 100,0% |
| Tiết kiệm đo được | 0,47 tr USD | 44,9% |
| Tiềm năng tối đa (điều chỉnh giá, nếu giữ sản lượng) | 2,42 tr USD | 232,7% |
| Đo được + tiềm năng tối đa | 2,89 tr USD | 277,7% |

Riêng tiết kiệm đo được thì chưa đạt mục tiêu; phần này đến từ việc bỏ các xe không chạy. Các kịch bản giá có thể vượt mục tiêu, nhưng chỉ khi khách hàng chấp nhận. Hai loại được tách riêng có chủ đích.

## 2. Quy mô đội xe

Nhu cầu mỗi ngày đếm số xe hoạt động trong ngày (một chuyến chiếm xe ⌈thời gian ÷ 24 giờ⌉ ngày), giống trên dashboard. Số xe cần = ⌈p99 nhu cầu mỗi ngày × (1 + tỷ lệ chuyến thiếu mã xe) × (1 + tăng trưởng) ÷ hệ số sẵn sàng⌉. Hệ số sẵn sàng = 1 − giờ dừng bảo dưỡng ÷ tổng giờ của các xe đang chạy.

| Tăng trưởng | Nhu cầu thiết kế | Hệ số sẵn sàng | Số xe cần | Đội xe | Đang chạy | Dư |
|---|---:|---:|---:|---:|---:|---:|
| +0% | 76,5 | 97,7% | 79 | 120 | 92 | 41 |
| +5% | 80,3 | 97,7% | 83 | 120 | 92 | 37 |
| +10% | 84,1 | 97,7% | 87 | 120 | 92 | 33 |
| +20% | 91,8 | 97,7% | 94 | 120 | 92 | 26 |

**Đề xuất ở mức tăng trưởng 0%** (xe tốn bảo dưỡng nhất được thanh lý trước):

| Bậc | Số xe | Trạng thái | Đưa lại vận hành | Bảo dưỡng mỗi năm | Loại |
|---|---:|---|---:|---:|---|
| 1 | 13 | Ngừng hoạt động | 0 | 0,22 tr USD | đo được |
| 2 | 15 | Đang bảo dưỡng | 0 | 0,25 tr USD | đo được |
| 3 | 13 | Đang chạy (ít dặm nhất) | 0 | 0,20 tr USD | tiềm năng tối đa |

**Đối chiếu:** ngày bận nhất 80 xe; tháng đông nhất có 92 xe chạy (bảng chỉ số sử dụng xe theo tháng). Ở mức tăng trưởng 0% đội xe cần 79 xe; 8 trên 1096 ngày cần nhiều hơn, có thể thuê xe ngắn hạn.

Tiền bán xe không có trong dữ liệu: là lợi ích thêm chưa định lượng.

## 3. Lợi nhuận tuyến

Cả 58 tuyến đều có lời trên chi phí đo được; biên là trước lương tài xế. Tuyến yếu nhất lỗ nếu chi phí tài xế vượt 0,857 USD/dặm.

| Nhóm | Số tuyến | Doanh thu mỗi năm | Khoảng biên |
|---|---:|---:|---|
| Tăng sản lượng (sản lượng vừa, biên cao) | 6 | 13,49 tr USD | 68,5% – 69,5% |
| Tìm thêm nguồn hàng (sản lượng thấp, biên cao) | 6 | 14,54 tr USD | 68,4% – 72,2% |
| Duy trì (biên vừa) | 11 | 14,71 tr USD | 62,6% – 68,3% |
| Theo dõi (sản lượng thấp, biên vừa) | 8 | 10,78 tr USD | 63,6% – 67,5% |
| Giữ và bảo vệ (sản lượng cao, biên cao) | 7 | 17,72 tr USD | 70,2% – 72,7% |
| Đàm phán lại giá (sản lượng cao, biên thấp) | 6 | 7,63 tr USD | 50,4% – 61,1% |
| Rà soát giá cước (sản lượng thấp, biên thấp) | 6 | 9,44 tr USD | 54,8% – 62,5% |
| Rà soát giá và chi phí (sản lượng vừa, biên thấp) | 8 | 11,31 tr USD | 51,4% – 62,0% |

**Kịch bản** (tiềm năng tối đa; mất khách hòa vốn trung vị = các tuyến điều chỉnh giá có thể mất bao nhiêu sản lượng trước khi thu ít hơn hiện tại):

| Trần tăng cước | S1 phụ phí | S2 cước | Tổng mỗi năm | Mất khách hòa vốn (trung vị) |
|---|---:|---:|---:|---:|
| +5% | 0,96 tr USD | 1,26 tr USD | 2,22 tr USD | 9,6% |
| +10% | 0,96 tr USD | 2,49 tr USD | 3,45 tr USD | 14,7% |
| không giới hạn (lý thuyết) | 0,96 tr USD | 5,66 tr USD | 6,62 tr USD | 25,7% |

**S3 – phụ phí theo chỉ số giá nhiên liệu** (giá cơ sở trung hòa doanh thu 2,318 USD/gallon; không tính là tiết kiệm):

| Năm | Giá trung bình | Phụ phí thực tế | Phụ phí theo chỉ số |
|---|---:|---:|---:|
| 2022 | 4,198 USD | 10,03 tr USD | 11,92 tr USD |
| 2023 | 3,850 USD | 9,94 tr USD | 9,63 tr USD |
| 2024 | 3,650 USD | 10,01 tr USD | 8,43 tr USD |

### Ghép chuyến: điều xe gần nhất (mô phỏng, ước tính)

Mô phỏng lại toàn bộ 85.410 lô theo giờ thực tế với hai cách điều phối: như hiện tại (xe rảnh lâu nhất, ở đâu cũng được) và điều xe gần nhất. Quãng đường lấy từ mạng tuyến (đường ngắn nhất khi hai thành phố không có tuyến trực tiếp), mỗi dặm chạy rỗng 0,605 USD (3,899 USD mỗi gallon ÷ 6,45 dặm mỗi gallon). Số dặm chạy rỗng của mô hình gấp khoảng ba lần mức mà nhiên liệu mua ngoài chuyến cho phép, nên chỉ áp tỷ lệ giảm (−59,5%) lên phần nhiên liệu đó (7,18 tr USD): 4,27 tr USD mỗi năm, là mức tối đa, không cộng vào tổng. Không đặt giới hạn cứng cho quãng chạy rỗng: xe ở các thành phố ít hàng đi phải chạy xa, và mọi giới hạn đến 24 giờ đều cần thêm hàng nghìn xe.

|  | Như hiện tại | Điều xe gần nhất |
|---|---:|---:|
| Chuyến phải điều xe | 89,5% | 41,1% |
| Lần điều xe mỗi năm | 25.436 | 11.690 |
| Dặm chạy rỗng mỗi năm | 34.911.718 | 14.145.598 |
| Dặm mỗi lần điều xe | 1.373 | 1.210 |
| Lần điều xe trong một ngày lái (11 giờ) | 14,3% | 33,4% |
| Số xe cần | 211 | 195 |

## 4. Đã kiểm tra và loại bỏ

| Đòn bẩy | Bằng chứng |
|---|---|
| Giao trễ quá 2 giờ | 44,4% lần giao trễ quá 2 giờ; theo thành phố, khách hàng, giờ hẹn, tuyến, tài xế tương quan giữa hai giai đoạn cao nhất 0,14 (cần 0,7) |
| Mô hình dự báo trễ (ML) | Đúng giờ theo tài xế/khách hàng/tuyến/xe: tương quan 2022-23 với 2024 = 0,01–0,09 |
| Cải thiện MPG theo tài xế/xe | MPG theo tài xế/xe: tương quan qua các năm 0,003 / −0,068; chênh 6,37–6,54 |
| Giảm chạy không tải | Giờ không tải với thời gian, quãng đường, nhiên liệu: tương quan ≈ 0 |
| Đổ nhiên liệu ở nơi rẻ hơn | Giá nhiên liệu trung bình giữa các thành phố chênh 0,02 USD/gallon |
| Lợi nhuận theo khách hàng | Biên theo khách hàng: tương quan qua các năm 0,03 |
| Thay xe cũ | Chi phí bảo dưỡng/dặm: không tăng theo đời xe; tương quan qua các năm 0,12 |
| Điểm nghẽn | Chờ ở xưởng và chờ ở cửa nhận hàng: có tín hiệu, chủ dự án bỏ vì chưa thực tế |
| Ghép hàng, tính phí chờ | Ghép hàng và tính phí chờ: chủ dự án bỏ (hàng gấp không chờ ghép được; tính phí chờ không hợp lý) |
