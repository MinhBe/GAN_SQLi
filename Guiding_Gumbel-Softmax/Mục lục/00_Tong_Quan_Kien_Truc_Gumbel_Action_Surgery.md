# 00 — Tổng Quan Kiến Trúc Gumbel Action-Surgery

> Mục tiêu: biến nhánh Gumbel-Softmax thành một kế hoạch triển khai modular, cùng phong cách với `Guiding/Mục lục`, nhưng cập nhật theo phản biện mới: **Gumbel không phải đòn bẩy chống collapse; action/masked surgery + anchor + paired-D mới là đòn bẩy thật**. [`Guiding_Gumbel-Softmax\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:24-31`](..\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

---

## 1. Định hướng đã chốt

Nhánh này không quay lại SeqGAN/Gumbel full-sequence.

Kiến trúc chốt:

```text
Conditional MLE anchor
+ tamper/action surgery dataset
+ Gumbel chọn action/slot có kiểm soát
+ paired/contrastive discriminator
+ D-as-scorer như deliverable độc lập
+ evaluator execution/diversity/novelty gate
```

Tên đóng góp nên dùng trong proposal:

```text
SQLi Action-Surgery GAN with Gumbel Relaxation
```

Không nên đặt trọng tâm là:

```text
Gumbel-Softmax chống collapse
```

vì Phase 2 đã có Gumbel/anneal mà vẫn collapse cả 3 seed, và Phase 3 quyết định `MLE_MAIN`. [`Guiding\Phase 2\eval\gan_results.json:3-9`](..\..\Guiding\Phase%202\eval\gan_results.json) [`Guiding\Phase 3\eval\phase03\decision.json:2-4`](..\..\Guiding\Phase%203\eval\phase03\decision.json)

---

## 2. Luồng tổng thể

```text
01 Data Reality + Slot/Action Audit
        ↓
02 De-risk Vertical Slice
        ↓
03 Decision Gate
        ↓
04 Full Data Foundation + Libinjection/Action Taxonomy
        ↓
05 Label & Condition System
        ↓
06 Evaluator & Model Separation
        ↓
        ┌────────────────────────────────────────────┐
        │                                            │
07 MLE Anchor + D-as-scorer          08 Gumbel Action-Surgery GAN
        │                            + anchor-only ablation
        └──────────────────────┬─────────────────────┘
                               ↓
09 Final Evaluation & Delivery
                               ↑
10 Literature/Implementation Roadmap
```

---

## 3. Danh sách phase

| Số | Phase | Vai trò |
|---:|---|---|
| 01 | Data Reality + Slot/Action Audit | gate G0: dữ liệu có đủ non-literal/action signal không |
| 02 | De-risk Vertical Slice | pilot nhỏ, không đốt compute |
| 03 | Decision Gate | khóa metric, seed, kill-switch |
| 04 | Full Data Foundation | dựng action taxonomy và surgery dataset |
| 05 | Label & Condition System | condition đủ sạch để train/evaluate |
| 06 | Evaluator & Model Separation | không để classifier proxy thành ground truth |
| 07 | MLE Anchor + D-as-scorer | baseline chính và deliverable GAN an toàn |
| 08 | Gumbel Action-Surgery GAN | centerpiece có điều kiện |
| 09 | Final Evaluation & Delivery | kết luận kiến trúc |
| 10 | Literature/Implementation Roadmap | đọc paper còn thiếu và map vào quyết định |

---

## 4. Nguyên tắc bất biến

```text
1. Gumbel chỉ là estimator/relaxation, không phải thuốc chống collapse.
2. Không train Phase 08 trước gate G0 slot/action audit.
3. S2 tamper-action là đường chính nếu slot hiện tại chỉ là literal.
4. D-as-scorer là đóng góp độc lập, không phải phụ lục cứu nguy.
5. Anchor-only ablation bắt buộc; adv phải thắng anchor-only mới claim GAN có ích.
6. Không WGAN-GP vòng đầu; dùng BCE/hinge/RSGAN nhẹ và SpectralNorm nếu thật sự cần.
7. Evaluator phải có syntax/relex/novelty/diversity, không chỉ keyword proxy.
8. Multi-seed và cỡ sinh đủ lớn; không kết luận từ best seed.
9. Tie với MLE hoặc anchor-only thì chọn baseline đơn giản hơn.
10. Nếu composite tăng nhưng sub-metric quan trọng giảm, không claim thắng.
```

---

## 5. Kết luận kiến trúc

Nhánh Gumbel đáng triển khai vì GSQLi/RelGAN/MaskGAN mở ra một đường thực dụng hơn SeqGAN cũ: **action-surgery nhỏ, có anchor, có paired-D, có evaluator**. Nhưng mục tiêu đúng không phải "thắng MLE end-to-end"; mục tiêu đúng là chứng minh adversarial/action surgery tạo thêm giá trị so với anchor-only và D-as-scorer trong một vùng frontier đã đăng ký. [`Guiding_Gumbel-Softmax\03_Phan_Tich_Sau_Tu_Paper.md:75-82`](..\03_Phan_Tich_Sau_Tu_Paper.md)
