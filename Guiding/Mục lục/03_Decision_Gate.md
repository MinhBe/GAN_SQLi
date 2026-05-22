# 03 — Decision Gate

> Mục tiêu: quyết định có mở rộng Gumbel-SeqGAN hay không bằng một cổng đánh giá nghiêm túc, chống cherry-pick, chống best-run bias và chống tự lừa.

---

## 1. Vấn đề cần giải quyết

Nếu tiêu chí là:

```text
GAN hơn MLE ở một vùng nào đó
```

thì quá lỏng. Với mô hình stochastic và nhiều metric, gần như luôn tìm được một điểm GAN nhỉnh hơn do nhiễu.

Decision Gate phải trả lời:

```text
GAN có thật sự đáng scale không?
Hay MLE-first nên là hướng chính?
```

---

## 2. Tính chất của phase này

| Tính chất | Diễn giải |
|---|---|
| Pre-registered | Metric và vùng so sánh được khóa trước |
| Statistical | Dùng nhiều seed, mean, CI |
| Baseline-first | MLE là mặc định thắng nếu hòa |
| Anti-cherry-pick | Không chọn run đẹp nhất |
| Kill-capable | Có quyền dừng GAN full-scale |

---

## 3. Nguyên tắc chính

```text
MLE is default.
GAN is experimental challenger.
```

Nếu GAN hòa MLE:

```text
chọn MLE
```

Vì MLE đơn giản hơn, ổn định hơn, dễ reproduce hơn và dễ debug hơn.

---

## 4. Điều kiện bắt buộc trước khi gate

Gate chỉ hợp lệ nếu phase 02 đã có:

```text
pre-registered protocol
≥3 seeds mỗi nhánh
MLE sampling frontier
GAN results đủ seed
D shortcut diagnostic
collapse metrics theo step
không dùng best run làm kết luận
```

Nếu thiếu các điều kiện này, gate không hợp lệ.

---

## 5. Primary comparison

Không so một điểm đơn lẻ.

So theo frontier:

```text
quality-diversity frontier
```

Ví dụ các trục:

```text
quality = syntax_validity + type_accuracy
diversity = unique_ratio + self-BLEU + AST/template entropy
```

Có thể định nghĩa composite nội bộ, nhưng phải đăng ký trước.

---

## 6. Vùng so sánh phải đăng ký trước

Ví dụ:

```text
type_accuracy >= 0.70
syntax_validity >= 0.85
unique_ratio in [0.70, 0.95]
self_BLEU_3 <= 0.85
```

GAN chỉ được coi là thắng nếu cải thiện trong vùng này, không phải thắng ở một điểm rời rạc ngoài vùng.

---

## 7. Điều kiện pass cho GAN

GAN pass nếu đồng thời thỏa:

```text
1. Chạy ít nhất 3 seeds.
2. Mean performance tốt hơn MLE frontier trong vùng đã đăng ký.
3. Khoảng tin cậy không cho thấy cải thiện chỉ là nhiễu.
4. Cải thiện nằm trên một vùng liên tục, không phải một điểm lẻ.
5. Không collapse ở đa số seeds.
6. D shortcut diagnostic pass.
7. Proxy metric tăng không làm verified/dev metric giảm.
8. Không có exact-copy/memorization bất thường.
```

---

## 8. Điều kiện fail

GAN fail nếu có một trong các trường hợp:

```text
collapse ở phần lớn seeds
chỉ thắng ở best run
chỉ thắng ở một điểm cherry-pick
D học one-hotness/softness shortcut
type consistency proxy tăng nhưng verified metric giảm
MLE hòa hoặc tốt hơn trong frontier
variance quá lớn khiến kết luận không đáng tin
```

---

## 9. Tie-break rule

Nếu kết quả không rõ:

```text
MLE thắng
```

Không tiếp tục full-scale GAN chỉ vì:

```text
GAN có vẻ tiềm năng
GAN thỉnh thoảng tốt hơn
GAN phù hợp thesis hơn
```

---

## 10. Kết quả sau gate

### 10.1. GAN Pass

Đi tiếp:

```text
Full Data Foundation
Full Label System
Full Evaluator
Full Gumbel-SeqGAN
```

Nhưng MLE vẫn giữ làm baseline chính thức.

### 10.2. GAN Fail rõ

Không full-scale GAN.

Chuyển main path sang:

```text
Conditional MLE + evaluator-guided search
```

GAN chỉ còn là phần phân tích thất bại hoặc future work.

### 10.3. GAN Không rõ / Inconclusive

Không scale ngay.

Làm thêm pilot trung gian:

```text
300k–500k rows
```

nhưng phải có protocol mới, không tune vô hạn.

---

## 11. Kết quả đầu ra

```text
reports/03_decision_gate_report.md
eval/phase03/mle_vs_gan_frontier.png
eval/phase03/statistical_summary.json
eval/phase03/decision.json
```

Nội dung `decision.json`:

```json
{
  "decision": "MLE_MAIN | GAN_PASS | INCONCLUSIVE",
  "reason": "...",
  "metrics": {},
  "seeds": [],
  "gate_passed": true
}
```

---

## 12. Cách evaluate phase này

Phase này pass nếu có một quyết định rõ ràng và có bằng chứng.

Không pass nếu:

```text
chưa đủ seed
chưa có MLE frontier
chưa có D shortcut diagnostic
chưa có protocol pre-register
chỉ có best run
```

---

## 13. Kết luận

Decision Gate là cơ chế chống tự lừa.

Nếu gate không nghiêm, mọi phase sau chỉ là hợp thức hóa một quyết định đã muốn tin từ trước.
