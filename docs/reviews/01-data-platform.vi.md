# Đánh giá · Module 1: `data-platform`

> CRISP-DM pha 2–3 · Bản tiếng Anh: [01-data-platform.md](01-data-platform.md) · Spec:
> [SPEC-data-platform.vi.md](../../SPEC-data-platform.vi.md) · Tổng kết: [SUMMARY.vi.md](../SUMMARY.vi.md)
> **Trạng thái:** hoàn tất ngày 03/10/2026 · Commit: `61e34a7`, `01a9afa`, `53e0967`, `618a91f`
> **Nguyên tắc của file:** chỉ ghi điều đã kiểm chứng bằng code hoặc truy vấn.

## 1. Output so với spec

| Output trong spec | Đã giao | Bằng chứng |
|---|---|---|
| Một lệnh dựng lại toàn bộ từ CSV | ✅ `logops build`: CSV → Parquet có kiểu → DuckDB → kiểm tra chất lượng → báo cáo | 14 bảng, 549.706 dòng; số dòng khớp CSV (test tích hợp) |
| Kiểu dữ liệu khai báo rõ, báo lỗi khi sai | ✅ `schema.py` + `ingest.py`; lỗi nêu đúng `bảng.cột` | Test với giá trị `"about 700"` trong cột số |
| Đánh dấu dòng lỗi, không xóa | ✅ Cột `dq_issues` trên mọi bảng + bảng `dq_findings` | Test: số dòng trước và sau kiểm tra bằng nhau |
| Báo cáo chất lượng EN/VI kèm số liệu nền | ✅ `docs/02-data-quality-report` (tự sinh, chạy lại ra file giống hệt) | Test tích hợp: phủ 14 bảng, mọi quy tắc |
| Build < 30 giây | ✅ 4,2 giây (14 bảng), 5,4 giây (thêm quy tắc khóa), 8,0 giây (đủ 69 quy tắc + báo cáo) | Thời gian in ra bởi `logops build` |
| Ngoài spec | Sơ đồ quan hệ ER (`02-data-model`), giải thích ngưỡng (`02-dq-rule-thresholds`), phân tích dữ liệu (`02-data-understanding`) | Theo yêu cầu bổ sung của chủ dự án |

## 2. Số liệu đo được

| Chỉ số | Giá trị |
|---|---|
| Số quy tắc chất lượng | 69 (50 quy tắc khóa + 19 quy tắc giá trị; 43 error, 26 warn) |
| Quy tắc có vi phạm | 14 / 69 |
| Dòng có lỗi mức error | 8.084 (1,5%) |
| Dòng có ít nhất một vấn đề, kể cả cảnh báo | 365.147 (66,4%). Trong đó 344.331 dòng (62,6% tổng số dòng) **chỉ** vì 2 cột địa điểm hỏng; số đo trên các dòng này vẫn đúng |
| Test | 47, tất cả qua |

## 3. Đánh giá dữ liệu: tin được gì

| Mức | Nội dung | Bằng chứng |
|---|---|---|
| ✅ Tin được | Quan hệ giữa các bảng | 0 khóa trùng, 0 khóa ngoại trỏ sai |
| ✅ | Các khoản tiền | Tổng = các thành phần; lệch lớn nhất 0,005 USD |
| ✅ | Bảng tổng hợp tháng | Khớp 100% với số tính lại |
| ✅ | Không trùng lặp | 0 dòng trùng tuyệt đối |
| ⚠️ Có điều kiện | Mã tài xế/xe/rơ-moóc rỗng (~2%) | Thiếu ngẫu nhiên (MCAR); khôi phục từ bảng khác được 0 dòng |
| ⚠️ | Giao trước khi lấy | 486 chuyến (thực tế), 175 chuyến (kế hoạch) |
| ⚠️ | Mức sử dụng xe > 100% | 436 tháng-xe (13,2%) |
| ❌ Không dùng | Bang trên phiếu nhiên liệu và sự cố | 95,3% và 95,9% sai bang |
| ❌ | `facility_id` trên sự kiện giao nhận | Khớp tuyến 3,4%; `location_city` khớp 100% |
| ❌ | `idle_time_hours` | Tương quan với thời gian chuyến 0,006, quãng đường 0,007, nhiên liệu/dặm 0,000: nhiễu ngẫu nhiên. 7.450 chuyến (8,7%) có giá trị lớn hơn cả thời gian chuyến |
| ❌ | Giá nhiên liệu theo địa điểm | Giá trung bình giữa các thành phố chênh 0,02 USD/gallon |

**`on_time_flag`** = \|thực tế − giờ hẹn\| ≤ 120 phút, khớp 100% với 170.820 sự kiện. Ranh giới sắc gọn:
mọi cờ `True` lệch trong ±120,00 phút, mọi cờ `False` lệch quá mức đó. Tài liệu của bộ dữ liệu
không định nghĩa cờ này và không có nguồn bên ngoài cho con số 120.

## 4. Không làm hoặc chưa làm, và vì sao

| Hạng mục | Lý do |
|---|---|
| Việc 6 `agg_drift` (cắt) | Kiểm tra một lần cho thấy lệch 0%; kết quả đưa vào phần kiểm tra chéo của báo cáo |
| Việc 8 hoàn thiện (cắt) | 0 dòng trùng; build đã ổn định và nhanh |
| Quy tắc tuổi tuyển dụng (bỏ) | Quyết định của chủ dự án: tập trung vào năng suất và chất lượng |
| 7 quy tắc chưa có test riêng | Mỗi *loại* quy tắc đều có test; danh sách ở `02-dq-rule-thresholds` §5 |
| Suy ra bang đúng từ thành phố | Đã đề xuất (25 thành phố ↔ 25 bang, sửa được 100%), chưa được duyệt |
| Tách lỗi cấp cột khỏi lỗi cấp dòng trong tóm tắt báo cáo | Đã đề xuất, chưa được duyệt; tóm tắt vẫn ghi 66,4% |

## 5. Ảnh hưởng tới các module sau

- Phân tích theo địa điểm dùng `location_city`, không dùng `facility_id`.
- Không đưa ra khoản tiết kiệm nào từ chạy không tải hoặc giá nhiên liệu theo địa điểm.
- Xếp hạng tài xế/xe loại các dòng thiếu mã; tổng đội xe giữ mọi dòng.
- Mục tiêu tiết kiệm: ≥ 3,1 triệu USD trong 3 năm (3% của 104,0 triệu USD chi phí đo được).

## 6. Tái lập

```powershell
python -m uv run logops build      # dựng kho, kiểm tra, sinh báo cáo
python -m uv run pytest            # 47 test của module này (76 tính cả module 2)
```
