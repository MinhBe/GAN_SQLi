from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import math
import random
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


TIMELINE = Path(__file__).resolve().parents[1]
DATA = TIMELINE / "Data"
RAW = DATA / "raw"
MANIFESTS = DATA / "manifests"
PROCESSED = DATA / "processed"
REPRO = TIMELINE / "Reproduction"
CONFIGS = REPRO / "configs"
RESULTS = REPRO / "results"
LOGS = REPRO / "logs"
CHECKPOINTS = REPRO / "checkpoints"
REPORTS = TIMELINE / "Reports"

OFFICIAL_DIR = RAW / "dasari_2025"
OFFICIAL_SQLI = OFFICIAL_DIR / "sqli.csv"
OFFICIAL_MODIFIED = OFFICIAL_DIR / "Modified SQL Dataset.csv"
FALLBACK_SQLI = RAW / "sqliv5-dataset" / "sqli.csv"

RUN_ID = "dasari_cwgangp_smoke_v1"
KAGGLE_SQLI_URL = "https://www.kaggle.com/datasets/syedsaqlainhussain/sql-injection-dataset"
SQLIV5_URL = "https://github.com/nidnogg/sqliv5-dataset"
ARXIV_URL = "https://arxiv.org/abs/2502.04786"


def artifact_path(path: Path) -> str:
    try:
        return path.relative_to(TIMELINE.parent).as_posix()
    except ValueError:
        return path.as_posix()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def read_csv_flexible(path: Path) -> tuple[list[dict[str, str]], str]:
    encodings = ("utf-8-sig", "utf-16", "latin-1")
    last_error = ""
    for encoding in encodings:
        try:
            with path.open("r", encoding=encoding, errors="strict", newline="") as f:
                rows = list(csv.DictReader(f))
            if rows and any(rows[0].keys()):
                return rows, encoding
        except Exception as exc:  # pragma: no cover - diagnostic path
            last_error = f"{type(exc).__name__}: {exc}"
    raise RuntimeError(f"Could not read {path}: {last_error}")


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_query(value: str) -> str:
    value = value.replace("\x00", "")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def split_for_hash(value_hash: str) -> str:
    bucket = int(hashlib.sha256(("dasari-cwgangp-v1:" + value_hash).encode("ascii")).hexdigest()[:8], 16) % 100
    if bucket < 80:
        return "train"
    if bucket < 90:
        return "validation"
    return "test"


@dataclass(frozen=True)
class SourceChoice:
    path: Path
    source_id: str
    source_url: str
    status: str
    encoding: str
    official_kaggle_available: bool
    modified_dataset_available: bool


def choose_source() -> tuple[SourceChoice, list[dict[str, str]]]:
    candidates = [
        (OFFICIAL_SQLI, "kaggle_sqli_csv", KAGGLE_SQLI_URL, "official_kaggle"),
        (FALLBACK_SQLI, "sqliv5_sqli_csv_fallback", SQLIV5_URL, "fallback_mirror_not_exact"),
    ]
    for path, source_id, source_url, status in candidates:
        if not path.exists():
            continue
        rows, encoding = read_csv_flexible(path)
        return (
            SourceChoice(
                path=path,
                source_id=source_id,
                source_url=source_url,
                status=status,
                encoding=encoding,
                official_kaggle_available=OFFICIAL_SQLI.exists(),
                modified_dataset_available=OFFICIAL_MODIFIED.exists(),
            ),
            rows,
        )
    raise FileNotFoundError(
        "No Dasari source found. Put Kaggle sqli.csv under "
        f"{OFFICIAL_SQLI} or keep fallback mirror at {FALLBACK_SQLI}."
    )


def select_columns(rows: list[dict[str, str]]) -> tuple[str, str]:
    fieldnames = list(rows[0].keys())
    query_candidates = ("Query", "query", "Sentence", "sentence", "sql", "SQL")
    label_candidates = ("Label", "label", "class", "Class")
    query_col = next((name for name in query_candidates if name in fieldnames), None)
    label_col = next((name for name in label_candidates if name in fieldnames), None)
    if not query_col or not label_col:
        raise ValueError(f"Could not infer query/label columns from {fieldnames}")
    return query_col, label_col


def prepare_rows(source: SourceChoice, rows: list[dict[str, str]]) -> list[dict[str, str]]:
    query_col, label_col = select_columns(rows)
    prepared: list[dict[str, str]] = []
    seen: set[str] = set()
    skipped = 0
    for row in rows:
        query = normalize_query(row.get(query_col, ""))
        label = str(row.get(label_col, "")).strip()
        if label not in {"0", "1"} or not query:
            skipped += 1
            continue
        query_hash = sha256_text(query)
        dedupe_key = f"{query_hash}:{label}"
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        prepared.append(
            {
                "source_id": source.source_id,
                "source_status": source.status,
                "label": label,
                "query_base64": base64.b64encode(query.encode("utf-8", errors="replace")).decode("ascii"),
                "query_sha256": query_hash,
                "split": split_for_hash(query_hash),
                "length": str(len(query)),
            }
        )
    if skipped:
        print(f"Skipped {skipped} malformed rows")
    return prepared


def build_vocab(train_texts: list[str], vocab_limit: int) -> list[str]:
    counts = Counter(ch for text in train_texts for ch in text)
    chars = [ch for ch, _count in counts.most_common(max(0, vocab_limit - 3))]
    return ["<pad>", "<unk>", "<eos>"] + chars


def decode_b64(value: str) -> str:
    return base64.b64decode(value.encode("ascii")).decode("utf-8", errors="replace")


def encode_text(text: str, stoi: dict[str, int], max_len: int) -> list[int]:
    ids = [stoi.get(ch, stoi["<unk>"]) for ch in text[: max_len - 1]]
    ids.append(stoi["<eos>"])
    ids.extend([stoi["<pad>"]] * (max_len - len(ids)))
    return ids[:max_len]


def decode_ids(ids: list[int], vocab: list[str]) -> str:
    chars = []
    for idx in ids:
        token = vocab[idx]
        if token == "<eos>":
            break
        if token not in {"<pad>", "<unk>"}:
            chars.append(token)
    return normalize_query("".join(chars))


class Generator(nn.Module):
    def __init__(self, noise_dim: int, label_dim: int, hidden_dim: int, max_len: int, vocab_size: int):
        super().__init__()
        self.max_len = max_len
        self.vocab_size = vocab_size
        self.label_embedding = nn.Embedding(2, label_dim)
        self.net = nn.Sequential(
            nn.Linear(noise_dim + label_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim * 2),
            nn.ReLU(),
            nn.Linear(hidden_dim * 2, max_len * vocab_size),
        )

    def forward(self, noise: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        labels_emb = self.label_embedding(labels)
        logits = self.net(torch.cat([noise, labels_emb], dim=1))
        return logits.view(noise.shape[0], self.max_len, self.vocab_size)


class Critic(nn.Module):
    def __init__(self, label_dim: int, hidden_dim: int, max_len: int, vocab_size: int):
        super().__init__()
        self.label_embedding = nn.Embedding(2, label_dim)
        self.net = nn.Sequential(
            nn.Linear(max_len * vocab_size + label_dim, hidden_dim * 2),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, sequence_probs: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        flat = sequence_probs.reshape(sequence_probs.shape[0], -1)
        labels_emb = self.label_embedding(labels)
        return self.net(torch.cat([flat, labels_emb], dim=1)).view(-1)


def gradient_penalty(critic: Critic, real: torch.Tensor, fake: torch.Tensor, labels: torch.Tensor, device: torch.device) -> torch.Tensor:
    alpha = torch.rand(real.shape[0], 1, 1, device=device)
    interpolates = (alpha * real + (1 - alpha) * fake).requires_grad_(True)
    scores = critic(interpolates, labels)
    gradients = torch.autograd.grad(
        outputs=scores,
        inputs=interpolates,
        grad_outputs=torch.ones_like(scores),
        create_graph=True,
        retain_graph=True,
        only_inputs=True,
    )[0]
    gradients = gradients.reshape(gradients.shape[0], -1)
    return ((gradients.norm(2, dim=1) - 1) ** 2).mean()


def one_hot(ids: torch.Tensor, vocab_size: int) -> torch.Tensor:
    return torch.nn.functional.one_hot(ids, num_classes=vocab_size).float()


def train_smoke(
    prepared: list[dict[str, str]],
    *,
    max_len: int,
    vocab_limit: int,
    noise_dim: int,
    hidden_dim: int,
    batch_size: int,
    epochs: int,
    critic_steps: int,
    gp_lambda: float,
    synthetic_count: int,
    seed: int,
) -> dict[str, object]:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    train_rows = [row for row in prepared if row["split"] == "train"]
    train_texts = [decode_b64(row["query_base64"]) for row in train_rows]
    vocab = build_vocab(train_texts, vocab_limit)
    stoi = {token: idx for idx, token in enumerate(vocab)}

    encoded = torch.tensor([encode_text(text, stoi, max_len) for text in train_texts], dtype=torch.long)
    labels = torch.tensor([int(row["label"]) for row in train_rows], dtype=torch.long)
    loader = DataLoader(TensorDataset(encoded, labels), batch_size=batch_size, shuffle=True, drop_last=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    generator = Generator(noise_dim, 8, hidden_dim, max_len, len(vocab)).to(device)
    critic = Critic(8, hidden_dim, max_len, len(vocab)).to(device)
    opt_g = torch.optim.Adam(generator.parameters(), lr=1e-4, betas=(0.0, 0.9))
    opt_c = torch.optim.Adam(critic.parameters(), lr=1e-4, betas=(0.0, 0.9))

    history = []
    for epoch in range(1, epochs + 1):
        for real_ids, batch_labels in loader:
            real_ids = real_ids.to(device)
            batch_labels = batch_labels.to(device)
            real_probs = one_hot(real_ids, len(vocab)).to(device)
            last_c_loss = torch.tensor(0.0, device=device)
            for _ in range(critic_steps):
                noise = torch.randn(real_ids.shape[0], noise_dim, device=device)
                fake_logits = generator(noise, batch_labels)
                fake_probs = torch.softmax(fake_logits, dim=-1).detach()
                c_real = critic(real_probs, batch_labels).mean()
                c_fake = critic(fake_probs, batch_labels).mean()
                gp = gradient_penalty(critic, real_probs, fake_probs, batch_labels, device)
                c_loss = c_fake - c_real + gp_lambda * gp
                opt_c.zero_grad(set_to_none=True)
                c_loss.backward()
                opt_c.step()
                last_c_loss = c_loss.detach()

            noise = torch.randn(real_ids.shape[0], noise_dim, device=device)
            fake_probs = torch.softmax(generator(noise, batch_labels), dim=-1)
            g_loss = -critic(fake_probs, batch_labels).mean()
            opt_g.zero_grad(set_to_none=True)
            g_loss.backward()
            opt_g.step()
        history.append({"epoch": epoch, "critic_loss": float(last_c_loss.cpu()), "generator_loss": float(g_loss.detach().cpu())})

    synthetic_rows = generate_samples(generator, vocab, max_len, noise_dim, synthetic_count, seed, device)
    checkpoint = {
        "run_id": RUN_ID,
        "generator": generator.state_dict(),
        "critic": critic.state_dict(),
        "vocab": vocab,
        "config": {
            "max_len": max_len,
            "vocab_limit": vocab_limit,
            "noise_dim": noise_dim,
            "hidden_dim": hidden_dim,
            "batch_size": batch_size,
            "epochs": epochs,
            "critic_steps": critic_steps,
            "gp_lambda": gp_lambda,
            "synthetic_count": synthetic_count,
            "seed": seed,
        },
        "history": history,
    }
    return {"checkpoint": checkpoint, "history": history, "vocab": vocab, "synthetic_rows": synthetic_rows, "device": str(device)}


def generate_samples(
    generator: Generator,
    vocab: list[str],
    max_len: int,
    noise_dim: int,
    synthetic_count: int,
    seed: int,
    device: torch.device,
) -> list[dict[str, str]]:
    generator.eval()
    synthetic_rows: list[dict[str, str]] = []
    with torch.no_grad():
        labels = torch.tensor([idx % 2 for idx in range(synthetic_count)], dtype=torch.long, device=device)
        noise_gen = torch.Generator(device=device).manual_seed(seed + 17)
        noise = torch.randn(synthetic_count, noise_dim, generator=noise_gen, device=device)
        logits = generator(noise, labels)
        ids = torch.argmax(logits, dim=-1).cpu().numpy().tolist()
    for idx, (sample_ids, label) in enumerate(zip(ids, labels.cpu().numpy().tolist()), start=1):
        text = decode_ids(sample_ids[:max_len], vocab)
        sample_hash = sha256_text(text)
        synthetic_rows.append(
            {
                "sample_id": f"dasari-synth-{idx:04d}",
                "run_id": RUN_ID,
                "label": str(label),
                "synthetic_query_base64": base64.b64encode(text.encode("utf-8", errors="replace")).decode("ascii"),
                "synthetic_sha256": sample_hash,
                "length": str(len(text)),
            }
        )
    return synthetic_rows


def classifier_metrics(y_true: list[int], y_pred: np.ndarray) -> dict[str, str]:
    return {
        "accuracy": f"{accuracy_score(y_true, y_pred):.4f}",
        "precision": f"{precision_score(y_true, y_pred, zero_division=0):.4f}",
        "recall": f"{recall_score(y_true, y_pred, zero_division=0):.4f}",
        "f1": f"{f1_score(y_true, y_pred, zero_division=0):.4f}",
    }


def detection_uplift(prepared: list[dict[str, str]], synthetic_rows: list[dict[str, str]], seed: int) -> list[dict[str, str]]:
    train_rows = [row for row in prepared if row["split"] == "train"]
    test_rows = [row for row in prepared if row["split"] == "test"]
    x_train = [decode_b64(row["query_base64"]) for row in train_rows]
    y_train = [int(row["label"]) for row in train_rows]
    x_test = [decode_b64(row["query_base64"]) for row in test_rows]
    y_test = [int(row["label"]) for row in test_rows]

    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 5), min_df=1)
    x_train_vec = vectorizer.fit_transform(x_train)
    x_test_vec = vectorizer.transform(x_test)
    baseline = LogisticRegression(max_iter=500, random_state=seed)
    baseline.fit(x_train_vec, y_train)
    baseline_metrics = classifier_metrics(y_test, baseline.predict(x_test_vec))

    synthetic_texts = [decode_b64(row["synthetic_query_base64"]) for row in synthetic_rows if row["length"] != "0"]
    synthetic_labels = [int(row["label"]) for row in synthetic_rows if row["length"] != "0"]
    augmented_vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 5), min_df=1)
    x_aug = x_train + synthetic_texts
    y_aug = y_train + synthetic_labels
    x_aug_vec = augmented_vectorizer.fit_transform(x_aug)
    x_test_aug_vec = augmented_vectorizer.transform(x_test)
    augmented = LogisticRegression(max_iter=500, random_state=seed)
    augmented.fit(x_aug_vec, y_aug)
    augmented_metrics = classifier_metrics(y_test, augmented.predict(x_test_aug_vec))

    return [
        {"run_id": RUN_ID, "model": "char_tfidf_logreg", "training_set": "real_train_only", **baseline_metrics},
        {"run_id": RUN_ID, "model": "char_tfidf_logreg", "training_set": "real_train_plus_cwgangp_synthetic_smoke", **augmented_metrics},
    ]


def summarize_lengths(prepared: list[dict[str, str]]) -> dict[str, str]:
    lengths = [int(row["length"]) for row in prepared]
    return {
        "min_length": str(min(lengths) if lengths else 0),
        "max_length": str(max(lengths) if lengths else 0),
        "avg_length": f"{(sum(lengths) / len(lengths)) if lengths else 0:.2f}",
    }


def write_artifacts(
    source: SourceChoice,
    prepared: list[dict[str, str]],
    train_result: dict[str, object],
    uplift_rows: list[dict[str, str]],
    args: argparse.Namespace,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    split_counts = Counter(row["split"] for row in prepared)
    label_counts = Counter(row["label"] for row in prepared)
    unique_hashes = len({row["query_sha256"] for row in prepared})
    length_stats = summarize_lengths(prepared)
    synthetic_rows: list[dict[str, str]] = train_result["synthetic_rows"]  # type: ignore[assignment]
    synthetic_unique = len({row["synthetic_sha256"] for row in synthetic_rows})
    nonempty_synthetic = sum(1 for row in synthetic_rows if row["length"] != "0")
    history: list[dict[str, float]] = train_result["history"]  # type: ignore[assignment]
    last_history = history[-1] if history else {"critic_loss": math.nan, "generator_loss": math.nan}

    CONFIGS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    CHECKPOINTS.mkdir(parents=True, exist_ok=True)
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    config_text = f"""run_id: {RUN_ID}
paper: Dasari 2025 - Enhancing SQL Injection Detection and Prevention Using Generative Models
reproduction_level: partial_smoke
source_status: {source.status}
source_url: {source.source_url}
local_source: {artifact_path(source.path)}
official_kaggle_sqli_available: {str(source.official_kaggle_available).lower()}
modified_sql_dataset_available: {str(source.modified_dataset_available).lower()}
model: CWGAN-GP character-level smoke implementation
max_len: {args.max_len}
vocab_limit: {args.vocab_limit}
noise_dim: {args.noise_dim}
hidden_dim: {args.hidden_dim}
batch_size: {args.batch_size}
epochs: {args.epochs}
critic_steps: {args.critic_steps}
gp_lambda: {args.gp_lambda}
synthetic_count: {args.synthetic_count}
seed: {args.seed}
guardrails:
  - local_lab_only
  - no_raw_payloads_in_reports_or_logs
  - do_not_claim_exact_until_official_kaggle_snapshot_is_recorded
"""
    (CONFIGS / "dasari_cwgangp_config.yaml").write_text(config_text, encoding="utf-8")

    processed_fields = ["source_id", "source_status", "label", "query_base64", "query_sha256", "split", "length"]
    write_csv(PROCESSED / "dasari_cwgangp_prepared.csv", prepared, processed_fields)

    synthetic_fields = ["sample_id", "run_id", "label", "synthetic_query_base64", "synthetic_sha256", "length"]
    write_csv(RESULTS / "dasari_cwgangp_synthetic_samples.csv", synthetic_rows, synthetic_fields)

    metrics = [
        {
            "run_id": RUN_ID,
            "timestamp_utc": now,
            "reproduction_level": "partial_smoke",
            "source_status": source.status,
            "source_id": source.source_id,
            "raw_source_path": artifact_path(source.path),
            "source_encoding": source.encoding,
            "rows_prepared": str(len(prepared)),
            "unique_hashes": str(unique_hashes),
            "label_0_rows": str(label_counts.get("0", 0)),
            "label_1_rows": str(label_counts.get("1", 0)),
            "train_rows": str(split_counts.get("train", 0)),
            "validation_rows": str(split_counts.get("validation", 0)),
            "test_rows": str(split_counts.get("test", 0)),
            "min_length": length_stats["min_length"],
            "max_length": length_stats["max_length"],
            "avg_length": length_stats["avg_length"],
            "device": str(train_result["device"]),
            "epochs": str(args.epochs),
            "critic_steps": str(args.critic_steps),
            "vocab_size": str(len(train_result["vocab"])),  # type: ignore[arg-type]
            "synthetic_count": str(len(synthetic_rows)),
            "synthetic_nonempty": str(nonempty_synthetic),
            "synthetic_unique_hashes": str(synthetic_unique),
            "synthetic_duplicate_rows": str(len(synthetic_rows) - synthetic_unique),
            "last_critic_loss": f"{last_history['critic_loss']:.6f}",
            "last_generator_loss": f"{last_history['generator_loss']:.6f}",
        }
    ]
    metric_fields = list(metrics[0].keys())
    write_csv(RESULTS / "dasari_cwgangp_metrics.csv", metrics, metric_fields)

    uplift_fields = ["run_id", "model", "training_set", "accuracy", "precision", "recall", "f1"]
    write_csv(RESULTS / "dasari_cwgangp_detection_uplift.csv", uplift_rows, uplift_fields)

    torch.save(train_result["checkpoint"], CHECKPOINTS / "dasari_cwgangp_smoke.pt")

    data_status = [
        {
            "source": "Dasari 2025 Kaggle sqli.csv",
            "paper_or_origin": "Dasari 2025",
            "role": "CWGAN-GP augmentation reproduction source",
            "source_url": KAGGLE_SQLI_URL,
            "local_file": artifact_path(OFFICIAL_SQLI),
            "status": "present" if source.official_kaggle_available else "missing",
            "notes": "Use for exact/closer reproduction when available.",
        },
        {
            "source": "Dasari 2025 Modified SQL Dataset.csv",
            "paper_or_origin": "Dasari 2025",
            "role": "Secondary CWGAN-GP augmentation reproduction source",
            "source_url": "not_confirmed_in_local_metadata",
            "local_file": artifact_path(OFFICIAL_MODIFIED),
            "status": "present" if source.modified_dataset_available else "missing",
            "notes": "Guiding expects this file; official source still needs confirmation.",
        },
        {
            "source": "SQLiV3 mirror sqli.csv fallback",
            "paper_or_origin": "SQLiV3/Kaggle mirror",
            "role": "Fallback only for partial smoke reproduction",
            "source_url": SQLIV5_URL,
            "local_file": artifact_path(FALLBACK_SQLI),
            "status": "used" if source.path == FALLBACK_SQLI else "available",
            "notes": "Do not claim exact Dasari reproduction from this fallback.",
        },
    ]
    write_csv(
        MANIFESTS / "dasari_cwgangp_data_status.csv",
        data_status,
        ["source", "paper_or_origin", "role", "source_url", "local_file", "status", "notes"],
    )

    source_card = f"""# Dasari CWGAN-GP Data Status

- Run id: `{RUN_ID}`
- Timestamp UTC: `{now}`
- Paper: Dasari 2025, `Enhancing SQL Injection Detection and Prevention Using Generative Models`
- Paper URL: `{ARXIV_URL}`
- Selected source: `{source.source_id}`
- Selected source URL: `{source.source_url}`
- Selected local file: `{artifact_path(source.path)}`
- Selected source status: `{source.status}`
- Encoding detected: `{source.encoding}`
- Official Kaggle `sqli.csv` present locally: `{source.official_kaggle_available}`
- `Modified SQL Dataset.csv` present locally: `{source.modified_dataset_available}`

## Reproduction Claim

This run is `partial_smoke`, not exact reproduction. Exact/closer reproduction requires recording the official Kaggle snapshot and the secondary modified dataset if it is used.

## Prepared Data

- Rows prepared: {len(prepared)}
- Unique query hashes: {unique_hashes}
- Label 0 rows: {label_counts.get("0", 0)}
- Label 1 rows: {label_counts.get("1", 0)}
- Train rows: {split_counts.get("train", 0)}
- Validation rows: {split_counts.get("validation", 0)}
- Test rows: {split_counts.get("test", 0)}

No raw payload strings are printed in this source card.
"""
    (MANIFESTS / "dasari_cwgangp_source_status.md").write_text(source_card, encoding="utf-8")

    log_text = f"""[{now}] {RUN_ID}
source_id={source.source_id}
source_status={source.status}
rows_prepared={len(prepared)}
train_rows={split_counts.get("train", 0)}
validation_rows={split_counts.get("validation", 0)}
test_rows={split_counts.get("test", 0)}
device={train_result["device"]}
epochs={args.epochs}
critic_steps={args.critic_steps}
synthetic_count={len(synthetic_rows)}
synthetic_unique_hashes={synthetic_unique}
last_critic_loss={last_history["critic_loss"]:.6f}
last_generator_loss={last_history["generator_loss"]:.6f}
raw_payloads_printed=false
"""
    (LOGS / "dasari_cwgangp_run.log").write_text(log_text, encoding="utf-8")

    uplift_summary = "\n".join(
        f"| {row['training_set']} | {row['accuracy']} | {row['precision']} | {row['recall']} | {row['f1']} |"
        for row in uplift_rows
    )
    report = f"""# Dasari 2025 CWGAN-GP Reproduction Smoke

## Status

- Reproduction level: `partial_smoke`
- Selected source: `{source.source_id}`
- Source status: `{source.status}`
- Official Kaggle `sqli.csv` present locally: `{source.official_kaggle_available}`
- `Modified SQL Dataset.csv` present locally: `{source.modified_dataset_available}`
- WAF-A-MoLE remains frozen at `threshold_reached=0`; this run does not reopen it.

## Artifacts

- Config: `Timeline/Reproduction/configs/dasari_cwgangp_config.yaml`
- Prepared data: `Timeline/Data/processed/dasari_cwgangp_prepared.csv`
- Checkpoint: `Timeline/Reproduction/checkpoints/dasari_cwgangp_smoke.pt`
- Metrics: `Timeline/Reproduction/results/dasari_cwgangp_metrics.csv`
- Detection uplift smoke: `Timeline/Reproduction/results/dasari_cwgangp_detection_uplift.csv`
- Synthetic samples: `Timeline/Reproduction/results/dasari_cwgangp_synthetic_samples.csv`
- Data status: `Timeline/Data/manifests/dasari_cwgangp_data_status.csv`

## Data Summary

| Metric | Value |
| --- | ---: |
| Prepared rows | {len(prepared)} |
| Unique query hashes | {unique_hashes} |
| Label 0 rows | {label_counts.get("0", 0)} |
| Label 1 rows | {label_counts.get("1", 0)} |
| Train rows | {split_counts.get("train", 0)} |
| Validation rows | {split_counts.get("validation", 0)} |
| Test rows | {split_counts.get("test", 0)} |
| Synthetic samples | {len(synthetic_rows)} |
| Non-empty synthetic samples | {nonempty_synthetic} |
| Unique synthetic hashes | {synthetic_unique} |

## Detection Uplift Smoke

| Training set | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
{uplift_summary}

## Interpretation

This is a smoke implementation to start the Dasari reproduction path and verify the required artifact contract: config, checkpoint, log, metrics, and report. It must not be cited as an exact paper reproduction until the official Kaggle snapshot and modified dataset status are resolved.

No raw payload strings are printed in this report.
"""
    (REPORTS / "04a_dasari_cwgangp_reproduction.md").write_text(report, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Dasari 2025 CWGAN-GP partial smoke reproduction.")
    parser.add_argument("--max-len", type=int, default=96)
    parser.add_argument("--vocab-limit", type=int, default=96)
    parser.add_argument("--noise-dim", type=int, default=48)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--critic-steps", type=int, default=1)
    parser.add_argument("--gp-lambda", type=float, default=10.0)
    parser.add_argument("--synthetic-count", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20260529)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source, raw_rows = choose_source()
    prepared = prepare_rows(source, raw_rows)
    train_result = train_smoke(
        prepared,
        max_len=args.max_len,
        vocab_limit=args.vocab_limit,
        noise_dim=args.noise_dim,
        hidden_dim=args.hidden_dim,
        batch_size=args.batch_size,
        epochs=args.epochs,
        critic_steps=args.critic_steps,
        gp_lambda=args.gp_lambda,
        synthetic_count=args.synthetic_count,
        seed=args.seed,
    )
    uplift_rows = detection_uplift(prepared, train_result["synthetic_rows"], args.seed)  # type: ignore[arg-type]
    write_artifacts(source, prepared, train_result, uplift_rows, args)
    print(f"{RUN_ID} completed with source_status={source.status}; raw payloads printed=false")


if __name__ == "__main__":
    main()
