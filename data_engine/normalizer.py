"""
Normalizer — Chuẩn hóa payload SQLi.
URL-decode, chuẩn hóa whitespace, loại artifact, normalize encoding.
"""
import re
import sys
import html
from urllib.parse import unquote
from typing import Dict, Any

sys.stdout.reconfigure(encoding='utf-8')


def url_decode(payload: str) -> str:
    """URL-decode payload (%27 -> ', v.v.)."""
    decoded = unquote(payload)
    while "%" in decoded:
        new_decoded = unquote(decoded)
        if new_decoded == decoded:
            break
        decoded = new_decoded
    return decoded


def html_decode(payload: str) -> str:
    """Decode HTML entities (&apos; -> ')."""
    return html.unescape(payload)


def normalize_whitespace(payload: str) -> str:
    """Chuẩn hóa whitespace: multiple spaces -> single, trim."""
    result = re.sub(r"\s+", " ", payload).strip()
    return result


def normalize_sql_keywords_case(payload: str) -> str:
    """
    Giữ nguyên case của payload vì case variation là kỹ thuật evasion.
    Chỉ normalize những chỗ rõ ràng là artifact.
    """
    return payload


def remove_artifacts(payload: str) -> str:
    """Loại bỏ các placeholder/artifact không phải SQL thật."""
    result = payload
    result = result.replace("__TIME__", "5")
    result = result.replace("__VERSION__", "version()")
    result = re.sub(r"'[a-z]{4}'\s*(?:=|like)\s*'[a-z]{4}'", "", result, flags=re.IGNORECASE)
    return result


def normalize_quotes(payload: str) -> str:
    """Chuẩn hóa các dạng quote không chuẩn."""
    result = payload
    result = result.replace('\\"', '"')
    result = result.replace("\\'", "'")
    result = result.replace("''", "'")
    return result


def clean_csv_artifacts(payload: str) -> str:
    """Làm sạch artifact từ BCCC dataset nhưng giữ nguyên injection payload."""
    result = payload

    m = re.search(r'WHERE\s+username\s*=\s*"(.*?)"(?:\s*(?:OR|AND)\s+username\s*=\s*".+?")*\s*$', result, flags=re.IGNORECASE)
    if m:
        result = m.group(1)
    else:
        m2 = re.search(r'WHERE\s+username\s*=\s*"(.*?)"', result, flags=re.IGNORECASE)
        if m2:
            result = m2.group(1)

    result = re.sub(r'\s+AND\s+username\s*=\s*".*$', "", result, flags=re.IGNORECASE)
    result = re.sub(r'\s+OR\s+username\s*=\s*".*$', "", result, flags=re.IGNORECASE)

    result = re.sub(r'""', '"', result)
    result = result.strip(' "\'')
    return result


def normalize_payload(payload: str, source: str = "") -> str:
    """Pipeline chuẩn hóa toàn bộ cho một payload."""
    result = payload
    result = url_decode(result)
    result = html_decode(result)
    result = normalize_whitespace(result)
    result = remove_artifacts(result)

    if source == "bccc":
        result = clean_csv_artifacts(result)
        result = normalize_whitespace(result)

    return result


def normalize_batch(samples: list) -> list:
    """Chuẩn hóa toàn bộ samples."""
    normalized = []
    for sample in samples:
        payload = sample["payload"]
        source = sample.get("source", "")
        cleaned = normalize_payload(payload, source)
        if cleaned and len(cleaned) > 2:
            sample["payload"] = cleaned
            normalized.append(sample)

    print(f"[+] Normalized: {len(normalized)} / {len(samples)} samples (loại {len(samples) - len(normalized)} rác)")
    return normalized
