import torch
from abcd_seqgan.models import Generator,Discriminator
from abcd_seqgan.rollout import Rollout

def test_batched_rollout_shapes_and_prefix():
    torch.manual_seed(12)
    maps={"y_complexity":{"Y1":1},"database":{"SQLite":1}}
    g=Generator(16,maps,emb=8,hidden=12,layers=1,cond_dim=8)
    d=Discriminator(16,maps,emb=8,filters=4,cond_dim=8)
    c=torch.ones(3,2,dtype=torch.long)
    seq=g.sample(c,12)
    prefix=seq[:,:4]
    out=g.sample(c,12,prefix=prefix)
    assert torch.equal(out[:,:4],prefix)
    rewards,mask=Rollout(g).rewards(seq,c,d,rollouts=2,stride=4)
    assert rewards.shape==mask.shape==seq.shape
    assert torch.isfinite(rewards).all()
