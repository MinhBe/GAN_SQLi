
import argparse, json, os, random, time
from contextlib import nullcontext
from pathlib import Path
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
from .data import load_rows,Codec,Samples
from .models import Generator,Discriminator
from .rollout import Rollout

def setup(seed):
    rank=int(os.environ.get("RANK",0))
    world=int(os.environ.get("WORLD_SIZE",1))
    local=int(os.environ.get("LOCAL_RANK",0))
    if world>1:
        if not torch.cuda.is_available(): raise RuntimeError("DDP requires CUDA here")
        torch.cuda.set_device(local)
        dist.init_process_group("nccl")
    dev=torch.device(f"cuda:{local}" if torch.cuda.is_available() else "cpu")
    random.seed(seed+rank);np.random.seed(seed+rank);torch.manual_seed(seed+rank)
    return rank,world,dev

def model(m): return m.module if isinstance(m,DDP) else m
def amp_context(dev, enabled):
    return torch.autocast("cuda",dtype=torch.float16) if dev.type=="cuda" and enabled else nullcontext()
def scaler_for(dev,enabled):
    return torch.amp.GradScaler("cuda",enabled=dev.type=="cuda" and enabled)
def step(loss,net,opt,scaler,clip):
    opt.zero_grad(set_to_none=True)
    scaler.scale(loss).backward()
    scaler.unscale_(opt)
    nn.utils.clip_grad_norm_(net.parameters(),clip)
    scaler.step(opt);scaler.update()
def g_loss(g,seq,c,dev,amp):
    inp=torch.cat([torch.ones_like(seq[:,:1]),seq[:,:-1]],1)
    with amp_context(dev,amp):
        logits=g(inp,c)
        loss=F.cross_entropy(logits.reshape(-1,logits.size(-1)),seq.reshape(-1),ignore_index=0)
    return loss
def d_loss(d,real,fake,c,dev,amp):
    with amp_context(dev,amp):
        logits_real=d(real,c);logits_fake=d(fake,c)
        return (F.binary_cross_entropy_with_logits(logits_real,torch.ones_like(logits_real))+
                F.binary_cross_entropy_with_logits(logits_fake,torch.zeros_like(logits_fake)))/2

def save(path,g,d,go,do,codec,config,phase,epoch):
    path=Path(path);path.mkdir(parents=True,exist_ok=True)
    codec.save(path/"codec.json")
    torch.save({"generator":model(g).state_dict(),"discriminator":model(d).state_dict(),
                "g_opt":go.state_dict(),"d_opt":do.state_dict(),
                "config":config,"phase":phase,"epoch":epoch},path/"checkpoint.pt")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data",required=True,help="Boolean_ABCD.zip or extracted directory")
    ap.add_argument("--out",default="runs/abcd")
    ap.add_argument("--batch",type=int,default=64,help="per GPU batch")
    ap.add_argument("--workers",type=int,default=2)
    ap.add_argument("--max-len",type=int,default=0)
    ap.add_argument("--embedding",type=int,default=128)
    ap.add_argument("--hidden",type=int,default=256)
    ap.add_argument("--layers",type=int,default=2)
    ap.add_argument("--filters",type=int,default=128)
    ap.add_argument("--mle-epochs",type=int,default=12)
    ap.add_argument("--d-epochs",type=int,default=3)
    ap.add_argument("--adv-epochs",type=int,default=5)
    ap.add_argument("--rollouts",type=int,default=4)
    ap.add_argument("--rollout-stride",type=int,default=8,help="1 = full per-token MC")
    ap.add_argument("--g-lr",type=float,default=0.001)
    ap.add_argument("--d-lr",type=float,default=0.0002)
    ap.add_argument("--adv-lr",type=float,default=0.0001)
    ap.add_argument("--amp",action="store_true")
    ap.add_argument("--seed",type=int,default=42)
    ap.add_argument("--resume",default="")
    ap.add_argument("--max-steps",type=int,default=0,help="debug: cap batches/epoch")
    args=ap.parse_args()
    rank,world,dev=setup(args.seed)
    if rank==0: print(f"device={dev} world={world} torch={torch.__version__}",flush=True)
    rows=load_rows(args.data)
    out=Path(args.out)
    codec=Codec.load(Path(args.resume).parent/"codec.json") if args.resume else Codec(rows,args.max_len)
    if rank==0:
        print(f"eligible={len(rows)} cells={len({r['structure_cell_id'] for r in rows})} max_len={codec.max_len} vocab={len(codec.itos)}",flush=True)
        out.mkdir(parents=True,exist_ok=True)
        (out/"run_config.json").write_text(json.dumps(vars(args),indent=2))
    dataset=Samples(rows,codec)
    sampler=DistributedSampler(dataset,num_replicas=world,rank=rank,shuffle=True,drop_last=True) if world>1 else None
    loader=DataLoader(dataset,batch_size=args.batch,shuffle=sampler is None,sampler=sampler,
                      drop_last=True,num_workers=args.workers,pin_memory=dev.type=="cuda",
                      persistent_workers=args.workers>0)
    config=dict(vocab=len(codec.itos),maps=codec.maps,emb=args.embedding,hidden=args.hidden,layers=args.layers,filters=args.filters)
    g=Generator(config["vocab"],config["maps"],config["emb"],config["hidden"],config["layers"]).to(dev)
    d=Discriminator(config["vocab"],config["maps"],config["emb"],config["filters"]).to(dev)
    go=torch.optim.Adam(g.parameters(),lr=args.g_lr)
    do=torch.optim.Adam(d.parameters(),lr=args.d_lr)
    phase="mle";start=0
    if args.resume:
        ck=torch.load(args.resume,map_location="cpu",weights_only=False)
        if ck["config"]!=config: raise ValueError("resume architecture differs")
        g.load_state_dict(ck["generator"]);d.load_state_dict(ck["discriminator"])
        go.load_state_dict(ck["g_opt"]);do.load_state_dict(ck["d_opt"])
        phase=ck["phase"];start=ck["epoch"]+1
    if world>1:
        g=DDP(g,device_ids=[dev.index],output_device=dev.index)
        d=DDP(d,device_ids=[dev.index],output_device=dev.index)
    gs=scaler_for(dev,args.amp);ds=scaler_for(dev,args.amp)
    rollout=Rollout(model(g))
    phases=[("mle",args.mle_epochs),("d",args.d_epochs),("adv",args.adv_epochs)]
    idx=[v[0] for v in phases].index(phase)
    for stage,total in phases[idx:]:
        if stage != phase: start=0
        if stage=="adv":
            for group in go.param_groups: group["lr"]=args.adv_lr
        for epoch in range(start,total):
            if sampler: sampler.set_epoch(epoch+sum(x[1] for x in phases[:[v[0] for v in phases].index(stage)]))
            if dev.type=="cuda": torch.cuda.reset_peak_memory_stats(dev); torch.cuda.synchronize(dev)
            t0=time.time(); losses=[]
            g.train();d.train()
            for i,(real,c) in enumerate(loader):
                if args.max_steps and i>=args.max_steps:break
                real=real.to(dev,non_blocking=True);c=c.to(dev,non_blocking=True)
                if stage=="mle":
                    loss=g_loss(g,real,c,dev,args.amp)
                    step(loss,g,go,gs,1.0)
                elif stage=="d":
                    with torch.no_grad():
                        fake=model(g).sample(c,codec.max_len)
                    loss=d_loss(d,real,fake,c,dev,args.amp)
                    step(loss,d,do,ds,1.0)
                else:
                    # Freeze D parameters, but keep D usable for reward inference.
                    model(d).eval()
                    with torch.no_grad():
                        seq=model(g).sample(c,codec.max_len)
                        rewards,mask=rollout.rewards(seq,c,model(d),args.rollouts,args.rollout_stride)
                    inp=torch.cat([torch.ones_like(seq[:,:1]),seq[:,:-1]],1)
                    with amp_context(dev,args.amp):
                        logits=g(inp,c)
                        lp=F.log_softmax(logits.float(),-1).gather(-1,seq.unsqueeze(-1)).squeeze(-1)
                        # Per-condition batch baseline; do not center over time (different prefix rewards).
                        baseline=(rewards*mask).sum(0)/(mask.sum(0).clamp_min(1))
                        advantage=(rewards-baseline[None,:]).detach()
                        loss=-(lp*advantage*mask).sum()/mask.sum().clamp_min(1)
                    step(loss,g,go,gs,1.0)
                    rollout.update(model(g))
                    model(d).train()
                    with torch.no_grad():
                        fake=model(g).sample(c,codec.max_len)
                    dloss=d_loss(d,real,fake,c,dev,args.amp)
                    step(dloss,d,do,ds,1.0)
                losses.append(float(loss.detach()))
            if dev.type=="cuda": torch.cuda.synchronize(dev)
            elapsed=time.time()-t0
            if rank==0:
                print(json.dumps({"stage":stage,"epoch":epoch,"loss":sum(losses)/max(1,len(losses)),
                                  "steps":len(losses),"seconds":round(elapsed,1),
                                  "training_sequences_per_second":round(len(losses)*args.batch*world/max(elapsed,1e-6),1),
                                  "gpu_peak_allocated_gib":round(torch.cuda.max_memory_allocated(dev)/2**30,2) if dev.type=="cuda" else 0}),flush=True)
                next_phase=phases[[v[0] for v in phases].index(stage)+1][0] if epoch==total-1 and stage!="adv" else stage
                save(out,g,d,go,do,codec,config,next_phase,-1 if next_phase!=stage else epoch)
            if world>1:dist.barrier()
        phase=stage;start=0
    if world>1:dist.destroy_process_group()
if __name__=="__main__":main()
