---
name: mistral-ocr
description: >-
  Extract text from images and PDFs using a local OCR engine (EasyOCR). Works
  completely offline — no API key, no network calls, no data leaves your
  machine. Use when the user needs to OCR a document, extract text from
  scanned PDFs/images, digitize printed documents, or convert PDF/image to
  Markdown/plain text without sending data to any external service. Fully
  air-gap compatible.
compatibility: python3, easyocr, PyMuPDF
---

# OCR PDF (Offline)

Fully local OCR processor. No API key, no internet, no data sent anywhere.

## Requirements

```bash
pip install -r requirements.txt
```

First run downloads EasyOCR models (~100MB) — after that, fully offline.

## Two Modes

| Mode | Technology | Paragraph | Use Case | Speed |
|------|------------|-----------|----------|-------|
| `fast` | Native Text Extraction | No | Digital PDFs with text layer | **Instant** |
| `max` | EasyOCR (Offline) | Yes | Scanned PDFs, Images, difficult docs | Slow |

- **Fast** is default — Near-instant, uses PyMuPDF to extract existing text. Skips images.
- **Max** uses deep learning (EasyOCR) to read text from pixels. 10-50x slower but works on anything.

## Usage

```bash
# Fast (default)
python scripts/ocr_processor.py --input paper.pdf --output paper.md

# Max quality
python scripts/ocr_processor.py --input paper.pdf --output paper.md --mode max

# Override DPI manually
python scripts/ocr_processor.py --input paper.pdf --output paper.md --mode max --dpi 400
```

### Flags

| Flag | Description |
|------|-------------|
| `--input` / `-i` | Path to PDF, PNG, JPG, WEBP, GIF |
| `--output` / `-o` | Output `.md` file (default: stdout) |
| `--mode` | `fast` (default) or `max` |
| `--lang` | Language code(s) (default: `en`) |
| `--dpi` | Override DPI (overrides mode default) |
| `--page-separator` | Text between pages (default: `---`) |
| `--include-images` | Save rendered page images as PNG |
| `--gpu` | Use GPU if available |

## Error Detection

The script auto-detects problems and writes to `ocr_errors.json` in the output directory:

| Error Type | Meaning |
|------------|---------|
| `exception` | File corrupt, encrypted, or unreadable |
| `empty_output` | OCR returned no text at all |
| `output_too_short` | Very little text extracted (< 50 chars) |

### Batch Pipeline

```powershell
# Step 1: Fast batch
foreach ($pdf in Get-ChildItem "*.pdf") {
  python scripts/ocr_processor.py --input $pdf --output "out/$($pdf.BaseName).md" --mode fast
}

# Step 2: Check errors.json, retry failed with --mode max
$errors = Get-Content "out/ocr_errors.json" | ConvertFrom-Json
foreach ($e in $errors) {
  python scripts/ocr_processor.py --input $e.path --output "out/$($e.file -replace '.pdf','.md')" --mode max
}
```

## Examples

```bash
# Fast batch all PDFs in folder
python scripts/ocr_processor.py --input scan.png

# Vietnamese with max quality
python scripts/ocr_processor.py --input doc.pdf --lang vi --mode max --output doc.md

# Extract page images too
python scripts/ocr_processor.py --input doc.pdf --output doc.md --include-images
```

## Supported Formats

PDF, PNG, JPG/JPEG, WEBP, GIF — all processed locally.
