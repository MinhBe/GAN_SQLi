"""Prepare MLE training data from gold + silver tiers."""
import os, sys, json, random
from collections import Counter

import pandas as pd

SPECIAL_TOKENS = ['<PAD>', '<UNK>', '<SOS>', '<EOS>']

def build_vocab(texts, min_freq=1):
    counter = Counter()
    for text in texts:
        for token in text.split():
            counter[token] += 1
    token2id = {t: i for i, t in enumerate(SPECIAL_TOKENS)}
    idx = len(SPECIAL_TOKENS)
    for token, freq in counter.most_common():
        if freq >= min_freq:
            token2id[token] = idx
            idx += 1
    return token2id

def main():
    random.seed(42)
    base = 'Asset/LabelData/OpenCode'
    out_dir = os.path.join(base, 'mle_data')
    os.makedirs(out_dir, exist_ok=True)

    # Read gold + silver
    gold = pd.read_csv(os.path.join(base, 'gold.csv'))
    silver = pd.read_csv(os.path.join(base, 'silver.csv'))
    print(f"Gold: {len(gold)}, Silver: {len(silver)}")

    df = pd.concat([gold, silver], ignore_index=True)
    df.rename(columns={'payload_delex_v2': 'payload_delex'}, inplace=True)
    print(f"Total: {len(df)}")

    # Build tokenizer from delex text
    texts = df['payload_delex'].fillna('').tolist()
    token2id = build_vocab(texts)
    print(f"Vocab size: {len(token2id)}")

    # Save tokenizer
    vocab_path = os.path.join(out_dir, 'tokenizer_vocab.json')
    with open(vocab_path, 'w', encoding='utf-8') as f:
        json.dump(token2id, f, ensure_ascii=False, indent=2)
    print(f"Saved tokenizer -> {vocab_path}")

    # Shuffle and split 90/10
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    n = len(df)
    n_train = int(0.9 * n)
    train = df.iloc[:n_train]
    val = df.iloc[n_train:]

    train_path = os.path.join(out_dir, 'train.csv')
    val_path = os.path.join(out_dir, 'val.csv')
    train[['payload_delex']].to_csv(train_path, index=False)
    val[['payload_delex']].to_csv(val_path, index=False)
    print(f"Train: {len(train)}, Val: {len(val)}")

    # Empty expert_demos.csv
    expert_path = os.path.join(out_dir, 'expert_demos.csv')
    pd.DataFrame(columns=['payload_delex']).to_csv(expert_path, index=False)
    print(f"Expert demos: (empty)")

    # Print unique tokens for reference
    print("\nTop-20 tokens:")
    for i, (tok, freq) in enumerate(Counter(' '.join(texts).split()).most_common(20)):
        print(f"  {i+1:2d}. {tok:20s} x{freq}")

if __name__ == '__main__':
    main()
