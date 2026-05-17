#!/usr/bin/env python3
"""
Label chunks 111-113 in parallel.
Rule: Trust payload_inner, ignore hints.
Output: chunk_NNN_labeled.csv with id, payload_inner, sqli_type, db_engine, confidence, reasoning, sources_agree
"""

import pandas as pd
import re
from pathlib import Path
import concurrent.futures
from typing import Dict, Tuple, Optional

CHUNK_DIR = Path(r"C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks")
OUTPUT_DIR = CHUNK_DIR.parent

# Taxonomy: type priority (lower = higher priority)
TYPE_PRIORITY = {
    'rce': 1,
    'out_of_band': 2,
    'stacked_queries': 3,
    'error_based': 4,
    'time_blind': 5,
    'heavy_query': 6,
    'union_based': 7,
    'boolean_blind': 8,
    'auth_bypass': 9,
    'second_order': 10,
    'polyglot': 11,
    'lateral': 12,
    'benign': 13,
    'unknown': 14,
}

DB_ENGINES = ['mysql', 'mssql', 'oracle', 'postgresql', 'sqlite', 'firebird', 'db2', 'generic', 'unknown']

# Signals for type detection (by priority)
TYPE_SIGNALS = {
    'rce': [r'xp_cmdshell', r'certutil', r'powershell', r'/bin/bash', r'cmd\.exe'],
    'out_of_band': [r'load_file', r'utl_http', r'utl_inaddr', r'xp_dirtree', r'xp_fileexist', r'openrowset'],
    'stacked_queries': [r';\s*(create|drop|insert|update|delete|exec|call)', r';\s*select'],
    'error_based': [r'extractvalue', r'updatexml', r'ctxsys', r'drithsx'],
    'time_blind': [r'sleep\s*\(', r'pg_sleep', r'waitfor\s+delay', r'benchmark\s*\(', r'randomblob\s*\(', r'dbms_pipe', r'dbms_lock'],
    'heavy_query': [r'from\s+\w+\s+as\s+\w+\s*,\s*\w+\s+as\s+\w+\s*,\s*\w+\s+as\s+\w+'],  # 3+ table cross-join
    'union_based': [r'union\s+(all\s+)?select', r'order\s+by\s+\d+'],
    'boolean_blind': [r"(and|or)\s+(1\s*=\s*1|'[a-z]'\s*=\s*'[a-z]'|0\s*=\s*0)"],
    'auth_bypass': [r"admin\s*'", r"admin\s*'--", r"admin\s*'#"],
}

DB_SIGNATURES = {
    'mysql': [r'sleep\s*\(', r'@@version', r'information_schema', r'load_file', r'extractvalue', r'updatexml', r'benchmark', r'/*!.*?\*/'],
    'mssql': [r'waitfor\s+delay', r'sysobjects', r'xp_cmdshell', r'@@servername', r'sys\.tables', r'char\s*\(\s*\d+\s*\)'],
    'oracle': [r'utl_inaddr', r'ctxsys', r'xmltype', r'from\s+dual', r'rownum', r'v\$version', r'all_users'],
    'postgresql': [r'pg_sleep', r'::\s*text', r'pg_catalog', r'pg_tables'],
    'sqlite': [r'sqlite_version', r'sqlite_master', r'randomblob'],
    'firebird': [r'rdb\$', r'iif\s*\('],
    'db2': [r'sysibm\.systables', r'syscat\.tables'],
}

class ChunkLabeler:
    def __init__(self, chunk_num: int):
        self.chunk_num = chunk_num
        self.chunk_path = CHUNK_DIR / f"chunk_{chunk_num:03d}.csv"
        self.output_path = OUTPUT_DIR / f"chunk_{chunk_num:03d}_labeled.csv"

    def load_chunk(self) -> pd.DataFrame:
        """Load chunk CSV, use payload_inner column."""
        df = pd.read_csv(self.chunk_path)
        # Ensure we have payload_inner
        if 'payload_inner' not in df.columns:
            raise ValueError(f"No payload_inner column in chunk_{self.chunk_num:03d}.csv")
        return df

    def detect_type(self, payload: str) -> Tuple[str, float]:
        """Detect SQLi type from payload. Returns (type, confidence)."""
        if not payload or len(payload.strip()) < 3:
            return ('benign', 0.5)

        payload_lower = payload.lower()

        # Check attack signals in priority order
        detected_types = {}
        for sqli_type, patterns in TYPE_SIGNALS.items():
            for pattern in patterns:
                if re.search(pattern, payload_lower, re.IGNORECASE):
                    if sqli_type not in detected_types:
                        detected_types[sqli_type] = 0
                    detected_types[sqli_type] += 1
                    break

        if not detected_types:
            # No explicit attack signal found
            # Check for SQLi-like fragments: quote escapes, parentheses nesting, logical operators

            # Count SQLi-like patterns
            sqli_indicators = 0

            # Quote escape patterns
            if re.search(r"['\"][\s\)]*(?:or|and)", payload_lower):
                sqli_indicators += 2
            if re.search(r"'[\s\)]*=[\s\)]*'", payload_lower):
                sqli_indicators += 2
            if re.search(r"'\s*\)", payload_lower):
                sqli_indicators += 1
            if re.search(r"\)\s*or\s", payload_lower):
                sqli_indicators += 2
            if re.search(r"\)\s*and\s", payload_lower):
                sqli_indicators += 2
            if re.search(r"where.*=", payload_lower):
                sqli_indicators += 1

            # Cast and type conversion patterns (error-based)
            if 'cast' in payload_lower or '::' in payload_lower:
                sqli_indicators += 2

            # Nested parentheses (suspicious injection)
            paren_depth = 0
            max_paren_depth = 0
            for c in payload:
                if c == '(':
                    paren_depth += 1
                    max_paren_depth = max(max_paren_depth, paren_depth)
                elif c == ')':
                    paren_depth -= 1
            if max_paren_depth >= 3:
                sqli_indicators += 1

            if sqli_indicators >= 3:
                # Likely a boolean-blind or similar fragment
                if 'or' in payload_lower or 'and' in payload_lower:
                    return ('boolean_blind', 0.75)
                elif 'cast' in payload_lower or '::' in payload_lower:
                    return ('error_based', 0.65)
                else:
                    return ('unknown', 0.55)

            # No attack signal found
            # Check for benign indicators
            if any(kw in payload_lower for kw in ['select *', 'from users', 'where', 'and', 'or']):
                # Looks like normal SQL
                if not any(atk in payload_lower for atk in
                          ['union', 'sleep', 'benchmark', 'extractvalue', 'xp_', 'load_file',
                           "' or", "' and", 'or 1=1', 'and 1=1', 'admin']):
                    return ('benign', 0.8)
            return ('unknown', 0.5)

        # Choose type by lowest priority (highest severity)
        detected_type = min(detected_types.keys(), key=lambda t: TYPE_PRIORITY.get(t, 100))

        # Confidence based on signal strength
        signal_count = detected_types[detected_type]
        confidence = min(0.95, 0.6 + (signal_count * 0.15))

        return (detected_type, confidence)

    def detect_db_engine(self, payload: str, sqli_type: str) -> str:
        """Detect DB engine from payload signatures."""
        if not payload:
            return 'generic'

        payload_lower = payload.lower()

        # DB-exclusive signatures by type
        exclusive_sigs = {
            'postgresql': [r'pg_sleep', r'::\s*text'],
            'mysql': [r'sleep\s*\(', r'benchmark\s*\('],
            'mssql': [r'waitfor\s+delay', r'char\s*\(\s*\d+\s*\)'],
            'oracle': [r'xmltype', r'from\s+dual'],
            'sqlite': [r'randomblob'],
            'firebird': [r'rdb\$'],
            'db2': [r'sysibm'],
        }

        # Check exclusive signatures first
        for db, patterns in exclusive_sigs.items():
            for pattern in patterns:
                if re.search(pattern, payload_lower, re.IGNORECASE):
                    return db

        # Check general signatures
        detected_dbs = {}
        for db, patterns in DB_SIGNATURES.items():
            match_count = 0
            for pattern in patterns:
                if re.search(pattern, payload_lower, re.IGNORECASE):
                    match_count += 1
            if match_count > 0:
                detected_dbs[db] = match_count

        if detected_dbs:
            # Return DB with most matches
            return max(detected_dbs.keys(), key=lambda db: detected_dbs[db])

        return 'generic'

    def count_sources_agree(self, row: pd.Series, sqli_type: str, db_engine: str) -> int:
        """Count how many sources (a_type, a_db, c_type, c_db) agree with our labels."""
        agree = 0
        total = 0

        if 'a_type' in row and pd.notna(row['a_type']):
            total += 1
            if str(row['a_type']).lower() == sqli_type:
                agree += 1

        if 'c_type' in row and pd.notna(row['c_type']):
            total += 1
            if str(row['c_type']).lower() == sqli_type:
                agree += 1

        if 'a_db' in row and pd.notna(row['a_db']):
            total += 1
            if str(row['a_db']).lower() == db_engine:
                agree += 1

        if 'c_db' in row and pd.notna(row['c_db']):
            total += 1
            if str(row['c_db']).lower() == db_engine:
                agree += 1

        # If no sources to compare, return 0
        if total == 0:
            return 0

        # Return agreement count (0-4)
        return agree

    def generate_reasoning(self, payload: str, sqli_type: str, db_engine: str, confidence: float) -> str:
        """Generate reasoning string based on signals found."""
        payload_lower = payload.lower()

        # Find the specific signal that triggered the classification
        if sqli_type == 'benign':
            return "No SQLi signals detected in payload"

        if sqli_type == 'unknown':
            return "Payload too short or insufficient signal for classification"

        # Find which signal matched
        if sqli_type in TYPE_SIGNALS:
            for pattern in TYPE_SIGNALS[sqli_type]:
                if re.search(pattern, payload_lower, re.IGNORECASE):
                    match = re.search(pattern, payload_lower, re.IGNORECASE)
                    signal = match.group()

                    # Type-specific reasonings
                    if sqli_type == 'time_blind':
                        return f"Time-blind signal detected: '{signal}' in {db_engine} payload"
                    elif sqli_type == 'error_based':
                        return f"Error-based signal detected: '{signal}' for {db_engine}"
                    elif sqli_type == 'union_based':
                        return f"UNION-based signal detected: '{signal}' pattern found"
                    elif sqli_type == 'boolean_blind':
                        return f"Boolean blind signal detected: logical comparison pattern"
                    elif sqli_type == 'auth_bypass':
                        return f"Auth bypass signal detected: 'admin' with quote/comment syntax"
                    elif sqli_type == 'stacked_queries':
                        return f"Stacked queries signal detected: semicolon + new statement"
                    elif sqli_type == 'rce':
                        return f"RCE signal detected: '{signal}' command execution function"
                    elif sqli_type == 'out_of_band':
                        return f"Out-of-band signal detected: '{signal}' exfiltration function"
                    else:
                        return f"Signal detected: '{signal}' indicates {sqli_type}"

        return f"Classified as {sqli_type} (confidence {confidence:.2f})"

    def label_chunk(self) -> pd.DataFrame:
        """Label all rows in chunk."""
        df = self.load_chunk()

        results = []
        for idx, row in df.iterrows():
            payload = str(row.get('payload_inner', ''))

            # Detect type and DB engine
            sqli_type, confidence = self.detect_type(payload)
            db_engine = self.detect_db_engine(payload, sqli_type)

            # Generate reasoning
            reasoning = self.generate_reasoning(payload, sqli_type, db_engine, confidence)

            # Ensure minimum reasoning length
            if len(reasoning) < 50:
                reasoning += f" (confidence {confidence:.2f})"

            # Count sources agreement
            sources_agree = self.count_sources_agree(row, sqli_type, db_engine)

            results.append({
                'id': row.get('id', idx),
                'payload_inner': payload,
                'sqli_type': sqli_type,
                'db_engine': db_engine,
                'confidence': round(confidence, 2),
                'reasoning': reasoning,
                'sources_agree': sources_agree,
            })

        return pd.DataFrame(results)

    def save_and_report(self, df: pd.DataFrame) -> Dict:
        """Save labeled CSV and generate report."""
        df.to_csv(self.output_path, index=False)

        # Generate statistics
        report = {
            'chunk': self.chunk_num,
            'total_rows': len(df),
            'types': df['sqli_type'].value_counts().to_dict(),
            'top_5_types': df['sqli_type'].value_counts().head(5).to_dict(),
            'low_conf': df[df['confidence'] < 0.7],
            'short_reasoning': df[df['reasoning'].str.len() < 50],
            'avg_sources_agree': df['sources_agree'].mean(),
            'output_path': str(self.output_path),
        }

        return report

def process_chunk(chunk_num: int) -> Dict:
    """Process single chunk."""
    labeler = ChunkLabeler(chunk_num)
    df = labeler.label_chunk()
    report = labeler.save_and_report(df)
    return report

# Run 3 chunks in parallel
if __name__ == '__main__':
    print("Labeling chunks 111-113 in parallel...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(process_chunk, i): i
            for i in [111, 112, 113]
        }

        all_reports = {}
        for future in concurrent.futures.as_completed(futures):
            chunk_num = futures[future]
            try:
                report = future.result()
                all_reports[chunk_num] = report
                print(f"[OK] Chunk {chunk_num} completed")
            except Exception as e:
                print(f"[FAIL] Chunk {chunk_num} failed: {e}")

    # Print summary
    print("\n" + "="*80)
    print("LABELING SUMMARY")
    print("="*80)

    for chunk_num in sorted(all_reports.keys()):
        report = all_reports[chunk_num]
        print(f"\nChunk {chunk_num}:")
        print(f"  Total rows: {report['total_rows']}")
        print(f"  Output: {report['output_path']}")
        print(f"  Top-5 types:")
        for t, c in list(report['top_5_types'].items())[:5]:
            print(f"    {t}: {c}")
        print(f"  Low-confidence rows (<0.7): {len(report['low_conf'])}")
        print(f"  Short-reasoning rows (<50 chars): {len(report['short_reasoning'])}")
        print(f"  Average sources agreement: {report['avg_sources_agree']:.2f}/4")

    print("\n" + "="*80)
