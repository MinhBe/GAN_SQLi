import pandas as pd

disputed = [19, 64, 91, 92, 109, 146, 180, 298, 378, 381, 391, 396, 424, 436, 441, 446, 461, 488]
auto = pd.read_csv("SeqGAN_SQLi/data/split_data_labeled.csv")

manual = pd.concat(
    [pd.read_csv(f"SeqGAN_SQLi/data/split_data_labeled_batch_{i}.csv") for i in range(1, 10)],
    ignore_index=True,
)

m = manual.merge(auto, on="id", suffixes=("_manual", "_auto"))
mismatch = m[m["sqli_type_manual"] != m["sqli_type_auto"]]

print(f"Remaining disagreements: {len(mismatch)}/{len(m)}")

for _, r in mismatch.iterrows():
    print(f"  id={r['id']:3d}: manual={r['sqli_type_manual']:15s} auto={r['sqli_type_auto']:15s}")

print(f"\nFinal distribution:")
print(auto["sqli_type"].value_counts().to_string())
