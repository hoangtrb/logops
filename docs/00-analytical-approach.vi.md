# 00 · Cơ sở phân tích và định hướng tối ưu

> Bản tiếng Anh: [00-analytical-approach.md](00-analytical-approach.md) · Nhật ký dự án: [00-project-journal.vi.md](00-project-journal.vi.md)
> **Trạng thái:** phần dữ liệu (§3) đã triển khai. Các phần §4–§10 là phương pháp *đã chọn và sẽ
> triển khai*; khi làm thật, nếu số liệu buộc phải đổi hướng thì file này được cập nhật kèm lý do.

Tài liệu này trả lời 4 câu hỏi cho từng bước phân tích:
1. Dựa trên **lý thuyết hoặc khung** nào?
2. Dùng **mô hình hoặc kỹ thuật** nào?
3. **Vì sao** chọn nó?
4. **Vì sao không** chọn phương án khác?

---

## Tóm tắt một trang

| Câu hỏi của giám đốc | Lý thuyết / khung | Mô hình / kỹ thuật | Vì sao không dùng phương án khác |
|---|---|---|---|
| Cả dự án đi theo trình tự nào? | **CRISP-DM** + thang phân tích (mô tả → chẩn đoán → dự báo → đề xuất) | 6 pha, mỗi pha có sản phẩm | KDD/SEMMA thiếu pha hiểu nghiệp vụ và triển khai |
| Đo cái gì? | **SCOR** (độ tin cậy, chi phí, hiệu quả tài sản) + **cây KPI** | View KPI bằng SQL | KPI tự chọn dễ thiếu hoặc trùng lặp |
| Dữ liệu có tin được không? | **6 chiều chất lượng dữ liệu (DAMA)** | Quy tắc SQL, *đánh dấu* chứ không xóa | Xóa dòng lỗi làm mất dấu vết và lệch số |
| Tuyến/khách nào lỗ? | **Chi phí theo hoạt động (ABC)**, **cost-to-serve**, **biên đóng góp** | Xếp hạng lợi nhuận tuyến, đường cong "cá voi", Pareto | ABC đầy đủ cần chi phí chung, mà dữ liệu không có |
| Vì sao giao trễ? | **Phân tích nguyên nhân** + **học có giám sát** | **Gradient boosting** + SHAP/permutation importance, chia train/test theo thời gian | Mạng nơ-ron kém hơn trên dữ liệu bảng; hồi quy logistic chỉ làm mốc so sánh |
| Có lãng phí nhiên liệu? | **Benchmarking** + **thống kê bền vững** | Trung vị + MAD/IQR, so trong cùng nhóm | Trung bình ± độ lệch chuẩn bị chính các điểm bất thường kéo lệch |
| Đội xe có thừa không, xe nào nên thay? | **Mức sử dụng tài sản**, **chi phí vòng đời / tuổi thọ kinh tế** | Quy mô đội xe theo phân vị nhu cầu, xu hướng chi phí/dặm theo tuổi xe | Bảo dưỡng dự đoán bằng ML cần dữ liệu cảm biến, mà dữ liệu không có |
| Tiết kiệm được bao nhiêu? | **Ước tính thận trọng** | Đưa điểm kém về *trung vị*, không về mức tốt nhất; không cộng trùng | Lấy mức tốt nhất làm chuẩn sẽ hứa quá |
| AI giúp gì? | **LLM dựa trên dữ liệu có sẵn (grounding)** | Claude diễn giải số do code tính; câu hỏi → SQL chỉ đọc | Để LLM tự tính số dễ sinh số bịa |

---

## 1. Khung tổng thể

### 1.1 CRISP-DM

CRISP-DM (Cross-Industry Standard Process for Data Mining, Chapman và cộng sự, 2000) gồm 6 pha:

| Pha | Sản phẩm trong dự án |
|---|---|
| Hiểu nghiệp vụ | `docs/01` |
| Hiểu dữ liệu | báo cáo DQ |
| Chuẩn bị dữ liệu | kho DuckDB + view KPI |
| Mô hình hóa | 4 engine |
| Đánh giá | `docs/05` |
| Triển khai | dashboard + báo cáo |

**Vì sao chọn:**
- Pha đầu tiên là *hiểu nghiệp vụ*, tức bắt đầu từ câu hỏi của giám đốc chứ không từ dữ liệu.
  Pha cuối là *triển khai*, tức kết quả phải đến tay người dùng. Đây chính là điều một giám đốc
  logistics quan tâm.
- Quy trình có vòng lặp: nếu số liệu ở pha 2 làm thay đổi mục tiêu thì quay lại pha 1. Vì vậy
  các mục tiêu trong `docs/01` §5 được ghi là *tạm thời*.

**Vì sao không dùng khung khác:**
- **KDD** (Fayyad, 1996) và **SEMMA** (SAS) tập trung vào khai phá dữ liệu: chọn mẫu, khám phá,
  mô hình hóa. Hai khung này không có pha nghiệp vụ và pha triển khai rõ ràng.
- **TDSP** (Microsoft) đầy đủ nhưng nặng về quy trình nhóm và hạ tầng Azure, thừa cho một dự án
  3 ngày.

### 1.2 Thang giá trị phân tích

Dự án đi qua đủ 4 bậc của thang phân tích. Thang này được Gartner phổ biến, và Davenport &
Harris (2007) mô tả tương tự.

| Bậc | Câu hỏi | Ví dụ trong dự án |
|---|---|---|
| Mô tả (descriptive) | Đã xảy ra gì? | KPI: chi phí/dặm, % đúng giờ |
| Chẩn đoán (diagnostic) | Vì sao? | Phân rã chi phí, yếu tố gây trễ |
| Dự báo (predictive) | Sẽ xảy ra gì? | Rủi ro trễ của từng lô hàng |
| Đề xuất (prescriptive) | Nên làm gì? | Khuyến nghị kèm $ tiết kiệm |

**Đây là điểm khác biệt so với một dashboard báo cáo thông thường.** Phần lớn dashboard dừng ở
bậc mô tả, còn dự án này kết thúc ở bậc đề xuất: mỗi khuyến nghị có hành động cụ thể và số tiền.

---

## 2. Khung KPI: đo cái gì và vì sao

### 2.1 Mô hình SCOR

Mô hình SCOR (Supply Chain Operations Reference, do ASCM/APICS quản lý) chia hiệu quả chuỗi
cung ứng thành 5 thuộc tính. Dự án ánh xạ 4 lĩnh vực tối ưu vào các thuộc tính này:

| Thuộc tính SCOR | Lĩnh vực trong dự án | KPI chính |
|---|---|---|
| **Độ tin cậy** (Reliability) | Giao đúng giờ | % đúng giờ, giờ chờ (detention) |
| **Chi phí** (Cost) | Cost-to-serve, nhiên liệu | Chi phí/dặm, chi phí nhiên liệu/dặm, biên lợi nhuận tuyến |
| **Hiệu quả tài sản** (Asset management) | Đội xe & bảo dưỡng | Mức sử dụng xe, chi phí bảo dưỡng/dặm, giờ dừng |
| Khả năng đáp ứng (Responsiveness) | Gián tiếp qua thời gian vận chuyển | Thời gian chuyến so với kế hoạch |
| Tính linh hoạt (Agility) | Không xét | Dữ liệu không có kịch bản đột biến nhu cầu |

**Vì sao chọn SCOR:** đây là ngôn ngữ chung của ngành chuỗi cung ứng. Khi giám đốc nghe "độ tin
cậy và chi phí phục vụ", họ biết ngay đang nói về điều gì. Một bộ KPI tự đặt ra dễ bị thiếu (bỏ
sót hiệu quả tài sản) hoặc trùng (hai chỉ số cùng đo một thứ).

### 2.2 Cây KPI (phân rã kiểu DuPont)

Thay vì chỉ báo "chi phí/dặm tăng", ta tách nó thành các thành phần cộng lại được:

```
Chi phí / dặm  =  nhiên liệu/dặm  +  bảo dưỡng/dặm  +  tài xế/dặm  +  an toàn/dặm
                      │                                  │
             giá nhiên liệu ÷ MPG             số giờ × đơn giá giờ (ước tính)
                      │
             MPG ← thời gian chạy không tải, loại xe, tuyến
```

**Vì sao:** cây KPI chỉ thẳng vào *đòn bẩy* để hành động. Nếu chi phí/dặm cao do giá nhiên liệu
thì giải pháp là chính sách mua nhiên liệu. Nếu do MPG thấp thì giải pháp là đào tạo tài xế
hoặc giảm chạy không tải. Cách tiếp cận này mượn từ phân rã DuPont trong phân tích tài chính.

---

## 3. Hiểu và chuẩn bị dữ liệu (đã triển khai)

### 3.1 Các chiều chất lượng dữ liệu

Khung DAMA-DMBOK định nghĩa các chiều chất lượng dữ liệu. Mỗi quy tắc DQ của dự án kiểm một chiều:

| Chiều | Câu hỏi | Quy tắc trong dự án |
|---|---|---|
| Đầy đủ (Completeness) | Có thiếu giá trị bắt buộc không? | `fk_missing`, % null theo cột |
| Duy nhất (Uniqueness) | Có bản ghi trùng không? | `pk_unique`, bỏ dòng trùng tuyệt đối |
| Hợp lệ (Validity) | Giá trị có nằm trong miền hợp lý không? | Kiểu dữ liệu (lúc nạp), `range` |
| Nhất quán (Consistency) | Các bảng có khớp nhau không? | `fk_orphan`, `amount_mismatch`, `agg_drift`, `geo_mismatch` |
| Chính xác (Accuracy) | Có đúng với thực tế không? | `time_order` (giao trước khi lấy là vô lý) |
| Kịp thời (Timeliness) | Dữ liệu có cũ không? | Không xét: dữ liệu là ảnh chụp lịch sử |

**Đánh dấu, không xóa.** Mỗi dòng có cột `dq_issues` liệt kê lỗi của nó, và bảng `dq_findings`
tổng hợp toàn bộ.
- **Vì sao:** xóa dòng lỗi làm lệch số mà không ai biết. Ví dụ, xóa các chuyến thiếu `driver_id`
  sẽ làm tổng chi phí nhiên liệu thấp đi. Việc đánh dấu để người dùng ở bước sau tự chọn: tính
  chi phí thì giữ dòng, xếp hạng tài xế thì loại dòng.
- Ngoại lệ duy nhất là dòng trùng tuyệt đối. Những dòng này bị bỏ, và số dòng bỏ được ghi lại.

**Báo lỗi khi sai kiểu, không ép kiểu ngầm.** Khi nạp, mỗi giá trị được kiểm có ép được sang
kiểu khai báo không. Một giá trị sai sẽ dừng build và chỉ đúng `bảng.cột`.
- **Vì sao:** nếu để công cụ tự đoán kiểu như mặc định của pandas, một ô bẩn khiến cả cột số
  thành chữ. Khi đó các phép tính phía sau sai hoặc chạy chậm mà không có cảnh báo.

### 3.2 Mô hình hóa chiều (Kimball)

Dữ liệu được tổ chức theo **lược đồ hình sao** (Kimball & Ross, 2013):

- **Bảng sự kiện (fact):** chứa các con số phát sinh theo thời gian.
  `trips`, `loads`, `fuel_purchases`, `delivery_events`, `maintenance_records`, `safety_incidents`.
- **Bảng chiều (dimension):** chứa thông tin mô tả để lọc và nhóm.
  `drivers`, `trucks`, `trailers`, `routes`, `customers`, `facilities`, cộng thêm chiều thời gian.

**Vì sao:** câu hỏi kinh doanh luôn có dạng *"đo X, theo Y, trong khoảng thời gian Z"*, ví dụ
chi phí theo tuyến theo tháng. Lược đồ hình sao trả lời đúng dạng câu hỏi đó, dễ đọc với người
không chuyên, và là chuẩn của các công cụ BI.

**Vì sao không chuẩn hóa sâu (3NF) hoặc gộp thành một bảng phẳng lớn:**
- 3NF tối ưu cho việc *ghi* dữ liệu, không cho *phân tích*, và mỗi truy vấn phải nối nhiều bảng.
- Một bảng phẳng lặp lại dữ liệu và khó mở rộng.

### 3.3 Công nghệ dữ liệu

| Chọn | Vì sao | Vì sao không dùng phương án khác |
|---|---|---|
| **DuckDB** | CSDL phân tích chạy ngay trong tiến trình, không cần server. Đọc CSV/Parquet trực tiếp. Dựng 14 bảng trong 4,2 giây | **Spark:** dành cho dữ liệu hàng trăm GB trên cụm máy, với 58 MB chỉ thêm chi phí khởi động. **PostgreSQL:** cần cài server, chậm hơn với truy vấn tổng hợp. **pandas:** tốn bộ nhớ, đoán kiểu ngầm |
| **Parquet** | Lưu theo cột, nén tốt, giữ kiểu dữ liệu | CSV không lưu kiểu, đọc chậm |
| **SQL cho KPI** | Ai biết SQL đều kiểm tra được công thức | Logic chôn trong code Python khó kiểm toán |

**Điểm nói khi phỏng vấn:** cùng mô hình này (Parquet + engine SQL) mở rộng lên dữ liệu thật
của một chuỗi bán lẻ bằng cách đổi engine sang Spark, Databricks hoặc BigQuery. Logic SQL giữ
gần như nguyên vẹn.

---

## 4. Lĩnh vực 1: Cost-to-serve và lợi nhuận tuyến

**Lý thuyết**
- **Chi phí theo hoạt động** (Activity-Based Costing, Kaplan & Cooper, 1998): phân bổ chi phí
  theo *hoạt động thật sự tiêu tốn nguồn lực* (dặm chạy, giờ lái, lần bảo dưỡng), thay vì chia
  đều theo doanh thu.
- **Cost-to-serve và đường cong "cá voi"** (Kaplan & Narayanan, 2001): xếp khách hàng theo lợi
  nhuận tích lũy. Đường cong thường vọt lên trên 100% rồi tụt xuống, nghĩa là một nhóm nhỏ khách
  hàng "ăn" phần lợi nhuận do các khách khác tạo ra.
- **Biên đóng góp** (contribution margin) = doanh thu − chi phí biến đổi. Một tuyến có biên âm
  là tuyến *mỗi chuyến chạy thêm lại lỗ thêm*.

**Kỹ thuật**
- Tính chi phí/dặm theo cây KPI ở §2.2, rồi tính biên đóng góp cho từng tuyến và từng khách hàng.
- Áp dụng nguyên lý **Pareto** (phân loại ABC): xem khoảng 20% tuyến nào tạo ra khoảng 80% lợi
  nhuận hoặc lỗ.
- Với mỗi tuyến lỗ, tính **mức giá hòa vốn** = chi phí/dặm ÷ (1 − biên mục tiêu). Từ đó có
  khoảng cách so với giá hiện tại.

**Hành động đề xuất:** tăng giá, đàm phán lại phụ phí, gộp chuyến, hoặc rút khỏi tuyến.

**Vì sao không làm ABC đầy đủ:** dữ liệu không có lương tài xế và chi phí chung (văn phòng, khấu
hao). Vì vậy:
- Chi phí tài xế được *ước tính* bằng số giờ × đơn giá giờ, và đây là **giả định ghi rõ**.
- Kết quả gọi là *biên đóng góp*, không gọi là *lợi nhuận ròng*. Làm vậy để không hứa quá.

---

## 5. Lĩnh vực 2: Giao đúng giờ và thời gian chờ

**Lý thuyết**
- **OTIF** (On-Time In-Full) là thước đo chuẩn của bán lẻ cho độ tin cậy giao hàng.
- **Phân tích nguyên nhân gốc:** trễ do kho (thời gian chờ ở cửa nhận hàng), do tuyến (quãng
  đường), do khung giờ, hay do tài xế/xe?

**Kỹ thuật**
- **Bậc mô tả và chẩn đoán:** tính % đúng giờ và số giờ chờ theo kho, tuyến, khung giờ, ngày
  trong tuần. Quy giờ chờ ra tiền: giờ chờ × chi phí giờ của xe và tài xế.
- **Bậc dự báo:** mô hình phân loại **gradient boosting** (Friedman, 2001) dự báo xác suất trễ
  của từng lô hàng, dùng các thông tin *biết trước khi xe chạy*: tuyến, kho, khung giờ hẹn, loại
  hàng, trọng lượng, tài xế, tuổi xe.
- **Giải thích mô hình:** dùng **permutation importance** và **SHAP** (Lundberg & Lee, 2017) để
  trả lời "yếu tố nào gây trễ nhiều nhất".

**Vì sao chọn gradient boosting:**
- Đây là dữ liệu dạng bảng, trộn cột số và cột phân loại, có quan hệ phi tuyến và tương tác giữa
  các yếu tố (ví dụ kho X chỉ trễ vào buổi chiều). Gradient boosting xử lý tốt trường hợp này mà
  không cần nhiều xử lý trước.
- Trên dữ liệu bảng, các mô hình cây vẫn vượt mạng nơ-ron (Grinsztajn và cộng sự, 2022).

**Vì sao không dùng phương án khác:**

| Phương án | Lý do |
|---|---|
| Mạng nơ-ron | Cần nhiều dữ liệu, khó giải thích, không tốt hơn trên dữ liệu bảng |
| Hồi quy logistic | Dễ giải thích nhưng bỏ sót tương tác. **Vẫn được dùng làm mốc so sánh**: gradient boosting phải thắng được nó |
| Random forest | Thường kém gradient boosting một chút, và không có lợi thế giải thích hơn |

**Đánh giá mô hình**
- **Chia train/test theo thời gian:** train trên các tháng đầu, test trên các tháng sau. Chia
  ngẫu nhiên sẽ để "tương lai" lọt vào dữ liệu train, làm điểm số đẹp giả tạo.
- **Chống rò rỉ dữ liệu (leakage):** không dùng thông tin chỉ biết *sau* khi giao, như giờ giao
  thực tế hay số phút chờ.
- **Chỉ số:**
  - ROC-AUC (mục tiêu ≥ 0,70) so với mốc ngây thơ (đoán theo tỷ lệ trễ chung).
  - Precision ở nhóm rủi ro cao nhất, vì điều phối viên chỉ can thiệp được một số ít lô mỗi ngày.

**Giới hạn cần nói rõ:** mô hình cho biết *tương quan*, không chứng minh *nhân quả*. Kết luận
kiểu "kho X gây trễ" là giả thuyết để kiểm chứng tại hiện trường, chưa phải sự thật.

**Lưu ý:** scikit-learn chưa có trong danh sách thư viện. Sẽ hỏi bạn trước khi thêm, theo quy
tắc "hỏi trước khi thêm thư viện" trong spec.

---

## 6. Lĩnh vực 3: Hiệu quả nhiên liệu

**Lý thuyết**
- **Benchmarking nội bộ:** so mỗi xe và tài xế với chính đội xe của mình.
- **Thống kê bền vững** (robust statistics): dùng trung vị và **MAD** (độ lệch tuyệt đối trung
  vị), hoặc **IQR** (quy tắc Tukey, 1977), để phát hiện điểm bất thường.

**Vì sao không dùng trung bình ± 3 độ lệch chuẩn:** chính các điểm bất thường kéo trung bình và
độ lệch chuẩn về phía chúng, nên chúng "che" lẫn nhau (Leys và cộng sự, 2013). Phân phối MPG và
thời gian chạy không tải thường lệch, không chuẩn. Trung vị và MAD không bị ảnh hưởng bởi vài
giá trị cực đoan.

**So trong cùng nhóm.** Ví dụ, chỉ so MPG giữa các chuyến cùng loại hàng và cùng nhóm quãng
đường. Nếu so chung, một tài xế chạy toàn tuyến đèo với hàng nặng sẽ bị đánh giá oan. Đây là
cách tránh **nghịch lý Simpson**: xu hướng chung có thể ngược với xu hướng trong từng nhóm.

**Ước tính tiết kiệm**
- **Nhiên liệu do MPG thấp:** (số gallon thực tế − số gallon nếu đạt MPG trung vị của nhóm) × giá
  nhiên liệu. Chỉ tính cho các xe hoặc tài xế *kém hơn* trung vị.
- **Chạy không tải:** số giờ không tải vượt trung vị × mức tiêu hao mỗi giờ không tải. Mức tiêu
  hao này là **giả định ghi rõ**, vì dữ liệu không có.
- **Giá mua nhiên liệu:** chênh lệch giá theo địa điểm. Hành động đề xuất là chính sách đổ nhiên
  liệu ở trạm hoặc khu vực rẻ hơn.

---

## 7. Lĩnh vực 4: Mức sử dụng đội xe và bảo dưỡng

**Lý thuyết**
- **Mức sử dụng tài sản:** xe đứng yên vẫn tốn khấu hao, bảo hiểm và chỗ đỗ.
- **Định cỡ đội xe:** cân bằng giữa *chi phí giữ xe thừa* và *rủi ro thiếu xe*. Tư duy này giống
  bài toán newsvendor trong quản trị tồn kho.
- **Chi phí vòng đời và tuổi thọ kinh tế:** khi xe già, chi phí bảo dưỡng/dặm tăng dần. Thời
  điểm nên thay xe là khi chi phí vận hành biên vượt chi phí sở hữu một xe mới. Đây là lý thuyết
  thay thế thiết bị (equipment replacement theory).

**Kỹ thuật**
- **Số xe cần thiết:** tính *số xe đang chạy mỗi ngày*, rồi lấy **phân vị cao (ví dụ p90)** làm
  quy mô đội xe đề xuất. Không lấy đỉnh, vì sẽ giữ xe cho vài ngày cao điểm hiếm hoi. Không lấy
  trung bình, vì sẽ thiếu xe một nửa số ngày. Phần chênh với đội hiện tại là số xe có thể bán
  hoặc chuyển đi.
- **Xe nên thay:** xếp hạng xe theo chi phí bảo dưỡng/dặm, giờ dừng và tỷ lệ sửa chữa đột xuất
  so với bảo dưỡng định kỳ, có xét xu hướng theo tuổi xe.

**Vì sao không làm bảo dưỡng dự đoán bằng ML:** cách này cần dữ liệu cảm biến (nhiệt độ động cơ,
độ rung, mã lỗi). Dữ liệu chỉ có 2.920 bản ghi bảo dưỡng, không có cảm biến. Mô hình dự đoán
hỏng hóc trên dữ liệu đó sẽ không đáng tin. Chấm điểm dựa trên chi phí và xu hướng thì minh bạch
và đủ để ra quyết định.

---

## 8. Ước tính tiết kiệm: các nguyên tắc

1. **Chuẩn là trung vị, không phải mức tốt nhất.** Đưa nhóm kém về mức *bình thường* của chính
   đội xe là mục tiêu đạt được. Lấy mức tốt nhất làm chuẩn sẽ hứa quá.
2. **Không cộng trùng.** Ví dụ, tiết kiệm nhiên liệu do bán bớt xe và do cải thiện MPG không được
   cộng đơn giản. Mỗi khoản được gán vào một lĩnh vực duy nhất.
3. **Truy được nguồn.** Mỗi con số $ dẫn được về truy vấn và các dòng dữ liệu tạo ra nó.
4. **Ghi rõ giả định.** Các đầu vào ước tính (đơn giá giờ tài xế, tiêu hao khi không tải) được
   liệt kê và có thể chỉnh. Báo cáo hiển thị chúng.
5. **So với mục tiêu.** Tổng tiết kiệm được so với mục tiêu ≥ 3% tổng chi phí vận hành trong
   `docs/01` §5. Phần so sánh này nằm ở CRISP-DM pha 5 (`docs/05-evaluation`).

---

## 9. Tối ưu hóa (phần mở rộng, chỉ làm nếu còn thời gian)

**Bài toán phân công xe/tài xế cho lô hàng** bằng **quy hoạch tuyến tính (LP)** với OR-Tools:
cực tiểu chi phí (dặm rỗng, chi phí theo xe) với ràng buộc mỗi lô có đúng một xe và mỗi xe một
việc tại một thời điểm.

**Vì sao không làm bài toán định tuyến xe (VRP):** VRP cần dữ liệu từng điểm dừng (tọa độ cửa
hàng, khung giờ nhận, ma trận khoảng cách). Dữ liệu này chỉ có 58 tuyến liên tỉnh dài, mỗi chuyến
là một cặp điểm đi–đến.

**Điểm nói khi phỏng vấn:** với Saigon Co.op, nơi giao hàng từ trung tâm phân phối (DC) đến hàng
trăm cửa hàng trong khung giờ hẹp, **VRP có khung thời gian (VRPTW)** là bước tiếp theo tự nhiên.
Phần dữ liệu và KPI trong dự án là nền móng cho bước đó.

---

## 10. Vai trò của LLM (Claude)

**Nguyên tắc: LLM giải thích, code tính toán.** Mọi con số do SQL/Python tính. Claude chỉ nhận
bảng số đã tính và viết nhận xét bằng lời. Đây là cách **neo vào dữ liệu** (grounding).

- **Vì sao:** LLM có thể viết ra số sai một cách rất tự tin (hallucination). Với báo cáo trình
  giám đốc, một con số sai làm mất uy tín cả báo cáo.
- **Câu hỏi bằng lời → SQL:** chỉ chạy trên các view KPI, chế độ chỉ đọc, giới hạn số dòng. Câu
  SQL được hiển thị để người dùng kiểm tra.
- **Kiểm soát chi phí:** lưu cache nhận xét theo (loại báo cáo, khoảng ngày, mã hash dữ liệu),
  nên chạy lại cùng báo cáo không gọi API lần nữa.

**Vì sao không để LLM tự phân tích dữ liệu thô:** kết quả không tái lập được (mỗi lần chạy một
khác), khó kiểm toán, tốn token, và dễ sai số học.

---

## 11. Công nghệ trình bày

| Chọn | Vì sao | Vì sao không dùng phương án khác |
|---|---|---|
| **Streamlit + Plotly** | Viết bằng Python nên dùng thẳng được mô hình và engine tối ưu. Miễn phí, tái lập được từ code | **Power BI / Tableau** mạnh về BI nhưng khó nhúng mô hình Python, cần giấy phép, khó đưa vào git |
| **Báo cáo HTML/PDF tự chứa** | Gửi email được, mở không cần cài gì | Báo cáo chỉ có trong dashboard thì không chia sẻ ra ngoài được |

---

## 12. Giới hạn và cách trình bày trung thực

- **Dữ liệu tổng hợp (synthetic) từ Kaggle.** Một số mẫu có thể không giống thực tế, ví dụ tỷ lệ
  đúng giờ sơ bộ chỉ 55,7%. Cách nói khi phỏng vấn: *phương pháp* mới là sản phẩm, số liệu
  minh họa cách nó vận hành.
- **Tương quan, không phải nhân quả.** Các yếu tố gây trễ là giả thuyết cần kiểm chứng thực địa.
- **Thiếu dữ liệu chi phí** (lương, chi phí chung): dùng biên đóng góp và giả định ghi rõ.
- **Chuyển sang bối cảnh Co.op:** nhiều điểm dừng mỗi chuyến (DC → cửa hàng), hàng tươi sống cần
  chuỗi lạnh, khung giờ nhận hàng ở cửa hàng. Khung KPI và quy trình giữ nguyên. Phần cần thêm là
  dữ liệu điểm dừng và mô hình VRPTW.

---

## Tài liệu tham khảo

- Chapman, P. và cộng sự (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. SPSS.
- Fayyad, U., Piatetsky-Shapiro, G., Smyth, P. (1996). From data mining to knowledge discovery in databases. *AI Magazine*, 17(3).
- ASCM/APICS. *SCOR Digital Standard* (Supply Chain Operations Reference model).
- DAMA International (2017). *DAMA-DMBOK: Data Management Body of Knowledge*, 2nd ed.
- Kimball, R., Ross, M. (2013). *The Data Warehouse Toolkit*, 3rd ed. Wiley.
- Kaplan, R. S., Cooper, R. (1998). *Cost & Effect: Using Integrated Cost Systems to Drive Profitability and Performance*. HBS Press.
- Kaplan, R. S., Narayanan, V. G. (2001). Measuring and managing customer profitability. *Journal of Cost Management*, 15(5).
- Davenport, T. H., Harris, J. G. (2007). *Competing on Analytics*. HBS Press.
- Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *Annals of Statistics*, 29(5).
- Lundberg, S. M., Lee, S.-I. (2017). A unified approach to interpreting model predictions. *NeurIPS*.
- Grinsztajn, L., Oyallon, E., Varoquaux, G. (2022). Why do tree-based models still outperform deep learning on typical tabular data? *NeurIPS Datasets and Benchmarks*.
- Tukey, J. W. (1977). *Exploratory Data Analysis*. Addison-Wesley.
- Leys, C. và cộng sự (2013). Detecting outliers: Do not use standard deviation around the mean, use absolute deviation around the median. *Journal of Experimental Social Psychology*, 49(4).
