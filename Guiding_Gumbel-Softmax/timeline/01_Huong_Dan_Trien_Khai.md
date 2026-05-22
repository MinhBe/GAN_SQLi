# Timeline Triển Khai Gumbel-Softmax Action-Surgery

Ngày tạo: 2026-05-22  
Phạm vi: chỉ `Guiding_Gumbel-Softmax`, dùng nền dữ liệu/evaluator từ `Guiding`. Dữ liệu gốc: `C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\FinalDataSet`.

---

## 1. Quyết định triển khai mặc định

Tài liệu này chỉ áp dụng cho nhánh Gumbel-Softmax/action-surgery. Mọi artifact, gate và báo cáo trong file này dùng namespace `gumbel`.

Thứ tự triển khai khuyến nghị:

```text
1. Triển khai Gumbel Action-Surgery trước.
2. Giữ MLE/D-as-scorer làm baseline và đường an toàn.
3. Chỉ mở Gumbel action-GAN sau khi slot/action audit, slice, evaluator và D-as-scorer đã qua gate.
```

Lý do:

- Gumbel/action-surgery đã có đường triển khai thực dụng hơn nhờ GSQLi/action taxonomy và D-as-scorer. [`Guiding_Gumbel-Softmax\03_Phan_Tich_Sau_Tu_Paper.md:54-62`](..\03_Phan_Tich_Sau_Tu_Paper.md)
- SeqGAN/GAN full-sequence cũ đã bị gate loại: `MLE_MAIN`, fail 4/6 gate, `collapse_count=3`, `dominating_pair_count=0`. [`Guiding\Phase 3\eval\phase03\decision.json:2-4`](..\..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 3\eval\phase03\decision.json:79-91`](..\..\Guiding\Phase%203\eval\phase03\decision.json)

---

## 2. File theo dõi tiến độ

Timeline JSON nằm tại:

```text
timeline/timeline_progress.json
```

Mỗi khi hoàn thành hoặc chặn một bước, cập nhật tối thiểu các trường trong JSON:

```text
updated_at
overall_progress.status
overall_progress.progress_percent
overall_progress.active_phase_id
phase.status
phase.progress_percent
phase.evidence_artifacts
phase.gate.current_result
```

Khi phase hoàn tất hoặc bị chặn, cập nhật thêm `overall_progress.last_completed_phase_id`, `overall_progress.next_action`, và `phase.notes` nếu các trường này đổi ý nghĩa. Trong văn bản báo cáo có thể gọi ngắn là `gate_result`, nhưng trong `timeline_progress.json` hiện tại giá trị gate nằm ở `phase.gate.current_result`. Không thêm trường `gate_result` phẳng nếu không đổi schema tracker.

Quy ước `status`:

```text
not_started  : chưa làm
in_progress  : đang làm
blocked      : bị chặn bởi dữ liệu, code, compute, paper hoặc label
completed    : hoàn tất và có artifact
failed       : đã chạy nhưng fail gate
skipped      : bỏ qua có lý do
```

---

## 3. Cấu trúc thư mục triển khai đề xuất

Tạo dần khi bắt đầu code:

```text
data/
  gumbel/
    audit/
    slice/
    full/

models/
  gumbel/
    d_scorer/
    action_gan/

eval/
  gumbel/
    slice/
    phase01/
    phase02/
    phase03/
    final/

reports/
  gumbel/
```

Không tạo hết thư mục ngay: đây là nguyên tắc tránh artifact rỗng, không phải thiếu chuẩn bị. Chỉ tạo khi phase bắt đầu và có artifact thật.

---

## 4. Lộ trình triển khai Gumbel Action-Surgery

### G01 — Slot/Action Audit

Mục tiêu:

```text
Chứng minh dữ liệu là đủ giàu action/slot phi-literal để đi tiếp.
```

Việc cần làm:

```text
1. Đọc Phase 4 canonical/delex/template artifacts.
2. Tích hợp Libinjection hoặc parser tương đương.
3. Đếm slot/action theo family: literal, operator, comment, encoding, function, keyword, whitespace.
4. Báo coverage theo technique × db_hint.
5. Xuất quyết định G0: S1_MASKED_SLOT, S2_TAMPER_ACTION hoặc STOP.
```

Artifact bắt buộc:

```text
reports/gumbel/01_slot_action_audit.md
data/gumbel/audit/action_taxonomy.json
data/gumbel/audit/g0_decision.json
```

Gate:

```text
Pass nếu có đủ non-literal/action signal.
Fail nếu chỉ có literal slot.
Nếu fail literal-only, chuyển S2 tamper-action làm đường chính.
```

Nguồn kế hoạch: [`Guiding_Gumbel-Softmax\Mục lục\01_Data_Reality_Check_And_Slot_Audit.md`](..\Mục%20lục\01_Data_Reality_Check_And_Slot_Audit.md)

---

### G02 — De-risk Action-Surgery Slice

Mục tiêu:

```text
Chạy một lát nhỏ end-to-end trước khi full-scale.
```

Việc cần làm:

```text
1. Chọn subset 5k-10k train, 1k-2k dev/test.
2. Build action-surgery dataset.
3. Round-trip check.
4. Train anchor-only action infiller.
5. Train paired-D nhỏ.
6. Freeze D và chạy D-as-scorer.
7. Chạy Gumbel action-GAN pilot 1 seed nếu các bước trên pass.
```

Artifact:

```text
data/gumbel/slice/action_surgery_train.parquet
eval/gumbel/slice/baseline_comparison.json
reports/gumbel/02_de_risk_action_surgery_slice.md
```

Gate:

```text
round_trip_success >= ngưỡng đăng ký
syntax/parse không tụt dưới floor
anchor+adv phải được so với anchor-only
```

Nguồn kế hoạch: [`Guiding_Gumbel-Softmax\Mục lục\02_De_Risk_Action_Surgery_Slice.md`](..\Mục%20lục\02_De_Risk_Action_Surgery_Slice.md)

---

### G03 — Pre-scale Decision Gate / Slice Decision Gate

Mục tiêu:

```text
Khóa protocol và quyết định có mở rộng từ slice sang full hay không.
```

G03 là gate `scale/no-scale` sau G02 slice, không phải final evaluation. H4 ở đây là Gumbel action-surgery GAN pilot trên slice; G08 vẫn là phase train Gumbel Action-Surgery GAN ở quy mô full/pilot nâng cấp sau G07.

So sánh:

```text
H1 Conditional MLE
H2 MLE + D-as-scorer
H3 anchor-only action infiller
H4 Gumbel action-surgery GAN
H5 rule/tamper baseline
```

Điều kiện pass:

```text
>= 3 seeds, tốt nhất 5 seeds
>= 5k samples/seed
H4 > H3 anchor-only
H4 không thua H2 trong frontier đã đăng ký
không collapse diversity/entropy
không tăng near-copy
```

Artifact:

```text
eval/gumbel/phase03/decision.json
eval/gumbel/phase03/statistical_summary.json
reports/gumbel/03_decision_gate_report.md
```

Nguồn kế hoạch: [`Guiding_Gumbel-Softmax\Mục lục\03_Decision_Gate.md`](..\Mục%20lục\03_Decision_Gate.md)

---

### G04 — Full Data Foundation + Action Taxonomy

Mục tiêu:

```text
Mở rộng action-surgery dataset lên full data nhưng giữ cluster-safe split.
```

Phase 4 hiện đã có `12,753,953` dòng và cluster leakage `0`; mọi split mới phải giữ nguyên điều này. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:4`](..\..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:33`](..\..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

Artifact:

```text
data/gumbel/full/action_foundation.parquet
data/gumbel/full/action_splits.json
reports/gumbel/04_full_data_foundation_action_taxonomy.md
```

---

### G05 — Label/Condition System

Mục tiêu:

```text
Tạo condition đủ sạch cho action generator và evaluator.
```

Không dùng `unknown` như engine thật; `unknown` nghĩa là thiếu bằng chứng label/dialect, không phải class thật. [`Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md:210-219`](..\..\Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md)

Artifact:

```text
data/gumbel/full/condition_table.parquet
reports/gumbel/05_label_condition_system.md
```

---

### G06 — Evaluator And Model Separation

Mục tiêu:

```text
Không để classifier/WAF proxy trở thành ground truth.
```

Metric bắt buộc:

```text
round_trip_success
parse_success
slot/action validity
unique_ratio
self_bleu3
template/action entropy
exact/near-copy
cluster novelty
condition accuracy
D shortcut diagnostic
```

Artifact:

```text
eval/gumbel/evaluator_config.json
reports/gumbel/06_evaluator_model_separation.md
```

---

### G07 — MLE Anchor + D-as-scorer

Mục tiêu:

```text
Chạy baseline mạnh và deliverable GAN an toàn.
```

D-as-scorer là đóng góp độc lập, không phải phụ lục cứu nguy. [`Guiding_Gumbel-Softmax\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:54-56`](..\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

Artifact:

```text
models/gumbel/d_scorer/paired_d_scorer.pt
eval/gumbel/d_scorer_frontier.json
reports/gumbel/07_mle_anchor_and_d_scorer.md
```

---

### G08 — Gumbel Action-Surgery GAN

Mục tiêu:

```text
Train adversarial action generator sau khi H1/H2/H3 pass.
```

Không làm:

```text
full-sequence GAN
WGAN-GP
REINFORCE/MC rollout
large Transformer generator
```

Artifact:

```text
models/gumbel/action_gan/seed_*/best.pt
eval/gumbel/action_gan_comparison.json
reports/gumbel/08_gumbel_action_surgery_gan.md
```

---

### G09 — Final Evaluation

Mục tiêu:

```text
Kết luận MLE, D-as-scorer hay action-GAN là kết quả chính.
```

Kết luận hợp lệ:

```text
MLE_MAIN
D_SCORER_MAIN
GUMBEL_ACTION_PASS
INCONCLUSIVE
```

---

## 5. Cách cập nhật báo cáo tiến độ

Mỗi lần chạy xong một bước:

1. Cập nhật `timeline/timeline_progress.json`.
2. Điền `evidence_artifacts` bằng đường dẫn artifact thật.
3. Điền `phase.gate.current_result` nếu bước có gate. Trong báo cáo text có thể gọi ngắn là `gate_result`, nhưng tracker JSON dùng trường lồng này.
4. Nếu fail, không xóa; đổi `status` thành `failed` và ghi `failure_reason`.
5. Nếu blocked, ghi blocker cụ thể và bước mở khóa.

Ví dụ trạng thái sau khi chạy G01:

```json
{
  "id": "G01",
  "status": "completed",
  "progress_percent": 100,
  "gate": {
    "current_result": "S2_TAMPER_ACTION"
  },
  "evidence_artifacts": [
    "reports/gumbel/01_slot_action_audit.md",
    "data/gumbel/audit/g0_decision.json"
  ]
}
```

---

## 6. Việc làm ngay

Thứ tự thực thi gần nhất:

```text
1. Tạo script/report G01 slot_action_audit.
2. Cập nhật timeline_progress.json: G01 -> in_progress.
3. Sau audit, chọn S1 hoặc S2.
4. Nếu S2, build action taxonomy slice.
5. Chạy G02 slice: anchor-only, D-as-scorer, pilot action-GAN.
```

---

## 7. Câu chốt vận hành

```text
Gumbel/action-surgery là nhánh triển khai trong thư mục này.
D-as-scorer là baseline/đường an toàn; action-GAN chỉ mở sau gate G01-G07.
Mọi quyết định phải đi qua artifact + gate, không đi qua cảm giác mô hình "có tiềm năng".
```
