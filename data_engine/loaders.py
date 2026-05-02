"""
Format detector + loaders cho các loại file dữ liệu SQLi.
Hỗ trợ: CSV, JSON, XML (sqlmap), TXT (seclists).
"""
import csv
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any

sys.stdout.reconfigure(encoding='utf-8')
from config import INPUT_SOURCES


def detect_csv_payload_column(headers: List[str]) -> str:
    """Tự động tìm column chứa payload trong CSV."""
    priority_keywords = [
        "pattern", "payload", "data", "sentence", "query",
        "sql", "input", "text", "description",
    ]
    for kw in priority_keywords:
        for h in headers:
            if kw.lower() in h.lower():
                return h
    return headers[0]


def load_csv_source(source_name: str, source_config: dict) -> List[Dict[str, Any]]:
    """Load dữ liệu từ file CSV."""
    path = Path(source_config["path"])
    if not path.exists():
        print(f"  [WARN] File không tồn tại: {path}")
        return []

    encodings_to_try = ["utf-8", "utf-16", "utf-16-le", "utf-16-be", "latin-1"]
    f = None
    encoding_used = "utf-8"

    for enc in encodings_to_try:
        try:
            f = open(path, "r", encoding=enc, errors="strict")
            first_line = f.readline(200)
            if "\x00" in first_line:
                f.close()
                continue
            f.seek(0)
            encoding_used = enc
            break
        except (UnicodeDecodeError, UnicodeError):
            if f:
                f.close()
            continue

    if f is None:
        f = open(path, "r", encoding="utf-8", errors="replace")

    results = []
    try:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print(f"  [WARN] CSV rỗng: {path}")
            f.close()
            return []

        payload_col = detect_csv_payload_column(reader.fieldnames)

        for row in reader:
            payload = row.get(payload_col, "").strip()
            if payload:
                results.append({
                    "payload": payload,
                    "source": source_name,
                    "raw": dict(row),
                })
    finally:
        f.close()

    print(f"  [OK] {source_name}: {len(results)} samples từ {path.name} (encoding: {encoding_used})")
    return results


def load_json_source(source_name: str, source_config: dict) -> List[Dict[str, Any]]:
    """Load dữ liệu từ file JSON."""
    path = Path(source_config["path"])
    if not path.exists():
        print(f"  [WARN] File không tồn tại: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        data = [data]

    results = []
    for item in data:
        payload = ""
        if isinstance(item, dict):
            payload = item.get("pattern", item.get("payload", item.get("sql", "")))
        elif isinstance(item, str):
            payload = item

        if payload and isinstance(payload, str):
            results.append({
                "payload": payload.strip(),
                "source": source_name,
                "raw": item if isinstance(item, dict) else {},
            })

    print(f"  [OK] {source_name}: {len(results)} samples từ {path.name}")
    return results


def load_txt_dir_source(source_name: str, source_config: dict) -> List[Dict[str, Any]]:
    """Load dữ liệu từ thư mục chứa các file TXT (seclists)."""
    path = Path(source_config["path"])
    if not path.exists():
        print(f"  [WARN] Thư mục không tồn tại: {path}")
        return []

    results = []
    txt_files = sorted(path.glob("*.txt"))

    for txt_file in txt_files:
        inferred_type = _infer_type_from_filename(txt_file.name)
        inferred_db = _infer_db_from_filename(txt_file.name)

        with open(txt_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    results.append({
                        "payload": line,
                        "source": source_name,
                        "raw": {
                            "filename": txt_file.name,
                            "inferred_type": inferred_type,
                            "inferred_db": inferred_db,
                        },
                    })

    print(f"  [OK] {source_name}: {len(results)} samples từ {len(txt_files)} files")
    return results


def load_xml_dir_source(source_name: str, source_config: dict) -> List[Dict[str, Any]]:
    """Load payloads từ thư mục XML của sqlmap."""
    path = Path(source_config["path"])
    if not path.exists():
        print(f"  [WARN] Thư mục không tồn tại: {path}")
        return []

    results = []
    xml_files = sorted(path.glob("*.xml"))

    for xml_file in xml_files:
        attack_type = _xml_to_sqli_type(xml_file.stem)

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for test in root.iter("test"):
                title = test.find("title")
                request_elem = test.find("request")
                if request_elem is not None:
                    payload_elem = request_elem.find("payload")
                    if payload_elem is not None and payload_elem.text:
                        payload = payload_elem.text.strip()
                        if payload:
                            results.append({
                                "payload": payload,
                                "source": source_name,
                                "raw": {
                                    "xml_file": xml_file.name,
                                    "attack_type": attack_type,
                                    "title": title.text if title is not None else "",
                                },
                            })
        except ET.ParseError as e:
            print(f"  [WARN] Lỗi parse XML {xml_file.name}: {e}")

    print(f"  [OK] {source_name}: {len(results)} payloads từ {len(xml_files)} XML files")
    return results


def _infer_type_from_filename(filename: str) -> str:
    """Gợi ý loại SQLi từ tên file."""
    name = filename.lower()
    if "blind" in name:
        return "boolean_blind"
    if "union" in name:
        return "union_based"
    if "error" in name:
        return "error_based"
    if "auth" in name or "bypass" in name or "login" in name:
        return "auth_bypass"
    if "polyglot" in name:
        return "polyglot"
    if "nosql" in name:
        return "unknown"
    return "unknown"


def _infer_db_from_filename(filename: str) -> str:
    """Gợi ý DB engine từ tên file."""
    name = filename.lower()
    if "mysql" in name:
        return "mysql"
    if "mssql" in name:
        return "mssql"
    if "oracle" in name:
        return "oracle"
    if "postgres" in name:
        return "postgresql"
    if "sqlite" in name:
        return "sqlite"
    if "nosql" in name:
        return "nosql"
    if "db2" in name:
        return "mssql"
    return "unknown"


def _xml_to_sqli_type(xml_stem: str) -> str:
    """Ánh xạ tên file XML của sqlmap sang loại SQLi."""
    mapping = {
        "boolean_blind": "boolean_blind",
        "error_based": "error_based",
        "time_blind": "time_blind",
        "union_query": "union_based",
        "stacked_queries": "stacked_queries",
        "inline_query": "error_based",
    }
    return mapping.get(xml_stem, "unknown")


def load_all_sources() -> List[Dict[str, Any]]:
    """Load toàn bộ sources đã cấu hình."""
    all_samples = []

    for source_name, source_config in INPUT_SOURCES.items():
        fmt = source_config["format"]
        print(f"[*] Đang load: {source_name} ({fmt})")

        if fmt == "csv":
            samples = load_csv_source(source_name, source_config)
        elif fmt == "json":
            samples = load_json_source(source_name, source_config)
        elif fmt == "txt_dir":
            samples = load_txt_dir_source(source_name, source_config)
        elif fmt == "xml_dir":
            samples = load_xml_dir_source(source_name, source_config)
        else:
            print(f"  [WARN] Format không hỗ trợ: {fmt}")
            samples = []

        all_samples.extend(samples)

    print(f"\n[+] Tổng: {len(all_samples)} samples từ {len(INPUT_SOURCES)} sources")
    return all_samples
