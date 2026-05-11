import pandas as pd

auto = pd.read_csv("SeqGAN_SQLi/data/split_data_labeled.csv")
manual = pd.concat([pd.read_csv(f"SeqGAN_SQLi/data/split_data_labeled_batch_{i}.csv") for i in range(1, 10)], ignore_index=True)
m = manual.merge(auto, on="id", suffixes=("_m", "_a"))
d = m[m["sqli_type_m"] != m["sqli_type_a"]]
print(f"{len(d)} disagreements remaining:")
for _, r in d.iterrows():
    print(f"  id={r['id']:3d}: manual={r['sqli_type_m']:15s} auto={r['sqli_type_a']:15s}")
