# Kế hoạch triển khai đề tài GAN sinh payload SQL Injection để kiểm thử WAF

Ngày lập: 2026-05-27  
Phạm vi: kế hoạch nghiên cứu, triển khai, đánh giá và trình bày đề tài theo góp ý của người hướng dẫn.

> Câu hỏi trung tâm: Liệu các mô hình tạo sinh như GAN, LLM hoặc diffusion có thể sinh ra payload SQL Injection hợp nghĩa, có tính mới, và cải thiện hiệu quả kiểm thử WAF so với các baseline dựa trên rule, template hoặc mutation truyền thống hay không?

## Mục lục

1. [Phần 1: Mong muốn của người hướng dẫn](#phần-1-mong-muốn-của-người-hướng-dẫn)
2. [Phần 2: Tài nguyên và kế hoạch thực hiện](#phần-2-tài-nguyên-và-kế-hoạch-thực-hiện)
3. [Checklist nghiệm thu trước buổi trình bày tiếp theo](#checklist-nghiệm-thu-trước-buổi-trình-bày-tiếp-theo)

---

# Phần 1: Mong muốn của người hướng dẫn

## 1. Kết luận ngắn

Người hướng dẫn không chỉ muốn nghe câu "em dùng GAN để sinh payload SQL Injection". Phần trình bày cần chứng minh năng lực nghiên cứu:

- Biết đặt vấn đề: sinh payload để làm gì, tiêu chí thành công là gì.
- Biết vì sao cần làm: khoảng trống của rule, template, mutation, RL, GAN, LLM hiện tại là gì.
- Biết dữ liệu đến từ đâu: nguồn, số dòng, trạng thái tải, số dòng dùng được, nhãn và rủi ro nhiễu nhãn.
- Biết kiến trúc vận hành ra sao: Generator, Discriminator, Evaluator/WAF nằm ở đâu trong training và evaluation.
- Biết loss và metric gắn với mục tiêu nào: realism, validity, bypass, diversity, novelty, collapse.
- Biết điểm nghẽn hiện tại: mode collapse sau khoảng 500 vòng lặp, Discriminator quá mạnh, reward/loss chưa hoàn chỉnh.
- Biết bước tiếp theo để biến demo thành luận văn hoặc bài báo.

## 2. Câu trả lời cốt lõi cần chuẩn bị

| Câu hỏi của thầy | Câu trả lời cần có |
|---|---|
| What? | Sinh payload SQL Injection loại nào, đầu vào/đầu ra là gì, dùng để augmentation, adversarial testing hay benchmark WAF. |
| How? | GAN sinh payload qua pipeline nào, Discriminator học gì, WAF/Evaluator tham gia ở đâu, loss tính thế nào. |
| Why? | Vì sao cần GAN thay vì template, rule hoặc random mutation; GAN giải quyết khoảng trống nào. |
| Data? | Dataset tên gì, nguồn nào, file nào, raw rows bao nhiêu, usable rows bao nhiêu, loại bỏ gì, nhãn kiểm chứng ra sao. |
| Label? | Phân biệt valid syntax, malicious intent, bypass/non-bypass, realistic/non-realistic. |
| Loss? | Generator tối ưu realism, validity, bypass và diversity như thế nào; Discriminator phân biệt real/fake hoặc thêm class nào. |
| Evaluation? | So với baseline nào, trên WAF nào, metric nào, protocol ra sao, có an toàn và tái lập không. |
| Failure? | Mode collapse đo bằng gì, nguyên nhân giả thuyết là gì, thí nghiệm sửa lỗi tiếp theo là gì. |
| Novelty? | Đóng góp nằm ở dataset, evaluator, loss, architecture, benchmark hay protocol. |

## 3. Pipeline tổng thể cần trình bày

```text
Raw payload/data
  -> cleaning / de-duplication / normalization
  -> template extraction / safe split
  -> tokenization
  -> Generator
  -> generated payload candidates
  -> syntax + semantic evaluator
  -> Discriminator realism score
  -> WAF/testbed evaluation
  -> metrics: validity, diversity, bypass, novelty, collapse
```

Điểm cần làm rõ:

- WAF dùng để đánh nhãn, làm feedback reward, hay chỉ dùng để evaluation.
- Training path và evaluation path phải được tách riêng trên sơ đồ.
- Mỗi mũi tên cần ghi rõ dữ liệu đi qua: token sequence, payload string, score, label hoặc reward.
- Nếu WAF thật quá chậm, cần nêu proxy/evaluator thay thế trong training.

## 4. Các tiêu chí nghiên cứu người hướng dẫn đang yêu cầu

### 4.1. Vấn đề phải sắc

Một câu định vị:

> Đề tài nghiên cứu mô hình sinh payload SQL Injection bằng GAN với mục tiêu sinh ra payload hợp lệ, đa dạng, realistic và được đánh giá bằng cả evaluator nội bộ lẫn WAF/testbed thực tế trong môi trường an toàn.

Cần nêu rõ:

- Đối tượng nghiên cứu là payload, không phải khai thác hệ thống thật.
- Phạm vi SQLi nào được xét: boolean-based, union-based, time-based, error-based hoặc subset phù hợp.
- Thành công được định nghĩa bằng metric, không bằng cảm nhận.
- Câu hỏi nghiên cứu chính: GAN có tốt hơn template/mutation baseline hay không.

### 4.2. Related work phải dẫn tới khoảng trống

Không liệt kê paper rời rạc. Cần gom theo nhóm:

| Nhóm phương pháp | Ví dụ | Vai trò trong đề tài | Khoảng trống cần chỉ ra |
|---|---|---|---|
| Rule/template | SQLMap payload, SecLists, PayloadsAllTheThings | Baseline đơn giản và dễ tái lập | Dễ trùng lặp, novelty thấp, khó phủ biến thể mới. |
| Mutation/fuzzing | WAF-A-MoLE, AdvSQLi | Baseline mạnh cho bypass WAF | Có thể phụ thuộc seed/template, cần kiểm tra semantic preservation. |
| RL/RNN | SSQLi, SeqGAN-style generation | Học chuỗi rời rạc bằng reward | Reward sparse, training khó ổn định. |
| GAN cho text | SeqGAN, Gumbel-Softmax GAN, RelGAN, MaskGAN | Cơ sở thuật toán cho dữ liệu token rời rạc | Mode collapse, validity thấp nếu không có evaluator. |
| LLM-based | Prompting, RAG, fine-tuning | Baseline hiện đại, chất lượng ngôn ngữ cao | Chi phí, thiếu minh bạch, kiểm soát an toàn và reproducibility khó. |
| Defense/evaluator | ModSecurity CRS, Coraza, WAF-ML | Đích đánh giá và đề xuất phòng thủ | Cần protocol an toàn, không test trái phép. |

### 4.3. Dữ liệu phải truy vết được

Cần có bảng dataset bắt buộc:

| Field | Nội dung cần điền |
|---|---|
| `name` | Tên dataset/repository. |
| `source` | URL hoặc nguồn paper. |
| `file` | File local cụ thể. |
| `raw rows` | Số dòng ban đầu. |
| `usable rows` | Số dòng dùng được sau lọc. |
| `removed rows` | Duplicate, invalid, encoding lỗi, không phải payload, thiếu nhãn. |
| `labels` | Nguồn nhãn: dataset gốc, parser, rule, WAF, evaluator, human review. |
| `split rule` | Cách chia train/dev/test để tránh leakage. |
| `status` | Chưa tải, đã tải, đã lọc, đã token hóa, đã kiểm chứng. |
| `risk` | Rủi ro nhiễu nhãn, license, dữ liệu nhạy, overfit. |

Cần phân biệt rõ các nhãn:

- `syntax_valid`: payload có hợp cú pháp theo parser/validator hay không.
- `malicious_intent`: payload có ý đồ SQLi hay không.
- `bypass`: payload có đi qua WAF trong testbed hay không.
- `realistic`: payload có giống mẫu thực tế/dataset gốc hay không.
- `novel`: payload có khác seed/template hay chỉ là biến thể bề mặt.

### 4.4. Kiến trúc phải giải thích được

Sơ đồ mô hình cần có tối thiểu:

| Khối | Input | Output | Vai trò |
|---|---|---|---|
| Generator | Noise `z`, condition, template hoặc prefix | Chuỗi token/payload candidate | Sinh payload mới. |
| Discriminator | Payload thật và payload sinh | Real/fake score, có thể thêm validity/class score | Học realism và hỗ trợ reward. |
| Syntax/Semantic Evaluator | Payload candidate | Validity score, semantic preservation score | Lọc payload vô nghĩa. |
| WAF/Testbed | HTTP request hoặc payload trong container | Allow/block/log/rule hit | Đánh giá bypass trong môi trường được phép. |
| Metric Aggregator | Kết quả từ evaluator và WAF | ASR, FPR, diversity, novelty, transferability | So sánh mô hình với baseline. |

Training path và evaluation path:

- Training path: dùng Discriminator, evaluator nhẹ, có thể dùng proxy reward.
- Evaluation path: chạy payload trên WAF/testbed thật, log kết quả, không cập nhật model trực tiếp nếu chưa thiết kế reward an toàn.

### 4.5. Loss và metric phải gắn mục tiêu

| Mục tiêu | Signal/Loss dự kiến | Metric kiểm tra | Ghi chú |
|---|---|---|---|
| Realism | Adversarial loss từ Discriminator | Discriminator score, human/evaluator review | Không được đồng nhất realism với bypass. |
| Syntax validity | Parser/validator reward hoặc penalty | Validity rate | Có thể dùng SQL parser hoặc rule validator. |
| Semantic preservation | So khớp template/AST/effect class | Semantic preservation rate | Tránh payload vô nghĩa chỉ để bypass. |
| WAF bypass | WAF/proxy reward | ASR | Chỉ trong testbed hoặc môi trường được cấp phép. |
| Diversity | Entropy, uniqueness, distance penalty | Unique ratio, Levenshtein/AST distance, embedding distance | Chống mode collapse. |
| Novelty | Khoảng cách với train seed/template | Novelty rate, nearest-neighbor distance | Tránh copy payload từ dữ liệu huấn luyện. |

Mode collapse cần được đo bằng:

- Unique ratio giảm theo step.
- Duplicate rate tăng.
- Token entropy giảm.
- Top-k payload lặp lại nhiều lần.
- Discriminator accuracy quá cao hoặc quá thấp bất thường.
- Generator loss không còn phản ánh cải thiện mẫu.

### 4.6. Kết quả phải biết tự phê bình

Khi trình bày kết quả hiện tại, cần tách rõ:

- Đã chạy: cấu hình, dataset, số step, output.
- Chưa chạy: phần loss/evaluator/WAF feedback còn là kế hoạch.
- Failure: mode collapse sau khoảng 500 vòng lặp.
- Giả thuyết nguyên nhân: Discriminator quá mạnh, reward sparse, dữ liệu mất cân bằng, tokenization kém, learning rate chưa hợp lý.
- Thí nghiệm sửa lỗi: pretraining, label smoothing, gradient penalty, entropy/diversity reward, cân bằng số bước G/D, sampling temperature, Gumbel-Softmax, SeqGAN smoke test.

## 5. Cấu trúc slide nên dùng cho lần trình bày tiếp theo

1. Title: GAN-based SQL Injection Payload Generation.
2. Problem: payload cần hợp lệ, đa dạng, realistic, có khả năng kiểm thử WAF.
3. Why hard: syntax, semantics, WAF behavior, noisy labels, mode collapse.
4. Related work map: template, mutation, RL, GAN, LLM, gap.
5. Dataset inventory: nguồn, số dòng, trạng thái, license, risk.
6. Data pipeline: raw -> clean -> template -> safe split -> tokenization.
7. Label/verification: parser, rule, WAF, evaluator, human review.
8. Model overview: Generator, Discriminator, Evaluator/WAF.
9. Training loop vs evaluation loop.
10. Loss/objective: current version and planned version.
11. Metrics: validity, diversity, bypass, novelty, collapse.
12. Current result: những gì đã chạy thật.
13. Failure analysis: mode collapse sau khoảng 500 vòng lặp.
14. Fix plan: 3 thí nghiệm gần nhất.
15. Contribution and next milestone.

---

# Phần 2: Tài nguyên và kế hoạch thực hiện

## 1. Tóm tắt điều hành

Dự án được chia thành 6 giai đoạn:

1. Tổng hợp tài liệu và dữ liệu.
2. Tái tạo baseline.
3. Thiết kế và huấn luyện mô hình.
4. Đánh giá trên testbed an toàn.
5. Phân tích kết quả và đề xuất phòng thủ.
6. Viết báo cáo, đóng gói artifact và đảm bảo tái lập.

Sản phẩm cuối cần có:

- Bản đồ related work và paper card.
- Dataset inventory có thể truy vết.
- Pipeline tiền xử lý, template, tokenization và safe split.
- Baseline mutation/template/RL tối thiểu.
- Mô hình GAN hoặc biến thể GAN có log training.
- Testbed WAF an toàn, ưu tiên ModSecurity + OWASP CRS và Coraza.
- Bộ metric: ASR, validity, semantic preservation, diversity, novelty, FPR, transferability.
- Báo cáo kỹ thuật, slide, README, Docker/CI nếu đủ thời gian.

## 2. Giai đoạn triển khai

| Giai đoạn | Mục tiêu | Công việc kỹ thuật | Sản phẩm đầu ra | Thời lượng dự kiến |
|---|---|---|---|---|
| 1. Tài liệu và dữ liệu | Hiểu bài toán, nguồn dữ liệu, baseline và rủi ro | Thu thập paper, repo, dataset; lập paper card; lập dataset inventory; xác định license và ethical boundary | Related work map, dataset table, risk register | 2-3 tuần |
| 2. Tái tạo baseline | Có mốc so sánh tối thiểu | Template baseline, mutation baseline, parser/validator, test WAF local | Baseline report, scripts, log kết quả | 3-4 tuần |
| 3. Thiết kế và huấn luyện | Xây mô hình sinh payload | SeqGAN/Gumbel GAN/RelGAN/MaskGAN hoặc GAN v0; pretraining; loss v0; collapse metrics | Model checkpoints, training logs, sample report | 6-8 tuần |
| 4. Đánh giá và testbed | Đánh giá công bằng và an toàn | ModSecurity + CRS, Coraza, WAF-ML nếu có; protocol white-box/black-box được phép; metric aggregator | Evaluation report, ASR/diversity/validity tables | 4-6 tuần |
| 5. Phân tích và phòng thủ | Biến kết quả thành insight | So sánh baseline vs model; phân tích failure; đề xuất WAF hardening/adversarial training/semantic validation | Analysis report, defense recommendations | 3-4 tuần |
| 6. Báo cáo và tái lập | Hoàn thiện luận văn/artifact | README, Docker, CI smoke test, reproducibility guide, slide, appendix | Final report, slides, artifact package | 3-4 tuần |

## 3. Giai đoạn 1: Tổng hợp tài liệu và dữ liệu

### 3.1. Công việc

- Thu thập và phân nhóm paper: GAN nền tảng, GAN cho text rời rạc, SQLi mutation/RL, LLM-based SQLi, WAF/evaluator, defense.
- Tìm mã nguồn và dataset: PayloadsAllTheThings, SecLists, SQLMap payloads, WAF-A-MoLE, ModSecurity CRS, Coraza, OWASP Juice Shop.
- Lập dataset inventory theo mẫu cố định.
- Kiểm tra license và trạng thái tải.
- Định nghĩa nhãn và tiêu chí lọc.
- Thiết kế safe split để tránh leakage giữa train/test.
- Định nghĩa metric từ đầu: ASR, validity, semantic preservation, diversity, novelty, FPR, transferability.
- Lập ranh giới đạo đức: không test hệ thống thật, không công bố payload khai thác chi tiết.

### 3.2. Tiêu chí hoàn thành

- Có ít nhất 15-20 paper card.
- Có bảng dataset với số dòng raw/usable/status.
- Có quy tắc safe split và ví dụ minh họa.
- Có danh sách baseline bắt buộc.
- Có risk register về dual-use, label noise, data leakage, license.

## 4. Giai đoạn 2: Tái tạo baseline

### 4.1. Baseline cần có

| Baseline | Mục đích | Output |
|---|---|---|
| Template baseline | Sinh payload từ mẫu cố định | Payload hợp cú pháp nhưng novelty thấp. |
| Random mutation | So sánh với biến đổi bề mặt | Payload biến đổi ký tự/format/comment/encoding. |
| Rule-based mutation | Baseline mạnh hơn random | Payload giữ ý đồ SQLi tốt hơn. |
| AST/tree transform | Kiểm tra biến đổi có cấu trúc | Payload biến đổi theo cây cú pháp nếu parser hỗ trợ. |
| MLE/RNN hoặc Transformer nhỏ | Baseline neural đơn giản | Payload học phân phối dữ liệu trước khi dùng GAN. |
| WAF-A-MoLE/AdvSQLi-style reproduction | Baseline nghiên cứu gần nhất | Kết quả so sánh với phương pháp đã công bố, nếu tái hiện được. |

### 4.2. Testbed baseline

Ưu tiên:

- ModSecurity + OWASP Core Rule Set.
- Coraza nếu cần WAF open-source thay thế.
- OWASP Juice Shop hoặc web app demo có lỗ hổng trong container.
- Script gửi request trong local network/container.
- Log allow/block, status code, rule id, payload id, method sinh.

Không làm:

- Không gửi payload vào website thật.
- Không test cloud WAF nếu chưa có môi trường sandbox và quyền rõ ràng.
- Không lưu dữ liệu người dùng thật hoặc PII.

## 5. Giai đoạn 3: Thiết kế và huấn luyện mô hình

## 5.1. Kiến trúc cần so sánh

| Kiến trúc | Mô tả | Ưu điểm | Nhược điểm | Vai trò đề xuất |
|---|---|---|---|---|
| SeqGAN | GAN + reinforcement learning, Generator RNN, Discriminator, Monte Carlo reward | Phù hợp chuỗi rời rạc, reward theo từng bước | Khó ổn định, cần pretraining MLE | Candidate chính nếu muốn bám GAN cho text. |
| GAN Gumbel-Softmax | Dùng Gumbel-Softmax để xấp xỉ token rời rạc và backpropagate | Dễ tích hợp, ổn định hơn policy gradient | Xấp xỉ có thể làm giảm tính hợp nghĩa token | Candidate cho bản v0/v1. |
| RelGAN | Gumbel + relational memory + discriminator multi-embedding | Quản lý dependency dài tốt hơn | Phức tạp, nhiều tham số, train lâu | Chỉ làm nếu baseline đơn giản đã ổn. |
| MaskGAN | Actor-critic GAN với cơ chế mask/fill-in | Tận dụng ngữ cảnh hai phía, tốt cho completion | Cài đặt phức tạp, chậm | Phương án nâng cao. |
| GSQLi hoặc GAN SQLi chuyên biệt | Mô hình GAN chuyên cho SQLi nếu xác minh được paper/code | Gần trực tiếp với đề tài | Có thể khó tìm code, cần xác minh nguồn | Dùng làm related work hoặc reproduction nếu đủ tài liệu. |
| LLM prompt/fine-tune | Dùng LLM làm generator hoặc baseline | Chất lượng và đa dạng cao | Chi phí, phụ thuộc provider, khó tái lập, rủi ro an toàn | Baseline hiện đại, không nên thay thế hoàn toàn GAN nếu đề tài là GAN. |
| Diffusion/TabDDPM/VAE | Học phân phối phức tạp, có noise control | Có tiềm năng đa dạng | Ít trực tiếp cho text SQLi, train nặng | Phụ lục hoặc future work. |

### 5.2. Loss dự kiến

Phiên bản v0:

```text
Generator objective =
  adversarial realism reward
  + syntax validity reward
  + diversity reward
  - duplicate penalty
```

Phiên bản v1:

```text
Generator objective =
  adversarial realism reward
  + syntax validity reward
  + semantic preservation reward
  + WAF/proxy bypass reward
  + novelty/diversity reward
  - unsafe/output-policy penalty
```

Lưu ý:

- WAF thật chỉ nên dùng ở evaluation hoặc dùng với quota rất nhỏ trong testbed, vì chi phí cao và feedback sparse.
- Training nên bắt đầu với evaluator/proxy nhẹ: parser, template validator, discriminator, local CRS.
- Phải log từng thành phần reward để biết mô hình tối ưu cái gì.

### 5.3. Xử lý mode collapse

Thứ tự thử nghiệm:

1. Pretrain Generator bằng MLE trước khi adversarial training.
2. Giảm tốc Discriminator hoặc cân bằng lại số step G/D.
3. Dùng label smoothing/noise cho Discriminator.
4. Thêm entropy hoặc diversity reward.
5. Theo dõi unique ratio, duplicate rate, token entropy theo từng epoch.
6. Thử Gumbel-Softmax nếu policy gradient quá bất ổn.
7. Nếu GAN tiếp tục collapse, dùng MLE/Transformer nhỏ làm fallback baseline và trình bày GAN failure như kết quả nghiên cứu.

## 6. Giai đoạn 4: Đánh giá và testbed an toàn

## 6.1. Đích WAF

| Nhóm | Đích | Mức ưu tiên | Ghi chú |
|---|---|---|---|
| Open-source WAF | ModSecurity + OWASP CRS | Cao | White-box, dễ tái lập, phù hợp luận văn. |
| Open-source WAF | Coraza | Trung bình | Có thể dùng để kiểm tra transferability. |
| WAF-ML công khai | CNN-WAF, WAF-Brain hoặc repo tương đương | Trung bình | Chỉ dùng nếu code/dataset tái lập được. |
| Cloud/commercial WAF | AWS WAF, Cloudflare WAF, Barracuda WAF | Thấp/kiểm soát chặt | Chỉ black-box trong môi trường sandbox được cấp phép, tuân thủ ToS. |

## 6.2. Metric

| Metric | Định nghĩa | Cách đo dự kiến |
|---|---|---|
| ASR | Tỷ lệ payload qua được WAF/testbed | `allowed / total_payloads` trong môi trường được phép. |
| Syntax validity | Tỷ lệ payload hợp cú pháp | SQL parser/validator hoặc rule-based checker. |
| Semantic preservation | Payload giữ ý đồ hoặc effect class | Template/AST/effect-class comparison. |
| Diversity | Mức khác nhau giữa payload sinh ra | Unique ratio, Levenshtein, AST distance, embedding distance. |
| Novelty | Khác với training seed/template | Nearest-neighbor distance, duplicate against train set. |
| Transferability | Payload qua được nhiều WAF khác nhau | Train/evaluate chéo giữa CRS, Coraza, WAF-ML. |
| FPR | Tỷ lệ benign/không tấn công bị nhận diện sai | Cần benign set riêng, không trộn với SQLi payload. |
| Collapse indicators | Dấu hiệu sinh lặp | Unique ratio, entropy, duplicate rate, top-k repetition. |

## 6.3. Protocol đánh giá

- Cố định seed, split, số lượng payload, temperature và threshold.
- Mỗi phương pháp sinh cùng số lượng mẫu.
- Chạy nhiều seed nếu đủ thời gian, báo cáo mean/std thay vì chỉ số tốt nhất.
- Tách tập train/dev/test để tránh payload hoặc template leakage.
- Không công bố payload bypass chi tiết trong báo cáo công khai.
- Log đủ metadata: model version, baseline, seed, WAF version, CRS version, timestamp.

## 7. Giai đoạn 5: Phân tích và đề xuất phòng thủ

Câu hỏi phân tích:

- GAN/LLM/diffusion có tốt hơn baseline nào, ở metric nào.
- Payload sinh ra có thật sự mới hay chỉ copy/near-copy.
- Trade-off giữa diversity và ASR ra sao.
- WAF fail ở nhóm pattern nào.
- Payload fail do syntax, semantic, WAF block hay model collapse.
- Có cần semantic validator hoặc AST equivalence để cải thiện WAF không.

Đề xuất phòng thủ có thể gồm:

- Cập nhật rule hoặc regex theo nhóm lỗi, không công bố exploit cụ thể.
- Adversarial training cho WAF-ML bằng payload sinh an toàn.
- Thêm lớp semantic/AST validation thay vì chỉ signature.
- Tạo benchmark regression test cho WAF từ các nhóm payload đã khái quát hóa.
- Coordinated disclosure nếu phát hiện lỗi nghiêm trọng trong sản phẩm/vendor.

## 8. Giai đoạn 6: Báo cáo, tái lập và công bố

Artifact cần chuẩn bị:

- `README.md`: mục tiêu, phạm vi, cách chạy, ranh giới an toàn.
- `data_manifest.md`: nguồn dữ liệu, license, số dòng, trạng thái xử lý.
- `paper_cards/`: tóm tắt paper theo mẫu thống nhất.
- `scripts/`: preprocess, train, evaluate, aggregate metrics.
- `docker/`: testbed WAF local và môi trường chạy evaluation.
- `configs/`: seed, model config, WAF config, split config.
- `reports/`: baseline report, model report, evaluation report, final thesis notes.
- CI smoke test: chạy parser/evaluator/baseline nhỏ để tránh bit rot.

Chuẩn công bố:

- Chỉ công bố kết quả tổng hợp, taxonomy, metric và khuyến nghị phòng thủ.
- Không công bố payload bypass có thể dùng trực tiếp.
- Ghi rõ nghiên cứu chỉ phục vụ học thuật và kiểm thử bảo mật được cấp phép.
- Nếu gửi bài báo, chuẩn bị artifact có thể tái lập và threat-to-validity.

## 9. Rủi ro và giảm thiểu

| Rủi ro | Tác động | Giảm thiểu |
|---|---|---|
| Dual-use | Bị hiểu là hướng dẫn tấn công | Không công bố payload khai thác chi tiết, tập trung vào metric và phòng thủ. |
| Test trái phép | Rủi ro pháp lý/đạo đức | Chỉ dùng lab, container, sandbox hoặc hệ thống được cấp phép. |
| Nhiễu nhãn | Model học sai | Kiểm chứng bằng parser, rule, WAF, human review mẫu nhỏ. |
| Data leakage | Kết quả ảo | Safe split theo template/family, de-dup và near-dup detection. |
| Mode collapse | Payload lặp, diversity thấp | Entropy/diversity reward, pretraining, cân bằng G/D, log collapse metrics. |
| WAF feedback sparse | Training không ổn định | Dùng proxy evaluator trong training, WAF thật cho evaluation. |
| Compute thiếu | Không train được mô hình lớn | Ưu tiên baseline nhỏ, SeqGAN/Gumbel smoke, LLM chỉ làm baseline giới hạn. |
| Paper/source chưa xác minh | Claim yếu | Đánh dấu "cần xác minh", chỉ dùng làm related work sau khi kiểm tra nguồn. |

## 10. Tài liệu ưu tiên cần đọc và xác minh

Các mục dưới đây là danh sách ưu tiên từ ghi chú ban đầu. Trước khi đưa vào báo cáo chính thức, cần xác minh metadata: tác giả, năm, venue, DOI/arXiv, code và dataset.

| Nhóm | Tài liệu/paper | Vai trò |
|---|---|---|
| GAN nền tảng | Goodfellow et al., 2014 | Nền tảng GAN. |
| GAN cho text | SeqGAN, MaskGAN, Gumbel-Softmax GAN, RelGAN | Cơ sở cho chuỗi rời rạc. |
| SQLi/WAF adversarial | WAF-A-MoLE, AdvSQLi, SSQLi, GenSQLi | Baseline và related work trực tiếp. |
| GAN/GenAI SQLi | GSQLi hoặc các paper GAN SQLi chuyên biệt | Cần xác minh paper/code. |
| LLM SQLi | RADAGAS/RefleXQLi, prompt-to-SQLi, adversarial SQLi with LLMs | Baseline hiện đại, cần kiểm soát an toàn. |
| Cybersecurity GAN | MalGAN, IDSGAN, DeepDGA, PassGAN | Bối cảnh GAN trong an ninh mạng. |
| Tabular/diffusion | CTGAN, TabDDPM | Phương án mở rộng/future work. |
| Survey | GAN for cybersecurity survey, GAN for malware detection survey | Khung tổng quan và threat model. |

## 11. Mã nguồn và dữ liệu ưu tiên

| Tài nguyên | URL tham khảo | Vai trò |
|---|---|---|
| PayloadsAllTheThings | `https://github.com/swisskyrepo/PayloadsAllTheThings` | Payload seed và taxonomy. |
| SecLists | `https://github.com/danielmiessler/SecLists` | Wordlist/payload security testing. |
| SQLMap | `https://github.com/sqlmapproject/sqlmap` | Công cụ/baseline tham khảo. |
| WAF-A-MoLE | `https://github.com/AvalZ/WAF-A-MoLE` | Mutation-based baseline. |
| OWASP CRS | `https://github.com/coreruleset/coreruleset` | Rule set WAF open-source. |
| ModSecurity | `https://github.com/owasp-modsecurity/ModSecurity` | WAF engine open-source. |
| Coraza | `https://github.com/corazawaf/coraza` | WAF engine open-source thay thế. |
| OWASP Juice Shop | `https://github.com/juice-shop/juice-shop` | Web app lab có lỗ hổng để test trong container. |
| CTGAN | `https://github.com/sdv-dev/CTGAN` | Baseline synthetic tabular data. |
| TabDDPM | `https://github.com/yandex-research/tab-ddpm` | Diffusion cho dữ liệu bảng. |
| CIC-IDS2017 | `https://www.unb.ca/cic/datasets/ids-2017.html` | Dataset IDS, chỉ dùng nếu liên quan rõ tới evaluator/IDS. |
| UNSW-NB15 | `https://research.unsw.edu.au/projects/unsw-nb15-dataset` | Dataset IDS, không trộn tùy tiện với SQLi payload. |
| NSL-KDD | Cần chọn nguồn chuẩn | Dataset IDS cổ điển, chỉ dùng làm tham khảo nếu cần. |
| Papers With Code | `https://paperswithcode.com/` | Tìm code tham khảo cho paper. |
| OWASP | `https://owasp.org/` | Chuẩn an toàn, CRS, Juice Shop, disclosure guidance. |

## 12. Lịch trình đề xuất năm 2026

| Thời gian | Trọng tâm | Mốc nghiệm thu |
|---|---|---|
| 2026-06 | Thu thập paper, repo, dataset, lập inventory | Có related work map, dataset table, ethical boundary. |
| 2026-07 | Baseline và testbed WAF local | Chạy được template/mutation baseline trên ModSecurity CRS. |
| 2026-08 | Mô hình v0 và evaluator | Có Generator/Discriminator v0, parser/evaluator, log collapse metrics. |
| 2026-09 | Mô hình v1 và xử lý collapse | Có SeqGAN/Gumbel hoặc GAN cải tiến, ablation ban đầu. |
| 2026-10 | Đánh giá đầy đủ | Có bảng ASR, validity, diversity, novelty, baseline comparison. |
| 2026-11 | Phân tích và đề xuất phòng thủ | Có analysis report, failure cases, defense recommendations. |
| 2026-12 | Báo cáo và artifact | Hoàn thiện luận văn, slide, README, Docker/CI smoke nếu kịp. |

Ước tính tài nguyên:

- Compute: 1-2 GPU mạnh, ưu tiên RTX 4080/4090 hoặc tương đương.
- GPU time: khoảng 500-1000 GPU-giờ nếu chạy nhiều biến thể; có thể giảm nếu giới hạn mô hình.
- Dung lượng: dưới 50 GB cho payload, log, checkpoint nhỏ; tăng nếu lưu nhiều model.
- Nhân lực: 1 người chính + hỗ trợ phản biện/kiểm tra an toàn; lý tưởng 2-3 người nếu làm đủ testbed và paper.

---

# Checklist nghiệm thu trước buổi trình bày tiếp theo

## 1. Checklist nội dung

- [ ] Nói được bài toán trong 1 câu.
- [ ] Có câu trả lời "tại sao GAN, không phải template/mutation".
- [ ] Có bảng related work dẫn tới khoảng trống.
- [ ] Có bảng dataset: nguồn, file, raw rows, usable rows, status, risk.
- [ ] Có ví dụ pipeline: raw -> clean -> template -> tokenized -> split.
- [ ] Có định nghĩa safe split và cách tránh leakage.
- [ ] Có sơ đồ mô hình tổng thể tách training path và evaluation path.
- [ ] Có slide loss/objective, dù là bản v0/v1.
- [ ] Có metric đo mode collapse.
- [ ] Có baseline tối thiểu.
- [ ] Có protocol đánh giá WAF an toàn.
- [ ] Có 3 thí nghiệm tiếp theo đo được.

## 2. Ba thí nghiệm gần nhất nên làm

| Thí nghiệm | Mục tiêu | Tiêu chí thành công |
|---|---|---|
| Data inventory + safe split | Chốt dữ liệu đáng tin | Có bảng số dòng raw/usable, duplicate rate, split rule. |
| Baseline mutation trên CRS | Có mốc so sánh | Chạy được N payload trong ModSecurity CRS và log allow/block. |
| GAN v0 + collapse tracking | Biết mô hình fail ở đâu | Có unique ratio, entropy, duplicate rate theo step; xác nhận collapse hoặc cải thiện. |

## 3. Điều kiện để báo cáo với thầy là "đã tiến bộ"

- Không còn trình bày GAN như một hộp đen.
- Có số liệu dữ liệu cụ thể thay vì nói chung chung.
- Có loss/metric gắn với mục tiêu nghiên cứu.
- Có baseline và protocol so sánh.
- Có failure analysis rõ ràng nếu mô hình chưa tốt.
- Có ranh giới an toàn và đạo đức rõ.
- Có kế hoạch tiếp theo đo được bằng bảng, log, code hoặc report.
