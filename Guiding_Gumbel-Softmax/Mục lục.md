# Mục lục — Nhánh Gumbel-Softmax (GAN-trung-tâm)

> **Ngày:** 2026-05-22
> **Nhánh này là gì:** phiên bản **đặt GAN (họ Gumbel-Softmax) làm trung tâm** của luận văn, dùng *khung
> benchmark* của tài liệu Gumbel-Softmax gốc nhưng **thay lõi GAN** bằng Gumbel-trên-masked-slot + paired
> discriminator + evaluator thực thi. Tái dùng toàn bộ nền dữ liệu/đánh giá của V5.
>
> **Quan hệ với `Guiding/Mục lục`:** `Guiding` = kế hoạch **MLE-first** (GAN mở có điều kiện ở Phase 08).
> Nhánh này = **GAN-trung-tâm** cho yêu cầu "luận văn bắt buộc có GAN". Hai nhánh **chia sẻ chung** nền
> data (Phase 1/4), label (Phase 5), evaluator (Phase 6) và literature roadmap (Phase 10) — không làm lại.
>
> **Nội dung chi tiết:** xem `00_Ke_Hoach_Tong_The.md` (all-in-one). File này chỉ là index điều hướng.

---

## Danh sách phase

| Số | Phase | Trạng thái | Section trong all-in-one |
|---:|---|---|---|
| 00 | Tổng quan kiến trúc nhánh GAN-trung-tâm | mới | §E |
| 01 | Nền dữ liệu (Data Foundation) | **tái dùng** `Guiding/Phase 1` + `Mục lục/04` | §F.01 |
| 02 | Label & verified split | **tái dùng** `Guiding/Mục lục/05` | §F.02 |
| 03 | Evaluator thực thi + Composite Score | **mới — cổng mọi đo lường** | §F.03 |
| 04 | Tamper-aware delex + surgery dataset | **mới** | §F.04 |
| 05 | Conditional MLE baseline + frontier | **tái dùng** `Guiding/Phase 2,7` | §F.05 |
| 06 | H2 — Discriminator-as-scorer (paired) | mới (lưới an toàn) | §F.06 |
| 07 | Gumbel masked payload-surgery GAN | **mới — centerpiece** | §F.07 |
| 08 | Benchmark 6 phương pháp + RQ1/2/3 | mới | §F.08 |
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
        │   (parse + execute + injection-structure + novelty)
        ▼
04 Tamper-aware delex + surgery dataset (round-trip check, vệ sinh rác)
        │
        ▼
05 Conditional MLE baseline + frontier  ←── baseline mạnh mọi GAN phải vượt
        │
        ├───────────────────────────┬───────────────────────────┐
        ▼                           ▼                           ▼
06 H2 D-as-scorer            07 Gumbel masked            (anchor-only ablation
   (paired, safety net)         payload-surgery GAN          = trong 07)
        │                     (08A audit → pilot → multi-seed)
        └───────────────┬───────────┘
                        ▼
08 Benchmark 6 phương pháp trên frozen test (Composite Score, RQ1/2/3)
                        ▼
09 Final eval → kết luận: MLE thắng / GAN thắng qua gate mới / GAN future work
                        ▲
10 Literature mapping ──┘ (nuôi quyết định kiến trúc xuyên suốt)
```

---

## Nguyên tắc bất biến (kế thừa kỷ luật V5)

```text
1. Evaluator thực thi (không phải "có keyword") là ground-truth đo lường.
2. Anchor-only ablation bắt buộc; adv phải thắng anchor-only mới claim GAN có giá trị.
3. Multi-seed, mean±CI, đơn vị = seed; không cherry-pick.
4. Không lặp WGAN-GP/SN/TTUR/Gumbel-full-sequence đã fail (Phase 3/3.5).
5. Proxy tăng nhưng verified giảm → dừng/rollback.
6. Tie MLE↔GAN → chọn MLE; GAN-trung-tâm là khung benchmark, không phải ép GAN thắng.
```
