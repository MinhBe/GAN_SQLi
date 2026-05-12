"""
train_xgboost_ids.py — Train XGBoost IDS classifier cho ML-IDS evasion metric.
Dùng char n-gram TF-IDF features để phân biệt SQLi vs benign payloads.
"""
import argparse
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, roc_auc_score
import xgboost as xgb

sys.path.insert(0, str(Path(__file__).parent.parent))


SYNTHETIC_BENIGN = [
    "1", "2", "admin", "test", "hello", "user", "john", "password",
    "user@test.com", "admin@example.com", "2024-01-01", "true", "false",
    "SELECT", "product_name", "order_id", "customer", "item", "100",
] * 50  # ~1000 synthetic benign samples


def train_ids(train_csv: str, val_csv: str, out_dir: str):
    out_p = Path(out_dir)
    out_p.mkdir(parents=True, exist_ok=True)

    df_train = pd.read_csv(train_csv)
    df_val = pd.read_csv(val_csv)

    # Payload column
    payload_col = next(
        (c for c in ["payload_norm", "payload_delex", "payload"] if c in df_train.columns),
        df_train.columns[0],
    )
    print(f"Using payload column: {payload_col}")

    # Attack label: sqli_type != benign
    for df in [df_train, df_val]:
        if "sqli_type" in df.columns:
            df["is_attack"] = (df["sqli_type"] != "benign").astype(int)
        else:
            df["is_attack"] = 1  # assume all attack

    # Add synthetic benign if no benign in training data
    if df_train["is_attack"].sum() == len(df_train):
        print(f"No benign in train — adding {len(SYNTHETIC_BENIGN)} synthetic benign samples")
        benign_df = pd.DataFrame({
            payload_col: SYNTHETIC_BENIGN,
            "is_attack": [0] * len(SYNTHETIC_BENIGN),
        })
        df_train = pd.concat([df_train, benign_df], ignore_index=True)

    X_texts_train = df_train[payload_col].fillna("").astype(str).tolist()
    X_texts_val = df_val[payload_col].fillna("").astype(str).tolist()
    y_train = df_train["is_attack"].values
    y_val = df_val["is_attack"].values

    print(f"Train: {len(X_texts_train)} samples ({y_train.sum()} attacks, {(~y_train.astype(bool)).sum()} benign)")
    print(f"Val:   {len(X_texts_val)} samples ({y_val.sum()} attacks)")

    # TF-IDF with char n-grams (robust to obfuscation)
    vec = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 4),
        max_features=5000,
        sublinear_tf=True,
    )
    X_train = vec.fit_transform(X_texts_train)
    X_val = vec.transform(X_texts_val)

    clf = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss",
        verbosity=0,
    )
    clf.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )

    y_pred = clf.predict(X_val)
    y_proba = clf.predict_proba(X_val)[:, 1]

    print("\n=== IDS Classifier Evaluation ===")
    print(classification_report(y_val, y_pred, target_names=["benign", "attack"]))
    if len(np.unique(y_val)) > 1:
        auc = roc_auc_score(y_val, y_proba)
        print(f"AUC-ROC: {auc:.4f}")

    joblib.dump(clf, out_p / "ids_xgb.pkl")
    joblib.dump(vec, out_p / "ids_vectorizer.pkl")
    print(f"\nSaved: {out_p / 'ids_xgb.pkl'}")
    print(f"Saved: {out_p / 'ids_vectorizer.pkl'}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_csv", default="SeqGAN_SQLi/data/v2/train.csv")
    parser.add_argument("--val_csv", default="SeqGAN_SQLi/data/v2/val.csv")
    parser.add_argument("--out_dir", default="SeqGAN_SQLi/eval/ids_classifier")
    args = parser.parse_args()
    train_ids(args.train_csv, args.val_csv, args.out_dir)


if __name__ == "__main__":
    main()
