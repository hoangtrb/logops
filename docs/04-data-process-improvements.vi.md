# 04 · Lỗ hổng dữ liệu → cải tiến quy trình

> Sinh tự động bằng `uv run logops build` từ `src/logops/optimize/`; không sửa tay. · Bản tiếng Anh: [04-data-process-improvements.md](04-data-process-improvements.md) · Spec: [SPEC-optimize.vi.md](../SPEC-optimize.vi.md)

Mỗi lỗ hổng: chi phí đo được nếu để nguyên, và biện pháp khả thi. Mức 1 = quy trình hoặc cấu hình trên hệ thống sẵn có. Mức 2 = thiết bị. Giá thiết bị là số liệu công khai tham khảo, cần thay bằng báo giá thực tế.

| # | Lỗ hổng | Bằng chứng | Chi phí khi không làm | Mức 1 | Mức 2 |
|---|---|---|---|---|---|
| 1 | Nhiên liệu mua chưa được đối soát với nhiên liệu tiêu thụ | Mua nhiều hơn tiêu thụ 5,57 triệu gallon trong 3 năm (tỷ lệ 1,29, như nhau ở mọi xe) | 7,24 triệu USD mỗi năm tiền nhiên liệu chưa giải thích được. Chuẩn ngành về lạm dụng thẻ: 2–5% chi phí nhiên liệu = 0,64 triệu USD–1,59 triệu USD mỗi năm | Báo cáo hằng tháng gallon mua so với tiêu thụ theo từng xe (dự án đã tính sẵn: KPI `fuel_purchased_to_burned`); điều tra xe vượt ngưỡng; bắt buộc nhập mã xe, mã tài xế và số đồng hồ km mỗi lần quẹt thẻ | Telematics đo mức nhiên liệu và vị trí, khớp với từng giao dịch thẻ |
| 2 | Thiếu mã tài xế và mã xe ở khoảng 2% chuyến và phiếu nhiên liệu | Thiếu ngẫu nhiên; khôi phục từ bảng khác được 0 dòng | 1,25 triệu USD mỗi năm chi phí nhiên liệu không gán được cho tài xế hay xe, nên xếp hạng và trách nhiệm không đầy đủ | Bắt buộc nhập mã tài xế và mã xe khi điều phối và trên thẻ nhiên liệu (hệ thống chặn: không có mã thì không điều phối) | Không cần |
| 3 | Dữ liệu không có lương tài xế và chi phí chung | Biên đóng góp 65,2% là trước lương tài xế | Không xác nhận được tuyến lời hay lỗ: tuyến yếu nhất lỗ nếu chi phí tài xế vượt 0,857 USD/dặm, và hiện không kiểm tra được | Xuất dữ liệu lương tài xế (theo tài xế, theo tháng) từ hệ thống lương vào kho dữ liệu hằng tháng | Không cần |
| 4 | Không ghi lý do khi giao hàng lệch khung giờ | Việc lệch không lặp lại theo tài xế, tuyến, khách hàng hay xe: nguyên nhân không có trong dữ liệu | 15.766 lần giao mỗi năm lệch khung ±2 giờ (55,4%) mà không chẩn đoán được nguyên nhân | Danh sách mã lý do ngắn trên ứng dụng tài xế hoặc TMS ở mỗi lần giao (kẹt xe, chờ cửa, giấy tờ, lấy hàng trễ, khác) | Giờ đến/đi theo hàng rào định vị (geofence) từ telematics |
| 5 | Trường kho và bang không đáng tin | `facility_id` khớp tuyến 3,4%; bang sai ở 95% phiếu nhiên liệu | 86.849 giờ chờ mỗi năm không gán được cho kho nào; không phân tích được theo kho hay theo bang | Danh mục kho và danh mục thành phố → bang chuẩn; kiểm tra dữ liệu nhập theo danh mục | Check-in tại kho bằng hàng rào định vị (dùng chung thiết bị telematics ở dòng 1) |
| 6 | Thời gian chạy không tải là nhiễu | Tương quan ≈ 0 với thời gian chuyến, quãng đường và nhiên liệu | Hoàn toàn không đo được lãng phí do nổ máy chờ | Không có: cần dữ liệu từ động cơ | Giờ nổ máy chờ từ telematics (dùng chung thiết bị ở dòng 1) |

## Telematics (mức 2 cho các dòng 1, 5, 6): chi phí so với lợi ích

|  |  |
|---|---:|
| Số xe đang chạy | 92 |
| Chi phí mỗi năm (thuê bao + thiết bị chia đều 3 năm) | 25.147 USD – 65.013 USD |
| Hòa vốn: phần chi phí nhiên liệu cần tiết kiệm | 0,2% |
| Chuẩn ngành riêng cho lạm dụng thẻ nhiên liệu | 2–5% = 0,64 triệu USD – 1,59 triệu USD |

Một thiết bị phục vụ các dòng 1, 5, 6. Thiết bị tự hoàn vốn nếu ngăn được 0,2% chi phí nhiên liệu; riêng chuẩn ngành về lạm dụng thẻ đã là 2–5%.

## Nguồn

- GPS Insight, “How Much Does Telematics Cost”: “$20 – $45 per vehicle per month for software and connectivity, plus $100–$500 in upfront hardware per vehicle” — <https://www.gpsinsight.com/blog/what-is-the-cost-of-telematics/>
- Automotive Fleet, citing Shell Fleet Solutions: “At a minimum, we have seen 2-5% of fuel spend lost to misuse every year” — <https://www.automotive-fleet.com/articles/fuel-fraud-prevention-strategies-reducing-costs-and-risks-for-fleets>
