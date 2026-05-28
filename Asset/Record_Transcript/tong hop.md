# Tổng hợp định hướng nghiên cứu hiện tại

## 1. Tổng quan

Tài liệu này tổng hợp định hướng hiện tại cho đề tài sinh và đánh giá payload SQL Injection bằng generative models. Trọng tâm là xây dựng một kế hoạch nghiên cứu rõ ràng, có thể kiểm chứng và bám sát mục tiêu hiện tại.

Mục tiêu nghiên cứu:

> Sinh và đánh giá các payload SQL Injection tổng hợp sao cho payload hợp lệ về cú pháp, giữ được ý đồ tấn công, có tính mới so với seed corpus, và hữu ích cho kiểm thử WAF trong testbed được kiểm soát.

Phạm vi chính:

- Đối tượng nghiên cứu là payload SQLi và biến thể payload.
- Đánh giá chỉ thực hiện trong local lab hoặc môi trường được cấp quyền.
- Kết quả cần được trình bày bằng metric, taxonomy, bảng so sánh và failure analysis.
- Hướng đề xuất ưu tiên là một protocol đánh giá payload SQLi generated có căn cứ.

Không mở rộng sang:

- Khai thác hệ thống thực.
- Cloud WAF khi chưa có sandbox hoặc permission rõ ràng.
- Công bố hướng dẫn bypass từng bước.
- Dùng bằng chứng không gắn trực tiếp với protocol đánh giá hiện tại.

## 2. Câu hỏi nghiên cứu

Câu hỏi trung tâm:

> Generative models có thể sinh payload SQL Injection hợp nghĩa, có tính mới và hữu ích cho kiểm thử WAF tốt hơn các baseline rule/mutation truyền thống hay không?

Câu hỏi con:

1. Payload sinh ra có hợp lệ về cú pháp không?
2. Payload sinh ra có giữ được ý đồ SQL Injection không?
3. Payload sinh ra có vượt qua WAF trong testbed an toàn không?
4. Payload sinh ra có thực sự mới so với seed corpus không?
5. Nếu tốt hơn baseline, phương pháp tốt hơn ở khía cạnh nào: validity, semantic preservation, ASR, novelty, diversity hay transferability?

## 3. Nguyên tắc trình bày

Phần trình bày cần đi theo logic `What / How / Why`:

| Câu hỏi | Nội dung cần trả lời |
|---|---|
| What | Sinh loại payload nào, đầu vào là gì, đầu ra là gì, tiêu chí thành công là gì. |
| How | Dữ liệu được lấy và xử lý thế nào, baseline/model sinh payload ra sao, evaluator/WAF tham gia ở đâu. |
| Why | Vì sao cần generative model thay vì chỉ dùng template, rule hoặc mutation truyền thống. |

Nguyên tắc diễn đạt:

- Trình bày theo hướng kế hoạch, tiêu chí và bằng chứng.
- Mỗi thành phần trong pipeline phải có input, output, vai trò và tiêu chí kiểm tra.
- Mỗi claim cần gắn với metric hoặc bằng chứng kiểm chứng được.
- Không dùng các cụm mơ hồ như "dữ liệu lớn", "mô hình tốt", "payload mới" nếu chưa định nghĩa cách đo.

## 4. Khung nghiên cứu tổng thể

Pipeline nghiên cứu đề xuất:

```text
Paper/Dataset selection
  -> Paper card + dataset card
  -> Seed corpus + SQLi taxonomy
  -> Safe split: train / dev / test / held-out taxonomy
  -> Baseline generation: rule / mutation / tree-transform / RL
  -> Generative generation: GAN / Gumbel / LLM
  -> Validation: syntax + semantic/effect
  -> WAF evaluation: local WAF testbed
  -> Novelty + diversity analysis
  -> Failure analysis
  -> Research gap / proposal
```

Vai trò các nhóm thành phần:

| Thành phần | Vai trò | Đầu ra cần có |
|---|---|---|
| Paper và related work | Xác định nền tảng học thuật, baseline và khoảng trống | Paper card, related work map |
| Dataset và seed corpus | Cung cấp payload gốc, taxonomy và dữ liệu tái hiện | Dataset card, source card, seed manifest |
| Baseline | Tạo mốc so sánh công bằng trước khi đánh giá generative model | Baseline result table |
| Generative model | Sinh payload mới để so sánh với baseline | Model card, generated payload set |
| Evaluator | Kiểm tra syntax, intent, semantic, WAF bypass và novelty | Metric table, failure distribution |
| Proposal | Chọn một khoảng trống hẹp để phát triển thành đóng góp | Research gap and proposal |

## 5. Thành phần chi tiết

### 5.1. Dữ liệu

Dữ liệu cần được mô tả bằng data card hoặc source card. Mỗi nguồn dữ liệu cần có:

- Tên nguồn dữ liệu.
- Nguồn lấy dữ liệu.
- License hoặc điều kiện sử dụng nếu có.
- Số lượng mẫu ban đầu.
- Số lượng mẫu dùng được.
- Quy tắc lọc trùng, lọc lỗi và chuẩn hóa.
- Nhãn có sẵn và nhãn cần kiểm chứng lại.
- Vai trò trong nghiên cứu: train, dev, test, held-out hoặc seed taxonomy.

Các nhóm dữ liệu cần tách rõ:

1. **Dataset gốc theo paper**: dùng để tái hiện paper.
2. **PayloadsAllTheThings SQL Injection**: dùng làm seed corpus và taxonomy thực tế.
3. **Testbed lab**: dùng để kiểm tra effect và phản hồi WAF trong môi trường an toàn.

### 5.2. Nhãn và evaluator

Không gộp mọi đánh giá vào một điểm duy nhất. Cần tách các nhãn/score chính:

| Nhãn/score | Ý nghĩa | Cách kiểm chứng |
|---|---|---|
| `syntax_valid` | Payload hợp lệ về cú pháp hoặc có thể parse/execute trong lab | SQL parser hoặc DB lab |
| `attack_intent` | Payload thể hiện ý đồ SQL Injection | Rule, evaluator hoặc human review |
| `semantic_preserved` | Payload giữ ý đồ so với seed hoặc template gốc | AST/effect equivalence trong lab |
| `waf_bypass` | Payload đi qua WAF trong testbed | ModSecurity/CRS, Coraza hoặc WAF-ML |
| `novelty` | Payload khác seed một cách có ý nghĩa | Token/AST/Levenshtein/embedding |

Evaluator cần kiểm tra:

- Cú pháp và khả năng thực thi.
- Ý đồ SQLi.
- Khả năng bypass WAF trong local testbed.
- Độ mới và độ đa dạng của payload sinh ra.
- Failure case để phục vụ phân tích.

### 5.3. Metric

Metric chính:

| Metric | Ý nghĩa |
|---|---|
| `Validity rate` | Tỷ lệ payload hợp lệ về cú pháp. |
| `Semantic preservation rate` | Tỷ lệ payload giữ được ý đồ tấn công. |
| `ASR` | Tỷ lệ payload bypass WAF trong lab. |
| `Uniqueness` | Tỷ lệ payload không trùng lặp. |
| `Novelty` | Độ khác seed theo token, AST, Levenshtein hoặc embedding. |
| `Diversity` | Mức đa dạng theo entropy, self-BLEU, Levenshtein hoặc AST family coverage. |
| `Transferability` | Payload qua WAF A có qua WAF B không. |
| `Failure distribution` | Phân bố lỗi: malformed, benignized, duplicate, blocked, timeout. |

Metric không nên làm trung tâm:

- Accuracy chung chung.
- Điểm discriminator nếu không gắn với WAF/effect.
- Số lượng payload sinh ra nếu không đi kèm validity và semantic.

### 5.4. Baseline

Baseline cần được thực hiện trước generative model để có mốc so sánh công bằng.

Baseline ưu tiên:

1. Rule-based hoặc template-based generation.
2. Mutation baseline kiểu WAF-A-MoLE/sqlmap tamper.
3. Tree-transform hoặc RL baseline nếu paper có đủ mô tả.

Yêu cầu với baseline:

- Chạy trên cùng seed corpus hoặc cùng split.
- Chạy trên cùng local WAF testbed.
- Đo bằng cùng bộ metric.
- Có failure analysis, không chỉ báo cáo số tốt nhất.

### 5.5. Generative model

Generative model chỉ nên đưa vào sau khi baseline và evaluator đã rõ.

Thông tin cần xác định cho mỗi model:

- Input của model.
- Output của model.
- Cách tạo payload.
- Cách evaluator tham gia vào train/test.
- Metric so sánh với baseline.
- Giới hạn và điều kiện áp dụng.

Thứ tự ưu tiên:

1. Phương pháp generative gần nhất với paper lõi.
2. SeqGAN/Gumbel nếu cần giải thích bài toán text rời rạc.
3. LLM baseline có kiểm soát nếu cần so với hướng hiện đại.
4. Diffusion chỉ để optional.

## 6. Lộ trình thực hiện

### Giai đoạn 1: Chốt bài toán và related work

Việc cần làm:

- Viết problem statement một trang.
- Lập danh sách paper lõi về SQLi payload generation và WAF evasion.
- Tạo paper card cho từng paper quan trọng.
- Xác định paper nào có thể tái hiện exact, partial hoặc conceptual.
- Xác định baseline bắt buộc.

Sản phẩm:

- `problem_statement.md`
- `paper_cards.md`
- `related_work_map.md`

Tiêu chí nghiệm thu:

- Nói được bài toán trong một câu.
- Nói được vì sao cần generative model.
- Nói được paper nào là baseline và vì sao.

### Giai đoạn 2: Chuẩn hóa dữ liệu và seed corpus

Việc cần làm:

- Lập dataset card cho từng nguồn dữ liệu.
- Lập source card cho PayloadsAllTheThings.
- Tách rõ known payload và generated payload.
- Định nghĩa split an toàn để tránh leakage giữa train và test.
- Định nghĩa nhãn tối thiểu: syntax, attack intent, semantic preservation, bypass, novelty.

Sản phẩm:

- `dataset_cards.md`
- `payload_source_card_payloadsallthethings.md`
- `seed_corpus_manifest.csv`
- `split_policy.md`

Tiêu chí nghiệm thu:

- Mỗi seed có nguồn rõ.
- Có quy tắc tách train/dev/test/held-out.
- Có cách đo novelty không phụ thuộc vào cảm tính.

### Giai đoạn 3: Tái hiện baseline

Việc cần làm:

- Chạy ít nhất hai baseline phù hợp.
- Dùng cùng testbed local cho mọi phương pháp.
- Đo validity, semantic preservation, ASR, novelty và diversity.
- Ghi nhận failure distribution.

Sản phẩm:

- `baseline_results.md`
- `baseline_failure_analysis.md`
- log tái lập thí nghiệm.

Tiêu chí nghiệm thu:

- Có ít nhất hai baseline chạy được.
- Có bảng metric thống nhất.
- Có phân tích failure ở mức thống kê.

### Giai đoạn 4: Thử generative model

Việc cần làm:

- Chọn một hướng generative gần nhất với paper lõi.
- Xác định input/output của model.
- Xác định evaluator tham gia ở bước nào.
- So sánh với baseline trên cùng seed/testbed/metric.
- Phân tích điểm mạnh, điểm yếu và điều kiện áp dụng.

Sản phẩm:

- `generative_reproduction_results.md`
- `model_card.md`
- `claim_verification_table.md`

Tiêu chí nghiệm thu:

- Có kết quả end-to-end cho ít nhất một phương pháp generative.
- So sánh được với baseline.
- Giải thích được kết quả bằng metric và failure analysis.

### Giai đoạn 5: Đề xuất hướng riêng

Ưu tiên đề xuất theo thứ tự:

1. Protocol đánh giá payload SQLi generated theo validity, semantic, novelty và WAF.
2. Cơ chế reward/loss kết hợp validity, semantic, WAF và diversity.
3. Hướng phòng thủ dựa trên failure của payload sinh ra.

Sản phẩm:

- `research_gap_and_proposal.md`
- `experiment_plan_next.md`

Tiêu chí nghiệm thu:

- Đề xuất có baseline.
- Đề xuất có metric.
- Đề xuất có phạm vi đủ hẹp để thực hiện.
- Đề xuất không phụ thuộc vào việc train quá nhiều model lớn.

## 7. Deliverable

Tài liệu tối thiểu:

- Problem statement một trang.
- Paper card cho nhóm paper lõi.
- Related work map.
- Dataset card và source card.
- SQLi taxonomy.
- Split policy.
- Baseline result table.
- Metric definition.
- Model card cho phương pháp generative được chọn.
- Claim verification table.
- Failure analysis.
- Research gap and proposal.

Slide nên có:

1. Title và một câu bài toán.
2. Why hard: syntax, semantics, WAF behavior, discrete text, dual-use.
3. Related work map.
4. Dataset/source card.
5. Pipeline tổng thể.
6. Safe split và novelty split.
7. Baseline methods.
8. Generative method.
9. Evaluator và local WAF testbed.
10. Metrics.
11. Claim verification.
12. Failure analysis.
13. Research gap.
14. Proposed direction.
15. Next milestone.

## 8. Checklist trước khi gặp thầy

- [ ] Có một câu bài toán rõ ràng.
- [ ] Có câu trả lời cho `What / How / Why`.
- [ ] Có related work map và paper card.
- [ ] Có data card/source card cho dữ liệu.
- [ ] Có định nghĩa nhãn và evaluator.
- [ ] Có split an toàn và novelty split.
- [ ] Có baseline trước generative model.
- [ ] Có pipeline tổng thể.
- [ ] Có local WAF testbed.
- [ ] Có metric chính: validity, semantic preservation, ASR, novelty, diversity, transferability.
- [ ] Có tiêu chí nghiệm thu cho từng giai đoạn.
- [ ] Có hướng đề xuất hẹp và có thể kiểm chứng.

## 9. Câu trình bày ngắn

> Em định hướng đề tài theo hướng sinh và đánh giá payload SQL Injection trong môi trường an toàn. Trọng tâm hiện tại là xây một protocol nghiên cứu có thể kiểm chứng: dữ liệu có source card, split an toàn, baseline rõ, evaluator rõ và metric gắn với mục tiêu kiểm thử WAF. Sau khi tái hiện baseline và một phương pháp generative trên cùng testbed, em sẽ chọn một khoảng trống hẹp để đề xuất, ưu tiên protocol đánh giá payload SQLi generated theo validity, semantic preservation, novelty và WAF behavior.
