# Timeline Update — 2026-05-16

> **Phiên bản**: V4 Anti-Collapse + Data Curator
> **Ngày**: 2026-05-16 (chốt sau buổi meeting thầy Lâm 13/05)
> **Trạng thái**: Phát hiện root cause + đã build prototype skill mới
> **Người báo cáo**: User (sinh viên)

---

## 1. NHẬN XÉT CỦA THẦY (Buổi gặp 13/05/2026)

Nguồn: `Dashboard/1. Capture/Sandbox/Thầy lâm 2_Max.md` (transcript 765 giây, tiếng Việt)

### 1.1. Phản hồi chính (6 điểm)

| # | Nhận xét nguyên văn (paraphrased) | Mức độ nghiêm túc |
|---|----------------------------------|------------------|
| 1 | "Sơ đồ này chưa có bất kỳ cái mối quan hệ nào — 3 khối phải có kết nối với nhau" | **Critical** |
| 2 | "5 điểm WAF đấy em dùng làm gì? Reward đó dùng ở đâu? Em không trả lời được" | **Critical** |
| 3 | "Hiện tại em vẫn bị collap, vì nó đang trở về 1" | **Critical** |
| 4 | "Có thể em thay LSTM bằng 3LSTM, BBI" (BiLSTM) | Gợi ý kỹ thuật |
| 5 | "Em phải huấn luyện cả dữ liệu CNB ở trong này lẫn với dữ liệu gốc" (benign + attack) | Gợi ý kỹ thuật |
| 6 | "Em dùng Wasserstein GAN Gradient Penalty đúng không?" | Đồng ý hướng |

### 1.2. Câu hỏi thầy mà sinh viên không trả lời được

> "Thầy là tường lửa. Thầy cho em 5 điểm. 5 điểm đấy em dùng phần gì?
>  Thầy cho em 0 điểm, thầy cho em 10 điểm, và cái điểm đấy em dùng làm gì?"

→ Sinh viên ấp úng. Đây là **lỗ hổng kiến thức lớn**: chưa giải thích được luồng reward WAF.

### 1.3. So sánh baseline

Thầy chỉ yêu cầu so sánh với:
- **CTGAN** (Conditional Tabular GAN)
- **WGAN-GP** (Wasserstein GAN + Gradient Penalty)

Không cần so VAE-GAN hay Gumbel-Softmax (mặc dù sinh viên hỏi).

### 1.4. Deadline & cam kết

- Thầy hỏi: "Tháng mấy được bảo vệ nhỉ?"
- Sinh viên: "Tháng 5/2026, cố gắng sớm hơn"
- Cam kết: **Lộ trình tháng 5/2026 chạy hết thí nghiệm**
- Buổi gặp tiếp theo: chiều 2 giờ tuần sau (~20/05/2026)

---

## 2. PHÁT HIỆN MỚI — Root cause Mode Collapse

Trong quá trình investigate sau buổi gặp thầy, phát hiện ra **collapse KHÔNG do training dynamics** mà do **DATASET disaster**:

### 2.1. Function name preservation = 0% (bằng chứng)

Khi delex V1 (đang dùng cho V3), 100% các function name SQLi đặc trưng bị xóa:

```
xmltype       5,793 → 0   (100% mất - Oracle error)
pg_sleep        225 → 0   (100% mất - PostgreSQL time)
extractvalue    250 → 0   (100% mất - MySQL error)
updatexml       107 → 0   (100% mất - MySQL error)
dbms_pipe       212 → 0   (100% mất - Oracle time)
randomblob      190 → 0   (100% mất - SQLite time)
elt           1,045 → 0   (100% mất - MySQL boolean)
```

→ G nhìn vào data không phân biệt được Oracle XMLTYPE với MySQL extractvalue → buộc phải collapse.

### 2.2. Statistics khác

- **Delex collision: 71.89%** — 17,821 unique payload chỉ thành 5,009 delex unique
- **Wrapper bias: 53.64%** — payload bị bọc bởi `select * from users WHERE username = "..."` → toàn bộ inner payload bị nuốt trong `__STR__`
- **Top-100 patterns chiếm 42.82% data** — quá tập trung
- **Reasoning quality: 40% < 20 chars** — labeler dùng pattern match cứng (top 5 reasoning lặp 800-2066 lần)
- **Type×DB holes**: error_based+sqlite=0, auth_bypass+mssql=0, union+sqlite=0

### 2.3. Số "88.6% Oracle XMLTYPE" trước đó là SAI

Số đúng:
- error_based + oracle + xmltype = **32.34%** (không phải 88.6%)
- error_based toàn bộ = 41% attack
- oracle toàn bộ = 43.5% attack

---

## 3. ĐỊNH HƯỚNG XỬ LÝ (2 hướng song song)

### Hướng A — V4 Anti-Collapse Training (đáp ứng thầy)

8 fixes anti-collapse, đáp ứng tất cả 6 nhận xét thầy:

| Fix | Đáp ứng nhận xét # | Trạng thái |
|-----|-------------------|-----------|
| 1. entropy_coeff 0.03 → 0.10 | (anti-collapse) | ✅ Code xong |
| 2. temperature 1.0 → 1.30 | (anti-collapse) | ✅ Code xong |
| 3. EMA alpha 0.05 → 0.20 | (anti-collapse) | ✅ Code xong |
| 4. Type-balanced batch (14 types) | (anti-collapse) | ✅ Code xong |
| 5. Diversity bonus (Jaccard) | (anti-collapse) | ✅ Code xong |
| 6. Dynamic D steps | (anti-collapse) | ✅ Code xong |
| 7. **Benign SQL trong Discriminator** | **#5 thầy yêu cầu** | ✅ Code xong + generator script |
| 8. **GeneratorBiLSTMEncoder** | **#4 thầy gợi ý** | ✅ Code xong |
| (kèm sơ đồ G-D-WAF rõ ràng) | **#1 thầy yêu cầu** | ✅ Trong SKILL.md |
| (kèm reward formula chi tiết) | **#2 thầy yêu cầu** | ✅ Trong SKILL.md |

**Files**:
- `SeqGAN_SQLi/configs/seqgan_v4.yaml`
- `SeqGAN_SQLi/train_adversarial_v4.py` (~600 dòng)
- `SeqGAN_SQLi/src/generator.py` (+130 dòng cho GeneratorBiLSTMEncoder)
- `SeqGAN_SQLi/data/generate_benign_sql.py`

### Hướng B — Skill `sqli-data-curator` (chữa root cause)

Skill mới thay 3 skills cũ (`sqli-labeler`, `sqli-label-validator`, `sqli-label-critic`).

**4-phase workflow**:
- **Phase 1 TRIAGE**: Critique labels → Keep/Relabel/Drop
- **Phase 2 RELABEL**: 3-source validation (rule + Claude Haiku/Chat + heuristic)
- **Phase 3 TRANSFORM**: Strip wrapper + delex_v2 với function whitelist
- **Phase 4 TIER**: Gold/Silver/Bronze split (chưa code)

**Files**:
```
Skill/sqli-data-curator/
├── SKILL.md
├── references/{taxonomy,function_whitelist,wrapper_patterns}.md
└── scripts/{delex_v2,strip_wrapper,label_payload,critique_labels,run_prototype}.py
```

---

## 4. KẾT QUẢ PROTOTYPE (1000 rows test, đã chạy 16/05)

| Metric | Trước (V1 delex) | Sau (Curator) | Mục tiêu | Status |
|--------|------------------|---------------|----------|--------|
| Collision rate | 71.89% | **4.33%** | < 30% | ✅ PASS (cải thiện 16x) |
| Vocab size | 89 tokens | **147 tokens** | 100-180 | ✅ PASS |
| Top-100 coverage | 42.82% | **23.16%** | < 25% | ✅ PASS |
| xmltype preservation | 0% | **100%** | > 95% | ✅ PASS |
| pg_sleep preservation | 0% | **100%** | > 95% | ✅ PASS |
| extractvalue preservation | 0% | **100%** | > 95% | ✅ PASS |
| Critique triage | n/a | KEEP 45.6%, RELABEL 53.3%, DROP 1.1% | Phân bố hợp lý | ✅ |

---

## 5. CÁC QUYẾT ĐỊNH USER ĐÃ CHỐT (16/05)

| Quyết định | Lý do |
|------------|-------|
| Skill cấu trúc: **1 skill** `sqli-data-curator` thay 3 cũ | Overlap workflow lớn, gộp dễ maintain |
| LLM source B: **Claude Code subagent** (không dùng API) | Tiết kiệm $20 + không cần API key |
| Long-tail types: **DROP 134 rows** (ldap/rce/comment/inline/...) | Out of scope SQLi, không augment |
| Phase 2 chat mode: **subagent song song**, chat toàn bộ RELABEL | Không trust shortcut A+C, chất lượng cao |
| Bắt đầu: **prototype 1000 rows** trước full pipeline | Verify trước khi đầu tư |

---

## 6. ROADMAP TUẦN 16-20/05

### Tuần này (16/05 - 20/05)

**Mục tiêu**: Có dataset sạch + V4 chạy thử + slide báo cáo thầy

| Ngày | Việc | Output |
|------|------|--------|
| 16/05 (T6) | ✅ Prototype curator 1000 rows | `prototype_v3.csv` (đã có) |
| 17/05 (T7) | Build Phase 2 chat-mode coordinator + merge | `chat_label_coordinator.py`, `merge_chunks.py` |
| 18/05 (CN) | Build Phase 4 (tier_split, resample) | `tier_split.py`, `resample_balanced.py` |
| 18/05 đêm | Chạy full pipeline trên 40,860 rows | `dataset_v3.csv` |
| 19/05 (T2) | Re-pretrain MLE trên gold.csv + V4 smoke test | `mle_v4_best.pt`, smoke logs |
| 19/05 (T2) | V4 full training (warmup + 5000 adv steps) | `adv_v4_step5000.pt` |
| 20/05 (T3) | Evaluate V4 + chuẩn bị slide | `eval_report_v4.json`, slide.pptx |
| 20/05 chiều | **Họp thầy 2 giờ** | Báo cáo + nhận feedback mới |

### Mục tiêu định lượng V4 (so V3)

| Metric | V3 step2000 (best) | V4 target step3000 |
|--------|-------------------|-------------------|
| Self-BLEU-3 | 0.9894 (critical) | < 0.80 |
| Unique payloads/64 batch | 6-7 | > 40 |
| Type entropy (bits) | ~0.3 | > 2.0 |
| Relex uniqueness | 1.000 (warmup) | > 0.80 (adv) |
| Composite score | 0.471 | > 0.55 |

---

## 7. NHỮNG GÌ CHƯA CODE (open work)

1. ❌ `chat_label_coordinator.py` — orchestrate subagents
2. ❌ `merge_chunks.py` — merge subagent outputs
3. ❌ `tier_split.py` — Gold/Silver/Bronze
4. ❌ `resample_balanced.py` — cap mỗi signature ≤ 30 rows
5. ❌ `augment_synthetic.py` — fill Type×DB holes (optional)
6. ❌ MLE pretrain V4 trên dataset_v3
7. ❌ V4 smoke test
8. ❌ Docker ModSecurity setup (để dùng real WAF)
9. ❌ Slide báo cáo cho thầy

---

## 8. RỦI RO CẦN ĐỀ PHÒNG

| Rủi ro | Xác suất | Tác động | Mitigation |
|--------|----------|----------|------------|
| V4 vẫn collapse sau khi sửa data | Medium | High | Tăng entropy_coeff lên 0.15, hoặc thêm MC rollout |
| Subagent labeling chậm hơn dự kiến | Medium | Medium | Giảm chunk_size, tăng parallel |
| Subagent label không nhất quán | Low | Medium | Template prompt cố định, đọc SKILL.md trước |
| Real WAF Docker setup phức tạp | Medium | Low | Dùng dev_proxy cho V4 demo, real WAF chỉ cho final eval |
| Thầy yêu cầu thêm experiment chưa làm | High | Medium | Plan slot dự phòng 1-2 ngày, focus core results |
| MLE val_ppl cao hơn V3 trên data mới | High | Low | Bình thường (data đa dạng hơn) — không phải bug |

---

## 9. TÀI LIỆU LIÊN QUAN

| File | Mô tả |
|------|-------|
| `RECOVERY.md` | **Tái lập tiến trình khi mở session mới** |
| `Dashboard/1. Capture/Sandbox/Thầy lâm 2_Max.md` | Transcript buổi gặp thầy 13/05 |
| `IMPROVEMENTS_SUMMARY.md` | Lịch sử V1 → V3 |
| `V2_POSTMORTEM_AND_V3_PLAN.md` | Phân tích V2 fail + V3 plan |
| `V3_RESULTS.md` | Kết quả V3 (collapse) |
| `WAF_EVAL_RESULTS.md` | WAF eval V3 |
| `Skill/sqli-data-curator/SKILL.md` | Workflow skill mới |
| `~/.claude/plans/ultrathink-c-users-admin-documents-dashb-wiggly-fiddle.md` | Plan file hiện tại (Phase 2 chat mode) |

---

## 10. MEMO CUỐI

> "V4 + curator skill là 2 chân cùng song hành. V4 fix training dynamics, curator fix data.
>  Nhưng curator quan trọng hơn — nếu data vẫn collapse 71.89% sau delex, V4 cũng vô dụng.
>  Làm curator trước, V4 sau."
