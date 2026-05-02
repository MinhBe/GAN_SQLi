"""
Classifier — Phân loại payload SQLi.
Lớp 1: Rule-based pattern matching (ưu tiên cao).
Lớp 2: ML fallback (cho payload rule không match).
"""
import re
import sys
from typing import Dict, List, Any, Tuple

sys.stdout.reconfigure(encoding='utf-8')
from config import SQLI_TYPES, DB_ENGINES, EVASION_TECHS


RULE_PATTERNS = {
    "union_based": [
        r"(?i)\bUNION\b.*\bSELECT\b",
        r"(?i)\bUNION\b.*\bALL\b.*\bSELECT\b",
        r"(?i)\bORDER\s+BY\b\s+\d+",
    ],
    "error_based": [
        r"(?i)\bEXTRACTVALUE\s*\(",
        r"(?i)\bUPDATEXML\s*\(",
        r"(?i)\bXMLTYPE\s*\(",
        r"(?i)\bctxsys\.drithsx\.sn\s*\(",
        r"(?i)\butl_inaddr\.get_host_address\s*\(",
        r"(?i)\bdbms_utility\.sqlid_to_sqlhash\s*\(",
        r"(?i)\bCONVERT\s*\(\s*int\s*,",
        r"(?i)\bCAST\s*\([^)]*AS\s+(?:int|numeric)\s*\)",
        r"(?i)\bctxsys\.drithsx\.sn",
        r"(?i)\bchar\s*\(\s*113\s*\)\s*\+\s*char\s*\(\s*113\s*\)",
        r"(?i)\bchr\s*\(\s*113\s*\)\s*\|\|",
        r"(?i)\bchr\s*\(\s*113\s*\)",
        r"(?i)\bchar\s*\(\s*113\s*\)",
        r"(?i)\bchar\s*\(\s*49\s*\)\s*\)\s*\+\s*char\s*\(\s*48\s*\)",
    ],
    "boolean_blind": [
        r"(?i)\bAND\s+\d+\s*=\s*\d+",
        r"(?i)\bOR\s+\d+\s*=\s*\d+",
        r"(?i)\bAND\s+'[^']*'\s*(?:=|LIKE)\s*'[^']*'",
        r"(?i)\bOR\s+'[^']*'\s*(?:=|LIKE)\s*'[^']*'",
        r"(?i)\bASCII\s*\(\s*SUBSTRING",
        r"(?i)\bSUBSTRING\s*\(.*\)\s*=",
        r"(?i)\bCASE\s+WHEN\s+.*\s+THEN\s+1\s+ELSE\s+0\s+END",
        r"(?i)\bMID\s*\(",
        r"(?i)\bASCII\s*\(",
        r"(?i)'\s*=\s*'[a-z]+'",
        r"(?i)'\s+LIKE\s+'[a-z]+'",
        r"(?i)\bwhere\s+\d+\s*=\s*\d+",
        r"(?i)\bas\s+[a-z]+\s+where\s+\d+\s*=\s*\d+",
        r"(?i)\)\s*or\s+\(\s*'",
        r"(?i)'\s*and\s+'[a-z]+'\s*=\s*'[a-z]+'",
        r"(?i)'\s*or\s+'[a-z]+'\s*=\s*'[a-z]+'",
        r"(?i)\)\s*or\s+\d+\s*=\s*\d+",
        r"(?i)\)\s*and\s+\d+\s*=\s*\d+",
    ],
    "time_blind": [
        r"(?i)\bSLEEP\s*\(\s*\d+\s*\)",
        r"(?i)\bIF\s*\(.*,\s*SLEEP\s*\(",
        r"(?i)\bWAITFOR\s+DELAY\s+",
        r"(?i)\bpg_sleep\s*\(\s*\d+\s*\)",
        r"(?i)\bdbms_pipe\.receive_message\s*\(",
        r"(?i)\bBENCHMARK\s*\(",
        r"(?i)\brandomblob\s*\(",
    ],
    "heavy_query": [
        r"(?i)\bCOUNT\s*\(\s*\*\s*\)\s*FROM\s+\S+\s+\w+\s*,\s*\S+\s+\w+\s*,\s*\S+\s+\w+",
        r"(?i)\bgenerate_series\s*\(",
        r"(?i)(?:SELECT\s+\d+\s+FROM\s+\S+){3,}",
    ],
    "out_of_band": [
        r"(?i)\bLOAD_FILE\s*\(",
        r"(?i)\bxp_dirtree\s",
        r"(?i)\bxp_cmdshell\s",
        r"(?i)\bUTL_HTTP\.request\s*\(",
        r"(?i)\bCOPY\s+.*\bTO\s+PROGRAM\b",
        r"(?i)\bOPENROWSET\s*\(",
        r"(?i)(?:nslookup|attacker\.com|\.com\\\\a)",
    ],
    "stacked_queries": [
        r";\s*(?:DROP|INSERT|UPDATE|DELETE|EXEC|CREATE|ALTER|GRANT)\b",
        r";\s*\bSELECT\b",
        r";\s*RECONFIGURE",
    ],
    "second_order": [
        r"(?i)INSERT\s+INTO.*VALUES.*(?:--|#|')",
        r"(?i)UPDATE\s+\w+\s+SET.*(?:--|#|')",
    ],
    "auth_bypass": [
        r"(?i)'\s*OR\s+'[^']*'\s*=\s*'[^']*'",
        r"(?i)'\s*OR\s+1\s*=\s*1",
        r"(?i)'\s*OR\s*'\d+'\s*=\s*'\d+'",
        r"(?i)admin'\s*(?:--|#)",
        r"(?i)'\s*OR\s*''\s*=\s*'",
        r"(?i)\bOR\s+1\s*=\s*1\s*(?:--|#)",
    ],
    "lateral": [
        r"(?i)\bJOIN\b.*\bON\b",
        r"(?i)\bUNION\b.*\bJOIN\b",
    ],
    "data_exfil": [
        r"(?i)\bINTO\s+OUTFILE\b",
        r"(?i)\bINTO\s+DUMPFILE\b",
        r"(?i)\bLOAD_FILE\s*\(",
        r"(?i)\bpg_read_file\s*\(",
        r"(?i)\blo_import\s*\(",
        r"(?i)\blo_get\s*\(",
    ],
    "rce": [
        r"(?i)\bxp_cmdshell\s",
        r"(?i)\bEXEC\s+.*system\s*\(",
        r"(?i)\bCREATE\s+.*\bFUNCTION\b.*\bsystem\b",
        r"(?i)\bcertutil\s",
        r"(?i)\bCOMMAND\b.*EXEC",
    ],
    "polyglot": [
        r"(?i)SLEEP\s*\(.*\)\s*/\*.*OR.*SLEEP",
        r"(?i)['\"].*OR.*SLEEP.*['\"].*OR.*SLEEP",
    ],
}

DB_PATTERNS = {
    "mysql": [
        r"(?i)\bSLEEP\s*\(",
        r"(?i)\bBENCHMARK\s*\(",
        r"(?i)\bLOAD_FILE\s*\(",
        r"(?i)\bINTO\s+OUTFILE\b",
        r"(?i)\bINTO\s+DUMPFILE\b",
        r"(?i)\bGROUP_CONCAT\b",
        r"(?i)\\x[0-9a-fA-F]{2,}",
        r"(?i)\bEXTRACTVALUE\s*\(",
        r"(?i)\bUPDATEXML\s*\(",
        r"(?i)/\*!\d+",
        r"(?i)\bMID\s*\(",
    ],
    "mssql": [
        r"(?i)\bWAITFOR\s+DELAY\b",
        r"(?i)\bxp_cmdshell\b",
        r"(?i)\bxp_dirtree\b",
        r"(?i)\bOPENROWSET\b",
        r"(?i)\bCONVERT\s*\(\s*int",
        r"(?i)\bSTRING_AGG\b",
        r"(?i)\@\@version",
        r"(?i)\bsys\.tables\b",
        r"(?i)\bsys\.columns\b",
    ],
    "oracle": [
        r"(?i)\bctxsys\.drithsx\.sn\b",
        r"(?i)\butl_inaddr\b",
        r"(?i)\bdbms_pipe\b",
        r"(?i)\bUTL_HTTP\b",
        r"(?i)\bdual\b",
        r"(?i)\bXMLTYPE\s*\(",
        r"(?i)\bdbms_utility\b",
        r"(?i)\bv\$version\b",
        r"(?i)\blistagg\b",
    ],
    "postgresql": [
        r"(?i)\bpg_sleep\s*\(",
        r"(?i)\bpg_read_file\b",
        r"(?i)\bgenerate_series\b",
        r"(?i)\blo_import\b",
        r"(?i)\blo_get\b",
        r"(?i)\bchr\s*\(",
        r"(?i)\bstring_agg\b",
        r"(?i)\bCOPY\s+.*\bTO\s+PROGRAM\b",
    ],
    "sqlite": [
        r"(?i)\bsqlite_version\s*\(",
        r"(?i)\bsqlite_master\b",
        r"(?i)\bATTACH\s+DATABASE\b",
        r"(?i)\brandomblob\s*\(",
    ],
    "nosql": [
        r"(?i)\\$gt\b",
        r"(?i)\$regex\b",
        r"(?i)\$ne\b",
        r"(?i)\$where\b",
    ],
}

EVASION_PATTERNS = {
    "url_encoding": [r"%27", r"%20", r"%28", r"%29", r"%3D", r"%22", r"%3A", r"%5C", r"%09", r"%0a"],
    "double_url_encoding": [r"%2527", r"%2520", r"%253D", r"%2522"],
    "unicode_encoding": [r"%u0027", r"%uff07", r"%uff08", r"%uff09"],
    "html_entity": [r"&apos;", r"&quot;", r"&amp;", r"&lt;", r"&gt;"],
    "case_variation": [r"(?i)[Ss][Ee][Ll][Ee][Cc][Tt]", r"(?i)[Uu][Nn][Ii][Oo][Nn]"],
    "comment_whitespace": [r"/\*\*/", r"/\*[^*]*\*/", r"%09", r"%0a"],
    "inline_comment": [r"/\*.*?\*/"],
    "keyword_obfuscation": [r"(?i)(?:SELEC%54|UNION%20SELECT)"],
    "function_alternative": [r"(?i)(?:MID|SUBSTR|LEFT|RIGHT)\s*\(", r"(?i)(?:LIKE|REGEXP)\s+['\"]"],
    "hex_string": [r"0x[0-9a-fA-F]{4,}"],
    "scientific_notation": [r"\d+e\d+", r"\d+E\d+"],
    "null_byte": [r"%00", r"\x00"],
}

CONTEXT_PATTERNS = {
    "string_single_quote": r"'\s*(?:OR|AND|--|#)",
    "string_double_quote": r'"\s*(?:OR|AND|--|#)',
    "numeric": r"\b\d+\s*(?:OR|AND)",
    "like_clause": r"(?i)LIKE\s+'%",
    "order_by": r"(?i)ORDER\s+BY\s+",
    "in_clause": r"(?i)\bIN\s*\(",
    "insert": r"(?i)\bINSERT\s+INTO\b",
    "update": r"(?i)\bUPDATE\s+\w+\s+SET\b",
}


def classify_sqli_type(payload: str) -> Tuple[str, float]:
    """Phân loại payload theo SQLi type. Trả về (type, confidence)."""
    matches = []

    for sqli_type, patterns in RULE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, payload):
                matches.append(sqli_type)
                break

    if not matches:
        return "unknown", 0.0

    if len(matches) == 1:
        return matches[0], 0.8

    priority_order = [
        "rce", "polyglot", "out_of_band", "stacked_queries",
        "error_based", "union_based", "time_blind", "boolean_blind",
        "heavy_query", "auth_bypass", "data_exfil", "lateral",
        "second_order",
    ]
    for ptype in priority_order:
        if ptype in matches:
            return ptype, 0.7

    return matches[0], 0.5


def classify_db_engine(payload: str) -> Tuple[str, float]:
    """Phân loại DB engine từ payload."""
    scores = {}
    for db, patterns in DB_PATTERNS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, payload):
                score += 1
        if score > 0:
            scores[db] = score

    if not scores:
        return "unknown", 0.0

    best_db = max(scores, key=scores.get)
    max_score = scores[best_db]
    total_possible = len(DB_PATTERNS[best_db])
    confidence = min(max_score / total_possible, 1.0)

    return best_db, confidence


def detect_evasion_techniques(payload: str) -> List[str]:
    """Phát hiện các kỹ thuật evasion trong payload."""
    detected = []
    for tech, patterns in EVASION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, payload):
                detected.append(tech)
                break
    return detected


def detect_context(payload: str) -> str:
    """Phát hiện ngữ cảnh injection."""
    for ctx, pattern in CONTEXT_PATTERNS.items():
        if re.search(pattern, payload):
            return ctx
    return "unknown"


def classify_sample(sample: Dict[str, Any]) -> Dict[str, Any]:
    """Phân loại một sample hoàn chỉnh."""
    payload = sample["payload"]
    inferred_raw = sample.get("raw", {})

    sqli_type, type_conf = classify_sqli_type(payload)
    db_engine, db_conf = classify_db_engine(payload)
    evasion = detect_evasion_techniques(payload)
    context = detect_context(payload)

    if inferred_raw.get("inferred_type") and inferred_raw["inferred_type"] != "unknown":
        sqli_type = inferred_raw["inferred_type"]
        type_conf = max(type_conf, 0.6)

    if inferred_raw.get("inferred_db") and inferred_raw["inferred_db"] != "unknown":
        db_engine = inferred_raw["inferred_db"]
        db_conf = max(db_conf, 0.6)

    if inferred_raw.get("attack_type") and inferred_raw["attack_type"] != "unknown":
        sqli_type = inferred_raw["attack_type"]
        type_conf = max(type_conf, 0.9)

    final_confidence = (type_conf + db_conf) / 2.0 if db_conf > 0 else type_conf

    sample["sqli_type"] = sqli_type
    sample["db_engine"] = db_engine
    sample["evasion_tech"] = evasion
    sample["confidence"] = round(final_confidence, 2)
    sample["classification_method"] = "rule"
    sample["context"] = context

    return sample


def classify_batch(samples: list) -> list:
    """Phân loại toàn bộ samples."""
    classified = []
    type_counts = {}

    for sample in samples:
        result = classify_sample(sample)
        classified.append(result)
        st = result.get("sqli_type", "unknown")
        type_counts[st] = type_counts.get(st, 0) + 1

    print(f"\n[+] Classified {len(classified)} samples:")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"    {t}: {c}")

    return classified


class MLClassifier:
    """ML fallback classifier — train sau khi có data đã label bởi rules."""

    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.is_trained = False

    def train(self, samples: list, model_path: str = None):
        """Train ML classifier trên data đã label."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.pipeline import Pipeline
            import pickle

            payloads = [s["payload"] for s in samples if s.get("sqli_type") != "unknown"]
            labels = [s["sqli_type"] for s in samples if s.get("sqli_type") != "unknown"]

            if len(payloads) < 50:
                print("  [WARN] Không đủ data để train ML (< 50 samples có label)")
                return False

            self.vectorizer = TfidfVectorizer(
                analyzer="char_wb",
                ngram_range=(2, 5),
                max_features=10000,
                min_df=2,
            )
            self.classifier = RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                random_state=42,
                class_weight="balanced",
            )

            X = self.vectorizer.fit_transform(payloads)
            self.classifier.fit(X, labels)
            self.is_trained = True

            from sklearn.model_selection import cross_val_score
            scores = cross_val_score(self.classifier, X, labels, cv=5, scoring="accuracy")
            print(f"  [OK] ML classifier trained: accuracy = {scores.mean():.3f} (+/- {scores.std():.3f})")

            if model_path:
                with open(model_path, "wb") as f:
                    pickle.dump({
                        "vectorizer": self.vectorizer,
                        "classifier": self.classifier,
                    }, f)
                print(f"  [OK] Model saved to {model_path}")

            return True

        except ImportError:
            print("  [WARN] sklearn not installed. ML classifier unavailable.")
            return False

    def predict(self, samples: list) -> list:
        """Predict cho samples mà rule không classify được."""
        if not self.is_trained:
            print("  [WARN] ML classifier chưa được train. Bỏ qua.")
            return samples

        import pickle
        unclassified = [s for s in samples if s.get("sqli_type") == "unknown"]
        if not unclassified:
            print("  [OK] Không có sample nào cần ML classify")
            return samples

        payloads = [s["payload"] for s in unclassified]
        X = self.vectorizer.transform(payloads)
        predictions = self.classifier.predict(X)
        probabilities = self.classifier.predict_proba(X)

        for i, sample in enumerate(unclassified):
            sample["sqli_type"] = predictions[i]
            sample["confidence"] = round(float(max(probabilities[i])), 2)
            sample["classification_method"] = "ml"

        print(f"  [OK] ML classified {len(unclassified)} additional samples")
        return samples
