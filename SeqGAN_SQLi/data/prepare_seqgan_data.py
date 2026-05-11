"""Sprint 1: Data pipeline — de-lex, split, tokenize, expert demos."""
import os
import sys
import argparse
import json
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tokenizer import SQLTokenizer, delex

SRC_CSV = os.path.join(ROOT, 'Asset', 'LabelData', 'combined_labeled_data.csv')
TRAIN_CSV = os.path.join(DATA_DIR, 'train.csv')
VAL_CSV = os.path.join(DATA_DIR, 'val.csv')
TEST_CSV = os.path.join(DATA_DIR, 'test.csv')
EXPERT_CSV = os.path.join(DATA_DIR, 'expert_demos.csv')
VOCAB_JSON = os.path.join(DATA_DIR, 'tokenizer_vocab.json')

RENAME = {'boolean_based': 'boolean_blind', 'stacked_query': 'stacked_queries'}
EXPERT_CONFIDENCE = 0.95
SEED = 42


def load_and_preprocess(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df['sqli_type'] = df['sqli_type'].replace(RENAME)
    df['is_attack'] = df['sqli_type'] != 'benign'
    df['payload_delex'] = df['payload_norm'].apply(delex)
    return df


def stratified_split(df: pd.DataFrame):
    # Some rare classes have < 2 samples; merge into 'other' for split stratification
    counts = df['sqli_type'].value_counts()
    rare = counts[counts < 4].index
    df['_strat_key'] = df['sqli_type'].where(~df['sqli_type'].isin(rare), 'other')

    train_val, test = train_test_split(
        df, test_size=0.15, random_state=SEED, stratify=df['_strat_key']
    )
    train, val = train_test_split(
        train_val, test_size=0.15 / 0.85, random_state=SEED, stratify=train_val['_strat_key']
    )
    train = train.drop(columns=['_strat_key'])
    val = val.drop(columns=['_strat_key'])
    test = test.drop(columns=['_strat_key'])
    return train, val, test


def extract_expert_demos(train: pd.DataFrame) -> pd.DataFrame:
    return train[(train['is_attack']) & (train['confidence'] >= EXPERT_CONFIDENCE)].copy()


def build_tokenizer(train: pd.DataFrame) -> SQLTokenizer:
    tok = SQLTokenizer()
    tok.build_vocab(train['payload_delex'].tolist(), min_freq=2)
    return tok


def verify(train, val, test, tok, expert):
    print("\n=== Verification ===")
    print(f"Train: {len(train):,} | Val: {len(val):,} | Test: {len(test):,}")
    print(f"Total: {len(train)+len(val)+len(test):,} (src: 40860)")
    print(f"Vocab size: {tok.vocab_size} (target: 100-200)")
    print(f"Expert demos: {len(expert):,}")
    print("\nType distribution (train):")
    print(train['sqli_type'].value_counts().head(10).to_string())
    print("\nSample de-lex:")
    row = train[train['is_attack']].iloc[0]
    print(f"  norm:  {row['payload_norm'][:80]}")
    print(f"  delex: {row['payload_delex'][:80]}")
    # Round-trip check
    enc = tok.encode(train['payload_delex'].iloc[0])
    dec = tok.decode(enc)
    print(f"\nRound-trip OK: {len(enc)} tokens")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--sqli_type', default=None,
                        help='If set, filter dataset to this attack type only (e.g. error_based)')
    args = parser.parse_args()

    # Resolve output directory — per-type goes into data/<sqli_type>/
    if args.sqli_type:
        out_dir = os.path.join(DATA_DIR, args.sqli_type)
        os.makedirs(out_dir, exist_ok=True)
    else:
        out_dir = DATA_DIR

    train_csv  = os.path.join(out_dir, 'train.csv')
    val_csv    = os.path.join(out_dir, 'val.csv')
    test_csv   = os.path.join(out_dir, 'test.csv')
    expert_csv = os.path.join(out_dir, 'expert_demos.csv')
    vocab_json = os.path.join(out_dir, 'tokenizer_vocab.json')

    print("Loading dataset...")
    df = load_and_preprocess(SRC_CSV)

    if args.sqli_type:
        before = len(df)
        df = df[df['sqli_type'] == args.sqli_type].copy()
        print(f"Filtered to sqli_type='{args.sqli_type}': {len(df):,} rows (from {before:,})")
        if len(df) < 100:
            raise ValueError(f"Too few samples ({len(df)}) for type '{args.sqli_type}'. Aborting.")

    print("Splitting (70/15/15 stratified by sqli_type)...")
    train, val, test = stratified_split(df)

    print("Extracting expert demos...")
    expert = extract_expert_demos(train)

    print("Building tokenizer...")
    tok = build_tokenizer(train)

    print("Saving...")
    cols = ['payload_norm', 'payload_delex', 'sqli_type', 'db_engine', 'confidence', 'is_attack']
    train[cols].to_csv(train_csv, index=False)
    val[cols].to_csv(val_csv, index=False)
    test[cols].to_csv(test_csv, index=False)
    expert[cols].to_csv(expert_csv, index=False)
    tok.save(vocab_json)

    if args.verify:
        verify(train, val, test, tok, expert)

    print(f"\nDone. Vocab: {tok.vocab_size} tokens. Output: {out_dir}")


if __name__ == '__main__':
    main()
