# Boolean SQLi — No Context — gói nghiên cứu 800 Root IDs / 16.000 mẫu (v1)

**Ngày tạo:** 2026-09-24.  
**Phạm vi:** X = Boolean-style SQL Injection **candidates**; Z = Z1 / No Context / payload-only; Y = Y1–Y4.  
**Tình trạng dữ liệu:** **TẤT CẢ 16.000 mẫu chính là synthetic**, được sinh theo grammar có kiểm soát và kiểm tra *biểu thức* trong SQLite in-memory. Không có mẫu nào được xác nhận khai thác thành công ứng dụng thật. 1.787 mẫu trong file corpus tham chiếu là dữ liệu do người dùng cung cấp, **không được xác nhận là bắt từ lưu lượng tấn công thực tế**.

> **ĐỌC TRƯỚC KHI DÙNG:** `800 root IDs` = 200 công thức ngữ pháp/biểu diễn **trong mỗi tầng Y**, không có nghĩa là 800 cơ chế SQL khác nhau, 800 mẫu được quan sát thực tế hoặc 800 cây AST hoàn toàn độc lập. Các tầng Y3/Y4 cố ý chia sẻ *ngữ nghĩa* với các tầng thấp hơn; chúng khác ở **quy tắc biểu diễn đầu vào**. Sự khác nhau về chuỗi ≠ khác nhau về cơ chế khai thác.

## 0. Tóm tắt cho AI agent mới tiếp quản

Người dùng đang nghiên cứu sử dụng character-level SeqGAN để làm giàu dữ liệu huấn luyện cho detector SQL Injection, với mục đích hỗ trợ kiến trúc WAF → detector nhẹ → mô hình lớn chỉ khi cần. Người dùng quan tâm đặc biệt đến lượng request lớn, giá suy luận, độ tổng quát hóa và tránh sinh hàng nghìn mẫu chỉ thay `1=1` thành `2=2`. Trong cuộc trao đổi với sếp của người dùng, các yêu cầu trọng tâm là: định nghĩa chính xác đầu vào/bộ phận nào chặn, có bằng chứng thực nghiệm, phân biệt mẫu sinh ra với tấn công thực sự, so sánh với baseline hiện có và tính đến hiệu năng hệ thống thực.

Taxonomy được chốt để nghiên cứu:
- **X**: SQLi family / technique (Boolean, UNION, Error, Time, Stacked...); nhiều kỹ thuật có thể cùng xuất hiện, không nên coi family là lớp loại trừ tuyệt đối.
- **Y**: **độ phức tạp biểu diễn payload**, không phải độ nguy hiểm hay tỉ lệ thành công.
- **Z**: yêu cầu ngữ cảnh: Z1 chỉ payload; Z2 payload + ngữ cảnh một lần request/truy vấn; Z3 lịch sử/trạng thái nhiều bước. Second-order là hiện tượng gắn với chuỗi xử lý ở Z3, không phải mức độ khó của chuỗi.
- **MVP hiện tại = Boolean-style × Y1/Y2/Y3/Y4 × Z1**. Không có IP, request, query gốc, response, WAF log, DBMS mục tiêu, session hay execution trace ngoài giả định SQLite lab.
- **Y5** (Advanced Transformation / Obfuscation) và Y6 (Specialist) được dự kiến cho tương lai; **không thuộc yêu cầu bốn tầng dữ liệu hiện tại**. Câu yêu cầu “4 thư mục Y1 đến Y5” mâu thuẫn về số lượng; gói này làm **đúng 4 thư mục Y1–Y4**, để Y5 ngoài phạm vi và ghi rõ ở đây.

**Không giao nhầm nhiệm vụ:** SeqGAN sinh dữ liệu để train offline, không nhất thiết xử lý trực tiếp từng HTTP request. Random Forest / Logistic Regression / Transformer là ứng viên detector, chưa có benchmark tốc độ hay chất lượng để kết luận kiến trúc nào thắng.

## 1. Cách đọc con số

| Tầng | Tên | Số Root IDs | Số Structure Cells | Số mẫu / root | Số mẫu |
|---|---|---:|---:|---:|---:|
| Y1 | Simple | 200 | 400 | 20 | 4.000 |
| Y2 | Variation | 200 | 400 | 20 | 4.000 |
| Y3 | Basic Transformation | 200 | 400 | 20 | 4.000 |
| Y4 | Basic Obfuscation | 200 | 400 | 20 | 4.000 |
| **Tổng** | | **800** | **1.600** | | **16.000** |

**Công thức mỗi tầng:** `25 loại biểu thức Boolean (predicate kinds) × 8 grammar/representation recipes = 200 typed root IDs`.  
**Công thức mỗi root:** `2 structure cells × 10 sample/cell = 20 sample/root`.  
Mỗi root có **10 quan sát SQL truth = 1 và 10 SQL truth = 0** trong lab. Không được coi `truth = 0` là benign: một biểu thức được thiết kế có kết quả false vẫn có thể là input kiểm thử SQLi.

*Phân biệt:*
- **Root Grammar**: công thức có typed placeholders; ví dụ Y1 ` OR (<P:num_eq>)`. Ở Y3/Y4 root là **recipe biểu diễn**, không phải một AST SQL khác biệt về ngữ nghĩa.
- **Structure Cell**: hai biến thể *rendering* nằm trong cùng root (C01 canonical, C02 có khoảng trắng đầu hoặc comment kết thúc). Đây **không phải root grammar thứ 201**.
- **Grammar Slots**: quy tắc và miền hợp lệ của `<P>`, `<Q>` và chính sách biểu diễn. Đây là quy tắc generator phải tuân thủ, **không chỉ là nhãn**.
- **Generated Samples**: chuỗi cụ thể được đổ từ slots.
- **Validation & Provenance**: bản ghi thí nghiệm SQL lab và nguồn gốc mỗi chuỗi. Validation không bảo đảm exploit.
- **Typed grammar:** hai root có cùng text `<P>` nhưng `P = num_eq` và `P = text_like` được tách vì các loại toán tử/kiểu dữ liệu khác nhau. Sự khác nhau này vẫn không tự động chứng minh hai cơ chế SQLi độc lập.

## 2. Cây thư mục

```text
Boolean_No_Context_800_Roots_16000/
├── README.md                              ← đọc đầu tiên
├── dataset_manifest.json                  ← đếm, phạm vi, báo cáo kiểm thử
├── source_catalog.csv                     ← nguồn công khai + phân biệt tham chiếu/copy
├── source_corpus_boolean_candidates_NOT_LABELED.csv ← 1.787 mẫu từ file người dùng
├── Y1_Simple/
│   ├── root_grammars.csv                  ← 200 root
│   ├── structure_cells.csv                ← 400 cell
│   ├── grammar_slots.csv                  ← các typed slots/ràng buộc
│   ├── generated_samples.csv              ← 4.000 mẫu
│   └── validation_provenance.csv          ← 4.000 bản ghi
├── Y2_Variation/                          ← năm file cùng schema
├── Y3_Basic_Transformation/              ← năm file cùng schema
└── Y4_Basic_Obfuscation/                 ← năm file cùng schema
```

**CSV sử dụng UTF-8 with BOM và header row**, có thể dùng `csv.DictReader(encoding="utf-8-sig")`. Các chuỗi SQL có thể chứa dấu nháy, xuống dòng, dấu `%`, dấu phẩy; dùng parser CSV, không tách dòng bằng tay. Khi mở trong ứng dụng spreadsheet, coi `payload_raw` là văn bản, không phải công thức Excel.

## 3. Giải thích 4 tầng Y và ranh giới giữa chúng

### Y1 — Simple

Boolean predicate có kiểu dữ liệu rõ ràng và operator/connective; ví dụ đầu tiên ` OR (27 = 27)`. Root được tạo từ 25 predicate kinds × 8 khung kết hợp. Một số khung có `NOT` hoặc kết hợp hai predicate — vẫn là mẫu SQL logic trực tiếp, chưa có encoding/che giấu. **Simple** ở đây là quy ước giới hạn cú pháp của gói, không phải khẳng định mẫu chắc chắn dễ phát hiện ở mọi detector.

Tám pattern:
```text
OR P; AND P; OR NOT P; AND NOT P;
OR P AND Q; AND P OR Q; OR (P OR Q); AND (P AND Q)
```
File dùng dấu ngoặc để kiểm soát độ ưu tiên. Q = numeric equality được tạo sao cho cùng giá trị truth với P; `NOT` đảo chân trị ở cấp khung, nhưng `design_predicate_truth` vẫn nói về P.

### Y2 — Variation

Các lựa chọn cú pháp thể hiện Boolean trực tiếp, như chữ hoa/thường, ngoặc lồng, double negation hoặc cách biểu diễn truth test. Ví dụ ` oR (27 = 27)`. Không thêm HTTP/SQL execution context. Tám pattern được định nghĩa độc lập cho Y2 và được ghi trong `root_grammars.csv`; **khác biểu thức render không có nghĩa khác kết quả**. Không gán Y2 chỉ vì thay một số đơn thuần.

### Y3 — Basic Transformation

Biểu thức SQL gốc được viết thành **HTTP form-style input có một lớp percent encoding**. Ví dụ `'%20OR%20(27%20=%2027)'`; sau `urllib.parse.unquote_plus` một lần thành ` OR (27 = 27)`. Tám recipe: encode whitespace, form `+` cho space, encode parentheses, encode operator + một chữ connector, encode chữ số, encode connector, encode whitespace + parentheses, encode từng UTF-8 byte. Chúng là tám chính sách biểu diễn, **không phải tám phương pháp đã được xác nhận vượt WAF**.

**Ranh giới kỹ thuật quan trọng:** Y3 chỉ có thể xác thực dưới một `declared_decode` giả định. Thứ tự decode/normalize ở WAF, framework và app thật KHÔNG có trong Z1; không khẳng định URL encoder nào có thể khai thác hệ thống thật. File cung cấp cả raw và decoded. Không được đánh giá raw `%...` trực tiếp bằng SQL parser rồi kết luận invalid vì chưa áp dụng decode giả định.

### Y4 — Basic Obfuscation

Dùng comment/whitespace/case hợp lệ theo SQLite để thay đổi biểu diễn, ví dụ ` OR/**/(27 = 27)`. Tám recipe bao gồm comment rỗng, comment có nhãn, hai comment liên tiếp, comment + mixed case, comment sau `(`, comment trong vị trí khoảng trắng hợp lệ bên trong predicate, comment + linebreak và comment hậu tố. Comment không được chèn vào trong string literal. Không có keyword splitting bất hợp lệ, versioned comments của MySQL, bypass đặc thù một WAF hoặc multi-layer transformation; các cái đó cần thiết kế nghiên cứu riêng và kiểm tra theo DBMS.

**Y3 ≠ Y4** ở cách dữ liệu được biểu diễn: Y3 có giả định HTTP decode một lớp; Y4 là SQL comment/lexical presentation sau decode. Một mẫu có thể thuộc cả hai trong thực tế: các nhãn ở đây là nhóm thí nghiệm để kiểm soát biến, KHÔNG phải các lớp hoàn toàn loại trừ.

## 4. 25 predicate kinds đang được phủ

`num_eq`, `num_ne`, `num_gt`, `num_ge`, `num_lt`, `num_le`, `num_between`, `num_not_between`, `num_in`, `num_not_in`, `num_is`, `num_is_not`, `text_eq`, `text_ne`, `text_lt`, `text_gt`, `text_like`, `text_not_like`, `text_glob`, `text_not_glob`, `text_in`, `text_not_in`, `null_is_null`, `null_is_not_null`, `arithmetic_eq`.

Chúng bao gồm numeric, string, null test và arithmetic. Các biểu thức null test có literal số khác nhau theo sample để tránh duplicate cơ học, nhưng **không sinh 20 hành vi SQL mới**. SQLite được chọn để tự kiểm tra grammar bằng lab nhẹ; `GLOB`, `IS`, `NULLIF` cùng nhiều semantics khác là **SQLite-specific**, không chuyển nhãn một cách ngây thơ sang MySQL/PostgreSQL/SQL Server. Khi mở rộng multi-DBMS, tách dialect và lab validator.

## 5. Hệ thống ID và quan hệ giữa CSV

Ví dụ:
```text
root_id = Y1_R001
structure_cell_id = Y1_R001_C01 / Y1_R001_C02
sample_id = Y1_R001_S01 ... Y1_R001_S20
split_group_id = P01
```
- `root_grammars.csv`: đúng một dòng cho mỗi root; `root_grammar` có slot typed; `predicate_kind` là tên kiểu toán tử.
- `structure_cells.csv`: hai dòng/root; 10 sample/cell; không phải hai grammar độc lập.
- `grammar_slots.csv`: ba dòng/root: P, Q (có thể n/a), representation; `constraints` mô tả ranh giới.
- `generated_samples.csv`: `payload_raw` cho detector payload-only; `payload_after_declared_decode` cho đánh giá SQL lab; `design_predicate_truth` truth thiết kế của P; `lab_expression_truth` chân trị của *biểu thức gồm prefix/connective*; `real_application_exploit_confirmed=false`.
- `validation_provenance.csv`: truy vấn `SELECT CASE WHEN (...) THEN 1 ELSE 0 END`, success/failure, nhãn lab, giả định decode, nguồn. Mỗi sample_id map 1:1.
- `source_catalog.csv`: URL và vai trò chứng cứ, **không phải trích nguồn cho từng chuỗi là một cuộc tấn công được ghi nhận**.
- `source_corpus_boolean_candidates_NOT_LABELED.csv`: 1.787 Query được lấy từ tập `boolean_core_candidates.csv` đã tách trước đó từ file người dùng `Modified_SQL_Dataset.csv.zip`; chỉ là **candidates**, chưa gán Y, chưa match root, chưa xác minh true attack trong lab. Không trộn vào 16.000.

## 6. Dữ liệu “có nguồn gốc” nghĩa là gì trong gói này?

Phải phân biệt ba tầng bằng chứng:
1. **Source-informed synthetic**: 16.000 mẫu chính được sinh bởi quy tắc trong gói; kiến thức về SQL/SQLi được tham chiếu từ tài liệu SQLite, PortSwigger, OWASP; KHÔNG copy payload từng câu từ website rồi tuyên bố là thực nghiệm.
2. **User-provided corpus**: 1.787 câu trong file tham chiếu đã có từ dataset upload. Sự hiện diện của câu trong một dataset không có nghĩa nó là bản ghi request thực tế.
3. **Behaviorally validated attack attempt**: cần app lab có chỗ vulnerable, đầu vào/request cụ thể, SQL gốc, trace, quan sát và outcome. **Số mẫu loại (3) trong gói này = 0.**

Tài liệu nghiên cứu có tham khảo:
- SQLite expressions: https://www.sqlite.org/lang_expr.html
- SQLite comments: https://www.sqlite.org/lang_comment.html
- SQLite SELECT: https://www.sqlite.org/lang_select.html
- PortSwigger blind SQLi: https://portswigger.net/web-security/sql-injection/blind
- PortSwigger SQLi cheat sheet: https://portswigger.net/web-security/sql-injection/cheat-sheet
- OWASP prevention: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- OWASP CRS SQLi rules: https://github.com/coreruleset/coreruleset/blob/main/rules/REQUEST-942-APPLICATION-ATTACK-SQLI.conf
- PayloadsAllTheThings SQLite: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/SQLite%20Injection.md
- FuzzDB: https://github.com/fuzzdb-project/fuzzdb

Nguồn công khai là tài liệu bối cảnh / nơi có thể mở rộng một *external held-out set* trong tương lai; các kho trên **không được download và gộp làm hàng 16.000**. Không được viết bài rằng đây là “16.000 attacks observed in the wild”.

## 7. Phương pháp sinh và kiểm thử đã thực hiện

Một lần sinh mẫu:
```text
X = Boolean-style, Z = No Context
→ Y tier
→ typed root ID = predicate kind × tier-specific recipe
→ cell C01 hoặc C02
→ slots P (+ Q nếu cần), với số/string seed thay theo sample
→ raw payload
→ Y3: unquote_plus một lần (các tier khác: raw là SQL)
→ lồng vào biểu thức kiểm thử an toàn SELECT CASE WHEN (0/1 + fragment) THEN 1 ELSE 0 END
→ thực thi SQLite :memory:
→ ghi observed_truth, điều kiện test và provenance
```
**Lưu ý:** số `0` hay `1` trước fragment chỉ là scaffolding của lab để có một biểu thức hợp lệ; không phải SQL query template được quan sát ở app. Không chạy DDL/DML, không truy cập mạng, không trích xuất thông tin nhạy cảm. Toàn bộ biến đều là literal giả lập.

Kết quả tại thời điểm đóng gói: 4.000/4.000 sample mỗi tầng đều được SQLite xử lý và có true/false tương ứng kỳ vọng thiết kế (xem `dataset_manifest.json`); 4.000 payload thô không trùng trong mỗi tầng, 16.000 không trùng thô toàn gói. **Không kiểm tra attack success**, WAF bypass, false-positive rate, runtime latency hoặc exploit reliability. “Valid SQL expression” ≠ “valid SQLi in target application” ≠ “useful for learning”.

## 8. Đánh giá đúng tinh thần nghiên cứu: CỰC KỲ QUAN TRỌNG

**Không train/test random theo sample rồi công bố generalization.** Các sample cùng root thường chỉ khác literal hoặc rendering cell. Random split trộn chúng sẽ làm detector trông giỏi hơn thực tế. Có ít nhất bốn thí nghiệm tách biệt:
1. **IID sample split**: chỉ để baseline; báo rõ nguồn rò rỉ theo template.
2. **Unseen structure cell**: giữ toàn bộ C02 của các root ngoài training (hoặc thiết kế split cấp cell).
3. **Unseen root**: group split theo `lineage_id = root_id`.
4. **Unseen predicate lineage**: split theo `split_group_id = P01...P25` (có thể chọn held-out kind và không cho bất kỳ tier nào dùng kind ấy để train).
5. **Unseen transformation**: giữ nguyên recipe/grammatical_variant_id (và Y3 encoding strategy) ngoài train, không chỉ thay literals.

**Trong mỗi thí nghiệm, split raw originals trước khi sinh mọi augmentation;** giữ các họ biến thể cùng gốc trong cùng partition nếu muốn kiểm tra tổng quát hóa. Không chọn hyperparameter trên final test.

**Detector cần benign/hard negatives riêng** (từ corpus nguồn hoặc app lab). Bộ này chủ yếu gồm biểu thức SQLi-like; `lab_expression_truth=0` KHÔNG phải label 0/benign. Tuyệt đối không train binary attack/benign chỉ bằng 8.000 true + 8.000 false rồi nói mô hình detect SQLi.

**Ablation có ích:** Base detector chỉ train mẫu source-corpus sạch có đánh giá manual; +simple duplication; +rule-based typed augmentation; +SeqGAN augmentation. Giữ kích thước/tỉ lệ và split test giống nhau; so sánh recall trên family unseen, FPR trên benign, latency p50/p95/p99, throughput, CPU/RAM, cost per request, confidence calibration và volume cần escalate lên model lớn. Kiểm tra mức độ SeqGAN học các slot hợp lệ, không chỉ perplexity hoặc số lượng chuỗi khác biệt.

## 9. Hạn chế và cảnh báo cho hệ thống phòng thủ

- Đừng “trúng chuỗi SQL là block ngay”: nhiều benign có dấu nháy, `AND`, `LIKE`, số, code sample. Dùng decision/risk threshold, review false positives và kế hoạch rollback. Chuẩn hóa consistent với tầng nhận dữ liệu.
- Dữ liệu Z1 không thể xác nhận second-order, injection point, query context, database side effects, HTTP response khác biệt hoặc campaign qua nhiều IP. `z_context=Z1` là **phạm vi đầu vào**, không phải bằng chứng một request ngoài thực địa không có context.
- Boolean-based và Boolean-blind không phải một nhãn: từ payload chỉ có thể nhận diện cấu trúc điều kiện hoặc Boolean-style candidate; muốn xác nhận blind cần cặp request/response, điều kiện đúng/sai và kết quả.
- Y5 Specialist/advanced chưa được sinh ở gói này, không tự sửa Y4 thành Y5; Y5 dự kiến nhận diện thêm use case và có protocol/DBMS rõ.
- Phòng chống SQLi chủ động tại app vẫn nên dùng parameterized queries/prepared statements; detector/WAF chỉ là phòng thủ bổ sung. Không dùng tỷ lệ filter rule làm bằng chứng duy nhất về hiệu quả tấn công.

## 10. Contract dữ liệu cho AI agent

**Dữ liệu chính:** chỉ đọc `Y*/generated_samples.csv`. Sử dụng `payload_raw` nếu detector đang nhìn chuỗi user nhập, hoặc `payload_after_declared_decode` nếu pipeline chính thức của detector đã decode URL-form một lần. Tuyệt đối không trộn hai representation mà không thêm feature/nhãn `representation_layer`. ID root/cell có thể dùng để đánh giá nhưng **không làm feature đầu vào**, nếu không sẽ label leakage. Nối `sample_id` với `validation_provenance.csv` nếu cần log kiểm thử. `source_corpus_boolean_candidates_NOT_LABELED.csv` là external reference, chưa thể trộn trực tiếp thành hard truth.

**Không suy diễn:** 200 root trong Y1 không có nghĩa 200 cơ chế exploit; 200 root trong Y3 là 25 typed predicates × 8 encoding recipes; 200 root trong Y4 là 25 typed predicates × 8 SQL-comment/presentation recipes. Mẫu sinh không phải mẫu quan sát, root không phải unique AST được third-party xác nhận, truth flag không phải benign/malicious label, “comment obfuscation” không chứng minh WAF bypass.

**Khi mở rộng:** giữ schema/ID lineage, đưa vào DBMS-specific parser và controlled app lab, lưu *Attack Attempt = request context + input + processing/execution trace + observation + outcome*, đánh giá trên corpus ngoại lai sạch và false positive. Mục tiêu không phải làm số lượng mẫu lớn cho đẹp mà là **Generated ≠ Validated ≠ Useful**.
