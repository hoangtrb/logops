# Danh sách việc: data-platform

> Kế hoạch: [plan.vi.md](plan.vi.md) · Bản tiếng Anh: [todo.md](todo.md) (**file tiếng Anh là nguồn chuẩn để đánh dấu hoàn thành**; file này là bản dịch để tham khảo)
> Các lệnh dùng `uv`; nếu `uv` chưa có trong PATH thì dùng `python -m uv`.

## Việc 1: Khung dự án
**Mô tả:** Tạo `pyproject.toml` (uv, Python 3.11, thư viện: duckdb, polars, typer; thư viện phát
triển: pytest, ruff), package `src/logops/`, `config.py` chứa các đường dẫn, và lệnh `logops` có
sẵn khung cho lệnh `build`. Thêm README hướng dẫn tải dữ liệu.

**Tiêu chí chấp nhận:**
- [x] `uv sync` chạy thành công; `uv run logops --help` liệt kê lệnh `build`
- [x] `config.py` xác định đường dẫn `dataset/` và `data/` tương đối theo thư mục gốc của repo
- [x] README dẫn link dữ liệu Kaggle và nêu 3 bước cài đặt

**Kiểm chứng:** `uv run pytest` (một smoke test chạy qua) · `uv run ruff check .`
**Phụ thuộc:** Không có
**File:** `pyproject.toml`, `src/logops/__init__.py`, `src/logops/cli.py`, `src/logops/config.py`, `README.md` (+ `README.vi.md`), `tests/test_smoke.py`
**Quy mô:** S

## Việc 2: Lát cắt dọc một bảng (`routes`)
**Mô tả:** Khai báo lược đồ `routes` trong `schema.py`. `ingest.py` đọc CSV theo kiểu khai báo rõ
ràng và ghi Parquet; `warehouse.py` nạp Parquet vào DuckDB; `logops build` chạy cả hai bước.

**Tiêu chí chấp nhận:**
- [x] `logops build` tạo `data/parquet/routes.parquet` và bảng `routes` trong `data/warehouse.duckdb`
- [x] Kiểu cột khớp chính xác với lược đồ (cột số không bị chuyển thành VARCHAR)
- [x] Nếu CSV có kiểu dữ liệu sai, chương trình báo lỗi rõ ràng, nêu tên bảng và tên cột

**Kiểm chứng:** test trên dữ liệu mẫu `tests/data_platform/test_ingest.py` · kiểm tra thủ công: `duckdb data/warehouse.duckdb "describe routes"`
**Phụ thuộc:** Việc 1
**File:** `data_platform/schema.py`, `data_platform/ingest.py`, `data_platform/warehouse.py`, `cli.py`, `tests/fixtures/routes.csv`, file test
**Quy mô:** M

## Việc 3: Đủ 14 bảng
**Mô tả:** Thêm lược đồ (kiểu dữ liệu, khóa chính, khóa ngoại) cho 13 bảng còn lại, bao gồm thời
gian có phần micro giây, giá trị logic lưu dạng "True"/"False", và khóa ngoại có thể rỗng.

**Tiêu chí chấp nhận:**
- [x] Kho dữ liệu có 14 bảng; số dòng bằng số dòng trong CSV
- [x] Mỗi lược đồ khai báo khóa chính và khóa ngoại (dùng cho các quy tắc khóa sau này)

**Kiểm chứng:** `uv run pytest -m slow` (test tích hợp đếm số dòng trên dữ liệu thật)
**Phụ thuộc:** Việc 2
**File:** `schema.py`, `tests/data_platform/test_build_integration.py`
**Quy mô:** M

## Điểm kiểm tra A: Kho dữ liệu dựng được
- [x] Toàn bộ test + ruff đều qua
- [x] Chủ dự án xem lại trước khi làm phần kiểm tra chất lượng

## Việc 4: Bộ máy kiểm tra + quy tắc khóa
**Mô tả:** `quality.py` với `Rule(table, id, severity, predicate)`. Bộ máy thêm cột `dq_issues`
vào mỗi bảng và ghi bảng `dq_findings` (bảng, quy tắc, mức độ, số lượng, mã dòng mẫu). Các quy
tắc: `pk_unique`, `fk_missing`, `fk_orphan`, sinh tự động từ khai báo khóa chính/khóa ngoại trong
`schema.py`.

**Tiêu chí chấp nhận:**
- [x] Dữ liệu mẫu có khóa chính trùng, khóa ngoại rỗng và khóa ngoại không khớp → mỗi lỗi được đánh dấu đúng một lần
- [x] Các dòng mẫu sạch có `dq_issues` rỗng
- [x] Không xóa dòng nào

**Kiểm chứng:** `uv run pytest tests/data_platform/test_quality_keys.py`
**Phụ thuộc:** Việc 3
**File:** `quality.py`, `warehouse.py`, dữ liệu mẫu, file test
**Quy mô:** M

## Việc 5: Quy tắc giá trị
**Mô tả:** Thêm `range`, `amount_mismatch`, `time_order` và `geo_mismatch`, mỗi quy tắc một dòng.

**Tiêu chí chấp nhận:**
- [ ] Mỗi quy tắc có một test trên dữ liệu mẫu: đánh dấu dòng lỗi và bỏ qua dòng sạch
- [ ] `geo_mismatch` có mức `warn`, danh mục tham chiếu lấy từ facilities + routes

**Kiểm chứng:** `uv run pytest tests/data_platform/test_quality_values.py`
**Phụ thuộc:** Việc 4
**File:** `quality.py`, dữ liệu mẫu, file test
**Quy mô:** M

## Việc 6: Quy tắc `agg_drift`
**Mô tả:** Tính lại số chuyến, số dặm và doanh thu theo tháng cho từng tài xế và từng xe từ
`trips` + `loads`, rồi so với `driver_monthly_metrics` / `truck_utilization_metrics`. Đánh dấu
các dòng lệch hơn 2%.

**Tiêu chí chấp nhận:**
- [ ] Dữ liệu mẫu có một tháng bị lệch → được đánh dấu; tháng khớp → sạch
- [ ] Kết quả kiểm tra có phân phối độ lệch (trung vị, p95), không chỉ có số lượng

**Kiểm chứng:** `uv run pytest tests/data_platform/test_quality_agg.py`
**Phụ thuộc:** Việc 4
**File:** `quality.py`, dữ liệu mẫu, file test
**Quy mô:** S

## Điểm kiểm tra B: Kết quả kiểm tra chính xác
- [ ] Chạy trên dữ liệu thật; xem lại kết quả, đặc biệt là tỷ lệ báo động nhầm của `geo_mismatch`
- [ ] Chủ dự án xem lại

## Việc 7: Báo cáo chất lượng EN + VI kèm số liệu hiện trạng
**Mô tả:** `dq_report.py` tạo báo cáo từ `dq_findings` + % giá trị thiếu theo cột + số liệu hiện
trạng (tổng chi phí vận hành, % đúng giờ, MPG của đội xe, hiệu suất sử dụng trung bình), ghi ra
`docs/02-data-quality-report.md` và `.vi.md`, dùng một mẫu với hai bộ nhãn.

**Tiêu chí chấp nhận:**
- [ ] Cả hai file bao phủ đủ 14 bảng và mọi quy tắc, kèm 3 dòng mẫu cho mỗi vi phạm
- [ ] Số liệu hiện trạng giống hệt nhau ở cả hai ngôn ngữ
- [ ] Chạy lại tạo ra file giống hệt từng byte (không có dấu thời gian trong nội dung)

**Kiểm chứng:** `uv run pytest tests/data_platform/test_dq_report.py` · đọc thủ công cả hai file
**Phụ thuộc:** Việc 5, Việc 6
**File:** `dq_report.py`, `cli.py`, file test
**Quy mô:** M

## Việc 8: Hoàn thiện
**Mô tả:** Xóa dòng trùng lặp hoàn toàn và ghi lại số lượng; thêm tùy chọn `--skip-dq`; đảm bảo
chạy lần hai cho cùng kết quả; đo thời gian build.

**Tiêu chí chấp nhận:**
- [ ] Build toàn bộ < 30 giây trên laptop (dòng lệnh in ra thời gian chạy)
- [ ] Chạy hai lần cho cùng số dòng và cùng kết quả kiểm tra
- [ ] `--skip-dq` dựng kho dữ liệu mà không chạy bước kiểm tra chất lượng

**Kiểm chứng:** `uv run pytest -m slow` · chạy thủ công có đo thời gian
**Phụ thuộc:** Việc 3 (cần Việc 7 để kiểm tra đầy đủ)
**File:** `ingest.py`, `cli.py`, file test
**Quy mô:** S

## Việc 9: Tài liệu hiểu dữ liệu
**Mô tả:** Đọc báo cáo tự sinh và viết phần phân tích để kể chuyện khi phỏng vấn: dữ liệu bao
phủ những gì, các vấn đề chất lượng chính và cách xử lý, số liệu hiện trạng, và các mục tiêu
thành công ở tài liệu 01 §5 đã được xác nhận hoặc điều chỉnh.

**Tiêu chí chấp nhận:**
- [ ] `docs/02-data-understanding.md` + `.vi.md` tồn tại và nội dung khớp nhau
- [ ] Cập nhật mục tiêu ở tài liệu 01 §5 (cả hai ngôn ngữ) nếu số liệu hiện trạng làm thay đổi chúng

**Kiểm chứng:** chủ dự án đọc lại
**Phụ thuộc:** Việc 7
**File:** `docs/02-data-understanding.md`, `.vi.md`, `docs/01-*.md`
**Quy mô:** S

## Điểm kiểm tra C: Hoàn thành module
- [ ] Đạt mọi tiêu chí thành công trong SPEC-data-platform
- [ ] Sẵn sàng viết `SPEC-metrics.md`
