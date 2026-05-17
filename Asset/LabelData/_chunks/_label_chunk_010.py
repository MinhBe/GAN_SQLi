"""Label chunk_010.csv -> chunk_010_labeled.csv.

Priority (lower = stronger):
  1 benign, 2 auth_bypass, 3 boolean_blind, 4 error_based/heavy_query,
  5 time_blind, 6 out_of_band, 7 union_based, 8 stacked_queries, 9 polyglot.

Rule: scan payload for evidence tokens; choose lowest-priority match.
DB engine: pick by exclusive signature, fallback to a_db/c_db consensus, else generic.
"""

import re
import pandas as pd

IN = r"C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_010.csv"
OUT = r"C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_010_labeled.csv"

VALID_TYPES = {"benign","error_based","boolean_blind","time_blind","union_based",
               "auth_bypass","heavy_query","out_of_band","stacked_queries","polyglot"}
VALID_DBS = {"oracle","mysql","postgresql","mssql","firebird","sqlite","db2","generic"}

PRI = {"benign":1,"auth_bypass":2,"boolean_blind":3,"error_based":4,"heavy_query":4,
       "time_blind":5,"out_of_band":6,"union_based":7,"stacked_queries":8,"polyglot":9}


def detect_db(p: str, a_db: str, c_db: str) -> str:
    pl = p.lower()
    # DB-exclusive signatures
    oracle = ["xmltype","utl_inaddr","dbms_pipe","dbms_lock","ctxsys","dual",
              "utl_http","rownum","all_tables","sys.user","sys.all"]
    mysql = ["extractvalue","updatexml","sleep(","benchmark(","information_schema",
             "elt(","rlike","load_file","mysql.user","unhex(","concat_ws"]
    postgres = ["pg_sleep","pg_database","string_agg","generate_series","::int","::text"]
    mssql = ["xp_cmdshell","waitfor delay","sysobjects","sysdatabases","master..","xp_dirtree"]
    fb = ["rdb$","gen_id"]
    sqlite = ["randomblob","sqlite_master"]
    db2_ = ["sysibm.systables","current schema","sysibm."]

    def hit(toks):
        return any(t in pl for t in toks)

    if hit(oracle): return "oracle"
    if hit(postgres): return "postgresql"
    if hit(mssql): return "mssql"
    if hit(mysql): return "mysql"
    if hit(sqlite): return "sqlite"
    if hit(fb): return "firebird"
    if hit(db2_): return "db2"
    # fallback consensus
    if a_db == c_db and a_db in VALID_DBS:
        return a_db
    if a_db in VALID_DBS and a_db != "generic":
        return a_db
    if c_db in VALID_DBS and c_db != "generic":
        return c_db
    return "generic"


# Regex evidence per type — returns list of (type, token) hits
def detect_types(p: str):
    pl = p.lower()
    hits = []  # (type, token quote, db_hint)

    # time_blind P5
    for tok in ["pg_sleep","sleep(","waitfor delay","waitfor  delay","benchmark(",
                "dbms_pipe.receive_message","dbms_lock.sleep","randomblob("]:
        if tok in pl:
            hits.append(("time_blind", tok))

    # error_based P4
    for tok in ["xmltype","extractvalue","updatexml","utl_inaddr.get_host_address",
                "ctxsys.drithsx","exp(~","ora-","convert(int","cast(0x"]:
        if tok in pl:
            hits.append(("error_based", tok))
    # cast(... as int) overflow
    if re.search(r"cast\s*\([^)]*as\s+int", pl):
        hits.append(("error_based","cast(.. as int)"))

    # out_of_band P6
    for tok in ["load_file(","utl_http.request","xp_dirtree","into outfile","into dumpfile"]:
        if tok in pl:
            hits.append(("out_of_band", tok))

    # stacked_queries P8
    if re.search(r";\s*(insert|update|delete|drop|exec|create|alter)\b", pl):
        hits.append(("stacked_queries","; <DML>"))
    if "xp_cmdshell" in pl:
        hits.append(("stacked_queries","xp_cmdshell"))

    # union_based P7
    if re.search(r"\bunion\s+(all\s+)?select\b", pl):
        m = re.search(r"\bunion\s+(all\s+)?select\b", pl).group(0)
        hits.append(("union_based", m))

    # heavy_query P4
    if "generate_series" in pl:
        hits.append(("heavy_query","generate_series"))
    if re.search(r"\brepeat\s*\(\s*[^,]+,\s*\d{6,}", pl):
        hits.append(("heavy_query","repeat(...,big_int)"))
    # 7+ digit integer (DoS-style)
    if re.search(r"\b\d{7,}\b", pl):
        hits.append(("heavy_query","7+digit int"))

    # auth_bypass P2 — admin context or classic OR '1'='1' login bypass
    if re.search(r"\badmin\b.*--", pl) or "admin'--" in pl or "admin' --" in pl or "admin'#" in pl:
        hits.append(("auth_bypass","admin'--"))
    # classic ' or '1'='1
    if re.search(r"'\s*or\s*'?1'?\s*=\s*'?1", pl):
        hits.append(("auth_bypass","' or '1'='1"))
    if re.search(r"\"\s*or\s*\"?1\"?\s*=\s*\"?1", pl):
        hits.append(("auth_bypass",'" or "1"="1'))

    # boolean_blind P3
    for tok in [" and 1=1"," and 1=2"," or 1=1"," or 1=2","rlike","elt("]:
        if tok in pl:
            hits.append(("boolean_blind", tok.strip()))
    if re.search(r"\b(and|or)\s+\d+\s*=\s*\d+\b", pl):
        m = re.search(r"\b(and|or)\s+\d+\s*=\s*\d+\b", pl).group(0)
        hits.append(("boolean_blind", m))
    if re.search(r"\b(and|or)\s+\d+\s*[<>!]=?\s*\d+\b", pl):
        m = re.search(r"\b(and|or)\s+\d+\s*[<>!]=?\s*\d+\b", pl).group(0)
        hits.append(("boolean_blind", m))
    if re.search(r"\bcase\s+when\b", pl):
        hits.append(("boolean_blind","case when"))
    if re.search(r"\bif\s*\(", pl):
        hits.append(("boolean_blind","if(...)"))

    # polyglot P9 — XSS+SQLi
    if "<script" in pl or "onerror=" in pl or "alert(" in pl:
        hits.append(("polyglot","<script/alert"))

    return hits


def label(payload: str, a_type: str, c_type: str, a_db: str, c_db: str):
    if not isinstance(payload, str):
        payload = ""
    p = payload.strip()
    if not p:
        return "benign","generic",0.5,"UNCERTAIN: empty payload after strip; no tokens to evaluate, defaulting benign/generic.","UNCERTAIN"

    hits = detect_types(p)
    db = detect_db(p, a_db or "", c_db or "")

    if not hits:
        # benign? only if no SQLi metacharacter and looks like normal SQL or word
        has_meta = bool(re.search(r"['\"]\s*(or|and|union|;|--|#)", p.lower())) or "--" in p or "/*" in p
        if not has_meta and len(p) < 80:
            return ("benign", db, 0.7,
                    f"No SQLi tokens detected in payload; no quote-break / boolean / union / time / error indicators. Snippet: '{p[:60]}'",
                    None)
        # has meta but no specific hit → uncertain boolean_blind fallback
        return ("boolean_blind", db, 0.5,
                f"UNCERTAIN: payload contains SQL meta but no specific high-priority token matched; tentative boolean_blind. Snippet='{p[:80]}'",
                "UNCERTAIN")

    # pick lowest priority
    hits_sorted = sorted(hits, key=lambda x: PRI[x[0]])
    chosen_type = hits_sorted[0][0]
    # collect tokens for reasoning (top 3 for chosen + neighbors)
    chosen_tokens = [t for ty,t in hits if ty == chosen_type]
    other_tokens = [(ty,t) for ty,t in hits if ty != chosen_type][:2]

    # build reasoning >= 50 chars, quoting tokens
    tk = ", ".join(f"'{t}'" for t in chosen_tokens[:3])
    rationale = f"Matched {chosen_type} (P{PRI[chosen_type]}) via token(s) {tk} in payload"
    if other_tokens:
        ot = "; also saw " + ", ".join(f"{ty}:'{t}'" for ty,t in other_tokens) + f" but {chosen_type} has lower priority (stronger signal)"
        rationale += ot
    rationale += f". DB={db}."
    if len(rationale) < 50:
        rationale += f" Payload snippet: '{p[:60]}'"

    # confidence
    n_distinct = len(set(ty for ty,_ in hits))
    if len(chosen_tokens) >= 2 and n_distinct == 1:
        conf = 0.95
    elif len(chosen_tokens) >= 1 and (a_type == chosen_type or c_type == chosen_type):
        conf = 0.9
    elif len(chosen_tokens) >= 1:
        conf = 0.8
    else:
        conf = 0.7
    return chosen_type, db, conf, rationale, None


def main():
    df = pd.read_csv(IN)
    rows = []
    for _, r in df.iterrows():
        rid = r["id"]
        payload = r["payload_inner"] if isinstance(r.get("payload_inner"), str) and r.get("payload_inner") else r.get("payload_norm","")
        a_t = str(r.get("a_type","") or "")
        c_t = str(r.get("c_type","") or "")
        a_d = str(r.get("a_db","") or "")
        c_d = str(r.get("c_db","") or "")
        t, db, conf, reasoning, flag = label(payload, a_t, c_t, a_d, c_d)
        if t not in VALID_TYPES:
            t = "boolean_blind"
        if db not in VALID_DBS:
            db = "generic"
        # confidence clamp
        if flag == "UNCERTAIN":
            conf = 0.5
            if not reasoning.startswith("UNCERTAIN:"):
                reasoning = "UNCERTAIN: " + reasoning
        conf = max(0.5, min(1.0, float(conf)))

        # sources_agree
        if conf < 0.5:
            sa = 0
        else:
            match_a = (t == a_t)
            match_c = (t == c_t)
            if match_a and match_c:
                sa = 3
            elif match_a or match_c:
                sa = 2
            else:
                sa = 1

        # ensure reasoning length >= 50
        if len(reasoning) < 50:
            reasoning = reasoning + f" | extra: payload='{str(payload)[:50]}'"
        rows.append({
            "id": rid,
            "payload_inner": payload,
            "sqli_type": t,
            "db_engine": db,
            "confidence": round(conf, 2),
            "reasoning": reasoning,
            "sources_agree": sa,
        })

    out = pd.DataFrame(rows, columns=["id","payload_inner","sqli_type","db_engine","confidence","reasoning","sources_agree"])
    out.to_csv(OUT, index=False)

    print("ROWS:", len(out))
    print("TYPE DIST:")
    print(out["sqli_type"].value_counts())
    print("conf<0.7:", int((out["confidence"] < 0.7).sum()))
    print("reasoning<50:", int(out["reasoning"].str.len().lt(50).sum()))
    print("sources_agree dist:")
    print(out["sources_agree"].value_counts())


if __name__ == "__main__":
    main()
