import csv
from pathlib import Path
p = Path(r"C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_005_labeled.csv")
rows = list(csv.DictReader(p.open("r", encoding="utf-8")))
low = [r for r in rows if float(r["confidence"]) < 0.7]
print(f"Total low-conf: {len(low)}")
# Show breakdown by sqli_type
from collections import Counter
print(Counter(r["sqli_type"] for r in low))
print("\nSample 12 low-conf payloads:")
for r in low[:12]:
    print(f"--- id={r['id']} type={r['sqli_type']} db={r['db_engine']} conf={r['confidence']}")
    print(f"    payload: {r['payload_inner'][:100]}")
    print(f"    reason: {r['reasoning'][:200]}")
