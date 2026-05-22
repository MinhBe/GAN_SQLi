# 11 — Phản biện kế hoạch triển khai (nhánh Gumbel Action-Surgery)

> **Ngày:** 2026-05-22 · **Vai trò:** đánh giá phản biện *bộ kế hoạch 00–10* trong thư mục này. Kế hoạch đã hấp thụ tốt các phản biện ở `../02` và `../03`; vì vậy file này tìm **lớp vấn đề tiếp theo** — những điểm còn tồn đọng, cần làm lại, hoặc cần xem xét. Mỗi vấn đề kèm **tối thiểu 5 nguyên nhân & góc nhìn**.
> Quy ước trích dẫn: file cùng thư mục ghi `0X_*.md:dòng`; dữ liệu nội bộ ghi `..\..\Guiding\...`.

---

## Nhận xét tổng quan (mặt được)

Kế hoạch mạnh ở: (1) tách đúng centerpiece (action-surgery) khỏi "Gumbel chống collapse" [`00_Tong_Quan_Kien_Truc_Gumbel_Action_Surgery.md:84-96`](00_Tong_Quan_Kien_Truc_Gumbel_Action_Surgery.md); (2) đặt G0 slot/action audit làm cổng cứng [`01_Data_Reality_Check_And_Slot_Audit.md:76-94`](01_Data_Reality_Check_And_Slot_Audit.md); (3) D-as-scorer là deliverable dương độc lập [`07_MLE_Anchor_And_D_Scorer.md:42-65`](07_MLE_Anchor_And_D_Scorer.md); (4) kỷ luật multi-seed/anti-cherry-pick. Sáu vấn đề dưới đây là **chỗ kế hoạch chưa đứng vững**.

---

## VĐ-1 — Phase 04 là một *siêu dự án* bị nén vào một ô, và toàn kế hoạch **không có ngân sách thời gian/compute**

Phase 04 yêu cầu cùng lúc: `canonical_action_view`, `libinjection_token_view`, `tamper_action_candidates`, `action_equivalence_rules`, `dialect_compatibility_tags`, `round_trip_action_map`, `near_dup_action_clusters` [`04_Full_Data_Foundation_Action_Taxonomy.md:16-57`](04_Full_Data_Foundation_Action_Taxonomy.md). Đây không phải một phase, đây là 6–7 tiểu dự án. Cần làm lại: tách Phase 04 thành các sub-phase có deliverable riêng + gắn ước lượng.

**Nguyên nhân & góc nhìn:**
1. **Trộn ML với công việc thủ công ngôn ngữ học:** `action_equivalence_rules` và `dialect_compatibility_tags` là tri thức domain (tính đúng-ngữ-nghĩa của phép biến đổi), phải làm tay/kiểm chứng, không train được — dễ bị đánh giá thấp công sức nhất.
2. **Quy mô tính toán:** áp action + round-trip trên nền `12,753,953` dòng [`..\..\Guiding\Phase 4\outputs\full\04_data_foundation_report.md:4`](..\..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) là rất nặng; kế hoạch không nêu chiến lược lấy mẫu/giới hạn.
3. **Không có ước lượng person-day/GPU-hour ở bất kỳ phase nào** → không thể biết nhánh có vừa thời hạn luận văn không (khác hẳn `Guiding/Mục lục` V5 vốn có tham chiếu ~4h17m/đợt).
4. **Không có ranh giới "MVP slice" vs "full":** rủi ro cầu toàn ở nền dữ liệu (Phase 01/04) đến mức không bao giờ tới được phase mô hình.
5. **Phụ thuộc công cụ ngoài chưa kiểm:** Libinjection giới hạn payload < 100 ký tự trong GSQLi [`..\03_Phan_Tich_Sau_Tu_Paper.md:64-67`](..\03_Phan_Tich_Sau_Tu_Paper.md); chưa biết bao nhiêu payload corpus vượt ngưỡng đó → có thể mất một phần dữ liệu.
6. **Cạnh tranh nguồn lực:** cùng một người, cùng 6GB, kế hoạch chưa nêu rõ thứ tự ưu tiên giữa nền V5, audit dữ liệu, evaluator và training action-GAN.

---

## VĐ-2 — Vòng phụ thuộc ngược: nhiều gate đòi `round_trip_success` *trước khi* evaluator (Phase 06) tồn tại, và bản thân round-trip chưa được định nghĩa/kiểm định

Phase 01 và 02 đã gate theo round-trip [`01_Data_Reality_Check_And_Slot_Audit.md:82-84`](01_Data_Reality_Check_And_Slot_Audit.md) [`02_De_Risk_Action_Surgery_Slice.md:74-76`](02_De_Risk_Action_Surgery_Slice.md), nhưng evaluator được dựng ở Phase 06 [`06_Evaluator_And_Model_Separation.md:20-29`](06_Evaluator_And_Model_Separation.md), và Phase 4 nội bộ ghi `round_trip_status=not_evaluated` [`..\..\Guiding\Phase 4\outputs\full\04_data_foundation_report.md:72`](..\..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md). Cần xem xét lại thứ tự + định nghĩa round-trip *cho action* trước khi dùng nó làm gate.

**Nguyên nhân & góc nhìn:**
1. **Đảo thứ tự phụ thuộc:** không thể gate Phase 01/02/04 bằng một metric mà công cụ tính nó (Phase 06) chưa ra đời.
2. **Round-trip của action ≠ round-trip của delex:** "áp action → đảo action → ra payload gốc" là định nghĩa khác với "delex → refill = gốc"; kế hoạch chưa định nghĩa.
3. **Thiếu tập calibration known-valid/known-broken:** không có bộ mẫu chuẩn để *kiểm định chính cái round-trip checker* → gate dựa trên một thước đo chưa được hiệu chuẩn.
4. **Parser có thể "thành công" trên payload hỏng:** sqlparse/Libinjection vẫn parse ra cây cho chuỗi vô nghĩa → round-trip dương tính giả.
5. **Gộp hai khái niệm:** "action đảo ngược được" (tính kỹ thuật) bị trộn với "action giữ ngữ nghĩa tấn công" (tính semantic) — hai thứ rất khác, cần hai metric.
6. **Không có giao thức human spot-check** để xác nhận metric tự động khớp đánh giá người, dù `02` đã nhấn mạnh proxy có thể đánh lừa.

---

## VĐ-3 — **Nguồn tín hiệu adversarial chưa được giải quyết:** paired-D phân biệt "real vs generated", nhưng "real action-mutation" lấy ở đâu?

Phase 07/08 dùng `PairedActionDiscriminator` nhận `(base_payload, mutated_payload, action_trace, condition)` [`08_Gumbel_Action_Surgery_GAN.md:60-75`](08_Gumbel_Action_Surgery_GAN.md). Nhưng corpus là *payload đơn lẻ*, không phải cặp (gốc → biến thể) kèm action-trace thật. GSQLi né điều này bằng cách lấy **detector làm reward** (bypass = thắng) [`..\03_Phan_Tich_Sau_Tu_Paper.md:64-67`](..\03_Phan_Tich_Sau_Tu_Paper.md); kế hoạch đã bỏ tín hiệu đó nhưng chưa thay bằng cái tương đương. Cần xem xét lại: lớp "real" của D là gì, và mục tiêu bảo mật (evade WAF) còn nằm ở đâu.

**Nguyên nhân & góc nhìn:**
1. **Không có cặp ground-truth (base→mutated):** dataset không chứa action-trace thật → lớp "real" của paired-D không xác định được.
2. **Nếu "real" = payload corpus gốc, "fake" = payload do model biến thể:** D dễ học "văn phong người vs văn phong model" (artifact phân phối), *không* học chất lượng action.
3. **Action-trace của payload thật không tồn tại:** payload corpus không do hệ action của ta sinh ra → không thể trích trace để feed D như mô tả.
4. **Mất ý nghĩa bảo mật:** mục tiêu gốc của nhánh là *né WAF/detector*; bỏ reward-từ-detector mà không thay thế khiến adversarial không còn đo "tránh phát hiện" — chỉ còn đo "giống corpus".
5. **Phép loại suy MaskGAN gãy một nửa:** MaskGAN cho D ngữ cảnh thật vì *real in-fill có trong corpus* [`..\03_Phan_Tich_Sau_Tu_Paper.md:36-41`](..\03_Phan_Tich_Sau_Tu_Paper.md); ở đây "real action-fill" có thể không tồn tại.
6. **Rủi ro D-shortcut mới:** D có thể chỉ học "đây có phải dạng canonical của corpus không" thay vì "đây có phải mutation tấn công tốt không" — đúng loại shortcut Phase 07 muốn chẩn đoán [`07_MLE_Anchor_And_D_Scorer.md:70-79`](07_MLE_Anchor_And_D_Scorer.md) nhưng nguyên nhân nằm ở thiết kế dữ liệu, không phải ở D.

---

## VĐ-4 — "Pre-registered gate" nhưng ngưỡng phần lớn để trống ("ngưỡng đăng ký") → tự vô hiệu hóa mục đích chống cherry-pick

Hầu hết gate ghi `>= ngưỡng đăng ký` mà không cam kết con số: Phase 03 [`03_Decision_Gate.md:40-50`](03_Decision_Gate.md), Phase 04 [`04_Full_Data_Foundation_Action_Taxonomy.md:91-97`](04_Full_Data_Foundation_Action_Taxonomy.md). Một pre-registration với ngưỡng trống thì không phải pre-registration. Cần làm lại: cam kết **thủ tục đặt ngưỡng** (kể cả khi chưa có số) trước khi thấy kết quả GAN.

**Nguyên nhân & góc nhìn:**
1. **Mâu thuẫn mục đích:** gate "đăng ký trước" với ngưỡng TBD vẫn cho phép đặt ngưỡng *sau khi* nhìn kết quả — chính cherry-picking mà kế hoạch tuyên bố chống [`03_Decision_Gate.md:102-104`](03_Decision_Gate.md).
2. **Chưa có baseline nên chưa có số — nhưng vẫn có thể cam kết thủ tục:** ví dụ "ngưỡng = anchor-only trên dev, khóa trước khi train GAN"; kế hoạch chưa nêu thủ tục này.
3. **"Frontier đã đăng ký" được nhắc nhiều lần** [`03_Decision_Gate.md:44`](03_Decision_Gate.md) [`08_Gumbel_Action_Surgery_GAN.md:156`](08_Gumbel_Action_Surgery_GAN.md) nhưng **trục và điểm của frontier chưa từng được liệt kê**.
4. **Thiếu định nghĩa "thắng":** "H4 > H3" — hơn bao nhiêu? CI không chồng lấn? hay chỉ mean lớn hơn? Không nói → dễ tuyên thắng bằng chênh lệch vô nghĩa.
5. **Không hiệu chỉnh đa so sánh:** rất nhiều sub-metric × nhiều seed × nhiều H → xác suất dương tính giả cao nếu không Bonferroni/Holm.
6. **Thiếu ngưỡng effect-size:** phân biệt "có ý nghĩa thống kê" với "có ý nghĩa thực tiễn" — chưa có.

---

## VĐ-5 — Kết luận "6GB không còn là vấn đề" có thể là **overclaim**: kiến trúc thực tế nặng hơn GSQLi nhiều

`00`/`03` kết luận 6GB dư vì GSQLi chạy CPU [`..\03_Phan_Tich_Sau_Tu_Paper.md:64-67`](..\03_Phan_Tich_Sau_Tu_Paper.md). Nhưng GSQLi nhẹ vì nó là **dense net trên vector mutation 15-chiều cố định**. Generator của kế hoạch lại nhận `payload_action_frame + condition embedding + action history`, xuất phân phối action-family + argument + stop/continue [`08_Gumbel_Action_Surgery_GAN.md:28-49`](08_Gumbel_Action_Surgery_GAN.md) — tức **mô hình chuỗi** + encoder khung + paired-D trên hai payload. Cần xem xét lại: tính nhẹ của GSQLi *không* tự động chuyển sang kiến trúc này.

**Nguyên nhân & góc nhìn:**
1. **Khác lớp độ phức tạp:** GSQLi = vector cố định + dense; kế hoạch = sinh action *tuần tự* có `action history` → quay lại chế độ mô hình chuỗi mà nhánh tưởng đã tránh.
2. **`action history` ⇒ autoregressive:** sinh action theo bước = decoder chuỗi = đúng vùng tốn kém.
3. **Paired-D mã hóa 2 payload + trace** [`08_Gumbel_Action_Surgery_GAN.md:68-75`](08_Gumbel_Action_Surgery_GAN.md): nặng hơn `D(v,a)` của GSQLi nhiều.
4. **Encoder khung payload** gần như cần embedding/LSTM/Transformer → tái nhập chi phí mà kế hoạch tuyên bố đã loại.
5. **Không có ngân sách VRAM smoke-test cho kiến trúc thực tế:** chỉ nói "runtime_VRAM" như một metric [`02_De_Risk_Action_Surgery_Slice.md:64`](02_De_Risk_Action_Surgery_Slice.md) chứ chưa cam kết "< 6GB ở cấu hình X".
6. **Lập luận trộn hai mệnh đề:** "một action-GAN *có thể* nhỏ" (đúng cho GSQLi) bị dùng thay cho "action-GAN *này* nhỏ" (chưa kiểm chứng).

---

## VĐ-6 — Chưa hòa giải **quy mô dữ liệu**: 38.906 dòng slice (ở `00/01` gốc) vs 12.753.953 dòng (Phase 4) vs nhãn 30,58% → tập train thực tế chưa bao giờ được tính

Kế hoạch dùng nền 12,7M [`04_Full_Data_Foundation_Action_Taxonomy.md:8-9`](04_Full_Data_Foundation_Action_Taxonomy.md) nhưng nhãn chỉ phủ `30.5788%` [`05_Label_And_Condition_System.md:10-11`](05_Label_And_Condition_System.md) và verified chỉ 504/468 [`05_Label_And_Condition_System.md:9`](05_Label_And_Condition_System.md). Action-surgery cần đồng thời *payload sạch* ∩ *có condition* ∩ *có slot non-literal*. Cần xác định: tập train hữu hiệu sau giao nhau là bao nhiêu.

**Nguyên nhân & góc nhìn:**
1. **Hai thang dữ liệu chưa nối:** 38.906 (slice gán nhãn ở tài liệu trước) vs 12.753.953 (foundation) — phase nào dùng cái nào không rõ.
2. **Giao nhãn × sạch × có-slot chưa từng được ước cỡ:** đây mới là tập train thật của GAN, và nó có thể nhỏ hơn nhiều con số 12,7M.
3. **Lane N chiếm 99.965%** [`..\..\Guiding\Phase 4\outputs\full\04_data_foundation_report.md:9-15`](..\..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md): action-surgery train trên lane N hay toàn bộ? Không nói.
4. **Ô (technique × db × action_family) sẽ rỗng nhiều:** với verified 504/468, chia theo nhiều chiều điều kiện → nhiều ô không có mẫu test.
5. **Hai hệ near-dup cluster:** clustering ở 12,7M vs ở slice — metric novelty của GAN dựa trên cái nào?
6. **Class hiếm có thể biến mất sau giao:** `error_based` vốn đã hiếm (theo `00` D.3); sau khi giao với "có action slot + verified", có thể còn quá ít để claim controllability cho lớp đó.

---

## Vấn đề xuyên suốt của nhánh Gumbel

1. **Nhiều việc lớn song song, một người, một 6GB:** nền V5 + audit dữ liệu + evaluator + action-GAN; không có tài liệu phân bổ ưu tiên/lịch giữa chúng → rủi ro không hoàn thành cái nào.
2. **Lỗi đảo thứ tự evaluator:** gate dùng metric trước khi Phase 06 dựng evaluator.
3. **Ngưỡng để trống** ("ngưỡng đăng ký") → cần một tài liệu *threshold-setting protocol* cho riêng nhánh Gumbel.
4. **"Tái dùng nền V5" được nói lỏng:** chưa có hợp đồng artifact dùng chung (tên file, schema, version) giữa V5 và Gumbel → dễ lệch phiên bản.
5. **Chưa có tiêu chí dừng cả nhánh:** mỗi phase có stop-rule, nhưng không có điều kiện "bỏ nhánh Gumbel để dồn cho cái khác" nếu G0 hoặc slice thất bại sớm.

---

## Tóm tắt việc cần làm lại / xem xét (theo độ ưu tiên)

```text
P0  Tách Phase 04 thành sub-phase + gắn ước lượng compute/person-day (VĐ-1)
P0  Định nghĩa & hiệu chuẩn round-trip-cho-action TRƯỚC khi dùng làm gate; sửa thứ tự Phase 06 (VĐ-2)
P0  Giải quyết nguồn "real" cho paired-D, hoặc khôi phục tín hiệu detector có bọc evaluator (VĐ-3)
P1  Viết threshold-setting protocol (đặt ngưỡng từ anchor-only/dev, khóa trước train) (VĐ-4)
P1  Smoke-test VRAM kiến trúc thực tế; nếu vượt 6GB, rút về dense-action kiểu GSQLi (VĐ-5)
P1  Ước cỡ tập train hữu hiệu sau giao (sạch ∩ condition ∩ slot); báo ô rỗng (VĐ-6)
P2  Tài liệu phân bổ nguồn lực 3 nhánh + hợp đồng artifact dùng chung
```
