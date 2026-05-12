"""Loss functions: MLE, REINFORCE, WGAN-GP."""
import torch
import torch.nn.functional as F


def mle_loss(logits: torch.Tensor, targets: torch.Tensor,
             pad_id: int = 0, expert_mask: torch.Tensor = None,
             expert_weight: float = 3.0) -> torch.Tensor:
    """
    logits: (B, T, V), targets: (B, T)
    expert_mask: (B,) bool — True for expert demo rows
    """
    B, T, V = logits.shape
    loss = F.cross_entropy(
        logits.reshape(B * T, V),
        targets.reshape(B * T),
        ignore_index=pad_id,
        reduction='none',
    ).reshape(B, T)

    # Mean over non-pad positions
    non_pad = (targets != pad_id).float()
    loss = (loss * non_pad).sum(dim=1) / non_pad.sum(dim=1).clamp(min=1)  # (B,)

    if expert_mask is not None and expert_mask.any():
        weights = torch.ones(B, device=logits.device)
        weights[expert_mask] = expert_weight
        loss = (loss * weights).mean()
    else:
        loss = loss.mean()
    return loss


def reinforce_loss(log_probs: torch.Tensor, advantages: torch.Tensor,
                   pad_mask: torch.Tensor = None) -> torch.Tensor:
    """
    log_probs: (B, T) per-token log probabilities
    advantages: (B, T) or (B,) — if (B,) broadcast to T
    pad_mask: (B, T) bool, True where real (not pad)
    """
    if advantages.dim() == 1:
        advantages = advantages.unsqueeze(1).expand_as(log_probs)
    if pad_mask is not None:
        loss = -(log_probs * advantages.detach() * pad_mask.float()).sum() / pad_mask.float().sum().clamp(min=1)
    else:
        loss = -(log_probs * advantages.detach()).mean()
    return loss


def reinforce_loss_with_entropy(
    log_probs: torch.Tensor,
    advantages: torch.Tensor,
    logits: torch.Tensor,
    entropy_coeff: float = 0.03,
    pad_mask: torch.Tensor = None,
) -> tuple:
    """
    REINFORCE + entropy bonus to prevent mode collapse.

    Returns (total_loss, pg_loss, entropy_loss) for logging.

    log_probs: (B, T) per-token log probs from sampled sequence
    advantages: (B,) sequence-level advantages
    logits: (B, T, V) raw logits — used to compute entropy
    entropy_coeff: weight for entropy bonus (higher = more exploration)
    pad_mask: (B, T) bool, True where real (not pad)
    """
    if advantages.dim() == 1:
        advantages = advantages.unsqueeze(1).expand_as(log_probs)

    if pad_mask is not None:
        mask_f = pad_mask.float()
        n = mask_f.sum().clamp(min=1)
        pg_loss = -(log_probs * advantages.detach() * mask_f).sum() / n
        # Token-level entropy: -sum(p * log p) averaged over non-pad tokens
        probs = torch.softmax(logits, dim=-1)
        log_p = torch.log_softmax(logits, dim=-1)
        token_entropy = -(probs * log_p).sum(dim=-1)  # (B, T)
        entropy_loss = -(token_entropy * mask_f).sum() / n
    else:
        pg_loss = -(log_probs * advantages.detach()).mean()
        probs = torch.softmax(logits, dim=-1)
        log_p = torch.log_softmax(logits, dim=-1)
        token_entropy = -(probs * log_p).sum(dim=-1)
        entropy_loss = -token_entropy.mean()

    total_loss = pg_loss + entropy_coeff * entropy_loss
    return total_loss, pg_loss, entropy_loss


def wgan_gp_loss(d_real: torch.Tensor, d_fake: torch.Tensor,
                 gp: torch.Tensor) -> torch.Tensor:
    """Wasserstein distance + gradient penalty."""
    return -d_real.mean() + d_fake.mean() + gp
