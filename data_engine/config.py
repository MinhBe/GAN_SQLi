"""
Configuration cho SQLi Data Engine.
Định nghĩa đường dẫn, các loại SQLi, và các hằng số.
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
ASSET_DIR = BASE_DIR / "Asset" / "Data"
OUTPUT_DIR = Path(__file__).parent / "output"
DATASETS_DIR = OUTPUT_DIR / "datasets"
STATS_DIR = OUTPUT_DIR / "stats"

# Output files
UNIFIED_CSV = OUTPUT_DIR / "unified_sqli_pool.csv"
UNIFIED_JSON = OUTPUT_DIR / "unified_sqli_pool.json"

# SQLi types theo Type_of_SQLi.md
SQLI_TYPES = [
    "error_based",
    "union_based",
    "boolean_blind",
    "time_blind",
    "heavy_query",
    "out_of_band",
    "stacked_queries",
    "second_order",
    "auth_bypass",
    "lateral",
    "header_injection",
    "polyglot",
    "data_exfil",
    "rce",
    "evasion",
    "unknown",
]

# DB engines
DB_ENGINES = ["mysql", "mssql", "oracle", "postgresql", "sqlite", "nosql", "unknown"]

# Evasion techniques
EVASION_TECHS = [
    "url_encoding",
    "double_url_encoding",
    "unicode_encoding",
    "html_entity",
    "case_variation",
    "comment_whitespace",
    "inline_comment",
    "keyword_obfuscation",
    "function_alternative",
    "hex_string",
    "scientific_notation",
    "null_byte",
]

# Unified schema columns
UNIFIED_COLUMNS = [
    "payload",
    "sqli_type",
    "db_engine",
    "evasion_tech",
    "confidence",
    "classification_method",
    "source",
    "context",
]

# Input sources
INPUT_SOURCES = {
    "bccc": {
        "path": ASSET_DIR / "BCCC-SFU-SQLInj-2023.csv",
        "format": "csv",
        "description": "BCCC-SFU SQL Injection dataset 2023",
    },
    "sqliv5_csv": {
        "path": ASSET_DIR / "sqliv5_dataset" / "sqli.csv",
        "format": "csv",
        "description": "SQLiV5 dataset CSV v1",
    },
    "sqliv2_csv": {
        "path": ASSET_DIR / "sqliv5_dataset" / "sqliv2.csv",
        "format": "csv",
        "description": "SQLiV5 dataset CSV v2",
    },
    "sqliv3_csv": {
        "path": ASSET_DIR / "sqliv5_dataset" / "SQLiV3.csv",
        "format": "csv",
        "description": "SQLiV5 dataset CSV v3",
    },
    "sqliv5_json": {
        "path": ASSET_DIR / "sqliv5_dataset" / "SQLiV5.json",
        "format": "json",
        "description": "SQLiV5 dataset JSON v5",
    },
    "sqliv4_json": {
        "path": ASSET_DIR / "sqliv5_dataset" / "SQLiV4.json",
        "format": "json",
        "description": "SQLiV5 dataset JSON v4",
    },
    "sqliv3_json": {
        "path": ASSET_DIR / "sqliv5_dataset" / "SQLiV3_clean.json",
        "format": "json",
        "description": "SQLiV5 dataset JSON v3 clean",
    },
    "seclists": {
        "path": ASSET_DIR / "seclists_sqli" / "Fuzzing" / "Databases" / "SQLi",
        "format": "txt_dir",
        "description": "SecLists SQLi fuzzing payloads",
    },
    "exploitdb": {
        "path": ASSET_DIR / "exploitdb_sqli" / "sqli_exploits.csv",
        "format": "csv",
        "description": "ExploitDB filtered SQLi entries",
    },
    "sqlmap_xml": {
        "path": ASSET_DIR / "sqlmap_payloads" / "data" / "xml" / "payloads",
        "format": "xml_dir",
        "description": "SQLMap XML payload definitions",
    },
}

# Dedup settings
DEDUP_SIMILARITY_THRESHOLD = 0.85  # TF-IDF cosine similarity threshold for near-dedup

# ML classifier settings
ML_TEST_SIZE = 0.2
ML_RANDOM_STATE = 42
