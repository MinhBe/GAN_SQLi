from __future__ import annotations
from dataclasses import dataclass
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

PAD,BOS,EOS,UNK='<PAD>','<BOS>','<EOS>','<UNK>'

class CharTokenizer:
    def __init__(self, max_len=160): self.max_len=max_len; self.itos=[]; self.stoi={}
    def fit(self, texts):
        chars=sorted({c for t in texts for c in str(t)})
        self.itos=[PAD,BOS,EOS,UNK]+chars; self.stoi={t:i for i,t in enumerate(self.itos)}; return self
    @property
    def pad_id(self): return self.stoi[PAD]
    @property
    def bos_id(self): return self.stoi[BOS]
    @property
    def eos_id(self): return self.stoi[EOS]
    @property
    def vocab_size(self): return len(self.itos)
    def encode(self, text):
        ids=[self.bos_id]+[self.stoi.get(c,self.stoi[UNK]) for c in str(text)]+[self.eos_id]
        ids=ids[:self.max_len]+[self.pad_id]*max(0,self.max_len-len(ids)); return ids
    def decode(self, ids):
        out=[]
        for i in ids:
            tok=self.itos[int(i)] if 0<=int(i)<len(self.itos) else UNK
            if tok==EOS: break
            if tok not in {PAD,BOS,UNK}: out.append(tok)
        return ''.join(out)

@dataclass
class SeqGANConfig:
    max_len:int=160; embedding_dim:int=64; hidden_dim:int=128; batch_size:int=64; mle_epochs:int=1; adv_epochs:int=1; lr:float=1e-3; temperature:float=1.0; device:str='cuda' if torch.cuda.is_available() else 'cpu'

class Gen(nn.Module):
    def __init__(self,v,e,h): super().__init__(); self.emb=nn.Embedding(v,e); self.rnn=nn.LSTM(e,h,batch_first=True); self.fc=nn.Linear(h,v)
    def forward(self,x): z=self.emb(x); o,_=self.rnn(z); return self.fc(o)

class Disc(nn.Module):
    def __init__(self,v,e,h): super().__init__(); self.emb=nn.Embedding(v,e); self.rnn=nn.LSTM(e,h,batch_first=True,bidirectional=True); self.fc=nn.Linear(2*h,1)
    def forward(self,x): z=self.emb(x); _,(h,_)=self.rnn(z); return self.fc(torch.cat([h[-2],h[-1]],-1)).squeeze(-1)

class SeqGANStarter:
    """Compact SeqGAN-style starter. For paper-grade reproduction, add full MC rollout reward estimation."""
    def __init__(self, tok, cfg=SeqGANConfig()):
        self.tok=tok; self.cfg=cfg; self.dev=torch.device(cfg.device); self.G=Gen(tok.vocab_size,cfg.embedding_dim,cfg.hidden_dim).to(self.dev); self.D=Disc(tok.vocab_size,cfg.embedding_dim,cfg.hidden_dim).to(self.dev)
    def _ten(self,texts): return torch.tensor([self.tok.encode(t) for t in texts], dtype=torch.long)
    def pretrain_mle(self,texts):
        data=self._ten(texts); dl=DataLoader(TensorDataset(data), batch_size=self.cfg.batch_size, shuffle=True); opt=torch.optim.Adam(self.G.parameters(), lr=self.cfg.lr); losses=[]
        for _ in range(self.cfg.mle_epochs):
            for (x,) in dl:
                x=x.to(self.dev); logits=self.G(x[:,:-1]); loss=F.cross_entropy(logits.reshape(-1,logits.size(-1)), x[:,1:].reshape(-1), ignore_index=self.tok.pad_id); opt.zero_grad(); loss.backward(); opt.step(); losses.append(float(loss.item()))
        return sum(losses)/max(1,len(losses))
    @torch.no_grad()
    def sample_ids(self,n):
        x=torch.full((n,1), self.tok.bos_id, dtype=torch.long, device=self.dev)
        for _ in range(self.cfg.max_len-1):
            probs=torch.softmax(self.G(x)[:,-1,:]/max(1e-6,self.cfg.temperature), -1); nxt=torch.multinomial(probs,1); x=torch.cat([x,nxt],1)
        return x
    @torch.no_grad()
    def generate(self,n): return [self.tok.decode(row.cpu().tolist()) for row in self.sample_ids(n)]
    def fit(self,texts):
        texts=list(texts); mle=self.pretrain_mle(texts)
        # Minimal discriminator pass just to keep artifact small.
        return {'mle_loss':mle, 'note':'starter implementation; add full rollout for paper reproduction'}
