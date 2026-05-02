"""
Splitter — Chia unified SQLi pool thành các dataset riêng theo loại.
Output: mỗi loại SQLi có file riêng, cộng thống kê phân bố.
"""
import csv
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Any

sys.stdout.reconfigure(encoding='utf-8')
from config import (
    DATASETS_DIR,
    STATS_DIR,
    OUTPUT_DIR,
    UNIFIED_CSV,
    UNIFIED_JSON,
    SQLI_TYPES,
    UNIFIED_COLUMNS,
    EVASION_TECHS,
)


def save_unified_pool(samples: List[Dict[str, Any]]):
    """Lưu unified pool ra CSV và JSON."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    csv_rows = []
    for s in samples:
        row = {col: s.get(col, "") for col in UNIFIED_COLUMNS}
        row["evasion_tech"] = "|".join(s.get("evasion_tech", []))
        csv_rows.append(row)

    with open(UNIFIED_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=UNIFIED_COLUMNS)
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"[OK] Saved {UNIFIED_CSV} ({len(csv_rows)} rows)")

    with open(UNIFIED_JSON, "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved {UNIFIED_JSON}")

    return csv_rows


def split_by_type(samples: List[Dict[str, Any]]):
    """Chia samples theo sqli_type, xuất file riêng."""
    type_groups = defaultdict(list)
    evasion_groups = defaultdict(list)

    for s in samples:
        stype = s.get("sqli_type", "unknown")
        type_groups[stype].append(s)

        evasion_techs = s.get("evasion_tech", [])
        for tech in evasion_techs:
            evasion_groups[tech].append(s)

    os.makedirs(DATASETS_DIR / "evasion", exist_ok=True)

    for stype, group in type_groups.items():
        filename = f"{stype}.csv"
        filepath = DATASETS_DIR / filename
        if stype == "evasion":
            filepath = DATASETS_DIR / "evasion" / filename

        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=UNIFIED_COLUMNS)
            writer.writeheader()
            for s in group:
                row = {col: s.get(col, "") for col in UNIFIED_COLUMNS}
                row["evasion_tech"] = "|".join(s.get("evasion_tech", []))
                writer.writerow(row)
        print(f"  [OK] {filepath.name}: {len(group)} samples")

    for tech, group in evasion_groups.items():
        filename = f"evasion_{tech}.csv"
        filepath = DATASETS_DIR / "evasion" / filename
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=UNIFIED_COLUMNS)
            writer.writeheader()
            for s in group:
                row = {col: s.get(col, "") for col in UNIFIED_COLUMNS}
                row["evasion_tech"] = "|".join(s.get("evasion_tech", []))
                writer.writerow(row)
        print(f"  [OK] evasion/{filename}: {len(group)} samples")

    return type_groups, evasion_groups


def generate_stats(samples: List[Dict[str, Any]], type_groups: dict, evasion_groups: dict):
    """Tạo thống kê và báo cáo chất lượng."""
    os.makedirs(STATS_DIR, exist_ok=True)

    type_dist = {}
    for stype in SQLI_TYPES:
        count = len(type_groups.get(stype, []))
        if count > 0:
            type_dist[stype] = count

    db_dist = defaultdict(int)
    for s in samples:
        db = s.get("db_engine", "unknown")
        db_dist[db] += 1

    evasion_dist = {}
    for tech in EVASION_TECHS:
        count = len(evasion_groups.get(tech, []))
        if count > 0:
            evasion_dist[tech] = count

    method_dist = defaultdict(int)
    for s in samples:
        method = s.get("classification_method", "unknown")
        method_dist[method] += 1

    confidence_dist = {"high": 0, "medium": 0, "low": 0}
    for s in samples:
        conf = s.get("confidence", 0)
        if conf >= 0.8:
            confidence_dist["high"] += 1
        elif conf >= 0.5:
            confidence_dist["medium"] += 1
        else:
            confidence_dist["low"] += 1

    stats = {
        "total_samples": len(samples),
        "by_type": type_dist,
        "by_db_engine": dict(db_dist),
        "by_evasion_technique": evasion_dist,
        "by_classification_method": dict(method_dist),
        "by_confidence": confidence_dist,
        "type_distribution": type_dist,
    }

    type_dist_path = STATS_DIR / "distribution_by_type.json"
    with open(type_dist_path, "w", encoding="utf-8") as f:
        json.dump(type_dist, f, indent=2, ensure_ascii=False)

    db_dist_path = STATS_DIR / "distribution_by_db.json"
    with open(db_dist_path, "w", encoding="utf-8") as f:
        json.dump(dict(db_dist), f, indent=2, ensure_ascii=False)

    report = generate_report(stats)
    report_path = STATS_DIR / "quality_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n[OK] Stats saved to {STATS_DIR}")
    return stats


def generate_report(stats: dict) -> str:
    """Tạo markdown quality report."""
    lines = [
        "# SQLi Data Engine — Quality Report",
        "",
        f"**Tổng samples:** {stats['total_samples']}",
        "",
        "## Phân Bố Theo Loại SQLi",
        "",
        "| Loại | Số lượng | Tỉ lệ |",
        "|------|----------|-------|",
    ]

    total = stats["total_samples"]
    for stype, count in sorted(stats["by_type"].items(), key=lambda x: -x[1]):
        pct = f"{count / total * 100:.1f}%" if total > 0 else "0%"
        lines.append(f"| {stype} | {count} | {pct} |")

    lines.extend([
        "",
        "## Phân Bố Theo DB Engine",
        "",
        "| Engine | Số lượng |",
        "|--------|----------|",
    ])
    for db, count in sorted(stats["by_db_engine"].items(), key=lambda x: -x[1]):
        lines.append(f"| {db} | {count} |")

    lines.extend([
        "",
        "## Phân Bố Theo Phương Pháp Classification",
        "",
        "| Phương pháp | Số lượng |",
        "|-------------|----------|",
    ])
    for method, count in stats["by_classification_method"].items():
        lines.append(f"| {method} | {count} |")

    lines.extend([
        "",
        "## Chất Lượng Confidence",
        "",
        f"- High (>= 0.8): {stats['by_confidence']['high']}",
        f"- Medium (0.5-0.8): {stats['by_confidence']['medium']}",
        f"- Low (< 0.5): {stats['by_confidence']['low']}",
        "",
        "## Kỹ Thuật Evasion Phát Hiện",
        "",
        "| Kỹ thuật | Số lượng |",
        "|----------|----------|",
    ])
    for tech, count in sorted(stats["by_evasion_technique"].items(), key=lambda x: -x[1]):
        lines.append(f"| {tech} | {count} |")

    lines.extend([
        "",
        "---",
        f"*Generated by SQLi Data Engine*",
    ])

    return "\n".join(lines)


def run_splitter(samples: List[Dict[str, Any]]):
    """Entry point cho splitter."""
    print(f"\n[*] Splitting {len(samples)} samples into datasets...")
    save_unified_pool(samples)
    type_groups, evasion_groups = split_by_type(samples)
    stats = generate_stats(samples, type_groups, evasion_groups)
    return stats
