"""Inference: generate SQLi payloads from a checkpoint."""
import os
import sys
import argparse
import yaml
import torch
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from src.tokenizer import SQLTokenizer
from src.generator import GeneratorLSTM
from src.utils import load_checkpoint, get_device

DATA_DIR = os.path.join(ROOT, 'data')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ckpt', required=True)
    parser.add_argument('--config', default='configs/seqgan_fast.yaml')
    parser.add_argument('--data_dir', default=None, help='Data directory with tokenizer_vocab.json')
    parser.add_argument('--n_samples', type=int, default=1000)
    parser.add_argument('--batch_size', type=int, default=64)
    parser.add_argument('--temperature', type=float, default=1.0)
    parser.add_argument('--out', default='eval_samples.csv')
    args = parser.parse_args()

    cfg_path = args.config if os.path.exists(args.config) else os.path.join(ROOT, args.config)
    with open(cfg_path, encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    mc = cfg['model']

    data_dir = args.data_dir if args.data_dir else DATA_DIR
    if not os.path.isabs(data_dir) and not os.path.exists(data_dir):
        data_dir = os.path.join(ROOT, data_dir)

    device = get_device()
    tok = SQLTokenizer.load(os.path.join(data_dir, 'tokenizer_vocab.json'))

    model = GeneratorLSTM(
        tok.vocab_size, mc['embed_dim'], mc['hidden_dim'], mc['num_layers'], mc['dropout']
    ).to(device)

    if os.path.isabs(args.ckpt):
        ckpt_path = args.ckpt
    elif os.path.exists(args.ckpt):
        ckpt_path = args.ckpt
    else:
        ckpt_path = os.path.join(ROOT, args.ckpt)
    load_checkpoint(ckpt_path, model)
    model.eval()

    payloads = []
    n_generated = 0
    with torch.no_grad():
        while n_generated < args.n_samples:
            bs = min(args.batch_size, args.n_samples - n_generated)
            seqs, _ = model.sample(bs, mc['max_len'], device,
                                   tok.sos_id, tok.eos_id, args.temperature)
            for seq in seqs:
                payloads.append(tok.decode(seq.tolist()))
            n_generated += bs

    out_path = args.out if os.path.isabs(args.out) else os.path.join(ROOT, '..', args.out)
    df = pd.DataFrame({'payload': payloads})
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} samples -> {out_path}")


if __name__ == '__main__':
    main()
