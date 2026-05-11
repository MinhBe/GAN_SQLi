"""Sprint 3: MLE pre-training with Scheduled Sampling and expert upweighting."""
import os
import sys
import argparse
import math
import yaml
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from tqdm import tqdm
try:
    from torch.utils.tensorboard import SummaryWriter
    HAS_TB = True
except ImportError:
    HAS_TB = False

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from src.tokenizer import SQLTokenizer
from src.generator import GeneratorLSTM
from src.losses import mle_loss
from src.scheduled_sampling import ScheduledSampler
from src.utils import set_seed, pad_sequences, save_checkpoint, get_device

DATA_DIR = os.path.join(ROOT, 'data')
CKPT_DIR = os.path.join(ROOT, 'checkpoints')


class SeqDataset(Dataset):
    def __init__(self, csv_path: str, tokenizer: SQLTokenizer,
                 max_len: int = 80, is_expert: bool = False):
        df = pd.read_csv(csv_path)
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.is_expert = is_expert
        self.seqs = [
            tokenizer.encode(row, add_sos=True, add_eos=True)[:max_len + 2]
            for row in df['payload_delex'].fillna('').tolist()
        ]

    def __len__(self):
        return len(self.seqs)

    def __getitem__(self, idx):
        return self.seqs[idx]


def collate_fn(batch, pad_id: int):
    return pad_sequences(batch, pad_id)


def compute_perplexity(model, loader, device, pad_id):
    model.eval()
    total_loss = 0.0
    total_tokens = 0
    with torch.no_grad():
        for batch in loader:
            batch = batch.to(device)
            inp, tgt = batch[:, :-1], batch[:, 1:]
            logits, _ = model(inp)
            B, T, V = logits.shape
            loss = F.cross_entropy(
                logits.reshape(B * T, V),
                tgt.reshape(B * T),
                ignore_index=pad_id,
                reduction='sum'
            )
            mask = (tgt != pad_id).sum().item()
            total_loss += loss.item()
            total_tokens += mask
    return math.exp(total_loss / max(total_tokens, 1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/seqgan_fast.yaml')
    parser.add_argument('--data_dir', default=None, help='Override data directory (e.g. data/error_based)')
    parser.add_argument('--ckpt_dir', default=None, help='Override checkpoint directory')
    parser.add_argument('--epochs', type=int, default=None)
    parser.add_argument('--steps', type=int, default=None, help='Max steps (for smoke test)')
    parser.add_argument('--resume', default=None)
    args = parser.parse_args()

    cfg_path = args.config
    if not os.path.isabs(cfg_path) and not os.path.exists(cfg_path):
        cfg_path = os.path.join(ROOT, args.config)
    if not os.path.exists(cfg_path):
        cfg_path = os.path.join(ROOT, 'configs', 'seqgan_fast.yaml')
    with open(cfg_path, encoding='utf-8') as f:
        cfg = yaml.safe_load(f)

    pc = cfg['pretrain']
    mc = cfg['model']
    seed = pc.get('seed', 42)
    set_seed(seed)
    device = get_device()

    data_dir = args.data_dir if args.data_dir else DATA_DIR
    if not os.path.isabs(data_dir) and not os.path.exists(data_dir):
        data_dir = os.path.join(ROOT, data_dir)
    ckpt_dir = args.ckpt_dir if args.ckpt_dir else CKPT_DIR
    if not os.path.isabs(ckpt_dir) and not os.path.exists(ckpt_dir):
        ckpt_dir = os.path.join(ROOT, ckpt_dir)
    os.makedirs(ckpt_dir, exist_ok=True)

    print(f"Device: {device}")
    print(f"Data dir: {data_dir}")

    tok = SQLTokenizer.load(os.path.join(data_dir, 'tokenizer_vocab.json'))
    print(f"Vocab size: {tok.vocab_size}")

    model = GeneratorLSTM(
        vocab_size=tok.vocab_size,
        embed_dim=mc['embed_dim'],
        hidden_dim=mc['hidden_dim'],
        num_layers=mc['num_layers'],
        dropout=mc['dropout'],
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=pc['lr'])
    sampler = ScheduledSampler(ramp_steps=pc['scheduled_sampling_steps'])

    # Datasets
    pad_fn = lambda b: collate_fn(b, tok.pad_id)
    train_ds = SeqDataset(os.path.join(data_dir, 'train.csv'), tok, mc['max_len'])
    expert_ds = SeqDataset(os.path.join(data_dir, 'expert_demos.csv'), tok, mc['max_len'], is_expert=True)
    val_ds = SeqDataset(os.path.join(data_dir, 'val.csv'), tok, mc['max_len'])

    print(f"Train: {len(train_ds)} | Expert: {len(expert_ds)} | Val: {len(val_ds)}")

    train_loader = DataLoader(train_ds, batch_size=pc['batch_size'], shuffle=True, collate_fn=pad_fn)
    val_loader = DataLoader(val_ds, batch_size=pc['batch_size'], shuffle=False, collate_fn=pad_fn)

    expert_iter = None
    if len(expert_ds) > 0:
        expert_loader = DataLoader(expert_ds, batch_size=max(1, pc['batch_size'] // 4),
                                   shuffle=True, collate_fn=pad_fn)
        expert_iter = iter(expert_loader)

    writer = SummaryWriter(os.path.join(ROOT, 'runs', 'pretrain')) if HAS_TB else None

    n_epochs = args.epochs if args.epochs is not None else pc['epochs']
    best_ppl = float('inf')
    patience_counter = 0
    global_step = 0

    os.makedirs(ckpt_dir, exist_ok=True)

    for epoch in range(1, n_epochs + 1):
        model.train()
        epoch_loss = 0.0
        n_batches = 0

        for batch in tqdm(train_loader, desc=f'Epoch {epoch}/{n_epochs}', leave=False):
            if args.steps and global_step >= args.steps:
                break
            batch = batch.to(device)
            inp, tgt = batch[:, :-1], batch[:, 1:]

            # Scheduled sampling: mix GT tokens with model predictions
            if sampler.epsilon > 0:
                with torch.no_grad():
                    ss_logits, _ = model(inp)
                    pred_tokens = ss_logits.argmax(dim=-1)
                mask = torch.bernoulli(
                    torch.full(inp.shape, sampler.epsilon, device=device)
                ).bool()
                inp_ss = torch.where(mask, pred_tokens, inp)
            else:
                inp_ss = inp

            logits, _ = model(inp_ss)

            # Expert upweighting via mixed batch
            expert_mask = torch.zeros(batch.size(0), dtype=torch.bool, device=device)
            if expert_iter is not None:
                try:
                    exp_batch = next(expert_iter).to(device)
                except StopIteration:
                    expert_iter = iter(expert_loader)
                    exp_batch = next(expert_iter).to(device)
                exp_inp, exp_tgt = exp_batch[:, :-1], exp_batch[:, 1:]
                exp_logits, _ = model(exp_inp)
                exp_loss = mle_loss(exp_logits, exp_tgt, tok.pad_id) * pc['expert_weight']
                main_loss = mle_loss(logits, tgt, tok.pad_id)
                loss = (main_loss + exp_loss) / 2
            else:
                loss = mle_loss(logits, tgt, tok.pad_id)

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), pc['grad_clip'])
            optimizer.step()
            sampler.step()

            epoch_loss += loss.item()
            n_batches += 1
            global_step += 1

            if writer and global_step % 100 == 0:
                writer.add_scalar('train/loss', loss.item(), global_step)
                writer.add_scalar('train/epsilon', sampler.epsilon, global_step)

        avg_loss = epoch_loss / max(n_batches, 1)
        val_ppl = compute_perplexity(model, val_loader, device, tok.pad_id)
        print(f"Epoch {epoch} | loss={avg_loss:.4f} | val_ppl={val_ppl:.2f} | eps={sampler.epsilon:.3f}")

        if writer:
            writer.add_scalar('val/perplexity', val_ppl, epoch)

        if val_ppl < best_ppl:
            best_ppl = val_ppl
            patience_counter = 0
            save_checkpoint(
                os.path.join(ckpt_dir, 'mle_best.pt'),
                model, optimizer, global_step,
                {'epoch': epoch, 'val_ppl': val_ppl}
            )
            print(f"  >> Best checkpoint saved (ppl={best_ppl:.2f})")
        else:
            patience_counter += 1
            if patience_counter >= pc['patience']:
                print(f"Early stop (patience={pc['patience']})")
                break

        if args.steps and global_step >= args.steps:
            print("Reached step limit (smoke test).")
            break

    save_checkpoint(
        os.path.join(ckpt_dir, 'mle_final.pt'),
        model, optimizer, global_step,
        {'best_val_ppl': best_ppl}
    )
    print(f"\nPretraining done. Best val_ppl={best_ppl:.2f}")
    if writer:
        writer.close()


if __name__ == '__main__':
    main()
