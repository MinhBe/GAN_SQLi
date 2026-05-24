# Hướng Dẫn Triển Khai Và Theo Dõi Tiến Độ

Ngày tạo: 2026-05-22  
Phạm vi:  `Guiding_VAE_GAN`, nền dữ liệu/evaluator từ `Guiding`. dataset tại C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\FinalDataSet

---

## 1. Quyết định triển khai mặc định

Thứ tự triển khai khuyến nghị:

```text
1. Triển khai Gumbel Action-Surgery trước.
2. Giữ MLE/D-as-scorer làm baseline và đường an toàn.
3. Chỉ mở VAE-GAN sau khi hoàn tất paper nền + label readiness + pure-VAE gate.
```

Lý do:

- Gumbel/action-surgery đã có đường triển khai thực dụng hơn nhờ GSQLi/action taxonomy và D-as-scorer. [`Guiding_Gumbel-Softmax\03_Phan_Tich_Sau_Tu_Paper.md:54-62`](..\Guiding_Gumbel-Softmax\03_Phan_Tich_Sau_Tu_Paper.md)
- VAE-GAN có trần novelty cao hơn, nhưng còn thiếu paper nền và phụ thuộc nhãn yếu. [`Guiding_VAE_GAN\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:21-34`](..\Guiding_VAE_GAN\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md) [`Guiding_VAE_GAN\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:43-58`](..\Guiding_VAE_GAN\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)
- SeqGAN/GAN full-sequence cũ đã bị gate loại: `MLE_MAIN`, fail 4/6 gate, `collapse_count=3`, `dominating_pair_count=0`. [`Guiding\Phase 3\eval\phase03\decision.json:2-4`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 3\eval\phase03\decision.json:79-91`](..\Guiding\Phase%203\eval\phase03\decision.json)

---

## 2. File theo dõi tiến độ

Timeline JSON nằm tại:

```text
timeline/timeline_progress.json
```

Mỗi khi hoàn thành hoặc chặn một bước, cập nhật các trường:

```text
status
progress_percent
started_at
completed_at
evidence_artifacts
gate_result
notes
```

Quy ước `status`:

```text
not_started  : chưa làm
in_progress  : đang làm
blocked      : bị chặn bởi dữ liệu, code, compute, paper hoặc label
completed    : hoàn tất và có artifact
failed       : đã chạy nhưng fail gate
skipped      : bỏ qua có lý do
```

---

## 3. Cấu trúc thư mục triển khai đề xuất

Tạo dần khi bắt đầu code:

```text
data/
  gumbel/
    audit/
    slice/
    full/
  vae_gan/
    slice/
    full/

models/
  gumbel/
    d_scorer/
    action_gan/
  vae_gan/
    pure_vae/
    mi_vae/
    adversarial/

eval/
  gumbel/
    phase01/
    phase02/
    phase03/
    final/
  vae_gan/
    phase01/
    phase02/
    phase03/
    final/

reports/
  gumbel/
  vae_gan/
```

Không cần tạo hết ngay. Chỉ tạo khi phase bắt đầu để tránh artifact rỗng.

---

## 4. Lộ trình triển khai Gumbel Action-Surgery

### G01 — Slot/Action Audit

Mục tiêu:

```text
Chứng minh dữ liệu có đủ action/slot phi-literal.
```

Việc cần làm:

```text
1. Đọc Phase 4 canonical/delex/template artifacts.
2. Tích hợp Libinjection hoặc parser tương đương.
3. Đếm slot/action theo family: literal, operator, comment, encoding, function, keyword, whitespace.
4. Báo coverage theo technique × db_hint.
5. Xuất quyết định G0: S1_MASKED_SLOT, S2_TAMPER_ACTION hoặc STOP.
```

Artifact bắt buộc:

```text
reports/gumbel/01_slot_action_audit.md
data/gumbel/audit/action_taxonomy.json
data/gumbel/audit/g0_decision.json
```

Gate:

```text
Pass nếu có đủ non-literal/action signal.
Fail nếu chỉ có literal slot.
Nếu fail literal-only, chuyển S2 tamper-action làm đường chính.
```

Nguồn kế hoạch: [`Guiding_Gumbel-Softmax\Mục lục\01_Data_Reality_Check_And_Slot_Audit.md`](..\Guiding_Gumbel-Softmax\Mục%20lục\01_Data_Reality_Check_And_Slot_Audit.md)

---

### G02 — De-risk Action-Surgery Slice

Mục tiêu:

```text
Chạy một lát nhỏ end-to-end trước khi full-scale.
```

Việc cần làm:

```text
1. Chọn subset 5k-10k train, 1k-2k dev/test.
2. Build action-surgery dataset.
3. Round-trip check.
4. Train anchor-only action infiller.
5. Train paired-D nhỏ.
6. Freeze D và chạy D-as-scorer.
7. Chạy Gumbel action-GAN pilot 1 seed nếu các bước trên pass.
```

Artifact:

```text
data/gumbel/slice/action_surgery_train.parquet
eval/gumbel/slice/baseline_comparison.json
reports/gumbel/02_de_risk_action_surgery_slice.md
```

Gate:

```text
round_trip_success >= ngưỡng đăng ký
syntax/parse không tụt dưới floor
anchor+adv phải được so với anchor-only
```

Nguồn kế hoạch: [`Guiding_Gumbel-Softmax\Mục lục\02_De_Risk_Action_Surgery_Slice.md`](..\Guiding_Gumbel-Softmax\Mục%20lục\02_De_Risk_Action_Surgery_Slice.md)

---

### G03 — Decision Gate

Mục tiêu:

```text
Khóa protocol trước khi mở rộng.
```

So sánh:

```text
H1 Conditional MLE
H2 MLE + D-as-scorer
H3 anchor-only action infiller
H4 Gumbel action-surgery GAN
H5 rule/tamper baseline
```

Điều kiện pass:

```text
>= 3 seeds, tốt nhất 5 seeds
>= 5k samples/seed
H4 > H3 anchor-only
H4 không thua H2 trong frontier đã đăng ký
không collapse diversity/entropy
không tăng near-copy
```

Artifact:

```text
eval/gumbel/phase03/decision.json
eval/gumbel/phase03/statistical_summary.json
reports/gumbel/03_decision_gate_report.md
```

Nguồn kế hoạch: [`Guiding_Gumbel-Softmax\Mục lục\03_Decision_Gate.md`](..\Guiding_Gumbel-Softmax\Mục%20lục\03_Decision_Gate.md)

---

### G04 — Full Data Foundation + Action Taxonomy

Mục tiêu:

```text
Mở rộng action-surgery dataset lên full data nhưng giữ cluster-safe split.
```

Phase 4 hiện đã có `12,753,953` dòng và cluster leakage `0`; mọi split mới phải giữ nguyên điều này. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:4`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:33`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

Artifact:

```text
data/gumbel/full/action_foundation.parquet
data/gumbel/full/action_splits.json
reports/gumbel/04_full_data_foundation_action_taxonomy.md
```

---

### G05 — Label/Condition System

Mục tiêu:

```text
Tạo condition đủ sạch cho action generator và evaluator.
```

Không dùng `unknown` như engine thật; `unknown` là thiếu bằng chứng. [`Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md:210-219`](..\Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md)

Artifact:

```text
data/gumbel/full/condition_table.parquet
reports/gumbel/05_label_condition_system.md
```

---

### G06 — Evaluator And Model Separation

Mục tiêu:

```text
Không để classifier/WAF proxy trở thành ground truth.
```

Metric bắt buộc:

```text
round_trip_success
parse_success
slot/action validity
unique_ratio
self_bleu3
template/action entropy
exact/near-copy
cluster novelty
condition accuracy
D shortcut diagnostic
```

Artifact:

```text
eval/gumbel/evaluator_config.json
reports/gumbel/06_evaluator_model_separation.md
```

---

### G07 — MLE Anchor + D-as-scorer

Mục tiêu:

```text
Chạy baseline mạnh và deliverable GAN an toàn.
```

D-as-scorer là đóng góp độc lập, không phải phụ lục cứu nguy. [`Guiding_Gumbel-Softmax\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:54-56`](..\Guiding_Gumbel-Softmax\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

Artifact:

```text
models/gumbel/d_scorer/paired_d_scorer.pt
eval/gumbel/d_scorer_frontier.json
reports/gumbel/07_mle_anchor_and_d_scorer.md
```

---

### G08 — Gumbel Action-Surgery GAN

Mục tiêu:

```text
Train adversarial action generator sau khi H1/H2/H3 pass.
```

Không làm:

```text
full-sequence GAN
WGAN-GP
REINFORCE/MC rollout
large Transformer generator
```

Artifact:

```text
models/gumbel/action_gan/seed_*/best.pt
eval/gumbel/action_gan_comparison.json
reports/gumbel/08_gumbel_action_surgery_gan.md
```

---

### G09 — Final Evaluation

Mục tiêu:

```text
Kết luận MLE, D-as-scorer hay action-GAN là kết quả chính.
```

Kết luận hợp lệ:

```text
MLE_MAIN
D_SCORER_MAIN
GUMBEL_ACTION_PASS
INCONCLUSIVE
```

---

## 5. Lộ trình triển khai VAE-GAN

### V01 — Paper Foundation

Mục tiêu:

```text
Bổ sung paper nền trước khi claim học thuật.
```

Paper cần bổ sung:

```text
Larsen 2016 VAE-GAN
Kingma & Welling 2014 VAE
Bowman 2016 text VAE/posterior collapse
Higgins 2017 beta-VAE
```

Nếu chưa bổ sung, mọi claim về KL/free-bits/posterior collapse/disentanglement phải ghi là giả thuyết kỹ thuật, chưa phải claim có citation đầy đủ. [`Guiding_VAE_GAN\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:21-34`](..\Guiding_VAE_GAN\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

---

### V02 — Label Readiness

Mục tiêu:

```text
Xác định có đủ nhãn sạch cho controllability hay không.
```

Nếu label yếu:

```text
thử unsupervised MI trước
map post-hoc sang verified labels
không claim controllability theo technique nếu alignment không pass
```

Nguồn: [`Guiding_VAE_GAN\03_Phan_Tich_Sau_Tu_Paper.md:41-48`](..\Guiding_VAE_GAN\03_Phan_Tich_Sau_Tu_Paper.md)

---

### V03 — Partial Delex Dataset

Mục tiêu:

```text
Tạo dataset reconstruct được, vocab nhỏ, round-trip được.
```

Artifact:

```text
data/vae_gan/full/partial_delex_train.parquet
data/vae_gan/full/vocab.json
reports/vae_gan/04_full_data_foundation_partial_delex.md
```

---

### V04 — Pure-VAE Slice

Mục tiêu:

```text
Kiểm tra posterior collapse trước khi thêm adversarial.
```

Gate:

```text
reconstruction pass
validity pass
KL không về 0
active dims > ngưỡng tối thiểu
latent traversal còn hợp lệ
```

Không pass thì không mở VAE-GAN.

---

### V05 — MI Controllability

Mục tiêu:

```text
Ép latent/code mang thông tin điều khiển.
```

Hai đường:

```text
supervised MI trên verified labels
unsupervised MI rồi map post-hoc
```

---

### V06 — Adversarial VAE-GAN

Mục tiêu:

```text
Chỉ kiểm tra adversarial có cải thiện pure-VAE hay không.
```

Gate:

```text
VAE-GAN > pure-VAE
không giảm reconstruction/validity
không làm KL collapse
không tăng near-copy
```

Tie thì chọn pure-VAE. [`Guiding_VAE_GAN\03_Phan_Tich_Sau_Tu_Paper.md:8-13`](..\Guiding_VAE_GAN\03_Phan_Tich_Sau_Tu_Paper.md)

---

### V07 — Final Evaluation

Kết luận hợp lệ:

```text
PURE_VAE_MAIN
MI_VAE_MAIN
VAE_GAN_PASS
VAE_GAN_FUTURE_WORK
```

---

## 6. Cách cập nhật báo cáo tiến độ

Mỗi lần chạy xong một bước:

1. Cập nhật `timeline/timeline_progress.json`.
2. Điền `evidence_artifacts` bằng đường dẫn artifact thật.
3. Điền `gate_result` nếu bước có gate.
4. Nếu fail, không xóa; đổi `status` thành `failed` và ghi `failure_reason`.
5. Nếu blocked, ghi blocker cụ thể và bước mở khóa.

Ví dụ trạng thái sau khi chạy G01:

```json
{
  "id": "G01",
  "status": "completed",
  "progress_percent": 100,
  "gate_result": "S2_TAMPER_ACTION",
  "evidence_artifacts": [
    "reports/gumbel/01_slot_action_audit.md",
    "data/gumbel/audit/g0_decision.json"
  ]
}
```

---

## 7. Việc làm ngay

Thứ tự thực thi gần nhất:

```text
1. Tạo script/report G01 slot_action_audit.
2. Cập nhật timeline_progress.json: G01 -> in_progress.
3. Sau audit, chọn S1 hoặc S2.
4. Nếu S2, build action taxonomy slice.
5. Chạy G02 slice: anchor-only, D-as-scorer, pilot action-GAN.
6. Song song, V01 bổ sung paper nền VAE-GAN nếu muốn giữ nhánh VAE-GAN sống.
```

---

## 8. Câu chốt vận hành

```text
Gumbel/action-surgery là nhánh triển khai trước vì rủi ro thấp hơn và có D-as-scorer.
VAE-GAN là nhánh nghiên cứu có điều kiện, chỉ mở sau khi nền paper/label/pure-VAE pass.
Mọi quyết định phải đi qua artifact + gate, không đi qua cảm giác mô hình "có tiềm năng".
```
