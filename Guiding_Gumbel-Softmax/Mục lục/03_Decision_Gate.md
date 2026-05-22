# 03 — Decision Gate

> Mục tiêu: quyết định có mở rộng Gumbel action-surgery hay không bằng gate đăng ký trước, chống cherry-pick.

---

## 1. Câu hỏi quyết định

```text
Action-surgery GAN có tạo giá trị vượt anchor-only và MLE+D-scorer không?
Hay chỉ nên giữ MLE-first / D-as-scorer?
```

Không dùng câu hỏi:

```text
GAN có lúc nào đó hơn MLE không?
```

vì Phase 3 cũ đã cho thấy GAN fail 4/6 gates và không có frontier dominance. [`Guiding\Phase 3\eval\phase03\decision.json:2-4`](..\..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 3\eval\phase03\decision.json:85-91`](..\..\Guiding\Phase%203\eval\phase03\decision.json)

---

## 2. Model so sánh

```text
H1 Conditional MLE
H2 MLE + D-as-scorer
H3 anchor-only action infiller
H4 Gumbel action-surgery GAN
H5 rule/tamper baseline
```

---

## 3. Pre-registered gates

H4 pass nếu đồng thời:

```text
1. >= 5 seeds hoặc tối thiểu >= 3 seeds nếu compute hạn chế.
2. Sinh >= 5k samples/seed.
3. H4 > H3 anchor-only trên composite không bù trừ.
4. H4 không thua H2 ở vùng frontier đã đăng ký.
5. round_trip_success và syntax/parse không tụt dưới sàn.
6. unique/self-BLEU/template entropy không collapse.
7. near_copy_rate không tăng bất thường.
8. D shortcut diagnostic pass.
9. Kết luận dựa trên mean/std/CI, không best seed.
```

---

## 4. Tie-break

```text
H4 hòa H3 -> chọn H3 hoặc H2.
H4 hòa H2 -> chọn H2.
H2 hòa H1 -> chọn H1 nếu D không thêm giá trị rõ.
```

Không chọn GAN chỉ vì hợp luận văn hơn.

---

## 5. Fail conditions

```text
slot/action entropy collapse
adv gain chỉ xuất hiện ở best seed
composite tăng nhưng validity/novelty/verified giảm
D học template/length/condition shortcut
payload pass classifier nhưng fail parse/relex/DB dialect
runtime không phù hợp multi-seed
```

---

## 6. Output

```text
reports/gumbel/03_decision_gate_report.md
eval/gumbel/phase03/frontier.json
eval/gumbel/phase03/statistical_summary.json
eval/gumbel/phase03/decision.json
```

`decision.json`:

```json
{
  "decision": "GUMBEL_ACTION_PASS | D_SCORER_MAIN | MLE_MAIN | INCONCLUSIVE",
  "reason": "...",
  "failed_gates": [],
  "passed_gates": [],
  "seed_summary": {}
}
```

---

## 7. Kết luận

Decision Gate là cơ chế bảo vệ luận văn. Một kết quả âm có gate tốt vẫn là kết quả nghiên cứu hợp lệ; một kết quả dương không gate là không đáng tin.
