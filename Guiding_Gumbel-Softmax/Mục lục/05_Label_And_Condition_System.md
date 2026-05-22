# 05 — Label Và Condition System

> Mục tiêu: tạo condition đủ tin để action-surgery không học shortcut từ nhãn nhiễu.

---

## 1. Trạng thái hiện tại

Phase 5 sample report đang ở `detector_only`, xử lý `10,000` dòng, có `gold=4,821`, `silver=1,251`, `bronze=3,928`, `review_queue=5,360`, `verified_dev=504`, `verified_test=468`. [`Guiding\Phase 5\reports\05_full_label_system_report.md:4-20`](..\..\Guiding\Phase%205\reports\05_full_label_system_report.md)

Full progress mới `3,900,000 / 12,753,953`, tức `30.5788%`, nên không được coi full label đã hoàn tất. [`Guiding\Phase 5\logs\phase05_full_progress.json:4-10`](..\..\Guiding\Phase%205\logs\phase05_full_progress.json)

---

## 2. Condition được phép dùng

```text
technique_primary nếu gold/silver hoặc verified
db_hint nếu có bằng chứng dialect
action_family
template_family
payload_length_bucket
confidence_band
```

Không dùng:

```text
unknown như engine class thật
tier4_ai_needed làm label train chính
classifier-only label làm ground truth
```

Guiding nội bộ đã ghi `unknown` là thiếu bằng chứng, không phải engine category. [`Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md:210-219`](..\..\Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md)

---

## 3. Calibration

Kế hoạch:

```text
1. Tách gold/silver/bronze/review.
2. Tạo condition_confidence.
3. Dùng Snorkel-style label model nếu có nhiều labeling functions.
4. Report conflict theo duplicate cluster.
5. Chỉ dùng verified/gold-silver cho confirmatory gate.
```

Snorkel phù hợp vì học accuracy/correlation của labeling functions mà không cần full ground truth. [`Asset\Total_Analyst1\Ratner_2017_Snorkel.md_ANALYSIS.md:46-52`](..\..\Asset\Total_Analyst1\Ratner_2017_Snorkel.md_ANALYSIS.md)

---

## 4. Output

```text
data/gumbel/full/condition_table.parquet
data/gumbel/full/verified_condition_dev.parquet
data/gumbel/full/verified_condition_test.parquet
reports/gumbel/05_label_condition_system.md
```

---

## 5. Gate

Pass nếu:

```text
condition coverage đủ cho selected action families
verified_dev/test không quá nhỏ cho metric chính
unknown không bị dùng như class sinh mẫu
condition shortcut diagnostic được định nghĩa
```

Fail nếu:

```text
condition quá nhiễu
class hiếm không có verified sample
D hoặc G chỉ học condition imbalance
```

---

## 6. Kết luận

Action-surgery có thể chạy với label yếu ở pilot, nhưng claim cuối phải dựa trên verified/gold-silver hoặc report rõ confidence band.
