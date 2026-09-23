# ABCD Conditional SeqGAN — research MVP

**Only Corpus A is read.** The input archive is `Boolean_ABCD.zip`; `B_DETECTOR_CORPUS` is ignored. The archive has 28,800 A rows, of which 28,000 contain nonempty text; 800 Cassandra slots are unsupported. There are 1,400 nonempty cells × 20 samples. This is a *synthetic Boolean-style cross-dialect representation corpus*, not confirmed exploit observations.

## Repository dataset

Upload the **complete, unmodified** `Boolean_ABCD.zip` at the repository root. The training entry point accepts it directly with `--data Boolean_ABCD.zip`, and reads only `A_GENERATOR_CORPUS` from the archive. Keep metadata/provenance files intact; Corpus B is not used for training.

## Algorithm

Modern PyTorch implementation inspired by [Lantao Yu SeqGAN](https://github.com/LantaoYu/SeqGAN): conditional LSTM generator; conditional CNN discriminator; generator MLE pretraining; discriminator pretraining; alternating token-level REINFORCE and discriminator training; EMA rollout policy for intermediate prefix rewards. Unlike original SeqGAN, the architecture conditions on **six fields**: `y_complexity`, `abstract_family_id`, `database`, `query_language`, `root_id`, `structure_cell_id`. All six are metadata conditions, not text tokens. No normalization of raw payload text.

`--rollout-stride 1` uses MC completion rewards for every prefix (full SeqGAN-style per-action rollout); default stride 8 reuses rewards across blocks to save compute on long sequences (approximation). No guarantee of unique semantics or DB engine validity. CNN discriminator evaluates complete tokenized sequences. Generator EOS/PAD tokens are masked in policy loss; rollouts stop when EOS is reached.

## Kaggle dual T4

Attach `Boolean_ABCD.zip` as Kaggle Dataset, enable **GPU T4 ×2**, and set Internet on if cloning from GitHub. Do not `pip install --upgrade torch` on Kaggle: keep preinstalled CUDA-compatible PyTorch unless requirements actually fail.

```bash
!git clone https://github.com/YOUR_NAME/YOUR_REPO.git /kaggle/working/abcd-seqgan
%cd /kaggle/working/abcd-seqgan
!python -m pip install -q pytest
!nvidia-smi
!python -m pytest -q
!torchrun --standalone --nproc_per_node=2 -m abcd_seqgan.train \
  --data /kaggle/input/YOUR_DATASET/Boolean_ABCD.zip \
  --out /kaggle/working/abcd_run --amp --batch 64 \
  --mle-epochs 12 --d-epochs 3 --adv-epochs 5 \
  --rollouts 4 --rollout-stride 8
```

`--batch` is **per GPU**, so global batch is 128. FP16 AMP uses `torch.amp.autocast` and `GradScaler`; DDP uses NCCL with one process/GPU. The full dataset maximum length is 464 chars + EOS = 465; no silent truncation. Max length can dominate rollout cost. The default stride 8 is an *approximate* speed/quality compromise, not full token-by-token rollout.

Smoke first, without spending hours:

```bash
!torchrun --standalone --nproc_per_node=2 -m abcd_seqgan.train \
  --data /kaggle/input/YOUR_DATASET/Boolean_ABCD.zip \
  --out /kaggle/working/smoke --amp --batch 8 \
  --mle-epochs 1 --d-epochs 1 --adv-epochs 1 \
  --rollouts 1 --rollout-stride 32 --max-steps 2
```

Generate in parallel across both GPUs (1 process/GPU; each gets disjoint cells):

```bash
!torchrun --standalone --nproc_per_node=2 -m abcd_seqgan.generate \
  --data /kaggle/input/YOUR_DATASET/Boolean_ABCD.zip \
  --checkpoint /kaggle/working/abcd_run/checkpoint.pt \
  --out /kaggle/working/abcd_generated \
  --per-cell 60 --attempts 600 --batch 128 --temperature 0.9
```

Results: `generated_all.csv` (new, distinct raw strings *within each cell*) and `stats_all.csv` (attempts, actual accepted count, quota). There is **no automatic filler** if quota is unmet. `--strict-signature` optionally requires equality to a training string after substituting numeric and quoted literals; this is a coarse heuristic, not a grammar parser. Default condition-only output is explicitly marked `condition_only_unverified`. Never claim it satisfies the cell's grammar without a dialect-aware parser/validator. The generated CSV contains no original rows; original + new must be combined separately after review.

### Resume and session limits

Checkpoint is saved each epoch to `checkpoint.pt` plus `codec.json`. `--resume /kaggle/working/abcd_run/checkpoint.pt` resumes the saved phase/epoch; when resuming, use the same hyperparameters. Save `/kaggle/working/abcd_run` as a Kaggle notebook output at the end of each session. Kaggle sessions are not guaranteed to preserve `/kaggle/working` across sessions.

### Throughput / optimization knobs

- Benchmark `--batch 32/64/128` and monitor `nvidia-smi`, steps/sec, memory, loss. More GPU utilization is not necessarily faster accepted samples/sec.
- For exact token-level MC use `--rollout-stride 1` but expect substantially longer training, especially at 465 tokens. Start with 8/16/32 for exploratory runs, then compare to 1 on a smaller study.
- `--rollouts 2/4/8` trades compute for reward variance. Measure novelty and structural acceptance per cell.
- For this small corpus, two-GPU DDP may be slower than one GPU on short sequences due to sync overhead. Benchmark `python -m abcd_seqgan.train ...` against `torchrun ...`.
- Do not assume FP16 AMP improves LSTM throughput on every sequence length; compare time/epoch.
- `--max-len` below longest training sequence **raises an error**, rather than silently discarding examples.
- The generator and discriminator are small; increasing layers/hidden size is not guaranteed to improve generation.
- The input corpus is not a binary benign/attack dataset. This repo contains no detector training or Corpus B pipeline.

### Known limitations

1. Long-sequence rollout is expensive; default stride 8 approximates per-token rewards. For exact SeqGAN-style reward estimation use stride 1.
2. Generated samples are synthetic, and condition compliance is *not guaranteed*. Database engine execution/semantic equivalence is not implemented.
3. DDP training and generation were authored for dual T4, but **not benchmarked on Kaggle in this environment**. Run the included smoke tests and the 2-step dual-GPU smoke before full training.
4. The six conditions include some redundant metadata (root and cell imply other fields). Ablation can test removing root or cell embeddings after first working run.
5. `--resume` restores model and optimizer state but not exact RNG or sampler position. It resumes at epoch boundaries, not bit-for-bit identical.
6. Dataset output size and novelty may be much smaller than target. `stats_all.csv` is the authoritative count.
