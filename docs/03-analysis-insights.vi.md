# 03 · Phân tích và nhận xét

> CRISP-DM pha 2–3 (mô tả và chẩn đoán). Sinh tự động bằng `uv run logops build` từ `src/logops/analysis/`; không sửa tay. · Bản tiếng Anh: [03-analysis-insights.md](03-analysis-insights.md) · Spec: [SPEC-analysis.vi.md](../SPEC-analysis.vi.md)

Giai đoạn: 2022-01-01 đến 2024-12-31. Lợi nhuận là đóng góp trước lương tài xế và chi phí chung (không có trong dữ liệu). Chi phí ghi theo ngày phát sinh.

## 1. Nhận xét (sinh tự động từ số liệu theo quy tắc)

### Ưu tiên xử lý

**Lợi nhuận tăng nhờ nhiên liệu rẻ đi, không nhờ vận hành tốt hơn** · Rủi ro · Lợi nhuận

- **Diễn biến:** Biên đóng góp tăng từ 62,7% lên 67,2% (2022 → 2024) trong khi doanh thu mỗi dặm gần như không đổi (2,444 USD → 2,447 USD).
- **Ảnh hưởng:** Giá nhiên liệu giảm mang lại 4,12 tr USD trong 4,42 tr USD lợi nhuận đóng góp tăng thêm (93,2%). Đây là yếu tố công ty không kiểm soát được: nếu giá nhiên liệu quay về mức năm 2022, lợi nhuận đóng góp giảm khoảng 4,12 tr USD mỗi năm.
- **Đề xuất:** Gắn phụ phí nhiên liệu với giá nhiên liệu thực tế (phụ phí thả nổi theo chỉ số giá) thay vì mức cố định; tìm nguồn tăng lợi nhuận công ty chủ động được: giá cước, cơ cấu tuyến, năng suất xe.

**33,0% số lô kết thúc ở nơi không có hàng chiều về** · Tiêu cực · Mạng lưới

- **Diễn biến:** 28.178 lô kết thúc ở các thành phố nhận hàng nhiều hơn gửi đi; 16 trên 20 thành phố lệch quá 20%. Indianapolis, Los Angeles chỉ nhận hàng, không gửi lô nào. Tình trạng này lặp lại qua các năm (tương quan 0,997).
- **Ảnh hưởng:** Sau khi giao những lô này, xe không có hàng chở về và phải chạy rỗng đến điểm lấy hàng kế tiếp: tốn nhiên liệu, giờ tài xế và hao mòn xe mà không có doanh thu. Dữ liệu không ghi quãng chạy rỗng nên chưa quy được ra tiền.
- **Đề xuất:** Tìm nguồn hàng chiều về tại các thành phố nhận nhiều hơn gửi, bắt đầu từ Indianapolis, Los Angeles: tiếp cận chủ hàng tại đó, hoặc giảm giá cước chiều về để lấp đầy xe.

### Cần theo dõi

**Biên lợi nhuận lên xuống theo giá nhiên liệu** · Rủi ro · Lợi nhuận

- **Diễn biến:** Theo từng tháng, nhiên liệu rẻ đi thì biên tăng, đắt lên thì biên giảm (tương quan -0,92, gần như ngược chiều hoàn toàn).
- **Ảnh hưởng:** Phụ phí nhiên liệu thu của khách không đổi theo giá nhiên liệu, nên mọi biến động chi phí nhiên liệu đi thẳng vào lợi nhuận.
- **Đề xuất:** Theo dõi biên cùng giá nhiên liệu hằng tháng và xem lại điều khoản phụ phí nhiên liệu trong hợp đồng với khách.

**Đội xe lớn hơn nhu cầu thực tế** · Tiêu cực · Đội xe

- **Diễn biến:** 95% số ngày chỉ cần tối đa 73 xe chạy cùng lúc, 99% số ngày tối đa 75 xe, ngày bận nhất cần 80 xe. 92 xe từng chạy chuyến; công ty sở hữu 120 xe.
- **Ảnh hưởng:** 40 xe không cần đến kể cả vào ngày bận nhất nhưng vẫn phát sinh chi phí: 28 xe chưa chạy chuyến nào mà vẫn tốn 1,40 tr USD bảo dưỡng.
- **Đề xuất:** Rà soát số xe vượt nhu cầu, bắt đầu từ 28 xe chưa từng chạy: thanh lý, điều chuyển hoặc dừng bảo dưỡng định kỳ; vẫn giữ đủ xe cho 99% số ngày.

**Nhiên liệu mua vào nhiều hơn lượng ghi nhận dùng cho chuyến** · Tiêu cực · Nhiên liệu

- **Diễn biến:** Năm nào lượng nhiên liệu mua cũng bằng 1,28 đến 1,30 lần lượng ghi nhận tiêu thụ trên các chuyến.
- **Ảnh hưởng:** Chưa xác định được phần chênh lệch đi đâu, dùng hợp lý ngoài chuyến hay thất thoát: khi chưa đối soát thẻ nhiên liệu với chuyến thì không phân biệt được hai trường hợp này.
- **Đề xuất:** Đối soát giao dịch thẻ nhiên liệu với chuyến theo từng xe, từng tháng; ghi số đồng hồ quãng đường mỗi lần đổ nhiên liệu.

**Chuyến kế tiếp không được ghép với nơi xe vừa giao xong** · Tiêu cực · Mạng lưới

- **Diễn biến:** Ở 95,4% số trường hợp, chuyến kế tiếp của xe bắt đầu ở thành phố khác nơi chuyến trước kết thúc. Nếu giao chuyến hoàn toàn ngẫu nhiên, tỷ lệ này là 95,4%: dữ liệu không cho thấy việc điều phối ghép hàng theo vị trí xe.
- **Ảnh hưởng:** Gần như mọi chuyến đều phải điều xe sang thành phố khác trước, thường là chạy rỗng. Quãng di chuyển này không được ghi lại, nên thời gian và nhiên liệu bị ẩn khỏi báo cáo chi phí và lợi nhuận từng chuyến.
- **Đề xuất:** Ghi nhận mọi lần điều xe giữa hai chuyến (thời gian, quãng đường, lý do), và giao lô kế tiếp cho xe đang ở hoặc gần điểm lấy hàng; số lần điều xe tiết kiệm được sẽ tính ở module tối ưu.

### Tham khảo

**Không phụ thuộc vào khách hàng nào** · Tích cực · Lợi nhuận

- **Diễn biến:** Khách lớn nhất chiếm 0,6% doanh thu, mười khách lớn nhất 5,7%, cần 157 trên 200 khách mới đạt tám mươi phần trăm doanh thu (HHI 50).
- **Ý nghĩa:** Mất một khách bất kỳ chỉ ảnh hưởng tối đa 0,6% doanh thu. HHI dưới 1.000, mức bắt đầu đáng lo về tập trung.

**Sản lượng đi ngang** · Trung tính · Lợi nhuận

- **Diễn biến:** 28.589 chuyến năm 2022, 28.656 chuyến năm 2024 (0,2%).
- **Ý nghĩa:** Lợi nhuận tăng không đến từ tăng sản lượng. Nhu cầu xe ổn định nên có thể lập kế hoạch năng lực theo mức hiện tại.

**Các phân khúc khách hàng có biên như nhau** · Trung tính · Lợi nhuận

- **Diễn biến:** Mọi phân khúc khách hàng đều có biên từ 65,5% đến 65,8%.
- **Ý nghĩa:** Muốn cải thiện lợi nhuận nên xét theo tuyến và giá cước, không theo loại hợp đồng.

**TX đóng góp lợi nhuận lớn nhất** · Trung tính · Lợi nhuận

- **Diễn biến:** TX mang về 23,33 tr USD (11,9% tổng đóng góp). Biên theo bang đi từ 56,5% đến 69,9%.
- **Ý nghĩa:** Biên giữa các bang chênh nhau 13,4 điểm: các bang biên thấp là nơi nên xem lại giá cước hoặc chi phí trước.

**Nhu cầu xe biến động ngẫu nhiên theo ngày, không theo mùa vụ** · Trung tính · Đội xe

- **Diễn biến:** Bình quân mỗi ngày có 66,0 đến 66,2 xe hoạt động, ổn định qua các năm. Ngày cao điểm đến ngẫu nhiên: không có quý nào năm nào cũng bận hơn.
- **Ý nghĩa:** Không thể chuẩn bị xe theo mùa cao điểm. Quy mô đội xe nên tính theo số ngày cần đảm bảo đủ xe, ví dụ đủ cho 95% số ngày, thay vì theo lịch.

**Danh mục tuyến: 7 tuyến chủ lực, 6 tuyến cần đàm phán lại giá, 6 tuyến biên thấp cần rà soát** · Trung tính · Mạng lưới

- **Diễn biến:** Tuyến được chia 3×3 theo sản lượng và biên: 7 tuyến sản lượng cao biên cao, 6 tuyến sản lượng cao biên thấp, 6 tuyến sản lượng thấp biên thấp. Tuyến biên thấp nhất vẫn đạt 50,4%, tức mọi tuyến đều có lãi đóng góp.
- **Ý nghĩa:** Dữ liệu chưa có lương tài xế và chi phí chung nên chưa đủ căn cứ để ngừng tuyến nào. Ưu tiên đàm phán giá ở tuyến đông chuyến nhưng biên thấp: điều chỉnh giá ở đó tác động đến nhiều chuyến nhất.


## 2. Lãi lỗ theo năm

| Kỳ | Số chuyến | Doanh thu | Nhiên liệu | Bảo dưỡng | Bồi thường | Đóng góp | Biên | So kỳ trước | So cùng kỳ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 28.589 | 99,92 tr USD | 34,35 tr USD | 1,93 tr USD | 1,02 tr USD | 62,62 tr USD | 62,7% | — | — |
| 2023 | 28.165 | 98,91 tr USD | 31,07 tr USD | 1,97 tr USD | 0,79 tr USD | 65,07 tr USD | 65,8% | 3,9% | 3,9% |
| 2024 | 28.656 | 99,79 tr USD | 30,08 tr USD | 1,82 tr USD | 0,84 tr USD | 67,05 tr USD | 67,2% | 3,0% | 3,0% |

## 3. Lãi lỗ theo quý

| Quý | Doanh thu | Đóng góp | Biên | So kỳ trước | So cùng kỳ | Lũy kế năm | Lũy kế năm trước |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2022-Q1 | 24,51 tr USD | 15,62 tr USD | 63,7% | — | — | 15,62 tr USD | — |
| 2022-Q2 | 25,00 tr USD | 15,58 tr USD | 62,3% | -0,2% | — | 31,20 tr USD | — |
| 2022-Q3 | 25,28 tr USD | 15,64 tr USD | 61,8% | 0,3% | — | 46,84 tr USD | — |
| 2022-Q4 | 25,13 tr USD | 15,79 tr USD | 62,8% | 1,0% | — | 62,62 tr USD | — |
| 2023-Q1 | 24,52 tr USD | 16,14 tr USD | 65,8% | 2,2% | 3,3% | 16,14 tr USD | 15,62 tr USD |
| 2023-Q2 | 24,80 tr USD | 16,37 tr USD | 66,0% | 1,4% | 5,0% | 32,50 tr USD | 31,20 tr USD |
| 2023-Q3 | 24,79 tr USD | 16,25 tr USD | 65,5% | -0,7% | 3,9% | 48,75 tr USD | 46,84 tr USD |
| 2023-Q4 | 24,79 tr USD | 16,32 tr USD | 65,8% | 0,4% | 3,4% | 65,07 tr USD | 62,62 tr USD |
| 2024-Q1 | 24,82 tr USD | 16,79 tr USD | 67,6% | 2,9% | 4,0% | 16,79 tr USD | 16,14 tr USD |
| 2024-Q2 | 25,22 tr USD | 16,84 tr USD | 66,8% | 0,3% | 2,9% | 33,63 tr USD | 32,50 tr USD |
| 2024-Q3 | 24,81 tr USD | 16,63 tr USD | 67,0% | -1,3% | 2,4% | 50,27 tr USD | 48,75 tr USD |
| 2024-Q4 | 24,94 tr USD | 16,78 tr USD | 67,3% | 0,9% | 2,8% | 67,05 tr USD | 65,07 tr USD |

## 4. Cầu lợi nhuận 2022 → 2024

|  |  |
|---|---:|
| Đóng góp 2022 | 62,62 tr USD |
| Sản lượng | +0,15 tr USD |
| Giá mỗi chuyến | -0,37 tr USD |
| Giá nhiên liệu | +4,12 tr USD |
| Nhiên liệu mỗi chuyến | +0,22 tr USD |
| Bảo dưỡng | +0,11 tr USD |
| Bồi thường | +0,18 tr USD |
| Đóng góp 2024 | 67,05 tr USD |

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
| Contract | 112,40 tr USD | 73,64 tr USD | 65,5% | 37,5% |
| Spot | 94,22 tr USD | 61,97 tr USD | 65,8% | 31,6% |
| Dedicated | 92,00 tr USD | 60,53 tr USD | 65,8% | 30,9% |

**Loại hàng**

| Nhóm | Doanh thu | Đóng góp | Biên | Tỷ trọng đóng góp |
|---|---:|---:|---:|---:|
| Refrigerated | 150,13 tr USD | 98,51 tr USD | 65,6% | 50,2% |
| Dry Van | 148,50 tr USD | 97,63 tr USD | 65,7% | 49,8% |

**Bang đi (8 bang đóng góp nhiều nhất)**

| Nhóm | Doanh thu | Đóng góp | Biên | Tỷ trọng đóng góp |
|---|---:|---:|---:|---:|
| TX | 35,23 tr USD | 23,33 tr USD | 66,2% | 11,9% |
| OH | 28,58 tr USD | 19,96 tr USD | 69,9% | 10,2% |
| NC | 27,60 tr USD | 18,43 tr USD | 66,8% | 9,4% |
| WA | 26,94 tr USD | 18,06 tr USD | 67,0% | 9,2% |
| MO | 26,40 tr USD | 17,62 tr USD | 66,7% | 9,0% |
| IL | 24,18 tr USD | 16,00 tr USD | 66,2% | 8,2% |
| FL | 23,85 tr USD | 14,53 tr USD | 60,9% | 7,4% |
| PA | 17,46 tr USD | 11,51 tr USD | 65,9% | 5,9% |

**Tập trung khách hàng:** khách lớn nhất 0,6%, 10 khách lớn nhất 5,7%, 20 khách lớn nhất 11,2%; 157 trên 200 khách chiếm 80% doanh thu; HHI 50.

## 7. Nhiên liệu (thống kê)

| Năm | Gallon mua | Chi tiêu | Giá trung bình | Gallon tiêu thụ trên chuyến | Mua ÷ tiêu thụ |
|---|---:|---:|---:|---:|---:|
| 2022 | 8.181.816 | 34,35 tr USD | 4,198 USD | 6.344.699 | 1,29 |
| 2023 | 8.070.497 | 31,07 tr USD | 3,850 USD | 6.283.230 | 1,28 |
| 2024 | 8.241.247 | 30,08 tr USD | 3,650 USD | 6.318.352 | 1,30 |

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
| Thấp | 6 (rà soát (ít chuyến, biên thấp)) | 8 (theo dõi) | 6 (cơ hội tăng trưởng) |

## 10. Cân bằng hàng đi / hàng về (các thành phố lệch nhất)

| Thành phố | Lô đi | Lô đến | Chênh lệch | Mức lệch |
|---|---:|---:|---:|---:|
| Los Angeles | 0 | 8.948 | -8.948 | 200,0% |
| Indianapolis | 0 | 5.810 | -5.810 | 200,0% |
| Phoenix | 4.456 | 0 | 4.456 | 200,0% |
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
| surplus_act_pct | 20,0 | Ưu tiên xử lý khi trên 20% số lô kết thúc ở nơi không có hàng về; cùng mức với ngưỡng theo thành phố | dự án |
| predictable_autocorr | 0,5 | Dưới 0,5, một ngày giải thích dưới 25% biến động của ngày sau: quá yếu để lập kế hoạch | dự án |
| moved_watch_pct | 50,0 | Cần theo dõi khi phần lớn (trên một nửa) số lần chuyển phải di chuyển giữa các thành phố | dự án |
| fuel_gap_pct | 5,0 | Chênh lệch mua so với tiêu thụ trên 5% đáng để đối soát | dự án |
