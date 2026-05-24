# GAN-as-Policy Trong Real Space - Ke Hoach Vertical Slice

Ngay: 2026-05-23  
Muc tieu: thiet ke huong GAN/RL policy chon mutation lexical tren payload da rehydrate, nham do evasion trong khong gian that hon delex-space.

---

## 1. Ly Do Can Real Space

Ket qua held-out classifier oracle trong delex-space:

```text
accuracy gan 0.9999
recall 1.0
ROC-AUC gan 1.0
classifier-oracle bypass cua GAN gan 0
```

Dien giai:

```text
Delex-space khong co headroom evasion.
No do kha nang tach SQLi/benign trong representation da chuan hoa, khong do WAF evasion that.
```

Evasion that nam o lexical/surface space:

- casing
- comment insertion
- whitespace fragmentation
- encoding
- literal choice
- DB-specific syntax
- function/operator synonym

Viec can lam:

```text
Rehydrate delex payload thanh payload lexicalized truoc khi cham WAF/detector.
```

---

## 2. Gia Thuyet Nghien Cuu

### H-POLICY

```text
GAN/policy co the hoc chon cac action lexical de giam detection rate cua WAF/detector trong real-space, trong khi giu attack intent va validity.
```

### H0

```text
Policy khong vuot random/mutation-engine baseline.
```

### H1

```text
Policy-directed mutation co evasion cao hon random mutation tai cung muc validity va semantic-preservation.
```

---

## 3. Khac Biet Voi H5' Generator Cu

H5' cu:

```text
Input: delex template
Output: token/slot fill
Evaluate: delex classifier oracle
```

Huong policy moi:

```text
Input: real/rehydrated payload
Output: action chon mutation be mat
Evaluate: WAF/libinjection/detector real-space
Feedback: reward cho policy/reranker
```

Day khong phai tiep tuc tune H5' trong cung khong gian. Day la doi vai:

```text
GAN-as-generator -> GAN-as-evasion-policy
```

---

## 4. Kien Truc De Xuat

### Pipeline

```text
Delex payload
    -> Rehydrate literals
    -> Policy Generator chooses action
    -> Mutation engine applies action
    -> Validity/intent guard
    -> WAF/libinjection/detector
    -> reward/score
    -> update or rerank policy
```

### Thanh Phan

1. Rehydrator:

```text
__num__ -> numeric literal
__str__ -> quoted string
__time__ -> numeric delay
__comment__ -> comment token
```

2. Action vocabulary:

```text
case_toggle
inline_comment
space_fragment
operator_synonym
function_synonym
literal_variant
encoding_light
db_specific_comment
```

3. Policy model:

```text
chon action nao ap dung cho payload hien tai.
```

4. Oracle:

```text
libinjection / local WAF / classifier real-space.
```

5. Reward:

```text
valid + attack_intent + not_detected -> reward cao
detected -> reward thap
invalid/broken -> reward am
```

---

## 5. Tra Loi Cau Hoi "Reward Dung O Dau?"

Reward co the dung theo 2 muc.

### Muc 1 - Rerank/Search

Chua update model.

```text
Sinh nhieu action sequences
Cham WAF/detector
Chon action co reward cao
Bao cao evasion/validity
```

Uu diem:

- re
- de audit
- khong can policy-gradient ngay
- phu hop vertical slice

### Muc 2 - Policy Update

Neu Muc 1 co tin hieu, moi train policy.

Pseudo-formula:

```text
L_policy = - reward * log P(action | payload)
```

Hoac dung actor-critic/reinforce nhe.

Reward de xuat:

```text
reward =
  + 2.0 if not_detected
  + 1.0 if valid
  + 0.5 if intent_preserved
  - 2.0 if invalid
  - 1.0 if detected
  - duplicate_penalty
```

Can noi voi thay:

```text
Diem WAF khong chi de ghi lai. Diem do quy doi thanh reward de chon/cap nhat action cua policy.
```

---

## 6. Baselines Bat Buoc

Khong duoc claim policy co ich neu khong vuot baseline.

Baselines:

1. No mutation:

```text
payload rehydrated goc
```

2. Random mutation:

```text
chon action ngau nhien tu action vocabulary
```

3. Rule-based mutation-engine:

```text
deterministic hoac heuristic action
```

4. GAN/policy-directed mutation:

```text
policy chon action dua tren state/payload
```

Primary comparison:

```text
policy vs random mutation
policy vs mutation-engine
```

---

## 7. Metrics

Primary:

- WAF/detector bypass rate.
- Validity pass rate.
- Intent-preservation rate.
- Bypass at fixed validity.

Secondary:

- Duplicate rate.
- Number of actions per successful bypass.
- Technique preservation.
- Per-technique bypass:
  - union_based
  - boolean_blind
  - time_blind
  - error_based

Important:

```text
Bypass khong co y nghia neu validity/intention fail.
```

---

## 8. Real-Space Oracle Vertical Slice

Nen bat dau nho:

```text
1,000 - 5,000 payloads
libinjection or local lightweight WAF
CPU only
no external target
```

Muc dich cua slice:

```text
Chung minh real-space co headroom.
```

Khong claim:

```text
Khong claim thang SOTA.
Khong claim vuot ModSecurity neu chua test.
Khong claim real-world exploit.
```

Claim hop le:

```text
Delex-space oracle khong co headroom, nhung real lexical-space oracle co false negatives va do do phu hop hon de nghien cuu evasion policy.
```

---

## 9. Uu Diem

- Giu tinh than tan cong/evasion ban dau.
- Tra loi dung cau hoi cua thay ve WAF reward.
- Gan voi GSQLi/WAF-A-MoLE/RL-policy literature.
- GAN/policy co vai tro ro rang hon generator delex.
- Neu thanh cong, claim dương manh hon augmentation.

---

## 10. Nhuoc Diem

- Rủi ro cao hon augmentation.
- De dung GSQLi prior art.
- Can rehydration pipeline.
- Can oracle real-space.
- Can guardrail validity/intent de tranh payload hong nhung "bypass".
- Policy-gradient co the ton thoi gian va lai collapse neu lam qua lon.

---

## 11. Pham Vi An Toan

De tranh mo rong qua muc:

```text
Chi chay offline/local.
Khong target he thong that.
Khong automate exploit against public systems.
Chi dung payload trong sandbox/evaluator.
Bao cao raw payload can han che neu khong can thiet.
```

Trong slide:

```text
Day la evaluator/WAF local cho muc dich nghien cuu detector robustness/evasion, khong phai tan cong he thong that.
```

---

## 12. Ke Hoach Trien Khai

### Buoc 1 - Rehydration

Input:

```text
payload_delex_v5
```

Output:

```text
payload_real_candidate
```

Can log:

- template id
- literal choices
- DB family
- technique

### Buoc 2 - Lightweight WAF Oracle

Bat dau voi:

```text
libinjection or simple local WAF-like scanner
```

Neu on:

```text
ModSecurity CRS local
```

### Buoc 3 - Random/Rule Mutation Baseline

Tao baseline truoc policy:

```text
random action sequences
rule-based mutation-engine
```

### Buoc 4 - Policy/Rerank

Ban dau:

```text
policy-free search/rerank
```

Sau do neu co tin hieu:

```text
train policy model
```

### Buoc 5 - Bao Cao

Bang chinh:

| Method | Validity | Intent | Bypass | Dup | Actions |
|---|---:|---:|---:|---:|---:|
| No mutation | | | | | |
| Random mutation | | | | | |
| Rule mutation | | | | | |
| Policy-directed | | | | | |

---

## 13. Dieu Kien Dung Lai

Dung real-space policy neu:

- random mutation da thang policy
- policy chi thang bang payload invalid
- rehydration khong on
- WAF oracle qua yeu de co y nghia
- compute/runtime vuot budget

Luc do quay ve thesis chinh:

```text
negative-result + methodology + augmentation smoke test
```

---

## 14. Ket Luan

Huong real-space evasion-policy la cach giu tinh than tan cong cua de tai.

Nhung no nen la:

```text
vertical slice co gioi han
```

khong phai mo lai mot vong GAN tuning lon.

Thu tu uu tien:

1. Chot negative-result methodology.
2. Lam augmentation smoke test.
3. Lam real-space policy vertical slice neu con thoi gian.

