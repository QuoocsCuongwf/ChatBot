import sys
sys.path.insert(0, '.')
from DataCleaning import process_single_pdf, convert_from_path, POPPLER_PATH, ocr_from_images_parallel

pdf_path = '../Data/DataPhuc/127-cp.signed._tài sản côngpdf.pdf'

# Chuyển PDF sang ảnh
print("Chuyển PDF sang ảnh...")
images = convert_from_path(pdf_path, dpi=350, poppler_path=POPPLER_PATH)

# OCR
print("OCR...")
raw_text = ocr_from_images_parallel(images, silent=True)

# Tìm pattern "Chương" với context
import re
print("\n--- Các dòng chứa 'Chương' trong OCR (raw) ---")
for line in raw_text.split('\n'):
    if 'chương' in line.lower():
        print(f"  RAW: '{line[:100]}'")

# In một phần của text tìm xung quanh Điều 13, 14 (nơi Chương III nên xuất hiện)
print("\n--- Text xung quanh 'Điều 13' và 'Điều 14' ---")
idx_13 = raw_text.lower().find('điều 13')
if idx_13 > 0:
    print(raw_text[idx_13-200:idx_13+300])

print("\n--- Tìm 'Chương III' hoặc 'CHƯƠNG III' ---")
matches = re.findall(r'(Chương|CHƯƠNG)\s+\S{1,5}', raw_text)
for m in matches:
    print(f"  '{m}'")
