# GAN-as-Augmentation-Engine - Ke Hoach Pivot Sang Phong Thu

Ngay: 2026-05-23  
Muc tieu: bien ket qua GAN hien tai thanh mot huong nghien cuu phong thu hop le: GAN sinh du lieu tan cong tong hop de tang robustness cua SQLi detector.

---

## 1. Ly Do Pivot

Ket qua Phase 8 cho thay:

```text
GAN-as-payload-generator trong delex-space khong vuot anchor-only/mutation-engine tren held-out classifier oracle.
```

Nhung dieu do khong co nghia GAN vo dung. Neu generated samples bi detector bat duoc, chung van co the huu ich o vai tro khac:

```text
Augmentation data cho detector phong thu.
```

Cau hoi moi:

```text
GAN-generated SQLi variants co giup detector tong quat hoa tot hon khong?
```

Day la pivot tu:

```text
offensive evasion
```

sang:

```text
defensive robustness
```

---

## 2. Gia Thuyet Nghien Cuu

### H-AUG

```text
Them mau SQLi tong hop tu GAN vao train set co the cai thien robustness cua detector tren cac bien the tan cong chua thay, so voi detector chi train tren du lieu goc hoac mutation-engine.
```

### H0

```text
GAN augmentation khong cai thien detector so voi no-augmentation hoac mutation augmentation.
```

### H1

```text
GAN augmentation cai thien recall/F1/robustness tren held-out/adversarial SQLi variants trong khi khong lam false positive rate tren benign tang qua muc.
```

---

## 3. Vi Sao Huong Nay Giu GAN Trung Tam

Trong huong nay, GAN khong phai la cong cu de "vuot detector". GAN la:

```text
bo sinh du lieu tan cong tong hop de lam detector manh hon.
```

GAN trung tam vi:

- generator tao synthetic SQLi candidates
- discriminator/detector la doi tuong duoc tang cuong
- pipeline danh gia truc tiep gia tri cua GAN qua robustness
- ket qua am/duong deu co y nghia

Neu GAN augmentation thang:

```text
GAN co gia tri nhu augmentation engine.
```

Neu GAN augmentation khong thang:

```text
Ket luan: constrained/mutation transformations du de phu manifold; GAN khong them gia tri trong corpus nay.
```

---

## 4. Lien He Literature

Huong nay phu hop voi nhieu nhom tai lieu trong corpus:

- GAN for IDS.
- CTGAN/tabular augmentation.
- SMOTE-GAN / BNGAN.
- TDCGAN.
- GAN-based data balancing.
- Adversarial augmentation for detector robustness.

Khac voi GSQLi:

```text
GSQLi tap trung bypass/evasion.
Huong nay tap trung robustness/defense.
```

Vi vay khong can claim thang GSQLi.

---

## 5. Kien Truc De Xuat

### Pipeline

```text
Gold train data
    |
    +--> Train detector baseline
    |
    +--> Mutation-engine augmentation
    |       -> train detector mutation-augmented
    |
    +--> GAN candidate generation
            -> guardrail filter
            -> train detector GAN-augmented

All detectors
    -> evaluate on held-out / technique-held-out / adversarial variants
```

### Vai Tro Tung Khoi

Generator:

```text
Sinh SQLi variants tu delex/rehydrated templates.
```

Mutation-engine:

```text
Baseline augmentation khong hoc.
```

Detector:

```text
Mo hinh phong thu can tang robustness.
```

Evaluator:

```text
Do recall, F1, FPR, robustness tren test sets khac nhau.
```

---

## 6. Thiet Ke Thi Nghiem

### Train Sets

Tao 4 detector:

| Detector | Training data |
|---|---|
| D0 | Original train only |
| D1 | Original train + mutation-engine augmentation |
| D2 | Original train + H5' GAN augmentation |
| D3 | Original train + oracle-aware GAN-selected augmentation |

Co the them:

| Detector | Training data |
|---|---|
| D4 | Original train + mutation + GAN augmentation |

### Test Sets

1. Cluster-safe test:

```text
Phase 8 delex_cluster_split/test.parquet
```

2. Technique-held-out test:

```text
Hold out one technique during training, test on that technique.
```

3. Surface-adversarial test:

```text
Payloads duoc bien doi lexical:
  comments
  whitespace
  casing
  simple encoding
  operator/function synonym
```

4. Rehydrated real-space test neu lam duoc:

```text
Delex payload -> literal real -> detector test.
```

---

## 7. Metrics

Primary:

- SQLi recall on held-out test.
- SQLi recall on adversarial/surface-mutated test.
- False positive rate on benign.
- F1.

Secondary:

- AUROC/AUPRC.
- Recall by technique.
- Robustness delta:

```text
robustness_delta = recall_augmented - recall_baseline
```

- Cost:
  - train time
  - augmentation size
  - duplicate rate

---

## 8. Guardrails De Khong Tu Lua

Khong duoc claim GAN augmentation co ich neu:

- D2 khong hon D1.
- Recall tang nhung FPR tren benign tang manh.
- Test set leak template tu train.
- GAN samples chi la duplicate exact/near-duplicate.
- Chi thang tren weak test nhung khong thang tren adversarial/held-out.

Can so sanh toi thieu:

```text
GAN augmentation vs mutation augmentation.
```

Neu chi so voi no-augmentation, claim se yeu.

---

## 9. Uu Diem

- Giu GAN la thanh phan trung tam.
- Phu hop voi literature GAN-for-IDS/augmentation.
- Khong can GAN evade WAF.
- Compute nhe hon RL/policy.
- Co the tan dung samples da sinh:
  - max-aggressive
  - reranked
  - oracle-aware search
- Ket qua am van co y nghia.

---

## 10. Nhuoc Diem

- Doi huong de tai tu tan cong sang phong thu.
- Can thuyet phuc thay chap nhan framing moi.
- Neu GAN samples qua de-detect, augmentation co the khong giup.
- Phai co baseline mutation augmentation manh.
- Neu detector oracle AUC da 1.0 tren delex, can test adversarial/held-out kho hon de co headroom.

---

## 11. Ket Qua Mong Doi

### Truong Hop Tot

```text
GAN augmentation giup detector tang recall tren adversarial/technique-held-out test so voi mutation augmentation.
```

Claim:

```text
GAN khong vuot detector voi vai tro generator tan cong, nhung co gia tri nhu augmentation engine giup detector phong thu robust hon.
```

### Truong Hop Xau

```text
GAN augmentation khong hon mutation augmentation.
```

Claim:

```text
Trong corpus SQLi nay, constrained transformations/mutation da du phu manifold; GAN khong them gia tri phong thu dang ke.
```

Day van la ket qua am co gia tri.

---

## 12. Ke Hoach Trien Khai Ngan Han

Buoc 1:

```text
Tao augmentation sets:
  - mutation_engine_samples
  - H5' max-aggressive samples
  - oracle-aware selected samples
```

Buoc 2:

```text
Train detector D0/D1/D2/D3 tren cung architecture.
```

Buoc 3:

```text
Tao adversarial/surface-mutated test set.
```

Buoc 4:

```text
Bao cao:
  recall by technique
  FPR benign
  F1
  robustness_delta
```

Buoc 5:

```text
Quyet dinh pivot:
  neu GAN aug > mutation aug -> lay lam claim duong
  neu khong -> giu negative-result methodology thesis
```

