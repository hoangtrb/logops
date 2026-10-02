# Logistics Ops Optimizer

> Bản tiếng Anh: [README.md](README.md) · Các module: [CAPABILITY-MAP.vi.md](CAPABILITY-MAP.vi.md) · Lộ trình: [tasks/roadmap.vi.md](tasks/roadmap.vi.md)
> Tiến độ: [docs/00-project-journal.vi.md](docs/00-project-journal.vi.md) · Phương pháp: [docs/00-analytical-approach.vi.md](docs/00-analytical-approach.vi.md)

Biến dữ liệu đội xe thô thành các quyết định tiết kiệm chi phí cho mạng lưới phân phối: chi phí
phục vụ, giao hàng đúng giờ, hiệu quả nhiên liệu và mức sử dụng đội xe, trình bày trên dashboard
và báo cáo PDF/HTML xuất bằng một cú nhấp.

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
