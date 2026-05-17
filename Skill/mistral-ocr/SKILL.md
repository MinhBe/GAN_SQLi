---
name: mistral-ocr
description: >-
  Extract text from images and PDFs using Mistral OCR API. Convert scanned
  documents, receipts, invoices, contracts, or any image/PDF to Markdown, plain
  text, or structured output. Use when the user asks to OCR a document, extract
  text from an image/PDF, convert a scanned PDF to Markdown, digitize a
  document, or extract tables from a document. Requires a Mistral API key and
  Python with 'requests' installed.
compatibility: python3, requests, MISTRAL_API_KEY
---

# Mistral OCR

Extract text from PDFs and images (PNG, JPG, WEBP, GIF) using Mistral's OCR API via the `scripts/ocr_processor.py` CLI tool.

## Requirements

- Python 3.8+
- `pip install requests`
- `MISTRAL_API_KEY` environment variable (or `--api-key` flag)
- Get a key at [console.mistral.ai](https://console.mistral.ai/) — see [references/getting-started.md](references/getting-started.md)

## Quick Start

```bash
python scripts/ocr_processor.py --input document.pdf --output document.md
```

## API Key

The model will look for the key in this order:
1. `--api-key` argument (user provides inline)
2. `$MISTRAL_API_KEY` environment variable
3. Ask the user to provide one (guide them to `references/getting-started.md`)

## Usage

```bash
# Local PDF to Markdown
python scripts/ocr_processor.py --input report.pdf --output report.md

# Local image to Markdown (stdout)
python scripts/ocr_processor.py --input screenshot.png

# HTML table format for complex tables
python scripts/ocr_processor.py --input invoice.pdf --output invoice.md --table-format html

# Extract images embedded in the document
python scripts/ocr_processor.py --input doc.pdf --output doc.md --include-images

# Custom page separator
python scripts/ocr_processor.py --input doc.pdf --output doc.md --page-separator "\n\n## Page Break\n\n"
```

| Flag | Description |
|------|-------------|
| `--input` / `-i` | Path to input file (PDF, PNG, JPG, WEBP, GIF) |
| `--output` / `-o` | Output .md file path (default: stdout) |
| `--api-key` | Mistral API key (overrides `$MISTRAL_API_KEY`) |
| `--table-format` | `markdown` (default) or `html` |
| `--page-separator` | Text between pages (default: `---`) |
| `--include-images` | Save embedded images to `{output_name}_images/` |
| `--include-usage` | Print token/page usage to stderr |

## Supported Formats

PDF, PNG, JPG/JPEG, WEBP, GIF — processed directly without external converters.

## Workflow

When the user requests OCR:
1. Check `MISTRAL_API_KEY` is set (ask user if not)
2. Run `python scripts/ocr_processor.py --input "<file>" --output "<file>.md"`
3. If they want images too, add `--include-images`
4. If tables are complex, add `--table-format html`
5. Confirm the output file location to the user

## Error Handling

| Error | Likely Cause |
|-------|-------------|
| `MISTRAL_API_KEY not set` | No API key provided |
| `File not found` | Invalid input path |
| `Unsupported file format` | Wrong extension |
| `Unauthorized (401)` | Invalid or expired API key |
| `Bad request (400)` | Unreadable/encrypted file |
| `Rate limited (429)` | Too many requests — wait and retry |

## References

- [Getting Started](references/getting-started.md) — API key setup
- [Guide](references/guide.md) — Detailed usage examples
- [Output Formats](references/formats.md) — Markdown, JSON, plain text, CSV
- [PDF to Markdown](references/pdf-to-markdown.md) — PDF-specific tips
