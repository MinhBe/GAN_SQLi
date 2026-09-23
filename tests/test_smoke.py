
import torch
from abcd_seqgan.data import Codec,Samples
from abcd_seqgan.models import Generator,Discriminator
from abcd_seqgan.rollout import Rollout
def test_forward_rollout_and_condition():
    rows=[]
    for y in ["Y1","Y2"]:
        for i in range(5):
            rows.append(dict(payload_raw=f"score = {i}",y_complexity=y,abstract_family_id="AF_01",
                             database="SQLite",query_language="SQL",root_id=y+"_R01",
                             structure_cell_id=y+"_R01_D01"))
    codec=Codec(rows)
    seq,c=Samples(rows,codec)[0]
    seq=seq[None,:].repeat(2,1);c=c[None,:].repeat(2,1)
    g=Generator(len(codec.itos),codec.maps,emb=16,hidden=24,layers=1,cond_dim=128)
    d=Discriminator(len(codec.itos),codec.maps,emb=16,filters=8,cond_dim=128)
    inp=torch.cat([torch.ones_like(seq[:,:1]),seq[:,:-1]],1)
    loss=torch.nn.functional.cross_entropy(g(inp,c).reshape(-1,len(codec.itos)),seq.reshape(-1),ignore_index=0)
    loss.backward()
    assert g.proj.weight.grad is not None
    with torch.no_grad():
        samples=g.sample(c,codec.max_len)
        rewards,mask=Rollout(g).rewards(samples,c,d,rollouts=1,stride=3)
    assert samples.shape==seq.shape
    assert rewards.shape==seq.shape
    assert torch.isfinite(rewards).all()
    assert mask.sum()>0
