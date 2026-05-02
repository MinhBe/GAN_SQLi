"""
Final pipeline run — filter, classify, dedup, split, train ML.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from loaders import load_all_sources
from normalizer import normalize_batch
from classifier import classify_batch, MLClassifier
from deduplicator import exact_dedup, normalized_dedup
from splitter import run_splitter
from config import OUTPUT_DIR

print("=" * 60)
print("  FINAL PIPELINE RUN")
print("=" * 60)

print("\n[*] Loading...")
samples = load_all_sources()

print("\n[*] Normalizing...")
samples = normalize_batch(samples)

print("\n[*] Filtering out non-payload entries (exploitdb descriptions)...")
before = len(samples)
import re
sqli_keyword_pattern = re.compile(
    r"(?i)(?:select|union|insert|update|delete|drop|alter|create|"
    r"where|or\s+\d|and\s+\d|sleep|benchmark|waitfor|pg_sleep|"
    r"exec|xp_|cast|convert|char\(|chr\(|concat|"
    r"'\s*(?:or|and|;|--|#)|\"?\s*(?:or|and)|"
    r"order\s+by|group\s+by|having|"
    r"information_schema|sys\.(tables|columns|objects)|"
    r"dual|syscolumns|sysobjects)",
)
samples = [s for s in samples if s["source"] != "exploitdb" or sqli_keyword_pattern.search(s["payload"])]
print(f"  Filtered: {before} -> {len(samples)} (removed {before - len(samples)} non-payload entries)")

print("\n[*] Rule-based classification...")
samples = classify_batch(samples)

print("\n[*] Deduplication...")
samples = exact_dedup(samples)
samples = normalized_dedup(samples)

print("\n[*] Saving unified pool and splitting...")
stats = run_splitter(samples)

print("\n[*] Training ML classifier on rule-labeled data...")
labeled = [s for s in samples if s.get("sqli_type") != "unknown"]
clf = MLClassifier()
clf.train(labeled, model_path=str(OUTPUT_DIR / "ml_classifier.pkl"))

print("\n" + "=" * 60)
print("  FINAL RESULTS")
print("=" * 60)
print(f"  Total samples (after filter + dedup): {len(samples)}")
print(f"  Classified (rule): {len([s for s in samples if s['sqli_type'] != 'unknown'])}")
print(f"  Unknown (needs ML or manual review): {len([s for s in samples if s['sqli_type'] == 'unknown'])}")
print(f"  Output dir: {OUTPUT_DIR}")
print("=" * 60)
