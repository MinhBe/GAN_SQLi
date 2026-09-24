
import copy
import torch
import torch.nn.functional as F

class Rollout:
    """EMA rollout policy; stride=1 evaluates every action, stride>1 amortizes MC work."""
    def __init__(self,generator,update_rate=0.8):
        self.policy=copy.deepcopy(generator).eval()
        self.rate=update_rate
        for p in self.policy.parameters():p.requires_grad_(False)
    @torch.no_grad()
    def update(self, generator):
        for a,b in zip(self.policy.parameters(),generator.parameters()):
            a.mul_(self.rate).add_(b,alpha=1-self.rate)
        for a,b in zip(self.policy.buffers(),generator.buffers()):a.copy_(b)
    @torch.no_grad()
    def rewards(self,seq,c,discriminator,rollouts=4,stride=8,temperature=1.0):
        """Batched Monte Carlo continuations; do not rollout after all EOS tokens."""
        B,L=seq.shape
        eos=seq.eq(2).int().cumsum(1)
        valid=seq.ne(0) & (eos.eq(0) | seq.eq(2) & eos.eq(1))
        last=torch.sigmoid(discriminator(seq,c).float())
        rewards=torch.zeros((B,L),device=seq.device)
        # Nothing after last active token can contribute to policy loss.
        active_len=int(valid.sum(1).max().item())
        steps=list(range(stride,active_len,stride))
        previous=0
        for t in steps:
            # Generate K continuations in a single GPU batch, not K serial launches.
            prefix=seq[:,:t].repeat_interleave(rollouts,dim=0)
            conditions=c.repeat_interleave(rollouts,dim=0)
            completion=self.policy.sample(conditions,L,temperature,prefix=prefix)
            scores=torch.sigmoid(discriminator(completion,conditions).float())
            scores=scores.reshape(B,rollouts).mean(1)
            rewards[:,previous:t]=scores[:,None]
            previous=t
        rewards[:,previous:]=last[:,None]
        return rewards*valid.float(),valid.float()
