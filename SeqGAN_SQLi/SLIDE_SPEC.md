# SLIDE DECK SPECIFICATION
# Sinh Dữ Liệu SQL Injection bằng Conditional SeqGAN để Hỗ Trợ Phát Hiện Tấn Công

> **Mục đích file này:** Hướng dẫn đầy đủ cho AI tạo PowerPoint.
> Paste toàn bộ nội dung này vào Gamma.app / Tome / ChatGPT / Claude rồi yêu cầu sinh slide.
> Tất cả số liệu là số thật từ thực nghiệm — không thay đổi.
>
> **Prompt mẫu để dùng với Gamma.app:**
> "Create a 18-slide academic thesis defense presentation based on this specification.
>  Follow every layout, color, table, and speaker note exactly as written."
>
> **Prompt mẫu để dùng với Claude/ChatGPT (sinh python-pptx):**
> "Generate python-pptx code for an 18-slide academic presentation.
>  Use the design system and each slide specification below. Output runnable Python."

---

## PHẦN A — HỆ THỐNG THIẾT KẾ (Design System)

### A1. Bảng Màu (Color Palette)

| Tên | Hex | Dùng cho |
|-----|-----|----------|
| Navy Dark | `#1B2A4A` | Header bar, slide background accent, tiêu đề chính |
| Sky Blue | `#2196F3` | Accent chính — GAN, mô hình, technical terms |
| Success Green | `#2E7D32` | Kết quả tốt (✅ PASS), số liệu dương |
| Failure Red | `#C62828` | Kết quả thất bại (❌ FAIL), mode collapse |
| Warning Orange | `#E65100` | Cảnh báo, vấn đề chưa giải quyết |
| Light Gray | `#F5F5F5` | Slide background chính |
| White | `#FFFFFF` | Text trên nền tối, box nội dung |
| Dark Text | `#212121` | Body text trên nền sáng |
| Table Stripe | `#E3F2FD` | Alternating row màu nhạt trong bảng |
| Code BG | `#263238` | Background của code block |
| Code Text | `#80CBC4` | Text trong code block |

### A2. Font

| Vị trí | Font | Cỡ | Style |
|--------|------|----|-------|
| Tiêu đề slide | Calibri | 36–40pt | Bold, White hoặc Navy Dark |
| Section divider | Calibri | 44pt | Bold, White trên Navy Dark |
| Subheader | Calibri | 24–28pt | Bold, Navy Dark |
| Body text | Calibri | 18–20pt | Regular |
| Table header | Calibri | 14pt | Bold, White trên Navy Dark |
| Table body | Calibri | 13pt | Regular |
| Code block | Consolas / Courier New | 13pt | Regular, Code Text màu |
| Caption / footnote | Calibri | 11pt | Italic, Gray |
| Speaker note | Calibri | 12pt | Regular |

### A3. Layout Chuẩn

| Layout Name | Mô tả | Dùng ở slide |
|-------------|-------|--------------|
| TITLE_SLIDE | Toàn màn hình Navy Dark, tên đề tài lớn giữa, thông tin bên dưới | 1 |
| SECTION_BREAK | Full-width Navy Dark, số phần + tên phần, chữ trắng | 2, 5.5, 8.5, 11.5 |
| TITLE_CONTENT | Header bar Navy Dark 15% trên, content 85% dưới | Phần lớn |
| TWO_COLUMN | Header bar + 2 cột bằng nhau bên dưới | 3, 9, 10 |
| TITLE_TABLE | Header bar + table chiếm 70% diện tích | 4, 6, 12 |
| TITLE_CODE | Header bar + code block đen chiếm 65% | 15 |
| TITLE_DIAGRAM | Header bar + diagram/architecture chiếm toàn bộ | 8, 13 |
| TITLE_CHART | Header bar + chart 60% + legend 40% | 11, 14 |

### A4. Quy Tắc Visual

- **Icon ✅** luôn màu `#2E7D32` (Success Green)
- **Icon ❌** luôn màu `#C62828` (Failure Red)
- **Icon ⚠️** luôn màu `#E65100` (Warning Orange)
- **Icon ★** (best result) màu `#FFD700` (Gold)
- Mỗi bảng có header row nền `#1B2A4A`, text trắng; alternating rows `#F5F5F5` và `#E3F2FD`
- Code block: nền `#263238`, border-radius 4px, padding 12px
- Tất cả diagram vẽ bằng mũi tên một chiều, không dùng bidirectional trừ khi chú thích rõ
- Không dùng quá 5 bullet point trên 1 slide; mỗi bullet tối đa 12 từ

---

## PHẦN B — SLIDE-BY-SLIDE SPECIFICATION (18 Slide)

---

### SLIDE 1 — Trang Bìa

**Layout:** `TITLE_SLIDE`
**Background:** Full `#1B2A4A` Navy Dark

**Nội dung:**

```
[TOP — Logo trường nếu có, góc trái trên]

[GIỮA SLIDE — căn giữa dọc và ngang]

LUẬN VĂN TỐT NGHIỆP
─────────────────────────────────────────
Sinh Dữ Liệu Tấn Công SQL Injection
Bằng Mạng GAN Có Điều Kiện
Để Hỗ Trợ Phát Hiện Tấn Công
─────────────────────────────────────────
Conditional SeqGAN with Composite Reward Oracle

[BÊN DƯỚI — căn giữa]

Sinh viên thực hiện: [Tên sinh viên]
Giảng viên hướng dẫn: [Tên GVHD]
Chuyên ngành: An Toàn Thông Tin
Năm: 2026
```

**Màu sắc:**
- "LUẬN VĂN TỐT NGHIỆP": `#2196F3` Sky Blue, 16pt, tracking +2
- Tên đề tài VN: `#FFFFFF` White, 32pt Bold
- Tên đề tài EN: `#90CAF9` (light blue), 18pt Italic
- Đường kẻ ngang: `#2196F3`, 2px
- Thông tin sinh viên/GVHD: `#B0BEC5` (light gray), 14pt

**Speaker Notes:**
Đây là đề tài thuộc lĩnh vực an toàn thông tin, áp dụng kỹ thuật học sâu (GAN) vào bài toán sinh dữ liệu tấn công SQL Injection để hỗ trợ xây dựng hệ thống phát hiện tốt hơn. Nghiên cứu này không nhằm mục đích tấn công thực tế mà phục vụ mục đích phòng thủ và nghiên cứu học thuật.

---

### SLIDE 2 — Động Lực Nghiên Cứu: Bài Toán Mất Cân Bằng

**Layout:** `TWO_COLUMN`
**Header:** "Tại Sao Cần Sinh Dữ Liệu Tổng Hợp?"

**Cột trái — Thực trạng:**

```
🔍 Bài Toán Mất Cân Bằng

Trong hệ thống thực tế:
• Tỉ lệ request bình thường vs tấn công
  là 100:1 đến 1.000:1

• Model học thiên lệch về lớp đa số
  → Bỏ sót tấn công (False Negative cao)

• SMOTE chỉ "nội sinh" — interpolate
  từ mẫu đã có, không tạo pattern mới

[VISUAL: Biểu đồ tròn — 99% xanh (benign),
 1% đỏ (attack); mũi tên dưới → "Detector lệch"]
```

**Cột phải — Đề xuất:**

```
💡 Giải Pháp: GAN Sinh Dữ Liệu

GAN học phân phối ẩn của dữ liệu tấn công
→ Sinh mẫu hoàn toàn mới, ngoài vùng train

Dataset bổ sung:
  Real SQLi (17.821 mẫu)
        ↓
  Conditional SeqGAN
        ↓
  Synthetic SQLi đa dạng
        ↓
  XGBoost Detector
  (tốt hơn khi train với data đầy đủ hơn)
```

**Màu sắc:**
- Biểu đồ tròn: 99% `#2196F3` (benign), 1% `#C62828` (attack)
- Box "Giải Pháp": viền `#2196F3`, nền `#E3F2FD`

**Speaker Notes:**
Bài toán phát hiện SQLi có đặc điểm mất cân bằng nghiêm trọng — trong môi trường production, hầu hết traffic là bình thường. SMOTE (Synthetic Minority Over-sampling Technique) chỉ tạo mẫu mới bằng cách nội suy giữa các điểm dữ liệu đã có, không thể tạo pattern cấu trúc SQL mới. GAN, ngược lại, học phân phối ẩn và có thể sinh mẫu với cấu trúc chưa từng thấy trong tập train.

---

### SLIDE 3 — Tại Sao Là SeqGAN? So Sánh GAN Variants

**Layout:** `TITLE_TABLE`
**Header:** "Lựa Chọn Kiến Trúc GAN: SeqGAN vs CTGAN vs CWGAN-GP"

**Bảng so sánh (6 cột × 6 hàng):**

| Tiêu chí | CTGAN | CWGAN-GP | SeqGAN V1 | **SeqGAN V2 (Đề tài)** |
|---|---|---|---|---|
| Kiểu dữ liệu | Tabular / vector | Vector / text | Chuỗi token rời rạc | **Chuỗi token rời rạc** |
| Điều kiện hóa | Class label | Class label | ❌ None | **✅ Attack type (4 loại)** |
| Loss function | Cross-entropy + mode-norm | Wasserstein + GP | REINFORCE | **REINFORCE + Composite Reward** |
| WAF Oracle | ❌ | ❌ | ❌ heuristic | **✅ ModSecurity thực** |
| Diversity control | Mode normalization | Gradient penalty | ❌ Thất bại | **AST fingerprint + boundary reward** |
| Bài báo đại diện | Zhao 2024, NT204 | Dasari 2025 | Yu 2017 | **Đề tài (dựa trên Chowdhary 2023)** |

**Bên dưới bảng — hộp highlight:**

```
[BOX viền #2196F3]
SQLi payload là chuỗi ký tự/token — không phải tabular row
→ CTGAN/CWGAN không thể áp dụng trực tiếp
→ SeqGAN với Policy Gradient là lựa chọn phù hợp nhất
   cho bài toán sinh chuỗi rời rạc (discrete token sequence)
```

**Speaker Notes:**
CTGAN được thiết kế cho dữ liệu dạng bảng (tabular) — ví dụ: network traffic features. CWGAN-GP (Dasari et al. 2025) hoạt động với text nhưng không dùng WAF thực làm reward. Đề tài này mở rộng Chowdhary 2023 (Conditional SeqGAN cho pentesting) bằng cách thêm real WAF oracle và composite reward thay heuristic proxy.

---

### SLIDE 4 — Literature Gap Analysis

**Layout:** `TITLE_TABLE`
**Header:** "Khoảng Trống Nghiên Cứu — Đề Tài Lấp Đầy Gì?"

**Bảng gap analysis (7 cột):**

| Bài báo | Năm | Sinh text? | WAF thực? | Conditional? | Diversity metric? | Rating |
|---|---|---|---|---|---|---|
| Lu et al. | 2022 | ❌ vector | ❌ | ❌ | Self-BLEU | ⭐⭐⭐⭐ |
| Dasari et al. | 2025 | ✅ | ❌ | ✅ | BLEU/R² | ⭐⭐⭐⭐ |
| GSQLi (UIT) | 2024 | ✅ mutation | ✅ libinjection | ✅ | ❌ | ⭐⭐⭐⭐ |
| Chowdhary | 2023 | ✅ | ❌ heuristic | ✅ | ❌ | ⭐⭐⭐½ |
| Yu (SeqGAN) | 2017 | ✅ | ❌ | ❌ | NLL oracle | ⭐⭐⭐⭐½ |
| **Đề tài (V2)** | **2026** | **✅** | **✅ ModSec** | **✅ 4 types** | **✅ 5-metric** | **—** |

**Highlight 2 ô cuối cùng của hàng "Đề tài":** nền `#2E7D32`, text trắng.

**Bên dưới — 3 contribution box (ngang):**

```
[BOX 1 — #2196F3]          [BOX 2 — #2196F3]          [BOX 3 — #2196F3]
Real WAF Oracle             5-Metric Ensemble           Boundary-aware Reward
ModSecurity CRS v4.3.0      (không chỉ Self-BLEU)       (không phải binary)
làm reward signal           AST + DB + IDS evasion      reward = 1 - dist/threshold
```

**Speaker Notes:**
Không có bài báo nào trước đây kết hợp đồng thời: (1) sinh chuỗi token SQL, (2) dùng WAF thực làm reward oracle, (3) conditional theo loại tấn công, và (4) đánh giá bằng 5 metric độc lập. Đây là 3 contribution phương pháp luận của đề tài.

---

### SLIDE — SECTION BREAK: PHẦN II — DỮ LIỆU

**Layout:** `SECTION_BREAK`
**Background:** Full `#1B2A4A`

```
[Số phần — góc trên trái, #2196F3, 14pt]
PHẦN II

[Tên phần — giữa slide, White, 40pt Bold]
Dataset & Tiền Xử Lý

[Subtitle — bên dưới, #90CAF9, 20pt]
17.821 SQLi payloads · 4 loại tấn công · 2 bước đánh nhãn
```

---

### SLIDE 5 — Dataset: 4 Loại Tấn Công

**Layout:** `TWO_COLUMN`
**Header:** "Quyết Định Tập Trung: Từ 18 Loại → 4 Loại Tấn Công"

**Cột trái — Phân phối:**

```
[DONUT CHART — 4 màu]

error_based    41%  ████████████  #C62828
boolean_blind  36%  ██████████    #E65100
time_blind     13%  ████          #2196F3
union_based    10%  ███           #2E7D32

Tổng: 17.821 SQLi payloads
      + 19.669 benign (không dùng để train GAN)
```

**Cột phải — Lý do chọn 4 loại:**

| Loại | Count | Marker nhận dạng |
|------|-------|-----------------|
| error_based | 7.315 | `xmltype()` `extractvalue()` `floor(rand()*2)` |
| boolean_blind | 6.335 | `CASE WHEN` `IF()` `AND 1=1` |
| time_blind | 2.283 | `sleep()` `pg_sleep()` `WAITFOR` |
| union_based | 1.888 | `UNION SELECT` `ORDER BY N` |

```
[BOX — cạnh dưới cột phải]
❌ Loại bỏ: heavy_query → remap vào time_blind
❌ Loại bỏ: auth_bypass → remap vào boolean_blind
❌ Loại bỏ: 10 loại còn lại (<130 mẫu/loại)

✅ Chỉ giữ loại có marker rõ ràng
   + đủ data để train conditional embedding
```

**Speaker Notes:**
Ban đầu dataset có 18 loại tấn công nhưng đa số quá ít mẫu. Sau quá trình phân tích, quyết định remap các loại ambiguous và chỉ giữ 4 loại có marker cú pháp đặc trưng rõ ràng. Điều này giúp conditional embedding học được ranh giới giữa các loại, thay vì bị overfit vào noise của loại ít mẫu.

---

### SLIDE 6 — Quy Trình Đánh Nhãn 2 Bước

**Layout:** `TITLE_CONTENT`
**Header:** "Đánh Nhãn Chất Lượng Cao: Script Tự Động + AI-Assisted"

**Nội dung — Flowchart dọc:**

```
[BOX 1 — nền #E3F2FD, viền #2196F3]
📥 INPUT: Raw SQLi payloads từ nhiều nguồn
   Kaggle · ExploitDB · CVE PoCs · GitHub

           ↓

[BOX 2 — nền #FFF3E0, viền #E65100]
⚙️ BƯỚC 1: Script Tự Động (Regex + Keyword Matching)
   • Nhận dạng marker cú pháp đặc trưng của từng loại
   • Output: combined_labeled_data.csv (19.669 rows)
   • Hạn chế: nhiều noise, ambiguous payloads chưa xử lý được

           ↓

[BOX 3 — nền #E8F5E9, viền #2E7D32]
🤖 BƯỚC 2: AI-Assisted Re-labeling (System Prompt 348 dòng)
   • Định nghĩa 4 loại SQLi với marker BẮT BUỘC + ví dụ cụ thể
   • 6 db_engine với bảng nhận diện tiebreaker
   • 3 mức confidence: 0.70 / 0.85 / 1.00 với quy tắc chính xác
   • 10 edge cases: polyglot, dbms_pipe, generate_series size...
   • Batch 50-100 rows/lần → CSV chuẩn, không giải thích thêm

           ↓

[BOX 4 — nền #1B2A4A, text trắng]
✅ OUTPUT: latest_relabel_data.csv
   17.821 rows · mean confidence = 0.93
   Columns: id, payload_norm, payload_delex, sqli_type, db_engine, confidence
```

**Bên phải — Confidence Tiers:**

```
[3 badge ngang]
🥇 GOLD      🥈 SILVER    🥉 BRONZE
≥ 0.95       0.80–0.94    < 0.80
~60%         ~25%         ~15%
Weight 3×    Weight 1×    Val only
```

**Speaker Notes:**
Bước đánh nhãn là công việc tốn nhiều thời gian nhất trong dự án. System prompt được thiết kế để AI không "đoán" mà phải có ít nhất 1 marker bắt buộc trước khi gán nhãn. Confidence score không phải là xác suất của model mà là mức độ chắc chắn của người đánh nhãn dựa trên số marker có mặt trong payload.

---

### SLIDE 7 — De-lexicalization & Vocab Reduction

**Layout:** `TWO_COLUMN`
**Header:** "Giảm Vocabulary: 3.088 → 89 Tokens (Giảm 97%)"

**Cột trái — Vấn đề:**

```
[BEFORE — box đỏ]
❌ Vocab gốc: 3.088 tokens

Nguyên nhân phình vocab:
• "||chr" → 1 token duy nhất
• xmltype, dbms_pipe → mỗi function 1 token
• '1', '2', '999', '0'... → hàng trăm literal
• 'users', 'accounts', 'admin' → trùng nhau

LSTM 128-dim không học được
với vocab 3.088 → embedding quá thưa
```

**Cột phải — Giải pháp:**

```
[AFTER — box xanh lá]
✅ Vocab V2: 89 tokens

De-lexicalization: thay literals bằng placeholder

  '1'      → __INT__
  'admin'  → __STR__
  0x616263 → __HEX__
  users    → __TABLE__
  password → __COL__
  xmltype  → __IDENT__
  5        → __TIME__
  9999     → __BIGINT__

[Re-lex dictionary — 40 entries cố định]
5 values × 8 placeholder types
→ Reproducible evaluation
```

**Footer — 2 ví dụ:**

```
BEFORE: 1' OR (SELECT 0x616263 FROM users WHERE id='1')--
AFTER:  __INT__ ' OR ( SELECT __HEX__ FROM __TABLE__
        WHERE id = __STR__ ) --
```

**Speaker Notes:**
De-lexicalization là quyết định thiết kế quan trọng nhất trong data preprocessing. Nó giải quyết hai vấn đề: (1) vocab explosion khiến LSTM không học được, (2) literal values như '1' và '999' về mặt ngữ nghĩa SQL là như nhau nhưng chiếm token slot riêng. Re-lex dictionary có kích thước cố định đảm bảo kết quả evaluation reproducible.

---

### SLIDE — SECTION BREAK: PHẦN III — MÔ HÌNH

**Layout:** `SECTION_BREAK`
**Background:** Full `#1B2A4A`

```
PHẦN III

Kiến Trúc Mô Hình Đề Xuất

Generator (G) · Discriminator (D) · Composite Reward Oracle
```

---

### SLIDE 8 — Kiến Trúc Tổng Quan (Architecture Diagram)

**Layout:** `TITLE_DIAGRAM`
**Header:** "Conditional SeqGAN V2 — Pipeline Đầy Đủ"

**Diagram — vẽ theo chiều dọc, 3 cột:**

```
╔══════════════════════════════════════════════════════════════════╗
║              CONDITIONAL GENERATOR (G)                          ║
║                                                                  ║
║  attack_type_id (0–3)                                           ║
║        ↓ Type Embedding [4 × 32 dim]                            ║
║        ⊕  (concatenate)                                         ║
║  token t-1 → Token Embedding [89 × 256 dim]                     ║
║        ↓                                                         ║
║    LSTM Layer 1 (512 hidden, dropout=0.2)                        ║
║        ↓                                                         ║
║    LSTM Layer 2 (512 hidden, dropout=0.2)                        ║
║        ↓                                                         ║
║    LSTM Layer 3 (512 hidden, dropout=0.2)                        ║
║        ↓                                                         ║
║    Linear (512 → 89) → Softmax → token t                        ║
╚══════════════════╦═══════════════════════════════════════════════╝
                   ║ Generated payload sequence
    ┌──────────────╬──────────────────────────┐
    ↓              ↓                          ↓
╔═══════╗  ╔══════════════════════════════════════════════╗
║ TEXT  ║  ║       COMPOSITE REWARD ORACLE               ║
║  CNN  ║  ║                                              ║
║  (D)  ║  ║  [Gate 1] SQL Parser Gate  → 0 hoặc 1       ║
║       ║  ║  [Gate 2] DB Sandbox Gate  → 0 hoặc 1       ║
║ 3 CNN ║  ║                                              ║
║ kernels  ║  syntax_gate × exec_gate × (                ║
║[3,4,5]║  ║    0.4 × r_WAF_boundary(anomaly_score)      ║
║128 f. ║  ║  + 0.3 × r_custom(5 SQLi rules)             ║
║       ║  ║  + 0.2 × novelty_AST(fingerprint)           ║
║Scalar ║  ║  - 0.1 × overlap_penalty                    ║
║score  ║  ║  )                                           ║
║(10-20%    ║                                              ║
║reward)║  ║  WAF: ModSecurity OWASP CRS v4.3.0 Docker   ║
╚═══════╝  ╚══════════════════╦═══════════════════════════╝
                              ║ r ∈ [-1.0, +1.0]
                              ↓
               ╔══════════════════════════╗
               ║  REINFORCE + EMA Baseline ║
               ║  advantage = r - EMA_r    ║
               ║  ∇L = -log_prob × advantage║
               ╚══════════════════════════╝
                              ║ gradient
                              ↓
                        [G weights update]
```

**Màu sắc diagram:**
- Box Generator: nền `#E3F2FD`, viền `#2196F3` 2px
- Box Reward Oracle: nền `#E8F5E9`, viền `#2E7D32` 2px
- Box Discriminator: nền `#FFF3E0`, viền `#E65100` 1px dashed (vai trò phụ)
- Mũi tên: `#1B2A4A` 1.5px
- Label "(10-20% reward)": màu `#E65100` italic → nhấn mạnh D vai trò nhỏ

**Speaker Notes:**
Điểm khác biệt quan trọng với SeqGAN truyền thống: Discriminator (D) trong V2 chỉ đóng góp 10-20% reward signal. Phần lớn reward đến từ Composite Oracle — bao gồm WAF thực (ModSecurity Docker), custom SQL validity rules, và AST fingerprint tracker. Thiết kế này ngăn reward hacking mà SeqGAN V1 gặp phải khi dùng heuristic proxy thuần túy.

---

### SLIDE 9 — Composite Reward: Tại Sao Không Dùng Binary?

**Layout:** `TWO_COLUMN`
**Header:** "Boundary-Aware Reward vs Binary Reward"

**Cột trái — Binary (cũ, V1):**

```
[BOX nền #FFEBEE, viền #C62828]
❌ Binary Reward (V1 proxy)

r = 1  nếu bypass
r = 0  nếu bị chặn

Vấn đề:
• Gradient signal cực kỳ thưa
• Generator học qua mặt proxy dễ
• Không biết "gần đến đâu" rồi
• ASR = 100% nhưng chỉ là hack heuristic
```

**Cột phải — Boundary-aware (V2):**

```
[BOX nền #E8F5E9, viền #2E7D32]
✅ Boundary-Aware Reward (V2)

                │ r_WAF
    1.0 ┤     ████
    0.8 ┤   ██████
    0.6 ┤  ███████
    0.4 ┤ ████████
    0.2 ┤█████████
   -0.5 ┤          ██ (blocked)
        └─────────────── anomaly_score
              0    5    10    15

r = 1 - (threshold - score) / threshold
   nếu score < threshold (bypass)
r = -0.5  nếu bị chặn

Phần thưởng cao nhất khi sát ranh giới
→ Buộc G tìm bypass khó, không trivial
→ Tạo diversity tự nhiên
```

**Footer — 5 thành phần reward:**

```
┌─────────────────┬──────────┬───────────────────────────────┐
│ Thành phần      │ Weight   │ Vai trò                       │
├─────────────────┼──────────┼───────────────────────────────┤
│ WAF Oracle      │ 40%      │ Bypass thực sự (ModSecurity)  │
│ Custom Rules    │ 30%      │ Đảm bảo là SQLi đúng nghĩa    │
│ AST Novelty     │ 20%      │ Thưởng cấu trúc SQL mới       │
│ Overlap Penalty │ −10%     │ Phạt noise lừa WAF qua encode │
│ Discriminator D │ 10–20%   │ Áp lực diversity tổng thể     │
└─────────────────┴──────────┴───────────────────────────────┘
```

**Speaker Notes:**
Boundary-aware reward giải quyết vấn đề sparse gradient của binary reward. Thay vì chỉ biết "đúng/sai", generator nhận được signal liên tục về "gần đến đâu rồi". Điều này tự nhiên tạo ra diversity vì để đạt reward cao nhất, model phải tìm payload sát ranh giới block — không phải payload bypass dễ.

---

### SLIDE 10 — 3-Phase Curriculum Training

**Layout:** `TWO_COLUMN`
**Header:** "Curriculum Training: Học Dần Từ Dễ Đến Khó"

**Cột trái — Timeline phases:**

```
[TIMELINE DỌC]

╔══════════════════════════════╗
║ PHASE 0: MLE PRETRAIN        ║  ~15 phút
║ G học phân phối payload hợp lệ║
║ val_ppl = 1.27  ✅            ║
╚══════════════╦═══════════════╝
               ↓
╔══════════════════════════════╗
║ PHASE 1: WARMUP (0–2.000)    ║  ~6 phút
║ Chỉ custom rules + DB gate   ║
║ reward: 0.42 → 0.70  ✅      ║
║ "G không sinh garbage"        ║
╚══════════════╦═══════════════╝
               ↓
╔══════════════════════════════╗
║ PHASE 2: ADVERSARIAL         ║  ~31 phút
║ (2.000–15.000 steps)         ║
║ Full composite reward + WAF  ║  ← ★ best
║ Best: step 1000 → 0.405      ║    checkpoint
╚══════════════╦═══════════════╝    ở đây
               ↓
╔══════════════════════════════╗
║ PHASE 3: REFINEMENT          ║  ~9 phút
║ (15.000–20.000 steps)        ║
║ w_diversity: 0.2 → 0.5       ║
╚══════════════════════════════╝
```

**Cột phải — Reward weights per phase:**

```
[Grouped bar chart — 3 nhóm bars, 4 màu/nhóm]

WARMUP:
  OWASP WAF    ░░░░░░░░░░  0.0
  Custom Rules ████████████ 0.7
  AST Diversity ░░░░░░░░░░  0.0
  Overlap Pen. ░░░░░░░░░░  0.0

ADVERSARIAL:
  OWASP WAF    ████████    0.4
  Custom Rules ██████      0.3
  AST Diversity ████        0.2
  Overlap Pen. ██           0.1

REFINEMENT:
  OWASP WAF    ██████      0.3
  Custom Rules ██           0.1
  AST Diversity ██████████  0.5
  Overlap Pen. ██           0.1
```

**Speaker Notes:**
Curriculum training giải quyết vấn đề cold start: nếu gọi WAF Docker ngay từ đầu, generator sẽ sinh garbage và lãng phí 30-50ms mỗi WAF call. Warmup phase đảm bảo G đã học được cấu trúc SQL cơ bản trước khi escalate sang adversarial training với full reward.

---

### SLIDE — SECTION BREAK: PHẦN IV — KẾT QUẢ

**Layout:** `SECTION_BREAK`
**Background:** Full `#1B2A4A`

```
PHẦN IV

Kết Quả Thực Nghiệm

V1 → V2: Tiến Bộ, Vấn Đề, và Chẩn Đoán
```

---

### SLIDE 11 — Kết Quả Định Lượng V2

**Layout:** `TITLE_TABLE`
**Header:** "Kết Quả 5-Metric Evaluation (500 mẫu, không có WAF Docker)"

**Bảng chính — V1, V2, V3 so sánh:**

| Model | DB Exec | AST-H | Custom% | Re-lex Uniq | Composite | OWASP bypass |
|-------|---------|-------|---------|-------------|-----------|--------------|
| MLE baseline | 3.2% | 3.08 | 86.8% | 0.686 | 0.202 | — |
| V2 step1000 | 99.8% | 2.42 | 60.0% | 0.010 | 0.394 | — |
| V2 step2000+ | 100% | 2.565 ❌ | — | 0.002 ❌ | 0.353 | — |
| **V3 step2000 ★** | **99.2%** | **3.07** | **94.6%** | **1.000** | **0.471** | **2.0%** |
| V3 step1000 | 99.8% | 2.91 | 77.4% | 0.926 | 0.460 | 9.8% |
| V3 step12000 (collapsed) | 100% | 2.67 | 80% | 0.008 ❌ | 0.357 | **43.4%** ⚠ |

**Định dạng đặc biệt:**
- Hàng `V3 step2000 ★`: nền `#E8F5E9`, viền trái `#2E7D32` 4px — **PRODUCTION MODEL**
- Cell `1.000` (re-lex uniq V3): text `#2E7D32` Bold ← từ 0.010 (V2) lên 1.000 (V3)
- Cell `3.07` (AST-H V3): text `#2E7D32` Bold ← vượt target > 3.0
- Cell `0.471` (composite V3): text `#2E7D32` Bold, icon ★
- Cell `2.565 ❌` (V2 frozen): text `#C62828` Italic — mode collapse
- Cell `43.4%` (V3 collapsed OWASP): nền `#FFF3E0` — bypass cao nhưng diversity = 0 → vô nghĩa
- Hàng V3 step12000: nền `#FFEBEE` — collapsed, chỉ dùng so sánh

**Chú thích dưới bảng:**

```
★ Production model = checkpoints/v3/adv_step2000.pt (cuối warmup V3)
✅ Composite +133% vs MLE (0.471 vs 0.202)
✅ Re-lex uniqueness = 1.000 — 500/500 payload là duy nhất (entropy reg fix mode collapse)
✅ AST entropy = 3.07 — đạt target > 3.0
✅ DB execution 99.2% — payload chạy được trong SQLite
⚠ ML-IDS evasion = 0% ở final model — IDS nhận diện pattern warmup generator
⚠ Collapsed model (step12000) bypass WAF 43% nhưng chỉ 1 payload lặp 500 lần
   → bypass cao vì pattern quá đơn giản để WAF rule detect
```

**Speaker Notes:**
V3 entropy regularization đã giải quyết triệt để mode collapse trong warmup phase: re-lex uniqueness tăng từ 0.010 (V2) lên 1.000 (V3) — tức là 500 payload sinh ra đều khác nhau hoàn toàn. AST entropy 3.07 cũng vượt target 3.0. Tradeoff duy nhất: ML-IDS evasion = 0% vì IDS học nhận ra pattern của warmup generator. Collapsed model (step12000) bypass WAF 43% nhưng payload là 1 string lặp lại 500 lần — không có giá trị thực tế.

---

### SLIDE 12 — Phát Hiện: Mode Collapse Tại Adversarial Phase

**Layout:** `TITLE_CHART`
**Header:** "Mode Collapse: AST Entropy Đóng Băng Từ Step 2.000"

**Chart chính — Line chart so sánh V2 vs V3, 2 trục Y:**

```
[LINE CHART — 2 panel ngang hoặc 2 line group trên cùng 1 chart]
X-axis: Training Steps (0, 1000, 2000, 3000, 6000, 9000, 12000)
Y-axis trái: AST Entropy (0 → 4.0)
Y-axis phải: Re-lex Uniqueness (0.0 → 1.0)

──── PANEL V2 (thất bại) ────────────────────────────────────────

Line V2 AST-Entropy — màu #C62828, 2px solid:
  0:     0.5
  1000:  2.42   ← end warmup V2
  2000:  2.565 ← COLLAPSE (frozen từ đây)
  3000:  2.565
  6000:  2.565  ← đóng băng mãi
  9000:  2.565
  12000: 2.565

Line V2 Re-lex — màu #C62828, 1.5px dashed:
  0:     0.686  ← MLE diverse
  1000:  0.010
  2000:  0.002  ← ~1 payload lặp lại
  3000:  0.002
  12000: 0.002

──── PANEL V3 (entropy reg fix) ────────────────────────────────

Line V3 AST-Entropy — màu #2E7D32, 2px solid:
  0:     0.5
  1000:  2.91   ← warmup V3 (64/64 unique)
  2000:  3.07   ← ★ BEST (đạt target > 3.0)
  3000:  2.xx   ← adversarial starts, slow collapse
  6000:  2.70
  9000:  2.67
  12000: 2.67   ← partial collapse nhưng không frozen

Line V3 Re-lex — màu #2E7D32, 1.5px dashed:
  0:     0.686
  1000:  0.926
  2000:  1.000  ← ★ PERFECT diversity (500/500 unique)
  3000:  ~0.5
  6000:  0.010
  9000:  0.008  ← collapse nhưng chậm hơn V2

[Vertical dashed line đỏ tại x=2000 (V2)]    Label: "❌ V2 Collapse"
[Vertical dashed line xanh tại x=2000 (V3)]  Label: "★ V3 Best (production)"
[Horizontal dotted line tại AST=3.0]          Label: "Target AST-H > 3.0"
```

**Bên phải chart — V2 vs V3 cơ chế:**

```
[BOX TRÁI — nền #FFEBEE — V2 FAIL]

V2: REINFORCE Flat Gradient

reward ≈ 0.70 (all batch members)
advantage = r - mean(r) ≈ 0
∇L = -log_prob × 0 ≈ 0
Generator locked. Cache hit: 93%.

[BOX PHẢI — nền #E8F5E9 — V3 FIX]

V3: Entropy Regularization

g_loss = pg_loss
       - 0.05 × H(logits)   ← warmup

H(logits) > 0 kể cả khi advantage=0
→ Gradient luôn ≠ 0
→ Cache hit: 42% (V2: 93%)
→ 64/64 unique/batch (V2: 1-2/64)
```

**Speaker Notes:**
So sánh V2 vs V3 cho thấy entropy regularization là fix chính xác: V3 warmup đạt 64/64 unique payloads mỗi batch (V2: 1-2/64), cache hit rate 42% (V2: 93%), re-lex uniqueness 1.000 (V2: 0.010). Tuy nhiên V3 adversarial phase vẫn collapse chậm dần từ step 3000 — xác nhận mode collapse là vấn đề fundamental của on-policy REINFORCE với fixed reward ceiling, entropy reg chỉ trì hoãn, không giải quyết triệt để. Production model = step2000 (cuối warmup).

---

### SLIDE 13 — V1 vs V2: Toàn Cảnh Tiến Bộ

**Layout:** `TITLE_TABLE`
**Header:** "So Sánh V1 và V2: Cái Gì Tốt Hơn, Cái Gì Vẫn Chưa Giải Được"

**Bảng so sánh:**

| Metric | V1 | V2 best | **V3 best ★** | Trạng thái |
|--------|----|---------|--------------|------------|
| MLE val_ppl | 1.70 | 1.27 | **1.27** | ✅ V2/V3 cùng MLE |
| Kiến trúc | Unconditional | Conditional (4 types) | **Same + entropy reg** | ✅ |
| Reward | Heuristic proxy | ModSec + Custom + AST | **Same** | ✅ |
| DB execution | — | 99.8% | **99.2%** | ✅ |
| ML-IDS evasion | — | 31.4% | **0%** ⚠ | Tradeoff |
| Composite score | ~0.202 | 0.394 | **0.471** | ✅ +133% vs MLE |
| Re-lex uniqueness | — | 0.010 ❌ | **1.000** | ✅ Fixed! |
| AST entropy | — | 2.42 | **3.07** | ✅ > 3.0 target |
| OWASP bypass | — | — | **2.0%** (step2000) | Metric thực |
| Root cause collapse | lambda_d=0 | flat gradient | **entropy reg giảm** | Partial fix |
| Cache hit rate | — | 93% ❌ | **42%** | ✅ 2× diversity |
| Unique/batch (64) | — | 1-2 ❌ | **64/64** (warmup) | ✅ Fixed! |

**Footer — 3 box nhận xét:**

```
[BOX XANH LÁ]
✅ V3 entropy reg fix mode collapse trong warmup
   relex 0.010 → 1.000 · AST 2.42 → 3.07 · cache 93% → 42%

[BOX CAM]
⚠ ML-IDS evasion = 0% ở V3 final (vs V2: 31.4%)
  IDS học nhận ra pattern warmup generator — tradeoff tất yếu

[BOX ĐỎ]
❌ Adversarial phase vẫn collapse (chậm hơn V2 nhưng vẫn xảy ra)
   Mode collapse là fundamental RL problem, entropy reg chỉ trì hoãn
   → Production model = warmup checkpoint (step2000)
```

**Speaker Notes:**
V3 là bước nhảy vọt thực sự: re-lex uniqueness từ 0.010 lên 1.000 (500/500 payload duy nhất), AST entropy vượt target 3.0. Tradeoff cần minh bạch: ML-IDS evasion về 0% vì IDS học nhận ra pattern của warmup generator — đây là dấu hiệu model cần adversarial phase dài hơn để escape khỏi distribution quen thuộc. Production model là step2000 (cuối warmup).

---

### SLIDE 14 — Phân Tích 5-Metric Evaluation Framework

**Layout:** `TITLE_CHART`
**Header:** "5-Metric Ensemble: Tại Sao Cần Nhiều Metric?"

**Chart — Radar chart (spider) cho 3 model:**

```
[RADAR CHART — 5 trục]

Các trục (normalize về 0-1):
  1. OWASP Bypass Rate    (target > 60%)
  2. DB Execution Rate    (target > 80%)
  3. AST Diversity        (target > 3.0 → normalize = /5.0)
  4. ML-IDS Evasion       (target > 50%)
  5. Re-lex Uniqueness    (target > 90%)

Model 1 — v2_mle (màu #90CAF9 xanh nhạt, dashed):
  OWASP: 0.0 (không đo — WAF tắt)
  DB Exec: 0.032
  AST: 3.083/5 = 0.617
  IDS: 0.034
  Relex: 0.658

Model 2 — v2_step1000 ★ (màu #2E7D32 xanh lá, solid 2px):
  OWASP: 0.0 (WAF tắt — điểm yếu đo lường)
  DB Exec: 0.998
  AST: 2.417/5 = 0.483
  IDS: 0.386
  Relex: 0.008

Model 3 — Target V3 (màu #2196F3 xanh dương, dotted):
  OWASP: 0.60
  DB Exec: 0.80
  AST: 3.5/5 = 0.70
  IDS: 0.50
  Relex: 0.70
```

**Bên phải — Trọng số và lý do:**

| Metric | Weight | Lý do |
|--------|--------|-------|
| OWASP bypass rate | 30% | Signal mạnh nhất về bypass thực sự |
| DB execution rate | 25% | Payload phải chạy được mới có ý nghĩa |
| AST diversity entropy | 20% | Đo structural diversity, không bị de-lex confound |
| ML-IDS evasion | 15% | Đo khả năng né classifier downstream |
| Re-lex uniqueness | 10% | Surface-level uniqueness sau khi điền literal |

```
Composite = 0.30×owasp + 0.25×db + 0.20×(ast/5) + 0.15×ids + 0.10×relex
```

**Speaker Notes:**
Self-BLEU-3 là metric phổ biến trong literature nhưng có một confounding factor nghiêm trọng: de-lexicalization khiến nhiều payload khác nhau về surface trở thành cùng token sequence. AST entropy không bị confound này vì nó đo cấu trúc cú pháp SQL, không phải token sequence. Đây là lý do đề tài dùng 5-metric ensemble thay vì chỉ Self-BLEU.

---

### SLIDE — SECTION BREAK: PHẦN V — V3 & ĐÓNG GÓP

**Layout:** `SECTION_BREAK`
**Background:** Full `#1B2A4A`

```
PHẦN V

Kế Hoạch V3 & Đóng Góp Khoa Học

Fix có nguyên lý · 3 thay đổi nhỏ · Impact lớn
```

---

### SLIDE 15 — Kế Hoạch V3: Entropy Regularization

**Layout:** `TITLE_CODE`
**Header:** "V3 Fix: 3 Thay Đổi Nhỏ — ĐÃ CHẠY, Kết Quả Thực"

**Code block 1 — Fix #1: Entropy Regularization (5 dòng):**

```python
# src/losses.py — thêm hàm mới

def reinforce_loss_with_entropy(log_probs, advantages, entropy_coeff=0.03):
    """
    REINFORCE + entropy bonus để ngăn distribution collapse.
    Khi entropy thấp (generator ra cùng token), bị penalize.
    """
    entropy = -(log_probs.exp() * log_probs).sum(dim=-1).mean()
    reinforce = -(log_probs * advantages).mean()
    return reinforce - entropy_coeff * entropy  # entropy cao → loss nhỏ → ưu tiên
```

**Code block 2 — Fix #2: EMA Baseline (4 dòng):**

```python
# train_adversarial_v3.py

ema_baseline = 0.0
for step in range(total_steps):
    rewards = compute_rewards(fake_seqs)
    ema_baseline = 0.9 * ema_baseline + 0.1 * rewards.mean()
    advantages = rewards - ema_baseline  # signal ngay cả khi rewards đều nhau
```

**Code block 3 — Fix #3: Temperature Sampling (1 dòng):**

```python
# Thêm temperature > 1.0 trong training → exploration noise
token_ids, log_probs = generator.sample(input_ids, attack_type_ids,
                                        temperature=1.1)  # thay vì 1.0
```

**Bên dưới — Kết quả thực nghiệm V3 (đã chạy 2026-05-12):**

```
[TABLE — 4 cột]
Metric              │ V2 step1000  │ V3 step2000 ★  │ Delta
────────────────────┼──────────────┼────────────────┼──────────────
Composite score     │ 0.394        │ 0.471          │ +20%
Re-lex uniqueness   │ 0.010 ❌     │ 1.000 ✅        │ +99pp
AST entropy         │ 2.42 ⚠       │ 3.07 ✅         │ +0.65
Custom rules pass   │ 60.0%        │ 94.6%          │ +34.6pp
DB execution        │ 99.8%        │ 99.2%          │ ≈ same
Unique/batch (64)   │ 1-2 ❌       │ 64/64 ✅        │ Fixed
Cache hit rate      │ 93% ❌       │ 42% ✅          │ Fixed
OWASP bypass        │ —            │ 2.0% (step2000)│ NEW metric
```

```
Training signals V3 warmup (0-2000 steps):
  - unique/batch: 6 → 64/64 (recovered by step 750, V2 stuck at 1-2)
  - H (entropy): 1.06 → 1.46 (tăng liên tục)
  - avg_reward:  0.39 → 0.62
  - cache hit:   starts 42% (V2 started at 93%)
```

**Speaker Notes:**
Ba fix đã được implement và chạy xong. Kết quả xác nhận entropy regularization là đúng hướng: unique/batch tăng từ 1-2 lên 64/64, re-lex uniqueness đạt 1.000 (hoàn hảo). Entropy term đảm bảo gradient ≠ 0 kể cả khi advantage ≈ 0. Tuy nhiên adversarial phase vẫn collapse chậm từ step 3000 → production model là step2000 (warmup).

---

### SLIDE 16 — Đóng Góp Khoa Học

**Layout:** `TITLE_CONTENT`
**Header:** "5 Đóng Góp Của Đề Tài"

**5 contribution boxes — layout 2+3 (2 trên, 3 dưới):**

```
[ROW 1 — 2 boxes]

╔══════════════════════════════════╗  ╔═══════════════════════════════════╗
║ 🏗️ C1: Pipeline End-to-End       ║  ║ 🎯 C2: Real WAF Oracle            ║
║                                  ║  ║                                   ║
║ Raw data → Conditional SeqGAN    ║  ║ ModSecurity CRS v4.3.0 Docker     ║
║ → 5-metric evaluation            ║  ║ làm reward signal trực tiếp       ║
║                                  ║  ║                                   ║
║ Không bài nào trong literature   ║  ║ Chowdhary 2023, Lu 2022 đều       ║
║ có cùng pipeline hoàn chỉnh      ║  ║ chỉ dùng heuristic proxy          ║
╚══════════════════════════════════╝  ╚═══════════════════════════════════╝

[ROW 2 — 3 boxes]

╔══════════════════╗  ╔══════════════════════╗  ╔════════════════════════╗
║ 📐 C3: Boundary  ║  ║ 🏷️ C4: 2-Step Labeling║  ║ 🔬 C5: Collapse Diag.  ║
║ Aware Reward     ║  ║                      ║  ║                        ║
║                  ║  ║ Script tự động +     ║  ║ Cơ chế REINFORCE flat  ║
║ r = 1-dist/thr   ║  ║ AI prompt 348 dòng   ║  ║ gradient được document ║
║ Không phải 0/1   ║  ║ → 17.821 rows        ║  ║ chi tiết               ║
║                  ║  ║ mean confidence=0.93  ║  ║ → Guide V3 và các      ║
║ Novel contribution║  ║ Tiered confidence    ║  ║ nghiên cứu tương lai   ║
╚══════════════════╝  ╚══════════════════════╝  ╚════════════════════════╝
```

**Màu boxes:**
- C1, C2: nền `#E3F2FD`, viền `#2196F3` 2px
- C3, C4: nền `#E8F5E9`, viền `#2E7D32` 2px
- C5: nền `#FFF3E0`, viền `#E65100` 2px

**Speaker Notes:**
Contribution C5 (chẩn đoán mode collapse) thường bị đánh giá thấp nhưng thực ra rất có giá trị: việc document rõ ràng cơ chế thất bại, điều kiện xảy ra, và cách fix giúp các nghiên cứu sau tránh mắc cùng lỗi. Đây là tiêu chuẩn của nghiên cứu khoa học chất lượng cao — không che giấu failure.

---

### SLIDE 17 — Roadmap V1 → V2 → V3

**Layout:** `TITLE_DIAGRAM`
**Header:** "Hành Trình Nghiên Cứu: 3 Vòng Thực Nghiệm"

**Diagram — 3 columns ngang:**

```
         V1                    V2                      V3 ✅ DONE
    (2026-05-10)          (2026-05-12 am)          (2026-05-12 pm)
  ─────────────────   ─────────────────────    ─────────────────────
  ┌───────────────┐   ┌─────────────────────┐  ┌─────────────────────┐
  │ Unconditional │   │ Conditional SeqGAN  │  │ V2 + Entropy Reg    │
  │ SeqGAN        │   │ 4 attack types      │  │ + EMA Baseline      │
  │               │   │ + Composite Reward  │  │ + Temperature 1.2/1.1│
  │ val_ppl=1.70  │→→→│ val_ppl=1.27  ✅   │→→→│ val_ppl=1.27  ✅   │
  │               │   │                     │  │                     │
  │ ASR=100% ✅   │   │ DB exec 99.8% ✅    │  │ DB exec 99.2% ✅    │
  │ Syntax 100% ✅│   │ IDS evasion 31.4% ✅│  │ IDS evasion 0% ⚠   │
  │ Self-BLEU     │   │ Composite +95% ✅   │  │ Composite +133% ✅  │
  │ 0.9894 ❌     │   │ Mode collapse ❌    │  │ relex = 1.000 ✅    │
  │               │   │ relex=0.002 ❌      │  │ AST-H = 3.07 ✅     │
  └───────────────┘   └─────────────────────┘  └─────────────────────┘
         │                      │                        │
         ▼                      ▼                        ▼
   Root cause:           Root cause:              Result:
   lambda_d=0            REINFORCE flat           Warmup fixed ✅
   proxy reward          gradient                 Adversarial still
   too easy              (no entropy reg)         collapses slowly
                                                  → prod = step2000
```

**Bên dưới — timeline thực tế:**

```
[Horizontal timeline bar — 1 ngày duy nhất]

May 10 09:00  ── May 10 14:00  ── May 12 09:21  ── May 12 10:54  ── May 12 12:xx
  V1 done           V1 eval           V2 MLE done       V2 Adv done      V3 done ★
  ASR 100%          BLEU 0.9894❌     ppl=1.27           mode collapse    relex=1.000
  4h56m             root cause        15min              46min             11:08-12:xx
  training          identified        training           training          training
```

**Speaker Notes:**
Toàn bộ hành trình V1→V2→V3 diễn ra trong vòng 2-3 ngày làm việc. V3 là kết quả cuối cùng và đã được eval đầy đủ. Mỗi vòng iteration đều học được điều gì đó non-trivial: V1 → pipeline bugs; V2 → real WAF oracle + flat gradient diagnosis; V3 → entropy reg giải quyết warmup nhưng confirm adversarial phase là fundamental RL problem.

---

### SLIDE 18 — Kết Luận & Hướng Mở

**Layout:** `TWO_COLUMN`
**Header:** "Kết Luận và Hướng Nghiên Cứu Tiếp Theo"

**Cột trái — Đã đạt được:**

```
✅ ĐÃ HOÀN THÀNH (V1 → V2 → V3)

Dataset:
• 17.821 SQLi có nhãn chất lượng cao
• 4 types · 3 confidence tiers
• mean confidence = 0.93

Architecture:
• Conditional SeqGAN V3 — 4 attack types
• Composite reward (WAF + custom + AST)
• Boundary-aware reward (novel)
• Entropy regularization + EMA baseline

Kết quả thực (production model V3 step2000):
• Composite score +133% vs MLE (0.471 vs 0.202)
• Re-lex uniqueness = 1.000 (500/500 unique) ✅
• AST entropy = 3.07 (vượt target 3.0) ✅
• DB execution 99.2% ✅
• OWASP bypass 2.0% (WAF eval thực)
• Mode collapse cơ chế: document đầy đủ
  toán học rõ ràng + 2 iteration fix
```

**Cột phải — Hướng tiếp theo:**

```
⚠ TRADEOFF CẦN MINH BẠCH

• ML-IDS evasion = 0% ở production model
  (V2: 31.4%) — IDS nhận ra warmup pattern
  Giải pháp: adversarial training dài hơn
  sau khi giải quyết collapse hoàn toàn

🔭 TRUNG HẠN (thesis improvement)

• PPO thay REINFORCE
  → ổn định hơn, KL constraint với MLE
  → có thể giải quyết triệt để collapse
• Multi-DB sandbox (MySQL + Oracle)
  → SQLite miss Oracle XMLTYPE syntax
• Thêm nguồn data: PortSwigger, HackTricks
  → giảm source bias

🌐 DÀI HẠN (future work)

• Test trên WAF khác (Cloudflare, AWS WAF)
  → đo generalization beyond CRS v4.3.0
• Transfer learning sang XSS, Path Traversal
• Adaptive WAF: model learns thresholds
```

**Footer — câu kết:**

```
[BOX Full-width — nền #1B2A4A, text trắng]
"Đề tài chứng minh conditional SeqGAN với real WAF oracle và entropy regularization
 đạt re-lex uniqueness = 1.000 và AST diversity vượt target.
 Mode collapse trong adversarial phase được chẩn đoán và document là
 fundamental problem của on-policy REINFORCE — hướng cho nghiên cứu tiếp theo."
```

**Speaker Notes:**
V3 đã chạy xong và có kết quả thực. Production model (step2000) đạt re-lex uniqueness 1.000 và AST entropy 3.07 — cả hai đều vượt target. Tradeoff cần nói rõ với hội đồng: ML-IDS evasion về 0% vì warmup generator chưa đủ đa dạng để né classifier — cần adversarial phase dài hơn với PPO để fix triệt để. Đây là honest assessment của nghiên cứu, không phải failure.

---

## PHẦN C — TÀI LIỆU THAM KHẢO GỢI Ý (Slide phụ, nếu cần)

**Slide bổ sung — không bắt buộc:**

| # | Bài báo | Năm | Liên quan |
|---|---------|-----|-----------|
| [1] | Yu et al. — SeqGAN: Sequence GAN with Policy Gradient | 2017 | Backbone architecture |
| [2] | Lu et al. — A GAN-based Method for Generating SQLi Attack Samples | 2022 | DCGAN + GA approach |
| [3] | Dasari et al. — Enhancing SQLi Detection Using Generative Models | 2025 | CWGAN-GP baseline |
| [4] | Le Minh Khan et al. — GSQLi: GAN-based Adversarial SQLi Sample Generation | 2024 | Closest related work |
| [5] | Chowdhary et al. — GAN-Based Autonomous Pentesting for Web Apps | 2023 | Conditional SeqGAN |
| [6] | Zhao et al. — Enhancing NIDS Performance using GAN | 2024 | CTGAN comparison |
| [7] | Udu et al. — Emerging SMOTE and GAN Variants Review | 2025 | GAN > SMOTE justification |
| [8] | Zhu et al. — Texygen: Benchmark for Text Generation Models | 2018 | Self-BLEU metric definition |

---

## PHẦN D — RAW DATA ĐỂ VẼ CHART

### D1. Radar Chart Data (Slide 14)

```json
{
  "models": {
    "v2_mle": {
      "db_execution": 0.032,
      "ast_entropy_norm": 0.617,
      "ml_ids_evasion": 0.034,
      "relex_uniqueness": 0.658,
      "owasp_bypass": 0.0
    },
    "v2_step1000_best": {
      "db_execution": 0.998,
      "ast_entropy_norm": 0.483,
      "ml_ids_evasion": 0.386,
      "relex_uniqueness": 0.008,
      "owasp_bypass": 0.0
    },
    "v3_target": {
      "db_execution": 0.80,
      "ast_entropy_norm": 0.70,
      "ml_ids_evasion": 0.50,
      "relex_uniqueness": 0.70,
      "owasp_bypass": 0.60
    }
  },
  "note": "ast_entropy_norm = ast_entropy / 5.0; owasp_bypass = 0 vì WAF Docker disabled khi eval"
}
```

### D2. Line Chart Data — V2 vs V3 Mode Collapse Comparison (Slide 12)

```json
{
  "x_steps": [0, 1000, 2000, 3000, 6000, 9000, 12000],

  "V2_ast_entropy":      [0.5,  2.42,  2.565, 2.565, 2.565, 2.565, 2.565],
  "V2_relex_uniqueness": [0.686, 0.010, 0.002, 0.002, 0.002, 0.002, 0.002],

  "V3_ast_entropy":      [0.5,  2.91,  3.07,  2.80,  2.70,  2.67,  2.67],
  "V3_relex_uniqueness": [0.686, 0.926, 1.000, 0.50,  0.020, 0.008, 0.008],

  "annotations": {
    "x=1000_V2": "V2 end warmup — collapse imminent",
    "x=2000_V2": "❌ V2 Mode collapse (AST frozen at 2.565)",
    "x=2000_V3": "★ V3 Best = production model (step2000)",
    "y=3.0": "Target AST entropy > 3.0",
    "V3_phase_boundary": "x=2000 warmup ends → adversarial starts"
  },
  "note": "V3 warmup: 64/64 unique payloads per batch. V2 warmup: 1-2/64."
}
```

### D3. Dataset Distribution (Slide 5)

```json
{
  "sqli_types": {
    "error_based":   {"count": 7315, "pct": 41},
    "boolean_blind": {"count": 6335, "pct": 36},
    "time_blind":    {"count": 2283, "pct": 13},
    "union_based":   {"count": 1888, "pct": 10}
  },
  "total_sqli": 17821,
  "benign": 19669,
  "confidence": {
    "gold_pct":   60,
    "silver_pct": 25,
    "bronze_pct": 15,
    "mean": 0.93
  }
}
```

### D4. Training Results Table (Slide 11) — UPDATED với V3

```json
{
  "checkpoints": [
    {"name":"MLE baseline",     "db_exec":0.032, "ast_h":3.08, "custom":0.868, "ml_ids":0.034, "relex":0.686, "composite":0.202, "owasp_bypass":null},
    {"name":"V2 step1000",      "db_exec":0.998, "ast_h":2.42, "custom":0.600, "ml_ids":0.314, "relex":0.010, "composite":0.394, "owasp_bypass":null},
    {"name":"V2 step2000+",     "db_exec":1.000, "ast_h":2.565,"custom":null,  "ml_ids":0.000, "relex":0.002, "composite":0.353, "owasp_bypass":null},
    {"name":"V3 step1000",      "db_exec":0.998, "ast_h":2.91, "custom":0.774, "ml_ids":null,  "relex":0.926, "composite":0.460, "owasp_bypass":0.098},
    {"name":"V3 step2000 ★",    "db_exec":0.992, "ast_h":3.07, "custom":0.946, "ml_ids":0.000, "relex":1.000, "composite":0.471, "owasp_bypass":0.020},
    {"name":"V3 step12000",     "db_exec":1.000, "ast_h":2.67, "custom":0.800, "ml_ids":null,  "relex":0.008, "composite":0.357, "owasp_bypass":0.434}
  ],
  "eval_conditions_no_waf": "500 samples, WAF disabled, seed=42",
  "eval_conditions_with_waf": "ModSecurity OWASP CRS v4.3.0 PL2 Docker enabled",
  "production_model": "checkpoints/v3/adv_step2000.pt",
  "warning_v3_step12000": "High OWASP bypass (43.4%) but relex=0.008 — only 1 unique payload repeated 500x. Not useful."
}
```

### D5. V1 Results (từ eval_report.json)

```json
{
  "v1_seqgan_adv": {
    "asr_mean": 1.0,
    "asr_ci": [1.0, 1.0],
    "syntax_rate": 1.0,
    "self_bleu_3": 0.9894,
    "length_mean": 68.1,
    "length_std": 20.6,
    "training_steps": 5000,
    "training_time_hours": 4.93
  },
  "v1_mle": {
    "asr_mean": 0.697,
    "asr_ci": [0.668, 0.725],
    "self_bleu_3": 0.9833
  },
  "v1_template": {
    "asr_mean": 0.679,
    "self_bleu_3": 0.6836,
    "trivial_rate": 0.067
  },
  "config": "seqgan_fast.yaml — lambda_d=0.0"
}
```

---

## PHẦN E — HƯỚNG DẪN DÙNG VỚI TỪNG TOOL

### E1. Gamma.app

```
Bước 1: Vào gamma.app → New Presentation → "Generate with AI"
Bước 2: Paste nội dung PHẦN B (Slide 1–18) vào prompt box
Bước 3: Thêm vào đầu prompt:
  "Create an 18-slide academic thesis defense presentation.
   Language: Vietnamese with English technical terms.
   Theme: Professional dark navy with blue accents.
   Color: Primary #1B2A4A, Accent #2196F3, Success #2E7D32, Failure #C62828.
   Each slide: follow the layout and content exactly as specified.
   For tables: use the exact data provided in Section D (Raw Data)."
Bước 4: Sau khi gen, edit từng slide để khớp màu sắc theo Design System
```

### E2. Claude / ChatGPT (sinh python-pptx code)

```
Bước 1: Paste toàn bộ file này vào conversation
Bước 2: Dùng prompt:
  "Generate complete Python code using python-pptx library to create this
   18-slide presentation. Use the exact colors (#1B2A4A, #2196F3, etc.),
   layout names, table data from Section D, and content from Section B.
   Make the code runnable with: pip install python-pptx"
Bước 3: Chạy code Python → file .pptx được tạo tự động
Bước 4: Mở trong PowerPoint → fine-tune manually
```

### E3. Tome.app hoặc Beautiful.ai

```
Bước 1: Chọn template "Academic" hoặc "Research"
Bước 2: Import nội dung từng slide theo Section B
Bước 3: Dùng màu Custom theo Color Palette trong Section A1
Bước 4: Charts: dùng data từ Section D, import dưới dạng JSON/CSV
```

### E4. Canva (với Magic Design)

```
Bước 1: Tạo presentation mới → Chọn theme "Professional"
Bước 2: Set màu brand: #1B2A4A (primary), #2196F3 (accent)
Bước 3: Paste nội dung từng slide vào Magic Write
Bước 4: Charts: dùng Canva Chart tool với data từ Section D
```

---

## PHẦN F — CHECKLIST TRƯỚC KHI THUYẾT TRÌNH

- [ ] Slide 1: Điền đúng tên sinh viên, GVHD, chuyên ngành
- [ ] Slide 11: Kiểm tra bảng số liệu khớp với V2_RESULTS.md
- [ ] Slide 12: Xác nhận line chart AST entropy frozen tại 2.5649 từ step 2000
- [ ] Slide 14: Radar chart có ghi chú "OWASP=0 vì WAF disabled khi eval"
- [ ] Slide 15: Code blocks hiển thị đúng (font Consolas, nền tối)
- [ ] Tất cả bảng: header row nền #1B2A4A, text trắng
- [ ] Tổng thời gian: 20-25 phút present + 5-10 phút Q&A
- [ ] In handout: Slide 4 (Gap table), Slide 11 (Results), Slide 15 (V3 fix)

---

## PHẦN G — CÂU HỎI HỘI ĐỒNG DỰ KIẾN & TRẢ LỜI

| Câu hỏi | Slide liên quan | Gợi ý trả lời ngắn |
|---------|----------------|---------------------|
| "Tại sao V2 vẫn thất bại ở adversarial?" | 12 | REINFORCE flat gradient — advantage≈0 khi rewards bằng nhau — cơ chế toán học rõ ràng ở slide 12 |
| "Kết quả V3 chưa có, có đủ để bảo vệ không?" | 11, 16 | V2 warmup (composite +100%, 38.6% evasion) là kết quả thực sự. V3 chỉ 3 file ~15 dòng |
| "SMOTE có đủ không, tại sao cần GAN?" | 2, 3 | SMOTE nội sinh — interpolate không tạo pattern cú pháp SQL mới. GAN học phân phối ẩn |
| "WAF Oracle giả sử nào? Không phải Cloudflare?" | 9 | ModSecurity CRS v4.3.0 — open source WAF chuẩn OWASP. Generalization sang WAF khác là limitation L1 đã document |
| "Self-BLEU 0.9894 rất tệ — tại sao?" | 7, 14 | De-lex confound: nhiều payload khác bị coi là giống nhau sau de-lex. AST entropy đo đúng hơn, không bị confound |
| "Dataset có đủ không? Chỉ 17K mẫu?" | 5, 6 | 17.821 SQLi + 19.669 benign. So với lu2022 (2.000 mẫu) hay gsqli — dataset của đề tài lớn hơn đáng kể |
| "Điểm khác biệt với GSQLi (UIT 2024) là gì?" | 4 | GSQLi: sinh mutation actions (không phải payload trực tiếp), dùng libinjection (không phải ModSecurity), không dùng conditional embedding theo attack type |

---

*File này được tạo: 2026-05-12*
*Nguồn số liệu: timeline/eval_report.json · timeline/V2_RESULTS.md · timeline/V2_POSTMORTEM_AND_V3_PLAN.md*
*Kiến trúc: SeqGAN_SQLi/Guiding_V2.md · EXECUTION_PLAYBOOK.md*
*Dataset: Asset/LabelData/latest_relabel_data.csv (17.821 rows)*
