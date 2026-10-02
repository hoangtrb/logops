# 00 · Nhật ký dự án

> Bản tiếng Anh: [00-project-journal.md](00-project-journal.md) · Cơ sở phân tích: [00-analytical-approach.vi.md](00-analytical-approach.vi.md)
> **Cập nhật lần cuối:** Thứ 6 02/10/2026, sau Việc 3 (module `data-platform`).

**Cách dùng file này**
- Lần đầu đọc: đọc §1 → §4 để nắm dự án là gì, thư mục có gì, làm theo quy trình nào, đang ở đâu.
- Theo dõi hằng ngày: đọc §5 (đã làm), §6 (đang làm), §7 (sẽ làm).
- Muốn biết *vì sao* chọn cách phân tích này: đọc [00-analytical-approach.vi.md](00-analytical-approach.vi.md).
- Sau mỗi việc hoàn thành, thêm một mục vào §5 theo mẫu ở §11 và sửa §4, §6, §7.

---

## 1. Dự án là gì

**Logistics Ops Optimizer** biến dữ liệu vận hành đội xe (chuyến, nhiên liệu, giao nhận, bảo
dưỡng, sự cố) thành **quyết định tiết kiệm chi phí**, có ước tính số tiền tiết kiệm, trình bày
trên dashboard và báo cáo PDF/HTML xuất bằng một bước.

- **Mục đích:** dự án portfolio để trình bày với Giám đốc Logistics của Saigon Co.op trong buổi
  phỏng vấn **thứ Hai 05/10/2026**.
- **Người xem là nhà quản lý, không phải kỹ sư.** Mọi kết quả phải trả lời được câu hỏi
  *"tôi nên làm gì, và tiết kiệm được bao nhiêu?"*.
- **Dữ liệu:** [Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database)
  (Kaggle). Gồm 14 bảng, khoảng 58 MB, khoảng 550 nghìn dòng, từ 01/01/2022 đến 31/12/2024.
  Dữ liệu là của Mỹ (dặm, USD) và được giữ nguyên, vì phương pháp áp dụng được cho bất kỳ mạng
  lưới phân phối nào.
- **Khung làm việc:** CRISP-DM, gồm 6 pha. Mỗi pha có một sản phẩm nhìn thấy được (xem §4).

## 2. Bản đồ thư mục

```
logistics-ops/
├── README.md / .vi.md              Giới thiệu + 3 bước cài đặt
├── CAPABILITY-MAP.md / .vi.md      6 module, 4 lĩnh vực tối ưu, 6 loại báo cáo, ánh xạ CRISP-DM
├── SPEC-data-platform.md / .vi.md  Đặc tả module 1 (spec của các module sau sẽ nằm cạnh)
├── pyproject.toml, uv.lock         Khai báo thư viện (uv quản lý)
├── docs/
│   ├── 00-project-journal.*        ← file này: nhật ký tiến độ
│   ├── 00-analytical-approach.*    Cơ sở lý thuyết và lý do chọn phương pháp
│   ├── 01-business-understanding.* CRISP-DM pha 1: câu hỏi của giám đốc → KPI → tiêu chí thành công
│   └── 02-…                        (sẽ có) báo cáo chất lượng dữ liệu + phân tích dữ liệu
├── tasks/
│   ├── roadmap.md / .vi.md         Lịch 3 ngày cho cả 6 module
│   ├── plan.md / .vi.md            Kế hoạch module đang làm (hiện là data-platform)
│   └── todo.md / .vi.md            Danh sách việc; todo.md (tiếng Anh) là nguồn chuẩn để đánh dấu
├── src/logops/
│   ├── cli.py                      Lệnh `logops` (hiện có `build`)
│   ├── config.py                   Mọi đường dẫn, tính từ thư mục gốc repo
│   └── data_platform/
│       ├── schema.py               Kiểu cột, khóa chính, khóa ngoại của 14 bảng (nguồn chuẩn duy nhất)
│       ├── ingest.py               CSV → Parquet có kiểu, báo lỗi rõ khi sai kiểu
│       └── warehouse.py            Parquet → kho DuckDB
├── tests/
│   ├── fixtures/                   CSV nhỏ tự tạo, có lỗi cố ý để test
│   ├── test_smoke.py               CLI và đường dẫn
│   └── data_platform/              Test nạp dữ liệu, lược đồ, và test tích hợp trên dữ liệu thật
├── dataset/          (không commit) 14 file CSV gốc từ Kaggle, chỉ đọc
└── data/             (không commit) Sản phẩm sinh ra: parquet/ và warehouse.duckdb
```

## 3. Quy trình và quy ước

**Mỗi module đi theo vòng: spec → plan → build → checkpoint.**
1. **Spec** (`SPEC-<module>.md`): mục tiêu, công nghệ, cấu trúc, tiêu chí thành công.
2. **Plan + todo** (`tasks/`): chia thành các việc nhỏ, có tiêu chí chấp nhận và cách kiểm chứng.
3. **Build** theo *lát cắt dọc*: việc đầu tiên đưa **một bảng** đi hết đường ống (CSV → Parquet →
   DuckDB → CLI → test), sau đó mới mở rộng. Viết test trước, code sau.
4. **Checkpoint:** test và ruff xanh, bạn rà soát, rồi mới sang phần tiếp theo.

**Quy ước**
- Mọi tài liệu có 2 file: tiếng Anh `name.md` và tiếng Việt `name.vi.md`.
- **Bạn tự commit.** Claude chỉ `git add` và gợi ý message. Các tài liệu kế hoạch sẽ được commit
  cùng README ở cuối dự án.
- Dữ liệu gốc không bao giờ bị sửa. Dòng lỗi được **đánh dấu, không xóa**.
- Module gọn nhẹ: mỗi quy tắc/engine một test, mỗi module một test tích hợp.
- Các lệnh dùng `uv`. Nếu `uv` chưa có trong PATH thì dùng `python -m uv`.

## 4. Trạng thái tổng

| # | Module | Pha CRISP-DM | Ngày dự kiến | Trạng thái |
|---|---|---|---|---|
| — | Hiểu nghiệp vụ (`docs/01`) | 1 | T5 01/10 | ✅ Xong |
| 1 | `data-platform` | 2, 3 | T6 02/10 | 🔄 Đang làm: Việc 1–3 xong, đang ở Checkpoint A |
| 2 | `metrics` | 3 | Sáng T7 03/10 | ⏳ Chưa bắt đầu |
| 3 | `optimize` | 4, 5 | Chiều T7 03/10 | ⏳ |
| 4 | `insights` | 6 | Sáng CN 04/10 | ⏳ |
| 5 | `dashboard` | 6 | Sáng CN 04/10 | ⏳ |
| 6 | `reports` | 6 | Chiều CN 04/10 | ⏳ |
| — | Demo, đánh giá, đóng băng | 5 | Tối CN 04/10 | ⏳ |

Tiến độ module 1: ███░░░░░░ 3/9 việc.

## 5. Đã làm (theo thời gian)

### T5 01/10 · Hiểu nghiệp vụ và lập kế hoạch
- **Viết `docs/01-business-understanding`** (CRISP-DM pha 1). Tài liệu ánh xạ 5 câu hỏi của
  giám đốc sang KPI và kỹ thuật phân tích, đồng thời đặt tiêu chí thành công: tìm cơ hội tiết
  kiệm ≥ 3% tổng chi phí vận hành, mô hình dự báo trễ đạt AUC ≥ 0,70, xuất báo cáo ≤ 2 cú nhấp.
- **Viết `CAPABILITY-MAP`.** Chia dự án thành 6 module theo thứ tự phụ thuộc, xếp 4 lĩnh vực tối
  ưu theo mức ưu tiên của giám đốc.
- **Viết `SPEC-data-platform`, `tasks/plan` và `tasks/todo`** cho module 1, gồm 9 việc và 3 checkpoint.

### T6 02/10 · Lộ trình
- **Viết `tasks/roadmap`.** Lịch 3 ngày cho 6 module, cột "cắt nếu trễ", tiêu chí kết thúc mỗi ngày.

### T6 02/10 · Việc 1: Khung dự án ✅
- **Đã làm:** tạo project `uv` (Python 3.11; duckdb, polars, typer; pytest, ruff), package
  `src/logops/`, `config.py`, lệnh `logops build` dạng khung, README EN/VI.
- **Kết quả:** 2 test qua, ruff sạch.
- **Lưu ý:** ruff bản mới định dạng cả code trong file Markdown, nên đã loại `*.md` khỏi ruff.

### T6 02/10 · Việc 2: Lát cắt một bảng (`routes`) ✅
- **Đã làm:**
  - `schema.py` khai báo kiểu từng cột.
  - `ingest.py` đọc CSV dưới dạng chữ, kiểm từng giá trị có ép được sang kiểu khai báo không,
    rồi mới ghi Parquet.
  - `warehouse.py` nạp Parquet vào DuckDB bằng `CREATE OR REPLACE`, nên chạy lại bao nhiêu lần
    cũng ra cùng kết quả.
- **Kết quả:** 58 dòng trong 0,1 giây. Giá trị sai kiểu dừng build với lỗi dạng
  `routes.typical_distance_miles: 1 value(s) are not INTEGER, e.g. 'about 700'`.
- **Vì sao đọc dạng chữ trước:** nếu để DuckDB tự đoán kiểu, một ô bẩn sẽ khiến cả cột bị chuyển
  sang chữ mà không ai biết. Spec yêu cầu *báo lỗi to, không ép kiểu ngầm*.

### T6 02/10 · Việc 3: Đủ 14 bảng ✅
- **Đã làm:** khai báo đủ 14 bảng với kiểu dữ liệu, khóa chính và khóa ngoại. Thêm test lược đồ,
  test dữ liệu mẫu, và test tích hợp trên dữ liệu thật.
- **Kết quả:** 14 bảng nạp trong 4,2 giây (mục tiêu < 30 giây). Số dòng khớp CSV. 11 test xanh.
- **Quyết định:**
  - Hai bảng chỉ số tháng có khóa chính 2 cột: `(driver_id, month)` và `(truck_id, month)`.
  - `unit_number` và `trailer_number` là mã nên để kiểu chữ. `accessorial_charges` là tiền nên
    để DOUBLE.
  - Khóa ngoại rỗng được giữ thành NULL để Việc 4 đánh dấu (`trips.driver_id` rỗng ở 1.714 dòng,
    `fuel_purchases.driver_id` rỗng ở 3.988 dòng).
- **Số liệu sơ bộ** (chưa phải baseline chính thức; Việc 7 sẽ tính lại):

  | Chỉ số | Giá trị |
  |---|---|
  | Doanh thu (revenue + phụ phí) | ≈ 298,6 triệu USD |
  | Chi phí nhiên liệu | ≈ 95,6 triệu USD |
  | Chi phí bảo dưỡng | ≈ 5,7 triệu USD |
  | Tổng quãng đường | ≈ 122 triệu dặm |
  | MPG trung bình | 6,5 |
  | Tỷ lệ sự kiện đúng giờ (cả lấy hàng và giao hàng) | 55,7% |

  Tỷ lệ đúng giờ thấp bất thường. Cần kiểm tra ở Việc 7 và Việc 9 xem đó là đặc điểm của dữ liệu
  tổng hợp hay một cơ hội cải thiện thật.

## 6. Đang làm

**Checkpoint A: kho dữ liệu dựng được.** Test và ruff đã xanh. Còn chờ bạn rà soát kho, ví dụ
bằng `duckdb -ui data/warehouse.duckdb`, trước khi sang phần chất lượng dữ liệu.

## 7. Sẽ làm

**Module 1 còn lại (tối T6):**

| Việc | Nội dung | Cắt nếu trễ? |
|---|---|---|
| 4 | Engine DQ + quy tắc khóa: `pk_unique`, `fk_missing`, `fk_orphan` | Không |
| 5 | Quy tắc giá trị: `range`, `amount_mismatch`, `time_order`, `geo_mismatch` | Không |
| 6 | `agg_drift`: so bảng chỉ số tháng với số tính lại từ chuyến | **Có** |
| 7 | Sinh báo cáo DQ EN/VI + baseline (tổng chi phí, % đúng giờ, MPG, mức sử dụng) | Không |
| 8 | Gia cố: bỏ dòng trùng tuyệt đối, cờ `--skip-dq`, chạy lại ra cùng kết quả | **Có** |
| 9 | Viết `docs/02-data-understanding` để kể chuyện khi phỏng vấn | Không |

**Các module sau** (chi tiết trong [roadmap.vi.md](../tasks/roadmap.vi.md)):
- **Thứ 7:** `metrics` (view KPI bằng SQL) → `optimize` (4 engine khuyến nghị, mỗi engine có $ tiết kiệm).
- **Chủ nhật:** `insights` (Claude viết nhận xét) → `dashboard` (Streamlit) → `reports`
  (PDF/HTML) → kịch bản demo → đóng băng.

## 8. Các quyết định chính

Mỗi quyết định có lý do đầy đủ trong [00-analytical-approach.vi.md](00-analytical-approach.vi.md).

| Quyết định | Tóm tắt lý do |
|---|---|
| CRISP-DM làm khung | Bắt đầu từ câu hỏi kinh doanh và kết thúc bằng triển khai, đúng ngôn ngữ của nhà quản lý |
| DuckDB + Parquet, không dùng Spark | 58 MB chạy trên laptop trong vài giây; Spark chỉ thêm gánh nặng |
| Đánh dấu dòng lỗi, không xóa | Giữ dấu vết; người xem tự quyết có loại dòng hay không |
| Ước tính tiết kiệm theo *trung vị* đội xe | Thận trọng, đạt được thật, không hứa quá |
| Claude chỉ diễn giải số do code tính | Tránh việc LLM tự bịa số |
| Giữ đơn vị Mỹ | Phương pháp mới là điều cần chứng minh, không phải đơn vị |

## 9. Vấn đề đã gặp và cách xử lý

| Vấn đề | Cách xử lý |
|---|---|
| `uv` đã cài nhưng chưa có trong PATH | Dùng `python -m uv`, hoặc thêm thư mục Scripts của Python vào PATH |
| `uv` cảnh báo "Failed to hardlink" | Vô hại: cache nằm ở ổ C:, project ở ổ D:. Có thể đặt `UV_LINK_MODE=copy` để ẩn |
| ruff định dạng code trong Markdown | Thêm `extend-exclude = ["*.md"]` |
| DuckDB không nhận tham số `?` trong `CREATE VIEW` | Đưa đường dẫn vào câu SQL dạng chuỗi đã escape (`sql_path`) |
| File `.duckdb` bị khóa khi đang mở trong UI/PyCharm | Đóng kết nối trước khi `logops build`, hoặc mở ở chế độ `-readonly` |
| Terminal Windows không in được ký tự khung của DuckDB | Đặt `PYTHONIOENCODING=utf-8` |

## 10. Chạy và kiểm tra nhanh

```powershell
python -m uv sync                        # cài thư viện
python -m uv run logops build            # dựng lại kho từ dataset/
python -m uv run pytest                  # toàn bộ test (cả test trên dữ liệu thật)
python -m uv run pytest -m "not slow"    # chỉ unit test
python -m uv run ruff check .            # kiểm tra code
duckdb -ui data/warehouse.duckdb         # xem dữ liệu trên trình duyệt (cần cài DuckDB CLI)
```

## 11. Mẫu cập nhật (thêm vào §5 sau mỗi việc)

```markdown
### <Thứ ngày> · Việc N: <tên> ✅
- **Đã làm:** <sản phẩm cụ thể: file, lệnh, bảng>
- **Kết quả:** <số đo được: test, thời gian, số dòng, số phát hiện>
- **Quyết định:** <chọn gì, vì sao, phương án đã bỏ>
- **Vấn đề:** <nếu có, cách xử lý; thêm vào §9>
```

Sau đó cập nhật dòng "Cập nhật lần cuối", bảng §4, và các mục §6 và §7.
