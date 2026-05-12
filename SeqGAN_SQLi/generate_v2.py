"""generate_v2.py — Generate samples từ V2 checkpoint (hỗ trợ conditional embedding)."""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import torch
import yaml

sys.path.insert(0, str(Path(__file__).parent))

from src.generator import GeneratorLSTM
from src.tokenizer import SQLTokenizer


def load_tokenizer(path: str) -> SQLTokenizer:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    vocab = data.get("token2id", data)
    return SQLTokenizer(vocab)


def generate(cfg: dict, ckpt_path: str, n_samples: int, out_csv: str,
             attack_type: int = None):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    data_dir = Path(cfg["data_dir"])

    tok = load_tokenizer(str(data_dir / "tokenizer_vocab.json"))
    num_attack_types = cfg.get("num_attack_types", 4)
    type_embed_dim = cfg.get("type_embed_dim", 32)

    model = GeneratorLSTM(
        vocab_size=tok.vocab_size,
        embed_dim=cfg["embed_dim"],
        hidden_dim=cfg["hidden_dim"],
        num_layers=cfg["num_layers"],
        dropout=0.0,  # no dropout at inference
        num_conditions=num_attack_types,
        cond_embed_dim=type_embed_dim,
    ).to(device)

    ckpt = torch.load(ckpt_path, map_location=device)
    # Handle both save formats (save_checkpoint and manual torch.save)
    state = ckpt.get("model_state", ckpt.get("model_state_dict", ckpt))
    model.load_state_dict(state)
    model.eval()
    print(f"Loaded: {ckpt_path} (device={device})")

    samples = []
    cond_labels = []
    batch_size = 64
    n_done = 0

    with torch.no_grad():
        while n_done < n_samples:
            current_batch = min(batch_size, n_samples - n_done)

            # Cycle through attack types if none specified
            if attack_type is not None:
                cond = torch.full((current_batch,), attack_type, dtype=torch.long, device=device)
            else:
                cond = torch.randint(0, num_attack_types, (current_batch,), device=device)

            token_ids, _ = model.sample(
                current_batch, cfg["max_seq_len"], device,
                sos_id=tok.sos_id, eos_id=tok.eos_id,
                cond=cond,
            )

            for i, row in enumerate(token_ids.cpu().tolist()):
                tokens = [
                    t for t in row
                    if t not in (tok.pad_id, tok.sos_id, tok.eos_id)
                ]
                if tok.eos_id in row:
                    eos_pos = row.index(tok.eos_id)
                    tokens = [
                        t for t in row[:eos_pos]
                        if t not in (tok.pad_id, tok.sos_id)
                    ]
                samples.append(tok.decode(tokens))
                cond_labels.append(cond[i].item())

            n_done += current_batch

    df = pd.DataFrame({"payload_delex": samples[:n_samples], "type_id": cond_labels[:n_samples]})

    # Load type mapping for readable labels
    type_map_path = data_dir / "type_mapping.json"
    if type_map_path.exists():
        with open(type_map_path) as f:
            mapping = json.load(f)
        id2type = mapping.get("id_to_type", {})
        df["sqli_type"] = df["type_id"].astype(str).map(id2type).fillna("unknown")

    df.to_csv(out_csv, index=False)
    print(f"Generated {len(df)} samples -> {out_csv}")
    print(f"Type distribution: {df['type_id'].value_counts().to_dict()}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="SeqGAN_SQLi/configs/seqgan_v2.yaml")
    parser.add_argument("--ckpt", required=True)
    parser.add_argument("--n_samples", type=int, default=1000)
    parser.add_argument("--out", required=True)
    parser.add_argument("--attack_type", type=int, default=None,
                        help="Fixed attack type id (0-3). If None, random sampling.")
    args = parser.parse_args()

    cfg_path = args.config
    if not Path(cfg_path).exists():
        cfg_path = str(Path(__file__).parent / args.config)
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    generate(cfg, args.ckpt, args.n_samples, args.out, args.attack_type)


if __name__ == "__main__":
    main()
