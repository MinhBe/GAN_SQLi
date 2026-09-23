from __future__ import annotations
import hashlib, random, json
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_recall_fscore_support, average_precision_score, matthews_corrcoef
from sklearn.metrics.pairwise import cosine_distances
import joblib


def ensure_dir(p):
    p=Path(p); p.mkdir(parents=True, exist_ok=True); return p


def canonicalize_text(x: str) -> str:
    return " ".join(str(x).strip().lower().split())


def stable_hash(x: str, prefix: str) -> str:
    return f"{prefix}_" + hashlib.sha256(str(x).encode('utf-8','ignore')).hexdigest()[:16]


def normalize_corpus(df: pd.DataFrame, text_col='payload', label_col='label', source_col='source', family_col='attack_family', lineage_col='lineage_id') -> pd.DataFrame:
    if text_col not in df or label_col not in df:
        raise ValueError(f"Need columns {text_col!r} and {label_col!r}")
    out=df.copy()
    for c,d in [(source_col,'unknown'),(family_col,'unknown'),(lineage_col,'')]:
        if c not in out: out[c]=d
    out['raw_payload']=out[text_col].astype(str)
    out['canonical_payload']=out['raw_payload'].map(canonicalize_text)
    out['payload_id']=out['canonical_payload'].map(lambda s: stable_hash(s,'p'))
    out[lineage_col]=out.apply(lambda r: r[lineage_col] if str(r[lineage_col]).strip() else stable_hash(r['canonical_payload'],'l'), axis=1)
    out[label_col]=out[label_col].astype(int)
    return out.drop_duplicates(['canonical_payload', label_col]).reset_index(drop=True)


@dataclass
class Splits:
    train: pd.DataFrame
    val: pd.DataFrame
    test_iid: pd.DataFrame
    test_unseen_lineage: pd.DataFrame


def make_splits(df, label_col='label', lineage_col='lineage_id', test_size=0.2, val_size=0.1, seed=42):
    rng=np.random.default_rng(seed)
    lins=np.array(sorted(df[lineage_col].astype(str).unique()))
    rng.shuffle(lins)
    n=max(1, int(len(lins)*test_size))
    hold=set(lins[:n])
    test_unseen=df[df[lineage_col].astype(str).isin(hold)].copy()
    pool=df[~df[lineage_col].astype(str).isin(hold)].copy()
    def _can_stratify(x, frac):
        if len(x) < 4 or x[label_col].nunique() < 2:
            return False
        counts = x[label_col].value_counts()
        n_test = max(1, int(round(len(x) * frac)))
        return counts.min() >= 2 and n_test >= x[label_col].nunique() and (len(x) - n_test) >= x[label_col].nunique()

    strat=pool[label_col] if _can_stratify(pool, test_size) else None
    train_val, test_iid=train_test_split(pool, test_size=test_size, random_state=seed, stratify=strat)
    strat2=train_val[label_col] if _can_stratify(train_val, val_size) else None
    if len(train_val) <= 1:
        train, val = train_val, train_val.iloc[0:0].copy()
    else:
        train, val=train_test_split(train_val, test_size=val_size, random_state=seed, stratify=strat2)
    return Splits(train.reset_index(drop=True), val.reset_index(drop=True), test_iid.reset_index(drop=True), test_unseen.reset_index(drop=True))


def build_d0(ngram_range=(3,5), max_features=50000, class_weight='balanced', max_iter=1000):
    return Pipeline([
        ('tfidf', TfidfVectorizer(analyzer='char', ngram_range=ngram_range, max_features=max_features, min_df=1)),
        ('clf', LogisticRegression(class_weight=class_weight, max_iter=max_iter)),
    ])


def eval_binary(model, df, text_col='raw_payload', label_col='label'):
    if len(df)==0: return {'n':0}
    y=df[label_col].astype(int).to_numpy()
    s=model.predict_proba(df[text_col].astype(str))[:,1]
    pred=(s>=0.5).astype(int)
    p,r,f,_=precision_recall_fscore_support(y,pred,average='binary',zero_division=0)
    return {'n':int(len(df)), 'precision':float(p), 'recall':float(r), 'f1':float(f), 'pr_auc':float(average_precision_score(y,s)) if len(set(y))>1 else None, 'mcc':float(matthews_corrcoef(y,pred)) if len(set(y))>1 else None}


def conservative_mutations(text, n=2, seed=42):
    # No hard-coded attack templates. Only transforms authorized corpus text.
    rng=random.Random(seed); rows=[]
    for _ in range(n):
        s=str(text)
        if rng.random()<0.5: s=' '.join(s.split())
        if rng.random()<0.5: s=''.join(ch.upper() if rng.random()<0.5 else ch.lower() for ch in s)
        rows.append(s)
    return rows


def novelty_against_train(candidates, train_texts):
    if len(candidates)==0: return np.array([])
    vec=TfidfVectorizer(analyzer='char', ngram_range=(3,5), min_df=1)
    all_texts=pd.concat([train_texts.astype(str), candidates.astype(str)], ignore_index=True)
    X=vec.fit_transform(all_texts)
    d=cosine_distances(X[len(train_texts):], X[:len(train_texts)])
    return d.min(axis=1)


def quality_gate(candidates, train, min_len=2, max_len=256):
    out=candidates.copy()
    out['canonical_candidate']=out['candidate_payload'].astype(str).map(canonicalize_text)
    out['q_len']=out['candidate_payload'].astype(str).str.len().between(min_len, max_len)
    out['q_non_duplicate']=~out.duplicated('canonical_candidate', keep='first')
    out['quality_pass']=out['q_len'] & out['q_non_duplicate']
    out['novelty']=novelty_against_train(out['candidate_payload'], train['raw_payload'])
    return out


def select_candidates(df, budget=100, seed=42):
    pool=df[df['quality_pass'].astype(bool)].copy()
    if len(pool)<=budget: return {'all':pool}
    return {
        'random': pool.sample(n=budget, random_state=seed),
        'novelty': pool.sort_values('novelty', ascending=False).head(budget),
    }


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
