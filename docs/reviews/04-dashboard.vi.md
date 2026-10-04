# Đánh giá · Module 4: `dashboard`

> CRISP-DM pha 6 (Triển khai) · Bản tiếng Anh: [04-dashboard.md](04-dashboard.md)
> · Spec: [SPEC-dashboard.vi.md](../../SPEC-dashboard.vi.md) · Tổng quan: [SUMMARY.vi.md](../SUMMARY.vi.md)
> **Trạng thái:** xong 03/10/2026, chưa commit · **Quy tắc:** chỉ ghi sự thật đã kiểm chứng.

## 1. Bối cảnh

Dashboard Streamlit + Plotly để Giám đốc Logistics tự xem. Chủ dự án duyệt bản nháp component kèm ba
điều chỉnh: **tiếng Việt mặc định, có nút chuyển tiếng Anh**, **mọi trang và component đều
responsive**, giữ cả trang *Giao hàng & dịch vụ* lẫn phần định nghĩa KPI. Chi tiết bố cục chủ dự án
sẽ chỉnh sau khi xem thành phẩm.

## 2. Output so với spec

| Output | Kết quả | Bằng chứng |
|---|---|---|
| 8 trang: Tổng quan, Lợi nhuận, Khách hàng & khu vực, Tuyến & mạng lưới, Giao hàng & dịch vụ, Đội xe & năng suất, Nhiên liệu, Dữ liệu & định nghĩa | ✅ 27 biểu đồ, 6 bảng, có ô số ở mọi trang | Mọi trang chạy được ở cả hai ngôn ngữ (16 test) |
| Nhận xét đặt cạnh biểu đồ liên quan | ✅ Tổng quan hiện toàn bộ (lọc theo mức); mỗi trang hiện nhận xét đúng chủ đề | — |
| Nút chuyển VI/EN | ✅ Nút ở thanh bên; 174 nhãn mỗi ngôn ngữ, số định dạng theo ngôn ngữ (1.234,5 / 1,234.5), trục ngày tiếng Việt dạng MM/YYYY | Bộ khóa nhãn giống nhau ở hai ngôn ngữ (test) |
| Responsive | ✅ Cột tự xếp chồng trên màn hẹp; biểu đồ giãn theo khung; danh sách dài dùng cột ngang; bảng rộng cuộn ngang | Đã xem ảnh chụp từng trang ở 1440 px và 390 px |
| Dashboard không tự tính số | ✅ Đọc `analysis_bundle()`, `kpi()` và `analysis/service.py` mới; kết nối chỉ đọc chỉ mở trong `dashboard/data.py` | Không có SQL trong code dashboard (test) |
| Số khớp với lớp phân tích | ✅ | Ô doanh thu, đóng góp, biên bằng lãi lỗ năm đọc riêng (test) |
| Mỗi trang dưới 3 giây khi đã cache | ✅ | Test đo lần chạy lại từng trang, cả 16 lượt trang × ngôn ngữ đều dưới 3 giây |
| Lệnh `logops dashboard` | ✅ Mở trình duyệt ở cổng 8501 | — |

**Test:** 21 test mới (20 cho dashboard, 1 cho analysis); tổng 114, tất cả đều pass; `ruff` sạch.

**Bổ sung vào lớp phân tích cho dashboard** (để dashboard vẫn không chứa SQL): `analysis/service.py`
(đúng giờ theo khung, theo tháng và thành phố, thời gian chờ theo loại, trạng thái đội xe, các xe
không chạy chuyến nào, năng suất từng xe, đóng góp mỗi ngày kèm trung bình 30 ngày, phạm vi ngày của
dữ liệu) và kỳ *ngày* trong `profit.py`.

## 3. Kiểm tra giao diện: lỗi phát hiện và đã sửa

Đã chụp và xem từng trang ở độ rộng máy tính (1440 px) và điện thoại (390 px) trước khi đóng module.

| Lỗi | Cách sửa |
|---|---|
| Đường biên và giá nhiên liệu bị răng cưa | Phép nối làm xáo thứ tự tháng: sắp xếp lại ở lớp phân tích, thêm test chuỗi thời gian đúng thứ tự |
| Bảng lãi lỗ hiện "None" ở kỳ không có kỳ trước để so | Hiện "—" |
| Ô đơn vị kinh tế ghi "so với năm trước" nhưng thực ra so với năm đầu | Nay ghi "so với 2022" (năm đầu của khoảng chọn) |
| Trục ngày ở bản tiếng Việt hiện tên tháng tiếng Anh | Trục ngày tiếng Việt dùng MM/YYYY |
| Nhãn số bị cắt ở đầu cột ngang; nhãn Los Angeles đè lên tên thành phố | Nới rộng trục ra ngoài cột dài nhất |
| Nhãn p95 và p99 (73 và 75 xe) in đè lên nhau, nằm dưới đường dữ liệu | Chuyển tên các vạch tham chiếu vào chú giải |
| Biểu đồ lô đi/lô đến bị ẩn bớt tên thành phố trên điện thoại | Đổi sang cột ngang |
| Trạng thái xe, nhóm SCOR, tên phân khúc còn tiếng Anh ở bản tiếng Việt | Đã dịch |
| Ô số xe dùng mũi tên thay đổi để hiện chữ | Hiện giá trị "73 / 120" kèm chú thích |

## 4. Lưu ý khi trình bày

- **Lần tải đầu mất khoảng 10 giây** (tính `analysis_bundle()` đo được 10,2–10,3 giây); sau đó mỗi
  trang dưới 3 giây. Chọn **khoảng thời gian mới** sẽ tính lại (khoảng 10 giây nữa). **Mở dashboard
  một lần trước buổi demo.**
- **Bản đồ Hoa Kỳ cần kết nối internet**: Plotly tải hình các bang khi vẽ bản đồ. Các biểu đồ khác
  chạy được khi không có mạng.
- Các ô ở trang Tổng quan là **năm cuối của khoảng chọn** so với năm trước đó (dòng chú thích ghi rõ
  năm nào), không phải toàn bộ khoảng.
- Lợi nhuận vẫn là **đóng góp trước lương tài xế và chi phí chung** (dữ liệu không có hai khoản này).

## 5. Không làm (theo thiết kế)

| Không làm | Lý do |
|---|---|
| Khuyến nghị có số tiền tiết kiệm | Thuộc `optimize` (làm lại sau); sẽ thêm một trang |
| Nút xuất PDF/HTML | Thuộc `reports` |
| Đăng nhập, triển khai lên máy chủ | Chạy trên máy để demo |

## 6. Bàn giao

- **Optimize** (làm lại từ `feature/optimize`): trang khuyến nghị cắm vào theo cùng mẫu
  `pages.py` / `i18n.py`.
- **Reports**: dùng lại `charts.py` (cùng bảng màu và định dạng số) cho báo cáo HTML.

## 7. Chạy lại

```powershell
python -m uv run logops build        # một lần, nếu chưa có data/warehouse.duckdb
python -m uv run logops dashboard    # mở http://localhost:8501
python -m uv run pytest tests/dashboard -m "slow or not slow"   # 20 test của module này
```

## 8. Điều chỉnh sau lần rà soát đầu của chủ dự án (03/10/2026)

| Góp ý | Điều chỉnh |
|---|---|
| Tổng quan chỉ xem được năm cuối | Thêm nút chọn kỳ: *Cả giai đoạn* hoặc từng năm; chọn một năm thì so với năm trước khi cả hai đều là năm trọn vẹn trong khoảng chọn |
| Các ô có kích thước khác nhau | Ô KPI dựng bằng lưới HTML (`dashboard/ui.py`): cùng kích thước trong một hàng, 4 → 2 → 1 cột khi màn hẹp dần |
| "Giao trong khung ±2 giờ" và "xe bận (95% số ngày)" khó hiểu | Dùng tên KPI logistics, mỗi ô có một dòng định nghĩa: **Giao hàng đúng hẹn (OTD)**, thời gian chờ bình quân, chuyến hoàn thành, **hiệu suất sử dụng đội xe** (số xe có chuyến bình quân mỗi ngày ÷ số xe sở hữu, 55,1%). Không hiển thị OTIF: dữ liệu không có số lượng giao so với số lượng đặt nên không đo được phần *đủ hàng* |
| "Biên" là gì | Gọi thống nhất là **biên đóng góp**, ghi công thức dưới biểu đồ: (doanh thu − nhiên liệu − bảo dưỡng − bồi thường) ÷ doanh thu, chưa trừ lương tài xế và chi phí chung |
| Nhận xét chia nhiều ô màu | Mỗi trang một khung nhận xét, mức khẩn nhất lên trước, các dòng *thông tin* gom vào "xem thêm" |
| Trình bày chưa gọn | Biểu đồ đặt trong thẻ trắng có tiêu đề bên trong; nền trang sáng hơn; ẩn thanh công cụ; cỡ tiêu đề đặt trong `.streamlit/config.toml`; nhãn số nằm trong đầu thanh khi đủ chỗ |

Số liệu trang Tổng quan lấy từ hàm mới `analysis/service.scorecard()` (tiền từ bảng lãi lỗ, giao
hàng từ lớp KPI, hiệu suất đội xe từ số xe bận mỗi ngày), nên dashboard vẫn không tự tính số. Ở trang
Đội xe, cột `utilization_rate` của dữ liệu được ghi rõ là cột không có định nghĩa (vượt 100%), chỉ
dùng để so sánh giữa các xe.

**Test:** tổng 116, tất cả pass (scorecard khớp lãi lỗ năm và số xe bận; ô KPI khớp scorecard; khung
nhận xét và lưới ô KPI có test riêng).

## 9. Viết lại phần nhận xét (04/10/2026)

Góp ý: danh sách nhận xét lặp lại "cần hành động" ở mỗi dòng, không nói rõ tốt hay xấu và ảnh
hưởng thế nào, và tên "cần hành động" chưa rõ nghĩa.

| Thay đổi | Chi tiết |
|---|---|
| Ba tab | **Ưu tiên xử lý** · **Cần theo dõi** · **Tham khảo**, kèm số lượng; không lặp lại mức độ ở từng nhận xét. Trang chỉ có một mức thì ghi mức đó thành dòng chú thích thay vì một tab đơn |
| Mỗi nhận xét rõ ràng | Tiêu đề dễ hiểu, **đánh giá** (tích cực, tiêu cực, rủi ro, trung tính), rồi *diễn biến*, *ảnh hưởng* (*ý nghĩa* với mục tham khảo) và *đề xuất* cho các mục ưu tiên và theo dõi |
| Ảnh hưởng bằng tiền khi dữ liệu cho phép | Đội xe: 40 xe vượt nhu cầu ngày bận nhất, 28 xe chưa chạy chuyến nào vẫn tốn 1,40 triệu USD bảo dưỡng (dữ kiện mới trong bundle). Lợi nhuận: nếu giá nhiên liệu về lại mức 2022, lợi nhuận đóng góp giảm khoảng 4,12 triệu USD mỗi năm (phần giá nhiên liệu của cầu lợi nhuận) |
| Kiểm chứng trước khi viết | "Phụ phí nhiên liệu không đổi theo giá nhiên liệu": phụ phí mỗi dặm 0,245 USD cả 2022, 2023, 2024 trong khi giá nhiên liệu bình quân giảm từ 4,20 xuống 3,65 USD/gallon |
| Một nguồn cho nội dung | Nhãn mức độ, đánh giá, chủ đề và các mục nằm trong `analysis/insights.py`, dùng chung cho dashboard, lệnh CLI và `docs/03-analysis-insights` (nay mỗi nhận xét một khối) |

Cố ý không quy ra tiền: chạy rỗng sau các lô một chiều và giữa hai chuyến, vì dữ liệu không ghi quãng
đường này. **Test:** tổng 118, tất cả pass (mọi nhận xét có đánh giá, diễn biến, ảnh hưởng, và có đề
xuất nếu thuộc mức ưu tiên hoặc theo dõi; nội dung đổi theo mức độ).

## 10. Rà soát lần hai: văn phong, đơn vị, bảng, chuẩn đo giao hàng (04/10/2026)

Báo cáo điều hành mẫu chủ dự án cung cấp chỉ được tham khảo cách trình bày (chip đơn vị trên mỗi biểu
đồ, hộp diễn giải bên dưới, cột đánh giá trong bảng); không sao chép dữ liệu hay nhận diện thương hiệu.

| Góp ý | Điều chỉnh |
|---|---|
| Ô chọn khoảng thời gian lỗi thao tác | Form gồm *Từ ngày*, *Đến ngày* và nút **Áp dụng**: chọn ngày không làm trang tải lại; có test bằng AppTest (chỉ chọn ngày thì chưa đổi, bấm Áp dụng mới đổi) |
| Điểm chính chưa chia tab ở mọi trang | Mọi trang dùng chung khung nhận xét chia tab |
| Biên theo bang không có đơn vị, không rõ nghĩa | Chip đơn vị, tên bang đầy đủ, hộp diễn giải nêu bang cao nhất và thấp nhất |
| Đóng góp mỗi ngày và đường trung bình 30 ngày khó hiểu | Bỏ: số liệu theo ngày chỉ là nhiễu, không thêm gì so với biểu đồ theo kỳ và lũy kế |
| Lưới "số tuyến trong mỗi ô" không chỉ ra việc cần làm | Thay bằng **bảng đánh giá tuyến**: từng tuyến có số chuyến, doanh thu, lợi nhuận, biên, chênh lệch biên so với bình quân, mức sản lượng và mức biên, đánh giá và hướng xử lý, xếp theo mức ưu tiên, lọc được |
| Biểu đồ thiếu đơn vị | Mọi thẻ biểu đồ có "Đơn vị: …" và tiêu đề trục ở trục mang giá trị |
| Khung ±2 giờ có hợp lý với chuyến 3–4 ngày? | Kiểm tra trên dữ liệu: thời điểm giao rơi từ sớm 3 giờ đến muộn 6 giờ, phân bố đều, **như nhau với chuyến dưới 1 ngày, 1–2 ngày và trên 2 ngày** (đạt 44,5% / 44,8% / 43,9% theo khung ±2 giờ). Trang nay so sánh bốn chuẩn: trong khung ±2 giờ 44,6%, không trễ giờ hẹn 33,3%, trễ không quá 2 giờ 55,6%, đúng ngày hẹn 91,2% |
| Tên trang | Đổi tên (xem spec) |
| Mục tham khảo ở trang đội xe tối nghĩa | Viết lại bằng lời thường (nhu cầu xe biến động ngẫu nhiên, không theo mùa; quy mô đội xe tính theo số ngày cần đảm bảo) |
| "Cách đọc" → diễn giải; "xe bận" | Hộp ghi chú nay là "Diễn giải" với câu đầy đủ kèm số liệu; "xe bận" → "xe hoạt động" |
| Nhãn năng suất khó hiểu | Tên đầy đủ kèm dòng định nghĩa (ví dụ quãng đường bình quân mỗi xe mỗi tháng = tổng số dặm ÷ số tháng-xe có chạy chuyến); doanh thu mỗi xe mỗi tuần nay tính theo khoảng thời gian đã chọn |
| Tên biến trên màn hình (`utilization_rate`, tên bảng, mã quy tắc) | Đổi sang tên ngữ nghĩa ở mọi nơi (biểu đồ chất lượng dữ liệu, biểu đồ đội xe, định nghĩa KPI) |
| Bảng không lọc được như Excel | Mỗi bảng có ô lọc chọn nhiều giá trị cho từng cột phân loại và dòng "hiển thị n / N dòng"; số giữ dạng số nên sắp xếp đúng (hiển thị theo định dạng số của trình duyệt) |
| Bảng xe không chạy chuyến | Có số thứ tự; bỏ cột giờ dừng (không có ý nghĩa với xe chưa từng chạy); tiêu đề nêu số xe; hộp diễn giải nêu chi phí bảo dưỡng và lý do cần rà soát |
| Văn phong | Dùng thuật ngữ chuyên ngành (chi phí nhiên liệu thay cho chi tiêu nhiên liệu, chi phí bồi thường sự cố, lợi nhuận đóng góp…) |
| Định nghĩa KPI | Tên KPI theo nút ngôn ngữ; công thức viết bằng chữ; giải thích cột giá trị (KPI của toàn đội trong khoảng thời gian đang chọn) và hiển thị kèm đơn vị |

**Test:** tổng 119, tất cả pass; `ruff` sạch.

## 11. Rà soát lần ba (04/10/2026)

| Câu hỏi | Trả lời và điều chỉnh |
|---|---|
| "Chuyên tuyến" khác gì "Hợp đồng"? | Theo nghĩa ngành vì dữ liệu chỉ ghi loại khách: *Hợp đồng vận chuyển* = giá ký trước, xe lấy từ đội chung; *Xe chuyên trách* = xe và tài xế dành riêng cho một khách. Đã đổi tên và giải thích dưới biểu đồ. Trong dữ liệu này ba phân khúc có doanh thu mỗi dặm và biên như nhau |
| Vì sao tỷ lệ điều xe giữ quanh 95%? | Có thay đổi nhẹ (95,0–95,6% tùy khoảng thời gian), nhưng bằng đúng mức kỳ vọng nếu **giao chuyến ngẫu nhiên** (kỳ vọng 95,4%, thực tế 95,5%): dữ liệu không có ghép chuyến nối tiếp. Đã thêm mốc so sánh vào phân tích, nhận xét và diễn giải biểu đồ |
| Vì sao tuyến biên trên 50% lại "cân nhắc ngừng"? | Mức Cao/Vừa/Thấp là tương đối, và mọi tuyến đều có lãi đóng góp (thấp nhất 50,4%). Đổi hướng xử lý thành **Rà soát giá cước**, nhận xét nêu biên tuyến thấp nhất, ghi chú bảng giải thích cách chia mức. Giữ cột biên vì là căn cứ đánh giá |
| Chạy rỗng: xử lý ngay hay để tối ưu? | Chuyển sang `optimize`: dữ liệu không có quãng chạy rỗng và tọa độ, nên phần tiết kiệm phải tính bằng mô phỏng điều phối (giao lô kế tiếp cho xe đang ở thành phố lấy hàng) |
| Trục biểu đồ độ lệch "-3…-2" | Trục giờ liền mạch (−3 … +6), tô nền vùng khung ±2 giờ |

**Test:** 119, tất cả pass.

## 12. Sửa bố cục (04/10/2026)

- **Tràn chữ:** kiểm tra tự động ở 1440, 1280, 1024, 768 và 390 px; số trong ô KPI tràn ra ngoài ở khoảng 1024 px khi mở thanh bên. Lưới ô KPI và thẻ nhận xét nay chia cột theo độ rộng vùng nội dung (CSS container query) và số dài được xuống dòng; nhãn cột ngang chỉ ghi số (đơn vị ở tiêu đề thẻ); bảng nhiều chữ (định nghĩa KPI, mức tin cậy dữ liệu) chuyển sang bảng HTML có ngắt dòng thay vì bị cắt; bảng tuyến dành chỗ rộng hơn cho cột chữ.
- **Tab:** giữ tab đang chọn khi trang chạy lại (trước đây bị nhảy về tab đầu).
- **Điểm chính:** đóng/mở được, tiêu đề ghi số lượng từng mức, có chú thích: màu viền là đánh giá (đỏ tiêu cực, cam rủi ro, xanh lá tích cực, xám trung tính), tab là mức độ. Đã kiểm tra: màu viền của mọi nhận xét khớp nhãn đánh giá.
- **Đơn vị:** "triệu USD" rút gọn thành "tr USD" ở mọi nơi (dashboard và tài liệu sinh tự động).
- **Lỗi đã sửa:** bảng định nghĩa KPI có tiêu đề cột lệch thứ tự với dữ liệu (đã có test).
