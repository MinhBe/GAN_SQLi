from __future__ import annotations
import argparse, yaml, uuid, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pandas as pd
from gansqli.core import *
from gansqli.seqgan_starter import CharTokenizer, SeqGANStarter, SeqGANConfig


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',required=True); ap.add_argument('--input',required=True); ap.add_argument('--out',required=True); args=ap.parse_args()
    cfg=yaml.safe_load(Path(args.config).read_text(encoding='utf-8')); out=ensure_dir(args.out); seed=int(cfg['experiment']['seed'])
    df=normalize_corpus(pd.read_csv(args.input), text_col=cfg['data']['text_col'], label_col=cfg['data']['label_col'], source_col=cfg['data']['source_col'], family_col=cfg['data']['family_col'], lineage_col=cfg['data']['lineage_col'])
    splits=make_splits(df, label_col=cfg['data']['label_col'], lineage_col=cfg['data']['lineage_col'], test_size=cfg['data']['test_size'], val_size=cfg['data']['val_size'], seed=seed)
    split_dir=ensure_dir(out/'splits')
    for name, part in [('train',splits.train),('val',splits.val),('test_iid',splits.test_iid),('test_unseen_lineage',splits.test_unseen_lineage)]: part.to_csv(split_dir/f'{name}.csv', index=False)

    det=cfg['detector']; model=build_d0(tuple(det['ngram_range']), det['max_features'], det['class_weight'], det['max_iter']); model.fit(splits.train['raw_payload'], splits.train[cfg['data']['label_col']])
    metrics={'iid':eval_binary(model,splits.test_iid), 'unseen_lineage':eval_binary(model,splits.test_unseen_lineage)}
    ensure_dir(out/'baseline'); joblib.dump(model, out/'baseline/d0.joblib'); write_json(out/'baseline/metrics.json', metrics)

    # G1 conservative mutation
    rows=[]; pos=splits.train[splits.train[cfg['data']['label_col']].astype(int)==1]
    for i,row in pos.iterrows():
        for cand in conservative_mutations(row['raw_payload'], n=2, seed=seed+int(i)):
            rows.append({'candidate_id':'cand_'+uuid.uuid4().hex[:12], 'candidate_payload':cand, 'generator':'basic_mutation', 'parent_payload_id':row['payload_id'], 'expected_label':1})
    basic=pd.DataFrame(rows); ensure_dir(out/'candidates'); basic.to_csv(out/'candidates/basic_mutation.csv', index=False)

    # G2 SeqGAN starter
    sg=cfg['seqgan']; texts=pos['raw_payload'].astype(str).tolist()
    if len(texts)>=2:
        tok=CharTokenizer(max_len=sg['max_len']).fit(texts)
        seq=SeqGANStarter(tok, SeqGANConfig(max_len=sg['max_len'], embedding_dim=sg['embedding_dim'], hidden_dim=sg['hidden_dim'], batch_size=sg['batch_size'], mle_epochs=sg['mle_epochs'], adv_epochs=sg['adv_epochs'], temperature=sg['temperature']))
        hist=seq.fit(texts); gen=seq.generate(sg['generate_n'])
        seqdf=pd.DataFrame([{'candidate_id':'cand_'+uuid.uuid4().hex[:12], 'candidate_payload':g, 'generator':'seqgan_char', 'parent_payload_id':'', 'expected_label':1} for g in gen])
    else:
        hist={'error':'need at least 2 positive samples'}; seqdf=pd.DataFrame(columns=['candidate_id','candidate_payload','generator','parent_payload_id','expected_label'])
    seqdf.to_csv(out/'candidates/seqgan_char.csv', index=False); write_json(out/'candidates/seqgan_history.json', hist)

    # Quality + selection
    allcand=pd.concat([basic, seqdf], ignore_index=True)
    gated=quality_gate(allcand, splits.train, cfg['quality_gate']['min_len'], cfg['quality_gate']['max_len'])
    gated.to_csv(out/'candidates/candidates_gated.csv', index=False)
    sels=select_candidates(gated, budget=cfg['selection']['budget_per_selector'], seed=seed); sel_dir=ensure_dir(out/'selected')
    for name, sel in sels.items(): sel.to_csv(sel_dir/f'selected_{name}.csv', index=False)
    print('Done:', out); print(metrics)

if __name__=='__main__': main()
