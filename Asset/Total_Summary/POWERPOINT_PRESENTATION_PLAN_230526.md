# Ke Hoach Trinh Bay PowerPoint - Cap Nhat Huong GAN Trung Tam

Ngay: 2026-05-23  
Muc tieu: chuan bi noi dung thuyet trinh voi thay sau khi da co ket qua Phase 8.  
Thong diep trung tam: vai tro "GAN sinh payload de vuot detector" trong delex-space da fail gate, nhung GAN van co the giu vai tro trung tam neu doi sang hai huong hop le hon:

1. GAN-as-augmentation-engine cho phong thu.
2. GAN-as-policy trong real lexical space.

Tai lieu nay la ke hoach noi dung slide, khong phai ban text doc nguyen van.

---

## 0. Yeu Cau Chinh Cua Thay Tu Buoi Trao Doi

Tu transcript ngay 2026-05-13, cac yeu cau cua thay co the gom thanh 8 nhom:

1. Lam ro dataset:
   - lay tu nhung nguon nao
   - bao nhieu bo du lieu
   - dua ve mot schema chung nhu the nao
   - co ca payload tan cong va benign/user input hay khong

2. Lam ro nhan:
   - nhan tan cong la gi
   - loai tan cong nao
   - tan cong DB nao
   - confidence/reason duoc tao bang script hay thu cong
   - nhan co duoc model/luat kiem tra lai hay khong

3. Lam ro mo hinh de xuat:
   - Generator sinh gi
   - Discriminator phan biet gi
   - firewall/WAF nam o dau
   - moi quan he giua G, D va WAF la gi
   - cac khoi tren so do phai co ket noi ro rang

4. Lam ro reward:
   - WAF cho diem thi diem do dung o dau
   - diem cao/thap anh huong Generator nhu the nao
   - la filter, reward, rerank, hay label
   - khong duoc noi chung chung "ho tro Generator"

5. Lam ro vi sao SeqGAN cu collapse:
   - D qua manh
   - gradient cho G kem
   - discrete token khong truyen gradient tot
   - GAN full-sequence sinh payload SQLi khong on dinh

6. Lam ro so sanh mo hinh:
   - SeqGAN
   - WGAN-GP
   - CTGAN
   - mutation-engine
   - anchor-only/MLE
   - H5' paired surgery GAN

7. Lam ro firewall/WAF:
   - dung WAF ma nguon mo nao
   - WAF dung de label, reward, hay evaluate
   - neu payload khong qua WAF thi xu ly nhu the nao
   - neu dua vao DB thi co sandbox khong

8. Lam ro tien do:
   - trong thang 5 chay xong thi nghiem gi
   - cai gi da xong
   - cai gi fail
   - cai gi la huong tiep theo

---

## 1. Cau Chuyen Moi De Trinh Bay

Khong nen trinh bay theo cach:

```text
Em da lam GAN va dang tim cach de GAN thang.
```

Nen trinh bay theo cach:

```text
Em da thuc nghiem co he thong cac vai tro cua GAN trong bai toan SQLi.
Ket qua cho thay GAN full-sequence va slot-surgery generator khong vuot baseline trong delex-space.
Vi vay em chuyen vai tro GAN sang hai huong co headroom hon:
  1. GAN lam augmentation-engine cho detector phong thu.
  2. GAN lam policy chon bien doi trong real lexical space.
```

Diem manh cua cach ke nay:

- Khong phu nhan ket qua am.
- Tra loi duoc cau hoi "GAN nam o dau".
- Giu GAN la trung tam nhung khong bat GAN generator phai thang.
- Gan voi yeu cau cua thay: phai ro quan he G - D - WAF - reward.

---

## 2. De Xuat Cau Truc PowerPoint

### Slide 1 - Tieu De

Tieu de de xuat:

```text
Nghien cuu vai tro cua GAN trong sinh va tang cuong du lieu SQL Injection
```

Subtitle:

```text
Tu full-sequence generation den augmentation va real-space evasion policy
```

Thong diep:

```text
GAN khong chi duoc danh gia bang viec "sinh payload de vuot detector", ma bang tung vai tro cu the trong pipeline SQLi.
```

---

### Slide 2 - Bai Toan Va Muc Tieu

Noi dung:

- SQL Injection payload co cau truc ngan, nhieu bien the lexical.
- GAN tren chuoi roi rac thuong gap van de gradient/collapse.
- Muc tieu ban dau:
  - sinh payload SQLi moi
  - kiem tra voi detector/WAF
  - danh gia novelty, validity, evasion

Can noi voi thay:

```text
Ban dau em dat muc tieu tan cong/evasion. Sau khi thuc nghiem, em thay vai tro generator trong delex-space khong vuot baseline. Vi vay em tach lai bai toan thanh hai huong: augmentation phong thu va policy real-space.
```

---

### Slide 3 - Dataset Va Schema

Noi dung can co:

- Nguon du lieu:
  - Kaggle/public SQLi payload datasets
  - payloadbox / public payload lists neu co trong repo
  - cac bo SQLi/benign da merge
  - cac nguon duoc ghi trong manifest
- Tat ca dua ve mot schema chung.
- Cac cot chinh:
  - `payload_working`
  - `payload_delex_v5`
  - `is_sqli`
  - `technique_primary`
  - `db_family`
  - `confidence`
  - `label_source`
  - `reason/review flags`

Tra loi yeu cau cua thay:

```text
Em khong chi lay mot file roi train truc tiep. Em gom nhieu nguon, dua ve cung schema, bo mau khong ro, va ghi lai nguon/label/confidence.
```

---

### Slide 4 - Labeling Va Quality Control

Noi dung:

- Co script labeling/rule-based check.
- Co confidence/reason.
- Co bronze/silver/gold hoac verified split.
- Co review queue cho mau xung dot.
- Co audit label distribution.

Thong diep:

```text
Em khong coi label thu cong la tuyet doi. Label duoc script va cac audit kiem tra lai.
```

Can noi:

```text
Day la diem em da sua so voi lan truoc: confidence khong chi la cam tinh, ma co pipeline audit va reason.
```

---

### Slide 5 - Phat Hien Quan Trong: Template Leakage

Noi dung:

- Delex-template duplicate rat cao.
- Khoang 1.6M dong nhung chi khoang 77,804 template delex rieng.
- Neu split ngau nhien thi train/dev/test leak template.
- Da build cluster split theo delex-template:
  - train: 1,561,364
  - dev: 150,694
  - test: 272,315
  - overlap template = 0

Thong diep:

```text
Neu khong audit leakage, ket qua validation co the qua dep nhung khong co gia tri khoa hoc.
```

---

### Slide 6 - Vi Sao SeqGAN/Full-Sequence GAN Fail

Noi dung:

- SeqGAN/REINFORCE gap van de discrete token.
- D hoc nhanh hon G.
- G mat gradient/advantage.
- Collapse hoac sinh chuoi khong hop le.
- WGAN-GP/SpectralNorm/TTUR/Gumbel cung khong giai quyet tri de.

Can noi voi thay:

```text
Em da khong tiep tuc "mo cua day be". Em dung ket qua fail de doi don vi sinh: tu full-sequence sang slot-surgery.
```

---

### Slide 7 - Phase 8: H5' Paired Masked Payload-Surgery GAN

So do can ve:

```text
Payload/frame delex
    -> mask slot/local token
    -> Generator dien/sua slot
    -> Paired Discriminator so real/fake trong cung frame
    -> Evaluator cham validity / novelty / evasion
```

Noi dung:

- Khong sinh ca payload.
- Chi sua slot/local token.
- Co anchor-only CE de giu gan du lieu that.
- Co mutation-engine baseline.
- Co evaluator tach truc.

Thong diep:

```text
Day la cach em tra loi van de collapse: khong de GAN sinh toan bo chuoi nua.
```

---

### Slide 8 - Evaluator Contract

Noi dung:

Bon truc:

1. Validity:
   - balanced delimiter
   - parse/structure neu co
2. Novelty:
   - train-template duplicate
   - batch duplicate
3. Conditioning debug:
   - technique hint, chi la debug
4. Evasion:
   - chi tinh khi co detector/WAF results

Can nhan manh:

```text
Em khong dung keyword-only syntax lam gate chinh.
Em khong dung D-score nhu ground truth.
```

---

### Slide 9 - Ket Qua Generator: Gate Fail

Bang can dua:

| Method | Classifier-oracle bypass |
|---|---:|
| Anchor-only | `0.0050` |
| Mutation-engine | `0.0000` |
| H5' max-local | `0.0000` |
| H5' max-aggressive | `0.0050` |
| Oracle-aware search | `0.0050` |

Ket luan tren slide:

```text
H5' generator khong vuot anchor-only/mutation-engine tren held-out classifier oracle.
Adversarial contribution gan bang 0 tren truc evasion.
```

Can noi voi thay:

```text
Day la ket qua am, nhung no dung voi gate em da dat truoc. Em khong tiep tuc claim GAN generator thang.
```

---

### Slide 10 - Tai Sao Delex-Space Khong Do Duoc Evasion That

Noi dung:

- Classifier oracle trong delex-space co:
  - accuracy gan 0.9999
  - recall 1.0
  - ROC-AUC gan 1.0
- Dieu nay cho thay representation qua de tach SQLi/benign.
- Evasion that nam o lexical surface:
  - casing
  - comment
  - encoding
  - literal
  - DB-specific syntax
  - whitespace

Thong diep:

```text
Delex tot cho generation/conditioning, nhung khong phu hop de ket luan WAF evasion.
```

---

### Slide 11 - Pivot Moi: GAN Van Trung Tam Nhung Doi Vai

Noi dung:

Ba vai GAN:

1. GAN-as-generator:
   - da test
   - khong vuot baseline
   - ha xuong ablation/negative result

2. GAN-as-augmentation-engine:
   - sinh du lieu tan cong tong hop de train detector phong thu robust hon
   - huong chinh de co claim duong

3. GAN-as-policy:
   - hoc policy chon mutation real-space de test/evaluate detector
   - vertical slice neu con thoi gian

Thong diep:

```text
GAN khong bi bo, ma duoc chuyen sang vai co headroom that hon.
```

---

### Slide 12 - Huong 1: GAN-as-Augmentation-Engine

So do:

```text
Train detector baseline
Train detector + mutation augmentation
Train detector + GAN augmentation
Test tren held-out / adversarial / real-space variants
```

Muc tieu:

```text
GAN samples co giup detector tong quat hoa tot hon khong?
```

Metric:

- F1/Recall tren held-out.
- Recall tren technique held-out.
- Robustness tren adversarial surface mutations.
- False positive rate tren benign.

Thong diep:

```text
Neu GAN khong evade duoc detector, no van co the huu ich neu lam detector phong thu manh hon.
```

---

### Slide 13 - Huong 2: GAN-as-Policy Trong Real Space

So do:

```text
Payload real/rehydrated
    -> Policy Generator chon action lexical
    -> Apply mutation
    -> WAF/libinjection/detector cham
    -> reward quay lai policy
```

Can tra loi cau hoi thay: reward dung o dau?

```text
Reward khong phai chi de ghi diem.
Reward duoc dung de cap nhat policy hoac de rerank/select action.

Neu payload bi detect:
  reward thap
Neu payload giu intent + khong bi detect:
  reward cao
Neu payload hong validity:
  reward am/manh
```

Thong diep:

```text
Day la cach dung WAF dung nghia: WAF la oracle/feedback cho policy trong real-space, khong phai chi la cot diem roi bo do.
```

---

### Slide 14 - Kien Truc Moi De Tra Loi "3 Ong Quan He The Nao"

Can ve so do ro:

```text
                 +----------------+
                 | Real/Delex Data |
                 +--------+-------+
                          |
        +-----------------+------------------+
        |                                    |
        v                                    v
+---------------+                    +----------------+
| Generator /   |                    | Discriminator /|
| Policy / Aug  |                    | Detector       |
+-------+-------+                    +--------+-------+
        |                                     ^
        v                                     |
+---------------+      feedback/reward       |
| WAF/Oracle/   +-----------------------------+
| Validity Gate |
+-------+-------+
        |
        v
+---------------+
| Selected data |
| / augmented   |
| training set  |
+---------------+
```

Noi ro:

- D/detector hoc phan biet attack/benign.
- G/policy sinh candidate/action.
- WAF/oracle cham ket qua.
- Reward/score quay lai G theo hai cach:
  - rerank/select
  - policy update neu lam real-space policy

---

### Slide 15 - Ke Hoach Thuc Nghiem Tiep Theo

Buoc 1:

```text
Do diversity/coverage head-to-head:
GAN vs mutation-engine at fixed validity.
```

Buoc 2:

```text
Augmentation smoke test:
detector no-augmentation vs mutation augmentation vs GAN augmentation.
```

Buoc 3:

```text
Real-space vertical slice:
rehydrate payload, cham libinjection/local WAF, dung lam policy feedback.
```

Buoc 4:

```text
Chot thesis theo ket qua:
neu augmentation tang robustness -> GAN-as-augmentation la claim duong.
neu khong -> negative-result + methodology la dong gop chinh.
```

---

### Slide 16 - Ket Luan

Ket luan nen noi:

```text
Em da chung minh GAN generator trong delex-space khong vuot duoc baseline.
Day la ket qua am nhung co gia tri vi duoc do bang evaluator va cluster split chat.

Huong tiep theo khong phai tiep tuc tune generator, ma la doi vai tro GAN:
  1. augmentation-engine cho phong thu
  2. policy chon mutation trong real-space
```

Ket cau chot:

```text
GAN van la trung tam cua luan van, nhung trung tam theo nghia nghien cuu vai tro cua GAN trong SQLi pipeline, khong phai bat buoc GAN generator phai thang moi baseline.
```

---

## 3. Cac Cau Hoi Thay Co The Hoi Va Cau Tra Loi

### Hoi: GAN cua em nam o dau?

Tra loi:

```text
Ban dau GAN nam o vai generator sinh payload. Ket qua cho thay vai do khong vuot baseline. Hien em doi sang hai vai hop ly hon: GAN augmentation-engine de tang robustness detector, va GAN policy de chon mutation real-space dua tren feedback cua WAF.
```

### Hoi: WAF cho diem roi diem do dung lam gi?

Tra loi:

```text
Co hai cach dung:
1. Trong augmentation/rerank: diem WAF dung de chon mau kho/phu hop dua vao tap train detector.
2. Trong policy: diem WAF la reward de cap nhat policy chon action. Payload hop le va khong bi detect thi reward cao; payload hong validity thi reward am; payload bi detect thi reward thap.
```

### Hoi: Tai sao khong tiep tuc tune H5' GAN?

Tra loi:

```text
Vi H5' da fail gate em dat truoc: khong vuot anchor-only/mutation-engine tren held-out oracle. Tiep tuc tune trong cung delex-space co nguy co toi uu artifact. Em chuyen sang bai toan co headroom that hon.
```

### Hoi: Vay ket qua am co lam hong de tai khong?

Tra loi:

```text
Khong. Ket qua am giup xac dinh ro vai tro nao cua GAN khong phu hop. Dong gop cua em la pipeline danh gia chat, leakage-safe split, va chuyen huong sang vai tro GAN co y nghia hon.
```

### Hoi: Vi sao pivot sang phong thu?

Tra loi:

```text
Vi neu GAN samples bi detector bat duoc, chung van co the huu ich nhu du lieu kho de train detector robust hon. Literature ve GAN cho IDS/augmentation cung manh hon va phu hop voi corpus em da doc.
```

