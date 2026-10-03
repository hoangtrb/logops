# 02 · Ngưỡng của các quy tắc chất lượng dữ liệu: vì sao, nguồn, kiểm chứng

> Bản tiếng Anh: [02-dq-rule-thresholds.md](02-dq-rule-thresholds.md) · Quy tắc nằm trong
> `src/logops/data_platform/quality.py` · Kết quả: [02-data-quality-report.vi.md](02-data-quality-report.vi.md)
> **Kiểm chứng lần cuối:** 03/10/2026. Mọi con số dưới đây được đối chiếu với code (§6) và chạy lại
> trên dữ liệu thật bằng chính engine kiểm tra. Nếu đổi một ngưỡng, cập nhật file này cùng lúc.

Mỗi con số trả lời 3 câu hỏi: **dùng ở đâu**, **vì sao là số đó**, và **nguồn**.

**Loại nguồn**

| Ký hiệu | Nguồn | Ý nghĩa |
|---|---|---|
| 📊 | Hồ sơ dữ liệu | Đo trực tiếp trên bộ dữ liệu này |
| 📘 | Ngành / quy định | Chuẩn ngành hoặc văn bản pháp lý bên ngoài |
| 📐 | Định nghĩa / logic | Đúng theo định nghĩa, không cần ngưỡng (ví dụ tỷ lệ nằm trong 0–1) |
| 📝 | Quyết định của dự án | Ghi trong spec, là lựa chọn có chủ ý |
| 🧪 | Thiết kế test | Giá trị chọn để test rõ ràng ở một phía của ngưỡng |

**Tổng quan:** 69 quy tắc = 50 quy tắc khóa (sinh tự động từ `schema.py`) + 19 quy tắc giá trị.
Theo mức độ: 43 *error*, 26 *warn*.

---

## 1. Quy tắc khóa (`pk_unique`, `fk_missing`, `fk_orphan`)

Các quy tắc này **không có ngưỡng số**: khóa trùng, rỗng hoặc trỏ sai là sai, không có "trùng một chút".

| Con số / lựa chọn | Vì sao | Nguồn |
|---|---|---|
| `pk_unique` và `fk_orphan` là **error** | Khóa trùng hoặc trỏ tới bản ghi không tồn tại là dữ liệu *sai* | 📝 |
| `fk_missing` là **warn** | Mã rỗng là *thiếu thông tin*; dòng vẫn được tính vào tổng của đội xe | 📝 Xem `00-analytical-approach` §3.4 |
| 3 khóa mẫu cho mỗi quy tắc (`SAMPLE_SIZE = 3`) | Đủ để người đọc tra lại dòng lỗi, không làm báo cáo dài | 📝 Tiêu chí chấp nhận trong spec |

## 2. Quy tắc giá trị (`range`)

Các khoảng dạng "trong a–b" dùng `BETWEEN`, tức **tính cả hai đầu**: MPG đúng bằng 3 hoặc 12 vẫn hợp lệ.

| Ngưỡng | Bảng | Vì sao | Nguồn | Bằng chứng (📊) |
|---|---|---|---|---|
| MPG trong **3–12** | `trips`, `driver_monthly_metrics` | Xe đầu kéo (Class 8) chạy khoảng 6 MPG. Khoảng 3–12 là từ một nửa đến gấp đôi mức đó: chỉ bắt giá trị *không thể có* (gõ nhầm, sai đơn vị), không bắt xe chạy kém | 📘 U.S. DOE, Alternative Fuels Data Center + 📝 | Chuyến: 5,5–7,5 (trung vị 6,5). Bảng tháng: 6,01–7,07. 0 vi phạm. Không dùng khoảng hẹp hơn vì sẽ đánh dấu xe kém thật, đó là việc của module `optimize` |
| Quãng đường, thời gian, nhiên liệu của chuyến **> 0**; thời gian không tải **≥ 0** | `trips` | Chuyến đã hoàn thành không thể dài 0 dặm hay 0 giờ; không tải bằng 0 là hợp lệ | 📐 | Nhỏ nhất: 90 dặm, 1,4 giờ, 12 gallon |
| Số chuyến trong tháng **≥ 0** | `driver_monthly_metrics` | Số đếm không thể âm | 📐 | Nhỏ nhất: 5 |
| Doanh thu, trọng lượng, số kiện **> 0** | `loads` | Lô hàng có thật luôn có khối lượng và giá | 📐 | Nhỏ nhất: 125,93 USD, 10.000 lbs, 1 kiện |
| Phụ phí nhiên liệu, phụ phí khác **≥ 0** | `loads` | Không có phụ phí là hợp lệ | 📐 | 32.186 lô có `accessorial_charges = 0` |
| Gallon, giá nhiên liệu **> 0** | `fuel_purchases` | Phiếu đổ nhiên liệu luôn có lượng và giá | 📐 | 50–200 gallon; 3,15–5,00 USD/gallon |
| Giờ công, chi phí, giờ dừng **≥ 0** | `maintenance_records` | Âm là vô lý; bằng 0 là hợp lệ | 📐 | 0 vi phạm |
| Chi phí hư hại, bồi thường **≥ 0** | `safety_incidents` | Âm là vô lý; bằng 0 là hợp lệ (ví dụ hàng không hư hại) | 📐 | 122 sự cố có `cargo_damage_cost = 0` |
| Số phút chờ **≥ 0** | `delivery_events` | Không chờ là bình thường | 📐 | 22.472 sự kiện chờ 0 phút; nhiều nhất 239 phút |
| Tỷ lệ đúng giờ trong **0–1** | `driver_monthly_metrics` | Tỷ lệ theo định nghĩa nằm trong 0–100% | 📐 | 0,0–0,833 |
| Mức sử dụng xe trong **0–1**, mức **warn** | `truck_utilization_metrics` | Thường ≤ 100%. Để *warn* vì vượt 100% có thể do cách định nghĩa (ví dụ chia cho giờ chuẩn 8–10 giờ/ngày trong khi xe chạy nhiều ca), không hẳn là dữ liệu sai | 📐 + 📝 | **436 tháng (13,2%)** vượt 1; trung vị 0,833; p95 1,129; cao nhất 1,484 |

## 3. Quy tắc nhất quán

| Con số | Quy tắc | Vì sao | Nguồn | Bằng chứng (📊) |
|---|---|---|---|---|
| Sai lệch **1%** | `amount_mismatch` (nhiên liệu, bảo dưỡng, sự cố) | Tổng tiền phải bằng các thành phần: gallon × giá; công + phụ tùng; hư hại xe + hàng. Cần chừa chỗ cho làm tròn đến cent. 1% bắt được lỗi đáng kể (ví dụ tính tiền 120 gallon cho 100 gallon) nhưng bỏ qua sai số làm tròn. Với sự cố, 1% tính trên `claim_amount`; hai bảng kia tính trên `total_cost` | 📝 Spec | Lệch lớn nhất: 0,005 USD (0,003%) ở nhiên liệu; ở bảo dưỡng và sự cố chỉ có sai số dấu phẩy động (~10⁻¹²). 0 vi phạm |
| Thời gian không tải **≤ thời gian chuyến** | `idle_exceeds_duration` | Thời gian không tải là một *phần* của thời gian chuyến | 📐 | **7.450 chuyến (8,7%)** vi phạm; vượt trung vị 3,1 giờ, nhiều nhất 10,5 giờ |
| Giao **sau** lấy, cả thực tế và kế hoạch | `time_order` | Không thể giao trước khi lấy. So lần giao với lần lấy muộn nhất của cùng chuyến | 📐 | **486** chuyến (thực tế), **175** chuyến (kế hoạch) |
| Ngày nghỉ việc **không trước** ngày tuyển | `time_order` | Thứ tự bắt buộc | 📐 | 0 vi phạm |
| Cặp thành phố/bang thuộc **25 cặp tham chiếu** | `geo_mismatch:location_state` (nhiên liệu, sự cố, sự kiện giao nhận) | Tham chiếu là các địa điểm *chắc chắn có thật*: 50 kho cùng điểm đầu và cuối của 58 tuyến, gộp lại 25 cặp. Không thành phố nào xuất hiện ở hai bang. Mức *warn* vì cột bang không dùng được nhưng cột thành phố vẫn dùng được | 📊 | Nhiên liệu **95,3%** sai bang (ví dụ "Denver, TX"); sự cố **95,9%**; sự kiện giao nhận **0%** |
| Thành phố của sự kiện = thành phố của kho | `geo_mismatch:facility_id` | Sự kiện tại kho X phải diễn ra ở thành phố của kho X | 📐 | **96,6%** không khớp. Kiểm tra chéo cho thấy `location_city` khớp điểm đầu/cuối tuyến 100%, `facility_id` chỉ 3,4%, tức `facility_id` mới là cột sai |

*Quy tắc tuổi tuyển dụng đã được bỏ ngày 03/10/2026 theo yêu cầu của chủ dự án: dự án tập trung vào năng suất và chất lượng vận hành, không xét tuân thủ nhân sự.*

## 4. Kiểm tra chéo trong báo cáo (`dq_report.py`)

| Con số | Vì sao | Nguồn | Bằng chứng (📊) |
|---|---|---|---|
| Lệch **> 2%** giữa bảng tháng và số tính lại (số chuyến, dặm, doanh thu; chi phí bảo dưỡng) | Bảng tháng có thể làm tròn. 2% cho phép làm tròn nhưng bắt được tháng thiếu hoặc thừa chuyến | 📝 Spec | 0% tháng bị lệch, cả bảng tài xế và bảng xe |
| Số lần bảo dưỡng phải khớp **chính xác** | Số đếm không có sai số làm tròn | 📐 | Khớp 100% |
| Mức sàn **1 USD** khi so chi phí bảo dưỡng (`greatest(maintenance_cost, 1)`) | Tháng không bảo dưỡng có chi phí 0, khi đó dung sai 2% × 0 = 0 sẽ đánh dấu mọi sai lệch dù chỉ 1 cent. Sàn 1 USD giữ một dung sai tối thiểu | 📐 | — |
| Khung **±120 phút** của `on_time_flag` | **Không phải ngưỡng do dự án chọn**: đây là định nghĩa *tìm ra* từ dữ liệu. Thử các mức 60, 90, 119, 120, 121 phút; chỉ 120 khớp 100% | 📊 | Khớp 72,31% ở 60 phút; 86,10% ở 90; 99,53% ở 119; **100%** ở 120; 99,71% ở 121 |

## 5. Các con số trong test

Giá trị test được chọn **rõ ràng ở một phía** của ngưỡng, không nằm sát ranh giới, để test kiểm
đúng *ý nghĩa* của quy tắc và không phụ thuộc vào cách làm tròn. Giá trị "sạch" lấy gần với dữ liệu
thật để fixture trông giống thực tế.

### `test_quality_values.py`

| Trường hợp | Giá trị sạch | Giá trị lỗi | Vì sao chọn |
|---|---|---|---|
| MPG | 6,5 (500 dặm ÷ 77 gallon ≈ 6,49, tự khớp) | 40 | 6,5 = trung vị thực tế; 40 vượt xa trần 12, kiểu gõ nhầm hoặc nhầm đơn vị |
| Thời gian không tải | 2 giờ trên chuyến 10 giờ | 5 giờ trên chuyến 3 giờ | Vượt 2 giờ, gần trung vị vượt thực tế (3,1 giờ) |
| Doanh thu lô | 1.000 | −5 | Âm là vô lý rõ ràng |
| Tiền nhiên liệu | 100 gallon × 4 USD = 400 | 480 | Lệch 20%, gấp 20 lần ngưỡng 1% |
| Tiền bảo dưỡng | 100 + 50 = 150 | 300 | Lệch 100% |
| Bồi thường sự cố | 10 + 5 = 15 | 99 | Lệch 560% |
| Địa điểm nhiên liệu | Atlanta, GA | Atlanta, AZ | Mô phỏng đúng kiểu lỗi thật: thành phố đúng, bang sai |
| Tài xế | Tuyển 2015, nghỉ 2020 | Tuyển 2015, nghỉ 2010 | Nghỉ việc trước khi được tuyển 5 năm |
| Mức sử dụng xe | 0,7 | 1,4 | 0,7 gần trung vị (0,83); 1,4 gần mức cao nhất thật (1,484) |
| Sự kiện giao nhận | Lấy 08:00, giao 12:00 | Lấy 12:00, giao 08:00 | Đảo thứ tự 4 giờ, ở cả giờ thực tế và giờ kế hoạch |
| Kho của sự kiện | Sự kiện ở Atlanta, kho F1 ở Atlanta | Sự kiện ở Chicago, kho F1 ở Atlanta | Chicago, IL tự nó là cặp hợp lệ, nên test chỉ bắt lỗi *kho*, không bắt lỗi *bang* |

**Quy tắc chưa có test riêng** (logic giống các quy tắc đã test, nhưng chưa có dòng lỗi riêng trong fixture):

| Quy tắc | Bảng |
|---|---|
| `range` | `fuel_purchases`, `maintenance_records`, `safety_incidents`, `delivery_events`, `driver_monthly_metrics` |
| `geo_mismatch:location_state` | `safety_incidents`, `delivery_events` |

Mỗi *loại* quy tắc (`range`, `amount_mismatch`, `time_order`, `geo_mismatch`, `idle_exceeds_duration`)
đều có ít nhất một test, đúng tiêu chí "một test cho mỗi quy tắc" trong todo. Thêm test cho các dòng
trên mất khoảng 15 phút nếu muốn phủ đủ từng bảng.

### `test_quality_keys.py`

| Dòng | Lỗi cố ý | Kết quả mong đợi |
|---|---|---|
| `T1 → D1` | Không có | `dq_issues` rỗng |
| `T2` (2 dòng) | Khóa chính trùng | Cả 2 dòng `pk_unique` |
| `T3 → NULL` | Khóa ngoại rỗng | `fk_missing:driver_id` |
| `T4 → D9` | `D9` không có trong `drivers` | `fk_orphan:driver_id` |
| `D1, 2022-02-01` (2 dòng) | Khóa chính 2 cột bị trùng | Cả 2 dòng `pk_unique`; khóa mẫu hiển thị `D1\|2022-02-01` |

### `test_ingest.py` và `test_schema.py`

| Giá trị | Vì sao |
|---|---|
| `"about 700"` thay cho `697` trong cột số nguyên | Chữ lẫn trong cột số: đúng loại lỗi mà việc đoán kiểu ngầm sẽ che mất |
| Đổi tên cột `base_rate_per_mile` → `rate` | Header sai phải dừng build, không được nạp lệch cột |
| Ô trống ở `typical_distance_miles` của `RTE00004` | Phải thành NULL, không thành 0 |
| `2022-01-01 20:58:55.918185` | Lấy từ dòng đầu của dữ liệu thật: kiểm phần micro giây được giữ nguyên |
| `17:41:02.5` | Phần lẻ giây ngắn hơn 6 chữ số vẫn phải đọc đúng (thành 500.000 micro giây) |

Hai sự kiện mẫu này cũng khớp định nghĩa ±2 giờ: sự kiện đầu trễ 179 phút nên `on_time_flag = False`;
sự kiện sau sớm 19 phút nên `True`.

### `test_dq_report.py`

Số liệu mẫu (ví dụ doanh thu 298,6 triệu USD, MPG 6,5) lấy gần số thật để dễ nhận ra. Test chỉ kiểm
**cách định dạng** (dấu phẩy và dấu chấm theo ngôn ngữ, `|` được escape), không kiểm giá trị kinh doanh.

## 6. Bảng kiểm chứng: con số ↔ vị trí trong code

Đối chiếu ngày 03/10/2026 với các file trong thư mục `src/logops/data_platform/`.

| Con số | Vị trí | Khớp |
|---|---|---|
| `SAMPLE_SIZE = 3` | `quality.py:18` | ✅ |
| Danh sách 25 cặp tham chiếu (kho ∪ điểm đầu ∪ điểm cuối tuyến) | `quality.py:40–43` | ✅ |
| MPG 3–12, `> 0` / `< 0` cho chuyến | `quality.py:64–65` | ✅ |
| Không tải > thời gian chuyến | `quality.py:67` | ✅ |
| Lô hàng `> 0` / `< 0` | `quality.py:72–73` | ✅ |
| Nhiên liệu `> 0`; lệch 1% | `quality.py:75`, `quality.py:80` | ✅ |
| Bảo dưỡng `< 0`; lệch 1% | `quality.py:87`, `quality.py:93` | ✅ |
| Sự cố `< 0`; lệch 1% theo `claim_amount` | `quality.py:99`, `quality.py:105` | ✅ |
| Số phút chờ `< 0` | `quality.py:108` | ✅ |
| Giao trước lấy (thực tế, kế hoạch) | `quality.py:53`, `quality.py:109–122` | ✅ |
| Kho của sự kiện | `quality.py:129` | ✅ |
| Nghỉ trước tuyển | `quality.py:133` | ✅ |
| Bảng tháng tài xế: tỷ lệ 0–1, MPG 3–12, số chuyến ≥ 0 | `quality.py:138–139` | ✅ |
| Mức sử dụng 0–1 (warn) | `quality.py:145–146` | ✅ |
| Lệch 2% bảng tháng; số lần bảo dưỡng khớp chính xác; sàn 1 USD | `dq_report.py:80–96` | ✅ |
| Khung ±120 phút; sớm hơn 120 phút | `dq_report.py:103`, `dq_report.py:107` | ✅ |

*Số dòng có thể lệch nếu file được sửa sau ngày kiểm chứng.*

---

## Tài liệu tham khảo

- U.S. Department of Energy, Alternative Fuels Data Center. *Average Fuel Economy by Major Vehicle Category*.
