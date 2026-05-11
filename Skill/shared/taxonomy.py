from dataclasses import dataclass


@dataclass
class SQLiType:
    priority: int
    name: str
    signals: list[str]


SQLI_TYPES = [
    SQLiType(1,  "rce",             ["xp_cmdshell", "certutil", "powershell -e", "/bin/bash", "cmd /c"]),
    SQLiType(2,  "out_of_band",     ["LOAD_FILE(", "UTL_HTTP", "UTL_INADDR", "xp_dirtree", "OPENROWSET"]),
    SQLiType(3,  "stacked_queries", ["; CREATE", "; DROP", "; INSERT", "; EXEC", "; SELECT"]),
    SQLiType(4,  "error_based",     ["EXTRACTVALUE(", "UPDATEXML(", "utl_inaddr.get_host_address", "ctxsys"]),
    SQLiType(5,  "time_blind",      ["SLEEP(", "pg_sleep(", "WAITFOR DELAY", "BENCHMARK(", "randomblob("]),
    SQLiType(6,  "heavy_query",     ["COUNT(*)"]),
    SQLiType(7,  "union_based",     ["UNION SELECT", "UNION ALL SELECT", "UNION (SELECT"]),
    SQLiType(8,  "boolean_blind",   ["AND 1=1", "OR 1=1", "AND 'a'='a'", "OR '1'='1'"]),
    SQLiType(9,  "auth_bypass",     ["admin' OR", "admin'--", "admin'#", "' OR '1'='1"]),
    SQLiType(10, "second_order",    ["INSERT INTO ... VALUES"]),
    SQLiType(11, "polyglot",        []),
    SQLiType(12, "lateral",         ["JOIN ... OR 1=1", "LATERAL JOIN"]),
    SQLiType(13, "benign",          []),
    SQLiType(14, "unknown",         []),
]

VALID_TYPES = {t.name for t in SQLI_TYPES}
VALID_DB = {"mysql", "mssql", "oracle", "postgresql", "sqlite", "firebird", "db2", "generic", "unknown"}
TYPE_PRIORITY = {t.name: t.priority for t in SQLI_TYPES}

NORMALIZE_MAP = {
    "boolean_based":      "boolean_blind",
    "stacked_query":      "stacked_queries",
    "ldap_injection":     "unknown",
    "command_injection":  "rce",
}

REQUIRED_REVIEW = {"generic", "comment_based", "inline_query"}
