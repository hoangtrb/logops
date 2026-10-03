# 03 · Phân tích và nhận xét

> CRISP-DM pha 2–3 (mô tả và chẩn đoán). Sinh tự động bằng `uv run logops build` từ `src/logops/analysis/`; không sửa tay. · Bản tiếng Anh: [03-analysis-insights.md](03-analysis-insights.md) · Spec: [SPEC-analysis.vi.md](../SPEC-analysis.vi.md)

Giai đoạn: 2022-01-01 đến 2024-12-31. Lợi nhuận là đóng góp trước lương tài xế và chi phí chung (không có trong dữ liệu). Chi phí ghi theo ngày phát sinh.

## 1. Nhận xét (sinh tự động từ số liệu theo quy tắc)

| Mức độ | Nhận xét |
|---|---|
| cần hành động | Biên tăng từ 62,7% lên 67,2% (2022 → 2024) trong khi doanh thu/dặm gần như không đổi (2,444 USD → 2,447 USD). Giá nhiên liệu giảm đóng góp 4,12 triệu USD trong mức tăng 4,42 triệu USD của đóng góp (93,2%). Nếu giá nhiên liệu tăng lại, biên sẽ giảm. |
| cần theo dõi | Biên hằng tháng đi ngược giá nhiên liệu (tương quan -0,92): biên phụ thuộc giá nhiên liệu vì phụ phí nhiên liệu là cố định. |
| thông tin | Sản lượng gần như không đổi: 28.589 chuyến năm 2022, 28.656 chuyến năm 2024 (0,2%). |
| thông tin | Các phân khúc khách hàng có biên gần như bằng nhau (65,5% đến 65,8%): khác biệt lợi nhuận đến từ tuyến, không đến từ loại hợp đồng. |
| thông tin | TX đóng góp nhiều nhất (23,33 triệu USD, 11,9% tổng đóng góp); biên theo bang đi từ 56,5% đến 69,9%. |
| thông tin | Tập trung khách hàng: khách lớn nhất 0,6% doanh thu, mười khách lớn nhất 5,7%, cần 157 trên 200 khách để đạt tám mươi phần trăm doanh thu; HHI 50 (mức vừa từ 1.000, cao từ 1.800). |
| cần theo dõi | Năm nào lượng nhiên liệu mua cũng nhiều hơn lượng ghi nhận tiêu thụ trên chuyến (1,28 đến 1,30 lần). Chênh lệch này chưa được đối soát. |
| cần theo dõi | Số xe bận mỗi ngày: 95% số ngày cần tối đa 73 xe, 99% số ngày cần tối đa 75 xe, ngày bận nhất cần 80 xe. Đội có 92 xe đang chạy và 120 xe sở hữu. |
| thông tin | Không dự báo được ngày cao điểm: ngày này gần như không báo trước ngày sau (tương quan 0,18), không có quý nào bận hơn lặp lại qua các năm (0,04), và trung bình năm không đổi (66,0 đến 66,2 xe). Nên lập kế hoạch năng lực theo mức đảm bảo, không theo lịch. |
| thông tin | Danh mục tuyến (3×3 theo sản lượng và biên): 7 tuyến cần bảo vệ (sản lượng và biên cao), 6 tuyến nên xem lại giá (sản lượng cao, biên thấp), 6 tuyến cân nhắc rút lui (sản lượng và biên thấp). |
| cần hành động | 33,0% số lô (28.178) kết thúc ở thành phố không có hàng về tương ứng; 16 trên 20 thành phố lệch quá 20%, và mức lệch ổn định qua các năm (tương quan 0,997). Indianapolis, Los Angeles chỉ nhận hàng, không gửi lô nào. |
| cần theo dõi | Ở 95,4% số lần chuyển, chuyến tiếp theo của xe bắt đầu ở thành phố khác nơi chuyến trước kết thúc. Quãng di chuyển giữa hai chuyến không được ghi trong dữ liệu. |

## 2. Lãi lỗ theo năm

| Kỳ | Số chuyến | Doanh thu | Nhiên liệu | Bảo dưỡng | Bồi thường | Đóng góp | Biên | So kỳ trước | So cùng kỳ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 28.589 | 99,92 triệu USD | 34,35 triệu USD | 1,93 triệu USD | 1,02 triệu USD | 62,62 triệu USD | 62,7% | — | — |
| 2023 | 28.165 | 98,91 triệu USD | 31,07 triệu USD | 1,97 triệu USD | 0,79 triệu USD | 65,07 triệu USD | 65,8% | 3,9% | 3,9% |
| 2024 | 28.656 | 99,79 triệu USD | 30,08 triệu USD | 1,82 triệu USD | 0,84 triệu USD | 67,05 triệu USD | 67,2% | 3,0% | 3,0% |

## 3. Lãi lỗ theo quý

| Quý | Doanh thu | Đóng góp | Biên | So kỳ trước | So cùng kỳ | Lũy kế năm | Lũy kế năm trước |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2022-Q1 | 24,51 triệu USD | 15,62 triệu USD | 63,7% | — | — | 15,62 triệu USD | — |
| 2022-Q2 | 25,00 triệu USD | 15,58 triệu USD | 62,3% | -0,2% | — | 31,20 triệu USD | — |
| 2022-Q3 | 25,28 triệu USD | 15,64 triệu USD | 61,8% | 0,3% | — | 46,84 triệu USD | — |
| 2022-Q4 | 25,13 triệu USD | 15,79 triệu USD | 62,8% | 1,0% | — | 62,62 triệu USD | — |
| 2023-Q1 | 24,52 triệu USD | 16,14 triệu USD | 65,8% | 2,2% | 3,3% | 16,14 triệu USD | 15,62 triệu USD |
| 2023-Q2 | 24,80 triệu USD | 16,37 triệu USD | 66,0% | 1,4% | 5,0% | 32,50 triệu USD | 31,20 triệu USD |
| 2023-Q3 | 24,79 triệu USD | 16,25 triệu USD | 65,5% | -0,7% | 3,9% | 48,75 triệu USD | 46,84 triệu USD |
| 2023-Q4 | 24,79 triệu USD | 16,32 triệu USD | 65,8% | 0,4% | 3,4% | 65,07 triệu USD | 62,62 triệu USD |
| 2024-Q1 | 24,82 triệu USD | 16,79 triệu USD | 67,6% | 2,9% | 4,0% | 16,79 triệu USD | 16,14 triệu USD |
| 2024-Q2 | 25,22 triệu USD | 16,84 triệu USD | 66,8% | 0,3% | 2,9% | 33,63 triệu USD | 32,50 triệu USD |
| 2024-Q3 | 24,81 triệu USD | 16,63 triệu USD | 67,0% | -1,3% | 2,4% | 50,27 triệu USD | 48,75 triệu USD |
| 2024-Q4 | 24,94 triệu USD | 16,78 triệu USD | 67,3% | 0,9% | 2,8% | 67,05 triệu USD | 65,07 triệu USD |

## 4. Cầu lợi nhuận 2022 → 2024

|  |  |
|---|---:|
| Đóng góp 2022 | 62,62 triệu USD |
| Sản lượng | +0,15 triệu USD |
| Giá mỗi chuyến | -0,37 triệu USD |
| Giá nhiên liệu | +4,12 triệu USD |
| Nhiên liệu mỗi chuyến | +0,22 triệu USD |
| Bảo dưỡng | +0,11 triệu USD |
| Bồi thường | +0,18 triệu USD |
| Đóng góp 2024 | 67,05 triệu USD |

## 5. Đơn vị kinh tế

| Năm | Doanh thu/dặm | Chi phí/dặm | Đóng góp/dặm | Doanh thu/chuyến | Đóng góp/chuyến | Đóng góp/xe-tuần |
|---|---:|---:|---:|---:|---:|---:|
| 2022 | 2,444 USD | 0,912 USD | 1,532 USD | 3.495 USD | 2.190 USD | 12.931 USD |
| 2023 | 2,442 USD | 0,836 USD | 1,607 USD | 3.512 USD | 2.310 USD | 13.508 USD |
| 2024 | 2,447 USD | 0,803 USD | 1,644 USD | 3.482 USD | 2.340 USD | 13.835 USD |

## 6. Theo chiều kinh doanh

**Phân khúc khách hàng**

| Nhóm | Doanh thu | Đóng góp | Biên | Tỷ trọng đóng góp |
|---|---:|---:|---:|---:|
| Contract | 112,40 triệu USD | 73,64 triệu USD | 65,5% | 37,5% |
| Spot | 94,22 triệu USD | 61,97 triệu USD | 65,8% | 31,6% |
| Dedicated | 92,00 triệu USD | 60,53 triệu USD | 65,8% | 30,9% |

**Loại hàng**

| Nhóm | Doanh thu | Đóng góp | Biên | Tỷ trọng đóng góp |
|---|---:|---:|---:|---:|
| Refrigerated | 150,13 triệu USD | 98,51 triệu USD | 65,6% | 50,2% |
| Dry Van | 148,50 triệu USD | 97,63 triệu USD | 65,7% | 49,8% |

**Bang đi (8 bang đóng góp nhiều nhất)**

| Nhóm | Doanh thu | Đóng góp | Biên | Tỷ trọng đóng góp |
|---|---:|---:|---:|---:|
| TX | 35,23 triệu USD | 23,33 triệu USD | 66,2% | 11,9% |
| OH | 28,58 triệu USD | 19,96 triệu USD | 69,9% | 10,2% |
| NC | 27,60 triệu USD | 18,43 triệu USD | 66,8% | 9,4% |
| WA | 26,94 triệu USD | 18,06 triệu USD | 67,0% | 9,2% |
| MO | 26,40 triệu USD | 17,62 triệu USD | 66,7% | 9,0% |
| IL | 24,18 triệu USD | 16,00 triệu USD | 66,2% | 8,2% |
| FL | 23,85 triệu USD | 14,53 triệu USD | 60,9% | 7,4% |
| PA | 17,46 triệu USD | 11,51 triệu USD | 65,9% | 5,9% |

**Tập trung khách hàng:** khách lớn nhất 0,6%, 10 khách lớn nhất 5,7%, 20 khách lớn nhất 11,2%; 157 trên 200 khách chiếm 80% doanh thu; HHI 50.

## 7. Nhiên liệu (thống kê)

| Năm | Gallon mua | Chi tiêu | Giá trung bình | Gallon tiêu thụ trên chuyến | Mua ÷ tiêu thụ |
|---|---:|---:|---:|---:|---:|
| 2022 | 8.181.816 | 34,35 triệu USD | 4,198 USD | 6.344.699 | 1,29 |
| 2023 | 8.070.497 | 31,07 triệu USD | 3,850 USD | 6.283.230 | 1,28 |
| 2024 | 8.241.247 | 30,08 triệu USD | 3,650 USD | 6.318.352 | 1,30 |

Tương quan giữa biên hằng tháng và giá nhiên liệu hằng tháng: -0,92.

## 8. Năng lực đội xe

| Năm | Xe bận trung bình mỗi ngày | Phân vị 95 | Ngày bận nhất |
|---|---:|---:|---:|
| 2022 | 66,1 | 73 | 77 |
| 2023 | 66,0 | 73 | 80 |
| 2024 | 66,2 | 73 | 79 |

Cả giai đoạn: 95% số ngày ≤ 73 xe, 99% ≤ 75 xe, ngày bận nhất 80 xe. 92 xe đang chạy, 120 xe sở hữu. Tương quan giữa hai ngày liền nhau 0,18; mẫu hình theo quý qua các năm 0,04.

## 9. Ma trận tuyến (3×3, số tuyến)

| Sản lượng ↓ / Biên → | Thấp | Vừa | Cao |
|---|---|---|---|
| Cao | 6 (điều chỉnh giá) | 6 (duy trì) | 7 (bảo vệ) |
| Vừa | 8 (xem lại giá) | 5 (duy trì) | 6 (mở rộng) |
| Thấp | 6 (cân nhắc rút lui) | 8 (theo dõi) | 6 (cơ hội tăng trưởng) |

## 10. Cân bằng hàng đi / hàng về (các thành phố lệch nhất)

| Thành phố | Lô đi | Lô đến | Chênh lệch | Mức lệch |
|---|---:|---:|---:|---:|
| Phoenix | 4.456 | 0 | 4.456 | 200,0% |
| Los Angeles | 0 | 8.948 | -8.948 | 200,0% |
| Indianapolis | 0 | 5.810 | -5.810 | 200,0% |
| Chicago | 5.894 | 1.456 | 4.438 | 120,8% |
| Las Vegas | 5.865 | 1.479 | 4.386 | 119,4% |
| Denver | 1.505 | 5.863 | -4.358 | 118,3% |
| Columbus | 7.620 | 2.973 | 4.647 | 87,7% |
| Miami | 5.785 | 2.924 | 2.861 | 65,7% |

## 11. Xe bắt đầu chuyến ở nơi khác điểm kết thúc chuyến trước

| Năm | Số lần chuyển | Bắt đầu ở nơi khác | Tỷ lệ |
|---|---:|---:|---:|
| 2022 | 27.933 | 26.699 | 95,6% |
| 2023 | 27.645 | 26.406 | 95,5% |
| 2024 | 28.068 | 26.735 | 95,3% |

## 12. Đối chiếu với notebook của tác giả bộ dữ liệu

| Phân tích | Notebook | Vấn đề | Ở đây |
|---|---|---|---|
| Ma trận tuyến | Nhiên liệu cố định $3,80/gallon; doanh thu không gồm phụ phí; trung bình biên từng lô | Giá giả định; doanh thu thiếu; trung bình của tỷ lệ | Chi tiêu nhiên liệu thật, doanh thu đầy đủ, tổng ÷ tổng; giá trung bình 3,899 USD |
| Hàng đi/hàng về | Chi phí điều xe = \|tổng chênh lệch\| × 400 dặm × $0,85 | Tổng chênh lệch của mọi thành phố luôn bằng 0, nên chi phí luôn là $0; số dặm và đơn giá là giả định | Đo phần dư chiều đến theo từng thành phố: 28.178 lô |
| Tập trung khách hàng | Thị phần top 10/20, ngưỡng rủi ro 10% | Không có | Giữ nguyên, thêm HHI 50 |
| Mùa vụ | Đếm số lô theo tháng, so đỉnh và đáy | Tháng dài 28–31 ngày nên tháng dài luôn trông bận hơn | Tính theo ngày: không có mẫu hình lặp lại |
| Dặm chạy rỗng | Giả định 15% dặm rỗng, $0,85/dặm | Cả hai con số đều giả định | Đếm từ chuỗi chuyến: 95,4% số lần chuyển; không tính dặm (4 thành phố trên tuyến không có tọa độ) |

## 13. Ngưỡng của các quy tắc

| Ngưỡng | Giá trị | Lý do | Nguồn |
|---|---:|---|---|
| persistent_corr | 0,7 | Một mẫu hình được coi là có thật nếu tương quan giữa 2022–23 và 2024 đạt mức này; quy tắc dùng xuyên suốt dự án | dự án |
| flat_change_pct | 2,0 | Thay đổi dưới ±2% được coi là không đổi; cùng dung sai với kiểm tra chéo chất lượng dữ liệu | dự án |
| driver_share | 0,5 | Một yếu tố được coi là nguyên nhân chính khi giải thích ít nhất một nửa mức thay đổi | dự án |
| segment_spread_pts | 1,0 | Các biên chênh nhau dưới một điểm phần trăm được coi là bằng nhau | dự án |
| hhi_moderate | 1.000,0 | HHI 1.000–1.800 = tập trung vừa (ở đây áp dụng tương tự cho danh mục khách hàng) | [US DOJ/FTC Merger Guidelines 2023](https://www.ftc.gov/system/files/ftc_gov/pdf/2023_merger_guidelines_final_12.18.2023.pdf) |
| hhi_high | 1.800,0 | HHI trên 1.800 = tập trung cao | [US DOJ/FTC Merger Guidelines 2023](https://www.ftc.gov/system/files/ftc_gov/pdf/2023_merger_guidelines_final_12.18.2023.pdf) |
| customer_share_risk_pct | 10,0 | Một khách hàng chiếm trên 10% doanh thu là rủi ro tập trung | [Dataset author's notebook (Route_optimization)](https://www.kaggle.com/code/yogape/route-optimization) |
| city_imbalance_pct | 20,0 | Thành phố có lô đi và lô đến chênh nhau quá 20% là mất cân bằng | [Dataset author's notebook (Route_optimization)](https://www.kaggle.com/code/yogape/route-optimization) |
| surplus_act_pct | 20,0 | Cần hành động khi trên 20% số lô kết thúc ở nơi không có hàng về; cùng mức với ngưỡng theo thành phố | dự án |
| predictable_autocorr | 0,5 | Dưới 0,5, một ngày giải thích dưới 25% biến động của ngày sau: quá yếu để lập kế hoạch | dự án |
| moved_watch_pct | 50,0 | Cần theo dõi khi phần lớn (trên một nửa) số lần chuyển phải di chuyển giữa các thành phố | dự án |
| fuel_gap_pct | 5,0 | Chênh lệch mua so với tiêu thụ trên 5% đáng để đối soát | dự án |
