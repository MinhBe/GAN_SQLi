# PDF to Markdown Conversion

Convert PDF documents to structured Markdown using the Mistral OCR processor script.

## Overview

Mistral OCR processes PDFs **directly** - no need to convert to images first! The `ocr_processor.py` script handles the entire process: file encoding, API call, and markdown extraction.

## Quick Example

```bash
python scripts/ocr_processor.py --input document.pdf --output document.md
```

That's it! No pdftoppm, no ImageMagick, no base64, no curl.

---

## Usage

### Basic PDF to Markdown

```bash
python scripts/ocr_processor.py --input report.pdf --output report.md
```

### Multi-Page PDF with Custom Separators

The script combines all pages automatically (default separator: `\n\n---\n\n`):

```bash
python scripts/ocr_processor.py --input multipage.pdf --output full.md --page-separator "\n\n## Page Break\n\n"
```

### HTML Table Format (complex tables)

```bash
python scripts/ocr_processor.py --input financial_report.pdf --output report.md --table-format html
```

Use this for PDFs with merged cells, `colspan`, or `rowspan`.

### Include Embedded Images

PDFs with embedded images (scanned documents, diagrams):

```bash
python scripts/ocr_processor.py --input doc.pdf --output doc.md --include-images
```

Images are saved to `doc_images/` directory.

---

## Response Structure

The API returns structured JSON (the script handles this internally):

```json
{
  "pages": [
    {
      "index": 0,
      "markdown": "# Page Title\n\nContent here...",
      "images": [],
      "tables": [],
      "dimensions": {"dpi": 200, "height": 842, "width": 595}
    },
    {
      "index": 1,
      "markdown": "## Second Page\n\nMore content...",
      "images": [],
      "tables": []
    }
  ],
  "model": "mistral-ocr-latest",
  "usage_info": {
    "pages_processed": 2,
    "doc_size_bytes": 45678
  }
}
```

---

## Quality Tips

| Issue | Solution |
|-------|----------|
| Blurry text | Use higher quality PDF source |
| Tables broken | Use `--table-format html` |
| Headers missed | OCR 3 has improved header detection |
| Columns merged | OCR 3 better handles multi-column layouts |


---

## Prompt Variations (via Document QnA)

For specialized extraction, combine OCR with Mistral's Document QnA:

### Legal Documents
```
"Extract all article numbers, sections, and subsections. Keep citations intact."
```

### Academic Papers
```
"Extract content preserving equations (LaTeX notation) and figure references."
```

### Invoices/Forms
```
"Extract as structured data: invoice number, date, line items, totals."
```

---

## Comparison: Old vs New Approach

| Aspect | Old (Vision API) | New (OCR API) |
|--------|------------------|---------------|
| Dependencies | pdftoppm/ImageMagick required | None |
| Steps | PDF → Images → OCR | PDF → OCR directly |
| Speed | Slow (convert + multiple calls) | Fast (single call) |
| Cost | Higher (per-image) | Lower ($2/1000 pages) |
| Table quality | Basic | HTML with colspan/rowspan |

---

## Limitations

- **Maximum file size:** Check current limits at Mistral docs
- **Encrypted PDFs:** Must be unencrypted
- **Handwritten text:** Works but accuracy varies
- **Very complex layouts:** May need post-processing

---

## Output Example

**Input:** Scanned contract page

**Output:**
```markdown
# Service Agreement

**Date:** January 15, 2026
**Parties:** Company A and Company B

## Article 1: Scope of Services

The Provider agrees to deliver the following services:

1. Software development
2. Technical support
3. Monthly maintenance

## Article 2: Payment Terms

| Milestone | Amount | Due Date |
|-----------|--------|----------|
| Signing | $5,000 | Jan 20 |
| Delivery | $10,000 | Mar 15 |
```
