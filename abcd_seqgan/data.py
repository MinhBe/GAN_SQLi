
import csv, io, json, zipfile
from collections import Counter
from pathlib import Path
import torch
from torch.utils.data import Dataset

SPECIAL = ["<PAD>", "<BOS>", "<EOS>", "<UNK>"]

def load_rows(path):
    path = Path(path)
    out = []
    if path.is_file() and path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as z:
            files = [n for n in z.namelist() if "/A_GENERATOR_CORPUS/" in n and n.endswith("/generated_samples.csv")]
            if len(files) != 4:
                raise ValueError(f"Expected four Corpus A generated_samples.csv, got {len(files)}")
            for name in sorted(files):
                out.extend(csv.DictReader(io.StringIO(z.read(name).decode("utf-8-sig"))))
    else:
        files = sorted(path.glob("**/A_GENERATOR_CORPUS/Y*/generated_samples.csv"))
        if not files:
            files = sorted(path.glob("A_GENERATOR_CORPUS/Y*/generated_samples.csv"))
        if len(files) != 4:
            raise ValueError(f"Expected four Corpus A CSVs under {path}; got {len(files)}")
        for name in files:
            with open(name, encoding="utf-8-sig", newline="") as f:
                out.extend(csv.DictReader(f))
    out = [r for r in out if r.get("payload_raw","").strip()
           and r.get("compatibility_status","").lower() != "unsupported"]
    if not out:
        raise ValueError("No eligible nonempty Corpus A samples")
    required = ("y_complexity","abstract_family_id","database","query_language","root_id","structure_cell_id")
    for col in required:
        if any(not r.get(col) for r in out):
            raise ValueError(f"Missing {col}")
    return out

FIELDS = ["y_complexity", "abstract_family_id", "database", "query_language", "root_id", "structure_cell_id"]
class Codec:
    def __init__(self, rows, max_len=0):
        chars = sorted(set("".join(r["payload_raw"] for r in rows)))
        self.itos = SPECIAL + chars
        self.stoi = {s:i for i,s in enumerate(self.itos)}
        self.fields = FIELDS
        self.maps = {f: {v:i+1 for i,v in enumerate(sorted({r[f] for r in rows}))} for f in FIELDS}
        self.max_len = max_len or max(len(r["payload_raw"]) for r in rows)+1
        if any(len(r["payload_raw"])+1 > self.max_len for r in rows):
            raise ValueError("max_len would truncate real samples; increase --max-len")
    def encode(self, s):
        return [self.stoi.get(c,3) for c in s]+[2]
    def decode(self, ids):
        chars=[]
        for i in ids:
            i=int(i)
            if i == 2: break
            if i >= len(SPECIAL) and i < len(self.itos): chars.append(self.itos[i])
        return "".join(chars)
    def condition(self,r):
        return [self.maps[f][r[f]] for f in self.fields]
    def save(self, path):
        Path(path).write_text(json.dumps({"itos":self.itos,"maps":self.maps,"max_len":self.max_len},ensure_ascii=False,indent=2))
    @classmethod
    def load(cls,path):
        obj=cls.__new__(cls)
        v=json.loads(Path(path).read_text())
        obj.itos=v["itos"];obj.stoi={s:i for i,s in enumerate(obj.itos)}
        obj.maps=v["maps"];obj.max_len=v["max_len"];obj.fields=FIELDS
        return obj

class Samples(Dataset):
    def __init__(self, rows, codec):
        self.rows=rows;self.codec=codec
    def __len__(self): return len(self.rows)
    def __getitem__(self,i):
        r=self.rows[i]; ids=self.codec.encode(r["payload_raw"])
        ids=ids+[0]*(self.codec.max_len-len(ids))
        return torch.tensor(ids,dtype=torch.long),torch.tensor(self.codec.condition(r),dtype=torch.long)
