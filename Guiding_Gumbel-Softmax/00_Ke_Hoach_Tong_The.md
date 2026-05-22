# Kế Hoạch Tổng Thể (All-in-One) — Nhánh Gumbel-Softmax GAN-trung-tâm

> **Ngày:** 2026-05-22 · **Phần cứng:** RTX 3050 6GB + 20GB RAM · **Repo:** `C:\Users\Admin\Documents\GAN_SQLi`
> **Nguồn:** `Guiding_Gumbel-Softmax/Gumbel-Softmax_SQLi_Guiding.md` (bản gốc 05-04) + nền V5
> (`Guiding/Phase 1,2`, `Guiding/Mục lục/00–10`, `Kết luận 1.md`, kết quả Phase 3/3.5).
> File này là bản gom toàn bộ; điều hướng nhanh xem `Mục lục.md`.

---

## A. Mục lục

- **B.** Bối cảnh & quan hệ với Guiding V5
- **C.** Đính chính bản Gumbel-Softmax gốc (giữ gì / bỏ gì / thay gì)
- **D.** Phân tích đa góc độ (7 góc)
- **E.** Kiến trúc chốt của nhánh
- **F.** Roadmap phase 00–10 (mục tiêu / deliverable / gate / files)
- **G.** Gate pre-registered + chống tự lừa
- **H.** Tài nguyên 6GB, timeline, cây deliverable

---

## B. Bối cảnh & quan hệ với Guiding V5

`Guiding/Mục lục` (V5, cập nhật 05-22) là kế hoạch **MLE-first**: nhánh chính Conditional MLE +
evaluator-guided search; Phase 08 chỉ mở có điều kiện bằng paired masked payload-surgery GAN. Đó là kế
hoạch đúng về kỷ luật khoa học, nhưng GAN **không** ở vị trí trung tâm.

Luận văn của bạn **bắt buộc có GAN làm điểm chính**. Vì vậy nhánh `Guiding_Gumbel-Softmax` này **đảo vai
trò**: đặt GAN (họ Gumbel) làm *đối tượng nghiên cứu trung tâm*, đóng khung như một **benchmark
Structured Discrete Sequence Generation (SDSG)** — lấy chính *phương pháp luận benchmark* của tài liệu
Gumbel-Softmax gốc (Composite Score, so 6 phương pháp, frozen test, RQ1/RQ2/RQ3).

Hai nhánh **chia sẻ nền chung, không trùng lặp công sức**:

| Thành phần | Guiding (V5, MLE-first) | Guiding_Gumbel-Softmax (GAN-trung-tâm) |
|---|---|---|
| Nền dữ liệu (Phase 1/4) | sở hữu | **tái dùng** |
| Label & verified split (Phase 5) | sở hữu | **tái dùng** |
| Evaluator/model separation (Phase 6) | sở hữu | **tái dùng + làm chặt** (evaluator thực thi) |
| Generator chính | Conditional MLE | Gumbel masked-surgery GAN (MLE là baseline) |
| Vai trò GAN | phụ, có điều kiện | **trung tâm, là object của benchmark** |
| Khung đóng góp | hệ thống generation/eval | **benchmark phương pháp + đóng góp masked-surgery GAN** |
| Literature (Phase 10) | sở hữu | **tái dùng** |

> Câu chốt: nhánh này **không thay thế** V5; nó là *góc nhìn GAN-trung-tâm* trên cùng một nền, để viết
> luận văn có GAN làm trục — nhưng **vẫn tuân thủ kỷ luật** của V5 (gate, multi-seed, anti-cherry-pick).

---

## C. Đính chính bản Gumbel-Softmax gốc

Tài liệu `Gumbel-Softmax_SQLi_Guiding.md` (05-04) **không dùng nguyên trạng** được, vì:

**Hai vấn đề phải bỏ:**
1. **Path/dữ liệu chết:** trỏ `C:\Users\Admin\Documents\GAN`, `Asset/Data/master_sqli.csv`,
   `result_batch_*.csv`, data 41.460 dòng, các `SQLi-*-Roadmap.md` — **không còn tồn tại**; có trước nền
   V5 (slice 38.906 dòng đã gán nhãn hiện tại).
2. **Lõi kỹ thuật = đúng thứ đã fail:** decoder Gumbel **full-sequence** + Dilated CNN + **WGAN-GP** chính
   là cấu hình đã collapse ở Phase 3/3.5 (V_C = WGAN-GP collapse screening; straight-through Gumbel = V_A
   tụt syntax 0.449 vs MLE 0.712). Nội suy gradient-penalty trên token rời rạc còn sai bản chất.

**Phần giữ lại (giá trị thật):**
- **Phương pháp luận benchmark**: Composite Score, so sánh nhiều baseline trên **frozen test**, RQ1/2/3,
  bootstrap CI, hard-constraint validity. Đây là khung biến GAN thành *đối tượng đo lường nghiêm túc*.
- **Re-lexicalization + Syntax-Filter buffer**: ý tưởng tách sinh (delex) khỏi cụ thể hóa (relex) — hợp
  với surgery.

**Phần thay (nâng cấp "hướng đi mới"):**
- Lõi GAN: **Gumbel chỉ trên masked-slot** (không full-sequence) + **MLE anchor** + **paired discriminator**.
- Validity trong Composite Score: đo bằng **evaluator thực thi** (parse + execute + injection-structure),
  KHÔNG phải "có keyword" (metric cũ → 1.0 by construction khi giữ khung).
- Không WGAN-GP trên token rời rạc; D là classifier (BCE/hinge) + freeze gating.

---

## D. Phân tích đa góc độ

### D.1 Góc khoa học / phương pháp luận
Khung benchmark SDSG hợp lý và **bảo vệ được luận văn dù GAN thắng hay thua**: contribution là *so sánh có
kỷ luật* + phương pháp masked-surgery. Bắt buộc: pre-registration, multi-seed (≥5, đơn vị = seed),
mean±CI, anti-cherry-pick, frozen test có hash. RQ rõ:
- **RQ1**: phương pháp nào đạt Composite Score cao nhất trên SDSG (SQLi)?
- **RQ2**: tradeoff validity↔diversity ra sao? (ta đã có bằng chứng GAN full-sequence trượt dọc frontier)
- **RQ3**: masked-surgery + paired-D có **phá** được tradeoff đó so với full-sequence Gumbel/SeqGAN không?

### D.2 Góc kiến trúc
Full-sequence buộc G quyết định **toàn bộ** chuỗi token rời rạc → bề mặt collapse lớn + D dễ bão hòa
(RC1). Masked-surgery **giữ khung hợp lệ**, G chỉ điền slot → (a) syntax cao by construction (phá RC3
về cấu trúc), (b) ít quyết định rời rạc → giảm RC1. **Paired D** (so real/fake trên **cùng khung +
cùng condition, chỉ khác slot fill**) buộc D đánh giá *chất lượng slot* thay vì bắt template/độ dài →
chống lớp shortcut mới. **MLE anchor** trên slot luôn bật → chống drift (RC2).

### D.3 Góc dữ liệu (đã xác minh trên `slice_labeled.parquet`, 38.906 dòng)
- Slot trong delex hiện tại **chỉ là literal**: `__NUM__` ×36.876, `__STR__` ×33.744, `__TIME__` ×354.
  **Không có** slot operator/comment/encoding/identifier.
- `placeholder_types` **99,3% rỗng** → không dùng.
- Metric `syntax_validity_rate` cũ = regex "có keyword" → vô nghĩa cho surgery.
- Delex không thống nhất: Phase 2 `__NUM__/__STR__/__TIME__` ≠ `delex_v2` `__INT__/__FLOAT__/__HEX__/__IDENT__`.
- Rác lọt delex (vd `__ex]r&rv3;...__NUM__`); mất cân bằng: `error_based`=405, `db_hint` 78% unknown
  (oracle=146, sqlite=286, postgres=812, mssql=2205, mysql=5211).
- **Hệ quả:** Phase 04 (tamper-aware delex) là **tiểu dự án thật**, không phải tinh chỉnh; ô hiếm phải
  gộp/thu hẹp điều kiện; phải vệ sinh rác trước.

### D.4 Góc tài nguyên (RTX 3050 6GB)
Khả thi nếu: model nhỏ (LSTM/Transformer mini, embed≈64–128, hidden≈256), **không MC rollout**, **không
GP** (tránh `create_graph` nhân đôi bộ nhớ + sai token rời rạc), D classifier nhẹ + freeze gating,
batch 32–64, Gumbel chỉ trên vài token slot. Tham chiếu: pipeline Phase 3.5 chạy ~4h17m trên đúng máy này.

### D.5 Góc rủi ro & kết cục dễ xảy ra
- **Kết cục khả dĩ nhất: adv ≈ anchor-only** (masked infill + anchor mạnh ≈ supervised infiller; tín
  hiệu adversarial trên literal gần rỗng). → **bắt buộc** đóng khung S4 (đóng góp phương pháp luận) ngay
  từ proposal để luận văn sống sót.
- Collapse vẫn có thể nếu λ_adv lớn → điều tiết D + anchor.
- Sparsity ô hiếm → controllability per-(technique×db) yếu; có thể phải claim controllability hẹp.

### D.6 Góc đóng góp luận văn (GAN bắt buộc trung tâm)
GAN trung tâm theo nghĩa **object của benchmark** + **phương pháp masked-surgery mới**. Ngay cả khi
masked-surgery không vượt MLE, luận văn vẫn có: (a) đặc tả tradeoff validity↔diversity có số liệu, (b)
chẩn đoán D-saturation + cơ chế đề xuất, (c) D-as-scorer là ứng dụng GAN chạy được, (d) so sánh
full-sequence (fail) vs masked (mới). Đây là đóng góp thật, trung thực.

### D.7 Góc so với nhánh V5
Bổ trợ, không mâu thuẫn: V5 trả lời "hệ thống tốt nhất là gì" (MLE-first); nhánh này trả lời "GAN đóng
góp được gì, ở đâu, đo bằng benchmark nào". Cùng nền → kết quả của nhánh này feed ngược vào Phase 09 của V5.

---

## E. Kiến trúc chốt của nhánh

```text
                 ┌─────────────────────────────────────────────┐
   condition ───▶│  Gumbel Masked Payload-Surgery GAN (07)     │
 (technique,db)  │   - khung SQLi hợp lệ giữ nguyên             │──▶ payload biến thể
   khung+mask ──▶│   - Gumbel-Softmax CHỈ trên slot             │    (validity by construction)
                 │   - MLE anchor loss trên slot (chống RC2)    │
                 │   - điều tiết D: adaptive D/G, freeze acc>0.8 │
                 └───────────────┬─────────────────────────────┘
                                 │  (08A audit quyết: S1 paired-masked vs S2 tamper-action)
   real/fake cùng khung+cond ───▶│
                 ┌───────────────▼─────────────────────────────┐
                 │  Paired Discriminator (classifier BCE/hinge) │  ── KHÔNG WGAN-GP token rời rạc
                 └───────────────┬─────────────────────────────┘
                                 │ freeze → dùng lại ở 06
                 ┌───────────────▼─────────────────────────────┐
                 │  H2 D-as-scorer (06): rerank/reject candidate │  ── lưới an toàn, deliverable chắc
                 │  từ Conditional MLE baseline (05)             │
                 └───────────────┬─────────────────────────────┘
                                 ▼
        Evaluator thực thi (03): parse + execute(sqlite) + injection-structure + novelty
                                 ▼
        Benchmark (08): Markov · MLE · SeqGAN(cũ) · Gumbel-full(cũ) · Gumbel-masked(mới) · D-rerank
                                 ▼               → Composite Score, RQ1/2/3
```

**Composite Score (điều chỉnh):** `S = w1·Validity_exec + w2·(1−SelfBLEU3) + w3·(1−Ŵ1) + w4·Novelty`,
trong đó **Validity_exec** = tỉ lệ payload parse-được **và** execute-được trên sqlite sandbox **và** giữ
cấu trúc injection (không phải comment trống). Hard-constraint: Validity_exec < 50% → loại khỏi ranking.

---

## F. Roadmap phase 00–10

### F.00 — Tổng quan kiến trúc nhánh
Chốt định hướng (mục E), khóa giả thuyết & gate (mục G). Deliverable: chính file này + `Mục lục.md`.

### F.01 — Nền dữ liệu *(tái dùng)*
Dùng `Guiding/Phase 1/phase01_data_reality.parquet` (12,75M) + kế hoạch `Guiding/Mục lục/04`
(canonical, dedup sha256, near-dup MinHash, lane-aware strip wrapper, cluster-safe split).
Gate: cluster leakage = 0; report top-template coverage. **Không làm lại** nếu Phase 04 V5 đã chạy.

### F.02 — Label & verified split *(tái dùng)*
Theo `Guiding/Mục lục/05`: `technique_primary` tách `intent_secondary`; `unknown` không phải class
generator; verified_dev/test. Deliverable: `data/phase05/{labeled,verified_dev,verified_test}.parquet`.

### F.03 — Evaluator thực thi + Composite Score **(mới — cổng mọi đo lường)**
- `evaluator_exec.py`: parse-tree (sqlparse) + **execute oracle** sqlite in-memory (mysql/pg tùy chọn) +
  **injection-structure check** + novelty (Jaccard/edit-distance) + diversity (self-BLEU3, template entropy).
- `composite_score.py`: ráp Composite Score (validity = execute-based).
- Gate: phân biệt đúng ≥20 known-valid vs ≥20 known-broken; oracle không treo; thay hẳn metric keyword cũ.
- Deliverable: `eval/phase03/evaluator_calibration.json`, `reports/03_evaluator_report.md`.

### F.04 — Tamper-aware delex + surgery dataset **(mới)**
- `delex_unified.py`: hợp nhất 1 bộ token; **span-preserving** (round-trip delex→refill = gốc); đánh dấu
  slot **ngoài literal** (operator tương đương, comment/whitespace, encoding, function-choice) nếu trích được.
- `surgery_dataset.py`: dựng tuple `(khung_mask, slot_fills_thật, condition)`; vệ sinh rác; gộp ô hiếm.
- `slot_audit.py`: đếm slot *có nghĩa* theo `technique_primary × db_hint` → **dữ kiện chốt S1 vs S2**.
- Gate: round-trip ≥99% mẫu sạch; báo cáo số slot non-literal khả dụng.
- Deliverable: `data/phase04/surgery_{train,dev,frozen_test}.parquet` + hash + `reports/04_surgery_data_report.md`.

### F.05 — Conditional MLE baseline + frontier *(tái dùng Phase 2/7)*
Dùng `Guiding/Phase 2/models/mle_baseline/seed_42/best.pt` + frontier đã khóa (unique 0.803, self_bleu3
0.013, syntax 0.712). Mở rộng theo `Guiding/Mục lục/07`: temperature/top-k/top-p/rep-penalty, best-of-N,
rejection sampling, diversity-aware rerank. Deliverable: `eval/phase05/mle_frontier.json` + candidates.

### F.06 — H2 Discriminator-as-scorer (paired) **(lưới an toàn)**
Train D **paired** (real vs MLE-generated, cùng khung+condition, BCE) → freeze → rerank/guided-decode
candidate MLE + lọc novelty. Deliverable: `models/d_scorer.pt`, `eval/phase06/d_rerank_frontier.json`.
Đây là **deliverable GAN gần như chắc chắn chạy được**.

### F.07 — Gumbel masked payload-surgery GAN **(centerpiece)**
- **08A-first:** chạy F.03+F.04 audit + **fail-fast probe** (1 seed: anchor-only vs anchor+adv, đo bằng
  evaluator F.03) → quyết **S1 paired-masked** (đủ slot non-literal) vs **S2 tamper-action** (chỉ literal
  → sinh tổ hợp phép biến đổi giữ-hợp-lệ, tham chiếu sqlmap tamper).
- **Pilot 1 seed** → **confirmatory ≥5 seed** nếu pilot qua gate.
- Model: encoder khung + decoder điền slot (Gumbel trên mask) + MLE anchor + điều tiết D.
- Deliverable: `models/surgery_gan/seed_*/`, `eval/phase07/surgery_pilot.json`, multi-seed json.

### F.08 — Benchmark 6 phương pháp + RQ1/2/3 **(mới)**
Trên **cùng frozen test + cùng evaluator F.03**: Markov/template · MLE · SeqGAN(số liệu Phase 3/3.5) ·
Gumbel-full(số liệu Phase 3.5) · **Gumbel-masked-surgery(F.07)** · D-rerank(F.06). Report Composite
Score + sub-metrics + bootstrap CI; trả lời RQ1/2/3. Deliverable: `eval/phase08/benchmark.json` + frontier PNG.

### F.09 — Final evaluation & kết luận
Kết luận đúng một trong ba (pre-committed):
```text
(a) MLE-first thắng → masked-surgery là negative/limited result có kiểm soát + D-rerank là ứng dụng GAN.
(b) Masked-surgery thắng anchor-only & MLE qua gate mới → đóng góp GAN trung tâm dương.
(c) Inconclusive → GAN future work, ghi rõ điều kiện.
```
Deliverable: `eval/final/*`, `reports/09_final_evaluation_report.md`.

### F.10 — Literature mapping *(tái dùng)*
Dùng `Guiding/Mục lục/10` (corpus `Asset/Total_OCR`, `Total_Summary`): mỗi paper gắn verdict
`already_tested_failed` / `supports_current_path` / `new_GAN_hypothesis_candidate`. Đặc biệt khai thác
`Fedus_2018_MaskGAN`, `Jang_2017_Gumbel_Softmax`, `Nie_2019_RelGAN`, `Lu_2022_GAN_SQLi`, `Le_2024_GSQLi`
cho phần masked-surgery.

---

## G. Gate pre-registered + chống tự lừa

```text
GATE CHÍNH (khóa trước khi train):
  G1  anchor+adversarial PHẢI thắng anchor-only trên evaluator F.03 → mới claim GAN tạo giá trị.
  G2  Validity_exec(masked) ≥ MLE×0.95  VÀ  diversity ≥ MLE  → mới tính "phá tradeoff".
  G3  no-collapse: ≥4/5 seed unique không sụp.
  G4  paired-D shortcut diagnostic: D không phân biệt được khi slot fill giống nhau (cùng khung) → đạt.
  G5  CI theo seed; tie MLE↔GAN → chọn MLE.

KHÔNG chấp nhận:
  - GAN thắng 1 seed → mở full.
  - proxy (Composite) tăng nhưng Validity_exec/diversity verified giảm.
  - dùng metric keyword cũ.
  - cherry-pick checkpoint/seed.
  - coi unknown/tier4 là benign verified.
```

---

## H. Tài nguyên 6GB, timeline, cây deliverable

**6GB:** model nhỏ, batch 32–64, không MC rollout, không GP, Gumbel chỉ trên slot, freeze gating. Pilot
1 seed trước khi multi-seed. Theo dõi VRAM < 6GB ở smoke test.

**Timeline ước lượng (tương đối):**
```text
F.03 evaluator + F.04 surgery data ........ phần nặng nhất (tiểu dự án)
F.05 MLE baseline ......................... tái dùng, nhanh
F.06 D-scorer ............................. rẻ, chắc có deliverable
F.07 pilot 1 seed → multi-seed ............ ~vài giờ/đợt như Phase 3.5
F.08 benchmark + F.09 final ............... sau khi pilot qua gate
```

**Cây deliverable:**
```text
Guiding_Gumbel-Softmax/
  Mục lục.md
  00_Ke_Hoach_Tong_The.md            ← file này
data/phase04/surgery_{train,dev,frozen_test}.parquet (+ .md5)
data/phase05/{labeled,verified_dev,verified_test}.parquet
models/{mle_generator, d_scorer, surgery_gan/seed_*}/
eval/{phase03,phase05,phase06,phase07,phase08,final}/*.json + *.png
reports/{03_evaluator, 04_surgery_data, 09_final_evaluation}_report.md
```

---

> **Kết luận khung:** Nhánh này đặt GAN làm trung tâm theo cách **trung thực và sống sót mọi kết cục** —
> Gumbel-trên-masked-slot + paired D + evaluator thực thi, đo trong một benchmark SDSG đa phương pháp,
> trên nền V5 đã có. Không lặp lại WGAN-GP/full-sequence đã fail; để dữ liệu, ablation và evaluator quyết
> định, đúng kỷ luật `Guiding/Mục lục`.
