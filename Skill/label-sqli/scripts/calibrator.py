"""
calibrator.py -- Platt scaling calibration for cascade labeler confidence scores.

Converts tier-based confidence scores (0.85/0.72/0.55) into calibrated probabilities
using logistic regression (Platt scaling) fitted on a human-labeled gold set.

Usage:
    # Step 1: Create gold set
    python gold_set_creator.py --input labeled.csv --output gold_200.csv --n 200

    # Step 2: Human reviews gold_200.csv, corrects 'sqli_type' column

    # Step 3: Fit calibration
    python calibrator.py \
        --gold   Asset/LabelData/gold_200.csv \
        --labeled Asset/LabelData/Testing/Testing_labeled.csv \
        --output  calibration_params.json

    # Step 4: Apply calibrated scores (see apply_calibration())

Requires: scikit-learn (pip install scikit-learn)
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


def _check_sklearn():
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.calibration import CalibratedClassifierCV
        return True
    except ImportError:
        print("[FAIL] scikit-learn not installed. Run: pip install scikit-learn")
        sys.exit(1)


def fit_platt_scaling(gold_df: pd.DataFrame, labeled_df: pd.DataFrame) -> dict:
    """
    Fit Platt scaling on gold set.

    gold_df: human-labeled gold (columns: payload, sqli_type as ground truth)
    labeled_df: cascade output (columns: payload, confidence, sqli_type as prediction)

    Returns calibration params dict: {tier: (a, b)} for logistic(a*conf + b).
    """
    from sklearn.linear_model import LogisticRegression
    import numpy as np

    # Merge on payload to get (predicted_conf, correct_bool)
    payload_col = 'payload' if 'payload' in labeled_df.columns else labeled_df.columns[0]
    merged = gold_df.merge(
        labeled_df[[payload_col, 'confidence', 'sqli_type', 'tier']].rename(
            columns={payload_col: 'payload', 'sqli_type': 'pred_type'}
        ),
        on='payload', how='inner'
    )

    if len(merged) < 10:
        print(f"[WARN] Only {len(merged)} overlapping payloads — calibration may be unreliable")

    # Binary: did script predict the same type as human?
    X = merged['confidence'].values.reshape(-1, 1)
    y = (merged['sqli_type'] == merged['pred_type']).astype(int).values

    clf = LogisticRegression(C=1.0, max_iter=1000)
    clf.fit(X, y)

    a = float(clf.coef_[0][0])
    b = float(clf.intercept_[0])
    accuracy = float((clf.predict(X) == y).mean())

    params = {
        'a': round(a, 6),
        'b': round(b, 6),
        'n_samples': len(merged),
        'train_accuracy': round(accuracy, 4),
        'note': 'Platt scaling: P(correct) = sigmoid(a * confidence + b)',
    }
    print(f"[INFO] Calibration fitted: a={a:.4f}, b={b:.4f}, "
          f"acc={accuracy:.3f} on {len(merged)} samples")
    return params


def apply_calibration(confidence: float, params: dict) -> float:
    """Apply Platt scaling to a single confidence score."""
    import math
    z = params['a'] * confidence + params['b']
    return round(1.0 / (1.0 + math.exp(-z)), 4)


def main():
    _check_sklearn()

    parser = argparse.ArgumentParser(
        description="Fit Platt scaling calibration on gold set"
    )
    parser.add_argument('--gold',    required=True, help='Human-labeled gold CSV')
    parser.add_argument('--labeled', required=True, help='Cascade output CSV')
    parser.add_argument('--output',  required=True, help='Output JSON with calibration params')
    args = parser.parse_args()

    gold_path    = Path(args.gold)
    labeled_path = Path(args.labeled)
    output_path  = Path(args.output)

    for p in (gold_path, labeled_path):
        if not p.exists():
            print(f"[FAIL] File not found: {p}")
            sys.exit(1)

    print(f"[INFO] Loading gold set: {gold_path.name}")
    gold_df = pd.read_csv(gold_path, encoding='utf-8-sig')
    print(f"[INFO] Loading labeled output: {labeled_path.name}")
    labeled_df = pd.read_csv(labeled_path, encoding='utf-8-sig')

    params = fit_platt_scaling(gold_df, labeled_df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(params, f, indent=2)
    print(f"[OK] Calibration params written to: {output_path}")

    # Demo: show calibrated scores for typical tier values
    print("\nCalibrated confidence at tier thresholds:")
    for raw in (0.55, 0.70, 0.80, 0.85, 0.92, 1.00):
        cal = apply_calibration(raw, params)
        print(f"  raw={raw:.2f} → calibrated={cal:.4f}")


if __name__ == '__main__':
    main()
