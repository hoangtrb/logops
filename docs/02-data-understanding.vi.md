# 02 · Hiểu dữ liệu

> CRISP-DM pha 2 · Bản tiếng Anh: [02-data-understanding.md](02-data-understanding.md) · Số liệu
> lấy từ [02-data-quality-report.vi.md](02-data-quality-report.vi.md) (sinh tự động) · Ngưỡng và
> nguồn: [02-dq-rule-thresholds.vi.md](02-dq-rule-thresholds.vi.md) · Quan hệ bảng: [02-data-model.vi.md](02-data-model.vi.md)

**Tóm tắt một câu:** dữ liệu đủ tin cậy để phân tích chi phí và mức độ phục vụ, với điều kiện
**tránh dùng 3 cột** (bang trên phiếu nhiên liệu và sự cố, `facility_id` trên sự kiện giao nhận) và
**loại một số dòng** cho từng phép phân tích cụ thể. Không dòng nào bị xóa.

---

## 1. Dữ liệu nói về điều gì

Một đơn vị vận tải hàng hóa ở Mỹ, **3 năm từ 01/01/2022 đến 31/12/2024**, gồm 14 bảng và
549.706 dòng.

| Nhóm | Bảng | Quy mô |
|---|---|---|
| Tài sản và con người | `trucks`, `trailers`, `drivers` | 120 xe, 180 rơ-moóc, 150 tài xế |
| Thị trường | `customers`, `routes`, `facilities` | 200 khách hàng, 58 tuyến, 50 kho |
| Hoạt động | `loads`, `trips` | 85.410 lô hàng, mỗi lô đúng một chuyến |
| Sự kiện | `delivery_events`, `fuel_purchases`, `maintenance_records`, `safety_incidents` | 170.820 lần lấy/giao, 196.442 lần đổ nhiên liệu, 2.920 lần bảo dưỡng, 170 sự cố |
| Tổng hợp sẵn | `driver_monthly_metrics`, `truck_utilization_metrics` | 4.464 tháng-tài xế, 3.312 tháng-xe |

Dữ liệu được tổ chức theo **lược đồ hình sao**: `trips` ở trung tâm, nối với tài xế, xe, rơ-moóc
và lô hàng; các bảng sự kiện bao quanh (xem sơ đồ trong [02-data-model.vi.md](02-data-model.vi.md)).

## 2. Hiện trạng kinh doanh (số liệu nền)

| Chỉ số | Giá trị | Ý nghĩa |
|---|---|---|
| Doanh thu | 298,6 triệu USD | |
| Chi phí vận hành đo được | 104,0 triệu USD | Nhiên liệu + bảo dưỡng + bồi thường. Không có lương tài xế |
| ↳ Nhiên liệu | 95,6 triệu USD (**92%**) | **Đòn bẩy chi phí lớn nhất**: mỗi 1% tiết kiệm nhiên liệu ≈ 0,96 triệu USD |
| ↳ Bảo dưỡng | 5,7 triệu USD (5,5%) | |
| ↳ Bồi thường sự cố | 2,7 triệu USD (2,5%) | |
| Chi phí mỗi dặm | 0,851 USD | Trên 122,2 triệu dặm |
| MPG đội xe | 6,45 | Đúng mức thông thường của xe đầu kéo |
| Giao hàng trong khung ±2 giờ | **44,6%** | Thấp: hơn một nửa số lần giao lệch khung hẹn |
| Giao hàng không trễ (≤ giờ hẹn) | 33,3% | |
| Số giờ chờ (detention) | 260.607 giờ | Trung bình khoảng 1,5 giờ mỗi lần lấy/giao |
| Mức sử dụng xe trung bình | 83,0% | |

## 3. Dữ liệu tin được đến đâu

| Mức tin cậy | Nội dung | Bằng chứng |
|---|---|---|
| ✅ **Tin được** | Quan hệ giữa các bảng | 0 khóa trùng, 0 khóa ngoại trỏ sai ở cả 14 bảng |
| ✅ | Các khoản tiền | Tổng = các thành phần ở nhiên liệu, bảo dưỡng, sự cố (lệch lớn nhất 0,005 USD) |
| ✅ | Bảng tổng hợp tháng | Khớp 100% với số tính lại từ chuyến, lô hàng và bảo dưỡng |
| ✅ | Không trùng lặp | 0 dòng trùng tuyệt đối |
| ✅ | `location_city` của sự kiện giao nhận | Khớp điểm đầu/cuối tuyến 100% |
| ⚠️ **Dùng có điều kiện** | Khóa ngoại rỗng (khoảng 2%: tài xế, xe, rơ-moóc) | Thiếu ngẫu nhiên (MCAR); giữ cho tổng, loại khi xếp hạng. Xem `00-analytical-approach` §3.4 |
| ⚠️ | Thời gian không tải > thời gian chuyến | 7.450 chuyến (8,7%): **loại khỏi phân tích chạy không tải** |
| ⚠️ | Giao trước khi lấy | 486 chuyến (thời gian thực tế), 175 (kế hoạch): loại khỏi phân tích thời gian vận chuyển |
| ⚠️ | Mức sử dụng xe > 100% | 436 tháng (13,2%): khả năng do cách định nghĩa; dùng để *so sánh* giữa các xe, không đọc như phần trăm tuyệt đối |
| ❌ **Không dùng** | Bang (`location_state`) trên phiếu nhiên liệu và sự cố | 95–96% sai bang (ví dụ "Denver, TX"). Dùng thành phố thay thế |
| ❌ | `facility_id` trên sự kiện giao nhận | Chỉ khớp tuyến 3,4%, tương đương gán ngẫu nhiên. Phân tích theo địa điểm dùng `location_city` |
| ❌ | Chênh lệch giá nhiên liệu theo địa điểm | Giá trung bình giữa các thành phố chỉ chênh 0,02 USD/gallon (3,886–3,907): **không có tín hiệu** |

Tính chung, chỉ **1,5% số dòng** có lỗi mức *error*. Con số 66,4% "có ít nhất một vấn đề" chủ yếu
đến từ các cột bị đánh giá là không dùng được ở trên, không phải từ lỗi trong các số đo.

## 4. Phát hiện quan trọng: `on_time_flag` thực ra đo cái gì

Cờ đúng giờ **khớp 100%** với quy tắc "*đến trong khoảng ±120 phút so với giờ hẹn*", đã được thử ở
các mức 60, 90, 119, 120 và 121 phút; chỉ 120 khớp hoàn toàn. Hệ quả:

- Đến **trễ tới 2 giờ vẫn tính là đúng giờ**.
- Đến **sớm hơn 2 giờ bị tính là không đúng giờ** (5,5% sự kiện).

Đây là thước đo **tuân thủ khung giờ hẹn**, không phải đo trễ. Với một trung tâm phân phối, điều
này hợp lý: xe đến quá sớm cũng gây ùn ở cửa nhận hàng giống như xe đến trễ. Báo cáo sẽ trình bày
cả hai góc nhìn: tuân thủ khung (44,6%) và không trễ (33,3%).

## 5. Ảnh hưởng tới các bước tiếp theo

| Module | Điều chỉnh do dữ liệu |
|---|---|
| `metrics` | Chi phí/dặm tính trên mọi dòng. KPI đúng giờ có 2 định nghĩa (khung ±2 giờ và không trễ). Phân tích theo địa điểm dùng `location_city`, không dùng `facility_id` |
| `optimize` · nhiên liệu | **Bỏ đòn bẩy "mua nhiên liệu ở nơi rẻ hơn"** vì không có tín hiệu giá. Tập trung vào MPG và chạy không tải. Phân tích không tải loại 7.450 chuyến lỗi |
| `optimize` · giao hàng | Mô hình dự báo trễ dùng nhãn `on_time_flag` của lần giao (55,4% không đạt, nên hai lớp gần cân bằng). Tính năng địa điểm dùng `location_city` |
| `optimize` · đội xe | Mức sử dụng dùng để xếp hạng tương đối giữa các xe. Bảng tháng dùng được trực tiếp vì đã khớp 100% |
| Xếp hạng tài xế/xe | Loại các dòng thiếu mã; báo cáo có dòng "Không gán được" để tổng luôn khớp |

## 6. Đối chiếu tiêu chí thành công (`docs/01` §5)

| Tiêu chí | Trước | Sau khi đo | Kết luận |
|---|---|---|---|
| Tiết kiệm ≥ 3% chi phí vận hành | Tạm thời | 3% × 104,0 triệu = **≥ 3,1 triệu USD / 3 năm** (khoảng 1,04 triệu USD/năm) | Giữ. Thận trọng vì thiếu lương tài xế. Riêng nhiên liệu chiếm 92%, nên giảm 3,3% nhiên liệu là đạt mục tiêu |
| Mô hình trễ ROC-AUC ≥ 0,70 | Tạm thời | Hai lớp gần cân bằng (55,4% / 44,6%), nên AUC là thước đo phù hợp | Giữ |
| Báo cáo chất lượng phủ 100% bảng | Tạm thời | 14/14 bảng, 69 quy tắc | **Đạt** |

`docs/01` §5 đã được cập nhật theo bảng này.

## 7. Điểm nói khi phỏng vấn

1. **"Tôi kiểm tra trước khi tin."** 69 quy tắc chạy tự động mỗi lần build; dữ liệu lỗi được đánh
   dấu chứ không xóa, và mọi ngưỡng đều có nguồn.
2. **"Tôi tìm ra định nghĩa thật của chỉ số."** Cờ đúng giờ là khung ±2 giờ, không phải "không
   trễ". Nếu không phát hiện, báo cáo cho giám đốc sẽ hiểu sai mức độ phục vụ.
3. **"Tôi biết dữ liệu nào không được dùng, và vì sao."** Mã kho trên sự kiện là ngẫu nhiên, nên
   phân tích chờ theo kho phải dùng thành phố; giá nhiên liệu không chênh theo địa điểm, nên tôi
   không hứa một khoản tiết kiệm không có thật.
4. **"Nhiên liệu là 92% chi phí đo được."** Đó là nơi đầu tiên cần tìm tiền tiết kiệm.
