import pandas as pd

disputed = [19, 64, 91, 92, 109, 146, 180, 298, 378, 381, 391, 396, 424, 436, 441, 446, 461, 488]
auto = pd.read_csv("SeqGAN_SQLi/data/split_data_labeled.csv")
raw = pd.read_csv("SeqGAN_SQLi/data/split_data.csv", dtype={"sqli_type": str, "db_engine": str})

for i in disputed:
    r = auto[auto["id"] == i].iloc[0]
    norm = raw.iloc[i].payload_norm
    print(f"=== id={i} auto={r['sqli_type']} {r['db_engine']} {r['confidence']} ===")
    print(norm[:300])
    print()
