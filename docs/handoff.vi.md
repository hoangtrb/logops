# Chuyển dự án sang máy khác

> Bản tiếng Anh: [handoff.md](handoff.md) · Kịch bản trình bày: [demo-script.vi.md](demo-script.vi.md) ·
> Tổng kết: [SUMMARY.vi.md](SUMMARY.vi.md) · Cập nhật 05/10/2026, sau commit module 6.

## 1. Cài đặt (một lần)

| Cần có | Ghi chú |
|---|---|
| Git | Để lấy mã nguồn |
| Python 3.11 trở lên | `pyproject.toml`: `requires-python >= 3.11` |
| [uv](https://docs.astral.sh/uv/) | Quản lý thư viện; trên máy cũ dùng `python -m uv` (uv 0.12) |
| Microsoft Edge hoặc Google Chrome | Bắt buộc để xuất **PDF** (in bằng trình duyệt, không cần thư viện thêm). Không có thì chỉ xuất được HTML |
| Phông Times New Roman | Có sẵn trên Windows; PDF dùng phông này |

```powershell
git clone https://github.com/hoangtrb/logops.git
cd logops
python -m uv sync
```

## 2. Những thứ KHÔNG có trong repo, phải chép tay

| Thứ | Lấy ở đâu | Đặt vào |
|---|---|---|
| Bộ dữ liệu (14 file CSV) | [Kaggle: Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database), giải nén | `dataset/` |
| Ảnh bìa báo cáo | Máy cũ: `reports/assets/cover.jpg` (ảnh có logo hãng xe nên không đưa lên repo) | `reports/assets/cover.jpg`; thiếu ảnh thì bìa PDF không có hình, còn lại vẫn chạy |
| File báo cáo mẫu của bạn | Máy cũ: `Bao_Cao_Tong_Hop_Van_Tai_Kho_va_TPTS_*.html` (chỉ để tham khảo bố cục, không commit) | Thư mục gốc, nếu cần |
| Báo cáo dự phòng | Máy cũ: `reports/output/*.pdf, *.html` | Hoặc tạo lại ở bước 4 |

## 3. Dựng kho dữ liệu và kiểm tra

```powershell
python -m uv run logops build                      # khoảng 20 giây: Parquet, DuckDB, tài liệu sinh tự động
python -m uv run pytest -m "slow or not slow" -q   # 160 test, khoảng 2 phút
```

Sau `logops build`, `git status` phải sạch (tài liệu sinh tự động không ghi ngày giờ, thứ tự đã cố
định). Nếu có file đổi, xem lại trước khi commit.

## 4. Chạy

```powershell
python -m uv run logops dashboard                       # http://localhost:8501
python -m uv run logops report --format pdf --lang vi   # → reports/output/bao-cao-van-tai-...pdf
python -m uv run logops report --format html --lang en  # → reports/output/transport-report-...html
python -m uv run logops optimize                        # in khuyến nghị ra màn hình
```

Trên dashboard: thanh bên → **Xuất báo cáo** → HTML/PDF → **Tạo báo cáo** (chạy nền) → **Tải về**.

## 5. Trước giờ trình bày

- [ ] Mở dashboard, chọn **Vi**, bấm qua cả 9 trang một lần (lần đầu mỗi trang vài giây, sau đó
  dưới 3 giây).
- [ ] Thử xuất một PDF từ thanh bên (khoảng 30 giây).
- [ ] Mở sẵn bản dự phòng PDF và HTML trong `reports/output/`.
- [ ] Đọc lại [demo-script.vi.md](demo-script.vi.md) (7 phút + câu hỏi có thể gặp).

## 6. Lỗi thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| Dashboard báo kho dữ liệu đang bị khóa | Đóng chương trình đang mở `data/warehouse.duckdb` (DBeaver, notebook, một dashboard khác), rồi tải lại trang |
| `logops build` báo lỗi ghi file | Như trên: tắt dashboard trước khi build |
| Cổng 8501 đã có người dùng | `python -m uv run logops dashboard --port 8502` |
| Xuất PDF báo không tìm thấy trình duyệt | Cài Edge hoặc Chrome, hoặc chọn HTML |
| Sửa code mà dashboard không đổi | Tắt hẳn dashboard (Ctrl+C) rồi chạy lại |
| Bản đồ theo bang không hiện | Bản đồ cần mạng; báo cáo xuất ra không có bản đồ (đã chủ đích) |
| Có cảnh báo "No runtime found" khi chạy `logops report` | Vô hại: các hàm của dashboard chạy ngoài Streamlit |

## 7. Số liệu chính (để nói không cần nhìn)

| | |
|---|---|
| Doanh thu · chi phí vận hành · lợi nhuận đóng góp | 298,62 · 103,88 · 194,74 tr USD (2022–2024); biên 65,2% |
| Giao đúng hẹn | 44,6% (±2 giờ) · 91,2% (theo ngày hẹn) |
| Biên 2022 → 2024 | 62,7% → 67,2%; 93% mức tăng nhờ giá nhiên liệu |
| Mạng lưới | 33% lô kết thúc nơi không có hàng chiều về; 95,4% chuyến kế tiếp bắt đầu ở thành phố khác |
| Đội xe | 120 sở hữu, 92 từng chạy, 99% số ngày cần ≤ 75 xe; 28 xe chưa chạy chuyến nào tốn 1,40 tr USD bảo dưỡng |
| Mục tiêu tiết kiệm | 1,04 tr USD/năm (3% × 34,65 tr USD) |
| Đo được · tiềm năng tối đa · tổng | 0,47 · 2,42 · 2,89 tr USD (278% mục tiêu) |
| Không cộng vào tổng | 7,24 tr USD nhiên liệu cần đối soát |

## 8. Lưu ý khi làm tiếp với Claude trên máy mới

Claude trên máy mới không nhớ các thỏa thuận trước. Mở phiên mới thì bảo Claude đọc file này, hoặc
chép mục này vào `CLAUDE.md` ở thư mục gốc (Claude tự đọc file đó mỗi phiên).

- **Ngôn ngữ:** trả lời bằng tiếng Việt. Mọi tài liệu viết hai bản `tên.md` (tiếng Anh) và `tên.vi.md`
  (tiếng Việt), liên kết nhau ở đầu file, kể cả spec, kế hoạch, tài liệu sinh tự động.
- **Git:** Claude chỉ stage file và đề xuất lời commit; **chủ dự án tự commit và push**. Không bao giờ
  stage `dataset/`, `data/`, `.env`, `reports/output/`, `Bao_Cao_*.html`, `reports/assets/cover.jpg`.
- **Dữ liệu:** không dùng dữ liệu bên ngoài (đã từ chối tọa độ công khai); quãng đường giữa thành phố
  lấy từ mạng tuyến của dữ liệu. Không xây phần dữ liệu không có (lương tài xế, chi phí chung, giá bán
  lại xe). Dữ liệu mô phỏng: không tự đặt tên công ty.
- **Phạm vi:** tập trung năng suất và chất lượng vận hành (chi phí, nhiên liệu, đúng hẹn, mức sử dụng
  xe, chất lượng dữ liệu); không thêm tiêu chí nhân sự hay tuân thủ pháp lý.
- **Số tiền:** ba loại không bao giờ cộng lẫn: tiết kiệm đo được, tiềm năng tối đa (cần khách hoặc nội
  bộ chấp nhận), ước tính/chưa giải thích được (không cộng vào tổng). Chỉ ghi số đo từ dữ liệu; tín hiệu
  phải lặp lại qua các năm mới có số tiền.
- **Mỗi việc xong:** cập nhật `docs/00-project-journal.md` + `.vi.md`. Mỗi module xong: bản đánh giá
  `docs/reviews/NN-*.md` + `.vi.md` và `docs/SUMMARY` (chỉ sự thật đã kiểm). Module mới bắt đầu bằng spec
  xác định output trước.
- **Thư viện:** hỏi trước khi thêm thư viện mới.
- **Trình bày (dashboard và báo cáo):**
  - mọi biểu đồ có đơn vị và đoạn "Diễn giải" viết thành câu, có số cụ thể;
  - dùng từ chuyên ngành tiếng Việt (chi phí nhiên liệu, lợi nhuận đóng góp, xe hoạt động, OTD…),
    không hiện tên biến hay tên bảng; nút Vi/En đổi cả tên KPI;
  - bảng có STT và bộ lọc kiểu Excel; điểm chính chia ba nhóm Ưu tiên xử lý / Cần theo dõi / Tham khảo,
    mỗi ý có đánh giá tốt/xấu, diễn biến, ảnh hưởng, đề xuất;
  - không dùng icon/emoji; mức độ dùng chữ có màu;
  - số tiền triệu ghi "tr USD"; không dùng từ khó hiểu như "mức trần" (dùng "tiềm năng tối đa");
  - ô kết quả khó hiểu phải có phần rê chuột hiện cách tính bằng số cụ thể và điều kiện đạt mục tiêu;
  - kịch bản ghi bằng lời ("Như hiện tại", không ghi 0%); bỏ biểu đồ khó hiểu thay vì giải thích thêm;
  - trang Khuyến nghị tối ưu là một trang riêng, đặt trước trang Chất lượng dữ liệu;
  - việc chạy lâu (xuất báo cáo) chạy nền, có dòng trạng thái và nút Tải về đổ màu xanh lá.
- **Báo cáo:** một file gồm mọi trang dashboard. HTML responsive, mỗi trang một tab, thanh tab 2 hàng
  (5 + 4), không thanh cuộn. PDF dàn trang kiểu văn bản:
  - Times New Roman, chữ đen 11 pt, tiêu đề xanh đậm, lề 20 mm;
  - bìa (tên báo cáo, đề tài, nguồn dữ liệu, ảnh ở dưới cùng), mục lục, danh mục hình, danh mục bảng có
    số trang, tóm tắt điều hành;
  - mỗi mục sang trang mới; hình và bảng đánh số, không khung; bảng rộng in trang ngang, không cắt dữ
    liệu;
  - chân trang: tên báo cáo, ngày xuất, trang x / y.
- **Kiểm tra giao diện:** sau mỗi thay đổi, chụp màn hình để xem lại (dashboard ở 1440 px và 390 px,
  từng trang PDF), không chỉ dựa vào test.
