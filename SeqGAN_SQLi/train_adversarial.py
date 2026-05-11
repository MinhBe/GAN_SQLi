"""Sprint 4: Adversarial RL training (REINFORCE + WGAN-GP)."""
import os
import sys
import argparse
import yaml
import torch
import torch.nn.functional as F
import pandas as pd
from torch.utils.data import DataLoader, Dataset
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
from src.discriminator import DiscriminatorCNN
from src.baseline import ValueBaseline
from src.rollout import MCRollout
from src.reward import RewardOracle
from src.losses import reinforce_loss, wgan_gp_loss
from src.utils import set_seed, pad_sequences, save_checkpoint, load_checkpoint, get_device

DATA_DIR = os.path.join(ROOT, 'data')
CKPT_DIR = os.path.join(ROOT, 'checkpoints')


class SeqDataset(Dataset):
    def __init__(self, csv_path: str, tokenizer: SQLTokenizer, max_len: int = 80):
        df = pd.read_csv(csv_path)
        self.seqs = [
            tokenizer.encode(row, add_sos=True, add_eos=True)[:max_len + 2]
            for row in df['payload_delex'].fillna('').tolist()
        ]

    def __len__(self):
        return len(self.seqs)

    def __getitem__(self, idx):
        return self.seqs[idx]


def build_reward_fn(tokenizer, reward_oracle, discriminator, device):
    """Returns a function: (B, T) token_ids tensor → (B,) reward tensor."""
    def fn(token_ids: torch.Tensor) -> torch.Tensor:
        B = token_ids.size(0)
        rewards = torch.zeros(B, device=device)
        with torch.no_grad():
            d_scores = discriminator(token_ids).tolist()
        for i, seq in enumerate(token_ids.tolist()):
            payload = tokenizer.decode(seq)
            result = reward_oracle.compute(payload, d_score=d_scores[i],
                                           token_count=len(seq))
            rewards[i] = result['total']
        return rewards
    return fn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/seqgan_fast.yaml')
    parser.add_argument('--mle_ckpt', default='checkpoints/mle_best.pt')
    parser.add_argument('--data_dir', default=None, help='Override data directory (e.g. data/error_based)')
    parser.add_argument('--ckpt_dir', default=None, help='Override checkpoint output directory')
    parser.add_argument('--steps', type=int, default=None, help='Override total_steps')
    args = parser.parse_args()

    cfg_path = args.config
    if not os.path.isabs(cfg_path) and not os.path.exists(cfg_path):
        cfg_path = os.path.join(ROOT, args.config)
    if not os.path.exists(cfg_path):
        cfg_path = os.path.join(ROOT, 'configs', 'seqgan_default.yaml')
    with open(cfg_path, encoding='utf-8') as f:
        cfg = yaml.safe_load(f)

    ac = cfg['adversarial']
    mc = cfg['model']
    dc = cfg['discriminator']
    rc = cfg['reward']
    seed = ac.get('seed', 42)
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
    print(f"Ckpt dir: {ckpt_dir}")

    tok = SQLTokenizer.load(os.path.join(data_dir, 'tokenizer_vocab.json'))
    print(f"Vocab size: {tok.vocab_size}")

    # Models
    generator = GeneratorLSTM(
        tok.vocab_size, mc['embed_dim'], mc['hidden_dim'], mc['num_layers'], mc['dropout']
    ).to(device)
    discriminator = DiscriminatorCNN(
        tok.vocab_size, dc['embed_dim'], dc['kernel_sizes'], dc['num_filters']
    ).to(device)
    baseline = ValueBaseline(mc['hidden_dim'], ac['baseline_ema_decay']).to(device)

    # Load MLE checkpoint
    mle_path = args.mle_ckpt
    if not os.path.isabs(mle_path) and not os.path.exists(mle_path):
        mle_path = os.path.join(ROOT, args.mle_ckpt)
    if not os.path.exists(mle_path):
        mle_path = os.path.join(ROOT, 'checkpoints', 'mle_best.pt')
    if os.path.exists(mle_path):
        step0, metrics = load_checkpoint(mle_path, generator)
        print(f"Loaded MLE checkpoint (step={step0}, metrics={metrics})")
    else:
        print(f"WARNING: MLE checkpoint not found at {mle_path}, training from scratch")

    # Optimizers
    g_optim = torch.optim.Adam(generator.parameters(), lr=ac['lr_g'],
                                betas=(0.5, 0.999))
    d_optim = torch.optim.Adam(discriminator.parameters(), lr=ac['lr_d'],
                                betas=(0.5, 0.999))
    b_optim = torch.optim.Adam(baseline.parameters(), lr=1e-3)

    # Data
    pad_fn = lambda b: pad_sequences(b, tok.pad_id)
    real_ds = SeqDataset(os.path.join(data_dir, 'train.csv'), tok, mc['max_len'])
    real_loader = DataLoader(real_ds, batch_size=ac['batch_size'],
                             shuffle=True, collate_fn=pad_fn)
    real_iter = iter(real_loader)

    reward_oracle = RewardOracle(
        lambda_d=rc['lambda_d'],
        lambda_bypass=rc['lambda_bypass'],
        lambda_syntax=rc['lambda_syntax'],
        length_penalty_coef=rc['length_penalty_coef'],
        max_len=mc['max_len'],
    )
    rollout = MCRollout(generator, K=ac['mc_rollout_k'], max_len=mc['max_len'])
    reward_fn = build_reward_fn(tok, reward_oracle, discriminator, device)

    writer = SummaryWriter(os.path.join(ROOT, 'runs', 'adversarial')) if HAS_TB else None

    total_steps = args.steps if args.steps is not None else ac['total_steps']
    log_every = ac['log_every']
    eval_every = ac['eval_every']
    save_every = ac['save_every']
    syntax_check_step = ac['syntax_check_step']

    batch_size = ac['batch_size']
    max_len = mc['max_len']

    running_syntax = []
    running_reward = []

    for step in tqdm(range(1, total_steps + 1), desc='Adversarial RL'):
        generator.train()

        # ── Generate fake sequences ONCE — reused for both D-updates and G-update ──
        fake_seqs, log_probs = generator.sample(batch_size, max_len, device,
                                                 tok.sos_id, tok.eos_id)

        # ── Discriminator update (d_steps_per_g× per G update, reuse fake_seqs) ──
        for _ in range(ac['d_steps_per_g']):
            try:
                real_batch = next(real_iter).to(device)
            except StopIteration:
                real_iter = iter(real_loader)
                real_batch = next(real_iter).to(device)

            # Align batch size and sequence length
            B_min = min(real_batch.size(0), fake_seqs.size(0))
            T_min = min(real_batch.size(1), fake_seqs.size(1))
            real_batch_d = real_batch[:B_min, :T_min]
            fake_seqs_d = fake_seqs[:B_min, :T_min].detach()

            d_real = discriminator(real_batch_d)
            d_fake = discriminator(fake_seqs_d)
            gp = discriminator.gradient_penalty(real_batch_d, fake_seqs_d, ac['gp_lambda'])
            d_loss = wgan_gp_loss(d_real, d_fake, gp)

            d_optim.zero_grad()
            d_loss.backward()
            d_optim.step()

        # ── Generator update (REINFORCE) ──

        # Q values via MC rollout (simplified: terminal reward broadcast)
        terminal_rewards = reward_fn(fake_seqs)  # (B,)
        q_values = terminal_rewards  # (B,)

        # Baseline
        last_hidden = generator.get_hidden_last(fake_seqs)  # (B, H)
        b_values = baseline(last_hidden.detach())  # (B,)
        advantages = q_values - b_values.detach()  # (B,)

        # REINFORCE loss (sum log_probs for the full sequence)
        seq_log_probs = log_probs.sum(dim=1)  # (B,)
        reinforce_loss = -(seq_log_probs * advantages.detach()).mean()

        # Entropy bonus: forward pass to get full token distribution
        entropy_coef = ac.get('entropy_coef', 0.0)
        if entropy_coef > 0:
            logits_e, _ = generator(fake_seqs[:, :-1])          # (B, T, V)
            log_p = F.log_softmax(logits_e, dim=-1)              # (B, T, V)
            entropy = -(log_p.exp() * log_p).sum(dim=-1).mean() # scalar
            g_loss = reinforce_loss - entropy_coef * entropy
        else:
            entropy = torch.tensor(0.0)
            g_loss = reinforce_loss

        g_optim.zero_grad()
        g_loss.backward()
        torch.nn.utils.clip_grad_norm_(generator.parameters(), ac['grad_clip'])
        g_optim.step()

        # Baseline update
        b_loss = ((b_values - q_values.detach()) ** 2).mean()
        b_optim.zero_grad()
        b_loss.backward()
        b_optim.step()

        # Track metrics
        mean_r = terminal_rewards.mean().item()
        baseline.update_ema(mean_r)
        running_reward.append(mean_r)

        # Syntax rate tracking
        with torch.no_grad():
            sample_payloads = [tok.decode(seq.tolist()) for seq in fake_seqs[:16]]
        import sqlparse
        syntax_ok = sum(
            1 for p in sample_payloads
            if sqlparse.parse(p.strip()) and sqlparse.parse(p.strip())[0].tokens
        )
        syntax_rate = syntax_ok / len(sample_payloads)
        running_syntax.append(syntax_rate)

        if step % log_every == 0:
            avg_r = sum(running_reward[-log_every:]) / len(running_reward[-log_every:])
            avg_syn = sum(running_syntax[-log_every:]) / len(running_syntax[-log_every:])
            print(f"Step {step:5d} | g_loss={g_loss.item():.4f} | d_loss={d_loss.item():.4f} | "
                  f"reward={avg_r:.4f} | syntax={avg_syn:.2%} | entropy={entropy.item():.3f}")
            if writer:
                writer.add_scalar('adv/g_loss', g_loss.item(), step)
                writer.add_scalar('adv/d_loss', d_loss.item(), step)
                writer.add_scalar('adv/mean_reward', avg_r, step)
                writer.add_scalar('adv/syntax_rate', avg_syn, step)

        # Reward hacking detection: if syntax_rate < 0.5 after syntax_check_step
        if step == syntax_check_step:
            recent_syn = sum(running_syntax[-100:]) / max(len(running_syntax[-100:]), 1)
            if recent_syn < ac['syntax_rate_threshold']:
                print(f"WARNING: syntax_rate={recent_syn:.2%} < threshold -> boosting lambda_syntax")
                reward_oracle.update_lambda_syntax(ac['lambda_syntax_boosted'])

        if step % save_every == 0:
            save_checkpoint(
                os.path.join(ckpt_dir, f'adv_step{step}.pt'),
                generator, g_optim, step,
                {'mean_reward': mean_r, 'syntax_rate': syntax_rate}
            )

    save_checkpoint(
        os.path.join(ckpt_dir, 'adv_final.pt'),
        generator, g_optim, total_steps,
        {'final': True}
    )
    print("Adversarial training done. Checkpoint: checkpoints/adv_final.pt")
    if writer:
        writer.close()


if __name__ == '__main__':
    main()
