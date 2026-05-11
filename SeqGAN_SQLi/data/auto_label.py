import pandas as pd

df = pd.read_csv("SeqGAN_SQLi/data/split_data.csv", dtype={"sqli_type": str, "db_engine": str})


def label_row(norm):
    n = norm.lower()
    ns = n.replace(" ", "")

    has_xmltype = "xmltype(" in ns
    has_extractvalue = "extractvalue(" in ns
    has_updatexml = "updatexml(" in ns
    has_ctxsys = "ctxsys" in ns
    has_floor_rand = "floor(rand(" in ns
    has_exp_tilde = "exp(~(" in ns
    has_convert_int = "convert(int," in ns
    has_error_func_name = "error(" in ns or "raise_error(" in ns
    has_utl_inaddr = "utl_inaddr" in ns
    has_error_func = has_xmltype or has_extractvalue or has_updatexml or has_ctxsys or has_floor_rand or has_exp_tilde or has_convert_int or has_error_func_name or has_utl_inaddr
    has_double_query = "if((" in ns and "select*from(selectconcat(" in ns
    has_error_func = has_error_func or has_double_query
    has_cast_error = ("cast(" in ns and "::text" in ns and "asnumeric" in ns)
    has_division_error = "1/(select0)" in ns or "1/0)" in ns or "1/0," in ns

    has_sleep = "sleep(" in ns
    has_pg_sleep = "pg_sleep" in ns
    has_dbms_pipe = "dbms_pipe" in ns
    has_waitfor = "waitfor" in ns
    has_benchmark = "benchmark(" in ns
    has_generate_series = "generate_series" in ns
    has_heavy_generic = ("regexp_substring" in ns or "randomblob" in ns or "crypt_key" in ns) and (
        "repeat(" in ns or "hex(" in ns
    ) and "error" not in ns and "xmltype" not in ns and "updatexml" not in ns and "extractvalue" not in ns
    has_heavy_domain = "domain." in ns and "count(*)" in ns

    has_union = "union" in ns and "select" in ns
    has_order_by = "order by" in n

    has_case_when = "case when" in n
    has_make_set = "make_set(" in ns
    has_elt = "elt(" in ns
    has_rlike = "rlike" in ns and "sleep(" not in ns
    has_from_dual = "from dual" in n
    has_char_plus = "char(" in ns and "+char(" in ns
    has_mssql_concat = "'+" in n or "+'" in n
    has_info_schema = "information_schema" in ns
    has_master_db = "master.." in ns

    if has_error_func or has_cast_error or has_division_error:
        if has_division_error:
            return ("error_based", "generic", 1.00)
        if has_xmltype or has_ctxsys:
            commented = False
            for comment in ["or--", "or #", "or#"]:
                if comment in n:
                    idx_comment = n.index(comment)
                    if idx_comment >= 0:
                        idx_xml = n.find("xmltype")
                        if idx_xml > idx_comment:
                            commented = True
                        idx_ctx = n.find("ctxsys")
                        if idx_ctx > idx_comment:
                            commented = True
            if commented:
                return ("error_based", "oracle", 0.70)
            if has_convert_int:
                return ("error_based", "oracle", 0.85)
            return ("error_based", "oracle", 1.00)
        if has_updatexml or has_floor_rand or has_exp_tilde or has_extractvalue:
            return ("error_based", "mysql", 1.00)
        if has_convert_int:
            return ("error_based", "mssql", 1.00)
        if has_cast_error:
            if "'+" in n or "+'" in n:
                return ("error_based", "generic", 0.70)
            return ("error_based", "postgresql", 1.00)
        return ("error_based", "generic", 1.00)

    if has_sleep or has_pg_sleep or has_dbms_pipe or has_waitfor or has_benchmark or has_generate_series or has_heavy_generic or has_heavy_domain:
        if has_pg_sleep or has_generate_series:
            return ("time_blind", "postgresql", 1.00)
        if has_dbms_pipe:
            return ("time_blind", "oracle", 1.00)
        if has_waitfor:
            return ("time_blind", "mssql", 1.00)
        if has_sleep or has_benchmark:
            return ("time_blind", "mysql", 1.00)
        if has_heavy_generic:
            if "crypt_key" in ns:
                return ("time_blind", "mysql", 0.85)
            return ("time_blind", "generic", 0.85)
        if has_heavy_domain:
            return ("time_blind", "generic", 0.85)
        return ("time_blind", "generic", 1.00)

    if has_union:
        if "#" in ns and "from dual" in n:
            return ("union_based", "generic", 0.85)
        if "#" in ns:
            return ("union_based", "mysql", 0.85)
        if "'+" in n or "+'" in n:
            return ("union_based", "generic", 0.85)
        if "char(" in ns:
            return ("union_based", "mssql", 1.00)
        return ("union_based", "generic", 1.00)

    if has_order_by:
        if "#" in ns:
            return ("union_based", "mysql", 0.70)
        return ("union_based", "generic", 0.70)

    if has_case_when:
        if has_master_db:
            return ("boolean_blind", "mssql", 1.00)
        if "mysql.db" in ns:
            return ("boolean_blind", "mysql", 1.00)
        if has_info_schema and "#" in ns:
            return ("boolean_blind", "mysql", 1.00)
        if has_from_dual:
            return ("boolean_blind", "oracle", 0.85)
        if has_rlike:
            return ("boolean_blind", "mysql", 0.85)
        if "regexp_substring" in ns:
            return ("boolean_blind", "generic", 0.85)
        if "#" in ns:
            return ("boolean_blind", "mysql", 0.85)
        return ("boolean_blind", "generic", 1.00)

    if has_make_set or has_elt:
        return ("boolean_blind", "mysql", 0.85)
    if has_rlike:
        return ("boolean_blind", "mysql", 0.85)
    if has_char_plus:
        return ("boolean_blind", "mssql", 0.85)
    if has_mssql_concat:
        return ("boolean_blind", "mssql", 0.85)
    if has_from_dual and "where" in n:
        return ("boolean_blind", "oracle", 0.85)
    if "or0=0" in ns or "or1=1" in ns:
        if "#" in ns:
            return ("boolean_blind", "mysql", 0.85)
        return ("boolean_blind", "generic", 1.00)

    return ("boolean_blind", "generic", 0.85)


results = []
for i, row in df.iterrows():
    t, e, c = label_row(row["payload_norm"])
    results.append({"id": i, "sqli_type": t, "db_engine": e, "confidence": c})

out = pd.DataFrame(results)

# Merge auto labels into split_data.csv
base = pd.read_csv("SeqGAN_SQLi/data/split_data.csv", dtype={"sqli_type": str, "db_engine": str})
base = base.merge(out, on="id", how="left", suffixes=("", "_new"))
base["sqli_type"] = base["sqli_type_new"].fillna("")
base["db_engine"] = base["db_engine_new"].fillna("")
base["confidence"] = base["confidence_new"].fillna(0.0)
base = base[["id", "payload_norm", "payload_delex", "sqli_type", "db_engine", "confidence"]]
base.to_csv("SeqGAN_SQLi/data/split_data_labeled.csv", index=False)

print("Auto-labeling complete!")
print(out["sqli_type"].value_counts())
print()
print(out["db_engine"].value_counts())
print()
print(out["confidence"].value_counts())

# Compare with manual labels for first 500 rows
manual = pd.concat([
    pd.read_csv(f"SeqGAN_SQLi/data/split_data_labeled_batch_{i}.csv") for i in range(1, 10)
], ignore_index=True)
merged = manual.merge(out, on="id", suffixes=("_manual", "_auto"))
agree = (merged["sqli_type_manual"] == merged["sqli_type_auto"]).sum()
total = len(merged)
print(f"\nManual vs Auto agreement (first 500 rows): {agree}/{total} = {agree/total*100:.1f}%")
