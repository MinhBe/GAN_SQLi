"""
Deduplicator — Loại bỏ duplicate và near-duplicate payloads.
3 cấp độ: exact, near-duplicate (normalized), semantic (TF-IDF similarity).
"""
import hashlib
import sys
from typing import List, Dict, Any, Set
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
from config import DEDUP_SIMILARITY_THRESHOLD


def exact_dedup(samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Loại exact duplicate — payload string giống hệt nhau."""
    seen: Set[str] = set()
    deduped = []

    for sample in samples:
        h = hashlib.md5(sample["payload"].encode("utf-8", errors="replace")).hexdigest()
        if h not in seen:
            seen.add(h)
            deduped.append(sample)

    removed = len(samples) - len(deduped)
    print(f"[+] Exact dedup: {len(samples)} -> {len(deduped)} (loại {removed})")
    return deduped


def normalized_dedup(samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Loại near-duplicate sau khi normalize (lowercase, strip whitespace)."""
    seen: Set[str] = set()
    deduped = []

    for sample in samples:
        normalized = sample["payload"].lower().strip()
        normalized = "".join(normalized.split())
        h = hashlib.md5(normalized.encode("utf-8", errors="replace")).hexdigest()
        if h not in seen:
            seen.add(h)
            deduped.append(sample)

    removed = len(samples) - len(deduped)
    print(f"[+] Normalized dedup: {len(samples)} -> {len(deduped)} (loại {removed})")
    return deduped


def semantic_dedup(samples: List[Dict[str, Any]], threshold: float = DEDUP_SIMILARITY_THRESHOLD) -> List[Dict[str, Any]]:
    """Loại semantic duplicate dùng TF-IDF + cosine similarity."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        print("  [WARN] sklearn not installed. Bỏ qua semantic dedup.")
        return samples

    if len(samples) < 2:
        return samples

    payloads = [s["payload"] for s in samples]

    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 4),
        max_features=5000,
    )

    tfidf_matrix = vectorizer.fit_transform(payloads)

    batch_size = 500
    to_remove: Set[int] = set()

    for start in range(0, len(samples), batch_size):
        end = min(start + batch_size, len(samples))
        sim_chunk = cosine_similarity(tfidf_matrix[start:end], tfidf_matrix)

        for i in range(end - start):
            row_idx = start + i
            if row_idx in to_remove:
                continue
            for j in range(row_idx + 1, len(samples)):
                if j in to_remove:
                    continue
                sim_score = sim_chunk[i, j]
                if sim_score > threshold:
                    to_remove.add(j)

    deduped = [s for idx, s in enumerate(samples) if idx not in to_remove]
    removed = len(samples) - len(deduped)
    print(f"[+] Semantic dedup (threshold={threshold}): {len(samples)} -> {len(deduped)} (loại {removed})")
    return deduped


def full_dedup_pipeline(samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Chạy toàn bộ dedup pipeline."""
    print(f"\n[*] Bắt đầu dedup: {len(samples)} samples")
    result = exact_dedup(samples)
    result = normalized_dedup(result)
    result = semantic_dedup(result)
    print(f"[+] Tổng dedup result: {len(result)} samples\n")
    return result
