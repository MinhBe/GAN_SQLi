# Tổng Quan Kiến Trúc V5

> Kế hoạch cập nhật ngày 2026-05-22: **MLE-first vẫn là nhánh chính**, nhưng Phase 08 được mở lại có điều kiện bằng một giả thuyết mới: **paired masked payload-surgery GAN**. Không quay lại Gumbel-SeqGAN/WGAN-GP full-sequence đã fail.

---

## 1. Định hướng đã chốt

V5 không mặc định lấy GAN làm main production path.

Kiến trúc chốt:

```text
Nhánh chính:
  Conditional MLE Generator
  + evaluator-guided sampling/search

Nhánh GAN mới:
  Paired Masked Payload-Surgery GAN
  + MLE anchor trên slot
  + paired discriminator
  + D-as-scorer safety net
```

Nếu GAN mới không vượt MLE/anchor-only theo gate đã đăng ký:

```text
MLE-first là kiến trúc chính
H2 D-as-scorer là ứng dụng GAN phụ nếu có kết quả tốt
```

Nếu GAN mới vượt rõ:

```text
Masked payload-surgery GAN có thể trở thành đóng góp GAN trung tâm của luận văn.
```

---

## 2. Vì sao không quay lại Gumbel-SeqGAN cũ?

Phase 3 và Phase 3.5 đã chứng minh GAN full-sequence token-level không đủ tốt:

```text
SeqGAN/REINFORCE: collapse sau adversarial
straight-through Gumbel: tăng unique nhưng tụt syntax, variance cao
SpectralNorm/TTUR: collapse ở screening
WGAN-GP: collapse ở screening và không hợp token rời rạc
```

Ba gốc lỗi:

```text
RC1: D bão hòa làm gradient G hỏng
RC2: G thiếu mỏ neo ground-truth nên trôi khỏi cú pháp hợp lệ
RC3: GAN trượt dọc frontier MLE, không vượt frontier
```

Vì vậy Phase 08 mới phải đổi cơ chế, không chỉ đổi loss.

---

## 3. Vì sao chọn masked payload-surgery GAN?

SQLi thực tế thường biến đổi bằng:

```text
literal
operator tương đương
comment/tamper marker
encoding
identifier/literal pool
```

Trong khi khung cú pháp chính vẫn giữ:

```text
SELECT/UNION/WHERE/AND/OR
whitelist SQLi functions
template structure
```

Do đó phương án mới:

```text
giữ khung hợp lệ
chỉ sinh slot
neo bằng ground-truth slot
dùng D theo cặp cùng khung để tránh shortcut template
```

Cơ chế này đánh trực tiếp vào lỗi cũ:

```text
RC1 giảm vì G không còn quyết định toàn chuỗi token rời rạc
RC2 giảm vì anchor loss trên slot luôn bật
RC3 bị phá về mặt cấu trúc vì syntax không còn bị đánh đổi thô với diversity
```

---

## 4. Danh sách phase triển khai

| Số | Phase |
|---:|---|
| 01 | Data Reality Check |
| 02 | De-risk Vertical Slice |
| 03 | Decision Gate |
| 04 | Full Data Foundation |
| 05 | Full Label System |
| 06 | Evaluator & Model Separation |
| 07 | Main Generator: Conditional MLE + Evaluator-guided Search |
| 08 | Paired Masked Payload-Surgery GAN |
| 09 | Final Evaluation & Delivery |
| 10 | Literature/Implementation Roadmap |

---

## 5. Luồng tổng thể

```text
01 Data Reality Check
        ↓
02 De-risk Vertical Slice
        ↓
03 Decision Gate
        ↓
04 Full Data Foundation
        ↓
05 Full Label System
        ↓
06 Evaluator & Model Separation
        ↓
        ┌──────────────────────────────────────────┐
        │                                          │
07 Main MLE-first Generator        08 Paired Masked Surgery GAN
        │                          + H2 D-as-scorer safety net
        └──────────────────────┬───────────────────┘
                               ↓
09 Final Evaluation & Delivery
```

---

## 6. Nguyên tắc triển khai

```text
1. Không tin dữ liệu đầu vào trước khi phân lane.
2. Không label trước khi biết trạng thái dữ liệu.
3. Không train GAN trước khi có MLE baseline mạnh.
4. Không lặp lại WGAN-GP/SN/TTUR/ST Gumbel full-sequence đã fail.
5. Không tin WAF/DB nếu relex chưa đủ tốt.
6. Không dùng classifier proxy như ground truth.
7. Không chọn checkpoint theo best run.
8. Nếu MLE và GAN hòa, chọn MLE.
9. Nếu GAN chỉ thắng anchor-only không rõ ràng, không claim GAN tạo giá trị.
10. Nếu proxy metric tăng nhưng verified metric giảm, dừng hoặc rollback.
```

---

## 7. Kết quả cuối cùng cần có

```text
data/
  phase01/
  phase02/
  phase04/
  phase05/
  phase06/
  phase08/

models/
  mle_generator/
  d_scorer/
  paired_masked_surgery_gan/
  label_quality/
  consistency_classifier/

eval/
  mle_frontier/
  d_scorer_frontier/
  surgery_gan_comparison/
  final/

reports/
  01_data_reality_check.md
  02_slice_eval_report.md
  03_decision_gate_report.md
  08_surgery_gan_report.md
  09_final_evaluation_report.md
```

---

## 8. Kết luận

V5 là một hệ thống generation/evaluation hoàn chỉnh, không phải chỉ là một mô hình GAN.

Câu chốt:

```text
Build MLE-first để có hệ thống mạnh và ổn định.
Mở Phase 08 chỉ bằng paired masked payload-surgery GAN vì đây là giả thuyết mới đánh vào RC1/RC2/RC3.
Để dữ liệu, ablation và evaluator quyết định; không để nhu cầu "GAN phải trung tâm" làm yếu kỷ luật thực nghiệm.
```
