# Step-by-Step Guide

Complete tutorial for using the Mistral OCR processor script.

## Quick Start

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Get Your API Key

If you don't have a Mistral API key yet:

1. Go to [console.mistral.ai](https://console.mistral.ai/)
2. Create an account or sign in
3. Go to **API Keys** → **Create new key**
4. Copy your key

### 3. Set Up Your Key

```bash
# Windows PowerShell
$env:MISTRAL_API_KEY = "your-key-here"

# Linux/macOS
export MISTRAL_API_KEY="your-key-here"
```

Or pass it directly:

```bash
python scripts/ocr_processor.py --input doc.pdf --api-key "your-key-here"
```

### 4. Test It Works

```bash
python scripts/ocr_processor.py --input path/to/any.pdf
```

---

## Basic Usage

### Local PDF to Markdown

```bash
python scripts/ocr_processor.py --input report.pdf --output report.md
```

### Local Image to Markdown (stdout)

```bash
python scripts/ocr_processor.py --input screenshot.png
```

### HTML Table Format (complex tables)

```bash
python scripts/ocr_processor.py --input invoice.pdf --output invoice.md --table-format html
```

### Extract Embedded Images

```bash
python scripts/ocr_processor.py --input doc.pdf --output doc.md --include-images
```

Images save to `doc_images/` folder next to the output file.

### Custom Page Separator

```bash
python scripts/ocr_processor.py --input doc.pdf --output doc.md --page-separator "\n\n## Page Break\n\n"
```

---

## Batch Processing Multiple Files

```powershell
foreach ($pdf in Get-ChildItem -Filter "*.pdf") {
  $out = "output/$($pdf.BaseName).md"
  python scripts/ocr_processor.py --input $pdf.FullName --output $out
}
```

---

## Common Issues & Solutions

### Issue: `MISTRAL_API_KEY not set`

Provide the key via `--api-key` flag or set the `MISTRAL_API_KEY` environment variable.

### Issue: `Unsupported file format`

The script supports PDF, PNG, JPG, WEBP, GIF only.

### Issue: `Unauthorized (401)`

Your API key is invalid or has no credits. Check at [console.mistral.ai](https://console.mistral.ai/).

### Issue: Large file timeout

For very large files (>50 MB), consider splitting the PDF into smaller parts.

---

## Tips for Best Results

1. **Document Quality** — Higher resolution = better OCR
2. **Tables** — Use `--table-format html` for complex tables with merged cells
3. **Multi-page** — All pages are combined automatically with separators
4. **Images** — Use `--include-images` to extract embedded document images

---

## Next Steps

- See [formats.md](formats.md) for JSON and structured output options
- See [pdf-to-markdown.md](pdf-to-markdown.md) for advanced PDF handling
- Check Mistral docs at [docs.mistral.ai](https://docs.mistral.ai/capabilities/document_ai)
