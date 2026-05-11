"""Baseline: SeqGAN without advantage (Q instead of Q-b).
Trains like train_adversarial.py but skips baseline subtraction.
"""
import os
import sys
import argparse
import yaml
import torch
import pandas as pd
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from src.tokenizer import SQLTokenizer
from src.generator import GeneratorLSTM
from src.discriminator import DiscriminatorCNN
from src.reward import RewardOracle
from src.losses import wgan_gp_loss
from src.utils import set_seed, pad_sequences, save_checkpoint, load_checkpoint, get_device

DATA_DIR = os.path.join(ROOT, 'data')
CKPT_DIR = os.path.join(ROOT, 'checkpoints')


class SeqDataset(Dataset):
    def __init__(self, csv_path, tokenizer, max_len=80):
        df = pd.read_csv(csv_path)
        self.seqs = [
            tokenizer.encode(row, add_sos=True, add_eos=True)[:max_len + 2]
            for row in df['payload_delex'].fillna('').tolist()
        ]

    def __len__(self): return len(self.seqs)
    def __getitem__(self, idx): return self.seqs[idx]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/seqgan_default.yaml')
    parser.add_argument('--mle_ckpt', default='checkpoints/mle_best.pt')
    parser.add_argument('--steps', type=int, default=None)
    parser.add_argument('--out_ckpt', default='checkpoints/vanilla_final.pt')
    args = parser.parse_args()

    with open(os.path.join(ROOT, args.config)) as f:
        cfg = yaml.safe_load(f)

    ac = cfg['adversarial']
    mc = cfg['model']
    dc = cfg['discriminator']
    rc = cfg['reward']
    set_seed(ac.get('seed', 42))
    device = get_device()

    tok = SQLTokenizer.load(os.path.join(DATA_DIR, 'tokenizer_vocab.json'))
    generator = GeneratorLSTM(tok.vocab_size, mc['embed_dim'], mc['hidden_dim'],
                              mc['num_layers'], mc['dropout']).to(device)
    discriminator = DiscriminatorCNN(tok.vocab_size, dc['embed_dim'],
                                     dc['kernel_sizes'], dc['num_filters']).to(device)

    mle_path = os.path.join(ROOT, args.mle_ckpt)
    if os.path.exists(mle_path):
        load_checkpoint(mle_path, generator)

    g_optim = torch.optim.Adam(generator.parameters(), lr=ac['lr_g'], betas=(0.5, 0.999))
    d_optim = torch.optim.Adam(discriminator.parameters(), lr=ac['lr_d'], betas=(0.5, 0.999))

    pad_fn = lambda b: pad_sequences(b, tok.pad_id)
    real_ds = SeqDataset(os.path.join(DATA_DIR, 'train.csv'), tok, mc['max_len'])
    real_loader = DataLoader(real_ds, batch_size=ac['batch_size'], shuffle=True, collate_fn=pad_fn)
    real_iter = iter(real_loader)

    oracle = RewardOracle(rc['lambda_d'], rc['lambda_bypass'], rc['lambda_syntax'],
                          rc['length_penalty_coef'], mc['max_len'])

    total_steps = args.steps if args.steps is not None else ac['total_steps']
    bs, max_len = ac['batch_size'], mc['max_len']
    os.makedirs(CKPT_DIR, exist_ok=True)

    for step in tqdm(range(1, total_steps + 1), desc='SeqGAN Vanilla'):
        for _ in range(ac['d_steps_per_g']):
            try:
                real_batch = next(real_iter).to(device)
            except StopIteration:
                real_iter = iter(real_loader)
                real_batch = next(real_iter).to(device)
            with torch.no_grad():
                fake_seqs, _ = generator.sample(bs, max_len, device, tok.sos_id, tok.eos_id)
            T_min = min(real_batch.size(1), fake_seqs.size(1))
            gp = discriminator.gradient_penalty(real_batch[:, :T_min], fake_seqs[:, :T_min], ac['gp_lambda'])
            d_loss = wgan_gp_loss(discriminator(real_batch[:, :T_min]),
                                  discriminator(fake_seqs[:, :T_min]), gp)
            d_optim.zero_grad(); d_loss.backward(); d_optim.step()

        fake_seqs, log_probs = generator.sample(bs, max_len, device, tok.sos_id, tok.eos_id)
        rewards = torch.tensor([
            oracle.compute(tok.decode(seq.tolist()), token_count=len(seq.tolist()))['total']
            for seq in fake_seqs
        ], device=device)

        # Vanilla: use Q directly, no advantage (no baseline subtraction)
        g_loss = -(log_probs.sum(dim=1) * rewards.detach()).mean()
        g_optim.zero_grad(); g_loss.backward()
        torch.nn.utils.clip_grad_norm_(generator.parameters(), ac['grad_clip'])
        g_optim.step()

        if step % ac['log_every'] == 0:
            print(f"Vanilla step {step} | g_loss={g_loss.item():.4f} | reward={rewards.mean().item():.4f}")

    save_checkpoint(os.path.join(ROOT, args.out_ckpt), generator, g_optim, total_steps, {})
    print(f"Vanilla SeqGAN saved -> {args.out_ckpt}")


if __name__ == '__main__':
    main()
