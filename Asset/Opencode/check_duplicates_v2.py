import os
import hashlib
from collections import defaultdict

results_dir = r"C:\Users\Admin\Documents\GAN\Asset\Data\results"
file_map = defaultdict(list)

files = sorted([f for f in os.listdir(results_dir) if f.startswith("result_batch_") and f.endswith(".csv")])

print(f"Total files: {len(files)}")

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

print(f"\nDuplicate groups found: {len(duplicates)}")
print("=" * 60)

total_dup_files = 0
for i, (hash_val, filenames) in enumerate(duplicates.items(), 1):
    print(f"\nGroup {i}: {len(filenames)} files - EXACT MATCH (bao gom reasoning)")
    for f in filenames:
        print(f"  - {f}")
    total_dup_files += len(filenames)

print(f"\n{'=' * 60}")
print(f"Total duplicate files to DELETE: {total_dup_files}")
print(f"Unique content to KEEP: {len(file_map) - len(duplicates)}")