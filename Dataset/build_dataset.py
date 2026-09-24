#!/usr/bin/env python3
"""Reproducible, deliberately synthetic Boolean query-expression candidate research corpus.
No network, database or third-party service is contacted."""
from __future__ import annotations
import csv, json, hashlib, re, pathlib, urllib.parse, collections, zipfile, shutil, datetime
from dataclasses import dataclass

BASE = pathlib.Path(__file__).resolve().parent
A = BASE / "A_GENERATOR_CORPUS"
B = BASE / "B_DETECTOR_CORPUS"
N = 20
TIERS = {
 "Y1_Simple":"direct predicate shape",
 "Y2_Variation":"same task with grouped/alternated surface arrangement",
 "Y3_Basic_Transformation":"one URL form encoding of representation; decoded field also stored",
 "Y4_Basic_Obfuscation":"dialect-dependent comment/JSON-escape or spacing variant; may only be formatting for some D"
}
DBS = [
("D1","PostgreSQL","SQL"),("D1","MySQL","SQL"),("D1","MariaDB","SQL"),
("D1","SQLite","SQL"),("D1","SQL Server","T-SQL"),("D1","Oracle","SQL"),
("D2","BigQuery","GoogleSQL"),("D2","Snowflake","SQL"),("D2","ClickHouse","SQL"),
("D2","DuckDB","SQL"),("D3","MongoDB","MQL/JSON"),("D3","Couchbase","SQL++"),
("D4","Redis","RediSearch query syntax (module required)"),
("D4","Cassandra","CQL"),("D4","DynamoDB","Condition/FilterExpression with values"),
("D5","Neo4j","Cypher"),("D5","Elasticsearch","JSON Query DSL"),
("D5","OpenSearch","JSON Query DSL")
]
# Twenty *abstract* shapes. They are not twenty distinct real-world exploits.
SHAPES = [
("num_eq","eq","number"),("num_ne","ne","number"),("num_gt","gt","number"),
("num_ge","ge","number"),("num_lt","lt","number"),("num_le","le","number"),
("num_between","between","number"),("num_not_between","not_between","number"),
("num_in","in","number"),("num_not_in","not_in","number"),
("tag_eq","eq","text"),("tag_ne","ne","text"),("tag_prefix","prefix","text"),
("tag_contains","contains","text"),("tag_in","in","text"),("tag_not_in","not_in","text"),
("and_score_tag","and","compound"),("or_score_tag","or","compound"),
("and_interval_prefix","and_interval_prefix","compound"),
("or_membership","or_membership","compound")
]
SOURCE_URLS = {
 "OWASP_SQLi_prevention":"https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
 "PortSwigger_dialect_variants":"https://portswigger.net/web-security/sql-injection/cheat-sheet",
 "MongoDB_comparisons":"https://www.mongodb.com/docs/v8.0/reference/mql/query-predicates/comparison/",
 "Elasticsearch_bool":"https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-bool-query",
 "OpenSearch_DSL":"https://docs.opensearch.org/latest/query-dsl/",
 "Redis_Search":"https://redis.io/docs/latest/develop/ai/search-and-query/administration/overview/",
 "DynamoDB_expressions":"https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ExpressionAttributeValues.html",
 "Neo4j_predicates":"https://neo4j.com/docs/cypher-manual/current/expressions/predicates/",
 "Couchbase_SQL++":"https://docs.couchbase.com/server/current/n1ql/n1ql-language-reference/index.html",
 "BigQuery_operators":"https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/operators"
}
def write_csv(path, rows, columns=None):
 path.parent.mkdir(parents=True,exist_ok=True)
 if columns is None:
  columns = list(rows[0]) if rows else []
 with path.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=columns,extrasaction="ignore");w.writeheader();w.writerows(rows)
def text_json(obj):
 return json.dumps(obj,ensure_ascii=False,separators=(",",":"),sort_keys=True)
def sha(text):
 return hashlib.sha256(text.encode('utf-8')).hexdigest()
def q(s): return "'"+str(s).replace("'","''")+"'"
def vals(d_i,r_i,i):
 # Disjoint between A vs B (i <20 / i>=20), with per-system values and linked abstract shape.
 n= 11 + d_i*701 + r_i*41 + i*13
 tag = ["alpha","beta","gamma","delta","active","verified","pending","public","member","stone"][i%10] + str(d_i+1) + "x" + str(n)
 return dict(n=n,m=n+3,tag=tag,alt=tag+"_alt",prefix=tag[:-1],
             sample_index=i,slot_signature=sha(f"{d_i}|{r_i}|{i}")[:14])
def atom(spec,v):
 name,op,typ=spec
 n,m,t=v["n"],v["m"],v["tag"]
 f="score" if typ=="number" else "tag"
 if op=="eq": return (op,f,n if typ=="number" else t,None)
 if op=="ne": return (op,f,n if typ=="number" else t,None)
 if op in ("gt","ge","lt","le"): return (op,f,n,None)
 if op in ("between","not_between"): return (op,f,n,m)
 if op in ("in","not_in"): return (op,f,n if typ=="number" else t,m if typ=="number" else v["alt"])
 if op in ("prefix","contains"): return (op,f,v["prefix"],None)
 if op=="and": return ("and",("gt","score",n,None),("eq","tag",t,None))
 if op=="or": return ("or",("eq","score",n,None),("ne","tag",t,None))
 if op=="and_interval_prefix": return ("and",("between","score",n,m),("prefix","tag",v["prefix"],None))
 if op=="or_membership": return ("or",("in","score",n,m),("in","tag",t,v["alt"]))
 raise ValueError(spec)
SQL_OP=dict(eq="=",ne="<>",gt=">",ge=">=",lt="<",le="<=")
def sql_render(a):
 op=a[0]
 if op in ("and","or"):
  return "("+sql_render(a[1])+" "+op.upper()+" "+sql_render(a[2])+")"
 _,f,x,y=a
 if op in SQL_OP:return f"{f} {SQL_OP[op]} {q(x) if isinstance(x,str) else x}"
 if op=="between":return f"{f} BETWEEN {x} AND {y}"
 if op=="not_between":return f"{f} NOT BETWEEN {x} AND {y}"
 if op in ("in","not_in"):
  vv= lambda k:q(k) if isinstance(k,str) else str(k)
  return f"{f} {'NOT IN' if op=='not_in' else 'IN'} ({vv(x)}, {vv(y)})"
 if op=="prefix":return f"{f} LIKE {q(x+'%')}"
 if op=="contains":return f"{f} LIKE {q('%'+x+'%')}"
 raise ValueError(a)
def cypher_render(a):
 op=a[0]
 if op in ("and","or"):return "("+cypher_render(a[1])+" "+op.upper()+" "+cypher_render(a[2])+")"
 _,f,x,y=a
 f="n."+f
 if op in SQL_OP:return f"{f} {SQL_OP[op]} {q(x) if isinstance(x,str) else x}"
 if op=="between":return f"({f} >= {x} AND {f} <= {y})"
 if op=="not_between":return f"NOT ({f} >= {x} AND {f} <= {y})"
 if op in ("in","not_in"):
  return f"{'NOT ' if op=='not_in' else ''}({f} IN [{q(x) if isinstance(x,str) else x}, {q(y) if isinstance(y,str) else y}])"
 if op=="prefix":return f"{f} STARTS WITH {q(x)}"
 if op=="contains":return f"{f} CONTAINS {q(x)}"
 raise ValueError(a)
def mongo_obj(a):
 op=a[0]
 if op in ("and","or"):return {"$"+op:[mongo_obj(a[1]),mongo_obj(a[2])]}
 _,f,x,y=a
 if op in SQL_OP:return {f:{"$"+{"ne":"ne","eq":"eq","gt":"gt","ge":"gte","lt":"lt","le":"lte"}[op]:x}}
 if op in ("between","not_between"):
  obj={f:{"$gte":x,"$lte":y}}
  return {"$nor":[obj]} if op=="not_between" else obj
 if op in ("in","not_in"):return {f:{"$nin" if op=="not_in" else "$in":[x,y]}}
 if op in ("prefix","contains"):return {f:{"$regex":("^" if op=="prefix" else "")+re.escape(x)}}
 raise ValueError(a)
def elastic_obj(a):
 op=a[0]
 if op=="and":return {"bool":{"filter":[elastic_obj(a[1]),elastic_obj(a[2])]}}
 if op=="or":return {"bool":{"should":[elastic_obj(a[1]),elastic_obj(a[2])],"minimum_should_match":1}}
 _,f,x,y=a
 if op=="eq":return {"term":{f:x}}
 if op=="ne":return {"bool":{"must_not":[{"term":{f:x}}]}}
 if op in ("gt","ge","lt","le"):return {"range":{f:{{"gt":"gt","ge":"gte","lt":"lt","le":"lte"}[op]:x}}}
 if op in ("between","not_between"):
  z={"range":{f:{"gte":x,"lte":y}}}
  return {"bool":{"must_not":[z]}} if op=="not_between" else z
 if op in ("in","not_in"):
  z={"terms":{f:[x,y]}}
  return {"bool":{"must_not":[z]}} if op=="not_in" else z
 if op=="prefix":return {"prefix":{f:x}}
 if op=="contains":return {"wildcard":{f:"*"+x+"*"}}
 raise ValueError(a)
def redi(a):
 # RediSearch index assumes @score NUMERIC and @tag TAG; exact behavior/index analyzer unvalidated.
 op=a[0]
 if op in ("and","or"):
  return "("+redi(a[1])+(" | " if op=="or" else " ")+redi(a[2])+")"
 _,f,x,y=a
 if f=="score":
  if op=="eq":return f"@score:[{x} {x}]"
  if op=="ne":return f"-@score:[{x} {x}]"
  if op=="gt":return f"@score:[({x} +inf]"
  if op=="ge":return f"@score:[{x} +inf]"
  if op=="lt":return f"@score:[-inf ({x}]"
  if op=="le":return f"@score:[-inf {x}]"
  if op in ("between","not_between"):
   s=f"@score:[{x} {y}]";return ("-"+s) if op=="not_between" else s
  if op in ("in","not_in"):
   s=f"(@score:[{x} {x}] | @score:[{y} {y}])";return "-"+s if op=="not_in" else s
 if f=="tag":
  if op in ("eq","ne","in","not_in"):
   s=f"@tag:{{{x}{'|'+str(y) if op in ('in','not_in') else ''}}}"
   return "-"+s if op in ("ne","not_in") else s
  if op in ("prefix","contains"):
   # Wildcard semantics require actual index definition; NOT guaranteed equivalent to string contains.
   return f"@tag:{{{x}*}}" if op=="prefix" else f"@tag:{{*{x}*}}"
 raise ValueError(a)
def dynamo_expr(a, bind):
 op=a[0]
 if op in ("and","or"):return "("+dynamo_expr(a[1],bind)+" "+op.upper()+" "+dynamo_expr(a[2],bind)+")"
 _,f,x,y=a
 def var(x):
  k=":v"+str(len(bind)+1)
  bind[k]= {"N":str(x)} if isinstance(x,int) else {"S":str(x)}
  return k
 if op in SQL_OP:return f"#{f} {SQL_OP[op]} {var(x)}"
 if op in ("between","not_between"):
  z=f"#{f} BETWEEN {var(x)} AND {var(y)}"
  return "NOT ("+z+")" if op=="not_between" else z
 if op in ("in","not_in"):
  z=f"#{f} IN ({var(x)}, {var(y)})"
  return "NOT ("+z+")" if op=="not_in" else z
 if op=="contains":return f"contains(#{f}, {var(x)})"
 if op=="prefix":
  # DynamoDB does not generally supply begins_with() in all condition contexts. Scope: filter-expression sketch.
  return f"begins_with(#{f}, {var(x)})"
 raise ValueError(a)
def cassandra_render(a):
 op=a[0]
 if op in ("or","not_between","not_in","prefix","contains","ne"):
  return None, "unsupported_or_not_equivalent_in_general_CQL"
 if op=="and":
  l,ls=cassandra_render(a[1]);r,rs=cassandra_render(a[2])
  if l is None or r is None:return None,"unsupported_component_CQL"
  return l+" AND "+r,"schema_index_and_allow_filtering_dependent"
 _,f,x,y=a
 if op in ("eq","gt","ge","lt","le"):return f+" "+SQL_OP[op]+" "+(q(x) if isinstance(x,str) else str(x)),"schema_index_dependent"
 if op=="between":return f"score >= {x} AND score <= {y}","schema_index_dependent"
 if op=="in":return f+" IN ("+ (q(x) if isinstance(x,str) else str(x))+", "+(q(y) if isinstance(y,str) else str(y))+")","schema_index_dependent"
 return None,"unsupported_CQL"
def render(db,a):
 d=db[1]
 bind={}
 if d=="MongoDB":return text_json(mongo_obj(a)),"MQL JSON query object",{}, "documentation_informed_not_engine_validated"
 if d in ("Elasticsearch","OpenSearch"):return text_json({"query":elastic_obj(a)}),"JSON Query DSL",{}, "documentation_informed_not_engine_validated"
 if d=="Redis":return redi(a),"RediSearch FT.SEARCH query argument; module/index required",{}, "not_engine_validated"
 if d=="DynamoDB":
  expr=dynamo_expr(a,bind)
  return text_json({"FilterExpression":expr,"ExpressionAttributeValues":bind,
  "ExpressionAttributeNames":{"#score":"score","#tag":"tag"}}), "DynamoDB JSON request representation with bindings", {"ExpressionAttributeValues":bind, "ExpressionAttributeNames":{"#score":"score","#tag":"tag"}}, "not_engine_validated"
 if d=="Cassandra":
  v,status=cassandra_render(a)
  return v if v else "", "CQL WHERE fragment; needs table schema", {}, status
 if d=="Neo4j":return cypher_render(a),"Cypher WHERE expression",{}, "documentation_informed_not_engine_validated"
 return sql_render(a),"SQL/SQL++ WHERE predicate fragment",{}, "documentation_informed_not_engine_validated"
def variation(s,di,k,dialect):
 if not s:return s
 if dialect in ("MQL/JSON","JSON Query DSL"):
  parsed=json.loads(s)
  return json.dumps(parsed,ensure_ascii=False,sort_keys=(k%2==0),indent=(2 if k%3==0 else None))
 if k%3==0: return "("+s+")"
 if k%3==1: return s.replace(" AND ","\nAND\n").replace(" OR ","\nOR\n")
 return s.replace(" = ","  =  ").replace(" > ","  >  ")
def obfuscate(s,di,k,dialect):
 if not s:return s,"unsupported"
 if dialect in ("MQL/JSON","JSON Query DSL"):
  # JSON escape $ in keys: decoded JSON key identity stays the same.
  escaped=s.replace("$","\\u0024")
  return escaped, "JSON_unicode_escape_key_only" if escaped!=s else "JSON_spacing_only"
 if dialect in ("SQL","T-SQL","GoogleSQL","SQL++"):
  s=s.replace(" AND ","/**/AND/**/").replace(" OR ","/**/OR/**/")
  s=s.replace(" BETWEEN ","/**/BETWEEN/**/").replace(" IN ","/**/IN/**/")
  if s.find("/**/")==-1:
   s=s.replace(" = ","/**/=/**/").replace(" > ","/**/>/**/").replace(" < ","/**/</**/")
  return s,"SQL_comment_lexical_variation" if "/**/" in s else "no_valid_comment_insertion"
 if dialect=="Cypher":
  return s.replace(" AND "," /*c*/ AND ").replace(" OR "," /*c*/ OR "), "Cypher_comment_variant"
 return ("  "+s+"  "), "whitespace_only_NOT_verified_obfuscation"
def make_payload(y,s,db,idx):
 dname=db[1];dialect=db[2]
 if y.startswith("Y1"):return s,s,"direct", "none"
 if y.startswith("Y2"):
  v=variation(s,db[0],idx,dialect);return v,s,"variation", "none"
 if y.startswith("Y3"):
  # HTTP form only: percent-encoded raw requires exactly one decode before DB parser.
  return urllib.parse.quote(s,safe=""),s,"single_percent_encoded","HTTP_form_percent_decode_once_REQUIRED"
 if y.startswith("Y4"):
  v, technique=obfuscate(s,db[0],idx,dialect)
  return v,s,technique,"engine/parser_specific_NOT_validated"
 raise ValueError(y)

SAMPLE_COLS = [
 "sample_id","arm","y_complexity","d_category","database","query_language",
 "root_id","abstract_family_id","structure_cell_id","grammar_slots_id",
 "sample_index","payload_raw","payload_decoded_or_canonical","query_binding_json",
 "abstract_predicate_ast","predicate_type","representation_technique",
 "compatibility_status","eligibility_for_detector_attack_training",
 "generated_source_type","external_observed","behavior_validated","provenance_source_id",
 "raw_sha256","semantic_lineage_id","split_group_key","notes"
]
def build_arm(arm, idxrange):
 everything=[]
 abstract_schema=[]
 if arm=="A": # 20 roots/tier; 18 structure cells per root per engine, 20 samples/cell
  for cat,db,language in DBS:pass
 for y in TIERS:
  roots=[];cells=[];slots=[];rows=[]
  for ri,spec in enumerate(SHAPES):
   root_id=f"{y[:2]}_R{ri+1:02d}"
   root={"root_id":root_id,"y_complexity":y,"abstract_family_id":f"AF_{ri+1:02d}",
         "grammar_signature":spec[0],"abstract_operator":spec[1],"abstract_operand_type":spec[2],
         "root_grammar_description":f"Boolean predicate {spec[0]} with typed score/tag slots; not an independent exploit mechanism",
         "syntax_template_sql_reference":sql_render(atom(spec,vals(0,ri,0))),
         "source_type":"synthetic_documentation_informed","independent_real_attack_observed":"false"}
   roots.append(root)
   for di,dbs in enumerate(DBS):
    cat,dname,lang=dbs
    cellid=f"{root_id}_D{di+1:02d}"
    cells.append({"structure_cell_id":cellid,"root_id":root_id,"complexity":y,
                  "database":dname,"query_language":lang,"d_category":cat,
                  "rendering_recipe":"dialect-specific documented predicate renderer plus Y tier",
                  "expected_samples":len(idxrange),"cross_db_semantic_equivalence":"NOT_CONFIRMED",
                  "execution_context":"none_Z1"})
    slots.append({"grammar_slots_id":cellid+"_SLOTS","structure_cell_id":cellid,
                  "slot_schema_json":text_json({"score":"integer","tag":"safe_ascii_token","n":"integer","m":"n+3","index":"20 per A cell or 15 per B cell"}),
                  "binding_requirement":"required for DynamoDB; all others are render-only",
                  "frozen_lineage":f"AF_{ri+1:02d}"})
    for i in idxrange:
     vv=vals(di,ri,i);ab=atom(spec,vv)
     base,kind,bindings,compat=render(dbs,ab)
     raw,canon,recipe,processing=make_payload(y,base,dbs,i)
     is_usable=bool(raw) and compat not in ("unsupported_or_not_equivalent_in_general_CQL","unsupported_component_CQL","unsupported_CQL")
     sampleid=f"{arm}_{y[:2]}_D{di+1:02d}_R{ri+1:02d}_V{i+1:02d}"
     rows.append(dict(sample_id=sampleid,arm=arm,y_complexity=y,d_category=cat,
       database=dname,query_language=lang,root_id=root_id,abstract_family_id=f"AF_{ri+1:02d}",
       structure_cell_id=cellid,grammar_slots_id=cellid+"_SLOTS",sample_index=i+1,
       payload_raw=raw,payload_decoded_or_canonical=canon,
       query_binding_json=text_json(bindings) if bindings else "",
       abstract_predicate_ast=text_json(ab),predicate_type=spec[0],
       representation_technique=recipe,compatibility_status=compat,
       eligibility_for_detector_attack_training="not_validated_attack" if is_usable else "exclude_unsupported",
       generated_source_type="synthetic_documentation_informed",external_observed="false",
       behavior_validated="false",provenance_source_id="SOURCES_PER_DIALECT_AND_ABSTRACT",
       raw_sha256=sha(raw) if raw else "",
       semantic_lineage_id=f"AF_{ri+1:02d}_D{di+1:02d}_R{ri+1:02d}",
       split_group_key=f"AF_{ri+1:02d}",notes=(kind+"; "+processing+"; "+("DO_NOT_TREAT_AS_CONFIRMED_SQLi" if is_usable else "NO_PAYLOAD_UNSUPPORTED"))))
  dest=(A if arm=="A" else B)/y
  write_csv(dest/"root_grammars.csv",roots)
  write_csv(dest/"structure_cells.csv",cells)
  write_csv(dest/"grammar_slots.csv",slots)
  write_csv(dest/"generated_samples.csv",rows,SAMPLE_COLS)
  # provenance sample-specific, not source claims
  prov=[{k:r[k] for k in ["sample_id","generated_source_type","database","compatibility_status","behavior_validated","raw_sha256","semantic_lineage_id"]} for r in rows]
  write_csv(dest/"validation_provenance.csv",prov)
  everything.extend(rows)
 return everything

def benign(i,hard):
 # These are DESIGNED controls, not observed field traffic or lab-confirmed benign for arbitrary app.
 base_hard=[
 "O'Reilly","AND / OR are logical operators","SELECT * FROM tutorial_table",
 "price > 10 AND stock < 20","SQL LIKE '%demo%'","error 404 and retry","comment /* greeting */",
 "WHERE status = active","user@example.com","how to learn SELECT and WHERE",
 "search?q=AND%20OR%20LIKE","JSON {\"$and\": [\"text\"]}","alice OR bob",
 "ID=0000 AND name=demo","order by date","support note: 1 = 1 is math",
 "SQL Server documentation","PostgreSQL tutorial","MongoDB $or syntax guide",
 "hello from Côte d'Azur","screenshot of CREATE TABLE","if x > 1 and y < 2",
 "SELECT is a music group","query optimizer explanation","ticket OR-1001"
 ]
 base_easy=[
 "hello there","invoice draft","customer name","2026-09-24","product catalog",
 "payment pending","return policy","shipping address","support ticket","weekly meeting",
 "user profile","blue sky","sample text","receipt number","books and authors",
 "learn database","hợp đồng tháng chín","café sữa đá","東京都","réservation"
 ]
 stock=base_hard if hard else base_easy
 d=DBS[i%18]
 repeat=i//18
 v=stock[repeat%len(stock)]
 suffix=f" #{repeat+1:05d} ref={repeat*17+4:06d}"
 # no claim this exact text has been observed or is safe in every conceivable SQL context
 return {"sample_id":("B_HARD_" if hard else "B_BENIGN_")+f"{i+1:04d}",
 "arm":"B","y_complexity":"","d_category":d[0],"database":d[1],
 "query_language":d[2],"root_id":"","abstract_family_id":"","structure_cell_id":"",
 "grammar_slots_id":"","sample_index":"","payload_raw":v+suffix,"payload_decoded_or_canonical":v+suffix,
 "query_binding_json":"","abstract_predicate_ast":"","predicate_type":"","representation_technique":"natural_like_or_sql_looking_benign",
 "compatibility_status":"not_app_lab_tested","eligibility_for_detector_attack_training":"designed_benign_control",
 "generated_source_type":"synthetic_hard_negative" if hard else "synthetic_benign",
 "external_observed":"false","behavior_validated":"false","provenance_source_id":"DESIGNED_CONTROLS",
 "raw_sha256":sha(v+suffix),"semantic_lineage_id":"NEG_"+str(repeat%len(stock)),
 "split_group_key":"NEG_"+str(repeat%len(stock)), "notes":"Synthetic designed benign; not proof of harmlessness for arbitrary application contexts.",
 "binary_label_provisional":0,"control_type":"hard_negative" if hard else "ordinary_benign"}
def generate():
 aa=build_arm("A",range(0,20))
 bb=build_arm("B",range(20,35))
 neg=[benign(i,False) for i in range(3000)]+[benign(i,True) for i in range(3000)]
 write_csv(B/"benign_and_hard_negatives.csv",neg)
 # Training view includes only supported candidate rows and controls and never marks candidates as confirmed attacks.
 det=[]
 for x in bb:
  if not x["payload_raw"]:continue
  det.append({"sample_id":x["sample_id"],"text":x["payload_raw"],
             "candidate_label_provisional":1 if x["payload_raw"] else "",
             "control_type":"candidate_not_validated","eligible":x["eligibility_for_detector_attack_training"],
             "dialect":x["database"],"tier":x["y_complexity"],"root_id":x["root_id"],
             "split_group_key":x["split_group_key"],"source_kind":"synthetic",
             "warning":"provisional candidate label is not ground truth for SQL injection"})
 for x in neg:
  det.append({"sample_id":x["sample_id"],"text":x["payload_raw"],"candidate_label_provisional":0,
             "control_type":x["control_type"],"eligible":"synthetic_control_only",
             "dialect":x["database"],"tier":"","root_id":"",
             "split_group_key":x["split_group_key"],"source_kind":x["generated_source_type"],
             "warning":"synthetic designed benign; validate on application/HTTP traces"})
 write_csv(B/"detector_training_VIEW_PROVISIONAL.csv",det)
 dialect_rows=[]
 for i,(cat,d,language) in enumerate(DBS):
  r=[x for x in aa if x["database"]==d]
  dialect_rows.append({"dialect_id":"D"+str(i+1).zfill(2),"category":cat,"database":d,"query_language":language,
      "A_rows":len(r),"A_nonempty_rendered":sum(bool(x["payload_raw"]) for x in r),
      "B_rows":sum(x["database"]==d for x in bb),
      "SQLi_ground_truth":"not_available","engine_executed":"false",
      "dependency":("RediSearch module and index" if d=="Redis" else "table/schema/index rules" if d=="Cassandra" else "bound expression values" if d=="DynamoDB" else "dialect-specific lab pending"),
      "supported_claim":"abstract rendering only; no universal grammar or exploit guarantee"})
 write_csv(BASE/"D_DIALECT_CATALOG.csv",dialect_rows)
 source_rows=[{"source_id":k,"URL":v,"observed_samples_copied":0,
 "used_for":"documentation-informed grammar and compatibility caveats; no scraped examples added",
 "license_status":"review source terms before redistribution"} for k,v in SOURCE_URLS.items()]
 write_csv(BASE/"SOURCE_CATALOG.csv",source_rows)
 rows=aa+bb+neg
 hashes=set(x["raw_sha256"] for x in aa+bb if x["raw_sha256"])
 unsupported=[x for x in aa+bb if not x["payload_raw"]]
 fromcollections=lambda rows,key:dict(collections.Counter(x[key] for x in rows))
 qc={"created_date_utc_date":"2026-09-24",
 "A_total_rows":len(aa),"B_total_rows":len(bb)+len(neg),
 "B_candidate_rows":len(bb),"B_control_rows":len(neg),"B_easy_controls":3000,"B_hard_negatives":3000,
 "combined_total_rows":len(rows),"A_roots":sum(1 for r in aa if r["sample_index"]==1 and r["database"]=="PostgreSQL"),
 "root_id_per_tier":20,"dialects":len(DBS),"A_samples_per_root_dialect":20,
 "B_samples_per_root_dialect":15,
 "synthetic_nonempty_payload_count":sum(bool(x["payload_raw"]) for x in aa+bb),
 "combined_nonempty_sample_count":sum(bool(x["payload_raw"]) for x in aa+bb)+len(neg),
 "unsupported_or_empty_rows":len(unsupported),
 "synthetic_distinct_raw_sha256":len(hashes),
 "synthetic_both_arms_shared_raw_sha256_count":len(set(x["raw_sha256"] for x in aa if x["raw_sha256"]) & set(x["raw_sha256"] for x in bb if x["raw_sha256"])),
 "A_per_y":fromcollections(aa,"y_complexity"),
 "B_candidates_per_y":fromcollections(bb,"y_complexity"),
 "unsupported_per_db":dict(collections.Counter(x["database"] for x in unsupported)),
 "warnings":["row count is not number of validated executable attacks","B/A have disjoint literal slot indices but share the SAME abstract grammar families",
             "some dialect renderings are unsupported, experimental or representation-only",
             "JSON snippets and safe DynamoDB placeholder expressions are NOT automatically injection payloads",
             "no real traffic, source-observed attack outcomes or external test labels have been added"]}
 (BASE/"QA_REPORT.json").write_text(json.dumps(qc,indent=2,ensure_ascii=False),encoding="utf-8")
 (BASE/"dataset_manifest.json").write_text(json.dumps({"title":"ABCD Boolean-style Z1 cross-dialect research pack",
    "A_count":len(aa),"B_count":len(bb)+len(neg),"total":len(rows),
    "tier_structure":"4x20 root IDs x18 target engines x (20 in A;15 in B) +6000 designed controls",
    "not_a_validated_attack_corpus":True,
    "required_review_before_detector_training":True},indent=2),encoding="utf-8")
 return qc
if __name__=="__main__":
 print(json.dumps(generate(),ensure_ascii=False,indent=2))
