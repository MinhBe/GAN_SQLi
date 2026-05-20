# AGENT BRIEF: Test 10K — Pilot SQLi Labeling Run

> Self-contained runbook. Bất kỳ AI agent nào đọc file này có thể triển khai độc lập.
> Không cần context từ cuộc hội thoại trước.
> Ngày tạo: 2026-05-18

---

## MỤC TIÊU

Chạy thử 10,000 payload SQLi đầu tiên qua skill `label-sqli`, dùng GPT-4o-mini làm
AI reviewer độc lập (thay vì Claude Haiku) để đảm bảo tính trung lập, sau đó evaluate
kết quả qua 6 metrics cụ thể.

---

## CẤU TRÚC DỰ ÁN (toàn bộ path tuyệt đối)

```
C:\Users\Admin\Documents\GAN_SQLi\
├── Asset\LabelData\
│   ├── Testing\Testing_data.csv            ← INPUT (10,000 rows, cột: payload_norm)
│   ├── FinalDataSet\final_dataset_1.csv   ← GROUND TRUTH cũ (1,084,880 rows, cột: payload_norm)
│   ├── combined_labeled_data.csv          ← GROUND TRUTH labels (40,860 rows, cột: payload_norm, sqli_type, db_engine, confidence)
│   ├── test_labeled_10k.csv               ← WORKING COPY (10K rows, cột: payload)
│   └── scripts\
│       └── Test 10K.md                    ← File này
└── Skill\label-sqli\scripts\
    ├── detectors.py       ← Core: score_all(), primary_type(), primary_db_engine()
    ├── owasp_scorer.py    ← OWASP conservative scoring → score(payload) -> {type_vector, db_vector}
    ├── heuristic_scorer.py← Heuristic scoring → score(payload) -> {type_vector, db_vector}
    ├── comparator.py      ← compare_systems(owasp_r, heur_r) -> {needs_ai_review, confidence, ...}
    ├── ai_reviewer.py     ← Claude Haiku reviewer → review_batch(payloads, indices, ...)
    ├── label_resolver.py  ← resolve_label(payload, ai_result=None) -> {sqli_type, db_engine, ...}
    └── run_labeling.py    ← CLI orchestrator (cần sửa để thêm --reviewer flag)
```

---

## BƯỚC 1: EXTRACT 10K ROWS

**Tạo file**: `Skill\label-sqli\scripts\prepare_pilot.py`

```python
import sys
import io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
from pathlib import Path

ROOT = Path(r"C:\Users\Admin\Documents\GAN_SQLi")
INPUT = ROOT / "Asset" / "LabelData" / "Testing" / "Testing_data.csv"
OUTPUT = ROOT / "Asset" / "LabelData" / "test_labeled_10k.csv"

df = pd.read_csv(INPUT, encoding='utf-8-sig')
# final_dataset_1.csv dung cot 'payload_norm' → rename sang 'payload' cho run_labeling.py
df = df.rename(columns={'payload_norm': 'payload'})
df.to_csv(OUTPUT, index=False, encoding='utf-8-sig')
print(f"[OK] Saved {len(df)} rows -> {OUTPUT}")
```

**Chạy**:
```bash
python "C:\Users\Admin\Documents\GAN_SQLi\Skill\label-sqli\scripts\prepare_pilot.py"
```

**Output**: `Asset\LabelData\pilot_10k.csv` — 10,000 rows, cột `payload`

---

## BƯỚC 2: AI REVIEWER — CHAT MODE (KHÔNG CẦN API)

**File đã có sẵn**: `Skill\label-sqli\scripts\ai_reviewer.py`

**Cách hoạt động — hoàn toàn file-based, không cần API key:**

```
Pipeline chạy Phase 1
        |
        v
Ghi prompt files vào:   <work_dir>/prompts/batch_000.txt
                                           batch_001.txt  ...
        |
        v
[USER ACTION] Mở từng file → copy vào chat AI (Claude.ai / ChatGPT / Gemini / bất kỳ)
              Copy response → lưu vào:  <work_dir>/responses/batch_000.txt
                                                              batch_001.txt  ...
        |
        v
Pipeline tự động đọc response files → parse JSON → tiếp tục
```

**Resumable**: nếu dừng giữa chừng, chạy lại — các batch đã có response sẽ tự động skip.

**Work dir mặc định**: `Asset/LabelData/chat_review/`

---

## BƯỚC 3: run_labeling.py — ĐÃ CÓ SẴN, KHÔNG CẦN SỬA

**File**: `Skill\label-sqli\scripts\run_labeling.py`

Các flag liên quan:
```
--work_dir   <path>   Thư mục chứa prompts/ và responses/ (mặc định: <output_dir>/chat_review/)
--batch_size <int>    Số payloads mỗi batch (mặc định 50)
--budget_cap <int>    Số hàng tối đa gửi cho AI (mặc định 50000)
--dry_run             Không hỏi user, trả về mock labels (để test)
```

---

## BƯỚC 4: TẠO EVALUATE SCRIPT

**Tạo file**: `Skill\label-sqli\scripts\evaluate_pilot.py`

```python
"""
evaluate_pilot.py -- Evaluate pilot labeling results
6 metrics: entropy, kappa, calibration, cell coverage, label source, ground truth overlap

Usage:
    python evaluate_pilot.py \
        --labeled Asset/LabelData/pilot_labeled.csv \
        --ground_truth Asset/LabelData/combined_labeled_data.csv \
        --output Asset/LabelData/pilot_eval_report.md
"""
import sys
import io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import argparse
import math
import pandas as pd
from pathlib import Path

def entropy(counts_normalized):
    return -sum(p * math.log2(p) for p in counts_normalized if p > 0)

def cohen_kappa(a, b):
    from sklearn.metrics import cohen_kappa_score
    return cohen_kappa_score(a, b)

def run_evaluation(labeled_path, ground_truth_path, output_path):
    df = pd.read_csv(labeled_path, encoding='utf-8-sig')
    gt = pd.read_csv(ground_truth_path, encoding='utf-8-sig')
    n = len(df)
    lines = [f"# Pilot Evaluation Report\n", f"**Rows**: {n:,}\n"]

    # --- Metric 1: Type Entropy ---
    p = df['sqli_type'].value_counts(normalize=True)
    H = entropy(p.values)
    status = "[OK]" if H > 2.0 else "[WARN]"
    lines.append(f"## Metric 1: Type Entropy")
    lines.append(f"{status} H = {H:.3f} bits (target > 2.0, max = 2.32)")
    lines.append(f"\n{df['sqli_type'].value_counts().to_string()}\n")

    # --- Metric 2: Cohen's Kappa (if both reviewers available) ---
    if 'claude_label' in df.columns and 'gpt_label' in df.columns:
        ai_df = df[df['claude_label'].notna() & df['gpt_label'].notna()]
        if len(ai_df) > 0:
            try:
                kappa = cohen_kappa(ai_df['claude_label'].tolist(), ai_df['gpt_label'].tolist())
                k_status = "[OK]" if kappa > 0.60 else "[WARN]"
                lines.append(f"## Metric 2: Cohen's Kappa (Claude vs GPT)")
                lines.append(f"{k_status} kappa = {kappa:.4f} (target > 0.60)")
                lines.append(f"Rows compared: {len(ai_df):,}\n")
            except Exception as e:
                lines.append(f"## Metric 2: Cohen's Kappa\n[SKIP] {e}\n")
    else:
        lines.append("## Metric 2: Cohen's Kappa\n[SKIP] --reviewer both not used\n")

    # --- Metric 3: Confidence Calibration ---
    lines.append("## Metric 3: Confidence Calibration")
    bins = [(0.0, 0.5), (0.5, 0.7), (0.7, 0.85), (0.85, 1.01)]
    if 'claude_label' in df.columns and 'gpt_label' in df.columns:
        for lo, hi in bins:
            mask = (df['confidence'] >= lo) & (df['confidence'] < hi)
            sub = df[mask]
            if len(sub) > 0:
                agree_rate = (sub['claude_label'] == sub['gpt_label']).mean()
                lines.append(f"  [{lo:.2f}-{hi:.2f}): n={len(sub):,}, agree={agree_rate:.1%}")
    else:
        conf = df['confidence']
        lines.append(f"  mean={conf.mean():.3f}, median={conf.median():.3f}, "
                     f"min={conf.min():.3f}, max={conf.max():.3f}")
    lines.append("")

    # --- Metric 4: 20-Cell Coverage ---
    TYPES   = ['time_blind', 'boolean_blind', 'union_based', 'error_based', 'benign']
    ENGINES = ['mysql', 'postgres', 'oracle', 'mssql', 'sqlite', 'unknown']
    lines.append("## Metric 4: 20-Cell Coverage (sqli_type x db_engine)")
    pivot = df.groupby(['sqli_type', 'db_engine']).size().unstack(fill_value=0)
    sparse = []
    for t in TYPES:
        row = []
        for e in ENGINES:
            cnt = pivot.at[t, e] if (t in pivot.index and e in pivot.columns) else 0
            row.append(f"{cnt:4d}")
            if cnt < 10:
                sparse.append(f"{t} x {e}: {cnt}")
        lines.append(f"  {t:<18} " + " ".join(row))
    if sparse:
        lines.append(f"\n[WARN] Sparse cells (< 10 rows): {len(sparse)}")
        for s in sparse:
            lines.append(f"  - {s}")
    else:
        lines.append("\n[OK] No sparse cells")
    lines.append("")

    # --- Metric 5: Label Source Distribution ---
    lines.append("## Metric 5: Label Source Distribution")
    src = df['label_source'].value_counts()
    for s, cnt in src.items():
        pct = cnt / n * 100
        flag = ""
        if s == 'disagree_no_ai' and pct > 5:
            flag = " [WARN: increase budget_cap]"
        if s == 'unlabeled' and pct > 2:
            flag = " [WARN: pipeline bug?]"
        lines.append(f"  {str(s):<35} {cnt:>6,}  ({pct:.1f}%){flag}")
    lines.append("")

    # --- Metric 6: Ground Truth Overlap ---
    lines.append("## Metric 6: Overlap with Old Labels (combined_labeled_data.csv)")
    payload_col_gt = 'payload_norm' if 'payload_norm' in gt.columns else 'payload'
    payload_col_new = 'payload' if 'payload' in df.columns else 'payload_norm'
    merged = df.merge(gt, left_on=payload_col_new, right_on=payload_col_gt, suffixes=('_new', '_old'))
    if len(merged) == 0:
        lines.append("[INFO] No overlapping payloads found between pilot and ground truth")
    else:
        agree = (merged['sqli_type_new'] == merged['sqli_type_old']).mean()
        flag = "[OK]" if agree >= 0.40 else "[WARN: red flag]"
        lines.append(f"{flag} Overlap rows: {len(merged):,}")
        lines.append(f"     Agreement rate: {agree:.1%} (target >= 40%)")
    lines.append("")

    # Write report
    report = "\n".join(lines)
    Path(output_path).write_text(report, encoding='utf-8')
    print(f"[OK] Report written to: {output_path}")
    print("\n" + report)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--labeled',       required=True)
    parser.add_argument('--ground_truth',  required=True)
    parser.add_argument('--output',        required=True)
    args = parser.parse_args()
    run_evaluation(args.labeled, args.ground_truth, args.output)
```

---

## BƯỚC 5: CHẠY PIPELINE

```bash
# 1. Chuẩn bị 10K
python "C:\Users\Admin\Documents\GAN_SQLi\Skill\label-sqli\scripts\prepare_pilot.py"

# 2. Dry run (không hỏi user, mock labels — để kiểm tra logic)
python "C:\Users\Admin\Documents\GAN_SQLi\Skill\label-sqli\scripts\run_labeling.py" ^
    --input "C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\Testing\Testing_data.csv" ^
    --output "C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\test_labeled_dryrun.csv" ^
    --dry_run

# 3. Full run — chat mode (không cần API key nào)
#    Pipeline sẽ tạm dừng và hỏi user paste từng batch vào chat AI
python "C:\Users\Admin\Documents\GAN_SQLi\Skill\label-sqli\scripts\run_labeling.py" ^
    --input "C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\Testing\Testing_data.csv" ^
    --output "C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\test_labeled.csv" ^
    --work_dir "C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\chat_review" ^
    --batch_size 50

# 4. Evaluate
python "C:\Users\Admin\Documents\GAN_SQLi\Skill\label-sqli\scripts\evaluate_pilot.py" ^
    --labeled "C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\test_labeled.csv" ^
    --ground_truth "C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\combined_labeled_data.csv" ^
    --output "C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\test_eval_report.md"
```

### Workflow chi tiết khi chạy bước 3:

```
Terminal hiển thị:
  [ACTION] Batch 1/60 (50 payloads)
  Prompt : C:\...\chat_review\prompts\batch_000.txt
  Save response to: C:\...\chat_review\responses\batch_000.txt
  Press Enter when response file is ready...

User làm:
  1. Mở  chat_review\prompts\batch_000.txt
  2. Copy toàn bộ nội dung
  3. Paste vào Claude.ai / ChatGPT / Gemini / bất kỳ chat AI
  4. Copy response từ chat AI
  5. Lưu vào  chat_review\responses\batch_000.txt
  6. Nhấn Enter trong terminal

Pipeline tự động đọc và tiếp tục batch tiếp theo.
Ctrl+C khi đang ở bước input → bỏ qua batch đó (fallback label).
```

---

## DEPENDENCIES

```bash
pip install scikit-learn scipy pandas pyarrow
```

**Không cần API key. Không cần cài anthropic/openai/google.**
Chat AI reviewer hoạt động hoàn toàn qua file — user tự paste vào bất kỳ chat AI nào.

---

## OUTPUT FILES

| File | Mô tả |
|------|-------|
| `Asset/LabelData/test_labeled_10k.csv` | Chuẩn bị input 10K rows (cột: payload) |
| `Asset/LabelData/test_labeled_dryrun.csv` | Dry run output (mock labels) |
| `Asset/LabelData/test_labeled.csv` | Output đã label (30+ columns) |
| `Asset/LabelData/test_eval_report.md` | Báo cáo 6 metrics |

---

## PASS/FAIL CRITERIA

| Metric | Pass | Fail |
|--------|------|------|
| Type entropy H | > 2.0 bits | < 1.5 bits |
| Cohen's Kappa κ | > 0.60 | < 0.40 |
| Sparse cells (< 10 rows) | 0 cells | > 5 cells |
| disagree_no_ai % | < 5% | > 10% |
| unlabeled % | < 2% | > 5% |
| Ground truth agreement | > 40% | < 30% |

---

## SUMMARY — Thứ Tự Triển Khai

```
1. prepare_pilot.py    [TẠO MỚI + CHẠY]   → test_labeled_10k.csv (copy từ Testing_data.csv)
2. ai_reviewer.py      [ĐÃ CÓ SẴN]        → chat mode, không cần API
3. run_labeling.py     [ĐÃ CÓ SẴN]        → dùng --work_dir + --batch_size
4. evaluate_pilot.py   [TẠO MỚI]           → metrics script
5. dry_run             [CHẠY]              → verify không crash
6. full_run            [CHẠY]              → test_labeled.csv
7. evaluate            [CHẠY]              → test_eval_report.md
```

*Agent: đọc file này, thực hiện đúng thứ tự trên, báo kết quả sau mỗi bước.*
