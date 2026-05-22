# 03 — Phân tích sâu từ paper (nhánh Gumbel-Softmax)

> **Ngày:** 2026-05-22 · **Vai trò:** đọc *sau* `00/01/02`. File này trích **nội dung OCR gốc** (không phải bản analysis tóm tắt) của các paper trong `Asset/Total_OCR1`, để chốt các quyết định kỹ thuật bằng dòng cụ thể.
> Ba paper trục cho nhánh này: **RelGAN** (bằng chứng Gumbel làm text-GAN chạy), **MaskGAN** (tiền lệ masked in-filling), **GSQLi** (tiền lệ domain mutation-action — giải trực tiếp rủi ro PB2 của `02`).

---

## 1. RelGAN (Nie 2019): bằng chứng "Gumbel-Softmax làm text-GAN chạy" — *kèm điều kiện*

RelGAN tự nhận là **kiến trúc đầu tiên làm GAN-với-Gumbel-Softmax sinh được text thực tế** [`Asset\Total_OCR1\Nie_2019_RelGAN.md:28-29`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) [`Asset\Total_OCR1\Nie_2019_RelGAN.md:75-76`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md). Đây là *bằng chứng tồn tại* quan trọng nhất ủng hộ nhánh — nhưng đọc kỹ thì nó **không phải "chỉ thêm Gumbel"**, mà là một combo 3 thành phần + điều kiện huấn luyện chặt:

### 1.1 Temperature: phát hiện trực tiếp giải thích collapse Phase 2 của ta

RelGAN dùng **inverse temperature β** trong `ŷ = σ(β(o+g))` [`Asset\Total_OCR1\Nie_2019_RelGAN.md:232-234`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md). Lập luận cốt lõi:
- **β nhỏ** → generator buộc phải làm **phân phối logit của chính nó sắc** để bù khoảng cách relaxation → "implicitly discourages exploration... **this might be one factor that contributes to mode collapse**". [`Asset\Total_OCR1\Nie_2019_RelGAN.md:279-282`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md)
- **β lớn** → variance gradient `Var(∂ŷ/∂o) ∝ β²` rất lớn → quality kém. [`Asset\Total_OCR1\Nie_2019_RelGAN.md:275-278`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md)
- Giải pháp: **tăng dần β** theo `βn = βmax^(n/N)` (mềm lúc đầu, sắc dần) — *ngược* hướng "anneal cho sắc ngay". [`Asset\Total_OCR1\Nie_2019_RelGAN.md:284-291`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md)
- Hai cực đều hỏng: `βmax=1` → **collapse nặng + bất ổn**; `βmax=10⁷` → quality cải thiện không đáng kể; điểm ngọt {100, 1000}. [`Asset\Total_OCR1\Nie_2019_RelGAN.md:1125-1129`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md)

**Liên hệ trực tiếp với ta (mới):** `gan_results.json` Phase 2 cho thấy `tau` (nhiệt độ, = 1/β) **giảm 0.910 → 0.730 → ... → 0.370** trong khi unique đứng yên. [`Guiding\Phase 2\eval\gan_results.json:18-34`](..\Guiding\Phase%202\eval\gan_results.json) [`Guiding\Phase 2\eval\gan_results.json:80-87`](..\Guiding\Phase%202\eval\gan_results.json) Giảm τ = **làm phân phối sắc dần** — đúng *chiều mà RelGAN cảnh báo gây collapse* (β nhỏ → ép sắc → mất exploration). ⇒ Lịch nhiệt độ của Phase 2 **đi sai hướng / quá nhanh** theo lý thuyết RelGAN. Đây là chẩn đoán kỹ thuật cụ thể, không phải "GAN nói chung khó".

### 1.2 Những điều kiện RelGAN bắt buộc (mà "thêm Gumbel" đơn thuần không có)

- **MLE pre-train là cần thiết** cho hội tụ tốt — RelGAN pretrain generator 150 epoch lr 1e-2 rồi mới adversarial lr 1e-4. [`Asset\Total_OCR1\Nie_2019_RelGAN.md:387-388`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) [`Asset\Total_OCR1\Nie_2019_RelGAN.md:853-854`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) → khớp với **MLE anchor** của nhánh ta.
- **KHÔNG WGAN-GP.** RelGAN so 3 loss và chọn **RSGAN (relativistic)**; khi train *không pretrain*, WGAN-GP cho BLEU-2 chỉ `0.330` so với standard GAN `0.590`, hinge thì vanishing gradient. [`Asset\Total_OCR1\Nie_2019_RelGAN.md:361-367`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) [`Asset\Total_OCR1\Nie_2019_RelGAN.md:1073-1101`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) → củng cố nguyên tắc bất biến #4 của `00` (bỏ WGAN-GP). **Đề nghị thử RSGAN/hinge cho D thay vì BCE thuần.**
- **Gumbel >> REINFORCE** trong cùng khung: variance gradient của REINFORCE "quá lớn để cung cấp update hữu ích", không cải thiện sau pretrain. [`Asset\Total_OCR1\Nie_2019_RelGAN.md:640-650`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) → đây là lý do *chính đáng* để bỏ MC-rollout/REINFORCE của SeqGAN cũ (khớp `00` D.4).
- **D nhiều biểu diễn nhúng (S=64)** cho tín hiệu phong phú hơn → liên quan trực tiếp ý tưởng paired/multi-view D. Cấu hình: filter {3,4,5}, 300 feature map, batch 64, **5 bước D / 1 bước G**. [`Asset\Total_OCR1\Nie_2019_RelGAN.md:847-856`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md)
- **Diversity-quality transition:** quality tăng rồi giảm, diversity ngược lại, bước ngoặt ~800 iter. [`Asset\Total_OCR1\Nie_2019_RelGAN.md:1029-1053`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) → khẳng định **phải early-stop/checkpoint theo frontier**, không train đến cùng.

> **Rút ra:** RelGAN chứng minh Gumbel-text-GAN khả thi, nhưng cái làm nó chạy là *relational-memory + RSGAN + S=64 + lịch β tăng dần + MLE pretrain*, không phải Gumbel đơn lẻ. Điều này **củng cố PB1 của `02`**: Gumbel là điều kiện cần, không phải đủ.

---

## 2. MaskGAN (Fedus 2018): tiền lệ masked in-filling — ủng hộ *và* cảnh báo

MaskGAN là tiền lệ gần nhất với "masked payload-surgery" của ta: nó **xóa một phần text rồi điền vào (in-fill) có điều kiện ngữ cảnh xung quanh** [`Asset\Total_OCR1\Fedus_2018_MaskGAN.md:66-72`](..\Asset\Total_OCR1\Fedus_2018_MaskGAN.md) [`Asset\Total_OCR1\Fedus_2018_MaskGAN.md:142-161`](..\Asset\Total_OCR1\Fedus_2018_MaskGAN.md).

### 2.1 Ủng hộ kiến trúc nhánh ta

- **In-filling giảm collapse + giảm D-saturation:** "in-filling may mitigate the problem of severe mode-collapse. This task is also harder for the discriminator which **reduces the risk of the generator contending with a near-perfect discriminator**". [`Asset\Total_OCR1\Fedus_2018_MaskGAN.md:132-137`](..\Asset\Total_OCR1\Fedus_2018_MaskGAN.md) → đây là **bằng chứng paper trực tiếp** cho luận điểm masked-slot chống RC1 (D bão hòa) của `00` D.2.
- **D phải nhận ngữ cảnh thật** — nếu không, D không biết token nào là giả ("director director" — không phân biệt được occurrence nào giả). [`Asset\Total_OCR1\Fedus_2018_MaskGAN.md:178-191`](..\Asset\Total_OCR1\Fedus_2018_MaskGAN.md) → đây chính là lý lẽ paper cho **paired-D theo cùng khung+condition** (`00` mục E). Không có ngữ cảnh = tín hiệu học sai cho generator.
- **Reward theo từng token** (credit assignment mịn) nhờ D chấm mỗi vị trí. [`Asset\Total_OCR1\Fedus_2018_MaskGAN.md:73-80`](..\Asset\Total_OCR1\Fedus_2018_MaskGAN.md)
- **Mask khối liên tục > mask ngẫu nhiên** cho chất lượng. [`Asset\Total_OCR1\Fedus_2018_MaskGAN.md:596-599`](..\Asset\Total_OCR1\Fedus_2018_MaskGAN.md) → gợi ý cách chọn slot khi thiết kế surgery dataset (Phase 04).

### 2.2 Cảnh báo (phản biện trung thực — phải đưa vào proposal)

- **Masked-surgery KHÔNG diệt được collapse, vẫn thua MLE về đa dạng.** Table 6: % unique quadgram **MaskGAN 88.2 < MaskMLE 92.6 < LM 91.9**. [`Asset\Total_OCR1\Fedus_2018_MaskGAN.md:443-462`](..\Asset\Total_OCR1\Fedus_2018_MaskGAN.md) Tức ngay cả tiền lệ in-filling tốt nhất *vẫn kém MLE* ở metric đa dạng — đúng kịch bản G1/G2 của ta có thể fail. Đây là tham chiếu khách quan cho gate "tie → chọn MLE".
- **Lỗi cú pháp tại biên mask:** MaskGAN "struggles to produce syntactically correct sequences" ở chỗ nối giữa phần điền và phần giữ nguyên. [`Asset\Total_OCR1\Fedus_2018_MaskGAN.md:865-871`](..\Asset\Total_OCR1\Fedus_2018_MaskGAN.md) → với SQLi, lỗi biên = **payload sai cú pháp / không relex được**. ⇒ evaluator round-trip của Phase 03 phải kiểm *đặc biệt vùng biên slot*.
- **n-gram là proxy gây hiểu lầm:** tối ưu 4-gram metric có thể đánh đổi sụp perplexity → mẫu lặp lại. [`Asset\Total_OCR1\Fedus_2018_MaskGAN.md:887-905`](..\Asset\Total_OCR1\Fedus_2018_MaskGAN.md) → củng cố PB5 của `02` (sub-metric floor, chống bù trừ).
- MaskGAN dùng **actor-critic/REINFORCE**, không Gumbel; thời điểm đó "Gumbel chưa cho kết quả mạnh". [`Asset\Total_OCR1\Fedus_2018_MaskGAN.md:114-116`](..\Asset\Total_OCR1\Fedus_2018_MaskGAN.md) RelGAN (2019) mới lật được điều này → kết hợp **masked in-filling (MaskGAN) + Gumbel (RelGAN)** là tổ hợp *chưa có paper nào trong corpus làm sẵn* → đây có thể là **góc novelty thật** của nhánh.

---

## 3. GSQLi (Le 2024): tiền lệ domain **giải trực tiếp rủi ro PB2** của `02`

Đây là phát hiện quan trọng nhất của lượt đọc này. `02` cảnh báo: slot Phase 4 toàn literal → masked-surgery có thể rỗng tín hiệu adversarial (PB2). **GSQLi cho thấy cách lấy slot non-literal và đã chạy được:**

- **Không sinh full-sequence — sinh "mutation action" áp lên payload gốc** qua Payload Transformer. [`Asset\Total_OCR1\Le_2024_GSQLi.md:147-165`](..\Asset\Total_OCR1\Le_2024_GSQLi.md) ⇒ chính là **S2 tamper-action** mà `00` F.07 coi là phương án dự phòng — thực ra nó là *con đường chính đã được công bố*.
- **Token taxonomy phi-literal qua Libinjection:** token chia thành characters, numbers, **keywords, operations, expressions, strings, comments, functions, barewords**. [`Asset\Total_OCR1\Le_2024_GSQLi.md:167-170`](..\Asset\Total_OCR1\Le_2024_GSQLi.md) [`Asset\Total_OCR1\Le_2024_GSQLi.md:299-301`](..\Asset\Total_OCR1\Le_2024_GSQLi.md) → đây **chính xác** là loại slot operator/comment/function mà delex Phase 4 của ta thiếu. Giải pháp: chạy Libinjection trong Phase 04.
- **Action vocabulary giữ-semantic cụ thể** (Table II): Case swap (`UNION→uNIoN`), Inline comment (`/*!UNION*/`), Where injection (`id=2 → TRUE and id=2`), Whitespace swap, Logical operator swap (`and→&&`), Compare operator swap (`1=2 → 1 LIKE 2`), Number encoding (`10=1 → 0xA=0x1`), String encoding (`admin → 0x61646D696E`), Logic constant. "preserve their functionality and logic". [`Asset\Total_OCR1\Le_2024_GSQLi.md:329-360`](..\Asset\Total_OCR1\Le_2024_GSQLi.md) [`Asset\Total_OCR1\Le_2024_GSQLi.md:272-273`](..\Asset\Total_OCR1\Le_2024_GSQLi.md) → action set sẵn dùng cho nhánh.
- **Conditional GAN nhẹ, loss CE (không WGAN-GP):** G(noise ⊕ mutation_vector) → actions; D(mutation_vector ⊕ actions) → nhãn; `LG = CE(y0, D(v,a))`, `LD = CE(yc, D(v,a))`. [`Asset\Total_OCR1\Le_2024_GSQLi.md:240-264`](..\Asset\Total_OCR1\Le_2024_GSQLi.md) Mutation Vector = 15 đặc trưng đếm (UNION/WHERE/space/comment/function/bareword...). [`Asset\Total_OCR1\Le_2024_GSQLi.md:184-233`](..\Asset\Total_OCR1\Le_2024_GSQLi.md)
- **Cực nhẹ — chạy CPU.** G = Dense 512→256→128→a; D = Dense 256→128→64→2; máy 6 CPU core, 32GB RAM, **không cần GPU**. [`Asset\Total_OCR1\Le_2024_GSQLi.md:296-308`](..\Asset\Total_OCR1\Le_2024_GSQLi.md) [`Asset\Total_OCR1\Le_2024_GSQLi.md:361-408`](..\Asset\Total_OCR1\Le_2024_GSQLi.md) ⇒ **gỡ bỏ lo ngại 6GB**: action-GAN là mô hình bé tí, RTX 3050 thừa sức.

### 3.1 Phản biện GSQLi (để không sao chép mù)

- **Reward = detector/classifier** ("Attack Classifier" CNN gán nhãn cho D). [`Asset\Total_OCR1\Le_2024_GSQLi.md:286-294`](..\Asset\Total_OCR1\Le_2024_GSQLi.md) → đây đúng là **reward-hacking risk** mà guiding nội bộ ta cảnh báo: tối ưu để qua detector ≠ payload còn tấn công được. GSQLi *giả định* action giữ functionality nhưng **không đo execution-validity** trong vòng lặp. ⇒ Nếu mượn GSQLi, **bắt buộc bọc evaluator thực thi (Phase 03)** trước khi tính reward bypass, và đo diversity/collapse (GSQLi không báo các metric này).
- GSQLi giới hạn payload < 100 ký tự (giới hạn Libinjection). [`Asset\Total_OCR1\Le_2024_GSQLi.md:317`](..\Asset\Total_OCR1\Le_2024_GSQLi.md) → cần kiểm payload dài trong corpus ta.

---

## 4. Tổng hợp: 3 paper thay đổi gì trong kế hoạch nhánh

| Vấn đề trong `00/02` | Paper giải/đổi | Hành động cụ thể |
|---|---|---|
| PB2: slot toàn literal → adv rỗng | **GSQLi** dùng Libinjection → có slot keyword/operator/comment/function | Phase 04 tích hợp Libinjection; **S2 tamper-action là đường chính**, không phải dự phòng |
| PB1: Gumbel ≠ chống collapse | **RelGAN** cho thấy combo (RM+RSGAN+S=64+β tăng dần+pretrain) mới chạy | Đặt tên đóng góp = masked-surgery; thêm RSGAN/hinge loss + lịch β **tăng dần** (không giảm τ nhanh như Phase 2) |
| Lo ngại 6GB | **GSQLi** chạy CPU với dense nhỏ | Action-GAN bé → 6GB dư; có thể chạy multi-seed thoải mái |
| Masked-surgery có cứu collapse? | **MaskGAN** giảm D-saturation NHƯNG vẫn thua MLE diversity (88.2<92.6) | Giữ gate "tie→MLE"; đo round-trip *ở biên slot*; sub-metric floor |
| D thiết kế thế nào | **MaskGAN** (D cần ngữ cảnh thật) + **RelGAN** (S biểu diễn) | paired-D nhận khung+condition thật; thử multi-representation |
| Novelty thật ở đâu | MaskGAN(in-fill)+RelGAN(Gumbel) chưa ai ghép; GSQLi chưa có diversity/exec-gate | Đóng góp = **masked/action surgery + Gumbel + evaluator thực thi + diversity gate** — lấp đúng chỗ trống 3 paper để hở |

**Lịch nhiệt độ đề xuất (sửa theo RelGAN, thay con số Phase 2):** dùng inverse-temperature **tăng dần** `βn=βmax^(n/N)` với `βmax∈[100,1000]` (tương đương giữ τ *mềm* lâu rồi mới sắc), thay vì giảm τ 0.91→0.37 như Phase 2 đã làm và đã collapse. [`Asset\Total_OCR1\Nie_2019_RelGAN.md:284-291`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) [`Guiding\Phase 2\eval\gan_results.json:80-87`](..\Guiding\Phase%202\eval\gan_results.json)

---

## 5. Cập nhật đánh giá khả thi (sau khi đọc paper)

| Mục tiêu | `02` | `03` (sau paper) | Lý do đổi |
|---|---:|---:|---|
| Prototype chạy trên 6GB | 0.70 | **0.85** | GSQLi chứng minh action-GAN chạy CPU; 6GB dư. [`Asset\Total_OCR1\Le_2024_GSQLi.md:296-308`](..\Asset\Total_OCR1\Le_2024_GSQLi.md) |
| Có slot non-literal (giải PB2) | (rủi ro) | **0.75** | Libinjection cung cấp taxonomy; action set có sẵn. [`Asset\Total_OCR1\Le_2024_GSQLi.md:167-170`](..\Asset\Total_OCR1\Le_2024_GSQLi.md) |
| adv thắng anchor-only (G1) | 0.40 | **0.45** | GSQLi cho thấy bypass tăng được; nhưng MaskGAN cảnh báo diversity vẫn có thể thua. |
| Phá tradeoff diversity (G2) | 0.35 | **0.35** | MaskGAN: in-fill **vẫn** thua MLE quadgram (88.2<92.6). [`Asset\Total_OCR1\Fedus_2018_MaskGAN.md:443-462`](..\Asset\Total_OCR1\Fedus_2018_MaskGAN.md) |
| Không lặp collapse Phase 2 | — | **0.70** | Hiểu rõ nguyên nhân (τ sai chiều) + có lịch β đúng từ RelGAN. |

> **Kết luận nhánh (cập nhật):** sau khi đọc paper, **độ khả thi kỹ thuật của nhánh Gumbel tăng rõ** — chủ yếu nhờ GSQLi (giải PB2 + gỡ lo 6GB) và RelGAN (chẩn đoán đúng lịch nhiệt độ). Rủi ro còn lại **không phải "chạy được hay không"** mà là "**có thắng MLE về đa dạng không**" — và MaskGAN nói thẳng là *có thể không*. Vì vậy giữ nguyên khung "sống sót mọi kết cục": ngay cả khi thua MLE, đóng góp = *masked/action-surgery + Gumbel + evaluator thực thi + diversity gate* (tổ hợp chưa paper nào trong corpus làm trọn).
