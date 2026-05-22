# 02 — De-risk Action-Surgery Vertical Slice

> Mục tiêu: chạy một lát nhỏ đủ chứng minh pipeline action-surgery hoạt động end-to-end trước khi mở full training.

---

## 1. Phạm vi slice

Chọn subset nhỏ nhưng có đủ action family:

```text
3-5 technique chính
2-3 db_hint có bằng chứng
5-10k payload train
1-2k dev
1-2k test
```

Nếu dữ liệu verified quá ít, dùng gold/silver nhưng đánh dấu rõ label confidence; Phase 5 hiện vẫn detector-only và review queue cao, nên không được coi label là ground truth tuyệt đối. [`Guiding\Phase 5\reports\05_full_label_system_report.md:4-20`](..\..\Guiding\Phase%205\reports\05_full_label_system_report.md)

---

## 2. Các baseline bắt buộc

```text
B0 rule/tamper random
B1 Conditional MLE candidate
B2 anchor-only action infiller
B3 MLE + D-as-scorer
B4 Gumbel action-surgery pilot
```

B4 không được báo cáo nếu B2 chưa có.

---

## 3. Pipeline slice

```text
1. Build action candidate table.
2. Round-trip payload gốc -> action frame -> reconstructed payload.
3. Train anchor-only action model.
4. Train paired-D nhỏ.
5. Freeze D và chạy D-as-scorer.
6. Chạy Gumbel action-surgery 1 seed.
7. Evaluate cùng sample count.
```

---

## 4. Metric slice

```text
round_trip_success
syntax_or_parse_success
action_validity
unique_ratio
self_bleu3
template_entropy
near_copy_rate
condition_accuracy
D_shortcut_diagnostic
runtime_VRAM
```

Phase 2 cũ chỉ sinh khoảng `n_total=996` mỗi seed, dễ bị phản biện về phương sai; slice mới phải sinh tối thiểu `5k` mẫu/seed nếu runtime cho phép. [`Guiding_Gumbel-Softmax\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:42-44`](..\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

---

## 5. Stop rule trong slice

Dừng nếu:

```text
round_trip_success < 0.95
syntax_or_parse_success < 0.70
unique_ratio < 0.10
D acc > 0.90 kéo dài dù đã giảm capacity/freeze
anchor+adv không hơn anchor-only ở bất kỳ metric chính nào
```

---

## 6. Output

```text
data/gumbel/slice/action_surgery_train.parquet
data/gumbel/slice/action_surgery_dev.parquet
eval/gumbel/slice/baseline_comparison.json
eval/gumbel/slice/decision.json
reports/gumbel/02_de_risk_action_surgery_slice.md
```

---

## 7. Kết luận

Slice này không nhằm tạo kết quả đẹp. Nó nhằm trả lời câu hỏi: action-surgery có tín hiệu thật không, hay adversarial chỉ quay về anchor-only.
