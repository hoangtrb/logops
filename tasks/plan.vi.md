# Kế hoạch triển khai: data-platform

> Module 1/6 · Đặc tả: [SPEC-data-platform.vi.md](../SPEC-data-platform.vi.md) · Bản tiếng Anh: [plan.md](plan.md)
> Danh sách việc: [todo.vi.md](todo.vi.md) (file tiếng Anh `todo.md` là nguồn chuẩn để đánh dấu hoàn thành)

## Tổng quan

Xây dựng lệnh `uv run logops build`: một lệnh duy nhất, chạy lại nhiều lần vẫn cho cùng kết quả,
biến 14 file CSV từ Kaggle thành các file Parquet có kiểu, một kho dữ liệu DuckDB và báo cáo chất
lượng dữ liệu song ngữ kèm số liệu hiện trạng. Các việc được chia theo lát cắt dọc: lát đầu tiên
đưa **một bảng** đi qua toàn bộ quy trình (CSV → Parquet → DuckDB → dòng lệnh → test). Sau đó,
mỗi việc mở rộng thêm hoặc số bảng, hoặc số quy tắc.

## Quyết định kiến trúc

- **DuckDB làm phần việc nặng.** DuckDB đọc CSV theo lược đồ khai báo sẵn, ghi Parquet và chứa
  kho dữ liệu, nên không dùng pandas ở phần xử lý chính. Cách này nhanh và thể hiện một mô hình
  có khả năng mở rộng.
- **Lược đồ là dữ liệu.** `schema.py` chứa một dict cho mỗi bảng (cột → kiểu DuckDB, khóa chính,
  khóa ngoại). Phần nạp dữ liệu, quy tắc khóa ngoại và test đều đọc từ đây: một nguồn chuẩn duy
  nhất.
- **Quy tắc là dữ liệu.** Mỗi quy tắc chất lượng là `Rule(table, id, severity, sql_predicate)`.
  Bộ máy ghi các vi phạm vào cột danh sách `dq_issues` và bảng `dq_findings`. Không bao giờ xóa
  dòng (chỉ xóa dòng trùng lặp hoàn toàn, và có ghi lại).
- **Báo cáo = mẫu + bảng kết quả kiểm tra.** Một bộ tạo báo cáo, hai bộ nhãn (EN/VI), hai file.
  Không bao giờ gõ tay số liệu.
- **Dùng dữ liệu mẫu thay vì giả lập.** Các file CSV nhỏ chứa lỗi đã biết đặt trong
  `tests/fixtures/`. Test chạy quy trình thật trên các file này.

## Sơ đồ phụ thuộc

```
T1 khung dự án
  └─ T2 lát cắt một bảng (lược đồ → nạp → kho dữ liệu → dòng lệnh)
       └─ T3 đủ 14 bảng
            ├─ T4 bộ máy kiểm tra + quy tắc khóa ─ T5 quy tắc giá trị ─ T6 agg_drift
            │                                                       └─ T7 báo cáo EN/VI + số liệu hiện trạng
            └─ T8 xử lý trùng lặp, --skip-dq, chạy lặp lại, hiệu năng
                                                                   └─ T9 tài liệu hiểu dữ liệu EN/VI
```

## Danh sách việc

### Giai đoạn 1: Nền tảng
- [x] T1: Khung dự án (uv, package, khung dòng lệnh, pytest, ruff) · S
- [x] T2: Lát cắt dọc một bảng: `routes` từ đầu đến cuối · M
- [x] T3: Mở rộng lược đồ & phần nạp cho cả 14 bảng · M

### Điểm kiểm tra A: Kho dữ liệu dựng được
- [x] `logops build` tạo `data/warehouse.duckdb` có 14 bảng; số dòng khớp CSV
- [x] Test và ruff đều qua · chủ dự án xem lại

### Giai đoạn 2: Chất lượng dữ liệu
- [x] T4: Bộ máy kiểm tra + quy tắc khóa (`pk_unique`, `fk_missing`, `fk_orphan`) · M
- [ ] T5: Quy tắc giá trị (`range`, `amount_mismatch`, `time_order`, `geo_mismatch`) · M
- [ ] T6: Quy tắc `agg_drift` (số liệu tháng so với số tính lại từ trips) · S

### Điểm kiểm tra B: Kết quả kiểm tra chính xác
- [ ] Mỗi quy tắc có test chạy qua trên dữ liệu mẫu; kết quả trên dữ liệu thật hợp lý
- [ ] Chủ dự án xem lại tỷ lệ báo động nhầm (đặc biệt là `geo_mismatch`)

### Giai đoạn 3: Báo cáo & hoàn thiện
- [ ] T7: Bộ tạo báo cáo chất lượng EN + VI, kèm số liệu hiện trạng · M
- [ ] T8: Ghi lại dòng trùng lặp, `--skip-dq`, chạy lặp lại cho cùng kết quả, hiệu năng < 30 giây · S
- [ ] T9: Viết tay tài liệu `02-data-understanding` (EN + VI) · S

### Điểm kiểm tra C: Hoàn thành module
- [ ] Đạt mọi tiêu chí thành công trong đặc tả · sẵn sàng viết đặc tả `metrics`

## Rủi ro và cách giảm thiểu

| Rủi ro | Mức ảnh hưởng | Cách giảm thiểu |
|---|---|---|
| Đọc CSV theo kiểu khai báo bị lỗi (thời gian có phần micro giây, chuỗi rỗng, "True"/"False") | Cao | T2 thử nghiệm cách làm trên một bảng trước; T3 thêm test cho từng bảng |
| `geo_mismatch` không có danh mục thành phố→bang đáng tin cậy, nên báo động nhầm hàng loạt | Trung bình | Mức `warn`; danh mục tham chiếu = các cặp thành phố/bang có trong facilities + routes; xem lại ở Điểm kiểm tra B; bỏ quy tắc nếu chỉ gây nhiễu |
| Định nghĩa tháng cho `agg_drift` chưa rõ (theo ngày điều xe hay ngày giao) | Trung bình | Thử theo tháng điều xe; báo cáo phân phối độ lệch thay vì báo lỗi cứng |
| `uv` chưa có trong PATH trên Windows | Thấp | Dùng `python -m uv`, hoặc thêm thư mục Scripts của người dùng vào PATH |
| Phạm vi lan sang các view KPI | Trung bình | View KPI thuộc module `metrics`; module này dừng ở bảng sạch + kiểm tra chất lượng |

## Câu hỏi còn mở

Không có. Mọi quyết định đã được ghi trong đặc tả.
