# Đặc tả: data-platform

> Module 1/6 · xem [CAPABILITY-MAP.vi.md](CAPABILITY-MAP.vi.md) · CRISP-DM Giai đoạn 2–3 (Hiểu dữ liệu, Chuẩn bị dữ liệu) · Bản tiếng Anh: [SPEC-data-platform.md](SPEC-data-platform.md)

## Mục tiêu

**Dữ liệu nguồn:** [Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database)
(Kaggle, tác giả *yogape*), gồm 14 file CSV. Dữ liệu **không đưa lên git**: tải về, giải nén
vào thư mục `dataset/`, rồi chạy lệnh build.

Chuyển 14 file CSV thô trong `dataset/` thành một **kho dữ liệu DuckDB đã được kiểm tra, sẵn
sàng để truy vấn**. Mọi module khác đều đọc dữ liệu từ kho này. Module cũng tạo ra **báo cáo
chất lượng dữ liệu**: sản phẩm của Giai đoạn 2, cho người phỏng vấn thấy dữ liệu đã được kiểm
tra và hiểu rõ, không chỉ được nạp vào.

**Người dùng:** các module phía sau (`metrics`, `optimize`, …) và chủ dự án, người đọc báo cáo
chất lượng dữ liệu.

**Tiêu chí chấp nhận**
- Một lệnh duy nhất dựng lại toàn bộ từ CSV thô: file Parquet, cơ sở dữ liệu DuckDB và báo cáo
  chất lượng dữ liệu.
- Mọi bảng đều được nạp với kiểu dữ liệu khai báo rõ ràng cho từng cột, không để pandas tự đoán
  kiểu.
- Dòng lỗi được **đánh dấu, không xóa** (cột `dq_issues`). Chỉ xóa các dòng trùng lặp hoàn toàn,
  và ghi lại số dòng đã xóa.
- Báo cáo chất lượng dữ liệu liệt kê cho từng bảng: số dòng, % giá trị thiếu theo cột, tính duy
  nhất của khóa chính, khóa ngoại không khớp, các vi phạm quy tắc kèm số lượng và 3 dòng mẫu cho
  mỗi vi phạm.
- Các số liệu hiện trạng mà `docs/01-business-understanding.vi.md` §5 cần (tổng chi phí vận hành,
  % đúng giờ, MPG của đội xe, hiệu suất sử dụng) được in trong báo cáo, để xác nhận các mục tiêu
  thành công.

## Công nghệ

| Mục đích | Lựa chọn |
|---|---|
| Môi trường chạy | Python 3.11 (đã cài: 3.11.9) |
| Quản lý môi trường / thư viện | `uv` (đã cài 0.12.21, chưa có trong PATH, tạm dùng `python -m uv`) |
| Bộ xử lý | `duckdb` ≥ 1.1: đọc CSV, ghi Parquet, chứa kho dữ liệu |
| DataFrame | `polars` (chỉ dùng khi SQL không tiện) |
| Giao diện dòng lệnh | `typer` |
| Kiểm thử / kiểm tra code | `pytest`, `ruff` |

## Các lệnh

```bash
uv sync                          # cài thư viện
uv run logops build              # CSV → Parquet → DuckDB → báo cáo chất lượng (chạy lại nhiều lần vẫn cho cùng kết quả)
uv run logops build --skip-dq    # chỉ dựng kho dữ liệu (nhanh hơn khi đang phát triển)
uv run pytest                    # toàn bộ test
uv run pytest -m "not slow"      # chỉ unit test (không dùng dữ liệu thật)
uv run ruff check . && uv run ruff format .
```

## Cấu trúc dự án

```
dataset/                    → CSV gốc từ Kaggle (không đưa lên git, chỉ đọc, không bao giờ sửa)
data/                       → TỰ SINH, không đưa lên git
  parquet/<table>.parquet
  warehouse.duckdb
src/logops/
  cli.py                    → ứng dụng typer: `logops build`, sau này thêm `report`, `dashboard`
  config.py                 → đường dẫn, hằng số
  data_platform/
    schema.py               → khai báo kiểu cột cho 14 bảng (nguồn chuẩn duy nhất)
    ingest.py               → CSV → Parquet có kiểu
    quality.py              → quy tắc chất lượng → cờ dq_issues + kết quả kiểm tra
    warehouse.py            → Parquet → bảng DuckDB + quan hệ giữa các bảng
    dq_report.py            → kết quả kiểm tra → docs/02-data-quality-report(.vi).md
tests/
  fixtures/                 → các file CSV nhỏ tự tạo, chứa lỗi đã biết trước
  data_platform/
docs/
  02-data-quality-report.md     → TỰ SINH (tiếng Anh)
  02-data-quality-report.vi.md  → TỰ SINH (tiếng Việt, cùng số liệu, nhãn đã dịch)
  02-data-understanding.md      → phân tích viết tay dựa trên báo cáo (EN)
  02-data-understanding.vi.md   → bản tiếng Việt
```

## Quy tắc chất lượng dữ liệu (bộ ban đầu)

| Mã quy tắc | Kiểm tra | Bảng ví dụ |
|---|---|---|
| `pk_unique` | Khóa chính duy nhất và không rỗng | tất cả |
| `fk_orphan` | Khóa ngoại phải tồn tại trong bảng cha | trips→drivers, fuel→trips |
| `fk_missing` | Khóa ngoại bắt buộc bị rỗng | fuel_purchases.driver_id (đã thấy trong dữ liệu mẫu) |
| `geo_mismatch` | Cặp thành phố/bang không có trong facilities hay routes | fuel "New York, AZ" |
| `amount_mismatch` | `total_cost ≠ gallons × price` (±1%); `total_cost ≠ labor + parts` | fuel, maintenance |
| `range` | Giá trị ngoài khoảng hợp lý: mpg ∉ [3, 12], số dặm/chi phí âm, thời gian ≤ 0 | trips |
| `time_order` | Ngày nghỉ việc trước ngày tuyển; giao hàng trước khi lấy hàng | drivers, delivery_events |
| `agg_drift` | Số liệu tổng hợp theo tháng có sẵn lệch hơn 2% so với số tính lại từ trips | driver/truck monthly |

Các quy tắc nằm trong một danh sách duy nhất ở `quality.py`. Mỗi quy tắc là một điều kiện SQL
kèm mã và mức độ nghiêm trọng, nên thêm quy tắc mới chỉ cần một dòng.

## Phong cách code

```python
# quality.py: quy tắc là dữ liệu, không phải hàm
RULES: list[Rule] = [
    Rule("fuel_purchases", "amount_mismatch", "warn",
         "abs(total_cost - gallons * price_per_gallon) > 0.01 * total_cost"),
    Rule("trips", "range", "error",
         "average_mpg NOT BETWEEN 3 AND 12 OR actual_distance_miles <= 0"),
]
```

- Đặt tên snake_case; khai báo kiểu (type hint) ở mọi nơi; module nhỏ; xử lý bằng SQL trong
  DuckDB thay vì vòng lặp pandas.
- Đường dẫn chỉ lấy từ `config.py`; không bao giờ viết cứng `D:\...`.
- Cấu hình mặc định của Ruff, độ dài dòng 100.

## Chiến lược kiểm thử

- **Unit** (`tests/data_platform/`, chạy nhanh): các file CSV mẫu 5–10 dòng, mỗi file chứa một
  lỗi đã biết. Mỗi quy tắc chất lượng có một test chứng minh nó bắt được lỗi và bỏ qua dòng sạch.
- **Tích hợp** (`@pytest.mark.slow`): build toàn bộ trên dữ liệu thật trong `dataset/`; số dòng
  khớp với CSV; build hai lần cho kết quả giống hệt nhau.
- Chưa đặt mục tiêu % độ phủ test. Yêu cầu tối thiểu là mỗi quy tắc một test và test tích hợp
  phải chạy qua.

## Ranh giới

- **Luôn luôn:** giữ `dataset/` chỉ đọc; đánh dấu thay vì xóa; chạy `pytest` trước khi commit;
  ghi lại mọi quy tắc làm sạch trong báo cáo chất lượng dữ liệu.
- **Hỏi trước:** thêm thư viện ngoài danh sách công nghệ; xóa hoặc điền giá trị thay thế cho dữ
  liệu; thay đổi định nghĩa khóa chính hoặc khóa ngoại.
- **Không bao giờ:** commit `dataset/`, `data/` hay `.env`; sửa file CSV gốc; âm thầm ép kiểu dữ
  liệu (phải báo lỗi rõ ràng).

## Tiêu chí thành công

1. `uv run logops build` chạy xong trong **< 30 giây** trên laptop và tạo ra
   `data/warehouse.duckdb` chứa 14 bảng.
2. Số dòng trong kho dữ liệu bằng số dòng trong CSV, trừ đi các dòng trùng lặp hoàn toàn đã được
   ghi lại.
3. `docs/02-data-quality-report.md` và `.vi.md` được tạo ra, bao phủ đủ 14 bảng và tất cả quy tắc
   ở trên.
4. Báo cáo in ra các số liệu hiện trạng: tổng chi phí vận hành, % đúng giờ, MPG của đội xe, hiệu
   suất sử dụng trung bình.
5. `uv run pytest` chạy qua; `ruff check` không còn lỗi.

## Các quyết định đã chốt

- **Dữ liệu:** không phân phối lại; chỉ dẫn tên và đường link. Thư mục `dataset/` không đưa lên git.
- **Ngôn ngữ:** mọi tài liệu, đặc tả, kế hoạch và báo cáo tự sinh đều có hai file riêng EN
  (`name.md`) và VI (`name.vi.md`).
- **`uv`:** đã cài (0.12.21) nhưng chưa có trong PATH. Trong lúc chờ, dùng `python -m uv` thay
  cho `uv`.

## Câu hỏi còn mở

Không có.
