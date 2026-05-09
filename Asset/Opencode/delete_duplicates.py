import os
import hashlib
from collections import defaultdict

results_dir = r"C:\Users\Admin\Documents\GAN\Asset\Data\results"
file_map = defaultdict(list)

files = sorted([f for f in os.listdir(results_dir) if f.startswith("result_batch_") and f.endswith(".csv")])

for filename in files:
    filepath = os.path.join(results_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()[1:]
    
    content_parts = []
    for line in lines:
        parts = line.strip().split(",")
        if len(parts) >= 4:
            content_parts.append(",".join(parts[1:4]))
    
    content_str = "|".join(content_parts)
    content_hash = hashlib.md5(content_str.encode()).hexdigest()
    file_map[content_hash].append(filename)

duplicates = {h: files for h, files in file_map.items() if len(files) > 1}

files_to_delete = []
for hash_val, filenames in duplicates.items():
    files_to_delete.extend(filenames[1:])

print(f"Files to DELETE: {len(files_to_delete)}")
print("=" * 60)

deleted_count = 0
for filename in files_to_delete:
    filepath = os.path.join(results_dir, filename)
    try:
        os.remove(filepath)
        deleted_count += 1
        print(f"DELETED: {filename}")
    except Exception as e:
        print(f"ERROR: {filename} - {e}")

print(f"\n{'=' * 60}")
print(f"Total deleted: {deleted_count}")