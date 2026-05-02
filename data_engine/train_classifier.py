"""
Train ML Classifier — Train model TF-IDF + RandomForest
trên data đã được rule-based classifier label.
Dùng làm fallback cho các payload rule không match.
"""
import argparse
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent))

from config import OUTPUT_DIR, ML_TEST_SIZE, ML_RANDOM_STATE


def train_and_save(model_path: str = None):
    """
    Chạy pipeline → lấy data đã classify → train ML model → save.
    """
    from loaders import load_all_sources
    from normalizer import normalize_batch
    from classifier import classify_batch, MLClassifier

    print("=" * 60)
    print("  TRAIN ML CLASSIFIER")
    print("=" * 60)

    print("\n[*] Step 1: Loading data...")
    samples = load_all_sources()

    print("\n[*] Step 2: Normalizing...")
    samples = normalize_batch(samples)

    print("\n[*] Step 3: Rule-based classification...")
    samples = classify_batch(samples)

    ml_samples = [s for s in samples if s.get("sqli_type") != "unknown"]
    print(f"\n[*] {len(ml_samples)} samples có label để train ML")

    if len(ml_samples) < 50:
        print("[ERROR] Không đủ data để train ML. Cần ít nhất 50 samples.")
        return

    if model_path is None:
        model_path = os.path.join(OUTPUT_DIR, "ml_classifier.pkl")

    print(f"\n[*] Step 4: Training ML model...")
    clf = MLClassifier()
    success = clf.train(ml_samples, model_path=model_path)

    if success:
        print(f"\n[OK] ML classifier trained và saved to {model_path}")
        print("     Dùng model này trong classify_batch() bằng cách:")
        print("     clf = MLClassifier()")
        print("     clf.predict(unclassified_samples)")
    else:
        print("[FAIL] Không thể train ML classifier.")


def main():
    parser = argparse.ArgumentParser(description="Train ML SQLi Classifier")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to save trained model (default: output/ml_classifier.pkl)",
    )
    args = parser.parse_args()

    train_and_save(model_path=args.output)


if __name__ == "__main__":
    main()
