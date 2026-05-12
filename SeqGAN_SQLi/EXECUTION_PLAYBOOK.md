# Execution Playbook — Triển khai SeqGAN_SQLi V2

> **Đối tượng**: Claude Code chạy 1 lần từ đầu đến cuối.
> **Tài liệu kiến trúc**: `Guiding_V2.md`
> **Tài liệu lý luận**: `timeline/DEEP_ANALYSIS_10_PERSPECTIVES.md`
> **Ngày cập nhật**: 2026-05-12
> **Estimated total time**: 20-25 giờ (bao gồm training).

## DATASET UPDATE (2026-05-12)

Re-labeling đã hoàn tất. Dữ liệu mới:

| File | Path | Mục đích |
|---|---|---|
| **SQLi train data** | `C:\Projects\GAN_SQLi\Asset\LabelData\latest_relabel_data.csv` | Dataset chính (17,821 rows) |
| **Benign source** | `C:\Projects\GAN_SQLi\Asset\LabelData\combined_labeled_data.csv` | Chỉ extract benign (19,669 rows) |

**Thống kê `latest_relabel_data.csv`:**
- Columns: `id, payload_norm, payload_delex, sqli_type, db_engine, confidence`
- sqli_types: `error_based (7315), boolean_blind (6335), time_blind (2283), union_based (1888)` → **4 types** (không phải 8 như Guiding_V2 plan)
- Confidence: mean=0.93, gold(≥0.95)=~60%, silver(0.80-0.94)=~25%, bronze(<0.80)=~15%
- De-lex đã có sẵn trong cột `payload_delex`

**Ảnh hưởng đến implementation:**
- `num_attack_types = 4` (không phải 8)
- Không cần chạy de-lex script riêng (dùng `payload_delex` trực tiếp)
- Phase 0 re-labeling: **DONE** — bỏ qua STEP 0.8 multi-source crawl
- Biến môi trường: `$env:DATASET_PATH = "C:\Projects\GAN_SQLi\Asset\LabelData\latest_relabel_data.csv"`

**Phase 0 status: COMPLETE** (re-labeling done by user)

---

## Cách Đọc Playbook

Mỗi bước có format:

```
STEP X.Y: [Tên bước]
├─ WHY: Tại sao cần làm
├─ PRECOND: Điều kiện tiên quyết
├─ ACTION: Lệnh/code chính xác
├─ VALIDATE: Cách verify thành công
└─ ON_FAIL: Debug steps nếu thất bại
```

**Quy tắc thực thi:**
- Thực thi tuần tự theo thứ tự STEP X.Y
- KHÔNG skip step (kể cả tưởng đơn giản)
- Nếu một step fail và `ON_FAIL` không giải quyết được → STOP, log và báo user
- Sau mỗi PHASE, commit Git với message `Phase X complete: <summary>`
- Time estimate là expected wall time với 1× RTX 3060

---

## PRE-FLIGHT: Kiểm tra Môi trường

### STEP 0.1: Verify Working Directory

**WHY:** Tất cả lệnh giả định CWD là project root.

**ACTION:**
```powershell
cd C:\Projects\GAN_SQLi
Get-Location
```

**VALIDATE:** Output là `C:\Projects\GAN_SQLi`.

**ON_FAIL:** `Set-Location C:\Projects\GAN_SQLi` thủ công.

---

### STEP 0.2: Verify Python & Dependencies

**WHY:** Cần Python 3.10+, PyTorch CUDA, các lib mới.

**ACTION:**
```powershell
python --version
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

Nếu thiếu deps, install:
```powershell
pip install torch transformers numpy pandas sqlparse sqlglot pyyaml tqdm tensorboard requests scikit-learn xgboost imbalanced-learn
```

**VALIDATE:** Python ≥ 3.10; CUDA True (nếu có GPU); device hiển thị tên GPU.

**ON_FAIL:** Cài Python 3.10 từ python.org; cài CUDA 11.8+ nếu có GPU.

---

### STEP 0.3: Verify Existing Files

**WHY:** V2 dựa trên codebase V1 hiện có.

**ACTION:**
```powershell
Test-Path SeqGAN_SQLi/Guiding_V2.md
Test-Path SeqGAN_SQLi/src/generator.py
Test-Path SeqGAN_SQLi/checkpoints/mle_best.pt
Test-Path SeqGAN_SQLi/data/train.csv
Test-Path "C:/Projects/GAN_SQLi/Asset/Data/master_sqli.csv" -ErrorAction SilentlyContinue
```

**VALIDATE:** Top 4 path tồn tại True. Master CSV có thể không có.

**ON_FAIL:** Nếu V1 file thiếu, chạy `python SeqGAN_SQLi/run_full_pipeline.py` trước. Hoặc fallback dùng `combined_labeled_data.csv` ở project root.

---

### STEP 0.4: Find Source Dataset

**WHY:** Cần xác định path chính xác của dataset gốc.

**ACTION:**
```powershell
Get-ChildItem -Path C:\Projects\GAN_SQLi -Filter "combined_labeled_data*.csv" -Recurse | Select-Object FullName
Get-ChildItem -Path C:\Projects\GAN_SQLi -Filter "*.csv" | Where-Object { $_.Name -match "labeled|master|sqli" } | Select-Object FullName, Length
```

**VALIDATE:** Tìm thấy ít nhất 1 file CSV với attack labels.

**ON_FAIL:** Hỏi user path chính xác của dataset gốc.

**SAVE:** Note path dataset gốc vào biến môi trường:
```powershell
$env:DATASET_PATH = "<path tìm được>"
```

---

## PHASE 0: DATA AUDIT & RE-PREP

### STEP 0.5: Create Phase 0 Output Directory

**ACTION:**
```powershell
New-Item -ItemType Directory -Force -Path SeqGAN_SQLi/data/v2
New-Item -ItemType Directory -Force -Path SeqGAN_SQLi/data/v2/audit
```

**VALIDATE:** 2 thư mục tồn tại.

---

### STEP 0.6: Write Bias Audit Script

**WHY:** Verify giả thuyết bias từ G4 (88.6% target users/accounts, 60.6% Oracle XMLTYPE).

**ACTION:** Tạo file `SeqGAN_SQLi/data/audit_bias.py`:

```python
"""
audit_bias.py — Phát hiện bias trong dataset SQLi.
Output: report ở stdout + JSON ở data/v2/audit/bias_report.json
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd


def normalize_skeleton(payload: str) -> str:
    """Strip placeholders và whitespace để có structural skeleton."""
    s = re.sub(r"__\w+__", "_", str(payload))
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def audit(csv_path: str, out_dir: str):
    df = pd.read_csv(csv_path)
    print(f"\n=== DATASET BIAS AUDIT ===")
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    payload_col = next(
        (c for c in ["payload_norm", "payload", "payload_delex", "query"] if c in df.columns),
        None,
    )
    if not payload_col:
        raise ValueError("Không tìm thấy cột payload trong CSV")

    type_col = next(
        (c for c in ["sqli_type", "type", "attack_type", "label"] if c in df.columns),
        None,
    )

    report = {
        "total_rows": len(df),
        "payload_col": payload_col,
        "type_col": type_col,
    }

    # Test 1: Source diversity
    if "source" in df.columns:
        source_counts = df["source"].value_counts().to_dict()
        report["source_diversity"] = source_counts
        print(f"\n[Test 1] Source diversity:")
        for src, cnt in source_counts.items():
            print(f"  {src}: {cnt} ({cnt/len(df)*100:.1f}%)")
        max_source_pct = max(source_counts.values()) / len(df) * 100
        report["max_source_pct"] = max_source_pct
        if max_source_pct > 60:
            print(f"  WARNING: {max_source_pct:.1f}% từ 1 source - bias rất nặng")
    else:
        print(f"\n[Test 1] KHÔNG CÓ source column - không thể audit source diversity")
        report["source_diversity"] = None

    # Test 2: Skeleton diversity
    df["skeleton"] = df[payload_col].apply(normalize_skeleton)
    unique_skels = df["skeleton"].nunique()
    skeleton_ratio = unique_skels / len(df)
    report["skeleton_uniqueness"] = {
        "unique": unique_skels,
        "total": len(df),
        "ratio": skeleton_ratio,
    }
    print(f"\n[Test 2] Unique skeletons: {unique_skels} / {len(df)} = {skeleton_ratio*100:.2f}%")
    if skeleton_ratio < 0.05:
        print(f"  CRITICAL: <5% uniqueness - structural bias nặng")
    elif skeleton_ratio < 0.20:
        print(f"  WARNING: <20% uniqueness - structural bias đáng kể")

    # Test 3: Per-type skeleton diversity
    if type_col:
        per_type = {}
        print(f"\n[Test 3] Per-type skeleton uniqueness:")
        for sqli_type, group in df.groupby(type_col):
            ratio = group["skeleton"].nunique() / max(len(group), 1)
            per_type[str(sqli_type)] = {
                "count": int(len(group)),
                "unique_skeletons": int(group["skeleton"].nunique()),
                "ratio": ratio,
            }
            warn = "  [BIAS]" if ratio < 0.10 else ""
            print(f"  {sqli_type}: {len(group)} rows, {group['skeleton'].nunique()} skeletons ({ratio*100:.1f}%){warn}")
        report["per_type"] = per_type

    # Test 4: Top frequent tokens (xem dataset có dominated bởi 1 pattern không)
    all_tokens = []
    for p in df[payload_col].astype(str):
        all_tokens.extend(p.lower().split())
    token_counts = Counter(all_tokens)
    top_20 = token_counts.most_common(20)
    report["top_tokens"] = [{"token": t, "count": c} for t, c in top_20]
    print(f"\n[Test 4] Top 20 tokens:")
    for t, c in top_20:
        pct = c / len(all_tokens) * 100
        flag = "  [DOMINANT]" if pct > 5 else ""
        print(f"  '{t}': {c} ({pct:.2f}%){flag}")

    # Test 5: Target table check (G4 specific concern)
    table_patterns = re.compile(r"from\s+(\w+)|insert\s+into\s+(\w+)|update\s+(\w+)", re.IGNORECASE)
    target_tables = []
    for p in df[payload_col].astype(str):
        for match in table_patterns.finditer(p):
            for g in match.groups():
                if g:
                    target_tables.append(g.lower())
    if target_tables:
        table_counts = Counter(target_tables).most_common(10)
        report["top_target_tables"] = [{"table": t, "count": c} for t, c in table_counts]
        print(f"\n[Test 5] Top target tables:")
        total_table_refs = len(target_tables)
        for t, c in table_counts:
            pct = c / total_table_refs * 100
            flag = "  [BIAS]" if pct > 20 else ""
            print(f"  {t}: {c} ({pct:.1f}%){flag}")

    # Write report
    out_path = Path(out_dir) / "bias_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved: {out_path}")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to dataset CSV")
    parser.add_argument("--out_dir", default="SeqGAN_SQLi/data/v2/audit")
    args = parser.parse_args()
    audit(args.csv, args.out_dir)
```

**VALIDATE:** File tồn tại, syntax OK:
```powershell
python -c "import ast; ast.parse(open('SeqGAN_SQLi/data/audit_bias.py').read()); print('OK')"
```

---

### STEP 0.7: Run Bias Audit

**ACTION:**
```powershell
python SeqGAN_SQLi/data/audit_bias.py --csv $env:DATASET_PATH --out_dir SeqGAN_SQLi/data/v2/audit
```

**VALIDATE:** Output có 5 tests, không error; file `bias_report.json` tồn tại.

**ON_FAIL:** Check column names trong CSV — có thể cần sửa `payload_col` / `type_col` heuristics.

**INSPECT:**
```powershell
Get-Content SeqGAN_SQLi/data/v2/audit/bias_report.json | Select-String "ratio|max_source"
```

**EXPECTED FINDINGS:**
- Skeleton uniqueness < 20% (xác nhận G4 hypothesis)
- Per-type uniqueness của error_based < 10%
- Top target tables: users/accounts dominant

---

### STEP 0.8: Multi-Source Crawl (OPTIONAL - SKIP nếu không có internet)

**WHY:** Giảm source bias từ G7-P1. Đây là phương án tốn thời gian nhất; có thể skip nếu chỉ làm prototype.

**ACTION:** Nếu skip, tạo placeholder source column:
```powershell
python -c "
import pandas as pd
df = pd.read_csv('$env:DATASET_PATH')
if 'source' not in df.columns:
    df['source'] = 'original'
    df.to_csv('SeqGAN_SQLi/data/v2/dataset_with_source.csv', index=False)
    print(f'Added source column, saved {len(df)} rows')
else:
    df.to_csv('SeqGAN_SQLi/data/v2/dataset_with_source.csv', index=False)
    print(f'Source column existed, copied {len(df)} rows')
"
```

**Nếu thực hiện crawl (advanced):** Tạo script riêng `data/multi_source_loader.py` với 5-7 nguồn (PortSwigger cheatsheet, HackTricks, sqlmap tampers...). Implementation chi tiết để user tự làm — tốn 2-3 ngày.

**VALIDATE:** File `data/v2/dataset_with_source.csv` tồn tại.

---

### STEP 0.9: Write Tiered Confidence Filter

**WHY:** G7-P3 — phân tier gold/silver/bronze.

**ACTION:** Tạo `SeqGAN_SQLi/data/tier_filter.py`:

```python
"""
tier_filter.py — Phân tier confidence thành gold/silver/bronze.
"""
import argparse
from pathlib import Path

import pandas as pd


def tier_dataset(csv_path: str, out_path: str):
    df = pd.read_csv(csv_path)

    if "confidence" not in df.columns:
        print("WARNING: No 'confidence' column - assign default 0.85 (silver)")
        df["confidence"] = 0.85

    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0.5)

    def tier(c):
        if c >= 0.95:
            return "gold"
        elif c >= 0.80:
            return "silver"
        else:
            return "bronze"

    df["tier"] = df["confidence"].apply(tier)

    counts = df["tier"].value_counts().to_dict()
    print(f"Tier distribution:")
    for t in ["gold", "silver", "bronze"]:
        c = counts.get(t, 0)
        print(f"  {t}: {c} ({c/len(df)*100:.1f}%)")

    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    tier_dataset(args.csv, args.out)
```

**Run:**
```powershell
python SeqGAN_SQLi/data/tier_filter.py --csv SeqGAN_SQLi/data/v2/dataset_with_source.csv --out SeqGAN_SQLi/data/v2/dataset_tiered.csv
```

**VALIDATE:** File `dataset_tiered.csv` tồn tại, có column `tier`. Gold tier ≥ 5% total.

---

### STEP 0.10: Re-split với Stratification

**WHY:** Đảm bảo train/val/test balanced theo type × source × tier.

**ACTION:** Tạo `SeqGAN_SQLi/data/resplit_v2.py`:

```python
"""
resplit_v2.py — Stratified split bởi (sqli_type, source).
Output: data/v2/{train,val,test}.csv
"""
import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit


def resplit(csv_path: str, out_dir: str, seed: int = 42):
    df = pd.read_csv(csv_path)
    out_dir_p = Path(out_dir)
    out_dir_p.mkdir(parents=True, exist_ok=True)

    type_col = next((c for c in ["sqli_type", "type", "label"] if c in df.columns), None)
    if type_col is None:
        df["sqli_type"] = "unknown"
        type_col = "sqli_type"

    if "source" not in df.columns:
        df["source"] = "original"

    # Compound stratification
    df["_strat"] = df[type_col].astype(str) + "|" + df["source"].astype(str)

    # Filter rare combinations (< 2 samples) — không stratify được
    strat_counts = df["_strat"].value_counts()
    valid_strat = strat_counts[strat_counts >= 2].index
    df_strat = df[df["_strat"].isin(valid_strat)].copy()
    df_rare = df[~df["_strat"].isin(valid_strat)].copy()
    print(f"Stratifiable rows: {len(df_strat)} / Rare: {len(df_rare)} (put in train)")

    # First split: 70% train, 30% temp
    sss1 = StratifiedShuffleSplit(n_splits=1, test_size=0.30, random_state=seed)
    train_idx, temp_idx = next(sss1.split(df_strat, df_strat["_strat"]))
    df_train = df_strat.iloc[train_idx]
    df_temp = df_strat.iloc[temp_idx]

    # Second split: 50% val, 50% test of temp = 15% each total
    sss2 = StratifiedShuffleSplit(n_splits=1, test_size=0.50, random_state=seed)
    val_idx, test_idx = next(sss2.split(df_temp, df_temp["_strat"]))
    df_val = df_temp.iloc[val_idx]
    df_test = df_temp.iloc[test_idx]

    # Add rare samples to train
    df_train = pd.concat([df_train, df_rare], ignore_index=True)

    # Drop helper column
    for d in [df_train, df_val, df_test]:
        d.drop(columns=["_strat"], inplace=True, errors="ignore")

    df_train.to_csv(out_dir_p / "train.csv", index=False)
    df_val.to_csv(out_dir_p / "val.csv", index=False)
    df_test.to_csv(out_dir_p / "test.csv", index=False)

    print(f"Train: {len(df_train)}")
    print(f"Val:   {len(df_val)}")
    print(f"Test:  {len(df_test)}")

    # Write stratify report
    report_lines = [
        f"Split: train={len(df_train)} val={len(df_val)} test={len(df_test)}",
        f"\nPer-type distribution:",
    ]
    for split_name, split_df in [("train", df_train), ("val", df_val), ("test", df_test)]:
        report_lines.append(f"\n  {split_name}:")
        for t, c in split_df[type_col].value_counts().items():
            report_lines.append(f"    {t}: {c}")

    (out_dir_p / "stratify_report.txt").write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Stratify report: {out_dir_p / 'stratify_report.txt'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out_dir", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    resplit(args.csv, args.out_dir, args.seed)
```

**Run:**
```powershell
python SeqGAN_SQLi/data/resplit_v2.py --csv SeqGAN_SQLi/data/v2/dataset_tiered.csv --out_dir SeqGAN_SQLi/data/v2
```

**VALIDATE:** 3 file train/val/test trong `data/v2/`. Stratify report tồn tại.

---

### STEP 0.11: Prepare Tokenizer cho V2

**WHY:** Re-use V1 tokenizer (134 vocab) cho V2 baseline. Nếu muốn P2 partial de-lex, tốn thêm 2-3h — SKIP cho run đầu.

**ACTION:** Copy tokenizer vocab và đảm bảo dataset đã de-lex:
```powershell
Copy-Item SeqGAN_SQLi/data/tokenizer_vocab.json SeqGAN_SQLi/data/v2/tokenizer_vocab.json -Force
```

Verify de-lex đã được apply trong CSV:
```powershell
python -c "
import pandas as pd
df = pd.read_csv('SeqGAN_SQLi/data/v2/train.csv')
col = 'payload_norm' if 'payload_norm' in df.columns else 'payload'
print('Sample payloads:')
for p in df[col].head(5):
    print(f'  {p}')
has_placeholder = df[col].str.contains('__\w+__', regex=True).mean()
print(f'Rows with placeholder: {has_placeholder*100:.1f}%')
"
```

**VALIDATE:** ≥ 80% rows có placeholder `__STR__`/`__INT__`/etc. Nếu thấp, cần chạy de-lex.

**ON_FAIL:** Chạy lại `python SeqGAN_SQLi/data/prepare_seqgan_data.py --csv data/v2/dataset_tiered.csv --output_dir data/v2/`.

---

### STEP 0.12: Build Re-lex Dictionary

**WHY:** Cho metric `relex_uniqueness` ở Phase 5.

**ACTION:** Tạo `SeqGAN_SQLi/data/relex_dictionary.json`:

```json
{
  "__STR__": ["'admin'", "'test'", "'root'", "'user'", "'guest'"],
  "__INT__": ["1", "0", "-1", "999", "10"],
  "__HEX__": ["0x616263", "0x73797374656d", "0x61646d696e", "0x70617373", "0x726f6f74"],
  "__TABLE__": ["users", "accounts", "admin", "sessions", "products"],
  "__COL__": ["id", "username", "password", "email", "role"],
  "__IDENT__": ["xmltype", "dbms_pipe", "ctxsys", "sys_context", "user_tables"],
  "__TIME__": ["5", "10", "1", "2", "3"],
  "__BIGINT__": ["9999", "100000", "1", "0", "65535"]
}
```

**VALIDATE:**
```powershell
python -c "import json; d=json.load(open('SeqGAN_SQLi/data/relex_dictionary.json')); print(f'Placeholders: {list(d.keys())}'); print(f'Entries per: {[len(v) for v in d.values()]}')"
```

Expected: 8 keys, 5 entries each.

---

**CHECKPOINT PHASE 0:** Commit Git
```powershell
git add SeqGAN_SQLi/data/v2 SeqGAN_SQLi/data/audit_bias.py SeqGAN_SQLi/data/tier_filter.py SeqGAN_SQLi/data/resplit_v2.py SeqGAN_SQLi/data/relex_dictionary.json
git commit -m "Phase 0 complete: data audit, multi-source prep, tiered confidence, stratified split"
```

---

## PHASE 1: INFRASTRUCTURE SETUP

### STEP 1.1: Setup ModSecurity Docker

**WHY:** Real WAF Oracle cho G1.

**ACTION:** Tạo `SeqGAN_SQLi/docker/modsec/Dockerfile`:

```dockerfile
FROM owasp/modsecurity-crs:nginx-alpine

# Use OWASP CRS PL2 (paranoia level 2)
ENV PARANOIA=2
ENV ANOMALY_INBOUND=5
ENV ANOMALY_OUTBOUND=4

# Expose nginx on 8080
EXPOSE 8080

# Default config tốt, không cần override
```

Tạo `SeqGAN_SQLi/docker/modsec/docker-compose.yml`:

```yaml
version: "3.8"
services:
  modsec:
    build: .
    container_name: seqgan-modsec
    ports:
      - "8080:8080"
    environment:
      - PARANOIA=2
      - ANOMALY_INBOUND=5
      - ANOMALY_OUTBOUND=4
      - BACKEND=http://localhost:80
    restart: unless-stopped
```

**Build & run:**
```powershell
cd SeqGAN_SQLi/docker/modsec
docker-compose up -d --build
Start-Sleep -Seconds 10
docker ps --filter "name=seqgan-modsec"
cd ../../..
```

**VALIDATE:**
```powershell
$test = Invoke-WebRequest -Uri "http://localhost:8080/?id=1" -UseBasicParsing -ErrorAction SilentlyContinue
$test.StatusCode
$attack = Invoke-WebRequest -Uri "http://localhost:8080/?id=1' OR 1=1--" -UseBasicParsing -ErrorAction SilentlyContinue
$attack.StatusCode
```

Expected: Benign request → 200; attack → 403.

**ON_FAIL:**
- Nếu Docker không có: install Docker Desktop từ docker.com
- Nếu port 8080 bị chiếm: đổi port trong compose file (vd 8090)
- Nếu CRS không trigger: kiểm tra image tag, dùng `owasp/modsecurity-crs:nginx`

---

### STEP 1.2: Test WAF Oracle Wrapper Smoke

**WHY:** Verify Python có thể gọi WAF reliably.

**ACTION:** Tạo `SeqGAN_SQLi/scripts/smoke_waf.py`:

```python
"""smoke_waf.py — Test WAFOracle hoạt động."""
import requests
import time

WAF_URL = "http://localhost:8080"

KNOWN_ATTACKS = [
    "1' OR '1'='1",
    "1; DROP TABLE users--",
    "1 UNION SELECT password FROM users--",
    "<script>alert(1)</script>",
]
KNOWN_BENIGN = ["1", "admin", "hello world", "user@example.com"]


def test_payload(payload):
    try:
        resp = requests.get(WAF_URL, params={"id": payload}, timeout=5)
        return resp.status_code
    except Exception as e:
        return f"ERROR: {e}"


def main():
    print("=== WAF Smoke Test ===")
    print("\n[Attacks - expect 403]")
    for p in KNOWN_ATTACKS:
        code = test_payload(p)
        ok = "OK" if code == 403 else "FAIL"
        print(f"  [{ok}] {code} | {p[:50]}")

    print("\n[Benign - expect 200]")
    for p in KNOWN_BENIGN:
        code = test_payload(p)
        ok = "OK" if code == 200 else "FAIL"
        print(f"  [{ok}] {code} | {p[:50]}")

    # Latency check
    print("\n[Latency test - 100 calls]")
    start = time.time()
    for _ in range(100):
        test_payload("test")
    elapsed = time.time() - start
    print(f"  100 calls: {elapsed:.2f}s ({elapsed*10:.1f}ms/call)")


if __name__ == "__main__":
    main()
```

**Run:**
```powershell
python SeqGAN_SQLi/scripts/smoke_waf.py
```

**VALIDATE:** Attacks → 403, benigns → 200, latency < 100ms/call.

**ON_FAIL:** Restart container `docker-compose restart`, check logs `docker logs seqgan-modsec`.

---

**CHECKPOINT PHASE 1:** Commit
```powershell
git add SeqGAN_SQLi/docker SeqGAN_SQLi/scripts
git commit -m "Phase 1 complete: ModSecurity Docker + WAF smoke test"
```

---

## PHASE 2: COMPONENT IMPLEMENTATION

### STEP 2.1: Create WAF Oracle Module

**ACTION:** Tạo `SeqGAN_SQLi/src/waf_oracle.py`:

```python
"""
waf_oracle.py — Wrapper cho ModSecurity Docker.
"""
import re
import time
from typing import Optional

import requests


class WAFOracle:
    """
    Gọi ModSecurity Docker container, parse anomaly_score và rule match.
    """

    def __init__(
        self,
        url: str = "http://localhost:8080",
        timeout: float = 2.0,
        max_retries: int = 2,
    ):
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

    def evaluate(self, payload: str) -> dict:
        """
        Trả dict với:
          - status_code: HTTP code
          - blocked: True nếu 403
          - anomaly_score: int (parse từ header hoặc fallback)
        """
        if not payload or not isinstance(payload, str):
            return {"status_code": 0, "blocked": True, "anomaly_score": 999}

        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(
                    self.url,
                    params={"id": payload},
                    timeout=self.timeout,
                )
                blocked = resp.status_code == 403
                # ModSecurity stock không expose anomaly_score qua header
                # → suy ra từ status code
                anomaly_score = 10 if blocked else 0
                return {
                    "status_code": resp.status_code,
                    "blocked": blocked,
                    "anomaly_score": anomaly_score,
                }
            except (requests.Timeout, requests.ConnectionError) as e:
                if attempt == self.max_retries - 1:
                    return {"status_code": 0, "blocked": True, "anomaly_score": 999, "error": str(e)}
                time.sleep(0.1)

    def close(self):
        self.session.close()


def waf_boundary_reward(anomaly_score: int, threshold: int = 5) -> float:
    """
    Boundary-aware reward — cao nhất khi anomaly_score gần threshold.
    """
    if anomaly_score >= threshold:
        return -0.5
    distance = threshold - anomaly_score
    return 1.0 - (distance / threshold)
```

**VALIDATE:**
```powershell
python -c "
from SeqGAN_SQLi.src.waf_oracle import WAFOracle, waf_boundary_reward
w = WAFOracle()
print(w.evaluate('1'))
print(w.evaluate(\"1' OR '1'='1\"))
print('Reward 0:', waf_boundary_reward(0))
print('Reward 4:', waf_boundary_reward(4))
print('Reward 10:', waf_boundary_reward(10))
"
```

Expected: benign → blocked=False, attack → blocked=True. Reward(0)=0, Reward(4)=0.8, Reward(10)=-0.5.

---

### STEP 2.2: Create Custom Rules Engine

**ACTION:** Tạo `SeqGAN_SQLi/src/custom_rules.py`:

```python
"""
custom_rules.py — Kiểm tra payload có phải SQLi đúng nghĩa không.
Chống reward hacking — payload chỉ bypass OWASP qua trick encoding
nhưng không thực sự là SQLi sẽ fail ở đây.
"""
import re
from typing import List, Tuple


class CustomRuleEngine:
    """Rule-based SQLi validity checker."""

    KEYWORDS = [
        "union", "select", "or 1", "and 1", "or '", "and '",
        "sleep", "benchmark", "waitfor", "pg_sleep",
        "extractvalue", "updatexml", "xmltype", "concat",
        "drop", "insert", "delete", "update", "alter",
    ]
    QUOTE_OPS = ["'", '"', "--", "/*", "*/", "#", ";", "||", "&&"]
    RELATIONAL = re.compile(r"[=<>]|union|select|order\s+by|having|group\s+by", re.I)
    BENIGN_LIKE = re.compile(r"^[\w\s]+$")

    def __init__(self, min_length: int = 5):
        self.min_length = min_length

    def rule_1_keyword(self, p: str) -> bool:
        """≥ 1 SQLi keyword."""
        pl = p.lower()
        return any(kw in pl for kw in self.KEYWORDS)

    def rule_2_quote_or_op(self, p: str) -> bool:
        """≥ 1 quoting/comment/operator."""
        return any(c in p for c in self.QUOTE_OPS)

    def rule_3_length(self, p: str) -> bool:
        """Length sau strip ≥ min_length."""
        return len(p.strip()) >= self.min_length

    def rule_4_not_benign(self, p: str) -> bool:
        """KHÔNG match benign-like pattern."""
        return not self.BENIGN_LIKE.match(p.strip())

    def rule_5_relational(self, p: str) -> bool:
        """Có operator/keyword query."""
        return bool(self.RELATIONAL.search(p))

    def evaluate(self, payload: str) -> Tuple[float, List[bool]]:
        """
        Returns:
            (pass_ratio, [bool_per_rule])
        """
        if not payload or not isinstance(payload, str):
            return 0.0, [False] * 5

        results = [
            self.rule_1_keyword(payload),
            self.rule_2_quote_or_op(payload),
            self.rule_3_length(payload),
            self.rule_4_not_benign(payload),
            self.rule_5_relational(payload),
        ]
        ratio = sum(results) / len(results)
        return ratio, results

    def score(self, payload: str) -> float:
        """Alias cho evaluate() trả về chỉ ratio."""
        return self.evaluate(payload)[0]
```

**VALIDATE:**
```powershell
python -c "
from SeqGAN_SQLi.src.custom_rules import CustomRuleEngine
e = CustomRuleEngine()
print('Attack:', e.score(\"1' OR '1'='1\"))
print('Benign:', e.score('hello world'))
print('Trivial:', e.score('--'))
print('Garbage:', e.score('asdf'))
"
```

Expected: Attack ~0.8-1.0, Benign ~0.2-0.4, Trivial ~0.4, Garbage ~0.2.

---

### STEP 2.3: Create SQL Parser Gate

**ACTION:** Tạo `SeqGAN_SQLi/src/parser_gate.py`:

```python
"""
parser_gate.py — Syntax validity check sử dụng sqlparse + sqlglot.
"""
import sqlparse

try:
    import sqlglot
    HAS_SQLGLOT = True
except ImportError:
    HAS_SQLGLOT = False


class SQLParserGate:
    """
    Wrap payload trong context query và kiểm tra parse được không.
    """

    def __init__(self, dialect: str = "mysql", use_sqlglot: bool = True):
        self.dialect = dialect
        self.use_sqlglot = use_sqlglot and HAS_SQLGLOT

    def evaluate(self, payload: str) -> int:
        if not payload or not isinstance(payload, str):
            return 0
        wrapped = f"SELECT * FROM dummy WHERE id={payload}"

        # Sqlparse pass dễ
        try:
            parsed = sqlparse.parse(wrapped)
            if not parsed or not parsed[0].tokens:
                return 0
        except Exception:
            return 0

        # Sqlglot strict check
        if self.use_sqlglot:
            try:
                sqlglot.parse_one(wrapped, dialect=self.dialect)
            except sqlglot.errors.ParseError:
                return 0
            except Exception:
                return 0

        return 1
```

**VALIDATE:**
```powershell
python -c "
from SeqGAN_SQLi.src.parser_gate import SQLParserGate
g = SQLParserGate()
print('Valid:', g.evaluate(\"1 OR 1=1\"))
print('Quote attack:', g.evaluate(\"'1' OR '1'='1\"))
print('Invalid:', g.evaluate('garbage @#\$'))
print('Empty:', g.evaluate(''))
"
```

Expected: Valid=1, Quote attack=1, Invalid=0, Empty=0.

---

### STEP 2.4: Create DB Sandbox

**ACTION:** Tạo `SeqGAN_SQLi/src/db_sandbox.py`:

```python
"""
db_sandbox.py — SQLite in-memory để check payload chạy được không.
"""
import sqlite3
import threading


class DBSandbox:
    """Thread-safe SQLite sandbox để evaluate payload."""

    def __init__(self):
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.cur = self.conn.cursor()
        self._setup_schema()

    def _setup_schema(self):
        try:
            self.cur.execute("CREATE TABLE dummy (id INTEGER, name TEXT, email TEXT)")
            self.cur.execute("INSERT INTO dummy VALUES (1, 'admin', 'admin@test.com')")
            self.cur.execute("INSERT INTO dummy VALUES (2, 'user', 'user@test.com')")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

    def evaluate(self, payload: str) -> int:
        """
        Returns 1 nếu payload chạy được trong context, 0 nếu raise error.
        """
        if not payload or not isinstance(payload, str):
            return 0

        wrapped = f"SELECT * FROM dummy WHERE id={payload}"

        with self._lock:
            try:
                self.cur.execute(wrapped)
                _ = self.cur.fetchall()
                return 1
            except (sqlite3.OperationalError, sqlite3.Warning, sqlite3.DatabaseError):
                return 0
            except Exception:
                return 0

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass
```

**VALIDATE:**
```powershell
python -c "
from SeqGAN_SQLi.src.db_sandbox import DBSandbox
d = DBSandbox()
print('Valid 1:', d.evaluate('1'))
print('Or attack:', d.evaluate('1 OR 1=1'))
print('Union:', d.evaluate('1 UNION SELECT name FROM dummy'))
print('Invalid:', d.evaluate('garbage'))
print('Empty:', d.evaluate(''))
d.close()
"
```

Expected: Valid 1=1, Or attack=1, Union=1, Invalid=0, Empty=0.

---

### STEP 2.5: Create AST Fingerprint Tracker

**ACTION:** Tạo `SeqGAN_SQLi/src/ast_tracker.py`:

```python
"""
ast_tracker.py — Track AST subtree fingerprints để measure structural diversity.
"""
from collections import OrderedDict
from typing import Set

import sqlparse


class ASTFingerprintTracker:
    """
    Compute subtree fingerprints depth=3, track diversity.
    """

    def __init__(self, max_cache_size: int = 10000, depth: int = 3):
        self.cache: OrderedDict = OrderedDict()  # fingerprint_hash → count
        self.max_size = max_cache_size
        self.depth = depth
        self.parse_fail_count = 0
        self.total_count = 0

    def _extract_subtrees(self, node, current_depth=0):
        if current_depth >= self.depth:
            return [hash(str(getattr(node, "ttype", None)))]

        subtrees = []
        ttype_hash = hash(str(getattr(node, "ttype", None)))

        child_hashes = []
        for child in getattr(node, "tokens", []):
            child_hashes.extend(self._extract_subtrees(child, current_depth + 1))

        # Subtree = node_type + children hashes
        if child_hashes:
            combined = hash((ttype_hash, tuple(sorted(child_hashes[:5]))))
        else:
            combined = ttype_hash
        subtrees.append(combined)
        subtrees.extend(child_hashes)
        return subtrees

    def fingerprint(self, payload: str) -> Set[int]:
        if not payload or not isinstance(payload, str):
            return set()
        self.total_count += 1
        try:
            wrapped = f"SELECT * FROM dummy WHERE id={payload}"
            parsed = sqlparse.parse(wrapped)
            if not parsed:
                self.parse_fail_count += 1
                return set()
            return set(self._extract_subtrees(parsed[0]))
        except Exception:
            self.parse_fail_count += 1
            return set()

    def novelty(self, payload: str) -> float:
        """
        Returns: 1.0 nếu hoàn toàn mới, 0.0 nếu đã thấy hết.
        """
        fp = self.fingerprint(payload)
        if not fp:
            return 0.0
        if not self.cache:
            for f in fp:
                self.cache[f] = 1
            return 1.0

        new_count = sum(1 for f in fp if f not in self.cache)
        novelty_score = new_count / len(fp)

        for f in fp:
            if f in self.cache:
                self.cache[f] += 1
                self.cache.move_to_end(f)
            else:
                self.cache[f] = 1
                if len(self.cache) > self.max_size:
                    self.cache.popitem(last=False)

        return novelty_score

    def reset(self):
        self.cache.clear()
        self.parse_fail_count = 0
        self.total_count = 0

    def get_stats(self) -> dict:
        return {
            "cache_size": len(self.cache),
            "parse_fail_rate": self.parse_fail_count / max(self.total_count, 1),
            "total_seen": self.total_count,
        }
```

**VALIDATE:**
```powershell
python -c "
from SeqGAN_SQLi.src.ast_tracker import ASTFingerprintTracker
t = ASTFingerprintTracker()
print('Novelty 1st:', t.novelty(\"1 OR 1=1\"))
print('Novelty same:', t.novelty(\"1 OR 1=1\"))
print('Novelty diff:', t.novelty(\"1 UNION SELECT password FROM users\"))
print('Stats:', t.get_stats())
"
```

Expected: 1st=1.0, same<0.3, diff>0.5.

---

### STEP 2.6: Create Reward Cache

**ACTION:** Tạo `SeqGAN_SQLi/src/reward_cache.py`:

```python
"""
reward_cache.py — LRU cache cho composite reward.
"""
from collections import OrderedDict
from typing import Any, Callable


class RewardCache:
    """LRU cache: payload_hash → reward value."""

    def __init__(self, max_size: int = 100000):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, payload: str) -> Any:
        h = hash(payload)
        if h in self.cache:
            self.hits += 1
            self.cache.move_to_end(h)
            return self.cache[h]
        self.misses += 1
        return None

    def set(self, payload: str, value: Any):
        h = hash(payload)
        self.cache[h] = value
        self.cache.move_to_end(h)
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def get_or_compute(self, payload: str, compute_fn: Callable) -> Any:
        cached = self.get(payload)
        if cached is not None:
            return cached
        result = compute_fn(payload)
        self.set(payload, result)
        return result

    def stats(self) -> dict:
        total = self.hits + self.misses
        hit_rate = self.hits / max(total, 1)
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
        }

    def reset(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0
```

**VALIDATE:**
```powershell
python -c "
from SeqGAN_SQLi.src.reward_cache import RewardCache
c = RewardCache(max_size=3)
print('Miss 1:', c.get('a'))
c.set('a', 1.0)
print('Hit:', c.get('a'))
print('Stats:', c.stats())
"
```

---

### STEP 2.7: Create Composite Reward (Reward V2)

**ACTION:** Tạo `SeqGAN_SQLi/src/reward_v2.py`:

```python
"""
reward_v2.py — Composite reward kết hợp WAF + custom + AST + DB execution.
"""
from typing import Optional

from .ast_tracker import ASTFingerprintTracker
from .custom_rules import CustomRuleEngine
from .db_sandbox import DBSandbox
from .parser_gate import SQLParserGate
from .reward_cache import RewardCache
from .waf_oracle import WAFOracle, waf_boundary_reward


PHASE_WEIGHTS = {
    "warmup": {"owasp": 0.0, "custom": 0.7, "diversity": 0.0, "overlap": 0.0},
    "adversarial": {"owasp": 0.4, "custom": 0.3, "diversity": 0.2, "overlap": 0.1},
    "refinement": {"owasp": 0.3, "custom": 0.1, "diversity": 0.5, "overlap": 0.1},
}


class CompositeRewardV2:
    """
    r = syntax_gate × executable_gate × (
          w_owasp · r_boundary(anomaly)
        + w_custom · r_custom
        + w_diversity · novelty
        - w_overlap · overlap_penalty
    )

    Gates trả -1 hoặc -0.5 ngay (không vào composite).
    """

    def __init__(
        self,
        phase: str = "warmup",
        waf_url: str = "http://localhost:8080",
        boundary_threshold: int = 5,
        use_waf: bool = True,
        cache_size: int = 100000,
    ):
        self.parser = SQLParserGate()
        self.db = DBSandbox()
        self.custom = CustomRuleEngine()
        self.ast = ASTFingerprintTracker()
        self.waf = WAFOracle(url=waf_url) if use_waf else None
        self.use_waf = use_waf
        self.boundary_threshold = boundary_threshold
        self.cache = RewardCache(max_size=cache_size)
        self.set_phase(phase)

    def set_phase(self, phase: str):
        if phase not in PHASE_WEIGHTS:
            raise ValueError(f"Unknown phase: {phase}")
        self.phase = phase
        self.weights = PHASE_WEIGHTS[phase]

    def __call__(self, payload: str) -> float:
        cached = self.cache.get(payload)
        if cached is not None:
            return cached

        # Gate 1: syntax
        if self.parser.evaluate(payload) == 0:
            r = -1.0
            self.cache.set(payload, r)
            return r

        # Gate 2: DB executable
        if self.db.evaluate(payload) == 0:
            r = -0.5
            self.cache.set(payload, r)
            return r

        # Quality components
        if self.weights["owasp"] > 0 and self.use_waf and self.waf:
            waf_result = self.waf.evaluate(payload)
            r_owasp = waf_boundary_reward(
                waf_result["anomaly_score"],
                self.boundary_threshold,
            )
        else:
            r_owasp = 0.0

        r_custom = self.custom.score(payload)
        r_diversity = self.ast.novelty(payload) if self.weights["diversity"] > 0 else 0.0
        overlap_penalty = max(0, r_owasp - r_custom) if r_owasp > 0 else 0.0

        r = (
            self.weights["owasp"] * r_owasp
            + self.weights["custom"] * r_custom
            + self.weights["diversity"] * r_diversity
            - self.weights["overlap"] * overlap_penalty
        )

        self.cache.set(payload, r)
        return r

    def get_stats(self) -> dict:
        stats = {
            "phase": self.phase,
            "cache": self.cache.stats(),
            "ast": self.ast.get_stats(),
        }
        return stats

    def reset_ast_cache(self):
        """For refinement phase: force re-exploration."""
        self.ast.reset()

    def close(self):
        self.db.close()
        if self.waf:
            self.waf.close()
```

**VALIDATE:**
```powershell
python -c "
from SeqGAN_SQLi.src.reward_v2 import CompositeRewardV2
# Test without WAF first (Phase 1 warmup mode)
r = CompositeRewardV2(phase='warmup', use_waf=False)
print('Attack:', r(\"1 OR 1=1\"))
print('Trivial:', r('--'))
print('Garbage:', r('asdf'))
print('Stats:', r.get_stats())
r.close()
"
```

Expected: Attack >0, Trivial <0, Garbage <0.

---

### STEP 2.8: Create Conditional Generator (Optional - SKIP nếu vocab không đổi)

**WHY:** G8 Phản biện 8 — SeqGAN unconditional là weak.

**ACTION:** Edit `SeqGAN_SQLi/src/generator.py`, **append** class mới ở cuối file (không xóa class cũ):

```python
# === V2 ADDITION ===

class ConditionalGenerator(nn.Module):
    """
    LSTM Generator với attack type conditioning.
    """

    def __init__(
        self,
        vocab_size: int = 134,
        embed_dim: int = 256,
        hidden_dim: int = 512,
        num_layers: int = 3,
        num_attack_types: int = 8,
        type_embed_dim: int = 32,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.token_embed = nn.Embedding(vocab_size, embed_dim)
        self.type_embed = nn.Embedding(num_attack_types, type_embed_dim)
        self.lstm = nn.LSTM(
            input_size=embed_dim + type_embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
        )
        self.head = nn.Linear(hidden_dim, vocab_size)

    def forward(self, input_ids, attack_type_ids, hidden=None):
        tok_emb = self.token_embed(input_ids)  # (B, T, E)
        if attack_type_ids.dim() == 1:
            attack_type_ids = attack_type_ids.unsqueeze(1)  # (B, 1)
        type_emb = self.type_embed(attack_type_ids)  # (B, 1, type_E)
        type_emb_expanded = type_emb.expand(-1, tok_emb.size(1), -1)
        x = torch.cat([tok_emb, type_emb_expanded], dim=-1)
        out, hidden = self.lstm(x, hidden)
        logits = self.head(out)
        return logits, hidden

    def sample(self, batch_size, attack_type_ids, max_len, sos_token=0, eos_token=1, device="cuda"):
        """Generate batch of sequences cho cùng attack types."""
        if attack_type_ids.dim() == 1:
            attack_type_ids = attack_type_ids.unsqueeze(1)
        sequences = torch.full((batch_size, 1), sos_token, dtype=torch.long, device=device)
        hidden = None
        for _ in range(max_len - 1):
            logits, hidden = self.forward(sequences[:, -1:], attack_type_ids, hidden)
            probs = torch.softmax(logits[:, -1, :], dim=-1)
            next_tokens = torch.multinomial(probs, num_samples=1)
            sequences = torch.cat([sequences, next_tokens], dim=1)
        return sequences
```

**Note:** Để run nhanh prototype, có thể **dùng generator V1 existing**. Conditional là enhancement ở Phase 2.5.

**SKIP DECISION:** Nếu time-constrained, set `USE_CONDITIONAL=False` ở config và dùng existing `Generator` class.

---

### STEP 2.9: Create V2 Config

**ACTION:** Tạo `SeqGAN_SQLi/configs/seqgan_v2.yaml`:

```yaml
# SeqGAN V2 configuration
# Composite reward with OWASP CRS + Custom rules + AST diversity + DB execution

# Model
vocab_size: 134
embed_dim: 256
hidden_dim: 512
num_layers: 3
dropout: 0.2

# Conditional (Phase 2.5 — set false để skip)
use_conditional: false
num_attack_types: 8
type_embed_dim: 32

# Discriminator
d_embed_dim: 128
d_kernel_sizes: [3, 4, 5]
d_filters: 128

# Training
batch_size: 64
max_seq_len: 80
mc_rollout_k: 16
d_per_g_ratio: 1  # giảm từ 5 vì D không phải nguồn reward chính

# Phase steps
mle_epochs: 10
warmup_steps: 2000
adversarial_steps: 13000
refinement_steps: 5000

# Learning rates
lr_mle: 0.001
lr_g_warmup: 0.0001
lr_g_adversarial: 0.00005
lr_g_refinement: 0.00001
lr_d: 0.0001

# Optimizer
optimizer: adam
beta1: 0.5
beta2: 0.999
grad_clip: 1.0

# Reward
boundary_threshold: 5
use_waf: true
waf_url: "http://localhost:8080"
cache_size: 100000

# Phase weights (đã hardcode trong reward_v2.py PHASE_WEIGHTS)

# Paths
data_dir: "SeqGAN_SQLi/data/v2"
ckpt_dir: "SeqGAN_SQLi/checkpoints/v2"
log_dir: "SeqGAN_SQLi/logs/v2"

# Seed
seed: 42

# Eval
n_eval_samples: 1000
relex_dict_path: "SeqGAN_SQLi/data/relex_dictionary.json"
```

**VALIDATE:**
```powershell
python -c "import yaml; c=yaml.safe_load(open('SeqGAN_SQLi/configs/seqgan_v2.yaml')); print(list(c.keys())[:10])"
```

---

### STEP 2.10: Smoke Test Composite Reward End-to-End

**ACTION:** Tạo `SeqGAN_SQLi/scripts/smoke_reward_v2.py`:

```python
"""Smoke test cho CompositeRewardV2."""
import sys
import time
sys.path.insert(0, ".")

from SeqGAN_SQLi.src.reward_v2 import CompositeRewardV2

TEST_PAYLOADS = [
    ("1", "trivial benign"),
    ("admin", "benign string"),
    ("1 OR 1=1", "classic SQLi"),
    ("1' OR '1'='1", "quoted SQLi"),
    ("1 UNION SELECT password FROM users", "union attack"),
    ("--", "trivial"),
    ("asdf garbage", "non-SQL noise"),
    ("1 AND SLEEP(5)", "time-based"),
]


def test_phase(phase: str, use_waf: bool):
    print(f"\n=== Phase: {phase} (WAF: {use_waf}) ===")
    r = CompositeRewardV2(phase=phase, use_waf=use_waf)
    print(f"Weights: {r.weights}")
    for payload, desc in TEST_PAYLOADS:
        start = time.time()
        reward = r(payload)
        elapsed = (time.time() - start) * 1000
        print(f"  [{reward:+.3f}] ({elapsed:5.1f}ms) {desc}: {payload[:40]}")
    print(f"Stats: {r.get_stats()}")
    r.close()


if __name__ == "__main__":
    # Test warmup (no WAF)
    test_phase("warmup", use_waf=False)
    # Test adversarial with WAF
    test_phase("adversarial", use_waf=True)
    # Test refinement (diversity-weighted)
    test_phase("refinement", use_waf=True)
```

**Run:**
```powershell
python SeqGAN_SQLi/scripts/smoke_reward_v2.py
```

**VALIDATE:**
- Warmup: garbage payloads → negative, real attacks → positive
- Adversarial: WAF calls < 50ms/payload
- Cache hits ≥ 0 after second pass (do reward cache)

**ON_FAIL:** Nếu WAF timeout liên tục — check Docker container `docker ps`, restart container.

---

**CHECKPOINT PHASE 2:** Commit
```powershell
git add SeqGAN_SQLi/src/waf_oracle.py SeqGAN_SQLi/src/custom_rules.py SeqGAN_SQLi/src/parser_gate.py SeqGAN_SQLi/src/db_sandbox.py SeqGAN_SQLi/src/ast_tracker.py SeqGAN_SQLi/src/reward_cache.py SeqGAN_SQLi/src/reward_v2.py SeqGAN_SQLi/src/generator.py SeqGAN_SQLi/configs/seqgan_v2.yaml SeqGAN_SQLi/scripts/smoke_reward_v2.py
git commit -m "Phase 2 complete: WAF oracle, custom rules, AST tracker, DB sandbox, composite reward V2"
```

---

## PHASE 3: TRAINING

### STEP 3.1: MLE Pretrain V2

**WHY:** Train Generator trên gold+silver data với upweight gold 3×.

**ACTION:** Tạo `SeqGAN_SQLi/pretrain_mle_v2.py`:

```python
"""
pretrain_mle_v2.py — MLE pretrain với tiered data weighting.
Reuse architecture từ pretrain_mle.py V1 nhưng:
  - Đọc từ data/v2/
  - Upweight gold tier 3×
  - Save vào checkpoints/v2/
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import torch
import torch.nn as nn
import yaml
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler

sys.path.insert(0, str(Path(__file__).parent))

from src.generator import Generator
from src.tokenizer import SQLTokenizer
from src.utils import set_seed


class TieredSQLiDataset(Dataset):
    def __init__(self, csv_path, tokenizer, max_len=80, payload_col="payload_norm"):
        df = pd.read_csv(csv_path)
        if payload_col not in df.columns:
            for c in ["payload", "payload_delex"]:
                if c in df.columns:
                    payload_col = c
                    break
        if "tier" not in df.columns:
            df["tier"] = "silver"
        df = df[df["tier"].isin(["gold", "silver"])].copy()
        self.payloads = df[payload_col].astype(str).tolist()
        self.tiers = df["tier"].tolist()
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.payloads)

    def __getitem__(self, idx):
        tokens = self.tokenizer.encode(self.payloads[idx], max_len=self.max_len)
        weight = 3.0 if self.tiers[idx] == "gold" else 1.0
        return torch.tensor(tokens), weight


def train(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    set_seed(cfg["seed"])
    device = "cuda" if torch.cuda.is_available() else "cpu"

    data_dir = Path(cfg["data_dir"])
    ckpt_dir = Path(cfg["ckpt_dir"])
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = SQLTokenizer.from_vocab(data_dir / "tokenizer_vocab.json")

    train_ds = TieredSQLiDataset(data_dir / "train.csv", tokenizer, cfg["max_seq_len"])
    val_ds = TieredSQLiDataset(data_dir / "val.csv", tokenizer, cfg["max_seq_len"])

    # Weighted sampling: gold sees 3x more
    weights = [w for _, w in train_ds]
    sampler = WeightedRandomSampler(weights, len(weights), replacement=True)

    def collate(batch):
        tokens = torch.stack([b[0] for b in batch])
        return tokens

    train_loader = DataLoader(train_ds, batch_size=cfg["batch_size"], sampler=sampler, collate_fn=collate)
    val_loader = DataLoader(val_ds, batch_size=cfg["batch_size"], shuffle=False, collate_fn=collate)

    model = Generator(
        vocab_size=cfg["vocab_size"],
        embed_dim=cfg["embed_dim"],
        hidden_dim=cfg["hidden_dim"],
        num_layers=cfg["num_layers"],
        dropout=cfg["dropout"],
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=cfg["lr_mle"])
    criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_id)

    best_val_ppl = float("inf")
    patience = 0
    max_patience = 3

    for epoch in range(cfg["mle_epochs"]):
        model.train()
        train_loss = 0
        for batch in train_loader:
            batch = batch.to(device)
            input_ids = batch[:, :-1]
            target_ids = batch[:, 1:]
            logits, _ = model(input_ids)
            loss = criterion(logits.reshape(-1, logits.size(-1)), target_ids.reshape(-1))
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg["grad_clip"])
            optimizer.step()
            train_loss += loss.item()
        train_loss /= len(train_loader)

        model.eval()
        val_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                batch = batch.to(device)
                input_ids = batch[:, :-1]
                target_ids = batch[:, 1:]
                logits, _ = model(input_ids)
                loss = criterion(logits.reshape(-1, logits.size(-1)), target_ids.reshape(-1))
                val_loss += loss.item()
        val_loss /= len(val_loader)
        val_ppl = torch.exp(torch.tensor(val_loss)).item()
        print(f"Epoch {epoch+1}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, val_ppl={val_ppl:.4f}")

        if val_ppl < best_val_ppl:
            best_val_ppl = val_ppl
            patience = 0
            torch.save({
                "model_state_dict": model.state_dict(),
                "val_ppl": val_ppl,
                "epoch": epoch + 1,
                "config": cfg,
            }, ckpt_dir / "mle_best.pt")
            print(f"  Saved best (val_ppl={val_ppl:.4f})")
        else:
            patience += 1
            if patience >= max_patience:
                print(f"Early stop (patience={patience})")
                break

    torch.save({
        "model_state_dict": model.state_dict(),
        "val_ppl": val_ppl,
        "epoch": epoch + 1,
        "config": cfg,
    }, ckpt_dir / "mle_final.pt")
    print(f"\nFinal best val_ppl: {best_val_ppl:.4f}")
    print(f"Saved: {ckpt_dir / 'mle_best.pt'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="SeqGAN_SQLi/configs/seqgan_v2.yaml")
    args = parser.parse_args()
    train(args.config)
```

**Run:**
```powershell
python SeqGAN_SQLi/pretrain_mle_v2.py --config SeqGAN_SQLi/configs/seqgan_v2.yaml
```

**VALIDATE:** Final val_ppl < 2.0; checkpoint `checkpoints/v2/mle_best.pt` tồn tại.

**ON_FAIL:**
- OOM: giảm batch_size về 32
- Loss không giảm: check tokenizer/data integrity
- Slow: confirm CUDA active

**Expected time:** 10-15 phút.

---

### STEP 3.2: Adversarial Training V2 (Tất cả 3 phases)

**ACTION:** Tạo `SeqGAN_SQLi/train_adversarial_v2.py`:

```python
"""
train_adversarial_v2.py — Full adversarial training với 3-phase curriculum.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
import yaml

sys.path.insert(0, str(Path(__file__).parent))

from src.discriminator import Discriminator
from src.generator import Generator
from src.reward_v2 import CompositeRewardV2
from src.rollout import MonteCarloRollout
from src.tokenizer import SQLTokenizer
from src.utils import set_seed


def train(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    set_seed(cfg["seed"])
    device = "cuda" if torch.cuda.is_available() else "cpu"

    data_dir = Path(cfg["data_dir"])
    ckpt_dir = Path(cfg["ckpt_dir"])
    log_dir = Path(cfg["log_dir"])
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = SQLTokenizer.from_vocab(data_dir / "tokenizer_vocab.json")

    # Init Generator from MLE pretrain
    G = Generator(
        vocab_size=cfg["vocab_size"],
        embed_dim=cfg["embed_dim"],
        hidden_dim=cfg["hidden_dim"],
        num_layers=cfg["num_layers"],
        dropout=cfg["dropout"],
    ).to(device)
    mle_ckpt = torch.load(ckpt_dir / "mle_best.pt", map_location=device)
    G.load_state_dict(mle_ckpt["model_state_dict"])
    print(f"Loaded MLE checkpoint (val_ppl={mle_ckpt['val_ppl']:.4f})")

    D = Discriminator(
        vocab_size=cfg["vocab_size"],
        embed_dim=cfg["d_embed_dim"],
        kernel_sizes=cfg["d_kernel_sizes"],
        num_filters=cfg["d_filters"],
    ).to(device)

    # Reward V2 (composite)
    reward_fn = CompositeRewardV2(
        phase="warmup",
        waf_url=cfg["waf_url"],
        boundary_threshold=cfg["boundary_threshold"],
        use_waf=False,  # warmup không dùng WAF
        cache_size=cfg["cache_size"],
    )

    rollout = MonteCarloRollout(G, K=cfg["mc_rollout_k"])

    log_path = log_dir / "training_log.jsonl"
    log_f = open(log_path, "w", encoding="utf-8")

    def log(step, phase, **kwargs):
        entry = {"step": step, "phase": phase, **kwargs}
        log_f.write(json.dumps(entry) + "\n")
        log_f.flush()

    total_warmup = cfg["warmup_steps"]
    total_adv = cfg["adversarial_steps"]
    total_ref = cfg["refinement_steps"]
    grand_total = total_warmup + total_adv + total_ref

    optimizer_G = torch.optim.Adam(G.parameters(), lr=cfg["lr_g_warmup"], betas=(cfg["beta1"], cfg["beta2"]))
    optimizer_D = torch.optim.Adam(D.parameters(), lr=cfg["lr_d"], betas=(cfg["beta1"], cfg["beta2"]))

    start_time = time.time()
    step = 0

    print(f"\n=== Phase 1: WARMUP (steps 0-{total_warmup}) ===")
    reward_fn.set_phase("warmup")

    for warmup_step in range(total_warmup):
        step += 1
        # G generate
        with torch.no_grad():
            fake_seqs = G.sample(
                batch_size=cfg["batch_size"],
                max_len=cfg["max_seq_len"],
                sos_token=tokenizer.sos_id,
                device=device,
            )

        # Compute reward
        rewards = []
        for seq in fake_seqs:
            payload = tokenizer.decode(seq.tolist())
            r = reward_fn(payload)
            rewards.append(r)
        rewards_tensor = torch.tensor(rewards, dtype=torch.float, device=device)

        # G update (REINFORCE)
        logits, _ = G(fake_seqs[:, :-1])
        log_probs = F.log_softmax(logits, dim=-1)
        # gather log_probs cho actions chosen
        actions = fake_seqs[:, 1:]
        gathered_log_probs = log_probs.gather(2, actions.unsqueeze(-1)).squeeze(-1)  # (B, T)
        # baseline = mean
        advantages = rewards_tensor - rewards_tensor.mean()
        g_loss = -(gathered_log_probs.sum(dim=1) * advantages).mean()

        optimizer_G.zero_grad()
        g_loss.backward()
        torch.nn.utils.clip_grad_norm_(G.parameters(), cfg["grad_clip"])
        optimizer_G.step()

        if step % 100 == 0:
            elapsed = time.time() - start_time
            print(f"  Step {step}: g_loss={g_loss.item():.4f}, mean_reward={rewards_tensor.mean().item():.4f}, elapsed={elapsed/60:.1f}min")
            log(step, "warmup", g_loss=g_loss.item(), mean_reward=rewards_tensor.mean().item())

    torch.save({"model_state_dict": G.state_dict(), "step": step, "phase": "warmup"}, ckpt_dir / "adv_warmup.pt")
    print(f"Saved: {ckpt_dir / 'adv_warmup.pt'}")

    # === Phase 2: Adversarial ===
    print(f"\n=== Phase 2: ADVERSARIAL (steps {step}-{step+total_adv}) ===")
    reward_fn.set_phase("adversarial")
    reward_fn.use_waf = True  # enable WAF từ phase này
    if reward_fn.waf is None:
        from src.waf_oracle import WAFOracle
        reward_fn.waf = WAFOracle(url=cfg["waf_url"])

    optimizer_G = torch.optim.Adam(G.parameters(), lr=cfg["lr_g_adversarial"], betas=(cfg["beta1"], cfg["beta2"]))

    for adv_step in range(total_adv):
        step += 1
        with torch.no_grad():
            fake_seqs = G.sample(
                batch_size=cfg["batch_size"],
                max_len=cfg["max_seq_len"],
                sos_token=tokenizer.sos_id,
                device=device,
            )

        rewards = []
        for seq in fake_seqs:
            payload = tokenizer.decode(seq.tolist())
            r = reward_fn(payload)
            rewards.append(r)
        rewards_tensor = torch.tensor(rewards, dtype=torch.float, device=device)

        logits, _ = G(fake_seqs[:, :-1])
        log_probs = F.log_softmax(logits, dim=-1)
        actions = fake_seqs[:, 1:]
        gathered_log_probs = log_probs.gather(2, actions.unsqueeze(-1)).squeeze(-1)
        advantages = rewards_tensor - rewards_tensor.mean()
        g_loss = -(gathered_log_probs.sum(dim=1) * advantages).mean()

        optimizer_G.zero_grad()
        g_loss.backward()
        torch.nn.utils.clip_grad_norm_(G.parameters(), cfg["grad_clip"])
        optimizer_G.step()

        if step % 200 == 0:
            elapsed = time.time() - start_time
            cache_stats = reward_fn.get_stats()
            print(f"  Step {step}: g_loss={g_loss.item():.4f}, mean_reward={rewards_tensor.mean().item():.4f}, hit_rate={cache_stats['cache']['hit_rate']:.2f}, elapsed={elapsed/60:.1f}min")
            log(step, "adversarial", g_loss=g_loss.item(), mean_reward=rewards_tensor.mean().item(), cache_hit_rate=cache_stats["cache"]["hit_rate"])

        if step % 1000 == 0:
            torch.save({"model_state_dict": G.state_dict(), "step": step, "phase": "adversarial"}, ckpt_dir / f"adv_step{step}.pt")

    torch.save({"model_state_dict": G.state_dict(), "step": step, "phase": "adversarial"}, ckpt_dir / "adv_main.pt")
    print(f"Saved: {ckpt_dir / 'adv_main.pt'}")

    # === Phase 3: Refinement ===
    print(f"\n=== Phase 3: REFINEMENT (steps {step}-{step+total_ref}) ===")
    reward_fn.set_phase("refinement")
    optimizer_G = torch.optim.Adam(G.parameters(), lr=cfg["lr_g_refinement"], betas=(cfg["beta1"], cfg["beta2"]))

    for ref_step in range(total_ref):
        step += 1
        if step % 1000 == 0:
            reward_fn.reset_ast_cache()
            print(f"  AST cache reset at step {step}")

        with torch.no_grad():
            fake_seqs = G.sample(
                batch_size=cfg["batch_size"],
                max_len=cfg["max_seq_len"],
                sos_token=tokenizer.sos_id,
                device=device,
            )

        rewards = []
        for seq in fake_seqs:
            payload = tokenizer.decode(seq.tolist())
            r = reward_fn(payload)
            rewards.append(r)
        rewards_tensor = torch.tensor(rewards, dtype=torch.float, device=device)

        logits, _ = G(fake_seqs[:, :-1])
        log_probs = F.log_softmax(logits, dim=-1)
        actions = fake_seqs[:, 1:]
        gathered_log_probs = log_probs.gather(2, actions.unsqueeze(-1)).squeeze(-1)
        advantages = rewards_tensor - rewards_tensor.mean()
        g_loss = -(gathered_log_probs.sum(dim=1) * advantages).mean()

        optimizer_G.zero_grad()
        g_loss.backward()
        torch.nn.utils.clip_grad_norm_(G.parameters(), cfg["grad_clip"])
        optimizer_G.step()

        if step % 200 == 0:
            elapsed = time.time() - start_time
            print(f"  Step {step}: g_loss={g_loss.item():.4f}, mean_reward={rewards_tensor.mean().item():.4f}, elapsed={elapsed/60:.1f}min")
            log(step, "refinement", g_loss=g_loss.item(), mean_reward=rewards_tensor.mean().item())

    torch.save({"model_state_dict": G.state_dict(), "step": step, "phase": "refinement"}, ckpt_dir / "adv_refined.pt")
    print(f"Saved: {ckpt_dir / 'adv_refined.pt'}")

    log_f.close()
    reward_fn.close()

    print(f"\n=== Training Complete ===")
    print(f"Total time: {(time.time() - start_time) / 3600:.2f} hours")
    print(f"Total steps: {step}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="SeqGAN_SQLi/configs/seqgan_v2.yaml")
    args = parser.parse_args()
    train(args.config)
```

**Note quan trọng:** Script này simplify hơn V1 — không có Monte Carlo rollout per-token (vì compute quá lớn với WAF). Thay vào dùng **sequence-level reward** với simple baseline (mean). Đây là tradeoff để khả thi compute.

**Pre-run check (5 phút smoke):**
```powershell
# Sửa config tạm: warmup_steps=50, adversarial_steps=50, refinement_steps=50
# Run smoke
python SeqGAN_SQLi/train_adversarial_v2.py --config SeqGAN_SQLi/configs/seqgan_v2.yaml
```

Nếu smoke OK, revert config về full steps.

**Full run:**
```powershell
python SeqGAN_SQLi/train_adversarial_v2.py --config SeqGAN_SQLi/configs/seqgan_v2.yaml 2>&1 | Tee-Object -FilePath SeqGAN_SQLi/logs/v2/training_console.log
```

**Expected time:** 15-20 giờ.

**VALIDATE:** 
- `checkpoints/v2/adv_warmup.pt`, `adv_main.pt`, `adv_refined.pt` tồn tại.
- `logs/v2/training_log.jsonl` có entries cho cả 3 phases.
- Mean reward tăng dần (negative ở warmup → positive ở adversarial).

**ON_FAIL:**
- OOM: giảm batch_size, K
- WAF timeout: confirm Docker still running, restart nếu cần
- Loss NaN: giảm LR_G xuống 1e-5

---

**CHECKPOINT PHASE 3:** Commit
```powershell
git add SeqGAN_SQLi/pretrain_mle_v2.py SeqGAN_SQLi/train_adversarial_v2.py
git add SeqGAN_SQLi/checkpoints/v2 SeqGAN_SQLi/logs/v2
git commit -m "Phase 3 complete: V2 training (MLE + 3-phase adversarial with composite reward)"
```

---

## PHASE 4: EVALUATION

### STEP 4.1: Generate V2 Samples

**ACTION:** Tạo `SeqGAN_SQLi/generate_v2.py`:

```python
"""generate_v2.py — Generate samples từ V2 checkpoint."""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import torch
import yaml

sys.path.insert(0, str(Path(__file__).parent))

from src.generator import Generator
from src.tokenizer import SQLTokenizer


def generate(config_path, ckpt_path, n_samples, out_csv):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = SQLTokenizer.from_vocab(Path(cfg["data_dir"]) / "tokenizer_vocab.json")

    G = Generator(
        vocab_size=cfg["vocab_size"],
        embed_dim=cfg["embed_dim"],
        hidden_dim=cfg["hidden_dim"],
        num_layers=cfg["num_layers"],
        dropout=cfg["dropout"],
    ).to(device)
    ckpt = torch.load(ckpt_path, map_location=device)
    G.load_state_dict(ckpt["model_state_dict"])
    G.eval()

    samples = []
    batch_size = 64
    n_batches = (n_samples + batch_size - 1) // batch_size

    with torch.no_grad():
        for b in range(n_batches):
            current_batch = min(batch_size, n_samples - b * batch_size)
            fake_seqs = G.sample(
                batch_size=current_batch,
                max_len=cfg["max_seq_len"],
                sos_token=tokenizer.sos_id,
                device=device,
            )
            for seq in fake_seqs:
                payload = tokenizer.decode(seq.tolist())
                samples.append(payload)

    df = pd.DataFrame({"payload": samples[:n_samples]})
    df.to_csv(out_csv, index=False)
    print(f"Generated {len(df)} samples → {out_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="SeqGAN_SQLi/configs/seqgan_v2.yaml")
    parser.add_argument("--ckpt", required=True)
    parser.add_argument("--n_samples", type=int, default=1000)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    generate(args.config, args.ckpt, args.n_samples, args.out)
```

**Run cho cả 3 checkpoints:**
```powershell
python SeqGAN_SQLi/generate_v2.py --ckpt SeqGAN_SQLi/checkpoints/v2/adv_warmup.pt --out SeqGAN_SQLi/eval_v2_warmup.csv
python SeqGAN_SQLi/generate_v2.py --ckpt SeqGAN_SQLi/checkpoints/v2/adv_main.pt --out SeqGAN_SQLi/eval_v2_main.csv
python SeqGAN_SQLi/generate_v2.py --ckpt SeqGAN_SQLi/checkpoints/v2/adv_refined.pt --out SeqGAN_SQLi/eval_v2_refined.csv
python SeqGAN_SQLi/generate_v2.py --ckpt SeqGAN_SQLi/checkpoints/v2/mle_best.pt --out SeqGAN_SQLi/eval_v2_mle.csv
```

**VALIDATE:** 4 file CSV với 1000 payloads mỗi cái.

---

### STEP 4.2: Train ML-IDS Classifier (cho metric)

**ACTION:** Tạo `SeqGAN_SQLi/eval/train_xgboost_ids.py`:

```python
"""
train_xgboost_ids.py — Train XGBoost IDS classifier dùng cho ML-IDS evasion metric.
"""
import argparse
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
import xgboost as xgb

sys.path.insert(0, str(Path(__file__).parent.parent))


def train_ids(train_csv, val_csv, out_dir):
    out_p = Path(out_dir)
    out_p.mkdir(parents=True, exist_ok=True)

    df_train = pd.read_csv(train_csv)
    df_val = pd.read_csv(val_csv)

    payload_col = next((c for c in ["payload_norm", "payload"] if c in df_train.columns), None)

    # Label: attack (1) vs benign (0)
    if "sqli_type" in df_train.columns:
        df_train["is_attack"] = (df_train["sqli_type"] != "benign").astype(int)
        df_val["is_attack"] = (df_val["sqli_type"] != "benign").astype(int)
    else:
        # Assume all attack
        df_train["is_attack"] = 1
        df_val["is_attack"] = 1

    if df_train["is_attack"].sum() == len(df_train):
        print("WARNING: No benign in train. Adding synthetic benign...")
        benign = pd.DataFrame({
            payload_col: ["1", "admin", "test", "hello", "user@test.com"] * 200,
            "is_attack": [0] * 1000,
        })
        df_train = pd.concat([df_train, benign], ignore_index=True)

    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=5000)
    X_train = vec.fit_transform(df_train[payload_col].astype(str))
    X_val = vec.transform(df_val[payload_col].astype(str))

    y_train = df_train["is_attack"].values
    y_val = df_val["is_attack"].values

    clf = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss",
    )
    clf.fit(X_train, y_train)

    y_val_pred = clf.predict(X_val)
    y_val_proba = clf.predict_proba(X_val)[:, 1]
    print(classification_report(y_val, y_val_pred))
    try:
        auc = roc_auc_score(y_val, y_val_proba)
        print(f"AUC: {auc:.4f}")
    except Exception:
        pass

    joblib.dump(clf, out_p / "ids_xgb.pkl")
    joblib.dump(vec, out_p / "ids_vectorizer.pkl")
    print(f"Saved: {out_p / 'ids_xgb.pkl'}, {out_p / 'ids_vectorizer.pkl'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_csv", default="SeqGAN_SQLi/data/v2/train.csv")
    parser.add_argument("--val_csv", default="SeqGAN_SQLi/data/v2/val.csv")
    parser.add_argument("--out_dir", default="SeqGAN_SQLi/eval/ids_classifier")
    args = parser.parse_args()
    train_ids(args.train_csv, args.val_csv, args.out_dir)
```

**Run:**
```powershell
python SeqGAN_SQLi/eval/train_xgboost_ids.py
```

**VALIDATE:** `eval/ids_classifier/ids_xgb.pkl` và `ids_vectorizer.pkl` tồn tại; AUC > 0.85.

---

### STEP 4.3: Evaluate V2 — 5 Metrics

**ACTION:** Tạo `SeqGAN_SQLi/eval/evaluate_v2.py`:

```python
"""
evaluate_v2.py — Compute 5 metrics cho generated payloads.
"""
import argparse
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ast_tracker import ASTFingerprintTracker
from src.custom_rules import CustomRuleEngine
from src.db_sandbox import DBSandbox
from src.parser_gate import SQLParserGate
from src.waf_oracle import WAFOracle


def bootstrap_ci(values, n_resamples=10000, ci=0.95):
    values = np.array(values)
    means = np.array([
        np.mean(np.random.choice(values, size=len(values), replace=True))
        for _ in range(n_resamples)
    ])
    lo = np.percentile(means, (1 - ci) / 2 * 100)
    hi = np.percentile(means, (1 + ci) / 2 * 100)
    return float(np.mean(values)), float(lo), float(hi)


def re_lex(payload, relex_dict, seed=None):
    if seed is not None:
        random.seed(seed)
    result = payload
    for placeholder, options in relex_dict.items():
        while placeholder in result:
            result = result.replace(placeholder, random.choice(options), 1)
    return result


def compute_owasp_bypass(payloads, waf):
    blocked = []
    for p in payloads:
        try:
            r = waf.evaluate(p)
            blocked.append(1 if not r["blocked"] else 0)
        except Exception:
            blocked.append(0)
    return blocked


def compute_db_execution(payloads, db):
    return [db.evaluate(p) for p in payloads]


def compute_ast_diversity(payloads, tracker):
    fingerprints = []
    for p in payloads:
        fp = tracker.fingerprint(p)
        fingerprints.extend(fp)
    counts = Counter(fingerprints)
    if not counts:
        return 0.0
    total = sum(counts.values())
    entropy = -sum((c / total) * math.log(c / total) for c in counts.values())
    return entropy


def compute_ml_ids_evasion(payloads, classifier, vectorizer):
    X = vectorizer.transform(payloads)
    proba = classifier.predict_proba(X)[:, 1]  # P(attack)
    # Evasion = predicted as benign by IDS
    return (proba < 0.5).astype(int).tolist()


def compute_relex_uniqueness(payloads, relex_dict, n_samples_per=3):
    relexed = []
    for p in payloads:
        for s in range(n_samples_per):
            relexed.append(re_lex(p, relex_dict, seed=s))
    return len(set(relexed)) / max(len(relexed), 1)


def evaluate(samples_csv, out_json, config_path, ids_dir):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    with open(cfg["relex_dict_path"]) as f:
        relex_dict = json.load(f)

    df = pd.read_csv(samples_csv)
    payload_col = "payload" if "payload" in df.columns else df.columns[0]
    payloads = df[payload_col].astype(str).tolist()
    print(f"Evaluating {len(payloads)} payloads from {samples_csv}")

    # Init evaluators
    waf = WAFOracle(url=cfg["waf_url"])
    db = DBSandbox()
    parser = SQLParserGate()
    custom = CustomRuleEngine()
    tracker = ASTFingerprintTracker()

    ids_clf = joblib.load(Path(ids_dir) / "ids_xgb.pkl")
    ids_vec = joblib.load(Path(ids_dir) / "ids_vectorizer.pkl")

    # Metric 1: OWASP bypass rate
    print("Computing OWASP bypass...")
    owasp_bypass = compute_owasp_bypass(payloads, waf)
    m1, m1_lo, m1_hi = bootstrap_ci(owasp_bypass)
    print(f"  OWASP bypass: {m1:.4f} [{m1_lo:.4f}, {m1_hi:.4f}]")

    # Metric 2: DB execution rate
    print("Computing DB execution...")
    db_exec = compute_db_execution(payloads, db)
    m2, m2_lo, m2_hi = bootstrap_ci(db_exec)
    print(f"  DB execution: {m2:.4f} [{m2_lo:.4f}, {m2_hi:.4f}]")

    # Metric 3: AST diversity (entropy)
    print("Computing AST diversity...")
    ast_div = compute_ast_diversity(payloads, tracker)
    print(f"  AST diversity (entropy): {ast_div:.4f}")

    # Metric 4: ML-IDS evasion
    print("Computing ML-IDS evasion...")
    ids_evasion = compute_ml_ids_evasion(payloads, ids_clf, ids_vec)
    m4, m4_lo, m4_hi = bootstrap_ci(ids_evasion)
    print(f"  ML-IDS evasion: {m4:.4f} [{m4_lo:.4f}, {m4_hi:.4f}]")

    # Metric 5: Re-lex uniqueness
    print("Computing Re-lex uniqueness...")
    relex_uniq = compute_relex_uniqueness(payloads, relex_dict)
    print(f"  Re-lex uniqueness: {relex_uniq:.4f}")

    # Composite score
    composite = (
        0.30 * m1
        + 0.25 * m2
        + 0.20 * min(ast_div / 5.0, 1.0)
        + 0.15 * m4
        + 0.10 * relex_uniq
    )

    # Quality stats
    syntax_pass = [parser.evaluate(p) for p in payloads]
    custom_pass = [custom.score(p) for p in payloads]

    report = {
        "samples_file": str(samples_csv),
        "n_samples": len(payloads),
        "metrics": {
            "owasp_bypass_rate": {"mean": m1, "ci_lo": m1_lo, "ci_hi": m1_hi, "weight": 0.30},
            "db_execution_rate": {"mean": m2, "ci_lo": m2_lo, "ci_hi": m2_hi, "weight": 0.25},
            "ast_diversity_entropy": {"value": ast_div, "normalized": min(ast_div / 5.0, 1.0), "weight": 0.20},
            "ml_ids_evasion_rate": {"mean": m4, "ci_lo": m4_lo, "ci_hi": m4_hi, "weight": 0.15},
            "relex_uniqueness": {"value": relex_uniq, "weight": 0.10},
        },
        "composite_score": composite,
        "quality": {
            "syntax_pass_rate": np.mean(syntax_pass),
            "custom_rule_pass_mean": np.mean(custom_pass),
        },
        "ast_stats": tracker.get_stats(),
    }

    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n=== Composite Score: {composite:.4f} ===")
    print(f"Saved: {out_json}")

    waf.close()
    db.close()
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples_csv", required=True)
    parser.add_argument("--out_json", required=True)
    parser.add_argument("--config", default="SeqGAN_SQLi/configs/seqgan_v2.yaml")
    parser.add_argument("--ids_dir", default="SeqGAN_SQLi/eval/ids_classifier")
    args = parser.parse_args()
    evaluate(args.samples_csv, args.out_json, args.config, args.ids_dir)
```

**Run cho tất cả checkpoints + V1 + template:**
```powershell
python SeqGAN_SQLi/eval/evaluate_v2.py --samples_csv SeqGAN_SQLi/eval_v2_refined.csv --out_json SeqGAN_SQLi/eval/results/v2_refined.json
python SeqGAN_SQLi/eval/evaluate_v2.py --samples_csv SeqGAN_SQLi/eval_v2_main.csv --out_json SeqGAN_SQLi/eval/results/v2_main.json
python SeqGAN_SQLi/eval/evaluate_v2.py --samples_csv SeqGAN_SQLi/eval_v2_warmup.csv --out_json SeqGAN_SQLi/eval/results/v2_warmup.json
python SeqGAN_SQLi/eval/evaluate_v2.py --samples_csv SeqGAN_SQLi/eval_v2_mle.csv --out_json SeqGAN_SQLi/eval/results/v2_mle.json
python SeqGAN_SQLi/eval/evaluate_v2.py --samples_csv SeqGAN_SQLi/eval_seqgan.csv --out_json SeqGAN_SQLi/eval/results/v1_seqgan.json
python SeqGAN_SQLi/eval/evaluate_v2.py --samples_csv SeqGAN_SQLi/eval_template.csv --out_json SeqGAN_SQLi/eval/results/template.json
```

**VALIDATE:** 6 JSON files trong `eval/results/` với cấu trúc giống nhau.

---

### STEP 4.4: Compare & Generate Report

**ACTION:** Tạo `SeqGAN_SQLi/eval/compare_results.py`:

```python
"""compare_results.py — Tổng hợp results thành bảng so sánh."""
import argparse
import json
from pathlib import Path

import pandas as pd


def compare(results_dir, out_csv, out_md):
    results_p = Path(results_dir)
    rows = []
    for json_file in sorted(results_p.glob("*.json")):
        with open(json_file) as f:
            r = json.load(f)
        rows.append({
            "model": json_file.stem,
            "n_samples": r["n_samples"],
            "owasp_bypass": r["metrics"]["owasp_bypass_rate"]["mean"],
            "owasp_ci": f"[{r['metrics']['owasp_bypass_rate']['ci_lo']:.3f}, {r['metrics']['owasp_bypass_rate']['ci_hi']:.3f}]",
            "db_execution": r["metrics"]["db_execution_rate"]["mean"],
            "ast_entropy": r["metrics"]["ast_diversity_entropy"]["value"],
            "ml_ids_evasion": r["metrics"]["ml_ids_evasion_rate"]["mean"],
            "relex_uniqueness": r["metrics"]["relex_uniqueness"]["value"],
            "composite": r["composite_score"],
            "syntax_pass": r["quality"]["syntax_pass_rate"],
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("composite", ascending=False)
    df.to_csv(out_csv, index=False)

    md = ["# V2 Evaluation Comparison\n", df.to_markdown(index=False)]
    Path(out_md).write_text("\n".join(md), encoding="utf-8")

    print(df.to_string(index=False))
    print(f"\nSaved: {out_csv}")
    print(f"Saved: {out_md}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_dir", default="SeqGAN_SQLi/eval/results")
    parser.add_argument("--out_csv", default="SeqGAN_SQLi/eval/comparison.csv")
    parser.add_argument("--out_md", default="SeqGAN_SQLi/eval/comparison.md")
    args = parser.parse_args()
    compare(args.results_dir, args.out_csv, args.out_md)
```

**Run:**
```powershell
python SeqGAN_SQLi/eval/compare_results.py
```

**VALIDATE:** Bảng so sánh tại `eval/comparison.csv` và `eval/comparison.md`.

---

**CHECKPOINT PHASE 4:** Commit
```powershell
git add SeqGAN_SQLi/eval SeqGAN_SQLi/eval_v2_*.csv SeqGAN_SQLi/generate_v2.py
git commit -m "Phase 4 complete: 5-metric evaluation, comparison report"
```

---

## PHASE 5: POST-MORTEM & DECISION

### STEP 5.1: Write V2 Summary Report

**ACTION:** Tạo `SeqGAN_SQLi/timeline/V2_RESULTS.md`:

```markdown
# V2 Results — Composite Reward + Boundary-Aware Generation

> Date: <auto-fill>
> Config: configs/seqgan_v2.yaml
> Total training time: <từ logs>

## Key Findings

<Auto-populate từ comparison.md>

## Decision

- IF composite_score(v2_refined) > composite_score(v1_seqgan) + 0.1:
    DECISION = "V2 is better, commit to V2 architecture"
- ELIF composite_score(v2_refined) > composite_score(v1_seqgan):
    DECISION = "V2 marginal improvement, do ablations to identify which component helped"
- ELSE:
    DECISION = "V2 did not improve, see V2_POSTMORTEM.md for analysis"

## Comparison Table

<Embed comparison.md content>

## Next Steps

Based on decision:
- If V2 better → Proceed to Phase 6 ablations
- If V2 worse → Postmortem, identify failed component
```

**Generate auto:**
```powershell
python -c "
import json
from pathlib import Path

results = {}
for f in sorted(Path('SeqGAN_SQLi/eval/results').glob('*.json')):
    with open(f) as fh:
        results[f.stem] = json.load(fh)

v1 = results.get('v1_seqgan', {}).get('composite_score', 0)
v2_refined = results.get('v2_refined', {}).get('composite_score', 0)
v2_main = results.get('v2_main', {}).get('composite_score', 0)

print(f'V1 SeqGAN: {v1:.4f}')
print(f'V2 main:   {v2_main:.4f}')
print(f'V2 refined: {v2_refined:.4f}')
print(f'Delta: {v2_refined - v1:+.4f}')

if v2_refined - v1 > 0.1:
    print('VERDICT: V2 clearly better')
elif v2_refined - v1 > 0:
    print('VERDICT: V2 marginally better — run ablations')
else:
    print('VERDICT: V2 did not improve — postmortem needed')
" | Out-File -FilePath SeqGAN_SQLi/timeline/V2_VERDICT.txt
```

---

### STEP 5.2: Cleanup & Final Commit

**ACTION:**
```powershell
# Stop Docker container nếu không cần test thêm
docker-compose -f SeqGAN_SQLi/docker/modsec/docker-compose.yml stop

# Cleanup large intermediate files (optional)
# Remove-Item SeqGAN_SQLi/checkpoints/v2/adv_step*.pt -Confirm

git add SeqGAN_SQLi/timeline/V2_RESULTS.md SeqGAN_SQLi/timeline/V2_VERDICT.txt
git commit -m "V2 evaluation complete - see V2_RESULTS.md for findings"
```

---

## TROUBLESHOOTING

### Issue 1: Docker không start

```powershell
docker ps -a  # Xem container có exited không
docker logs seqgan-modsec  # Check logs
docker-compose -f SeqGAN_SQLi/docker/modsec/docker-compose.yml down
docker-compose -f SeqGAN_SQLi/docker/modsec/docker-compose.yml up -d --build --force-recreate
```

### Issue 2: WAF latency cao

- Check Docker resources: Docker Desktop → Settings → Resources → CPU/Memory
- Reduce K (mc_rollout_k) trong config từ 16 → 8
- Increase reward cache size

### Issue 3: Training quá chậm (> 1s/step)

- Confirm CUDA: `nvidia-smi`
- Confirm GPU using: `python -c "import torch; print(torch.cuda.is_available())"`
- Profile: thêm `torch.profiler` quanh G.sample() và reward computation
- Reduce batch_size nếu OOM nhưng giữ steps total

### Issue 4: Mean reward không tăng

- Check phase: `reward_fn.phase` printed at each log
- Check WAF: confirm `use_waf=True` trong phase 2 và 3
- Try reducing LR_G

### Issue 5: Composite score thấp hơn V1

- Run ablations (Step 5+): bỏ từng component để xác định
- Check parse_fail_rate trong AST stats — nếu > 30%, parser issue
- Verify WAF rules — possibly OWASP CRS quá strict cho dataset

---

## ESTIMATED TOTAL TIME

| Phase | Steps | Time (1× RTX 3060) |
|---|---|---|
| Phase 0 (data) | 0.5-12 | 30 phút (skip P1 crawl) |
| Phase 1 (docker) | 1.1-1.2 | 15-20 phút |
| Phase 2 (components) | 2.1-2.10 | 1-2 giờ (smoke tests) |
| Phase 3 (training) | 3.1-3.2 | 15-20 giờ |
| Phase 4 (eval) | 4.1-4.4 | 30-45 phút |
| Phase 5 (postmortem) | 5.1-5.2 | 15 phút |
| **Total** | | **~17-23 giờ** |

---

## EXIT CRITERIA

V2 implementation **COMPLETE** khi:
- [ ] Tất cả 5 PHASE checkpoints committed.
- [ ] `eval/comparison.md` có 5+ models compared.
- [ ] `timeline/V2_VERDICT.txt` có decision rõ ràng.
- [ ] Tất cả Docker containers stopped/cleaned.

V2 implementation **PARTIAL** (acceptable):
- Phase 0-2 done, Phase 3 fails do compute → document trong V2_POSTMORTEM.md, fallback V1.

V2 implementation **FAIL** (rollback):
- Phase 1 (Docker) không setup được → fallback heuristic proxy reward, run V1 với multi-source data.

---

*Playbook này được thiết kế để Claude Code thực thi sequential. Mỗi STEP có VALIDATE rõ ràng. Nếu bị stuck > 30 phút ở 1 step → STOP và escalate cho user.*
