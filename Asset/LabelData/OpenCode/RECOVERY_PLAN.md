# Recovery Plan — Phục hồi pipeline khi bị gián đoạn đột ngột

> **Mục đích**: Khi pipeline Phase 2→3→4 bị dừng giữa chừng (crash, timeout, restart),
> dùng file này để xác định trạng thái và resume nhanh mà không làm lại từ đầu.

---

## 1. CHECK TRẠNG THÁI NHANH

Chạy lệnh sau để biết pipeline đang ở phase nào:

```bash
python -c "
import glob, os, pandas as pd

print('=== STATE CHECK ===')

# Phase 1
tri = 'Asset/LabelData/triaged.csv'
if os.path.exists(tri):
    df = pd.read_csv(tri)
    print(f'[P1] TRIAGE: {len(df)} rows | verdicts: {dict(df[\"verdict\"].value_counts())}')
else:
    print('[P1] TRIAGE: NOT FOUND')

# Phase 2a
cq = 'Asset/LabelData/chat_queue.csv'
if os.path.exists(cq):
    df = pd.read_csv(cq)
    print(f'[P2a] chat_queue: {len(df)} rows')
    has_hints = all(c in df.columns for c in ['a_type','a_db','c_type','c_db'])
    print(f'[P2a] A+C hints present: {has_hints}')
else:
    print('[P2a] chat_queue: NOT FOUND')

# Phase 2b
chunks_dir = 'Asset/LabelData/_chunks'
if os.path.isdir(chunks_dir):
    plain = [f for f in os.listdir(chunks_dir) if f.endswith('.csv') and '_labeled' not in f and f.startswith('chunk_')]
    labeled = sorted(glob.glob(os.path.join(chunks_dir, 'chunk_*_labeled.csv')))
    print(f'[P2b] Chunks in _chunks/: {len(plain)} plain, {len(labeled)} labeled')
else:
    print('[P2b] _chunks/: NOT FOUND')

# Phase 2d
merged = 'relabeled_chat.csv'
if os.path.exists(merged):
    df = pd.read_csv(merged)
    print(f'[P2d] relabeled_chat.csv: {len(df)} rows')
else:
    print('[P2d] relabeled_chat.csv: NOT FOUND')

# Phase 3a
final = 'merged_final.csv'
if os.path.exists(final):
    df = pd.read_csv(final)
    print(f'[P3a] merged_final.csv: {len(df)} rows')
else:
    print('[P3a] merged_final.csv: NOT FOUND')

# Phase 3b
stripped = 'stripped.csv'
if os.path.exists(stripped):
    df = pd.read_csv(stripped)
    has_inner = 'payload_inner' in df.columns
    print(f'[P3b] stripped.csv: {len(df)} rows, payload_inner: {has_inner}')
else:
    print('[P3b] stripped.csv: NOT FOUND')

# Phase 3c
ds = 'dataset_v3.csv'
if os.path.exists(ds):
    df = pd.read_csv(ds)
    has_delex = 'payload_delex_v2' in df.columns
    n_unique = df['payload_delex_v2'].nunique() if has_delex else 0
    print(f'[P3c] dataset_v3.csv: {len(df)} rows, unique delex: {n_unique}')
else:
    print('[P3c] dataset_v3.csv: NOT FOUND')

# Phase 4
oc = 'Asset/LabelData/OpenCode'
for tier in ['dataset_v3_balanced','gold','silver','bronze']:
    f = os.path.join(oc, f'{tier}.csv')
    if os.path.exists(f):
        df = pd.read_csv(f)
        print(f'[P4] {tier}.csv: {len(df)} rows')
    else:
        print(f'[P4] {tier}.csv: NOT FOUND')
"
```

---

## 2. RECOVERY THEO TỪNG PHASE

### Phase 1 — TRIAGE bị dừng

```
Triệu chứng: triaged.csv không có hoặc chưa đủ 40,860 rows
Recovery:
  1. Xóa file cũ (nếu corrupted):
     Remove-Item Asset/LabelData/triaged.csv -ErrorAction SilentlyContinue
  2. Chạy lại critique_labels.py:
     python Skill/sqli-data-curator/scripts/critique_labels.py \
       --input Asset/LabelData/combined_labeled_data.csv \
       --output Asset/LabelData/triaged.csv
  3. Filter verdicts:
     python -c "
     import pandas as pd
     df = pd.read_csv('Asset/LabelData/triaged.csv')
     df[df['verdict']=='KEEP'].to_csv('Asset/LabelData/keep.csv', index=False)
     df[df['verdict']=='RELABEL'].to_csv('Asset/LabelData/to_relabel.csv', index=False)
     print('KEEP:', (df['verdict']=='KEEP').sum())
     print('RELABEL:', (df['verdict']=='RELABEL').sum())
     print('DROP:', (df['verdict']=='DROP').sum())
     "
```
Thời gian: ~1 phút.

### Phase 2a — Pre-label A+C bị dừng

```
Triệu chứng: chat_queue.csv không có hoặc sai schema
Recovery:
  python Skill/sqli-data-curator/scripts/label_payload.py \
    --mode chat_queue \
    --input Asset/LabelData/to_relabel.csv \
    --output Asset/LabelData/chat_queue.csv
```
Thời gian: ~2 phút.

### Phase 2b — Chia chunks bị dừng

```
Triệu chứng: _chunks/ không có hoặc thiếu chunk CSV files
Recovery:
  Remove-Item -Recurse Asset/LabelData/_chunks/ -ErrorAction SilentlyContinue
  python Skill/sqli-data-curator/scripts/chat_label_coordinator.py \
    --input Asset/LabelData/chat_queue.csv \
    --chunk_size 200 \
    --temp_dir Asset/LabelData/_chunks/
```
⚠️ Cảnh báo: Xóa _chunks/ sẽ mất các chunk đã label. Chỉ làm nếu thực sự cần.
Nếu chỉ thiếu vài chunk, dùng lệnh dưới đây để tạo chunk bị thiếu:
```bash
python -c "
import pandas as pd, os
cq = pd.read_csv('Asset/LabelData/chat_queue.csv')
chunk_size = 200
temp_dir = 'Asset/LabelData/_chunks'
os.makedirs(temp_dir, exist_ok=True)
n_chunks = (len(cq) + chunk_size - 1) // chunk_size
done = set()
for f in os.listdir(temp_dir):
    if f.endswith('_labeled.csv'):
        done.add(f.replace('_labeled.csv','.csv'))
for i in range(n_chunks):
    fname = f'chunk_{i+1:03d}.csv'
    if fname not in done and fname not in os.listdir(temp_dir):
        start = i * chunk_size
        end = min(start + chunk_size, len(cq))
        cq.iloc[start:end].to_csv(os.path.join(temp_dir, fname), index=False)
        print(f'Created missing: {fname}')
"
```

### Phase 2c — Subagent labeling bị dừng (THƯỜNG GẶP NHẤT)

```
Triệu chứng: Một số chunk_*.csv chưa có chunk_*_labeled.csv tương ứng
Recovery step-by-step:

1. Detect chunks chưa label:
   python -c "
   import glob, os
   chunks_dir = 'Asset/LabelData/_chunks'
   all_chunks = sorted(glob.glob(os.path.join(chunks_dir, 'chunk_*.csv')))
   all_chunks = [f for f in all_chunks if '_labeled' not in f]
   labeled = set(os.listdir(chunks_dir))
   
   missing = []
   for f in all_chunks:
       fname = os.path.basename(f)
       labeled_name = fname.replace('.csv', '_labeled.csv')
       if labeled_name not in labeled:
           missing.append(f)
   
   print(f'Total chunks: {len(all_chunks)}')
   print(f'Missing labeled: {len(missing)}')
   for f in missing[:10]:
       df = pd.read_csv(f)
       print(f'  {os.path.basename(f)}: {len(df)} rows')
   if len(missing) > 10:
       print(f'  ... and {len(missing)-10} more')
   "

2. Label các chunk missing:
   python -c "
   import pandas as pd, glob, os, sys, hashlib, re

   sys.path.insert(0, 'Skill/sqli-data-curator/scripts')
   from label_chunk_helper import label_chunk_claude

   # Load whitelist
   with open('Skill/sqli-data-curator/references/function_whitelist.md') as f:
       content = f.read()

   chunks_dir = 'Asset/LabelData/_chunks'
   labeled = set(os.listdir(chunks_dir))
   taxonomy = {}  # Simplified taxonomy

   all_chunks = sorted(glob.glob(os.path.join(chunks_dir, 'chunk_*.csv')))
   all_chunks = [f for f in all_chunks if '_labeled' not in f]

   for f in all_chunks:
       fname = os.path.basename(f)
       labeled_name = fname.replace('.csv', '_labeled.csv')
       if labeled_name in labeled:
           continue
       
       df = pd.read_csv(f)
       labeled_df, stats = label_chunk_claude(df, FUNCTION_WHITELIST, taxonomy)
       out_path = os.path.join(chunks_dir, labeled_name)
       labeled_df.to_csv(out_path, index=False)
       print(f'Labeled {fname}: {len(labeled_df)} rows, types: {stats[\"type_distribution\"]}')
   "

⚠️ Lưu ý: Script trên dùng label_chunk_helper.py (rule-based).
Nếu muốn chất lượng subagent Claude, spawn từng chunk qua Task tool.
```
Thời gian: ~30-45 phút cho ~28 chunks nếu batch, ~1h nếu subagent.

### Phase 2d — Merge chunks bị dừng

```
Triệu chứng: relabeled_chat.csv chưa có hoặc sai số rows
Recovery:
  python Skill/sqli-data-curator/scripts/merge_chunks.py \
    --temp_dir Asset/LabelData/_chunks/ \
    --output Asset/LabelData/relabeled_chat.csv
```
Thời gian: ~1 phút.

### Phase 3a — Concat KEEP + RELABELED bị dừng

```
Triệu chứng: merged_final.csv chưa có
Recovery:
  python -c "
  import pandas as pd
  keep = pd.read_csv('Asset/LabelData/keep.csv')
  relabeled = pd.read_csv('Asset/LabelData/relabeled_chat.csv')
  merged = pd.concat([keep, relabeled], ignore_index=True)
  merged = merged.drop_duplicates(subset='id')
  merged.to_csv('Asset/LabelData/merged_final.csv', index=False)
  print(f'Merged: {len(merged)} rows (keep={len(keep)} + relabeled={len(relabeled)})')
  "
```
Thời gian: ~10 giây.

### Phase 3b — Strip wrapper bị dừng

```
Triệu chứng: stripped.csv không có hoặc thiếu payload_inner
Recovery:
  python Skill/sqli-data-curator/scripts/strip_wrapper.py \
    --input Asset/LabelData/merged_final.csv \
    --output Asset/LabelData/stripped.csv \
    --col_in payload_norm --col_out payload_inner
```
Thời gian: ~1 phút.

### Phase 3c — Delex v2 bị dừng

```
Triệu chứng: dataset_v3.csv không có
Recovery:
  python Skill/sqli-data-curator/scripts/delex_v2.py \
    --input Asset/LabelData/stripped.csv \
    --output Asset/LabelData/dataset_v3.csv \
    --col_in payload_inner --col_out payload_delex_v2 --stats
```
Thời gian: ~3 phút.

### Phase 4a — Resample bị dừng

```
Triệu chứng: dataset_v3_balanced.csv chưa có
Recovery:
  python Skill/sqli-data-curator/scripts/resample_balanced.py \
    --input Asset/LabelData/dataset_v3.csv \
    --output Asset/LabelData/OpenCode/dataset_v3_balanced.csv \
    --cap_signature 30 --cap_type_db 300
```
Thời gian: ~1 phút.

### Phase 4b — Tier split bị dừng

```
Triệu chứng: gold/silver/bronze.csv chưa có
Recovery:
  python Skill/sqli-data-curator/scripts/tier_split.py \
    --input Asset/LabelData/OpenCode/dataset_v3_balanced.csv \
    --output_dir Asset/LabelData/OpenCode/
```
Thời gian: ~30 giây.

---

## 3. FILE INTERMEDIATE — KHÔNG XÓA

| File | Vai trò | Tái tạo được? |
|------|---------|:-------------:|
| `combined_labeled_data.csv` | Raw data gốc (source) | N/A |
| `triaged.csv` | Verdict KEEP/RELABEL/DROP | ✅ ~1 phút |
| `keep.csv` | KEEP rows (18,144) | ✅ từ triaged |
| `to_relabel.csv` | RELABEL rows (22,401) | ✅ từ triaged |
| `chat_queue.csv` | A+C hints cho subagent | ✅ ~2 phút |
| `_chunks/chunk_NNN.csv` | Chunk plain data | ✅ ~30 giây |
| **`_chunks/chunk_NNN_labeled.csv`** | **Subagent output (MẤT CÔNG)** | **❌ mất 1-1.5h** |
| `relabeled_chat.csv` | Merged chunks output | ✅ từ _labeled |
| `merged_final.csv` | keep + relabeled merged | ✅ |
| `stripped.csv` | payload_inner | ✅ |
| `dataset_v3.csv` | payload_delex_v2 | ✅ |
| `dataset_v3_balanced.csv` | Resampled | ✅ |
| `gold/silver/bronze.csv` | **FINAL OUTPUT** | ✅ |

> ⚠️ **chunk_NNN_labeled.csv là files mất công nhất** (1-1.5h để label 113 chunks).
> Nếu bị xóa, phải chạy lại Phase 2c từ đầu. **Backup _chunks/ trước khi xóa.**

---

## 4. LỆNH RECOVERY NHANH (1-LINER)

```bash
# Check state
# (Xem phần 1)

# Resume từ Phase 2c (label chunks missing)
python -c "
import pandas as pd, glob, os, sys
sys.path.insert(0, 'Skill/sqli-data-curator/scripts')
from label_chunk_helper import label_chunk_claude

chunks_dir = 'Asset/LabelData/_chunks'
labeled = set(os.listdir(chunks_dir))
all_chunks = sorted(glob.glob(os.path.join(chunks_dir, 'chunk_*.csv')))
all_chunks = [f for f in all_chunks if '_labeled' not in f]

for f in all_chunks:
    fname = os.path.basename(f)
    labeled_name = fname.replace('.csv', '_labeled.csv')
    if labeled_name in labeled:
        continue
    df = pd.read_csv(f)
    labeled_df, stats = label_chunk_claude(df, {}, {})
    labeled_df.to_csv(os.path.join(chunks_dir, labeled_name), index=False)
    print(f'Labeled {fname}: {len(labeled_df)} rows')
"

# Resume từ Phase 2d
python Skill/sqli-data-curator/scripts/merge_chunks.py \
    --temp_dir Asset/LabelData/_chunks/ \
    --output Asset/LabelData/relabeled_chat.csv

# Resume từ Phase 3a
python -c "
import pandas as pd
keep = pd.read_csv('Asset/LabelData/keep.csv')
rel = pd.read_csv('Asset/LabelData/relabeled_chat.csv')
merged = pd.concat([keep, rel], ignore_index=True).drop_duplicates(subset='id')
merged.to_csv('Asset/LabelData/merged_final.csv', index=False)
print(f'Merged: {len(merged)} rows')
"

# Resume từ Phase 3b
python Skill/sqli-data-curator/scripts/strip_wrapper.py \
    --input Asset/LabelData/merged_final.csv \
    --output Asset/LabelData/stripped.csv \
    --col_in payload_norm --col_out payload_inner

# Resume từ Phase 3c
python Skill/sqli-data-curator/scripts/delex_v2.py \
    --input Asset/LabelData/stripped.csv \
    --output Asset/LabelData/dataset_v3.csv \
    --col_in payload_inner --col_out payload_delex_v2 --stats

# Resume từ Phase 4a
python Skill/sqli-data-curator/scripts/resample_balanced.py \
    --input Asset/LabelData/dataset_v3.csv \
    --output Asset/LabelData/OpenCode/dataset_v3_balanced.csv \
    --cap_signature 30 --cap_type_db 300

# Resume từ Phase 4b
python Skill/sqli-data-curator/scripts/tier_split.py \
    --input Asset/LabelData/OpenCode/dataset_v3_balanced.csv \
    --output_dir Asset/LabelData/OpenCode/
```

---

## 5. ROLLBACK STRATEGY

| Phase fail | Backup | Hành động |
|------------|--------|-----------|
| Phase 1 | `combined_labeled_data.csv` | Debug `critique_labels.py`, rerun |
| Phase 2 | `_chunks/` vẫn còn | Respawn chunks chưa có `_labeled` |
| Phase 3 | `merged_final.csv` | Debug `strip_wrapper.py` / `delex_v2.py`, rerun |
| Phase 4 | `dataset_v3.csv` | Tune `cap_signature`, rerun `resample + tier_split` |

**Nguyên tắc**: Giữ tất cả intermediate files cho đến khi verification hoàn tất.
