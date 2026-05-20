# Recovery — Công đoạn gán nhãn SQLi (Testing_1)

> Ngày: 2026-05-20 | Mục đích: đúc kết vì sao lần gán nhãn "AI-only" không cho ra AI thật, trạng thái hiện tại, và các đường đi khả thi.

## 1. Chuyện gì đã xảy ra

- Đã viết bản plan "AI-only labeling" (`deep-research-report.md`), upload cho ChatGPT cùng `final_dataset_1(1).csv` (1.084.880 dòng).
- ChatGPT tạo ra `final_dataset_1_ai_only_labeled.csv` (46 cột, 1.08M dòng) + summary.
- **Nhưng metadata trong file tự thú nhận:**
  - `model_version = static_evidence_labeler_v1_no_trained_model`
  - `label_source  = static_evidence_pipeline_from_uploaded_plan`
- Tức là: **không có mô hình AI nào**. Toàn bộ nhãn do **regex/heuristic tĩnh** sinh ra. "AI-only" chỉ là tên file.

## 2. Vì sao ChatGPT chuyển từ "AI" sang script — 3 bức tường

1. **Môi trường:** ChatGPT chạy trong sandbox code-interpreter, không có model SQLi train sẵn để load, không gọi LLM-per-row cho 1M dòng được. Cái duy nhất chạy được là regex.
2. **Bản plan tự cấm:** chính `deep-research-report.md` viết "không khuyên dùng generative LLM cho từng dòng... dùng template để throughput cao" → ChatGPT tuân theo phần thực thi.
3. **Thiếu nguyên liệu:** không có model train sẵn, cũng không có ground-truth để train. Không có gì để instantiate "AI".

→ Bài học cốt lõi: **"AI-only" là một cái tên, chưa bao giờ là kiến trúc.** Plan không trả lời "model AI từ đâu ra, train trên dữ liệu nào".

## 3. Đánh giá kết quả thực tế (bằng số)

| Chỉ số | Giá trị | Nhận định |
|---|---|---|
| is_sqli=0 (benign) | 928.954 (85.6%) | Phần lớn là "không khớp rule → benign", KHÔNG phải verified benign. Nguy hiểm hơn "75.7% unknown" của v3.1 vì đội lốt nhãn sạch. |
| primary blind types | time_blind+boolean_blind = 69% SQLi | Mode collapse đổi đỉnh (v3.1 là union 48.5%). Rule mạnh ở `sleep`/`waitfor` nên dồn nhãn. |
| db_engine=unknown | 92.3% | DB fingerprinting gần như sụp đổ. |
| confidence_band=high | 1.670 (0.15%) | Hầu như không có dòng nào chắc chắn. "Reviewer đỡ cực" thất bại. |
| review_priority 2–3 | 99.7% | Gần như mọi dòng đều "cần review". |

**Phát hiện kèm theo:**
- Dataset đã **delexicalize** (token `__TIME__`, tách token) → CHAR decoder, multi-view, obfuscation_score phần lớn vô dụng. `char(` chỉ ~0.005%.
- Dữ liệu **gần như không trùng lặp** (300K mẫu → 299.998 unique) → KHÔNG có lối tắt dedup.
- **File local bị cắt cụt:** bản trên đĩa ~300K dòng (232MB), bản sandbox đầy đủ 1.08M dòng (818MB) chưa tải về hết. → Cần tải lại bản đầy đủ.
- False positive cụ thể: `create user ... ;` (DDL hợp lệ) bị gán `stacked_queries` chỉ vì có dấu `;`.

## 4. Nút thắt thật sự

Mục tiêu "AI đọc & đánh giá từng dòng" cho 16M dòng, với công cụ hiện có (**chỉ ChatGPT Plus, không API, không train**), là **bất khả thi về toán học**:

- Ô chat đọc kỹ ~50–100 dòng/tin nhắn.
- 1.08M ÷ 100 = ~10.800 tin nhắn (chỉ d1); cả 15 file = ~160.000 tin nhắn dán tay.
- Yêu cầu ChatGPT "xử lý cả file" → nó lại viết regex (đúng cái đã xảy ra).

→ ChatGPT Plus chỉ AI-label được **vài nghìn dòng** (dán theo lô). Đó là trần cứng.

## 5. Thế chân vạc — phải nới đúng MỘT ràng buộc

3 ràng buộc *(chỉ chat-UI, không API, không train)* không thể cùng tồn tại với mục tiêu *AI-label toàn bộ 16M*:

| Buông cái nào | Được gì | Chi phí |
|---|---|---|
| Buông "không API" | GPT đọc thật từng dòng cả 16M qua Batch API | ~70–140$ cho d1 (tiền thật) |
| Buông "không train" | GPT đọc vài nghìn dòng (qua ChatGPT Plus) → model nhỏ bắt chước GPT để phủ 16M miễn phí | 0đ |
| Buông "label toàn bộ" | GPT chỉ đọc một mẫu để kiểm toán/sửa rule; phần lớn giữ rule-label | 0đ |

## 6. Khuyến nghị

- Nếu không trả tiền API: chọn **buông "không train"** — đây là cách duy nhất phủ AI-derived label lên toàn bộ 16M miễn phí. GPT vẫn là bộ não (label seed), model nhỏ chỉ là cánh tay nhân bản. "Train" ở đây = một máy photo học bắt chước phán đoán GPT.
- Trước mọi thứ: **tải lại bản labeled đầy đủ 1.08M dòng** (bản local đang cụt 300K).
- Sửa taxonomy: `db_fingerprint`, `metadata_enumeration` là kỹ thuật phụ trợ → nên nằm trong `attack_tags`, không phải `primary_sqli_type`.
- Quyết định chưa chốt: **GAN sẽ sinh payload delex hay raw?** → quyết định luôn dataset đầu vào và schema.

## 7. Quyết định cần người dùng chốt

- [ ] Nới ràng buộc nào (mục 5)?
- [ ] GAN sinh delex hay raw?
- [ ] Có chấp nhận chi phí API không?

---

# Phần II — Phiên rà soát & chốt hướng (2026-05-20, tiếp)

> Tổng hợp buổi làm việc sau khi đọc lại recovery.md ở trên: phân tích chất lượng label, chốt 3 quyết định còn treo, dựng kế hoạch mới, và ghi nhận sự cố bàn giao cloud.

## 8. Làm rõ: có HAI "phương án cũ" khác nhau (đừng gộp)

| Phương án | File sinh ra | Đánh giá |
|---|---|---|
| **Cascade v2** (`Skill/label-sqli/`) | `labeled.csv` (18 cột) | Engine rule 4 tier **thiết kế tử tế** — state-aware, có Pass 2 AI review, checkpoint, calibrator. Đây là engine thật. |
| **"AI-only"** (`deep-research-report.md`) | `final_dataset_1_ai_only_labeled.csv` (44 cột) | Chính là cái recovery.md (Phần I) mổ xẻ: regex tĩnh đội lốt AI. **Hỏng.** |

→ recovery.md Phần I phê phán đúng phương án "AI-only", KHÔNG phải cascade v2.

## 9. Phát hiện then chốt: nhiều triệu chứng tệ là do gán nhãn trên DELEX

Khảo sát lại cho thấy ~3/5 triệu chứng tệ nhất của bản 44 cột **là hệ quả của việc chạy trên dữ liệu DELEX**, không phải lỗi engine:

| Triệu chứng | Vì sao là do delex |
|---|---|
| db_engine=unknown 92.3% | Tên hàm đặc trưng DB đã bị token hóa → fingerprint không còn gì để bắt |
| obf_*, CHAR decoder vô dụng | `0x...`, `char(`, `%27` đã bị xóa khi delex |
| Một phần benign giả | Token hóa làm mất tín hiệu tấn công |

→ **Chuyển sang RAW sẽ tự động hồi sinh db-fingerprint và obfuscation features.** Đây là lý do mạnh để gán nhãn trên raw, độc lập với nhu cầu của GAN.

## 10. Dữ liệu RAW có sẵn (trả lời mục 35 Phần I)

- Nguồn RAW: `Asset/LabelData/Dataset Source/rbsqli_dataset_[1-15].csv` (~1.05M dòng) + `payload_full.csv` (31K), `csic_ecml_final.csv` (85K), `BCCC-SFU-SQLInj-2023.csv` (11K), SQLiV5. Tổng ~1.1M raw.
- `final_dataset*.csv` (12.7M, 1.34GB) chính là bản **delex** của các nguồn này → KHÔNG dùng cho GAN-raw.
- File nhãn: `labeled.csv` (18 cột, delex), `final_dataset_1_ai_only_labeled.csv` (44 cột, delex, hỏng). Cả hai đều delex → đều lệch hướng cho GAN-raw.

## 11. Ý tưởng mới của người dùng (đã chốt) — AI là VERIFIER, không phải GENERATOR

> "Dùng code để đánh nhãn tay, sau rồi chỉ để AI đánh nhãn lại xem có đúng kiểu tấn công, chỉ 1 label thì sao?"

- Code/rule (cascade v2) gán nhãn hàng loạt.
- AI chỉ trả lời **một câu hỏi nhị phân trên một nhãn duy nhất** (`primary_sqli_type`): "kiểu tấn công này đúng/sai? nếu sai thì là gì?".
- Đây là **distillation của tác vụ kiểm tra**, sạch hơn nhiều so với distillation việc sinh nhãn (vốn là cái đã thất bại).

## 12. Ba quyết định còn treo (mục 7 Phần I) → ĐÃ CHỐT

| Quyết định | Lựa chọn |
|---|---|
| Nới ràng buộc nào | **Buông "không train"** — AI verify vài nghìn dòng → train model nhỏ bắt chước vai verifier, phủ toàn bộ miễn phí |
| GAN sinh delex hay raw | **RAW** → gán nhãn trên nguồn raw, bỏ delex |
| Chấp nhận chi phí API | Không (đi đường miễn phí: chat-UI + model nhỏ) |

## 13. Kế hoạch mới (6 bước) — đã lưu ở plan file

Plan đầy đủ: `C:\Users\Admin\.claude\plans\c-users-admin-documents-gan-sqli-asset-l-tranquil-moler.md`

1. **Dựng corpus RAW** — gộp rbsqli + nguồn raw về 1 cột `payload_raw`, dedup theo hash → `data/raw/raw_corpus.csv`. (script mới `build_raw_corpus.py`)
2. **Pass 1 — code gán nhãn hàng loạt trên RAW** — chạy `run_labeling.py --detector_only`, trọng tâm `primary_sqli_type`.
3. **Pass 2 — AI VERIFY một nhãn** — chỉnh `ai_reviewer.py` thành prompt verify (`{idx, agree, correct_type}`); chọn mẫu ~3–5K bằng `gold_set_creator` stratified → seed verified (qua ChatGPT Plus, không API).
4. **Train model nhỏ làm verifier** — `train_verifier.py` học từ seed, áp lên toàn bộ; bất đồng mạnh với rule → ghi đè/đẩy về verify. (cánh tay nhân bản phán đoán AI)
5. **Calibrate + chống mode collapse + refine rule** — Platt scaling; ma trận nhầm lẫn theo type; chuyển `db_fingerprint`/`metadata_enumeration` sang `attack_tags`, không nằm trong `primary_sqli_type`.
6. **QA & xuất** — báo cáo phân bố (không collapse, db=unknown giảm mạnh) → `data/processed/sqli_raw_labeled_final.csv`.

**Tái dùng (không viết lại):** `run_labeling.py`, `cascade_labeler.py`, `detectors_v2.py`, `ai_reviewer.py`, `gold_set_creator.py`, `calibrator.py`, `rule_refiner.py`.

**Kiểm chứng:** chạy thử mẫu 10K từ rbsqli → kiểm db_engine có giá trị thực (không ~92% unknown), obf_* không toàn 0; đo tỉ lệ AI đồng ý với rule trên ~200 dòng gold; phân bố cuối không có lớp nào > ~50% và benign không phình như bản cũ (85.6%).

## 14. Sự cố bàn giao cloud (Ultraplan)

- Thử gửi plan tới Ultraplan để refine từ xa → **thất bại: "Repo is too large to teleport"**, gần như chắc do các file CSV delex khổng lồ (riêng `final_dataset.csv` = 1.34GB).
- Khuyến nghị của công cụ: setup GitHub tại https://claude.ai/code. Cảnh báo: nếu CSV lớn đang được git track thì push cũng vượt giới hạn 100MB của GitHub → cần kiểm `.gitignore` và gỡ data lớn khỏi git trước.
- **Quyết định người dùng: triển khai thẳng tại máy local**, không qua cloud.

## 15. Việc cần làm tiếp

- [ ] Bắt đầu Bước 1: dựng `build_raw_corpus.py` và corpus RAW từ rbsqli + nguồn raw.
- [ ] (Tùy chọn) Dọn `.gitignore` để repo nhẹ, phòng khi muốn dùng cloud sau này.
