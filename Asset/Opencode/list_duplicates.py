import os
import hashlib
from collections import defaultdict

results_dir = r"C:\Users\Admin\Documents\GAN\Asset\Data\results"
file_map = defaultdict(list)

files = sorted([f for f in os.listdir(results_dir) if f.startswith("result_batch_") and f.endswith(".csv")])

print(f"Total files: {len(files)}")
print("=" * 60)

for filename in files:
    filepath = os.path.join(results_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()[1:]
    
    content_parts = []
    for line in lines:
        parts = line.strip().split(",")
        if len(parts) >= 4:
            content_parts.append(",".join(parts[1:]))  # giữ TẤT CẢ: sqli_type, db_engine, confidence, reasoning
    
    content_str = "|".join(content_parts)
    content_hash = hashlib.md5(content_str.encode()).hexdigest()
    file_map[content_hash].append(filename)

duplicates = {h: files for h, files in file_map.items() if len(files) > 1}

print(f"Duplicate groups found: {len(duplicates)}")
print("=" * 60)

total_dup = 0
group_num = 1

for hash_val, filenames in sorted(duplicates.items(), key=lambda x: int(x[1][0].replace("result_batch_", "").replace(".csv", ""))):
    batch_nums = [int(f.replace("result_batch_", "").replace(".csv", "")) for f in filenames]
    print(f"\n[Group {group_num}] {len(filenames)} files trùng nhau:")
    print(f"  Batch numbers: {batch_nums}")
    total_dup += len(filenames)
    group_num += 1

print(f"\n{'=' * 60}")
print(f"TONG DU LIEU TRUNG: {total_dup} files")
print(f"GIU LAI: {len(duplicates)} files unique")
print(f"TONG SAU XOA: {total_dup + len(duplicates)} files")