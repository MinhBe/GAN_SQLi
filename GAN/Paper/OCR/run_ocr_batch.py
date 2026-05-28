import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import fitz
from ftfy import fix_text


ROOT = Path(__file__).resolve().parents[3]
PDF_DIR = ROOT / "GAN" / "Paper" / "PDF"
OCR_DIR = ROOT / "GAN" / "Paper" / "OCR"
SAMPLE_DIR = OCR_DIR / "_sample"
ROUTER = ROOT / "Skill" / "OCR_PDF" / "scripts" / "ocr_router.py"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_pages(path: Path) -> int:
    doc = fitz.open(path)
    try:
        return len(doc)
    finally:
        doc.close()


def native_first_pages(path: Path, max_pages: int = 3) -> str:
    doc = fitz.open(path)
    try:
        return "\n".join(doc[i].get_text() for i in range(min(max_pages, len(doc))))
    finally:
        doc.close()


def run_router(pdf: Path, out: Path, mode: str, pages: str | None = None, dpi: int | None = None) -> tuple[bool, str]:
    cmd = [
        sys.executable,
        str(ROUTER),
        "--input",
        str(pdf),
        "--output",
        str(out),
        "--mode",
        mode,
        "--lang",
        "en",
    ]
    if pages:
        cmd.extend(["--pages", pages])
    if dpi:
        cmd.extend(["--dpi", str(dpi)])
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    log = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, log.strip()


def mojibake_score(text: str) -> int:
    markers = ["�", "â€", "ï¬", "\x00", "áº", "Ã½", "å¼", "ç”", "ï¼", "æµ"]
    return sum(text.count(ch) for ch in markers)


def garbage_ratio(text: str) -> float:
    stripped = text.strip()
    if not stripped:
        return 1.0
    good = sum(1 for ch in stripped if ch.isalnum() or ch.isspace() or ch in ".,;:()[]{}+-=*/%_<>#'\"`~@&|\\!?$")
    return 1.0 - (good / len(stripped))


def extract_title(text: str, fallback: str) -> str:
    lines = [re.sub(r"\s+", " ", line).strip(" #\t") for line in text.splitlines()]
    lines = [line for line in lines if 12 <= len(line) <= 180]
    skip = re.compile(r"^(abstract|keywords|arxiv|doi|issn|isbn|www\.|http|proceedings|journal)\b", re.I)
    for line in lines[:80]:
        if not skip.search(line) and sum(ch.isalpha() for ch in line) >= 8:
            return line
    return fallback


def quality_status(text: str, title: str) -> tuple[str, list[str]]:
    reasons: list[str] = []
    chars = len(text.strip())
    lower = text.lower()
    if chars < 1200:
        reasons.append(f"short sample ({chars} chars)")
    if "abstract" not in lower and chars < 5000:
        reasons.append("abstract not detected in first pages")
    if mojibake_score(text) > 3:
        reasons.append("mojibake markers detected")
    if garbage_ratio(text) > 0.12:
        reasons.append("high non-text character ratio")
    if not title or title == "unknown":
        reasons.append("title not detected")
    return ("weak" if reasons else "pass", reasons)


def conservative_repair(text: str) -> str:
    text = fix_text(text)
    text = text.replace("\x0c", "\n")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+$", "", text, flags=re.M)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"(?<=[a-z])-\n(?=[a-z])", "", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n"


def similar_title_groups(titles: dict[str, str]) -> list[list[str]]:
    groups = []
    seen = set()
    tokenized = {}
    for name, title in titles.items():
        tokens = set(re.findall(r"[a-z0-9]{3,}", title.lower()))
        tokenized[name] = tokens
    names = sorted(titles)
    for i, name in enumerate(names):
        if name in seen:
            continue
        group = [name]
        for other in names[i + 1 :]:
            if other in seen:
                continue
            a, b = tokenized[name], tokenized[other]
            if not a or not b:
                continue
            jaccard = len(a & b) / max(len(a | b), 1)
            if jaccard >= 0.42:
                group.append(other)
        if len(group) > 1:
            seen.update(group)
            groups.append(group)
    return groups


def main() -> int:
    OCR_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(PDF_DIR.glob("*.pdf"), key=lambda p: p.name.lower())
    hash_to_files: dict[str, list[Path]] = defaultdict(list)
    page_counts = {}
    for pdf in pdfs:
        digest = sha256(pdf)
        hash_to_files[digest].append(pdf)
        page_counts[pdf.name] = pdf_pages(pdf)

    manifest_rows = []
    sample_rows = []
    titles = {}
    duplicate_rows = []
    canonical_for_hash = {}

    for digest, files in sorted(hash_to_files.items(), key=lambda item: item[1][0].name.lower()):
        canonical = sorted(files, key=lambda p: p.name.lower())[0]
        canonical_for_hash[digest] = canonical
        if len(files) > 1:
            duplicate_rows.append((digest, canonical.name, [p.name for p in sorted(files, key=lambda p: p.name.lower()) if p != canonical]))

        sample_out = SAMPLE_DIR / f"{canonical.stem}.sample3.md"
        ok, log = run_router(canonical, sample_out, "auto", pages="1-3")
        sample_text = sample_out.read_text(encoding="utf-8", errors="replace") if sample_out.exists() else ""
        sample_text = conservative_repair(sample_text)
        sample_out.write_text(sample_text, encoding="utf-8")
        title = extract_title(sample_text or native_first_pages(canonical), canonical.stem)
        status, reasons = quality_status(sample_text, title)
        chosen_mode = "auto"
        chosen_dpi = ""

        if not ok or status == "weak":
            retry_out = SAMPLE_DIR / f"{canonical.stem}.sample3.quality.md"
            retry_ok, retry_log = run_router(canonical, retry_out, "quality", pages="1-3", dpi=300)
            retry_text = retry_out.read_text(encoding="utf-8", errors="replace") if retry_out.exists() else ""
            retry_title = extract_title(retry_text or native_first_pages(canonical), canonical.stem)
            retry_status, retry_reasons = quality_status(retry_text, retry_title)
            if retry_ok and retry_status == "pass":
                sample_out.write_text(conservative_repair(retry_text), encoding="utf-8")
                title = retry_title
                status = "pass_after_quality"
                reasons = []
                chosen_mode = "quality"
                chosen_dpi = "300"
                log = retry_log
            else:
                reasons = reasons or retry_reasons
                log = (log + "\n" + retry_log).strip()
                if retry_ok and len(retry_text.strip()) > len(sample_text.strip()):
                    sample_out.write_text(conservative_repair(retry_text), encoding="utf-8")
                    title = retry_title
                    chosen_mode = "quality"
                    chosen_dpi = "300"

        titles[canonical.name] = title
        sample_rows.append(
            {
                "pdf": canonical.name,
                "pages": page_counts[canonical.name],
                "sha256": digest,
                "sample_output": str(sample_out.relative_to(ROOT)),
                "sample_status": status,
                "chosen_mode": chosen_mode,
                "dpi": chosen_dpi,
                "title": title,
                "notes": "; ".join(reasons),
                "router_log_tail": log[-500:],
            }
        )

        full_out = OCR_DIR / f"{canonical.stem}.md"
        ok, log = run_router(canonical, full_out, chosen_mode, dpi=int(chosen_dpi) if chosen_dpi else None)
        full_chars = 0
        if full_out.exists():
            repaired = conservative_repair(full_out.read_text(encoding="utf-8", errors="replace"))
            full_out.write_text(repaired, encoding="utf-8")
            full_chars = len(repaired.strip())
        manifest_rows.append(
            {
                "source_pdf": str(canonical.relative_to(ROOT)),
                "output_markdown": str(full_out.relative_to(ROOT)),
                "sha256": digest,
                "canonical_pdf": canonical.name,
                "mode": chosen_mode,
                "engine": "router_auto",
                "dpi": chosen_dpi,
                "pages": page_counts[canonical.name],
                "status": "ok" if ok and full_chars else "error_or_empty",
                "title": title,
                "chars": full_chars,
                "notes": log[-500:],
            }
        )

        for dup in sorted(files, key=lambda p: p.name.lower()):
            if dup == canonical:
                continue
            dup_out = OCR_DIR / f"{dup.stem}.md"
            if full_out.exists():
                shutil.copyfile(full_out, dup_out)
            titles[dup.name] = title
            manifest_rows.append(
                {
                    "source_pdf": str(dup.relative_to(ROOT)),
                    "output_markdown": str(dup_out.relative_to(ROOT)),
                    "sha256": digest,
                    "canonical_pdf": canonical.name,
                    "mode": chosen_mode,
                    "engine": "copied_from_canonical",
                    "dpi": chosen_dpi,
                    "pages": page_counts[dup.name],
                    "status": "duplicate_copied" if dup_out.exists() else "duplicate_copy_failed",
                    "title": title,
                    "chars": full_chars,
                    "notes": f"Exact duplicate of {canonical.name}",
                }
            )

    manifest_path = OCR_DIR / "OCR_RUN_MANIFEST.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)

    dup_report = OCR_DIR / "DUPLICATE_PDF_REPORT.md"
    similar_groups = similar_title_groups(titles)
    lines = [
        "# Duplicate PDF Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Exact SHA-256 duplicates",
        "",
    ]
    if duplicate_rows:
        for digest, canonical, duplicates in duplicate_rows:
            lines.append(f"- `{canonical}` is canonical for hash `{digest[:16]}...`; duplicates: " + ", ".join(f"`{d}`" for d in duplicates))
    else:
        lines.append("- No exact duplicate PDFs detected.")
    lines.extend(["", "## Similar titles", ""])
    if similar_groups:
        for group in similar_groups:
            lines.append("- " + ", ".join(f"`{name}`" for name in group))
            for name in group:
                lines.append(f"  - {titles.get(name, '')}")
    else:
        lines.append("- No similar-title groups exceeded the conservative threshold.")
    lines.append("")
    dup_report.write_text("\n".join(lines), encoding="utf-8")

    quality_report = OCR_DIR / "OCR_QUALITY_REPORT.md"
    errors = []
    for errors_path in [OCR_DIR / "ocr_router_errors.json", SAMPLE_DIR / "ocr_router_errors.json"]:
        if errors_path.exists():
            try:
                for item in json.loads(errors_path.read_text(encoding="utf-8")):
                    item["log_path"] = str(errors_path.relative_to(ROOT))
                    errors.append(item)
            except Exception:
                errors.append(
                    {
                        "error_type": "parse_error",
                        "message": f"Could not parse {errors_path.relative_to(ROOT)}",
                        "log_path": str(errors_path.relative_to(ROOT)),
                    }
                )
    deduped_errors = []
    seen_errors = set()
    for err in errors:
        key = (
            err.get("file"),
            err.get("page"),
            err.get("mode"),
            err.get("error_type"),
            err.get("message"),
            err.get("log_path"),
        )
        if key not in seen_errors:
            seen_errors.add(key)
            deduped_errors.append(err)
    errors = deduped_errors

    q = [
        "# OCR Quality Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Environment",
        "",
        "- OCR engines available during probe: native_pdf, easyocr, tesseract, pytesseract_wrapper, rapidocr, paddleocr, surya, marker, doctr.",
        "- Runtime probe classified the machine as local-limited, with CUDA available on NVIDIA GeForce RTX 3050 6GB Laptop GPU.",
        "",
        "## Sample checks",
        "",
        "| PDF | Pages | Mode | Status | Title | Notes |",
        "|---|---:|---|---|---|---|",
    ]
    for row in sample_rows:
        q.append(
            "| {pdf} | {pages} | {mode}{dpi} | {status} | {title} | {notes} |".format(
                pdf=row["pdf"].replace("|", "\\|"),
                pages=row["pages"],
                mode=row["chosen_mode"],
                dpi=(" dpi=" + row["dpi"]) if row["dpi"] else "",
                status=row["sample_status"],
                title=row["title"].replace("|", "\\|"),
                notes=(row["notes"] or "ok").replace("|", "\\|"),
            )
        )
    q.extend(["", "## Full-run summary", ""])
    ok_count = sum(1 for row in manifest_rows if row["status"] in {"ok", "duplicate_copied"})
    q.append(f"- Markdown outputs created: {ok_count}/{len(pdfs)} PDF filenames.")
    q.append(f"- Canonical PDFs OCRed: {len(hash_to_files)}; exact duplicate outputs copied: {len(pdfs) - len(hash_to_files)}.")
    q.append("- Conservative post-processing applied: ftfy mojibake repair, form-feed removal, whitespace cleanup, obvious lowercase hyphenation joins, and blank-line normalization only.")
    q.extend(["", "## Router errors / weak pages", ""])
    if errors:
        for err in errors[-80:]:
            q.append(
                f"- `{err.get('file', 'unknown')}` page `{err.get('page', '')}` "
                f"mode `{err.get('mode', '')}` in `{err.get('log_path', '')}`: "
                f"{err.get('error_type')} {err.get('message', '')}".rstrip()
            )
    else:
        q.append("- No router errors recorded.")
    q.append("")
    quality_report.write_text("\n".join(q), encoding="utf-8")

    print(f"PDFs: {len(pdfs)}")
    print(f"Canonical PDFs: {len(hash_to_files)}")
    print(f"Manifest: {manifest_path}")
    print(f"Quality report: {quality_report}")
    print(f"Duplicate report: {dup_report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
