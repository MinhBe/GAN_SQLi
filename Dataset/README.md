# Boolean-style Injection Research — ABCD / No Context — Dual Corpus V1

> **ĐỌC FILE NÀY TRƯỚC KHI SỬ DỤNG DỮ LIỆU.** Gói ZIP có **56.400 bản ghi theo thiết kế**: Corpus A 28.800 ô mẫu, Corpus B 27.600 bản ghi (21.600 ô mẫu + 6.000 đối chứng). **55.000 bản ghi có text không rỗng**; 1.400 ô Cassandra được giữ trong ma trận nhưng đánh dấu unsupported và **không phải các payload để train**. Số câu raw phân biệt của hai corpus tổng hợp là 39.849, không phải 50.400 cơ chế độc lập. Không mẫu nào được chứng minh khai thác được ứng dụng thực.
>
> **Toàn bộ dữ liệu mới trong gói được sinh bằng script có kiểm soát.** Không có chuyện tự động scrape 50.000 cuộc tấn công thực tế. `SOURCE_CATALOG.csv` là **các tài liệu nguồn về cú pháp**, không phải chứng cứ rằng từng dòng đã quan sát trong thực địa. Mọi `candidate_label_provisional=1` chỉ có nghĩa *mẫu được thiết kế theo logic biểu thức Boolean*; **KHÔNG phải nhãn ground truth SQLi/malicious.**

Ngày thiết kế nghiên cứu: **24/09/2026**. Corpus chỉ sử dụng input Z1/payload-only cho mô hình; file metadata được dùng trong chuẩn bị dữ liệu/validation, **không** phải các feature buộc phải có tại inference.

## 0. Tóm tắt chuyển giao cho AI agent / mục tiêu người dùng

Người dùng nghiên cứu SeqGAN char-level để **làm giàu dữ liệu** nhận diện Boolean-style injection. Kiến trúc phòng thủ mong muốn: WAF → detector nhẹ (thử RF, char n-gram + Logistic Regression) → detector nặng hơn (Transformer/LLM) cho các request chưa chắc chắn. Generator học và sinh **offline**, không đặt SeqGAN làm bộ chặn trên đường request. Người dùng từng xây 16.000 ví dụ Boolean SQLite-centric: bản đánh giá bên ngoài nêu rằng mặc dù có 16.000 raw unique, sau chuẩn hóa gần đúng chỉ khoảng 7.500 dạng biểu diễn; chưa có benign/hard-negative; các mẫu có SQLite expression validity nhưng thiếu exploit-outcome, DBMS breadth, source-heldout và kết quả downstream detector thực.

Đề xuất sửa đổi của người dùng: đưa **D – query language / database dialect** vào taxonomy; tất cả abstract grammar giao thoa với **18 đích D**, không cấp quota rời từng database. Hai arm nghiên cứu:
- **Corpus A / generator**: `4 × 20 grammar × 18 D × 20 sample = 28.800` hàng thiết kế.
- **Corpus B / detector**: `4 × 20 × 18 × 15 = 21.600` hàng candidate + `3.000 designed benign + 3.000 designed hard negatives` = **27.600** hàng.
- **Tổng = 56.400** bản ghi, trong đó 1.400 hàng CQL không có text vì không thể dịch đúng một cách tổng quát. Do đó có **55.000 hàng có payload/control text**, bao gồm 49.000 synthetic query-expression candidates + 6.000 controls.

**Không nên dùng trực tiếp file `detector_training_VIEW_PROVISIONAL.csv` để báo cáo accuracy SQLi production**: nhãn đó là nhãn thiết kế provisional và một số NoSQL/parameterized expressions là câu truy vấn hợp lệ thông thường, không phải SQL Injection.

## 1. ABCD là taxonomy, không phải bốn phép nhân được đảm bảo hợp lệ

| Chiều | Giá trị trong gói | Quy tắc |
|---|---|---|
| A: Attack/Injection mechanism | `boolean_style_candidate` | Đây là ý tưởng dùng điều kiện logic, **không** khẳng định toàn bộ 18 DB là SQLi |
| B: Complexity/representation | Y1 Simple, Y2 Variation, Y3 Basic Transformation, Y4 Basic Obfuscation | Y là nhãn thiết kế; Y3 và Y4 có thể cùng **ngữ nghĩa trừu tượng** với Y1 |
| C: Context | Z1 No Context | Chỉ payload/request-value; **không** có HTTP source, IP, query gốc, response, latency, session |
| D: Query language/engine | 18 đích, 5 nhóm | Khác database có thể cùng dialect, và cấu trúc có thể không tồn tại ở một đích |

Không mở rộng Z1 thành behavior/second-order. `truth=false` của biểu thức không bằng benign. Second-order là một thuộc tính vòng đời nhiều giai đoạn, **không** là một tier payload complexity.

### D catalog đầy đủ
- D1: PostgreSQL, MySQL, MariaDB, SQLite, SQL Server, Oracle (6).
- D2: BigQuery, Snowflake, ClickHouse, DuckDB (4).
- D3: MongoDB, Couchbase (2).
- D4: Redis (cụ thể **RediSearch**, không phải Redis key-value thông thường), Cassandra, DynamoDB (3).
- D5: Neo4j, Elasticsearch, OpenSearch (3).

**Chú ý với D3–D5**: MongoDB dùng MQL object, Couchbase dùng SQL++, Redis cần RediSearch module/index, DynamoDB dùng FilterExpression + ExpressionAttributeValues, Neo4j dùng Cypher, Elastic/OpenSearch dùng JSON DSL. Một MongoDB query object hợp lệ hoặc DynamoDB bind an toàn tự thân **không có nghĩa là injection**. Không gộp sản phẩm NoSQL thành một loại SQLi duy nhất.

## 2. Công thức, thực thể, ranh giới uniqueness

Tổng cộng 20 **Abstract Grammar Families** (AF_01…AF_20), được triển khai trong **4 tầng Y** ⇒ 80 Root IDs (20 mỗi tầng). 20 nhóm gồm so sánh số, `BETWEEN`, `IN`, text comparisons, prefix/contains và một số AND/OR kết hợp. Đó là 20 **mẫu cấu trúc logic**, không phải 20 kỹ thuật khai thác mới và không phải 80 AST hoàn toàn khác nhau. Mỗi `root_id` × database là một `structure_cell_id`, tức **360 cells/tier × 4 = 1.440 cells trong mỗi arm**.

`Root Grammar` (mẫu trừu tượng) → `Structure Cell` (grammar × D × Y) → `Grammar Slots` (kiểu/quan hệ thay thế) → `Generated Samples` (ví dụ cụ thể) → `Validation & Provenance` (nguồn + trạng thái).

- A có 20 mẫu/cell, `sample_index` 1–20.
- B có 15 mẫu/cell, `sample_index` 21–35; các literal/slot khác A, nhưng **chia sẻ 20 abstract grammar families, các renderer và các phép biến đổi**. KHÔNG xem A và B là hai nguồn độc lập để chấm generalization.
- `raw_sha256` là hash text **chưa chuẩn hóa**, dùng tìm duplicate, không biểu thị khác ngữ nghĩa. `abstract_family_id` là lineage chính cho held-out; `structure_cell_id` là lineage cụ thể theo database/Y. SQL dialect tương thích rộng sẽ có chuỗi trông giống nhau giữa engine; đây không phải lỗi ngẫu nhiên nhưng làm số effective unique giảm.
- Số lượng cấu trúc Y1–Y4 là định nghĩa thí nghiệm; Y4 với Redis/Dynamo/Cassandra chỉ có thay đổi khoảng trắng: `representation_technique=whitespace_only_NOT_verified_obfuscation`, **không** khẳng định các mẫu đó qua được WAF hoặc là obfuscation thực sự.

## 3. Hai bộ dữ liệu được tách riêng trong ZIP

### A_GENERATOR_CORPUS — 28.800 hàng

Mỗi thư mục `Y1_Simple/`, `Y2_Variation/`, `Y3_Basic_Transformation/`, `Y4_Basic_Obfuscation/` chứa:
1. `root_grammars.csv`: 20 mô tả cấu trúc gốc/tier.
2. `structure_cells.csv`: 20 × 18 = 360 ánh xạ grammar × D/tier.
3. `grammar_slots.csv`: 360 bản thiết kế slot/tier.
4. `generated_samples.csv`: 7.200 hàng/tier.
5. `validation_provenance.csv`: 7.200 bản trạng thái/tier.

Corpus A dành cho thử nghiệm character-level SeqGAN/augmentation. **Chỉ lấy `payload_raw` với các hàng có text và đã qua bộ lọc tư cách tương ứng**; không feed cột `root_id`, `d_category` hoặc `compatibility_status` vào mô hình text đầu vào nếu muốn giữ No Context. Có thể conditional generation trên D/Y nếu nghiên cứu có chủ đích và nêu rõ khác biệt.

### B_DETECTOR_CORPUS — 27.600 hàng

Cấu trúc Y giống A nhưng chứa 15 ví dụ khác/cell = 5.400 hàng/tier. Ngoài ra:
- `benign_and_hard_negatives.csv`: 3.000 benign thường + 3.000 SQL-like hard-negative, **đều synthetic do chương trình tạo**, không phải record benign từ hệ thống thực. Một vài bản chứa SQL tutorials, thông tin developer hoặc dấu nháy đơn; không nên chặn mặc định.
- `detector_training_VIEW_PROVISIONAL.csv`: view phẳng candidate không rỗng + 6.000 controls; **đã loại 600 unsupported Cassandra của B**. `candidate_label_provisional` không phải ground truth SQLi; cả các controls chưa được đo tác động trong từng application.

**B không phải một immutable external test**: B/A có chung abstract roots và logic renderer. Để đánh giá giá trị SeqGAN, cần có test từ nguồn khác (hoặc group-held-out thật), hoàn toàn không augment/tune trên test.

## 4. Quy tắc biến đổi theo tier và hiệu lực của chúng

- **Y1**: biểu thức điều kiện trực tiếp của một dialect (WHERE predicate fragment, MQL/JSON query object, search DSL…). Với SQL fragment, phải gắn vào ngữ cảnh WHERE mới chạy; Z1 không biết ngữ cảnh app thật.
- **Y2**: nhóm ngoặc/format/whitespace/cách biểu diễn một biểu thức; nhiều Y2 tương đương AST với Y1; không tự tuyên bố mở rộng mechanisms.
- **Y3**: một lớp percent-encoding form/HTTP. `payload_raw` không phải SQL expression executable; nó cần decode **chính xác một lần** để ra `payload_decoded_or_canonical`. Nếu không có pipeline decode tương ứng, mẫu có thể không đi tới DB dưới dạng dự kiến.
- **Y4**: với SQL/SQL++ chèn comment dạng `/**/` tại một số chỗ cú pháp; với JSON dùng escape Unicode trong tên khóa; với Cypher cố gắng chèn comment; với các dialect còn lại có thể chỉ là whitespace. Cần test parser thật để xác nhận tương đương. Đây là tập **representation candidates**, không là benchmark chứng minh né WAF.

Tầng B complexity và D orthogonal về thiết kế nhưng không mọi phép kết hợp hợp lệ thực địa; **status = unsupported** cần được giữ tách biệt với `malicious=false`.

## 5. Kiểm soát tương thích: tại sao có 1.400 hàng không có raw text?

Một số cấu trúc như OR tổng quát, NOT BETWEEN, nhiều toán tử text không thể được ánh xạ thành CQL WHERE tổng quát mà không có schema/index/use case. **Không được tạo CQL giả** để lấp đủ quota: 1.400 cấu trúc-cross-dialect Cassandra (800 ở A, 600 ở B) được giữ như *coverage matrix slot* có `payload_raw=""`, `eligibility_for_detector_attack_training=exclude_unsupported`. Đếm rows = 56.400; đếm có text = 55.000. `D_DIALECT_CATALOG.csv` và `QA_REPORT.json` ghi rõ.

Ngay cả hàng Cassandra có raw text cũng chỉ là phác thảo WHERE schema-dependent, chưa xác nhận CQL engine. Redis requires RediSearch; DynamoDB requires separately bound values and syntax API validation; Elastic wildcard/prefix and MQL semantics depend on field index, BSON typing and runtime. `compatibility_status` phản ánh điều này. **Không mở rộng nhãn SQLi đến mọi DB**.

## 6. Sự khác nhau của các trường, schema, nguồn gốc

| Trường | Mô tả đúng |
|---|---|
| `sample_id` | ID bản ghi, không là hash AST |
| `root_id` | 1 trong 80 root IDs/từng arm; có thể cùng abstract semantics across tier |
| `abstract_family_id` | AF_01–AF_20, dùng group split |
| `structure_cell_id` | root × DB tier |
| `grammar_slots_id` | bảng slot và ràng buộc type |
| `payload_raw` | text đầu vào hay query representation sinh ra (có thể rỗng cho unsupported) |
| `payload_decoded_or_canonical` | cách biểu diễn trước transform hoặc sau decode, KHÔNG là ground-truth canonicalizer |
| `query_binding_json` | metadata thêm cho DynamoDB, không được mặc định là thông tin quan sát từ request |
| `abstract_predicate_ast` | tuple IR để phân tích nghiên cứu; không phải AST từ parser của DB |
| `compatibility_status` | chưa kiểm chứng engine, schema-dependent hoặc unsupported |
| `eligibility_for_detector_attack_training` | nhãn **thận trọng**, không dùng để claim malicious |
| `external_observed` | false cho các mẫu mới |
| `behavior_validated` | false cho các mẫu mới |
| `split_group_key` | AF ID; group giữ cùng một phía train/test để tránh lineage leakage |

**Synthetic:** chủ động sinh bằng code. **Source corpus/reference:** mẫu xuất hiện trong dataset người dùng cung cấp nhưng không có chứng nhận từ traffic thật. **Observed attack:** chỉ dùng khi có log/trace và provenance xác thực. **Validated:** chỉ ghi true kèm oracle, phiên bản engine/app và bằng chứng.

## 7. Những phát hiện từ báo cáo cũ và cách tránh lặp lại

Tài liệu `CONTEXT/user_supplied_dataset_assessment.md` được đưa vào ZIP để AI agent đọc đánh giá từ người dùng. Báo cáo cho rằng corpus 16.000 ban đầu có raw unique 16.000 nhưng ~7.500 normalized lexical variants sau cách chuẩn hóa gần đúng, Y3 ~1.000/Y4 ~1.500; đây **không** phải AST proof. Các baseline cũ `~89,88% IID → ~76,72% leave-one-variant-out` chỉ phân loại Y1–Y4, **KHÔNG phải attack detection accuracy**. Không đưa các điểm số đó lên đầu báo cáo detector mới.

Những thiếu sót vẫn còn: độc lập semantic roots thật, benign độc lập, confirmed application outcomes, multi-DB engine verification, external source-heldout, drift, false-positive and performance measurement. Corpus mới **cải thiện khả năng tổ chức D + có designed controls**, nhưng **chưa tự giải quyết** ground truth thực tế.

## 8. Cách tiến hành thí nghiệm đúng cho đề tài SeqGAN

1. Dựng train/val/test dựa trên `abstract_family_id` / nguồn trước khi augmentation. A và B chia literal indices nhưng chia sẻ **all abstract families**, nên không thể dùng B làm OOD headline test cho A.
2. Khóa một external review set độc lập (và nếu có thể laboratory-confirmed, app-context limited); không đưa bất kỳ mẫu test nào cho SeqGAN.
3. So sánh *cùng budget số training records*: Originals only; naive duplication; rule-based augmentation; SeqGAN augmentation; hybrid SeqGAN + grammar-filter.
4. Với SeqGAN ghi `raw uniqueness`, parser validity theo engine, semantic equivalence, novelty theo **group lineage**, nearest-neighbor/syntax overlap, duplication-adjusted effective samples. GAN hơn về raw count **không tự suy ra Detector tốt hơn**.
5. Với detector đo PR-AUC, precision/recall @ FPR cố định, FPR trên mẫu benign/hard-negative, latency p50/p95/p99, throughput, CPU/RAM, % request phải escalate lên AI nặng. Không có benign lab/external test thì **không** claim production-ready.
6. Giá trị Boolean đầu vào `true/false` là expected condition truth, không được suy diễn `false=benign`.
7. Baseline lightweight nên có char TF-IDF 3–5 grams + Logistic Regression và Random Forest có đặc trưng phù hợp; benchmark thật, không mặc định RF luôn nhanh hơn linear.
8. Production phòng chống SQLi chủ yếu vẫn dựa vào **parameterized queries**; WAF/model là lớp bổ sung, không thay đổi code/data separation.

## 9. Layout ZIP

```text
Boolean_ABCD_Dual_Corpus_56400/
├── README.md                             # Tài liệu này, ở TRONG ZIP
├── dataset_manifest.json
├── QA_REPORT.json
├── D_DIALECT_CATALOG.csv                  # 18 D
├── SOURCE_CATALOG.csv                     # Nguồn tài liệu, không chứng minh observed
├── build_dataset.py                       # script tái sinh corpus
├── CONTEXT/
│   ├── project_context_and_decisions.md
│   ├── user_supplied_dataset_assessment.md
│   └── legacy_1787_BOOLEAN_CANDIDATES_NOT_VALIDATED.csv
├── A_GENERATOR_CORPUS/
│   ├── Y1_Simple/                         # 5 CSV như mục 3
│   ├── Y2_Variation/
│   ├── Y3_Basic_Transformation/
│   └── Y4_Basic_Obfuscation/
└── B_DETECTOR_CORPUS/
    ├── Y1_Simple/                         # 5 CSV như mục 3
    ├── Y2_Variation/
    ├── Y3_Basic_Transformation/
    ├── Y4_Basic_Obfuscation/
    ├── benign_and_hard_negatives.csv
    └── detector_training_VIEW_PROVISIONAL.csv
```

## 10. QA đã thực hiện, còn chưa làm

`QA_REPORT.json` ghi kiểm tra counts theo nhóm/tier; script tái sinh deterministic và không gọi mạng. Trong khi tạo gói, đã parse JSON `payload_decoded_or_canonical` của MongoDB, Elasticsearch, OpenSearch, DynamoDB và kiểm tra **2.800 SQLite predicate fragments** trong SQLite in-memory dùng bảng `(score INTEGER, tag TEXT)`; cả 2.800 parse/execute thành công. Đây KHÔNG phải 2.800 lỗ hổng SQLi thực. Các DB còn lại chưa chạy engine; URL-encoded raw phải decode trước; Y4 không được chứng minh trốn WAF.

QA có thể làm tiếp: schema-level CQL, MongoDB/Elastic runtime against indexes, SQL dialect engines versioned, Unicode/normalization oracle, hard-negative manual review, licensed external-source review, independent lab-app execution, temporal traffic drift, leakage-safe evaluation.

## 11. Nguồn minh bạch và bản quyền

Nguồn tài liệu khảo sát về syntax và prevention ở `SOURCE_CATALOG.csv` (OWASP, PortSwigger, MongoDB, Elastic, OpenSearch, Redis, DynamoDB, Neo4j, Couchbase, BigQuery). Chúng là **nguồn tham chiếu thiết kế**; không có hàng nào được gán là *đã scrape trực tiếp từ trang đó*. File legacy 1.787 records là **tập ứng viên** trong bộ người dùng đã gửi; không đếm vào 56.400 và phải xác minh origin/license trước khi phát hành lại. Đánh giá văn bản từ người dùng ở CONTEXT có thể chứa trích dẫn hoặc giả định cần kiểm chứng; không biến chúng thành kết quả mới của script.

## 12. Một lưu ý kỹ thuật để không đánh tráo mục tiêu

Một số dữ liệu như `"score > 100"`, MongoDB `{ "$gt": ... }`, Elastic `bool` query và DynamoDB condition expression là **query/filter syntax** có thể xuất hiện trong ứng dụng bình thường. Không có application query construction trace, ta không thể gọi tất cả là *attack*. Bộ này là **candidate-level representation corpus**, phù hợp phát triển grammar và đo augmentation; để xây AI nhỏ dùng thật, phải làm bước adjudication/lab validation và kiểm tra false positives. Đó là nguyên tắc xuyên suốt: **Generated ≠ Validated ≠ Useful**.
