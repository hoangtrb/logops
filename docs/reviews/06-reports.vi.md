# Đánh giá · Module 6: `reports`

> CRISP-DM pha 6 (Triển khai) · Bản tiếng Anh: [06-reports.md](06-reports.md) · Spec:
> [SPEC-reports.vi.md](../../SPEC-reports.vi.md) · Tổng quan: [SUMMARY.vi.md](../SUMMARY.vi.md)
> **Trạng thái:** xong 04/10/2026, chưa commit · **Quy tắc:** chỉ ghi sự thật đã kiểm chứng.

## 1. Output so với spec

| Output | Kết quả | Bằng chứng |
|---|---|---|
| 5 loại báo cáo: tổng quan điều hành, kết quả kinh doanh & tuyến, chất lượng giao hàng, nhiên liệu, đội xe | ✅ | Mọi loại tạo được (test) |
| HTML tự chứa | ✅ Nhúng Plotly một lần (~4,7 MB mỗi file); không tải script bên ngoài | Test: không có `<script src=` |
| PDF không thêm thư viện | ✅ In headless bằng Edge hoặc Chrome, biểu đồ dàn theo khổ A4; thông báo rõ nếu không có trình duyệt | Test (bỏ qua khi không có trình duyệt); đã xem từng trang PDF |
| Số liệu giống dashboard | ✅ Cùng hàm phân tích và optimize, cùng biểu đồ và ô số | Test: báo cáo tổng quan tiếng Anh năm 2024 hiện đúng doanh thu và OTD của dashboard |
| Lệnh CLI `logops report` | ✅ Ghi vào `reports/output/` (đã git-ignore) | Dùng để tạo các báo cáo mẫu |
| Xuất từ dashboard | ✅ Thanh bên "Xuất báo cáo": loại, HTML/PDF, theo khoảng thời gian và ngôn ngữ đang chọn → tải về | Test: thanh bên tạo được báo cáo HTML |
| Báo cáo An toàn & tài xế | ❌ Bỏ (ngoài phạm vi) | — |

**Test:** 9 test mới (8 cho báo cáo, 1 cho nút xuất); tổng 157, tất cả pass; `ruff` sạch.

## 2. Số đo được

- Tạo một báo cáo mất 10–15 giây (tính bộ phân tích); in PDF thêm khoảng 2 giây.
- Bố cục PDF: biểu đồ không bị tách, bảng sang trang có lặp lại tiêu đề cột, mỗi phần bắt đầu trang
  mới.

## 3. Lưu ý

- PDF cần máy có Microsoft Edge hoặc Google Chrome (máy này có cả hai).
- Khuyến nghị trong báo cáo tính trên toàn bộ dữ liệu 2022–2024, không theo kỳ báo cáo (có ghi rõ
  trong báo cáo).

## 4. Chạy lại

```powershell
python -m uv run logops report --type executive --lang vi --format pdf
python -m uv run pytest tests/reports -m "slow or not slow"
```

## 5. Điều chỉnh 04/10/2026: một báo cáo gồm mọi trang

- Một báo cáo thay cho năm loại: mỗi trang dashboard là một tab, do chính code của trang vẽ qua bộ
  dựng HTML, nên không thể lệch với dashboard.
- Đã kiểm tra: HTML ở 1366 px và 390 px (không tràn ngang); PDF 48 trang A4 cho 2022–2024, mỗi
  trang dashboard sang tờ mới, chân trang có tên báo cáo, ngày xuất và trang x / y.
- Xuất từ dashboard chạy trên luồng riêng, nút Tải về đổ màu theo tiến độ.
- Tối: làm lại bố cục in (bìa, mục lục, đánh số mục, bảng rộng in trang ngang, không cắt dữ
  liệu): 43 trang. Test: tổng 156 sau khi thêm test giải thích tiết kiệm; trước đó: 155, tất cả pass (viết lại test báo cáo cho một báo cáo; thêm test bảo đảm khi vẽ báo
  cáo không chạm tới Streamlit ở luồng khác).
