# 00 · Nhật ký dự án

> Bản tiếng Anh: [00-project-journal.md](00-project-journal.md) · Cơ sở phân tích: [00-analytical-approach.vi.md](00-analytical-approach.vi.md)
> **Cập nhật lần cuối:** Thứ 7 03/10/2026, sau module 3 `analysis`. Tổng kết ngắn gọn: [SUMMARY.vi.md](SUMMARY.vi.md).

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
├── SPEC-data-platform.md / .vi.md  Đặc tả module 1
├── SPEC-metrics.md / .vi.md        Đặc tả module 2: định nghĩa output trước khi code
├── pyproject.toml, uv.lock         Khai báo thư viện (uv quản lý)
├── docs/
│   ├── 00-project-journal.*        ← file này: nhật ký tiến độ
│   ├── 00-analytical-approach.*    Cơ sở lý thuyết và lý do chọn phương pháp
│   ├── 01-business-understanding.* CRISP-DM pha 1: câu hỏi của giám đốc → KPI → tiêu chí thành công
│   ├── 02-data-model.*             (tự sinh) sơ đồ quan hệ ER + từ điển dữ liệu, từ schema.py
│   ├── 02-data-quality-report.*    (tự sinh) báo cáo chất lượng dữ liệu + số liệu nền
│   ├── 02-dq-rule-thresholds.*     Các con số trong quy tắc và test: vì sao, nguồn
│   ├── 02-data-understanding.*     CRISP-DM pha 2: phân tích dữ liệu, điểm nói khi phỏng vấn
│   ├── 03-kpi-definitions.*        (tự sinh) 21 KPI: công thức, đơn vị, giá trị đội xe
│   ├── reviews/NN-<module>.*       Đánh giá cuối mỗi module: output, số liệu thật, điều chưa làm
│   └── SUMMARY.*                   Tổng kết toàn dự án, cập nhật cuối mỗi module
├── tasks/
│   ├── roadmap.md / .vi.md         Lịch 3 ngày cho cả 6 module
│   ├── plan.md / .vi.md            Kế hoạch module đang làm (hiện là data-platform)
│   └── todo.md / .vi.md            Danh sách việc; todo.md (tiếng Anh) là nguồn chuẩn để đánh dấu
├── src/logops/
│   ├── cli.py                      Lệnh `logops build`, `logops docs`, `logops kpi`
│   ├── config.py                   Mọi đường dẫn, tính từ thư mục gốc repo
│   └── data_platform/
│       ├── schema.py               Kiểu cột, khóa chính, khóa ngoại của 14 bảng (nguồn chuẩn duy nhất)
│       ├── ingest.py               CSV → Parquet có kiểu, báo lỗi rõ khi sai kiểu
│       ├── warehouse.py            Parquet → kho DuckDB
│       ├── quality.py              Quy tắc chất lượng dữ liệu → cột `dq_issues` + bảng `dq_findings`
│       ├── data_model_doc.py       Sinh `docs/02-data-model` từ schema.py
│       └── dq_report.py            Sinh `docs/02-data-quality-report` từ kho dữ liệu
│   └── metrics/
│       ├── views.py                3 view nền: trip_economics, delivery_performance, truck_economics
│       ├── kpis.py                 Danh mục 21 KPI + hàm kpi()
│       └── kpi_doc.py              Sinh `docs/03-kpi-definitions`
├── tests/
│   ├── fixtures/                   CSV nhỏ tự tạo, có lỗi cố ý để test
│   ├── test_smoke.py               CLI và đường dẫn
│   ├── data_platform/              Test nạp dữ liệu, lược đồ, và test tích hợp trên dữ liệu thật
│   └── metrics/                    Kho mẫu tính tay được + test tích hợp đối chiếu số thật
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
- **Bạn tự commit và push** (repo: https://github.com/hoangtrb/logops). Claude chỉ `git add` và
  gợi ý message sau mỗi việc.
- Dữ liệu gốc không bao giờ bị sửa. Dòng lỗi được **đánh dấu, không xóa**.
- Module gọn nhẹ: mỗi quy tắc/engine một test, mỗi module một test tích hợp.
- Các lệnh dùng `uv`. Nếu `uv` chưa có trong PATH thì dùng `python -m uv`.

## 4. Trạng thái tổng

| # | Module | Pha CRISP-DM | Ngày dự kiến | Trạng thái |
|---|---|---|---|---|
| — | Hiểu nghiệp vụ (`docs/01`) | 1 | T5 01/10 | ✅ Xong |
| 1 | `data-platform` | 2, 3 | T6 02/10 | ✅ Xong (7 việc; Việc 6 và 8 đã cắt) |
| 2 | `metrics` | 3 | Sáng T7 03/10 | ✅ Xong (29 test), commit `e99d12a` |
| 3 | `analysis` | 2, 3 | Tối T7 03/10 | ✅ Xong (12 test). Chờ bạn rà soát và commit |
| 4 | `dashboard` | 6 | Sáng CN 04/10 | ⏳ |
| 5 | `optimize` | 4, 5 | Sau phân tích | ⏸️ Ở nhánh `feature/optimize` |
| 6 | `reports` | 6 | Chiều CN 04/10 | ⏳ |
| — | Demo, đánh giá, đóng băng | 5 | Tối CN 04/10 | ⏳ |

Tiến độ module 1: █████████ hoàn tất (7 việc xong, 2 việc cắt có lý do).

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

### T6 02/10 · Checkpoint A và commit đầu tiên ✅
- Kho dữ liệu đạt Checkpoint A. Commit đầu tiên `61e34a7` đã push lên
  [github.com/hoangtrb/logops](https://github.com/hoangtrb/logops).
- Đã thêm `*.html` (bản xem trước Markdown) vào `.gitignore`.

### T6 02/10 · Việc 4: Engine chất lượng dữ liệu + quy tắc khóa ✅
- **Đã làm:**
  - `quality.py`: mỗi quy tắc là dữ liệu, `Rule(table, id, severity, predicate, column)`, trong đó
    `predicate` là điều kiện SQL, đúng khi dòng vi phạm.
  - 3 quy tắc khóa được **sinh tự động** từ khóa chính và khóa ngoại khai báo trong `schema.py`:
    `pk_unique` (error), `fk_missing` (warn), `fk_orphan` (error). Tổng cộng 50 quy tắc cho 14 bảng (14 khóa chính, 18 khóa ngoại × 2).
  - Mỗi bảng có thêm cột `dq_issues` liệt kê lỗi của dòng (rỗng nếu sạch). Bảng `dq_findings`
    ghi số vi phạm và 3 khóa mẫu cho từng quy tắc, kể cả quy tắc có 0 vi phạm.
  - `logops build` chạy bước này và in tóm tắt.
- **Kết quả:** 17 test xanh. Build cả 14 bảng kèm kiểm tra mất 5,4 giây. Không dòng nào bị xóa.
- **Phát hiện trên dữ liệu thật:**
  - **Không có khóa chính trùng, không có khóa ngoại "mồ côi"** ở cả 14 bảng: quan hệ giữa các bảng
    toàn vẹn.
  - Chỉ có khóa ngoại rỗng (cảnh báo):

    | Cột | Số dòng rỗng |
    |---|---:|
    | `fuel_purchases.driver_id` | 3.988 |
    | `fuel_purchases.truck_id` | 3.880 |
    | `trips.driver_id` | 1.714 |
    | `trips.trailer_id` | 1.680 |
    | `trips.truck_id` | 1.672 |
    | `safety_incidents.truck_id` / `driver_id` | 1 / 1 |

  - **Phân bố trông ngẫu nhiên**, mỗi cột khoảng 2%: 4.838 chuyến thiếu 1 mã, 114 chuyến thiếu
    2 mã, không chuyến nào thiếu cả 3. Đây là kiểu nhiễu cố ý của dữ liệu tổng hợp, không phải lỗi
    có hệ thống.
  - Tài xế thiếu trên phiếu nhiên liệu **không khôi phục được** từ chuyến: mọi phiếu thiếu tài xế
    đều thuộc chuyến cũng thiếu tài xế.
  - **Tác động:** 3,76 triệu USD trên 95,6 triệu USD chi phí nhiên liệu (3,9%) không gán được cho
    tài xế hoặc xe.
- **Quyết định:**
  - `fk_missing` là *warn*, còn `pk_unique` và `fk_orphan` là *error*. Thiếu mã là thiếu thông tin;
    trùng khóa hoặc mã mồ côi là dữ liệu sai.
  - Các module sau sẽ **giữ** các dòng này khi tính tổng chi phí đội xe, nhưng **loại** khi xếp
    hạng tài xế và xe. Đây chính là lý do đánh dấu thay vì xóa.
  - Mỗi lần chạy, các bảng được sắp theo khóa chính, nên kết quả ổn định giữa các lần build.

### T7 03/10 · Sơ đồ mô hình dữ liệu (bổ sung) ✅
- **Vì sao:** DBeaver không hiện khóa chính/khóa ngoại, vì kho cố ý không khai báo ràng buộc vật
  lý. Thử nghiệm cho thấy ràng buộc trong DuckDB làm build dừng khi gặp dòng lỗi và chặn việc
  dựng lại bảng cha.
- **Đã làm:** `logops docs` sinh `docs/02-data-model.md` / `.vi.md` từ `schema.py`, gồm sơ đồ
  Mermaid (GitHub tự vẽ) và từ điển dữ liệu. Có test báo lỗi nếu tài liệu lệch khỏi `schema.py`.
- **Phương án đã bỏ:** khai báo PK/FK thật trong DuckDB (để dành cho Việc 8 nếu còn thời gian);
  khóa ảo trong DBeaver (thủ công, chỉ có trên một máy).
- **Bổ sung tài liệu:** `00-analytical-approach` §3.4 về xử lý dữ liệu thiếu (Rubin: MCAR/MAR/MNAR).
  Kiểm tra cho thấy `driver_id` thiếu là MCAR, nên giữ dòng và xử lý theo từng phép phân tích.

### T7 03/10 · Cắt Việc 6 và Việc 8 ✂️
- **Lý do:** kiểm tra một lần cho thấy cả hai việc đều chỉ trả về "0 lỗi". Bảng tháng khớp 100% với
  số tính lại (cả tài xế và xe, kể cả bảo dưỡng); 0 dòng trùng; build đã ổn định và chỉ 5,4 giây.
- **Thay vào đó:** kết quả hai kiểm tra này được đưa vào báo cáo DQ (mục Kiểm tra chéo), tính lại
  bằng SQL mỗi lần build.

### T7 03/10 · Việc 5: Quy tắc giá trị ✅
- **Đã làm:** 20 quy tắc giá trị trong `VALUE_RULES` (`range`, `amount_mismatch`, `time_order`,
  `geo_mismatch`, `idle_exceeds_duration`); `all_rules()` gộp với quy tắc khóa, tổng cộng 70 quy tắc.
  `logops build` báo rõ khi file kho đang bị DBeaver giữ.
- **Kết quả:** 47 test xanh; nạp + kiểm tra mất 2,8 giây. 14/70 quy tắc có vi phạm.
- **Phát hiện chính:**
  - `on_time_flag` = đến trong khung **±2 giờ** so với giờ hẹn (khớp 100%). Sớm hơn 2 giờ bị tính
    là không đúng giờ.
  - `delivery_events.facility_id` gần như ngẫu nhiên (khớp tuyến 3,4%); `location_city` khớp 100%.
  - Bang trên phiếu nhiên liệu sai 95% ("Denver, TX"); giá nhiên liệu giữa các thành phố chỉ chênh
    0,02 USD/gallon.
  - 7.450 chuyến (8,7%) có thời gian không tải lớn hơn thời gian chuyến.
- **Quyết định:** mọi ngưỡng được ghi nguồn trong `docs/02-dq-rule-thresholds`. (Quy tắc tuổi tuyển
  dụng sau đó đã được bỏ, xem mục bên dưới.)

### T7 03/10 · Việc 7: Báo cáo chất lượng dữ liệu ✅
- **Đã làm:** `dq_report.py` tính mọi con số một lần bằng SQL rồi in ra 2 ngôn ngữ:
  `docs/02-data-quality-report.md` / `.vi.md`. Gồm tóm tắt, số liệu nền, phát hiện kèm 3 khóa mẫu,
  định nghĩa quy tắc, kiểm tra chéo, giá trị thiếu. Chạy lại ra file giống hệt từng byte.
- **Kết quả:** chi phí vận hành đo được 104,0 triệu USD (nhiên liệu 92%), 0,851 USD/dặm, MPG 6,45,
  giao trong khung 44,6%, chỉ **1,5% dòng có lỗi mức error**.
- **Vấn đề:** dấu `|` làm vỡ bảng Markdown (đã escape); con số "66,4% dòng có vấn đề" gây hiểu lầm
  nên tách riêng số dòng có lỗi mức error.

### T7 03/10 · Tài liệu ngưỡng và nguồn ✅
- **Đã làm:** `docs/02-dq-rule-thresholds` giải thích mọi con số trong quy tắc và test: dùng ở đâu, vì
  sao, nguồn (hồ sơ dữ liệu, quy định, định nghĩa, spec, thiết kế test).

### T7 03/10 · Việc 9: Hiểu dữ liệu ✅
- **Đã làm:** `docs/02-data-understanding` (EN/VI): dữ liệu nói gì, số liệu nền, bảng mức tin cậy,
  định nghĩa thật của `on_time_flag`, ảnh hưởng tới các module sau, đối chiếu tiêu chí thành công,
  điểm nói khi phỏng vấn.
- **Cập nhật kèm theo:**
  - `docs/01` §3 và §5: mục tiêu tiết kiệm = **≥ 3,1 triệu USD trong 3 năm**.
  - `00-analytical-approach` §5 và §6: phân tích theo địa điểm dùng `location_city`; bỏ đòn bẩy
    giá nhiên liệu theo địa điểm.
  - `CAPABILITY-MAP`: ghi chú đòn bẩy đã bỏ.

### T7 03/10 · Bỏ quy tắc tuổi tuyển dụng ✅
- **Lý do:** chủ dự án quyết định dự án tập trung vào **năng suất và chất lượng vận hành**, không xét
  tuân thủ nhân sự (câu hỏi 18 hay 21 tuổi không còn cần trả lời).
- **Đã làm:** bỏ `time_order:date_of_birth` khỏi `quality.py`; còn **69 quy tắc** (19 quy tắc giá trị;
  43 error, 26 warn). Cập nhật định nghĩa trong báo cáo, test, `02-dq-rule-thresholds` (kể cả số dòng
  trong bảng kiểm chứng) và `02-data-understanding`.
- **Kết quả:** chủ dự án đã đóng DBeaver và chạy build; chạy lại sau thay đổi mất 8,0 giây, 47 test
  xanh. Báo cáo DQ chỉ đổi đúng 3 dòng liên quan.

### T7 03/10 · Module 2 `metrics` ✅
- **Spec trước:** `SPEC-metrics` định nghĩa output (3 view, 21 KPI, lệnh, tài liệu), danh sách *không
  làm*, và tiêu chí thành công. Đã được duyệt trước khi code.
- **Đã làm:** `views.py` (3 view nền, phân bổ chi phí nhiên liệu theo gallon tiêu thụ trong tháng,
  bảo dưỡng theo dặm xe-tháng); `kpis.py` (21 KPI, nhóm theo 7 chiều, lọc ngày, dòng "Không gán
  được"); lệnh `logops kpi`; `docs/03-kpi-definitions` tự sinh.
- **Kết quả:** 6/6 tiêu chí thành công đạt. Tổng khớp bảng gốc; 76 test qua; build 6,6–7,4 giây.
- **Phát hiện:** 28/120 xe không chạy chuyến nào (1,40 triệu USD bảo dưỡng); gallon mua nhiều hơn
  tiêu thụ 29% ở mọi xe; sản lượng gần như không đổi (+1,3%); biên tuyến 50,4–72,7%.
- **Vấn đề:** dấu `|` trong công thức làm vỡ bảng (đã escape); test CLI cũ của module 1 cần tắt các
  bước cần đủ 14 bảng.
- **Đánh giá:** [reviews/02-metrics.vi.md](reviews/02-metrics.vi.md); module 1:
  [reviews/01-data-platform.vi.md](reviews/01-data-platform.vi.md).

### T7 03/10 · Đổi thứ tự: phân tích trước, optimize sau
- Chủ dự án quyết định làm phân tích trước. Module optimize đã làm được chuyển sang nhánh
  `feature/optimize` (đã push), sẽ làm lại sau khi có kết quả phân tích.

### T7 03/10 · Module 3 `analysis` ✅
- **Spec chốt cùng chủ dự án:** lợi nhuận theo cách doanh nghiệp theo dõi; không dữ liệu ngoài (kể cả
  tọa độ); bỏ thứ trong tuần, mùa vụ, operating ratio, dặm rỗng và giả thuyết nhiên liệu.
- **Đã làm:** `src/logops/analysis/` gồm `profit.py` (lãi lỗ theo kỳ, cầu lợi nhuận, đơn vị kinh tế,
  chiều kinh doanh, tập trung khách hàng), `operations.py` (nhiên liệu, năng lực đội xe, ma trận tuyến,
  cân bằng mạng lưới, đổi điểm xuất phát), `insights.py` (12 quy tắc), `bundle.py`, `doc.py`; lệnh
  `logops insights`; `docs/03-analysis-insights` tự sinh; thêm chiều bang và loại hàng vào lớp KPI.
- **Kết quả:** 93 test qua. 93% mức tăng lợi nhuận đến từ giá nhiên liệu; 33% số lô kết thúc ở nơi
  không có hàng về; không dự báo được ngày cao điểm.
- **Đối chiếu notebook:** tìm ra lỗi tính chi phí điều xe luôn bằng $0, mùa vụ do tháng dài ngắn, và
  các con số giả định.
- **Vấn đề đã sửa:** tỷ trọng theo nhóm cộng quá 100% (đổi mẫu số); chữ số viết tay trong câu mẫu (test
  bắt được).
- **Đánh giá:** [reviews/03-analysis.vi.md](reviews/03-analysis.vi.md).

## 6. Đang làm

**Module 3 `analysis` xong, chờ bạn rà soát rồi commit.** Đọc theo thứ tự:
1. [03-analysis-insights.vi.md](03-analysis-insights.vi.md) §1: 12 nhận xét tự sinh.
2. [reviews/03-analysis.vi.md](reviews/03-analysis.vi.md): output so với spec, đối chiếu notebook.
3. Thử: `python -m uv run logops insights`.

## 7. Sẽ làm

**Chủ nhật:** `dashboard` (đọc `analysis_bundle()`, hiển thị nhận xét) → `optimize` (làm lại từ nhánh
`feature/optimize`, thêm ghép hàng chiều về) → `reports` → kịch bản demo → đóng băng.

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
| File `.duckdb` bị khóa khi đang mở trong UI/PyCharm/DBeaver | Đóng kết nối trước khi `logops build` (lệnh giờ báo rõ lý do), hoặc mở ở chế độ `-readonly` |
| Dấu `\|` làm vỡ ô bảng Markdown | Escape thành `\\|` khi sinh báo cáo (`_cell`) |
| Terminal Windows không in được ký tự khung của DuckDB | Đặt `PYTHONIOENCODING=utf-8` |

## 10. Chạy và kiểm tra nhanh

```powershell
python -m uv sync                        # cài thư viện
python -m uv run logops build            # dựng lại kho từ dataset/
python -m uv run logops docs             # sinh lại sơ đồ mô hình dữ liệu
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
