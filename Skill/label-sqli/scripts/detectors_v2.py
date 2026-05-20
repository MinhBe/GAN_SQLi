"""
detectors_v2.py -- State-aware SQLi detectors (v2).

Improvements over v1:
1. Unified patterns handle raw digits AND delex __TOKEN__ placeholders in one regex
2. Oracle error-based: utl_inaddr.get_host_address, ctxsys.drithsx, sys.all_tables fixed
3. Benign positive classifier (not just residual fallback)
4. Injection context detection works on delex payloads
5. All patterns work across raw, normalized, and delex states
"""

import re
import urllib.parse

# ---------------------------------------------------------------------------
# Regex fragments shared across pattern groups
# ---------------------------------------------------------------------------
# Numeric argument: raw digit OR delex TIME/INT/FLOAT token, inside possibly-spaced parens
_N   = r'(?:\d+|__(?:TIME|INT|FLOAT)__)'
# String value: single-quoted, double-quoted, or delex STR token
_S   = r"""(?:'[^']*'|"[^"]*"|__STR__)"""
# Left/right paren with optional surrounding spaces (handles normalized state)
_LP  = r'\s*\(\s*'
_RP  = r'\s*\)'
# Any identifier/placeholder
_ID  = r'(?:\w+|__IDENT__|__WORD__)'


def _p(pattern: str, flags: int = re.I) -> re.Pattern:
    return re.compile(pattern, flags)


# ===========================================================================
# HELPERS
# ===========================================================================

def _normalize(s: str) -> str:
    return re.sub(r'\s+', ' ', str(s).lower().strip())


def _strip_comments(s: str) -> str:
    p = re.sub(r'/\*.*?\*/', ' ', s, flags=re.DOTALL)
    p = re.sub(r'--[^\n]*', ' ', p)
    p = re.sub(r'#[^\n]*', ' ', p)
    return re.sub(r'\s+', ' ', p).strip()


def _try_url_decode(s: str) -> str:
    if '%' in s:
        try:
            return urllib.parse.unquote_plus(s)
        except Exception:
            pass
    return s


def _effective(payload: str) -> str:
    """Normalized + URL-decoded, preserving delex tokens."""
    return _normalize(_try_url_decode(str(payload)))


# ===========================================================================
# NORMALIZATION LAYER (#3) — decode obfuscation before detection
# ===========================================================================

def normalize_payload(payload: str) -> str:
    """
    Pre-normalize payload to strip encoding obfuscation BEFORE detection.
    Decodes: hex escapes (\\x27→'), unicode escapes (\\u0027→'), URL encoding (%27→').
    Preserves delex tokens (__STR__, __INT__, __TIME__) unchanged.
    URL encoding is also handled downstream by _effective() but doing it here
    ensures the string is clean before state detection.
    """
    p = str(payload)
    # Hex escape: \x27 → ' (common WAF bypass)
    p = re.sub(r'\\x([0-9a-fA-F]{2})',
               lambda m: chr(int(m.group(1), 16)), p)
    # Unicode escape: ' → '
    p = re.sub(r'\\u([0-9a-fA-F]{4})',
               lambda m: chr(int(m.group(1), 16)), p)
    # URL decode (%27 → ') — covers remaining %xx not caught by _effective later
    try:
        p = urllib.parse.unquote(p)
    except Exception:
        pass
    return p


# ===========================================================================
# INJECTION CONTEXT DETECTION (delex-aware)
# ===========================================================================

_CTX_PATTERNS = [
    # Classic: quote followed by SQL keyword
    _p(r"'[^']*(?:or|and|union|sleep|select|--|#)", re.I),
    # Delex: __STR__ or __INT__ followed by operator then SQL
    _p(r"__(?:STR|INT)__\s*(?:or|and|=)\s*(?:__(?:STR|INT)__|['\d])", re.I),
    # Comment at end of string (injection terminator)
    _p(r"(?:--|#|/\*)\s*$"),
    # OR/AND digit=digit (boolean injection)
    _p(r"(?:or|and)\s+" + _N + r"\s*=\s*" + _N, re.I),
    # Quote before semicolon + DML
    _p(r"'\s*;\s*(?:drop|select|insert|update|delete)", re.I),
    # Delex before semicolon + DML
    _p(r"__STR__\s*;\s*(?:drop|select|insert|update|delete)", re.I),
]


def has_injection_context(payload: str) -> bool:
    """True if payload looks like an injection value rather than standalone SQL."""
    p = str(payload)
    return any(pat.search(p) for pat in _CTX_PATTERNS)


# ===========================================================================
# TIER 1 — EXACT FUNCTION MATCH (confidence 0.90-1.00)
# ===========================================================================

# Each entry: (compiled_pattern, sqli_type, base_confidence, db_hint)
_TIER1_PATTERNS = [
    # --- time_blind ---
    (_p(r'\bsleep' + _LP + _N),               'time_blind',    0.95, 'mysql'),
    (_p(r'\bbenchmark' + _LP + _N),            'time_blind',    0.90, 'mysql'),
    (_p(r'\bpg_sleep' + _LP),                  'time_blind',    0.95, 'postgres'),
    (_p(r'\bwaitfor\s+delay\b'),               'time_blind',    0.95, 'mssql'),
    (_p(r'\bdbms_pipe\.receive_message' + _LP),'time_blind',    0.90, 'oracle'),
    (_p(r'\bdbms_lock\.sleep' + _LP),          'time_blind',    0.88, 'oracle'),
    (_p(r'\brandomblob' + _LP + _N),           'time_blind',    0.82, 'sqlite'),
    # --- union_based ---
    (_p(r'\bunion\s+all\s+select\b'),          'union_based',   0.95, None),
    (_p(r'\bunion\s+select\b'),                'union_based',   0.92, None),
    (_p(r'\bunion\s*/\*.*?\*/\s*select\b', re.I | re.DOTALL), 'union_based', 0.90, None),
    # MySQL file read (used in union/stacked injection)
    (_p(r'\bload_file' + _LP),                 'union_based',   0.82, 'mysql'),
    (_p(r'\binto\s+outfile\b'),                'union_based',   0.85, 'mysql'),
    # --- error_based MySQL ---
    (_p(r'\bextractvalue' + _LP),              'error_based',   0.95, 'mysql'),
    (_p(r'\bupdatexml' + _LP),                 'error_based',   0.95, 'mysql'),
    (_p(r'\bfloor\s*\(\s*rand\s*\('),          'error_based',   0.88, 'mysql'),
    (_p(r'\bexp\s*\(\s*~'),                    'error_based',   0.85, 'mysql'),
    (_p(r'\bgeometrycollection' + _LP),        'error_based',   0.80, 'mysql'),
    # --- error_based Oracle ---
    (_p(r'\bxmltype' + _LP),                   'error_based',   0.95, 'oracle'),
    (_p(r'\butl_inaddr\.get_host_address' + _LP), 'error_based', 0.95, 'oracle'),
    (_p(r'\butl_inaddr\.get_host_name' + _LP), 'error_based',  0.92, 'oracle'),
    (_p(r'\bctxsys\.drithsx\.sn' + _LP),       'error_based',   0.90, 'oracle'),
    (_p(r'\bctxsys\b'),                         'error_based',   0.80, 'oracle'),
    # --- error_based MSSQL ---
    (_p(r'\bconvert\s*\(\s*int\s*,'),          'error_based',   0.85, 'mssql'),
    (_p(r'\bcast\s*\(.+?\bas\s+int\b'),        'error_based',   0.82, 'mssql'),
    # --- error_based Postgres ---
    (_p(r'::\s*integer\b'),                     'error_based',   0.80, 'postgres'),
    # --- MSSQL hex dynamic SQL: DECLARE @s VARCHAR(N) SELECT @s = 0x... ---
    (_p(r'\bdeclare\s+@\w+\s+\w+\s*\(\s*\d+\s*\)\s+select\s+@\w+\s*=\s*0x', re.I),
     'time_blind', 0.90, 'mssql'),
    # --- Oracle execute immediate — string concatenation bypass ---
    (_p(r'\bexecute\s+immediate\b', re.I),      'error_based',   0.85, 'oracle'),
]


def tier1_score(payload: str) -> dict:
    """
    Try all Tier 1 exact-function patterns.

    Returns:
        {'sqli_type': str|None, 'db_hint': str|None,
         'confidence': float, 'matched_patterns': int}
    """
    p = _effective(normalize_payload(payload))
    best_type = None
    best_conf = 0.0
    best_db   = None
    count     = 0

    for pat, stype, base_conf, db_hint in _TIER1_PATTERNS:
        if pat.search(p):
            count += 1
            if base_conf > best_conf:
                best_conf = base_conf
                best_type = stype
                best_db   = db_hint

    # Bonus for multiple pattern hits (+0.02 per extra, capped at 1.0)
    if count > 1:
        best_conf = min(1.0, best_conf + (count - 1) * 0.02)

    return {
        'sqli_type':       best_type,
        'db_hint':         best_db,
        'confidence':      round(best_conf, 4),
        'matched_patterns': count,
    }


# ===========================================================================
# TIER 2 — STRUCTURAL PATTERNS (confidence 0.70-0.89)
# ===========================================================================

_TIER2_BOOL_PATTERNS = [
    (_p(r"'\s*(?:or|and)\s+" + _N + r"\s*=\s*" + _N),    0.88),   # ' OR 1=1
    (_p(r"\bor\s+" + _N + r"\s*=\s*" + _N),               0.85),   # OR 1=1
    (_p(r"\band\s+" + _N + r"\s*=\s*" + _N + r"\s*--"),   0.85),   # AND 1=2--
    # Classic: ' OR 'x'='y or ' OR 'x'='y' (closing quote optional — SQL provides it)
    (_p(r"'\s*(?:or|and)\s+'[^']*'\s*=\s*'"),             0.87),   # ' OR 'a'='a (unclosed ok)
    (_p(r"'\s*or\s+" + _S + r"\s*=\s*" + _S),             0.83),   # ' OR 'a'='a (full)
    # Delex variants: __STR__ = __STR__ with OR/AND
    (_p(r"(?:or|and)\s+__STR__\s*=\s*__STR__", re.I),     0.87),   # OR __STR__=__STR__
    (_p(r"(?:or|and)\s+__INT__\s*=\s*__INT__", re.I),      0.87),   # OR __INT__=__INT__
    # or ( 'a' = 'a  — parenthesized boolean, or without leading quote
    (_p(r"\bor\s*\(?\s*'[^']*'\s*=\s*'", re.I),            0.83),   # or ( 'a' = 'a
    (_p(r"\band\s*\(?\s*'[^']*'\s*=\s*'", re.I),           0.83),   # and ( 'a' = 'a
    (_p(r"\bsubstring" + _LP + r".+?" + _RP + r"\s*="),   0.78),   # substring(...)=
    (_p(r"\bmid" + _LP + r".+?" + _RP + r"\s*="),         0.75),   # mid(...)=
    (_p(r"\bascii\s*\(\s*(?:mid|substr|substring)"),       0.80),   # ascii(substr(
    (_p(r"\bord\s*\(\s*(?:mid|substr)"),                   0.80),   # ord(mid(
    (_p(r"\bif\s*\(.+?," + r"\s*.+?,\s*.+?" + _RP),       0.72),   # IF(cond, t, f)
    (_p(r"\bcase\s+when\s+.+?\bthen\b"),                   0.70),   # CASE WHEN...THEN
    # SQL boolean keywords (or true / or false)
    (_p(r'\bor\s+(?:true|false)\b', re.I),                 0.85),   # or true --
    (_p(r'\band\s+(?:true|false)\b', re.I),                0.82),   # and false --
    # Boolean subquery: or X in (select ...)
    (_p(r'\bor\s+\w+\s+in\s*\(\s*select\b', re.I),        0.88),   # or 1 in (select ...)
    (_p(r'\band\s+\w+\s+(?:not\s+)?in\s*\(\s*select\b', re.I), 0.85),  # and x not in (select ...)
]

_TIER2_UNION_PATTERNS = [
    (_p(r"\border\s+by\s+\d+\s*(?:--|#|/\*)"),            0.72),   # ORDER BY N--
    (_p(r"\bgroup\s+by\s+\d+\s+having"),                   0.75),   # GROUP BY N HAVING
    (_p(r"\bunion.{0,30}select\s+null\b"),                 0.82),   # UNION...SELECT NULL
    (_p(r"\bunion.{0,30}select\s+" + _N),                  0.78),   # UNION...SELECT 1
]

_TIER2_ERROR_PATTERNS = [
    (_p(r"\bselect\s+distinct\b.+\bfrom\s+\(" + r".*?" + r"\bwhere\s+rownum\b", re.I | re.DOTALL), 0.82),  # Oracle rownum subquery
    (_p(r"\bsys\.all_tables\b"),                           0.82),   # Oracle sys.all_tables
    (_p(r"\bsys\.user_tables\b"),                          0.80),   # Oracle user_tables
    (_p(r"\binformation_schema\.tables\b"),                0.72),   # MySQL info schema
    (_p(r"\bpg_catalog\b"),                                0.78),   # Postgres catalog
    (_p(r"\bsysobjects\b"),                                0.78),   # MSSQL sysobjects
    (_p(r"\bsqlite_master\b"),                             0.82),   # SQLite master
]

_TIER2_TIME_PATTERNS = [
    (_p(r"\bif\s*\(.+?(?:sleep|benchmark|pg_sleep)"),     0.82),   # IF(cond, sleep, ...)
    (_p(r"\bcase\s+when\s+.+?(?:sleep|waitfor)"),          0.82),   # CASE WHEN ... sleep
    (_p(r"\bxp_cmdshell\b"),                               0.88),   # MSSQL xp_cmdshell
]

_ALL_TIER2 = (
    [('boolean_blind', p, c) for p, c in _TIER2_BOOL_PATTERNS] +
    [('union_based',   p, c) for p, c in _TIER2_UNION_PATTERNS] +
    [('error_based',   p, c) for p, c in _TIER2_ERROR_PATTERNS] +
    [('time_blind',    p, c) for p, c in _TIER2_TIME_PATTERNS]
)


def tier2_score(payload: str) -> dict:
    """
    Structural pattern matching (Tier 2). No sqlparse needed.

    Returns:
        {'sqli_type': str|None, 'confidence': float, 'matched_patterns': int}
    """
    p = _effective(normalize_payload(payload))
    best_type = None
    best_conf = 0.0
    count     = 0

    for stype, pat, base_conf in _ALL_TIER2:
        if pat.search(p):
            count += 1
            if base_conf > best_conf:
                best_conf = base_conf
                best_type = stype

    if count > 1:
        best_conf = min(0.89, best_conf + (count - 1) * 0.01)

    return {
        'sqli_type':       best_type,
        'confidence':      round(best_conf, 4),
        'matched_patterns': count,
    }


# ===========================================================================
# DB ENGINE DETECTION (v2, state-aware)
# ===========================================================================

_DB_PATTERNS = {
    'mysql': [
        (_p(r'\bextractvalue' + _LP),   0.95),
        (_p(r'\bupdatexml' + _LP),      0.95),
        (_p(r'\bsleep' + _LP + _N),     0.88),
        (_p(r'\bbenchmark' + _LP),      0.90),
        (_p(r'\bgroup_concat' + _LP),   0.88),
        (_p(r'\bload_file' + _LP),      0.88),
        (_p(r'\binto\s+outfile\b'),      0.90),
        (_p(r'\belt' + _LP),            0.80),
        (_p(r'\bifnull' + _LP),         0.75),
        (_p(r'@@version\b'),             0.82),
        (_p(r'@@datadir\b'),             0.85),
        (_p(r'\binformation_schema\b'),  0.70),
        (_p(r'\bfloor\s*\(\s*rand'),     0.88),
        (_p(r'\bexp\s*\(\s*~'),          0.85),
    ],
    'postgres': [
        (_p(r'\bpg_sleep' + _LP),       0.98),
        (_p(r'\bpg_read_file' + _LP),   0.98),
        (_p(r'\bpg_ls_dir' + _LP),      0.98),
        (_p(r'\bcopy\s+\w+\s+to\b'),    0.88),
        (_p(r'::\s*integer\b'),          0.72),
        (_p(r'\bstring_agg' + _LP),     0.85),
        (_p(r'\barray_to_string' + _LP),0.85),
        (_p(r'\bpg_catalog\b'),          0.80),
        (_p(r'\\\$\\\$'),                0.75),
    ],
    'oracle': [
        (_p(r'\bxmltype' + _LP),                        0.98),
        (_p(r'\butl_inaddr\.get_host_address' + _LP),   0.98),
        (_p(r'\butl_inaddr\.get_host_name' + _LP),      0.95),
        (_p(r'\butl_http\b'),                            0.95),
        (_p(r'\butl_file\b'),                            0.92),
        (_p(r'\bdbms_pipe\b'),                           0.95),
        (_p(r'\bdbms_lock\b'),                           0.92),
        (_p(r'\bfrom\s+dual\b'),                         0.88),
        (_p(r'\brownum\b'),                              0.78),
        (_p(r'\bconnect\s+by\b'),                        0.78),
        (_p(r'\bsys\.all_tables\b'),                     0.82),
        (_p(r'\bsys\.user_tables\b'),                    0.80),
        (_p(r'\bctxsys\b'),                              0.82),
        (_p(r'\bv\$instance\b'),                         0.95),
    ],
    'mssql': [
        (_p(r'\bwaitfor\s+delay\b'),     0.98),
        (_p(r'\bxp_cmdshell\b'),         0.98),
        (_p(r'\bopenrowset' + _LP),      0.95),
        (_p(r'\bopendatasource' + _LP),  0.95),
        (_p(r'\bcharindex' + _LP),       0.78),
        (_p(r'\bstuff' + _LP),           0.78),
        (_p(r'\bsys\.objects\b'),        0.85),
        (_p(r'\bsys\.columns\b'),        0.85),
        (_p(r'@@servername\b'),           0.88),
        (_p(r'\bnchar' + _LP),           0.72),
        (_p(r'\bsysobjects\b'),          0.80),
    ],
    'sqlite': [
        (_p(r'\brandomblob' + _LP),      0.98),
        (_p(r'\bload_extension' + _LP),  0.98),
        (_p(r'\bsqlite_version' + _LP),  0.98),
        (_p(r'\bsqlite_master\b'),       0.95),
        (_p(r'\bsqlite_temp_master\b'),  0.95),
    ],
}


def detect_db_engine(payload: str) -> tuple:
    """
    Return (engine_name, confidence). ('unknown', 0.0) if nothing detected.
    """
    p = _effective(payload)
    best_engine = 'unknown'
    best_score  = 0.0

    for engine, patterns in _DB_PATTERNS.items():
        scores = [s for pat, s in patterns if pat.search(p)]
        if not scores:
            continue
        score = round(min(1.0, max(scores) * 0.92 + len(scores) * 0.015), 4)
        if score > best_score:
            best_score  = score
            best_engine = engine

    return best_engine, round(best_score, 4)


# ===========================================================================
# BENIGN POSITIVE CLASSIFIER
# ===========================================================================

_ATTACK_KWD = _p(
    r'\b(?:union|select|insert|update|delete|drop|truncate|sleep|waitfor|exec'
    r'|xp_|benchmark|extractvalue|updatexml|xmltype|utl_inaddr|ctxsys'
    r'|pg_sleep|randomblob|load_extension|openrowset)\b'
)

_INJECTION_CHARS = _p(r"[';]")  # strong injection markers

_CLEAN_INPUT_PATTERNS = [
    _p(r'^[\w\s@.\-+=:,]+$'),           # alphanumeric + common safe chars
    _p(r"^'[^']*'$"),                    # simple single-quoted string
    _p(r'^\d+(?:\.\d+)?$'),             # integer or float
    _p(r'^__(?:STR|INT|FLOAT)__$'),     # single delex token = clean value
]

# SQL tautology patterns generated by sqlmap — look benign but are boolean injection
_TAUTOLOGY_PATTERNS = [
    _p(r'(?:and|or)\s*\(\s*\d+\s*=\s*\d+\s*\)', re.I),    # AND ( 5452=6050 )
    _p(r'\*\d+\s+and\b', re.I),                             # *6050 AND
    _p(r'(?:and|or)\s*\(\s*\w+\s+like\s+\w+\s*\)', re.I),  # AND ( "x" LIKE "x" )
]


def score_benign(payload: str) -> float:
    """
    Positive benign classifier. Returns confidence 0.0-1.0.
    0.0 = definitely not benign (has attack signals).
    """
    p = str(payload).strip()
    pe = _effective(p)

    # Hard exclusions — cannot be benign
    if _ATTACK_KWD.search(pe):
        return 0.0
    if has_injection_context(p):
        return 0.0
    if any(pat.search(pe) for pat in _TAUTOLOGY_PATTERNS):
        return 0.0

    # Positive benign signals
    for pat in _CLEAN_INPUT_PATTERNS:
        if pat.match(p):
            return 0.88

    # Short, no SQL terminators → likely benign
    if len(pe) < 30 and not _INJECTION_CHARS.search(pe):
        return 0.75

    # Moderate length, no attack keywords, no injection context
    if len(pe) < 80 and not _INJECTION_CHARS.search(pe):
        return 0.62

    return 0.0


# ===========================================================================
# OBFUSCATION DETECTORS (unchanged from v1)
# ===========================================================================

def detect_comment_injection(payload: str) -> float:
    p = str(payload)
    score = 0.0
    if re.search(r'\w+\s*/\*[^*]*\*/\s*\w+', p):
        score = max(score, 0.85)
    if re.search(r'/\*!\d{5}', p):
        score = max(score, 0.90)
    if re.search(r'/\*\*/', p):
        score = max(score, 0.80)
    if len(re.findall(r'/\*.*?\*/', p)) >= 2:
        score = max(score, 0.75)
    return round(score, 4)


def detect_case_variation(payload: str) -> float:
    keywords = ['select', 'union', 'insert', 'update', 'delete', 'drop',
                'where', 'from', 'sleep', 'benchmark', 'waitfor']
    p = str(payload)
    score = 0.0
    for kw in keywords:
        pattern = re.compile(''.join(f'[{c.upper()}{c.lower()}]' for c in kw))
        for m in pattern.findall(p):
            if m != m.lower() and m != m.upper():
                ratio = sum(1 for c in m if c.isupper()) / len(m)
                if 0.1 < ratio < 0.9:
                    score = max(score, 0.80)
    return round(score, 4)


def detect_encoding_obfuscation(payload: str) -> float:
    p = _normalize(payload)
    score = 0.0
    if re.search(r'\b0x[0-9a-f]{4,}\b', p):
        score = max(score, 0.85)
    if re.search(r'\bchar\s*\(\s*\d+\s*(?:,\s*\d+\s*)*\)', p):
        score = max(score, 0.80)
    if re.search(r'\bunhex\s*\(', p):
        score = max(score, 0.85)
    if re.search(r'%[0-9a-f]{2}', str(payload).lower()):
        score = max(score, 0.60)
    return round(score, 4)


def is_complex_payload(t1: dict, t2: dict, threshold: float = 0.40) -> bool:
    """True if both Tier1 and Tier2 returned different sqli_types with decent confidence."""
    types = set()
    if t1.get('sqli_type') and t1.get('confidence', 0) >= threshold:
        types.add(t1['sqli_type'])
    if t2.get('sqli_type') and t2.get('confidence', 0) >= threshold:
        types.add(t2['sqli_type'])
    return len(types) >= 2


def get_sqli_types(t1: dict, t2: dict, threshold: float = 0.40) -> str:
    """
    Return pipe-separated list of all detected sqli_types above threshold.
    Used to populate the multi-label 'sqli_types' column in output schema.
    Example: 'union_based|boolean_blind'
    Returns '' if no types detected above threshold.
    """
    seen = {}
    for d in (t1, t2):
        stype = d.get('sqli_type')
        conf  = d.get('confidence', 0.0)
        if stype and conf >= threshold:
            seen[stype] = max(seen.get(stype, 0.0), conf)
    if not seen:
        return ''
    return '|'.join(k for k, _ in sorted(seen.items(), key=lambda x: -x[1]))


# ===========================================================================
# QUICK TEST
# ===========================================================================

if __name__ == '__main__':
    import sys, io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    tests = [
        ("admin' AND sleep(5)--",                          "time_blind mysql"),
        ("admin ' and sleep ( __TIME__ ) --",              "time_blind mysql delex"),
        ("admin ' and sleep ( __TIME__ ) -- (delex)",      "time_blind mysql delex"),
        ("' UNION SELECT NULL,NULL,NULL--",                "union_based"),
        ("' and extractvalue(1,concat(0x7e,version()))--", "error_based mysql"),
        ("' OR '1'='1",                                    "boolean_blind"),
        ("'; WAITFOR DELAY '0:0:5'--",                     "time_blind mssql"),
        ("' AND xmltype((select version from v$instance))--", "error_based oracle"),
        ("' AND utl_inaddr.get_host_address('x')--",       "error_based oracle"),
        ("__STR__ or __INT__ = __INT__ --",                "boolean_blind delex"),
        ("admin",                                           "benign"),
        ("1",                                              "benign"),
        ("__STR__",                                        "benign single token"),
        ("SELECT * FROM users WHERE id = 1",               "benign clean sql"),
    ]

    print(f"{'Payload':<55} {'Expected':<25} {'T1':<15} {'T1c':<6} {'T2':<15} {'T2c':<6} {'DB':<10} {'Benign'}")
    print("-" * 150)
    for payload, expected in tests:
        t1 = tier1_score(payload)
        t2 = tier2_score(payload)
        db, dbc = detect_db_engine(payload)
        bn = score_benign(payload)
        print(f"{payload:<55} {expected:<25} {str(t1['sqli_type']):<15} {t1['confidence']:<6.2f}"
              f" {str(t2['sqli_type']):<15} {t2['confidence']:<6.2f} {db:<10} {bn:.2f}")
