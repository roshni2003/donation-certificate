import os
import re
import requests
from pathlib import Path
from datetime import datetime
from num2words import num2words
from docxtpl import DocxTemplate
import subprocess
import shutil
import pandas as pd

# ---------- CONFIG ----------
API_URL = "https://script.google.com/macros/s/AKfycbxvvE91tWxzYUzrrrZTcaNWHB4yYIGcZ7dxmRGYwYjP9OZteYrgaWeoCcDZHC3UMPFY/exec"  # replace this
TEMPLATE_FILE = "template.docx"
OUTPUT_EDITABLE_DIR = Path("output/Editable")
OUTPUT_PDF_DIR = Path("output/PDF")
# ----------------------------

OUTPUT_EDITABLE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PDF_DIR.mkdir(parents=True, exist_ok=True)

USE_DOCX2PDF = True
try:
    from docx2pdf import convert as docx2pdf_convert
except:
    USE_DOCX2PDF = False

def safe_filename(s):
    s = re.sub(r'[\\/:"*?<>|]+', '', s)
    return s.strip().replace(" ", "_")

def amount_to_words(amount):
    try:
        n = int(float(amount))
    except:
        return f"INR {str(amount).strip()} Rupees"
    words = num2words(n).replace(",", "").replace(" and", "").title()
    return f"INR {words} Rupees"

def convert_docx_to_pdf(docx_file, pdf_file):
    if USE_DOCX2PDF:
        try:
            docx2pdf_convert(docx_file, pdf_file)
            return True
        except:
            pass

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        try:
            subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(OUTPUT_PDF_DIR), docx_file], check=True)
            return True
        except:
            return False

    print("Install MS Word or LibreOffice to enable PDF conversion.")
    return False

def fetch_sheet_data():
    res = requests.get(API_URL)
    res.raise_for_status()
    return pd.DataFrame(res.json())

def main():
    df = fetch_sheet_data()
    print(f"Fetched {len(df)} records")

    for i, row in df.iterrows():
        serial = str(row.get("Serial_No", "")).strip()
        date_val = str(row.get("Date", "")).strip()
        name = str(row.get("Name", "")).strip()
        address = str(row.get("Address", "")).strip()
        amount = row.get("Amount", "")
        pan = str(row.get("PAN", "")).strip()

        # Handle ISO like 2024-11-03T18:30:00.000Z
        if "T" in date_val:
            try:
                dt = datetime.fromisoformat(date_val.replace("Z", ""))
                date_val = dt.strftime("%d/%m/%y")
            except:
                pass

        # Handle YYYY-MM-DD
        elif re.match(r'^\d{4}-\d{2}-\d{2}$', date_val):
            dt = datetime.strptime(date_val, "%Y-%m-%d")
            date_val = dt.strftime("%d/%m/%y")


        amount_words = amount_to_words(amount)

        context = {
            "Serial_No": serial,
            "Date": date_val,
            "Name": name,
            "Address": address,
            "PAN": pan,
            "Amount_in_words": amount_words
        }

        doc = DocxTemplate(TEMPLATE_FILE)
        doc.render(context)

        base_name = f"{serial}_{name}" if serial and name else f"record_{i}"
        safe_name = safe_filename(base_name)

        docx_path = OUTPUT_EDITABLE_DIR / f"{safe_name}.docx"
        pdf_path = OUTPUT_PDF_DIR / f"{safe_name}.pdf"

        doc.save(docx_path)
        print(f"✅ Saved DOCX: {docx_path}")

        if convert_docx_to_pdf(str(docx_path), str(pdf_path)):
            print(f"✅ Saved PDF: {pdf_path}")
        else:
            print(f"⚠️ PDF failed for {docx_path} — open Word & export manually")

if __name__ == "__main__":
    main()
