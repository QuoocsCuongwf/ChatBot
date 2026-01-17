"""
Test nhiều file PDF trong thư mục DataPhuc
"""
import sys
import os
sys.path.insert(0, '.')
from DataCleaning import process_single_pdf

# Thư mục chứa PDF
pdf_dir = '../Data/DataPhuc/'
output_dir = '../Data/processed_json/'

# Lấy danh sách PDF
pdfs = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
print(f"Tìm thấy {len(pdfs)} file PDF")

# Xử lý từng file
for pdf in pdfs:
    print(f"\n{'='*60}")
    print(f"XỬ LÝ: {pdf}")
    print('='*60)
    
    result = process_single_pdf(
        os.path.join(pdf_dir, pdf),
        output_dir=output_dir,
        silent=False
    )
    
    if result['success']:
        stats = result['stats']
        print(f"  ✅ Thành công: {stats['so_chuong']} Chương, {stats['so_dieu']} Điều")
    else:
        print(f"  ❌ Lỗi: {result['error']}")
