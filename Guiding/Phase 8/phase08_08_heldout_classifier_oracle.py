# -*- coding: utf-8 -*-
"""
Phase 08 - Script 8: held-out classifier oracle for evasion scoring.

This script trains a local SQLi-vs-benign classifier on the Phase 8 train split,
sets a detection threshold using the dev split, evaluates the oracle on the
held-out test split, then scores generated JSONL samples.

It writes detector-result CSVs compatible with phase08_03_evaluator_contract.py:

    sample_id,detected

Raw payload text is never written to reports.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, average_precision_score, precision_recall_fscore_support, roc_auc_score
from sklearn.pipeline import FeatureUnion, Pipeline


if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


PHASE_DIR = Path(__file__).resolve().parent
DEFAULT_SPLIT_DIR = PHASE_DIR / "outputs" / "delex_cluster_split"
DEFAULT_OUT_DIR = PHASE_DIR / "outputs" / "classifier_oracle_results"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a held-out SQLi classifier oracle and score generated samples.")
    parser.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    parser.add_argument("--train", type=Path, default=None)
    parser.add_argument("--dev", type=Path, default=None)
    parser.add_argument("--test", type=Path, default=None)
    parser.add_argument("--text-col", default="payload_delex_v5")
    parser.add_argument("--label-col", default="is_sqli")
    parser.add_argument("--technique-col", default="technique_primary")
    parser.add_argument("--max-positive", type=int, default=150000)
    parser.add_argument("--max-negative", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=808)
    parser.add_argument("--target-benign-fpr", type=float, default=0.05)
    parser.add_argument("--max-iter", type=int, default=12)
    parser.add_argument(
        "--samples",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Generated JSONL samples to score. May be supplied multiple times.",
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--report-name", default="08_classifier_oracle_core_comparison")
    return parser.parse_args()


def ensure_under_phase(path: Path) -> Path:
    resolved = path.resolve()
    phase = PHASE_DIR.resolve()
    if resolved != phase and phase not in resolved.parents:
        raise ValueError(f"Refusing to write outside Phase 8: {resolved}")
    return resolved


def resolve_split_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    train = args.train or args.split_dir / "train.parquet"
    dev = args.dev or args.split_dir / "dev.parquet"
    test = args.test or args.split_dir / "test.parquet"
    for path in (train, dev, test):
        if not path.exists():
            raise FileNotFoundError(path)
    return train, dev, test


def parse_sample_specs(specs: list[str]) -> list[tuple[str, Path]]:
    parsed: list[tuple[str, Path]] = []
    for spec in specs:
        if "=" not in spec:
            raise ValueError(f"--samples must use NAME=PATH format, got: {spec}")
        name, raw_path = spec.split("=", 1)
        name = name.strip()
        path = Path(raw_path.strip())
        if not name:
            raise ValueError(f"Missing sample name in: {spec}")
        if not path.exists():
            raise FileNotFoundError(path)
        parsed.append((name, path))
    return parsed


def load_split(path: Path, text_col: str, label_col: str, technique_col: str | None = None) -> pd.DataFrame:
    columns = [text_col, label_col]
    if technique_col:
        columns.append(technique_col)
    df = pd.read_parquet(path, columns=columns)
    df = df.dropna(subset=[text_col, label_col]).copy()
    df[text_col] = df[text_col].astype(str)
    df[label_col] = df[label_col].astype(int)
    if technique_col and technique_col in df.columns:
        df[technique_col] = df[technique_col].fillna("unknown").astype(str)
    return df


def sample_training_rows(
    df: pd.DataFrame,
    label_col: str,
    max_positive: int,
    max_negative: int,
    seed: int,
) -> pd.DataFrame:
    positives = df[df[label_col] == 1]
    negatives = df[df[label_col] == 0]
    if positives.empty or negatives.empty:
        raise ValueError("Classifier training requires both positive SQLi and benign rows.")
    pos_n = min(len(positives), max_positive)
    neg_n = min(len(negatives), max_negative)
    sampled = pd.concat(
        [
            positives.sample(n=pos_n, random_state=seed),
            negatives.sample(n=neg_n, random_state=seed + 1),
        ],
        ignore_index=True,
    )
    return sampled.sample(frac=1.0, random_state=seed + 2).reset_index(drop=True)


def build_model(max_iter: int, seed: int) -> Pipeline:
    features = FeatureUnion(
        [
            (
                "char",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 6),
                    min_df=2,
                    max_features=220000,
                    lowercase=True,
                    sublinear_tf=True,
                ),
            ),
            (
                "word",
                TfidfVectorizer(
                    analyzer="word",
                    token_pattern=r"(?u)\b\w+\b|__\w+__|[^\w\s]",
                    ngram_range=(1, 3),
                    min_df=2,
                    max_features=120000,
                    lowercase=True,
                    sublinear_tf=True,
                ),
            ),
        ]
    )
    clf = SGDClassifier(
        loss="log_loss",
        penalty="elasticnet",
        alpha=1e-5,
        l1_ratio=0.05,
        class_weight="balanced",
        max_iter=max_iter,
        tol=1e-4,
        random_state=seed,
        n_jobs=-1,
    )
    return Pipeline([("features", features), ("clf", clf)])


def score_texts(model: Pipeline, texts: list[str]) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(texts)[:, 1]
    scores = model.decision_function(texts)
    return 1.0 / (1.0 + np.exp(-scores))


def choose_threshold(dev_y: np.ndarray, dev_scores: np.ndarray, target_benign_fpr: float) -> float:
    benign_scores = dev_scores[dev_y == 0]
    if len(benign_scores) == 0:
        raise ValueError("Dev split contains no benign rows; cannot set FPR-controlled threshold.")
    quantile = max(0.0, min(1.0, 1.0 - target_benign_fpr))
    threshold = float(np.quantile(benign_scores, quantile))
    return float(np.nextafter(threshold, np.inf))


def binary_metrics(y_true: np.ndarray, scores: np.ndarray, threshold: float) -> dict[str, Any]:
    y_pred = (scores >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())
    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    benign_den = max(tn + fp, 1)
    sqli_den = max(tp + fn, 1)
    try:
        roc_auc = float(roc_auc_score(y_true, scores))
    except ValueError:
        roc_auc = None
    try:
        avg_precision = float(average_precision_score(y_true, scores))
    except ValueError:
        avg_precision = None
    return {
        "n": int(len(y_true)),
        "threshold": threshold,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision),
        "recall_tpr": float(recall),
        "f1": float(f1),
        "benign_fpr": fp / benign_den,
        "benign_tnr": tn / benign_den,
        "sqli_fnr": fn / sqli_den,
        "roc_auc": roc_auc,
        "average_precision": avg_precision,
        "confusion": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
    }


def load_generated_samples(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            rows.append(
                {
                    "sample_id": str(payload.get("sample_id", idx)),
                    "technique": str(payload.get("technique", "unknown")),
                    "text": str(payload.get("text", "")),
                }
            )
    return rows


def score_generated(
    model: Pipeline,
    threshold: float,
    sample_specs: list[tuple[str, Path]],
    out_dir: Path,
) -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, path in sample_specs:
        rows = load_generated_samples(path)
        scores = score_texts(model, [row["text"] for row in rows])
        csv_path = out_dir / f"{name}_classifier_oracle_results.csv"
        by_technique: dict[str, Counter[str]] = defaultdict(Counter)
        detected_count = 0
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["sample_id", "detected", "score", "technique"])
            writer.writeheader()
            for row, score in zip(rows, scores):
                detected = bool(score >= threshold)
                detected_count += int(detected)
                technique = row["technique"]
                by_technique[technique]["samples"] += 1
                by_technique[technique]["detected"] += int(detected)
                writer.writerow(
                    {
                        "sample_id": row["sample_id"],
                        "detected": "true" if detected else "false",
                        "score": f"{float(score):.6f}",
                        "technique": technique,
                    }
                )
        n = len(rows)
        summaries[name] = {
            "samples": str(path),
            "detector_results": str(csv_path),
            "n_samples": n,
            "detected_rate": detected_count / max(n, 1),
            "bypass_rate": 1.0 - detected_count / max(n, 1),
            "score_mean": float(np.mean(scores)) if n else 0.0,
            "score_p10": float(np.quantile(scores, 0.10)) if n else 0.0,
            "score_p50": float(np.quantile(scores, 0.50)) if n else 0.0,
            "score_p90": float(np.quantile(scores, 0.90)) if n else 0.0,
            "by_technique": {
                technique: {
                    "samples": c["samples"],
                    "detected_rate": c["detected"] / max(c["samples"], 1),
                    "bypass_rate": 1.0 - c["detected"] / max(c["samples"], 1),
                }
                for technique, c in sorted(by_technique.items())
            },
        }
    return summaries


def write_report(args: argparse.Namespace, result: dict[str, Any]) -> None:
    report_dir = ensure_under_phase(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / f"{args.report_name}.json"
    md_path = report_dir / f"{args.report_name}.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 08 - Held-Out Classifier Oracle Report",
        "",
        "Scope: local SQLi-vs-benign classifier trained only on the Phase 8 train split, thresholded on dev, and audited on held-out test. Raw payloads are intentionally omitted.",
        "",
        "## Training",
        "",
        f"- Train split: `{result['inputs']['train']}`",
        f"- Dev split: `{result['inputs']['dev']}`",
        f"- Test split: `{result['inputs']['test']}`",
        f"- Training rows used: `{result['training']['rows_used']:,}`",
        f"- Positives used: `{result['training']['positives_used']:,}`",
        f"- Benign used: `{result['training']['negatives_used']:,}`",
        f"- Threshold: `{result['threshold']['value']:.6f}`",
        f"- Target benign FPR on dev: `{result['threshold']['target_benign_fpr']:.4f}`",
        "",
        "## Oracle Quality",
        "",
        "| Split | N | Accuracy | Precision | SQLi Recall | Benign FPR | ROC-AUC | AP |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for split in ("dev", "test"):
        m = result["metrics"][split]
        roc = "n/a" if m["roc_auc"] is None else f"{m['roc_auc']:.4f}"
        ap = "n/a" if m["average_precision"] is None else f"{m['average_precision']:.4f}"
        lines.append(
            f"| {split} | {m['n']:,} | {m['accuracy']:.4f} | {m['precision']:.4f} | {m['recall_tpr']:.4f} | {m['benign_fpr']:.4f} | {roc} | {ap} |"
        )
    lines.extend(
        [
            "",
            "## Generated Samples",
            "",
            "| Source | Samples | Detected | Bypass | Score P50 | Score P90 | CSV |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for name, data in result["generated"].items():
        lines.append(
            f"| {name} | {data['n_samples']:,} | {data['detected_rate']:.4f} | {data['bypass_rate']:.4f} | {data['score_p50']:.4f} | {data['score_p90']:.4f} | `{data['detector_results']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is stronger than the deterministic signature proxy because the detector is fit on held-out Phase 8 data and audited on the untouched test split.",
            "- It is still an offline classifier oracle, not a live WAF.",
            "- Use the generated CSVs with `phase08_03_evaluator_contract.py --detector-results`.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"report={md_path}")
    print(f"json={json_path}")


def main() -> None:
    args = parse_args()
    train_path, dev_path, test_path = resolve_split_paths(args)
    sample_specs = parse_sample_specs(args.samples)
    out_dir = ensure_under_phase(args.out_dir)

    train_df = load_split(train_path, args.text_col, args.label_col)
    train_sample = sample_training_rows(train_df, args.label_col, args.max_positive, args.max_negative, args.seed)
    dev_df = load_split(dev_path, args.text_col, args.label_col, args.technique_col)
    test_df = load_split(test_path, args.text_col, args.label_col, args.technique_col)

    model = build_model(args.max_iter, args.seed)
    model.fit(train_sample[args.text_col].tolist(), train_sample[args.label_col].to_numpy())

    dev_y = dev_df[args.label_col].to_numpy()
    test_y = test_df[args.label_col].to_numpy()
    dev_scores = score_texts(model, dev_df[args.text_col].tolist())
    test_scores = score_texts(model, test_df[args.text_col].tolist())
    threshold = choose_threshold(dev_y, dev_scores, args.target_benign_fpr)

    result = {
        "inputs": {
            "train": str(train_path),
            "dev": str(dev_path),
            "test": str(test_path),
        },
        "training": {
            "rows_used": int(len(train_sample)),
            "positives_used": int((train_sample[args.label_col] == 1).sum()),
            "negatives_used": int((train_sample[args.label_col] == 0).sum()),
            "max_iter": args.max_iter,
            "seed": args.seed,
        },
        "threshold": {
            "value": threshold,
            "target_benign_fpr": args.target_benign_fpr,
            "mode": "dev_benign_quantile",
        },
        "metrics": {
            "dev": binary_metrics(dev_y, dev_scores, threshold),
            "test": binary_metrics(test_y, test_scores, threshold),
        },
        "generated": score_generated(model, threshold, sample_specs, out_dir) if sample_specs else {},
    }
    write_report(args, result)


if __name__ == "__main__":
    main()
