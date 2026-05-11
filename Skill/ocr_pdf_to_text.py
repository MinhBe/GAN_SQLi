import os
import sys
import argparse

import pdfplumber
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFPageCountError
import pypdfium2 as pdfium
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def safe_print(msg):
    sys.stdout.buffer.write((msg + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()


def extract_text_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text.strip()
    except Exception as e:
        safe_print(f"  pdfplumber error: {e}")
        return ""


def ocr_pdf(pdf_path, dpi=300, lang="eng"):
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
    except (PDFPageCountError, Exception) as e:
        safe_print(f"  pdf2image failed ({e}), trying pypdfium2 fallback...")
        images = []
        pdf = pdfium.PdfDocument(pdf_path)
        for i in range(len(pdf)):
            page = pdf[i]
            bitmap = page.render(scale=dpi / 72)
            img = bitmap.to_pil()
            images.append(img)
        pdf.close()

    text_pages = []
    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img, lang=lang)
        text_pages.append(text)
        safe_print(f"  OCR page {i+1}/{len(images)} done")
    return "\n".join(text_pages)


def convert_pdf_to_text(pdf_path, output_dir=None, force_ocr=False, dpi=300, lang="eng"):
    if not os.path.isfile(pdf_path):
        safe_print(f"File not found: {pdf_path}")
        return

    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{pdf_name}.txt")

    extracted = "" if force_ocr else extract_text_from_pdf(pdf_path)

    if extracted and len(extracted) > 50:
        text = extracted
        method = "pdfplumber"
    else:
        safe_print(f"  Text extraction insufficient ({len(extracted)} chars), running OCR...")
        text = ocr_pdf(pdf_path, dpi=dpi, lang=lang)
        method = "OCR"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    safe_print(f"[{method}] {os.path.basename(pdf_path)} -> {output_path} ({len(text)} chars)")
    return output_path


def process_path(path, output_dir=None, force_ocr=False, dpi=300, lang="eng"):
    if os.path.isfile(path):
        convert_pdf_to_text(path, output_dir, force_ocr, dpi, lang)
    elif os.path.isdir(path):
        pdfs = sorted(f for f in os.listdir(path) if f.lower().endswith(".pdf"))
        if not pdfs:
            safe_print(f"No PDF files found in {path}")
            return
        for fname in pdfs:
            pdf_path = os.path.join(path, fname)
            convert_pdf_to_text(pdf_path, output_dir, force_ocr, dpi, lang)
    else:
        safe_print(f"Path not found: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF to text using OCR fallback")
    parser.add_argument("input", nargs="?", default=None,
                        help="PDF file or directory containing PDFs")
    parser.add_argument("-o", "--output", default=None,
                        help="Output directory (default: same as input)")
    parser.add_argument("--force-ocr", action="store_true",
                        help="Skip text extraction, force OCR")
    parser.add_argument("--dpi", type=int, default=300,
                        help="DPI for OCR (default: 300)")
    parser.add_argument("--lang", default="eng",
                        help="OCR language (default: eng)")
    args = parser.parse_args()

    if args.input is None:
        parser.print_help()
        sys.exit(1)

    process_path(args.input, args.output, args.force_ocr, args.dpi, args.lang)
