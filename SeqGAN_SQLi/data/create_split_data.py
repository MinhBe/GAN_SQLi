import pandas as pd

INPUT = "SeqGAN_SQLi/data/combined_full.csv"
OUTPUT = "SeqGAN_SQLi/data/split_data.csv"
TARGET_TYPES = ["error_based", "boolean_blind", "time_blind", "union_based"]

df = pd.read_csv(INPUT)

df = df[df["sqli_type"].isin(TARGET_TYPES) & (df["is_attack"] == True)]

df = df.drop(
    columns=["sqli_type", "db_engine", "confidence", "is_attack", "source", "tier"],
    errors="ignore",
)

df = df[["payload_norm", "payload_delex"]]

df["sqli_type"] = ""
df["db_engine"] = ""
df["confidence"] = 0.0

df.insert(0, "id", range(len(df)))

df.to_csv(OUTPUT, index=False)

print(f"Saved {len(df)} rows to {OUTPUT}")
print(df["sqli_type"].value_counts())

type_counts = pd.read_csv(INPUT)
type_counts = type_counts[type_counts["sqli_type"].isin(TARGET_TYPES) & (type_counts["is_attack"] == True)]
print("\nPer-type breakdown:")
print(type_counts["sqli_type"].value_counts())
