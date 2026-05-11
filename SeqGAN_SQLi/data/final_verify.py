import pandas as pd

df = pd.read_csv("SeqGAN_SQLi/data/split_data_labeled.csv")

print(f"Total rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"Nulls:\n{df.isnull().sum()}")
print()

t = df["sqli_type"]
print(f"sqli_type distribution:")
print(f"  error_based:   {(t=='error_based').sum()}")
print(f"  boolean_blind: {(t=='boolean_blind').sum()}")
print(f"  time_blind:    {(t=='time_blind').sum()}")
print(f"  union_based:   {(t=='union_based').sum()}")
print(f"  blank/other:   {(~t.isin(['error_based','boolean_blind','time_blind','union_based'])).sum()}")
print()

e = df["db_engine"]
print(f"db_engine distribution:")
print(f"  oracle:      {(e=='oracle').sum()}")
print(f"  mysql:       {(e=='mysql').sum()}")
print(f"  mssql:       {(e=='mssql').sum()}")
print(f"  postgresql:  {(e=='postgresql').sum()}")
print(f"  generic:     {(e=='generic').sum()}")
print(f"  blank/other: {(~e.isin(['oracle','mysql','mssql','postgresql','generic'])).sum()}")
print()

c = df["confidence"]
print(f"confidence distribution:")
print(f"  1.00: {(c==1.00).sum()}")
print(f"  0.85: {(c==0.85).sum()}")
print(f"  0.70: {(c==0.70).sum()}")
print(f"  other: {((c!=1.00)&(c!=0.85)&(c!=0.70)).sum()}")

print(f"\nValid values check:")
print(f"  sqli_type valid:  {(t.isin(['error_based','boolean_blind','time_blind','union_based'])).sum()}/{len(df)}")
print(f"  db_engine valid:  {(e.isin(['oracle','mysql','mssql','postgresql','generic'])).sum()}/{len(df)}")
print(f"  confidence valid: {(c.isin([1.0,0.85,0.7])).sum()}/{len(df)}")

print(f"\nSample (first 5):")
print(df.head(5).to_string())
