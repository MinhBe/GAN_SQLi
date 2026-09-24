
import torch
from torch import nn
import torch.nn.functional as F

class Condition(nn.Module):
    def __init__(self, maps, dim=24, out=128):
        super().__init__()
        self.emb=nn.ModuleList([nn.Embedding(len(m)+1,dim,padding_idx=0) for m in maps.values()])
        self.net=nn.Sequential(nn.Linear(len(self.emb)*dim,out),nn.Tanh())
        self.out=out
    def forward(self,c):
        return self.net(torch.cat([e(c[:,i]) for i,e in enumerate(self.emb)],dim=-1))

class Generator(nn.Module):
    def __init__(self, vocab, maps, emb=128, hidden=256, layers=2, cond_dim=128):
        super().__init__()
        self.cond=Condition(maps,out=cond_dim)
        self.embed=nn.Embedding(vocab,emb,padding_idx=0)
        self.lstm=nn.LSTM(emb+cond_dim,hidden,layers,batch_first=True)
        self.h0=nn.Linear(cond_dim,hidden*layers)
        self.c0=nn.Linear(cond_dim,hidden*layers)
        self.proj=nn.Linear(hidden,vocab)
        self.hidden=hidden;self.layers=layers
    def forward(self, tokens, c):
        z=self.cond(c); b=tokens.size(0)
        h=self.h0(z).reshape(b,self.layers,self.hidden).transpose(0,1).contiguous()
        cell=self.c0(z).reshape(b,self.layers,self.hidden).transpose(0,1).contiguous()
        x=torch.cat([self.embed(tokens),z[:,None,:].expand(-1,tokens.size(1),-1)],-1)
        y,_=self.lstm(x,(h,cell))
        return self.proj(y)
    @torch.no_grad()
    def sample(self,c,max_len,temperature=1.0,prefix=None):
        """Decode with cached LSTM state. Prefix is consumed ONCE; only suffix is sampled.
        PAD is emitted after EOS. Returns [batch, max_len].
        """
        z=self.cond(c)
        b=c.size(0)
        h=self.h0(z).reshape(b,self.layers,self.hidden).transpose(0,1).contiguous()
        cell=self.c0(z).reshape(b,self.layers,self.hidden).transpose(0,1).contiguous()
        cur=torch.full((b,),1,device=c.device,dtype=torch.long)
        prefix_len=0 if prefix is None else min(prefix.size(1),max_len)
        if prefix_len:
            prefix=prefix[:,:prefix_len]
        finished=torch.zeros(b,device=c.device,dtype=torch.bool)
        seq=[]
        for t in range(max_len):
            x=torch.cat([self.embed(cur),z],-1).unsqueeze(1)
            y,(h,cell)=self.lstm(x,(h,cell))
            if t<prefix_len:
                nxt=prefix[:,t]
            else:
                logits=self.proj(y[:,0]).float()/max(temperature,0.05)
                logits[:,0]=-1e9
                logits[:,1]=-1e9
                logits[:,3]=-1e9
                nxt=torch.multinomial(torch.softmax(logits,dim=-1),1).squeeze(1)
                nxt=torch.where(finished,torch.zeros_like(nxt),nxt)
            seq.append(nxt)
            finished |= nxt.eq(2) | nxt.eq(0)
            cur=nxt
            if t>=prefix_len and finished.all():
                break
        result=torch.stack(seq,1)
        if result.size(1)<max_len:
            result=F.pad(result,(0,max_len-result.size(1)))
        return result

class Discriminator(nn.Module):
    def __init__(self,vocab,maps,emb=128,filters=128,cond_dim=128,dropout=0.3):
        super().__init__()
        self.cond=Condition(maps,out=cond_dim)
        self.embed=nn.Embedding(vocab,emb,padding_idx=0)
        self.convs=nn.ModuleList([nn.Conv1d(emb+cond_dim,filters,k,padding=0) for k in (2,3,4,5)])
        self.fc=nn.Sequential(nn.Linear(filters*4+cond_dim,256),nn.LeakyReLU(0.2),nn.Dropout(dropout),nn.Linear(256,1))
    def forward(self,tokens,c):
        z=self.cond(c)
        x=torch.cat([self.embed(tokens),z[:,None,:].expand(-1,tokens.size(1),-1)],-1).transpose(1,2)
        features=[F.relu(conv(x)).amax(-1) for conv in self.convs]
        return self.fc(torch.cat(features+[z],-1)).squeeze(-1)
