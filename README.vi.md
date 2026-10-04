# Logistics Ops Optimizer

> Bản tiếng Anh: [README.md](README.md) · Các module: [CAPABILITY-MAP.vi.md](CAPABILITY-MAP.vi.md) · Lộ trình: [tasks/roadmap.vi.md](tasks/roadmap.vi.md)
> **Tổng kết: [docs/SUMMARY.vi.md](docs/SUMMARY.vi.md)** · Tiến độ: [docs/00-project-journal.vi.md](docs/00-project-journal.vi.md) · Phương pháp: [docs/00-analytical-approach.vi.md](docs/00-analytical-approach.vi.md)

Biến dữ liệu đội xe thô thành các quyết định tiết kiệm chi phí cho mạng lưới phân phối: chi phí
phục vụ, giao hàng đúng giờ, hiệu quả nhiên liệu và mức sử dụng đội xe, trình bày trên dashboard
và báo cáo PDF/HTML xuất bằng một cú nhấp.

## Tóm tắt

| | |
|---|---|
| **Bài toán** | Giảm ít nhất 3% chi phí vận hành mỗi năm (1,04 tr USD) và nâng chất lượng giao hàng, từ chính dữ liệu vận hành của doanh nghiệp |
| **Dữ liệu** | [Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database) (Kaggle, dữ liệu mô phỏng): doanh nghiệp vận tải đường bộ tại Mỹ, 14 bảng, 549.706 dòng, 85.410 chuyến giai đoạn 2022–2024, 120 xe tải, 200 khách hàng, 58 tuyến |
| **Phương pháp** | CRISP-DM qua sáu module: nền tảng dữ liệu → KPI → phân tích → dashboard → tối ưu → báo cáo |
| **Kết quả** | Tiết kiệm đo được 0,47 tr USD mỗi năm (45% mục tiêu); tiềm năng tối đa thêm 2,42 tr USD nếu khách chấp nhận điều chỉnh giá; tổng 2,89 tr USD (278%). Không cộng vào tổng: 7,24 tr USD nhiên liệu cần đối soát |

## Sử dụng

```bash
uv run logops dashboard          # dashboard tại http://localhost:8501 (VI/EN, 9 trang)
uv run logops report --format pdf --lang vi          # báo cáo → reports/output/
uv run logops report --format html --from 2024-01-01 --to 2024-12-31 --lang en
uv run logops optimize           # khuyến nghị so với mục tiêu tiết kiệm
```

Báo cáo (gồm mọi trang dashboard) cũng xuất được từ thanh bên dashboard, mục **Xuất báo cáo**:
báo cáo tạo ở chế độ nền. File HTML mở được khi không có mạng; PDF cần Microsoft Edge hoặc Google
Chrome.

## Các module

| # | Module | Kết quả |
|---|---|---|
| 1 | `data_platform` | Kho Parquet + DuckDB, 69 quy tắc chất lượng dữ liệu, báo cáo chất lượng dữ liệu |
| 2 | `metrics` | 21 KPI (SCOR) theo kỳ và nhóm, định nghĩa bằng lời |
| 3 | `analysis` | Cầu lợi nhuận, ma trận tuyến, năng lực đội xe, chuẩn giao hàng, nhận xét theo quy tắc |
| 4 | `dashboard` | Streamlit: 9 trang, điểm chính theo mức ưu tiên, đơn vị và diễn giải trên mọi biểu đồ |
| 5 | `optimize` | Quy mô đội xe, giá cước tuyến, kiểm tra giao trễ, cải tiến quy trình dữ liệu |
| 6 | `reports` | Một báo cáo gồm mọi trang: HTML responsive hoặc PDF dàn trang (bìa, mục lục, danh mục hình và bảng, tóm tắt điều hành) |

Đánh giá từng module: [docs/reviews/](docs/reviews/). Kịch bản trình bày khi phỏng vấn:
[docs/demo-script.vi.md](docs/demo-script.vi.md).

## Cài đặt

1. **Cài [uv](https://docs.astral.sh/uv/)** và các thư viện:
   ```bash
   uv sync
   ```
2. **Tải bộ dữ liệu** — [Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database)
   trên Kaggle — và giải nén 14 file CSV vào `dataset/` (dữ liệu không được phân phối lại trong repo này).
3. **Dựng kho dữ liệu:**
   ```bash
   uv run logops build
   ```

## Phát triển

```bash
uv run pytest                    # chạy toàn bộ test
uv run pytest -m "not slow"      # chỉ unit test (không cần dữ liệu thật)
uv run ruff check . && uv run ruff format .
```
