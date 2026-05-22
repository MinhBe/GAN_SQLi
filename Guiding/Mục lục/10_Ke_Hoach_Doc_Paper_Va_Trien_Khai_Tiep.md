# 10 — Kế Hoạch Đọc Paper Và Triển Khai Tiếp

> Ngày tạo: 2026-05-21  
> Phạm vi: `Asset/Total_OCR`, `Asset/Total_Summary`, `Guiding/Mục lục`, kết quả Phase 1 → Phase 3.5  
> Mục tiêu: biến toàn bộ paper/OCR và note hiện có thành kế hoạch triển khai tiếp theo, không lặp lại các thử nghiệm GAN đã fail.

---

## 1. Kết luận đầu vào bắt buộc

Tài liệu `Kết luận 1.md` đã chốt:

```text
DECISION = MLE_MAIN
GAN = HARD STOP cho các biến thể đã thử
```

Vì vậy hướng triển khai tiếp theo không được mặc định quay lại GAN. Hướng chính là:

```text
Conditional MLE
+ evaluator-guided search
+ data/label/evaluator foundation đầy đủ
```

GAN chỉ được mở lại nếu có một giả thuyết mới giải quyết đúng cơ chế đã quan sát:

```text
D saturation
syntax-vs-diversity tradeoff
high seed variance
```

Không mở lại chỉ bằng các kỹ thuật đã fail hoặc đã bị loại trong Phase 3.5:

```text
WGAN-GP trực tiếp
SpectralNorm/TTUR
straight-through Gumbel đơn thuần
PPO
best-run cherry-pick
```

Cập nhật ngày 2026-05-22:

```text
Phase 08 được phép mở lại dưới dạng paired masked payload-surgery GAN.
Điều kiện: phải có span-preserving surgery data, paired D, anchor-only ablation, H2 D-scorer safety net và gate đăng ký trước.
Không được coi đây là tiếp tục Gumbel-SeqGAN/WGAN-GP cũ.
```

---

## 2. Tình trạng tài liệu hiện có

### 2.1. OCR corpus

Thư mục:

```text
Asset/Total_OCR
```

Hiện có 56 file, gồm:

```text
paper OCR hợp lệ: phần lớn corpus
file OCR quá ngắn: 4 file trong Total_OCR
log OCR lỗi: ocr_errors.json
```

Các file OCR quá ngắn trong `Total_OCR`:

```text
Deep_Neural_Network_SQLi_2022.md
Phuong_2024_GAN_IDS_Evasion.md
Halfond_2006_Classification.md
Rahman_2025_Leveraging_GANs_IDS.md
```

Các PDF lỗi OCR được ghi trong `ocr_errors.json`:

```text
Ahmadi_2018_Gap_Weighted_Kernel.pdf
Attack_Model_2012_Penetration_SQLi.pdf
Deep_Neural_Network_SQLi_2022.pdf
GSQLi_2025_GAN_SQLi_WAF.pdf
Justin_Clarke_2012_SQLi_Book_Preview.pdf
LSTM_on_AST_SQLi_2021.pdf
Muduli_2023_AE_Net_SQLi.pdf
Phuong_2024_GAN_IDS_Evasion.pdf
Xu_2023_IE_GAN_SQLi.pdf
```

### 2.2. Summary corpus

Thư mục:

```text
Asset/Total_Summary
```

Các note đã đủ giá trị để làm decision input:

```text
MASTER_PROBLEM_SOLUTION.md
SEQGAN_TECHNICAL_SYNTHESIS.md
RELATED_WORK_SYNTHESIS.md
TONG_HOP_PHAN_TICH_30_BAI_BAO.md
LABEL_SQLI_V2_ARCHITECTURE.md
deep-research-report.md
```

Các note paper-level quan trọng:

```text
Yu_2017_SeqGAN.md_ANALYSIS.md
Jang_2017_Gumbel_Softmax.md_ANALYSIS.md
Gulrajani_2017_WGAN_GP.md_ANALYSIS.md
Guo_2018_LeakGAN.md_ANALYSIS.md
Lu_2022_GAN_SQLi.md_ANALYSIS.md
Ratner_2017_Snorkel.md_ANALYSIS.md
Rennie_2017_Self_Critical.md_ANALYSIS.md
```

---

## 3. Kế hoạch đọc toàn bộ OCR

Không đọc tuần tự theo tên file. Đọc theo câu hỏi kỹ thuật để mỗi paper trả lời một quyết định triển khai.

### Pass 0 — Inventory và chất lượng OCR

Mục tiêu:

```text
biết file nào đọc được
file nào duplicate
file nào cần OCR lại hoặc thay nguồn
file nào chỉ dùng làm context
```

Output:

```text
reports/literature/ocr_inventory.csv
reports/literature/ocr_repair_queue.md
```

Các cột cần có:

```text
file
paper_title
year
topic_group
ocr_chars
ocr_quality
duplicate_of
read_priority
implementation_relevance
```

### Pass 1 — Paper quyết định kiến trúc

Đọc trước nhóm có thể thay đổi design hiện tại:

```text
Lee_2022_Deduplicating.md
Ratner_2017_Snorkel.md
Gilardi_2023_ChatGPT_Labeling.md
Sennrich_2016_BPE.md
Feng_2020_CodeBERT.md
Hwang_2019_SQLova.md
Demetrio_2020_WAF_A_MoLE.md
Lu_2022_GAN_SQLi.md
Chowdhary_2023_GAN_Pentesting.md
Le_2024_GSQLi.md
Dasari_2025_Enhancing_SQLi.md
```

Câu hỏi cần trả lời:

```text
data foundation nên dedup/canonicalize thế nào?
label system nên dùng weak supervision hay AI-only đến đâu?
tokenization nên SQL-aware, BPE, hay hybrid?
evaluator nào đủ tin để làm gate?
mutation/evaluator-guided search nên nằm trước hay sau relex?
```

### Pass 2 — Paper GAN/SeqGAN chỉ để đóng hoặc mở giả thuyết mới

Đọc nhóm này với mục tiêu rất hẹp: tìm cơ chế mới chống D-saturation, không tìm lý do lặp lại GAN.

```text
Goodfellow_2014_GAN.md
Arjovsky_2017_WGAN.md
Gulrajani_2017_WGAN_GP.md
Miyato_2018_Spectral_Norm.md
Yu_2017_SeqGAN.md
Jang_2017_Gumbel_Softmax.md
Maddison_2017_Concrete_Dist.md
Bengio_2013_STE.md
Williams_1992_REINFORCE.md
Rennie_2017_Self_Critical.md
Guo_2018_LeakGAN.md
Fedus_2018_MaskGAN.md
Nie_2019_RelGAN.md
Blonde_2019_SAM_GAIL.md
Schulman_2017_PPO.md
Rosa_2022_Survey_Text_GAN.md
Zhang_2020_Adversarial_Text_Survey.md
Atkinson_2024_Advancements_SeqGAN.md
Pearson_2024_Enhancing_SeqGAN.md
Rodriguez_2024_GAN_RL.md
```

Mỗi paper phải được gắn một trong ba verdict:

```text
already_tested_failed
supports_current_MLE_path
new_GAN_hypothesis_candidate
```

Nếu là `new_GAN_hypothesis_candidate`, bắt buộc ghi:

```text
mechanism
expected failure mode fixed
minimal experiment
gate metric
resource estimate on RTX 3050 6GB
reason it is not WGAN-GP/SN/TTUR/ST repeated
```

### Pass 3 — Paper security/domain baseline

Đọc để hoàn thiện related work và evaluator/baseline, không để kéo roadmap chính lệch hướng.

```text
Alauthman_2026_GAN_IDS_Survey.md
Lin_2018_IDSGAN.md
Zhao_2024_WGAN_Botnet.md
Ahsan_2022_Comparative_CGAN.md
Nawaz_2025_CTGAN_Web_Attacks.md
Jamoos_2023_TDCGAN.md
Truong_2023_CTGAN_IDS.md
Peppes_2025_BNGAN.md
Agrawal_2024_GenAI_Synthetic.md
Udu_2025_SMOTE_GAN_Review.md
Strelcenia_2023_GAN_Survey_Credit.md
Scott_2019_GAN_SMOTE.md
Khoirunnisa_2025_SMOTE_CTGAN.md
Julianti_2024_CTGAN_Graduation.md
Emaan_2025_T_GAN.md
Ha_2023_GAN_Fault_Prediction.md
Le_2024_Hybrid_Sampling_IDS.md
```

Output:

```text
reports/literature/security_gan_baselines.md
reports/literature/baseline_matrix.csv
```

### Pass 4 — OCR repair

Các file quá ngắn hoặc OCR lỗi không được dùng làm bằng chứng chính cho kết luận.

Hành động:

```text
thử OCR lại từ Asset/Total_PDF
nếu vẫn lỗi, đánh dấu missing_source
nếu paper quan trọng, tìm metadata/link thay thế
```

Output:

```text
reports/literature/ocr_repair_results.md
```

---

## 4. Template đọc mỗi paper

Mỗi paper sau khi đọc phải có một bản ghi ngắn theo schema:

```text
paper_id:
claim:
method:
data:
metrics:
failure_modes:
what_applies_to_us:
what_not_to_copy:
implementation_decision:
confidence:
```

Không chấp nhận summary kiểu chỉ mô tả chung. Mỗi paper phải kết thúc bằng một quyết định:

```text
adopt
reject
baseline_only
related_work_only
needs_experiment
```

---

## 5. Roadmap triển khai tiếp theo

### Phase 04 — Full Data Foundation

Ưu tiên số 1.

Deliverables:

```text
data/phase04/foundation.parquet
data/phase04/exact_dedup_map.parquet
data/phase04/near_dup_clusters.parquet
data/phase04/splits_cluster_safe.json
reports/04_full_data_foundation_report.md
```

Việc cần làm:

```text
canonical_light và canonical_structural
exact dedup theo sha256
near-dedup theo SimHash/MinHash candidate
lane-aware strip wrapper
delex_v5 + literal pools + relex map
cluster-safe train/dev/test split
```

Gate để đi tiếp:

```text
cluster leakage = 0
delex collision trong gold/dev thấp và có report
top-template coverage không thống trị
literal pool đủ để relex/eval
```

### Phase 05 — Full Label System

Chỉ chạy sau khi Phase 04 có foundation ổn.

Deliverables:

```text
data/phase05/labeled.parquet
data/phase05/verified_dev.parquet
data/phase05/verified_test.parquet
data/phase05/review_queue.parquet
reports/05_full_label_system_report.md
```

Nguyên tắc:

```text
tách technique_primary khỏi intent_secondary
unknown không phải class generator chính
confidence phải có calibration hoặc band rõ nghĩa
tier4/unknown không được dùng như benign verified
```

### Phase 06 — Evaluator và model separation

Deliverables:

```text
models/phase06/label_quality_model.pkl
models/phase06/consistency_evaluator.pt
eval/phase06/evaluator_calibration.json
reports/06_evaluator_model_separation_report.md
```

Evaluator suite cần có:

```text
parser/AST
type/db consistency
novelty/exact-copy/near-copy
diversity/self-BLEU/template entropy
DB/WAF lab chỉ khi relex đủ tin
```

### Phase 07 — Main MLE-first Generator

Deliverables:

```text
models/phase07/mle_generator.pt
eval/phase07/mle_sampling_frontier.json
eval/phase07/generated_candidates.csv
reports/07_mle_first_generator_report.md
```

Thực nghiệm:

```text
3 seeds tối thiểu
temperature/top-k/top-p/repetition-penalty frontier
best-of-N và rejection sampling
diversity-aware reranking
```

### Phase 08 — Paired Masked Payload-Surgery GAN

Triển khai có điều kiện, không phải quay lại GAN cũ.

Giả thuyết mới được chấp nhận để pilot:

```text
Giữ khung SQLi hợp lệ, chỉ sinh slot literal/operator/comment/encoding.
D được train theo cặp cùng mask_frame/condition để tránh học template shortcut.
G luôn có MLE anchor trên slot để chống drift khỏi ground truth.
H2 D-as-scorer được chạy trước như ablation và safety net.
```

Điều kiện mở pilot:

```text
span-preserving surgery dataset có round-trip check
syntax/slot evaluator chặt hơn keyword-only proxy
anchor-only baseline đã chạy
paired D shortcut diagnostic đã định nghĩa
gate metric và stop rule được đăng ký trước
chi phí phù hợp RTX 3050 6GB
```

Thứ tự:

```text
08A data/evaluator hardening
08B H2 D-as-scorer
08C H5' paired masked surgery GAN pilot 1 seed
08D confirmatory >=3 seeds nếu pilot pass
08E report H1 vs H2 vs anchor-only vs H5'
```

### Phase 09 — Final Evaluation

Deliverables:

```text
eval/final/mle_frontier.json
eval/final/gan_comparison.json nếu có GAN
eval/final/verified_test_results.json
reports/09_final_evaluation_report.md
```

Kết luận cuối phải là một trong ba:

```text
MLE-first thắng
GAN thắng rõ qua gate mới
GAN vẫn là future work
```

---

## 6. Thứ tự làm ngay

```text
1. Tạo reports/literature/ocr_inventory.csv từ Total_OCR.
2. Tạo reports/literature/ocr_repair_queue.md từ ocr_errors.json và file quá ngắn.
3. Đọc Pass 1 và cập nhật decision matrix.
4. Triển khai Phase 04 Full Data Foundation trên dữ liệu full.
5. Chạy report Phase 04, chỉ sau đó mới label full.
6. Triển khai Phase 05 + verified_dev/test.
7. Train Phase 07 MLE frontier.
8. Viết protocol Phase 08 mới cho paired masked payload-surgery GAN, gồm H2 safety net và anchor-only ablation.
```

---

## 7. Tiêu chí chống tự lừa

Không chấp nhận các kết luận sau:

```text
GAN có vẻ tiềm năng nên train full
GAN thắng ở một seed nên mở lại
WAF score tăng nhưng syntax/diversity giảm vẫn tính là thắng
unknown/tier4 được xem là benign
classifier proxy được xem là ground truth
paper nói WGAN-GP tốt nên bỏ qua Phase 3.5
```

Chỉ chấp nhận kết luận dựa trên:

```text
pre-registered metrics
multi-seed
cluster-safe split
verified_dev/test
frontier comparison
mean/std/CI theo seed
failure analysis có đường dẫn artifact
```
