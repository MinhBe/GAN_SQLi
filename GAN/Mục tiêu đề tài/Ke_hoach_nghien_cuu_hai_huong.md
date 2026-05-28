# Kế hoạch mục tiêu đề tài: Generative models sinh payload SQL Injection để kiểm thử WAF

Ngày lập: 2026-05-26

## 1. Định vị lại đề tài

Đề tài này được xây lại từ đầu, không kế thừa pipeline, kết quả, dataset đã merge, hay các giả thuyết thực nghiệm cũ. Trọng tâm mới là:

> Nghiên cứu, tái hiện và đánh giá các phương pháp sinh payload SQL Injection bằng generative models, từ đó đề xuất một hướng nghiên cứu có thể kiểm chứng được về khả năng sinh payload hợp nghĩa, có tính mới, và hữu ích cho kiểm thử WAF trong môi trường an toàn.

Đề tài có 2 hướng song song:

1. **Hướng theo paper**: lấy paper làm chuẩn học thuật, tái hiện nghiên cứu, dùng dataset/testbed/metric gốc nếu có, sau đó phân tích khoảng trống.
2. **Hướng theo tài liệu của thầy**: lấy yêu cầu của thầy làm chuẩn lập luận nghiên cứu, gồm cách đặt vấn đề, dữ liệu, nhãn, evaluator, loss, baseline, failure analysis, và tiêu chí bảo vệ trước phản biện.

Hai hướng không thay thế nhau. Hướng theo paper giúp trả lời "người ta đã làm gì"; hướng theo thầy giúp trả lời "mình đang giải quyết bài toán gì và vì sao cách làm đáng tin".

## 2. Câu hỏi nghiên cứu

### Câu hỏi trung tâm

Generative models có thể sinh ra payload SQL Injection hợp nghĩa và có tính mới để kiểm thử WAF tốt hơn các baseline dựa trên rule/mutation truyền thống hay không?

### Câu hỏi con

1. Các paper hiện có sinh payload SQLi bằng cách nào: mutation, RL, GAN, LLM, hay hybrid?
2. Dataset gốc trong từng paper có đặc điểm gì, có đủ để tái hiện không, và có nguy cơ leakage/overfit không?
3. Payload sinh ra có còn hợp lệ về cú pháp, giữ ý đồ tấn công, và có khả năng bypass WAF trong testbed an toàn không?
4. Payload sinh ra có thực sự mới hay chỉ là biến đổi bề mặt của payload seed?
5. Nếu một phương pháp tốt hơn baseline, nó tốt hơn ở đâu: ASR, semantic preservation, diversity, transferability, hay khả năng hỗ trợ phòng thủ?

## 3. Phạm vi và ranh giới an toàn

Phạm vi:

- Đối tượng nghiên cứu là **payload SQLi và biến thể payload**, không phải khai thác hệ thống thực.
- Mọi đánh giá chạy trong lab/local testbed hoặc môi trường được cấp quyền.
- Báo cáo chính trình bày kết quả dạng thống kê, taxonomy, metric, failure case mức cao; không viết hướng dẫn bypass từng bước.
- Dataset của paper nào thì ưu tiên dùng đúng dataset gốc của paper đó. Nếu paper không mở dataset/code thì ghi rõ mức độ tái hiện: exact, partial, conceptual.

Không làm:

- Không dùng kết quả thực nghiệm cũ làm bằng chứng cho hướng mới.
- Không gom trộn tất cả dataset IDS như CIC-IDS2017, UNSW-NB15, NSL-KDD nếu paper SQLi/WAF đang tái hiện không dùng chung.
- Không test cloud WAF nếu không có môi trường sandbox/permission rõ ràng.
- Không công bố payload có tính hướng dẫn khai thác trực tiếp.

## 4. Hướng 1: Theo paper

### 4.1. Mục tiêu

Dùng paper làm trục chính để xây bản đồ nghiên cứu, tái hiện phương pháp, và rút ra khoảng trống có thể phát triển thành đề tài riêng.

Thành công của hướng này không phải là "chạy được nhiều model", mà là:

- Mỗi paper quan trọng có paper card rõ ràng.
- Biết paper nào tái hiện được, paper nào chỉ tái hiện một phần, paper nào không đủ căn cứ.
- Biết mỗi paper dùng dataset nào, WAF/testbed nào, metric nào.
- Biết claim của paper có đúng khi chạy lại trong môi trường của mình hay không.

### 4.2. Nhóm paper ưu tiên

| Nhóm | Paper / nguồn | Vai trò trong đề tài |
|---|---|---|
| Nền tảng GAN | Goodfellow 2014, WGAN-GP | Giải thích cơ sở adversarial learning và vấn đề ổn định train. |
| GAN cho text rời rạc | SeqGAN, Gumbel-Softmax GAN, RelGAN, MaskGAN, survey text GAN | Giải thích vì sao payload SQLi là chuỗi rời rạc và GAN khó train. |
| SQLi mutation/RL | WAF-A-MoLE, SSQLi, AdvSQLi | Baseline mạnh, cần tái hiện trước khi nói GAN/LLM tốt hơn. |
| GAN/GenAI cho SQLi | Lu 2022 GAN SQLi, GSQLi, BERT-GAN, VAE/CWGAN-GP SQLi | Paper gần trực tiếp với bài toán sinh/augmentation SQLi. |
| LLM cho SQLi/WAF | RADAGAS/RefleXQLi, các paper LLM adversarial SQLi mới | Hướng hiện đại để so với GAN, nhưng cần kiểm soát an toàn và chi phí. |
| Defense / robustness | Adversarial training, WAF hardening, semantic validation | Hướng đóng góp phòng thủ sau khi có kết quả kiểm thử. |

### 4.3. Mẫu paper card

Mỗi paper cần được tóm tắt theo cùng một mẫu:

```text
Paper:
Năm / venue:
Mục tiêu:
Loại phương pháp: mutation / RL / GAN / LLM / hybrid
Dataset gốc:
Code có mở không:
Testbed/WAF:
Metric:
Claim chính:
Kết quả cần tái hiện:
Giới hạn paper:
Có thể dùng làm baseline hay không:
Mức độ tái hiện: exact / partial / conceptual
```

### 4.4. Giai đoạn thực hiện theo paper

#### Giai đoạn P1: Lập bản đồ paper

Việc cần làm:

- Đọc paper OCR đã có trong `GAN/Paper/OCR`.
- Thêm paper ngoài nếu cần: WAF-A-MoLE, SSQLi, AdvSQLi, RADAGAS/RefleXQLi, PayloadsAllTheThings làm corpus/taxonomy.
- Loại paper không liên quan hoặc OCR nhận sai. Ví dụ file `GSQLi_2025_uncertain_from_old_notes` cần kiểm tra vì báo cáo OCR cho thấy title không liên quan SQLi.
- Tạo bảng so sánh `paper -> data -> method -> metric -> limitation`.

Sản phẩm:

- Bảng paper card.
- Bảng related work map.
- Danh sách paper lõi và paper phụ.

Tiêu chí xong:

- Có ít nhất 5 paper lõi.
- Mỗi paper lõi có dataset/testbed/metric rõ.
- Biết paper nào sẽ tái hiện trước.

#### Giai đoạn P2: Tái hiện baseline

Việc cần làm:

- Tái hiện mutation/rule baseline trước: WAF-A-MoLE style, sqlmap tamper style, AdvSQLi/tree-transform nếu có đủ mô tả.
- Dùng dataset gốc của từng paper nếu có.
- Nếu không có dataset gốc, dùng seed corpus từ PayloadsAllTheThings nhưng phải ghi là "replacement corpus", không gọi là tái hiện chính xác.
- Chạy trong testbed local: ModSecurity + OWASP CRS, Coraza nếu dùng được, và WAF-ML public nếu có code.

Sản phẩm:

- Baseline result table.
- Failure cases: malformed, duplicate, semantic broken, bypass fail.
- Reproduction notes.

Tiêu chí xong:

- Có ít nhất 2 baseline chạy được trên cùng testbed.
- Có ASR, validity, semantic preservation, diversity.
- Có log để tái lập.

#### Giai đoạn P3: Tái hiện generative model

Thứ tự ưu tiên:

1. GSQLi hoặc GAN SQLi gần nhất với bài toán.
2. SeqGAN/Gumbel nếu cần giải thích text discrete GAN.
3. LLM baseline có kiểm soát nếu cần so với hướng hiện đại.
4. Diffusion chỉ làm khi đã có thời gian, không đưa vào mục tiêu tối thiểu.

Sản phẩm:

- Model card cho từng model.
- Config train/test.
- Kết quả theo cùng metric với baseline.

Tiêu chí xong:

- Ít nhất 1 phương pháp generative được chạy end-to-end.
- So sánh được với mutation baseline.
- Có phân tích vì sao tốt/khá/kém.

#### Giai đoạn P4: Kiểm thử claim của paper

Câu hỏi cần trả lời:

- Paper claim bypass cao có lặp lại được không?
- Kết quả có phụ thuộc dataset/testbed không?
- Payload sinh ra có thực sự giữ ngữ nghĩa không?
- Payload mới có khác seed về cấu trúc hay chỉ khác bề mặt?
- Phương pháp có overfit vào WAF/rule cụ thể không?

Sản phẩm:

- Bảng `claim -> reproduction result -> explanation`.
- Threats to validity.
- Đề xuất khoảng trống.

## 5. Hướng 2: Theo tài liệu của thầy

### 5.1. Mục tiêu

Hướng này biến các yêu cầu của thầy thành khung nghiên cứu có thể thuyết trình và bảo vệ:

- Đặt vấn đề sắc.
- Giải thích dữ liệu và nhãn có căn cứ.
- Có pipeline tổng thể.
- Có evaluator rõ vai trò.
- Có metric gắn với mục tiêu.
- Có baseline và ablation.
- Biết tự phê bình failure.

Nếu hướng theo paper trả lời "người ta làm gì", hướng theo thầy trả lời "mình lập luận nghiên cứu như thế nào".

### 5.2. Một câu bài toán

> Bài toán là sinh và đánh giá các payload SQL Injection tổng hợp trong môi trường an toàn, sao cho payload vừa hợp lệ về cú pháp, giữ được ý đồ tấn công, có tính mới so với seed corpus, và giúp kiểm thử WAF tốt hơn các phương pháp mutation/rule-based baseline.

### 5.3. What / How / Why

| Câu hỏi | Câu trả lời cần có |
|---|---|
| What | Sinh payload SQLi, không sinh toàn bộ request/web app; đánh giá trên WAF/testbed local. |
| How | Dùng seed corpus, taxonomy, baseline mutation/RL/GAN/LLM; kiểm tra bằng parser, semantic/effect validator, WAF evaluator, diversity metric. |
| Why | WAF và detector cần được kiểm thử với biến thể mới; payload thủ công/rule-based có giới hạn; generative model có thể học phân phối và đề xuất biến thể ngoài template đã biết. |

### 5.4. Dữ liệu và nguồn seed

Nguồn dữ liệu chia thành 3 lớp:

1. **Dataset gốc theo paper**: dùng để tái hiện paper. Không trộn nếu paper không làm vậy.
2. **PayloadsAllTheThings SQL Injection**: dùng làm seed corpus/taxonomy thực tế, không xem là paper học thuật.
3. **Dataset bổ sung cho testbed**: DVWA/Juice Shop/custom vulnerable app chỉ dùng để validate effect trong lab.

PayloadsAllTheThings được thêm vào hướng mới theo gợi ý của thầy:

- Vai trò: seed corpus, taxonomy SQLi, known payload bank, known WAF-bypass references.
- Không được dùng như bằng chứng khoa học độc lập.
- Phải pin snapshot/commit, ghi license, và tạo data card.
- Phải tách `known payload` và `generated payload` để đo novelty thật.

Artifact cần có:

```text
payload_source_card:
  source_name:
  source_url:
  license:
  snapshot_date_or_commit:
  sql_type:
  dbms:
  original_label:
  verified_label:
  usable:
  notes:
```

### 5.5. Nhãn và evaluator

Cần tách 5 loại nhãn/score:

| Tên | Ý nghĩa | Cách kiểm chứng |
|---|---|---|
| `syntax_valid` | Payload parse/execute được | SQL parser / DB lab |
| `attack_intent` | Có ý đồ SQLi | rule/evaluator/human review |
| `semantic_preserved` | Giữ ý đồ so với seed | AST/effect equivalence trong lab |
| `waf_bypass` | Qua WAF trong testbed | ModSecurity/CRS, Coraza, WAF-ML |
| `novelty` | Khác seed có ý nghĩa | token/AST/Levenshtein/embedding |

Không được gộp các nhãn này thành một điểm duy nhất nếu chưa giải thích trong loss/metric.

### 5.6. Metric chính

Metric tối thiểu:

- `Validity rate`: tỷ lệ payload hợp lệ cú pháp.
- `Semantic preservation rate`: tỷ lệ payload giữ được ý đồ tấn công.
- `ASR`: tỷ lệ payload bypass WAF trong lab.
- `Uniqueness`: tỷ lệ không trùng lặp.
- `Novelty`: độ khác seed theo token/AST/embedding.
- `Diversity`: entropy, self-BLEU/Levenshtein/AST family coverage.
- `Transferability`: payload qua WAF A có qua WAF B không.
- `Failure distribution`: malformed, benignized, duplicate, blocked, timeout.

Metric không nên làm trung tâm:

- Accuracy chung chung.
- Điểm discriminator nếu không gắn với WAF/effect.
- Số lượng payload sinh ra nếu không có validity/semantic.

### 5.7. Pipeline tổng thể

Pipeline nghiên cứu để thuyết trình:

```text
Paper/Dataset selection
  -> Paper card + dataset card
  -> Seed corpus + SQLi taxonomy
  -> Safe split: known seed / train / dev / test / held-out taxonomy
  -> Baseline generation: rule, mutation, tree-transform, RL
  -> Generative generation: GAN / Gumbel / LLM / optional diffusion
  -> Validation: syntax + semantic/effect
  -> WAF evaluation: local WAF testbed
  -> Diversity + novelty analysis
  -> Failure analysis
  -> Defense recommendation
```

## 6. Điểm giao nhau giữa 2 hướng

| Thành phần | Hướng theo paper | Hướng theo thầy |
|---|---|---|
| Vấn đề | Lấy từ khoảng trống paper | Viết thành what/how/why rõ ràng |
| Dữ liệu | Dataset gốc của paper | Dataset card, nhãn, split an toàn |
| Baseline | Tái hiện baseline paper | Giải thích baseline vì sao công bằng |
| Model | Tái hiện phương pháp paper | Giải thích input/output/loss/evaluator |
| Evaluation | Lặp lại metric paper | Bổ sung validity, semantic, novelty, diversity |
| Đóng góp | Chỉ ra paper còn thiếu gì | Đề xuất protocol/model/defense có căn cứ |

Kết quả tốt nhất là: một paper reproduction có số liệu, được đặt trong một khung lập luận theo yêu cầu của thầy.

## 7. Kế hoạch giai đoạn

### Giai đoạn 1: Đặt vấn đề và lập bản đồ nghiên cứu

Thời gian: 1-2 tuần.

Việc cần làm:

- Viết 1 trang problem statement.
- Lập danh sách paper lõi và paper phụ.
- Tạo paper card cho từng paper.
- Tạo taxonomy SQLi từ paper + PayloadsAllTheThings.
- Chốt 2-3 paper ưu tiên tái hiện.

Sản phẩm:

- `problem_statement.md`
- `paper_cards.md`
- `sqli_taxonomy.md`

Tiêu chí nghiệm thu:

- Nói được bài toán trong 1 câu.
- Nói được vì sao cần generative model thay vì chỉ dùng mutation.
- Nói được paper nào là baseline bắt buộc.

### Giai đoạn 2: Data card và seed corpus

Thời gian: 1-2 tuần.

Việc cần làm:

- Lập data card cho dataset gốc của từng paper.
- Lập source card cho PayloadsAllTheThings.
- Lọc seed theo type/DBMS/context.
- Định nghĩa split an toàn: không để payload cùng template/AST family xuất hiện ở cả train và test nếu đang đo novelty.
- Định nghĩa nhãn: syntax, attack intent, semantic preservation, bypass, novelty.

Sản phẩm:

- `dataset_cards.md`
- `payload_source_card_payloadsallthethings.md`
- `seed_corpus_manifest.csv`

Tiêu chí nghiệm thu:

- Mỗi seed có nguồn và nhãn tối thiểu.
- Biết seed nào đến từ paper, seed nào đến từ PayloadsAllTheThings.
- Có rule rõ ràng để tách known/novel.

### Giai đoạn 3: Tái hiện baseline

Thời gian: 2-4 tuần.

Việc cần làm:

- Chạy mutation baseline.
- Chạy tree-transform/RL baseline nếu paper đủ thông tin.
- Dùng cùng testbed local.
- Đo validity, semantic preservation, ASR, novelty, diversity.

Sản phẩm:

- `baseline_results.md`
- `baseline_failure_analysis.md`
- log tái lập.

Tiêu chí nghiệm thu:

- Có ít nhất 2 baseline.
- Có bảng metric thống nhất.
- Có failure examples dạng thống kê.

### Giai đoạn 4: Tái hiện generative paper

Thời gian: 3-6 tuần.

Việc cần làm:

- Chọn 1 phương pháp GAN/LLM gần nhất với paper lõi.
- Tái hiện theo mức exact/partial/conceptual.
- So sánh với baseline trên cùng testbed.
- Phân tích mode collapse/reward sparsity/semantic break nếu có.

Sản phẩm:

- `generative_reproduction_results.md`
- `model_card.md`
- `claim_verification_table.md`

Tiêu chí nghiệm thu:

- Có kết quả end-to-end.
- Có so sánh với baseline.
- Có phân tích vì sao paper claim đúng/sai/không tái hiện được.

### Giai đoạn 5: Đề xuất hướng riêng

Thời gian: 1-2 tuần sau khi có kết quả tái hiện.

Chỉ chọn 1 trong 3 hướng đề xuất:

1. **Protocol contribution**: benchmark đánh giá payload SQLi generated theo validity/semantic/novelty/WAF.
2. **Model contribution**: một cơ chế reward/loss kết hợp validity, semantic, WAF, diversity.
3. **Defense contribution**: adversarial training hoặc rule hardening dựa trên failure của payload sinh.

Khuyến nghị: bắt đầu bằng **Protocol contribution**, vì chắc hơn và hợp với việc "tái hiện paper + kiểm thử quan điểm".

Sản phẩm:

- `research_gap_and_proposal.md`
- `experiment_plan_next.md`

Tiêu chí nghiệm thu:

- Đề xuất có baseline.
- Đề xuất có metric.
- Đề xuất có phạm vi hẹp có thể làm.
- Đề xuất không phụ thuộc vào việc train quá nhiều model lớn.

### Giai đoạn 6: Viết báo cáo và slide

Thời gian: 1-2 tuần.

Slide khuyến nghị:

1. Title và một câu bài toán.
2. Why hard: syntax, semantics, WAF behavior, discrete text, dual-use.
3. Related work map.
4. Paper reproduction plan.
5. PayloadsAllTheThings as seed taxonomy.
6. Dataset card và split an toàn.
7. Testbed và safety boundary.
8. Baseline methods.
9. Generative methods.
10. Metrics.
11. Claim verification.
12. Failure analysis.
13. Research gap.
14. Proposed direction.
15. Next milestone.

## 8. Phản biện xây dựng

### Điểm mạnh của hướng mới

- Không bị mắc vào kết quả cũ.
- Có trục học thuật rõ: paper -> reproduction -> gap -> proposal.
- Có trục thực tế rõ: PayloadsAllTheThings -> taxonomy -> seed corpus -> WAF testbed.
- Dễ thuyết phục thầy hơn vì có what/how/why và có tiêu chí nghiệm thu.

### Điểm yếu cần tránh

- Quá tham: nếu làm tất cả GAN, LLM, diffusion, WAF cloud, IDS dataset thì sẽ vỡ trận.
- Nhập nhằng giữa "sinh payload" và "phát hiện SQLi".
- Nhập nhằng giữa "valid SQL" và "malicious SQLi".
- Nhập nhằng giữa "bypass WAF" và "có giá trị phòng thủ".
- Dùng PayloadsAllTheThings mà không kiểm chứng lại nhãn/ngữ nghĩa.

### Quyết định thiết kế để giữ đề tài gọn

- Phase 1 chỉ chọn 2-3 paper lõi để tái hiện.
- PayloadsAllTheThings chỉ là seed/taxonomy, không phải dataset duy nhất.
- Testbed mặc định là local WAF, không cloud WAF.
- Diffusion để optional.
- LLM chỉ làm baseline có kiểm soát nếu cần, không biến thành đề tài LLM.

## 9. Checklist trước khi gặp thầy

- [ ] Có một câu bài toán mới, không liên quan pipeline cũ.
- [ ] Có 2 hướng rõ: theo paper và theo tài liệu/thầy.
- [ ] Có danh sách paper lõi và mức độ tái hiện.
- [ ] Có vai trò của PayloadsAllTheThings: seed corpus/taxonomy.
- [ ] Có định nghĩa dataset card và source card.
- [ ] Có split an toàn và novelty split.
- [ ] Có metric: validity, semantic, ASR, novelty, diversity, transferability.
- [ ] Có testbed local và ranh giới an toàn.
- [ ] Có baseline trước generative model.
- [ ] Có kế hoạch đề xuất sau khi tái hiện paper.

## 10. Câu nói ngắn để trình bày với thầy

> Em xin xây lại hướng nghiên cứu theo hai trục. Trục thứ nhất là trục paper: em chọn các paper lõi về SQLi payload generation và WAF evasion, dùng dataset/testbed gốc để tái hiện và kiểm thử claim. Trục thứ hai là trục theo yêu cầu nghiên cứu của thầy: em xây data card, taxonomy, evaluator, metric và split an toàn để đảm bảo mọi kết quả có căn cứ. PayloadsAllTheThings sẽ được dùng như seed corpus và taxonomy thực tế, không thay thế paper. Sau khi tái hiện xong, em sẽ chọn một khoảng trống hẹp để đề xuất: protocol đánh giá payload SQLi generated, model reward/loss mới, hoặc hướng phòng thủ dựa trên failure của WAF.
