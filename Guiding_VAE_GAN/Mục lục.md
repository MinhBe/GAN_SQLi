# Mục lục — Nhánh VAE-GAN (GAN-trung-tâm, Latent Controllable)

> **Ngày:** 2026-05-22
> **Nhánh này là gì:** phiên bản **đặt VAE-GAN làm trung tâm** của luận văn — kiến trúc hybrid *latent*
> (encoder → latent z có cấu trúc → decoder + discriminator). Điểm khác biệt cốt lõi so với 2 nhánh kia:
> **không gian latent có cấu trúc → ĐIỀU KHIỂN được kiểu attack/độ ngụy trang qua z** (conditional gen,
> interpolation, disentanglement). Đây là năng lực mà các baseline không có latent cấu trúc **không** dễ có.
>
> **Nguồn gốc:** `Guiding/Kịch bản/VAE-GAN_SQLi_Guiding.md` (bản 05-04).
>
> **Phạm vi thư mục:** `Guiding_VAE_GAN` chỉ chứa kế hoạch cho nhánh VAE-GAN theo trục **điều khiển/cấu trúc latent**
> (controllability). Nhánh này tái dùng nền data, label, evaluator và literature từ `Guiding` khi cần.
>
> **Nội dung chi tiết:** xem `00_Ke_Hoach_Tong_The.md` (all-in-one). File này chỉ là index điều hướng.

---

## Danh sách phase

| Số | Phase | Trạng thái | Section trong all-in-one |
|---:|---|---|---|
| 00 | Tổng quan kiến trúc VAE-GAN | mới | §E |
| 01 | Nền dữ liệu (Data Foundation) | **tái dùng** `Guiding/Phase 1` + `Mục lục/04` | §F.01 |
| 02 | Label & verified split | **tái dùng** `Guiding/Mục lục/05` | §F.02 |
| 03 | Evaluator thực thi + Composite Score | **mới — cổng mọi đo lường** | §F.03 |
| 04 | Partial de-lex + VAE-GAN dataset | **mới** (giữ keyword/function, mask table/col/literal) | §F.04 |
| 05 | Conditional MLE / pure-VAE baseline | **tái dùng** `Guiding/Phase 2,7` + thêm pure-VAE | §F.05 |
| 06 | Warm-up VAE (recon + KL, chưa có D) | **mới — gate posterior collapse** | §F.06 |
| 07 | Adversarial VAE-GAN (thêm D + feature matching) | **mới — centerpiece** | §F.07 |
| 08 | Controllability + Benchmark + δ-correlation | **mới** | §F.08 |
| 09 | Final evaluation & kết luận | mới | §F.09 |
| 10 | Literature mapping | **tái dùng** `Guiding/Mục lục/10` | §F.10 |

---

## Sơ đồ luồng tổng thể

```text
[Tái dùng nền V5]
01 Data Foundation ──→ 02 Label & verified split
                              │
                              ▼
03 Evaluator thực thi + Composite Score   ←── CỔNG: mọi metric phải qua đây
        │   (parse + execute + injection-structure + novelty; WER là phụ)
        ▼
04 Partial de-lex + VAE-GAN dataset (giữ keyword+function, mask slot; round-trip check)
        │
        ▼
05 Baseline: Conditional MLE + pure-VAE (+ KN-5/template/LSTM)
        │
        ▼
06 WARM-UP VAE  ←── GATE: KL ∈ [5,50] nats, recon ≥ 70%, KHÔNG posterior collapse
        │        (encoder Transformer/LSTM → z, decoder, recon + KL annealing + free bits)
        ▼
07 ADVERSARIAL VAE-GAN (thêm D 1D-CNN + feature matching; D:G điều tiết; KHÔNG GP token rời rạc)
        │
        ▼
08 Controllability (latent walk, conditional gen, disentanglement)
   + Benchmark đa phương pháp + δ-CORRELATION (thí nghiệm quan trọng nhất) + sample efficiency
        ▼
09 Final eval → kết luận: controllability có giá trị / VAE-GAN thắng qua gate / future work
        ▲
10 Literature mapping ──┘ (Larsen-2016 VAE-GAN, Kingma-VAE, Bowman-2016 KL-annealing, β-VAE)
```

---

## Nguyên tắc bất biến (kế thừa kỷ luật V5)

```text
1. Evaluator thực thi (không phải "có keyword") là ground-truth đo lường; WER chỉ là phụ.
2. Warm-up VAE phải qua gate posterior-collapse TRƯỚC khi thêm discriminator.
3. Adversarial (full VAE-GAN) phải thắng pure-VAE/anchor mới claim GAN-adversarial có giá trị.
4. Controllability phải đo bằng metric khách quan (conditional accuracy, disentanglement), không định tính suông.
5. Multi-seed, mean±CI, đơn vị = seed; không cherry-pick.
6. KHÔNG dùng WGAN-GP gradient-penalty trên nội suy token rời rạc; ưu tiên feature-matching + recon anchor.
7. Proxy tăng nhưng verified giảm → dừng/rollback. Tie → baseline đơn giản hơn.
8. 6GB là ràng buộc cứng: nếu full-spec không chạy nổi, thu nhỏ model trước khi bỏ thí nghiệm.
```
