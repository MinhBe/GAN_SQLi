# PostgreSQL Boolean No-Context Attack Corpus V2

## 1. Mục tiêu

Bộ dữ liệu này là **attack-side source corpus** dành cho bốn mô hình character-level SeqGAN độc lập:

- Y1 — Simple
- Y2 — Variation
- Y3 — Basic Transformation
- Y4 — Basic Obfuscation

Phạm vi được cố ý thu hẹp: **PostgreSQL × Boolean predicate logic × payload-only / no-context**.

Bộ này **không phải benchmark detector**. Không có benign, hard-negative, train/validation/test split hay detector labels.

## 2. Quy mô

Mỗi Y chứa 6.000 samples:

`100 semantic roots × 10 structure cells/root × 6 samples/cell = 6.000`

Tổng cộng 24.000 samples.

## 3. Lineage bắt buộc

Mỗi sample truy ngược được theo chuỗi:

`semantic intent → root grammar → structure cell → grammar slots → variation recipe → PostgreSQL representation → sample`

Các khóa chính:
- `root_id`
- `structure_cell_id`
- `variation_id`
- `structure_signature`
- `attack_fingerprint`

## 4. Uniqueness

Không dùng một metric duy nhất.

- **Raw uniqueness**: chuỗi payload có trùng tuyệt đối hay không.
- **Fingerprint uniqueness**: lineage + recipe + payload có tạo fingerprint riêng hay không.
- **Canonical uniqueness**: sau canonicalization còn bao nhiêu dạng.
- **Lexical distance**: khoảng cách character 4-gram nhỏ nhất tới sample khác trong cùng cell/root.

Canonical collision không mặc định là lỗi, đặc biệt ở Y3/Y4: nhiều representation có thể cố ý hội tụ về cùng semantic/canonical form.

## 5. Các feature mô tả sample

Corpus giữ các feature:
- character length
- estimated token count
- parenthesis depth
- operator/literal/function/cast/connector counts
- character entropy
- alpha/digit/whitespace/special-character ratios
- unique-character ratio
- character-class count
- decode requirement/layers
- PostgreSQL specificity
- expected Boolean truth
- semantic family
- canonical representation
- structure and attack fingerprints
- within-cell/root lexical distance

Các metric này dùng để audit/filter corpus trước SeqGAN; không bắt buộc phải trở thành đầu vào trực tiếp của generator.

## 6. Ranh giới bằng chứng

Mọi dòng thuộc **attack-side corpus** và có `attack_intent=boolean_predicate_injection`.

Điều này không đồng nghĩa mọi dòng đã được chứng minh exploit một ứng dụng thực. Các field runtime vẫn được giữ:
- `engine_validated`
- `behavior_confirmed`
- `exploit_confirmed`

Nếu chưa có lab/runtime evidence, chúng không được tự nâng thành `true`.

## 7. Phạm vi cố ý loại bỏ

V2 không sinh:
- SELECT/UNION data exfiltration
- stacked/destructive SQL
- time-based primitives
- contextual query-boundary breakout

Mục đích là buộc SeqGAN học **Boolean predicate structure/representation** thay vì trộn nhiều attack family.

## 8. File trong mỗi Y

- `attack_samples.csv`: bảng chính giàu metadata.
- `root_grammars.csv`: semantic roots.
- `structure_cells.csv`: representation/variation cells.
- `grammar_slots.csv`: typed slots và constraints.
- `validation_provenance.csv`: bằng chứng và trạng thái validation.
- `seqgan_attack_corpus.txt`: chỉ payload, một dòng/sample.
- `seqgan_attack_corpus.jsonl`: ID + lineage + payload.

## 9. Nguyên tắc dùng

Nếu cần huấn luyện bốn SeqGAN độc lập, mỗi model chỉ đọc `seqgan_attack_corpus.txt` của Y tương ứng.

Các CSV được giữ để:
1. audit trước khi train,
2. truy nguồn khi GAN sinh lỗi,
3. đo novelty/duplication,
4. xác định GAN đang học root/cell/representation nào.

Không có split benchmark trong corpus này.
