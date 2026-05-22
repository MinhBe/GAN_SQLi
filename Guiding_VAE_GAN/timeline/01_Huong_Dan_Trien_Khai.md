# Timeline Triển Khai VAE-GAN

Ngày tạo: 2026-05-22  
Phạm vi: chỉ `Guiding_VAE_GAN`, dùng nền dữ liệu/evaluator từ `Guiding`.

---

## 1. Quyết định triển khai mặc định

Tài liệu này chỉ áp dụng cho nhánh VAE-GAN. Mọi artifact, gate và báo cáo trong file này dùng namespace `vae_gan`.

Thứ tự triển khai bắt buộc:

```text
1. V01 paper foundation.
2. V02 label readiness.
3. V03 partial-delex dataset.
4. V04 pure-VAE slice.
5. V05 MI controllability.
6. V06 adversarial VAE-GAN chỉ mở sau khi V04/V05 pass.
7. V07 final evaluation.
```

Không bắt đầu full adversarial VAE-GAN ngay vì còn 3 blocker chính:

```text
thiếu paper nền cho KL/free-bits/disentanglement
nhãn controllability còn yếu
rủi ro posterior collapse trên GPU 6GB
```

---

## 2. File theo dõi tiến độ

Timeline JSON nằm tại:

```text
timeline/timeline_progress.json
```

Mỗi khi hoàn thành hoặc chặn một bước, cập nhật tối thiểu:

```text
updated_at
overall_progress.status
overall_progress.progress_percent
overall_progress.active_phase_id
phase.status
phase.progress_percent
phase.evidence_artifacts
phase.gate.current_result
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
  vae_gan/
    label_readiness/
    partial_delex/
    slice/
    full/

models/
  vae_gan/
    pure_vae/
    mi_vae/
    adversarial/

eval/
  vae_gan/
    label_readiness/
    partial_delex/
    slice/
    mi/
    adversarial/
    final/

reports/
  vae_gan/
```

Không cần tạo hết ngay. Chỉ tạo khi phase bắt đầu và có artifact thật.

---

## 4. Lộ trình triển khai VAE-GAN

### V01 - Paper Foundation

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

Nếu chưa bổ sung, mọi claim về KL/free-bits/posterior collapse/disentanglement phải ghi là giả thuyết kỹ thuật, chưa phải claim có citation đầy đủ.

Artifact:

```text
reports/vae_gan/01_paper_foundation.md
Asset/Total_Analyst1/Larsen_2016_VAE_GAN.md_ANALYSIS.md
Asset/Total_Analyst1/Kingma_2014_VAE.md_ANALYSIS.md
Asset/Total_Analyst1/Bowman_2016_Text_VAE.md_ANALYSIS.md
Asset/Total_Analyst1/Higgins_2017_Beta_VAE.md_ANALYSIS.md
```

---

### V02 - Label Readiness

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

Artifact:

```text
reports/vae_gan/02_label_readiness.md
data/vae_gan/label_readiness/condition_readiness.json
data/vae_gan/label_readiness/verified_condition_subset.parquet
```

---

### V03 - Partial-Delex Dataset

Mục tiêu:

```text
Tạo partial-delex dataset span-preserving, reconstruct được, vocab nhỏ, round-trip được.
```

Điều kiện dữ liệu:

```text
giữ cluster-safe split
freeze vocab trước train
round-trip partial-delex/relex phải có report
```

Artifact:

```text
data/vae_gan/partial_delex/partial_delex_train.parquet
data/vae_gan/partial_delex/vocab.json
reports/vae_gan/03_partial_delex_dataset.md
```

---

### V04 - Pure-VAE Slice

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

Không pass thì không mở adversarial VAE-GAN.

Artifact:

```text
models/vae_gan/pure_vae/slice/best.pt
eval/vae_gan/slice/pure_vae_metrics.json
reports/vae_gan/04_pure_vae_slice.md
```

---

### V05 - MI Controllability

Mục tiêu:

```text
Ép latent/code mang thông tin điều khiển.
```

Ưu tiên nếu nhãn còn yếu:

```text
1. unsupervised MI trước
2. map post-hoc sang verified labels/factors
3. chỉ dùng supervised MI khi verified labels đủ sạch
```

Không claim controllability theo `technique`/`db_hint` nếu alignment trên verified split không pass.

Artifact:

```text
models/vae_gan/mi_vae/seed_*/best.pt
eval/vae_gan/mi/mi_alignment.json
reports/vae_gan/05_mi_controllability.md
```

---

### V06 - Adversarial VAE-GAN

Mục tiêu:

```text
Chỉ kiểm tra adversarial có cải thiện pure-VAE hoặc MI-VAE hay không.
```

Ràng buộc kỹ thuật:

```text
dùng feature matching hoặc critic nhẹ
không dùng gradient penalty trên token rời rạc
không mở adversarial nếu V04/V05 chưa pass
```

Gate:

```text
VAE-GAN > pure-VAE/MI-VAE trên frontier đã đăng ký
không giảm reconstruction/validity
không làm KL collapse
không tăng near-copy
```

Tie thì chọn pure-VAE hoặc MI-VAE.

Artifact:

```text
models/vae_gan/adversarial/seed_*/best.pt
eval/vae_gan/adversarial/adversarial_comparison.json
reports/vae_gan/06_adversarial_vae_gan.md
```

---

### V07 - Final Evaluation

Kết luận hợp lệ:

```text
PURE_VAE_MAIN
MI_VAE_MAIN
VAE_GAN_PASS
VAE_GAN_FUTURE_WORK
```

Artifact:

```text
eval/vae_gan/final/model_comparison.json
eval/vae_gan/final/latent_traversal_report.md
reports/vae_gan/07_final_evaluation.md
```

---

## 5. Việc làm ngay

Thứ tự thực thi gần nhất:

```text
1. V01 hoàn thiện paper foundation.
2. V02 kiểm tra label readiness.
3. V03 tạo partial-delex dataset span-preserving, vocab frozen, round-trip được, giữ cluster-safe split.
4. V04 train pure-VAE slice; gate bắt buộc: recon pass, KL không collapse, active dims đủ, latent traversal hợp lệ.
5. V05 thêm MI controllability nếu V04 pass.
6. Chỉ sau V04/V05 pass mới xem xét V06 adversarial VAE-GAN.
```

---

## 6. Câu chốt vận hành

```text
VAE-GAN là nhánh nghiên cứu trong thư mục này.
Pure-VAE + MI là lõi trước; adversarial chỉ là challenger có gate.
Mọi quyết định phải đi qua artifact + gate, không đi qua cảm giác mô hình "có tiềm năng".
```
