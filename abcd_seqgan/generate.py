
import argparse,csv,json,os,re,hashlib
from collections import defaultdict,Counter
from pathlib import Path
import torch
import torch.distributed as dist
from .data import load_rows,Codec
from .models import Generator

def signature(text):
    # Fast heuristic, not an AST or dialect engine validator.
    text=re.sub(r"'(?:''|[^'])*'","<STR>",text)
    text=re.sub(r'"(?:\\"|[^"])*"','<STR>',text)
    text=re.sub(r'\b\d+\b',"<NUM>",text)
    return text

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data",required=True)
    ap.add_argument("--checkpoint",required=True)
    ap.add_argument("--out",default="runs/abcd/generated")
    ap.add_argument("--per-cell",type=int,default=60)
    ap.add_argument("--attempts",type=int,default=600)
    ap.add_argument("--batch",type=int,default=128)
    ap.add_argument("--temperature",type=float,default=0.9)
    ap.add_argument("--max-cells",type=int,default=0,help="debug")
    ap.add_argument("--strict-signature",action="store_true",help="only exact numeric/string abstracted string shape; may reject valid novel renderings")
    args=ap.parse_args()
    rank=int(os.environ.get("RANK",0));world=int(os.environ.get("WORLD_SIZE",1))
    local=int(os.environ.get("LOCAL_RANK",0))
    if world>1:
        torch.cuda.set_device(local);dist.init_process_group("nccl")
    dev=torch.device(f"cuda:{local}" if torch.cuda.is_available() else "cpu")
    rows=load_rows(args.data)
    codec=Codec.load(Path(args.checkpoint).parent/"codec.json")
    ck=torch.load(args.checkpoint,map_location="cpu",weights_only=False)
    cfg=ck["config"]
    g=Generator(cfg["vocab"],cfg["maps"],cfg["emb"],cfg["hidden"],cfg["layers"]).to(dev)
    g.load_state_dict(ck["generator"]);g.eval()
    groups=defaultdict(list)
    for r in rows:groups[r["structure_cell_id"]].append(r)
    keys=sorted(groups)
    if args.max_cells:keys=keys[:args.max_cells]
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    fields=["sample_id","structure_cell_id","root_id","y_complexity","abstract_family_id",
            "database","query_language","payload_raw","generated_source_type",
            "structure_match_method","behavior_validated","compatibility_status","raw_sha256"]
    total=0
    with open(out/f"generated_rank{rank}.csv","w",encoding="utf-8",newline="") as f, \
         open(out/f"stats_rank{rank}.csv","w",encoding="utf-8",newline="") as sf:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        sw=csv.DictWriter(sf,fieldnames=["structure_cell_id","original","accepted","attempted","quota"]);sw.writeheader()
        for idx,key in enumerate(keys):
            if idx%world!=rank:continue
            rs=groups[key];r=rs[0];seen={x["payload_raw"] for x in rs}
            signatures={signature(x["payload_raw"]) for x in rs}
            accepted=0;attempted=0
            cond=torch.tensor([codec.condition(r)],device=dev,dtype=torch.long)
            while accepted<args.per_cell and attempted<args.attempts:
                n=min(args.batch,args.attempts-attempted)
                cc=cond.expand(n,-1)
                with torch.inference_mode():
                    seq=g.sample(cc,codec.max_len,args.temperature).cpu().tolist()
                attempted+=n
                for tokens in seq:
                    if accepted>=args.per_cell:break
                    text=codec.decode(tokens)
                    if not text or text in seen or "<" in text and "UNK" in text:continue
                    if 2 not in tokens:continue # reject truncated generations
                    if args.strict_signature and signature(text) not in signatures:continue
                    seen.add(text);accepted+=1;total+=1
                    w.writerow(dict(sample_id=f"SEQGAN_{key}_{accepted:04d}",structure_cell_id=key,
                        root_id=r["root_id"],y_complexity=r["y_complexity"],
                        abstract_family_id=r["abstract_family_id"],database=r["database"],
                        query_language=r["query_language"],payload_raw=text,
                        generated_source_type="seqgan_synthetic_unvalidated",
                        structure_match_method="exact_abstracted_string_heuristic" if args.strict_signature else "condition_only_unverified",
                        behavior_validated="false",compatibility_status="generated_not_engine_validated",
                        raw_sha256=hashlib.sha256(text.encode()).hexdigest()))
            sw.writerow(dict(structure_cell_id=key,original=len(rs),accepted=accepted,attempted=attempted,quota=args.per_cell))
            if idx%25==0:print(f"rank={rank} cell={idx}/{len(keys)} accepted={accepted}/{args.per_cell}",flush=True)
    if world>1:dist.barrier()
    if rank==0:
        for stem in ["generated","stats"]:
            files=[out/f"{stem}_rank{i}.csv" for i in range(world)]
            with open(out/f"{stem}_all.csv","w",encoding="utf-8",newline="") as f:
                for i,path in enumerate(files):
                    with open(path,encoding="utf-8") as src:
                        if i:next(src)
                        for line in src:f.write(line)
        print(f"Generated files: {out}/generated_all.csv, {out}/stats_all.csv")
    if world>1:dist.destroy_process_group()
if __name__=="__main__":main()
