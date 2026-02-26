"""
OCR-based invoice field extraction using Tesseract.
Extracts: invoice_number, amount, invoice_date
from uploaded images or PDFs.
"""

import re
import io
from PIL import Image
import pytesseract


def extract_text_from_image(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    return pytesseract.image_to_string(img)


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(pdf_bytes, dpi=300, first_page=1, last_page=3)
        return "\n".join(pytesseract.image_to_string(img) for img in images)
    except Exception as e:
        return ""


def parse_invoice_fields(text: str) -> dict:
    """Parse OCR text and extract invoice fields. Returns best guesses."""
    result = {
        "invoice_number": None,
        "amount": None,
        "invoice_date": None,
        "raw_text": text,
    }

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # --- Invoice Number ---
    inv_patterns = [
        r'(?:invoice|inv|no|number|#)\s*[.:#]?\s*(\w[\w\-\/]+)',
        r'(INV[\-\s]?\d+)',
        r'NO\.\s*(\d+)',
    ]
    for pat in inv_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            result["invoice_number"] = m.group(1).strip()
            break

    # --- Amount (Total) ---
    # Look for "Total" line first, then largest dollar amount
    amount_patterns = [
        r'(?:total|grand\s*total|amount\s*due|balance\s*due|net\s*amount)\s*[:\s]*\$?\s*([\d,]+\.?\d*)',
        r'(?:total|grand\s*total|amount\s*due)\s*\$?\s*([\d,]+\.?\d*)',
    ]
    for pat in amount_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = m.group(1).replace(",", "")
            try:
                result["amount"] = str(float(val))
            except ValueError:
                pass
            break

    # Fallback: find all dollar amounts and pick the largest
    if not result["amount"]:
        dollar_amounts = re.findall(r'\$\s*([\d,]+\.?\d*)', text)
        if dollar_amounts:
            amounts = []
            for a in dollar_amounts:
                try:
                    amounts.append(float(a.replace(",", "")))
                except ValueError:
                    pass
            if amounts:
                result["amount"] = str(max(amounts))

    # --- Date ---
    date_patterns = [
        # 02 June, 2030 / June 02, 2030
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*[,.\s]+\d{4})',
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}[,.\s]+\d{4})',
        # MM/DD/YYYY or MM-DD-YYYY
        r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        # YYYY-MM-DD
        r'(\d{4}[/\-]\d{1,2}[/\-]\d{1,2})',
    ]
    for pat in date_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            raw = m.group(1).strip()
            # Try to normalize to YYYY-MM-DD
            from dateutil.parser import parse as parse_date
            try:
                dt = parse_date(raw)
                result["invoice_date"] = dt.strftime("%Y-%m-%d")
            except Exception:
                result["invoice_date"] = raw
            break

    return result


def ocr_extract(file_bytes: bytes, filename: str) -> dict:
    """Main entry: extract fields from an uploaded file."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    else:
        text = extract_text_from_image(file_bytes)

    if not text.strip():
        return {"invoice_number": None, "amount": None, "invoice_date": None, "raw_text": ""}

    return parse_invoice_fields(text)
