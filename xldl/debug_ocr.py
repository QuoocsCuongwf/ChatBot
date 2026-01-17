import json
from pdf2image import convert_from_path
import pytesseract
import re

# Config
POPPLER_PATH = r"D:\apps\Poppler\poppler-25.12.0\Library\bin"
TESSERACT_PATH = r"D:\apps\OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Extract specific pages with chapters
pdf_path = "F:/NghienCuuKhoaHoc/Data/DataPhuc/127-cp.signed._tài sản côngpdf.pdf"
pages_to_check = [1, 3, 5, 12, 16]

for page_num in pages_to_check:
    print(f"\n{'='*60}")
    print(f"Page {page_num}")
    print('='*60)
    
    images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH, first_page=page_num, last_page=page_num)
    text = pytesseract.image_to_string(images[0], config='--oem 1 --psm 6 -l vie')
    
    # Find all Chuong lines
    for line in text.split('\n'):
        if re.search(r'Chương|CHƯƠNG', line, re.IGNORECASE):
            print(f"  >> {line}")
