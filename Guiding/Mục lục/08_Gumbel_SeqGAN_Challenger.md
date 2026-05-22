# 08 — Paired Masked Payload-Surgery GAN

> Mục tiêu: mở lại GAN bằng một giả thuyết mới, không lặp lại SeqGAN/Gumbel/WGAN-GP full-sequence đã fail. Phase 08 dùng GAN làm trung tâm ở mức "phẫu thuật payload": giữ khung SQLi hợp lệ và chỉ sinh biến thể tại các slot có kiểm soát.

---

## 1. Bối cảnh bắt buộc

Phase 3 và Phase 3.5 đã chốt:

```text
MLE_MAIN
GAN full-sequence token-level = không scale
```

Các biến thể đã fail hoặc không đủ thắng MLE:

```text
SeqGAN/REINFORCE
straight-through Gumbel full-sequence
SpectralNorm/TTUR
WGAN-GP trên token rời rạc
```

Nguyên nhân gốc đã quan sát:

```text
RC1: adversarial coupling trên token rời rạc làm D bão hòa, gradient G hỏng
RC2: thiếu mỏ neo ground-truth làm G trôi khỏi cú pháp hợp lệ
RC3: GAN trượt dọc frontier MLE, đổi syntax lấy diversity thay vì vượt frontier
```

Điểm sáng còn giữ lại:

```text
G4 pass: D không ăn gian shortcut representation rõ ràng, D học được tín hiệu thật.
```

Phase 08 chỉ hợp lệ vì nó là một giả thuyết mới đánh vào RC1/RC2/RC3 bằng cách đổi đơn vị sinh từ "toàn chuỗi token" sang "slot surgery có khung cố định".

---

## 2. Quyết định kiến trúc

Phase 08 gồm ba nhánh so sánh, không chỉ một model:

```text
H1: Conditional MLE
    baseline chính + nguồn candidate

H2: Discriminator-as-scorer
    train D, freeze D, dùng D để rerank/reject candidate MLE

H5': Paired Masked Payload-Surgery GAN
     generator chỉ điền slot trong khung đã mask
     discriminator so real/fake theo cặp cùng khung và condition
```

Trong đó H5' là đóng góp GAN trung tâm. H2 là lưới an toàn và ablation bắt buộc.

---

## 3. Vì sao chọn paired masked surgery thay vì H5 thường

H5 thường giữ khung và sinh slot là hướng tốt, nhưng còn ba rủi ro:

```text
1. D có thể học template ID, số slot, độ dài, hoặc condition imbalance.
2. MLE anchor quá mạnh có thể biến mô hình thành supervised infiller, không còn chứng minh GAN có ích.
3. Syntax_validity cũ quá yếu: giữ keyword là có thể pass syntax dù payload không thật sự tốt.
```

Vì vậy Phase 08 dùng biến thể chặt hơn:

```text
Paired D:
  D luôn so real/fake trên cùng khung mask, cùng technique, cùng db_hint.

Ablation bắt buộc:
  anchor-only
  anchor + adversarial
  MLE + D-rerank

Evaluator hardening:
  không dùng syntax keyword-only làm bằng chứng chính.
```

Nếu `anchor + adversarial` không thắng `anchor-only`, không được claim GAN tạo giá trị.

---

## 4. Dữ liệu đầu vào

Nguồn tái dùng:

```text
Guiding/Phase 2/slice_labeled.parquet
Guiding/Phase 2/models/mle_baseline/seed_42/best.pt
Guiding/Phase 2/phase02_05_gan_train.py
Guiding/Phase 2/phase02_06_eval.py
Skill/sqli-data-curator/scripts/delex_v2.py
```

Lưu ý quan trọng sau phản biện:

```text
placeholder_types trong slice_labeled.parquet gần như rỗng.
Không được coi placeholder_types là metadata slot đã sẵn sàng.
Slot phải được dựng lại từ payload_working/payload_delex bằng span-preserving surgery parser.
```

Phase 08A phải tạo dữ liệu surgery mới:

```text
payload_working
payload_delex
mask_frame
slot_spans
slot_types
slot_values_real
technique_primary
db_hint
syntax_validity
source_row_id
template_id
```

Round-trip bắt buộc:

```text
mask_frame + slot_values_real -> payload tái dựng
payload tái dựng phải khớp payload gốc hoặc khớp canonical form đã định nghĩa.
```

---

## 5. Mask taxonomy

Giữ cố định:

```text
SQL keywords
whitelist SQLi functions
structural punctuation
template skeleton
```

Cho phép sinh:

```text
literal string
numeric literal
time interval
hex/encoded literal
identifier nếu được đánh dấu an toàn
operator tương đương trong whitelist
comment/tamper marker trong whitelist
```

Không sinh tự do:

```text
toàn bộ chuỗi
keyword chính
function SQLi quan trọng
template control flow
```

---

## 6. Generator

Tên:

```text
MaskedInfillGenerator
```

Mô hình mặc định:

```text
LSTM nhỏ
embedding_dim = 64
hidden_dim = 256
batch_size nhỏ vừa 6GB VRAM
```

Input:

```text
mask_frame tokens
slot_type tokens
technique_primary embedding
db_hint embedding
```

Output:

```text
slot fill tokens theo từng vị trí mask
```

Không dùng:

```text
MC rollout
full-sequence REINFORCE
WGAN-GP gradient penalty trên token rời rạc
unrolled GAN
```

---

## 7. Discriminator

Tên:

```text
PairedSlotDiscriminator
```

Input:

```text
mask_frame
filled_payload
slot_type sequence
condition
```

Nguyên tắc chống shortcut:

```text
Real và fake trong cùng batch phải được ghép theo cùng template_id hoặc cùng mask_frame.
D không được chỉ học template, độ dài, số slot, hoặc condition distribution.
```

Loss:

```text
BCE hoặc hinge loss
không dùng WGAN-GP
```

Điều tiết D:

```text
freeze D khi acc(D) > 0.8
giảm D steps nếu D bão hòa
cap capacity D
early stop nếu unique < 0.1 hoặc D loss -> 0 kéo dài
```

---

## 8. Loss Generator

Loss chính:

```text
L_G =
  L_anchor_slot
+ lambda_adv * L_adv_slot
+ lambda_entropy * L_entropy_slot
+ lambda_novelty * L_novelty_slot
```

Trong đó:

```text
L_anchor_slot:
  teacher-forcing CE trên slot thật, luôn bật để chống RC2

L_adv_slot:
  adversarial loss từ D, trọng số nhỏ để tránh RC1

L_entropy_slot:
  giữ đa dạng ở slot, chống collapse

L_novelty_slot:
  phạt exact-copy/near-copy slot quá gần train nếu vượt ngưỡng
```

Quy tắc claim:

```text
Nếu anchor + adversarial <= anchor-only:
  kết luận GAN không thêm giá trị.

Nếu anchor + adversarial > anchor-only và >= MLE frontier trong vùng đăng ký:
  có thể claim masked adversarial infill tạo giá trị.
```

---

## 9. H2: Discriminator-as-scorer

H2 là ablation và safety net.

Quy trình:

```text
1. Train D phân biệt real payload vs MLE-generated/candidate payload.
2. Freeze D.
3. MLE sinh N candidate theo condition.
4. D chấm điểm candidate.
5. Rerank/reject bằng D + novelty + syntax/type guard.
6. Giữ top candidate theo vùng frontier đã đăng ký.
```

Không làm:

```text
không cập nhật G bằng adversarial gradient
không claim đây là GAN training đầy đủ
```

Vai trò luận văn:

```text
tận dụng điểm sáng G4
đảm bảo vẫn có ứng dụng discriminator từ GAN pipeline nếu H5' không vượt gate
```

---

## 10. Evaluator hardening

Không dùng đơn độc metric cũ:

```text
syntax_validity_rate kiểu keyword-only
```

Metric cần bổ sung:

```text
round_trip_success
slot_validity_rate
template_preservation_rate
exact_copy_rate
near_copy_rate
nearest_neighbor_similarity
template_entropy
slot_entropy
condition_accuracy
paired_D_shortcut_diagnostic
```

Syntax gate mới:

```text
syntax_validity_rate cũ chỉ là proxy phụ.
Primary quality phải có parse/structure/slot validity hoặc evaluator rule chặt hơn.
```

---

## 11. Pre-registered gates

Đơn vị thống kê:

```text
seed
```

Số seed:

```text
pilot: 1 seed
confirmatory: >= 3 seeds, mục tiêu 5 nếu runtime cho phép
```

So sánh chính:

```text
Conditional MLE
MLE + D-rerank
anchor-only masked infiller
paired masked payload-surgery GAN
```

Gate tối thiểu:

```text
syntax/structure >= MLE * 0.95 hoặc vượt ngưỡng đăng ký
unique_ratio >= MLE trong cùng vùng quality
self_bleu3 không xấu hơn MLE ngoài ngưỡng
near_copy_rate không tăng bất thường
paired D shortcut pass
anchor + adversarial thắng anchor-only
CI theo seed không cho thấy chỉ là nhiễu
```

Tie-break:

```text
Nếu không rõ, chọn MLE hoặc H2.
Không chọn H5' chỉ vì hợp thesis hơn.
```

---

## 12. Stop rule

Dừng H5' nếu:

```text
D loss -> 0 kéo dài và G loss tăng mất kiểm soát
acc(D) kẹt > 0.9 dù đã freeze/gating
unique_ratio < 0.1
slot_entropy collapse
syntax/structure tụt dưới 0.6 ở pilot
anchor + adversarial không vượt anchor-only sau pilot hợp lệ
VRAM vượt 6GB hoặc runtime không phù hợp multi-seed
```

Khi dừng:

```text
ghi negative result H5'
chuyển deliverable GAN sang H2 D-as-scorer
giữ MLE-first là main
```

---

## 13. Files đầu ra

Đặt trong:

```text
Guiding/Phase 8/
```

Files:

```text
phase08_00_preregistered_protocol.md
phase08_01_surgery_data.py
phase08_02_models.py
phase08_03_train_paired_surgery_gan.py
phase08_04_d_scorer.py
phase08_05_eval.py
reports/08_surgery_gan_report.md
```

Artifacts:

```text
data/phase08/surgery_train.parquet
data/phase08/surgery_val.parquet
data/phase08/surgery_test.parquet
eval/phase08/decision.json
eval/phase08/statistical_summary.json
eval/phase08/mle_vs_surgery_frontier.png
```

---

## 14. Thứ tự thực hiện

```text
08A. Data/evaluator hardening
     dựng span-preserving surgery dataset
     round-trip check
     syntax/slot evaluator chặt hơn

08B. H2 safe baseline
     train D scorer
     rerank MLE candidate
     log frontier

08C. H5' pilot
     1 seed paired masked surgery GAN
     kiểm tra NaN, VRAM, D saturation, slot entropy

08D. Confirmatory
     >= 3 seeds nếu pilot pass
     mean/std/CI theo seed

08E. Report
     so H1/H2/anchor-only/H5'
     kết luận kiến trúc
```

---

## 15. Kết luận

Phase 08 không phải quay lại Gumbel-SeqGAN cũ.

Câu chốt:

```text
GAN chỉ được mở lại dưới dạng paired masked payload-surgery GAN.
Nếu adversarial slot infill không thắng anchor-only, không claim GAN tạo giá trị.
Nếu H5' fail, H2 D-as-scorer là deliverable GAN hợp lệ hơn việc lặp lại full-sequence GAN đã collapse.
```
