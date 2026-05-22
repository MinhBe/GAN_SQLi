# 10 — Literature And Implementation Roadmap

> Mục tiêu: nối paper đã đọc với quyết định triển khai, và liệt kê việc cần làm tiếp.

---

## 1. Paper đã tác động trực tiếp

| Paper/nguồn | Tác động |
|---|---|
| RelGAN | chứng minh Gumbel-text-GAN cần combo pretrain/loss/D/temperature, không chỉ Gumbel |
| MaskGAN | ủng hộ masked infill giảm D saturation, nhưng cảnh báo vẫn có thể thua MLE diversity |
| GSQLi | chuyển S2 tamper-action từ dự phòng thành đường chính |
| Jang/Maddison | Gumbel/Concrete là relaxation gradient, có bias/temperature tradeoff |
| WAF-A-MoLE/Lu | action/mutation phải giữ semantic, không random token |
| Lee Dedup | novelty phải theo cluster, không chỉ edit distance |

GSQLi là paper thay đổi kế hoạch mạnh nhất vì cung cấp payload transformer, mutation vector và action taxonomy nhẹ. [`Guiding_Gumbel-Softmax\03_Phan_Tich_Sau_Tu_Paper.md:54-62`](..\03_Phan_Tich_Sau_Tu_Paper.md)

---

## 2. Việc phải làm ngay

```text
1. Implement slot_action_audit.py.
2. Tích hợp Libinjection hoặc parser tương đương cho action taxonomy.
3. Build slice action-surgery dataset.
4. Chạy anchor-only và D-as-scorer trước.
5. Chỉ train Gumbel action-GAN nếu G0 pass.
6. Chuẩn hóa evaluator multi-dialect/soft-dialect.
7. Pre-register metric, seed, sample size, floor gates.
```

---

## 3. Việc không làm vòng đầu

```text
full-sequence GAN
WGAN-GP
PPO/REINFORCE/MC rollout
large Transformer generator
claim bypass nếu payload chưa pass parse/relex
claim privacy nếu chưa có memorization/privacy test
```

---

## 4. Deliverables research

```text
G0 action audit report
S2 action taxonomy dataset
D-as-scorer frontier
Gumbel action-surgery pilot/confirmatory report
negative result nếu adv không thắng anchor
```

---

## 5. Câu chốt

```text
Nhánh này đáng làm vì nó đã rời khỏi SeqGAN cũ:
không sinh full sequence, không coi Gumbel là thuốc chống collapse,
mà dùng Gumbel như công cụ chọn action trong một hệ surgery có evaluator.
```
