import argparse
import base64
import os
import sys
import json
from pathlib import Path

import requests

API_URL = "https://api.mistral.ai/v1/ocr"
DEFAULT_MODEL = "mistral-ocr-latest"

MIME_MAP = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}

SUPPORTED_EXTENSIONS = set(MIME_MAP.keys())


def detect_mime(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext not in MIME_MAP:
        supported = ", ".join(SUPPORTED_EXTENSIONS)
        print(
            f"Error: Unsupported file format '{ext}'. Supported: {supported}",
            file=sys.stderr,
        )
        sys.exit(1)
    return MIME_MAP[ext]


def encode_file(file_path: str) -> str:
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied: {file_path}", file=sys.stderr)
        sys.exit(1)


def call_mistral_ocr(api_key: str, b64_data: str, mime: str, table_format: str | None) -> dict:
    document_url = f"data:{mime};base64,{b64_data}"
    payload = {
        "model": DEFAULT_MODEL,
        "document": {
            "type": "document_url",
            "document_url": document_url,
        },
    }
    if table_format:
        payload["table_format"] = table_format

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=300)
    if resp.status_code == 401:
        print(
            "Error: Unauthorized (401). Check your Mistral API key.",
            file=sys.stderr,
        )
        sys.exit(1)
    elif resp.status_code == 400:
        body = resp.text[:500]
        print(
            f"Error: Bad request (400). Response: {body}",
            file=sys.stderr,
        )
        sys.exit(1)
    elif resp.status_code == 429:
        print(
            "Error: Rate limited (429). Wait and try again.",
            file=sys.stderr,
        )
        sys.exit(1)
    elif resp.status_code != 200:
        body = resp.text[:500]
        print(
            f"Error: API returned HTTP {resp.status_code}. Response: {body}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        return resp.json()
    except json.JSONDecodeError:
        print(
            f"Error: Invalid JSON response: {resp.text[:500]}",
            file=sys.stderr,
        )
        sys.exit(1)


def extract_markdown(data: dict, page_separator: str) -> str:
    pages = data.get("pages", [])
    if not pages:
        return ""
    markdown_parts = []
    for p in pages:
        md = p.get("markdown", "")
        if md:
            markdown_parts.append(md)
    return page_separator.join(markdown_parts)


def extract_images(data: dict, output_dir: str, base_name: str):
    pages = data.get("pages", [])
    images_dir = Path(output_dir) / f"{base_name}_images"
    images_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for p in pages:
        page_idx = p.get("index", 0)
        for img_idx, img in enumerate(p.get("images", [])):
            b64_str = img.get("image_base64", "")
            if not b64_str:
                continue
            try:
                img_data = base64.b64decode(b64_str)
                img_path = images_dir / f"page_{page_idx + 1}_img_{img_idx + 1}.png"
                img_path.write_bytes(img_data)
                count += 1
            except Exception as e:
                print(
                    f"Warning: Could not decode image on page {page_idx + 1}: {e}",
                    file=sys.stderr,
                )
    return count, str(images_dir)


def parse_args():
    parser = argparse.ArgumentParser(
        description="OCR processor using Mistral OCR API. Supports PDF, PNG, JPG, WEBP, GIF."
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to input file (PDF, PNG, JPG, WEBP, GIF)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output .md file (default: stdout)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Mistral API key (default: $MISTRAL_API_KEY env var)",
    )
    parser.add_argument(
        "--table-format",
        choices=["markdown", "html"],
        default=None,
        help="Table output format (default: markdown)",
    )
    parser.add_argument(
        "--page-separator",
        default="\n\n---\n\n",
        help="Separator between pages (default: '---')",
    )
    parser.add_argument(
        "--include-images",
        action="store_true",
        help="Extract embedded images from OCR response",
    )
    parser.add_argument(
        "--include-usage",
        action="store_true",
        help="Print usage information to stderr",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    input_path = args.input
    if not os.path.isfile(input_path):
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    api_key = args.api_key or os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print(
            "Error: MISTRAL_API_KEY not set. Provide via --api-key or $MISTRAL_API_KEY env var.",
            file=sys.stderr,
        )
        sys.exit(1)

    mime = detect_mime(input_path)
    b64_data = encode_file(input_path)

    print(f"Processing: {input_path} ({mime})", file=sys.stderr)
    data = call_mistral_ocr(api_key, b64_data, mime, args.table_format)

    markdown_text = extract_markdown(data, args.page_separator)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown_text, encoding="utf-8")
        pages_processed = data.get("usage_info", {}).get("pages_processed", 0)
        print(f"Saved: {output_path} ({pages_processed} pages)", file=sys.stderr)
    else:
        sys.stdout.write(markdown_text)
        if markdown_text and not markdown_text.endswith("\n"):
            sys.stdout.write("\n")

    if args.include_images and data.get("pages"):
        base_name = Path(args.output or input_path).stem
        output_dir = Path(args.output or ".").parent if args.output else Path(".")
        img_count, img_dir = extract_images(data, str(output_dir), base_name)
        print(f"Extracted {img_count} images to: {img_dir}", file=sys.stderr)

    if args.include_usage:
        usage = data.get("usage_info", {})
        print(f"Usage: {json.dumps(usage)}", file=sys.stderr)


if __name__ == "__main__":
    main()
