#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script để test xử lý PDF scan"""

import sys
sys.path.insert(0, 'f:/NghienCuuKhoaHoc/xldl')

from DataCleaning import process_single_pdf, is_text_pdf
import os

# Kiểm tra các file PDF scan
pdf_files = [
    "F:/NghienCuuKhoaHoc/Data/DataPhuc/127-cp.signed._tài sản côngpdf.pdf",
    "F:/NghienCuuKhoaHoc/Data/DataPhuc/120-cp.signed_qlyBTP.pdf",
]

print("=" * 70)
print("KIỂM TRA LOẠI PDF (TEXT vs SCAN)")
print("=" * 70)

for pdf_path in pdf_files:
    if os.path.exists(pdf_path):
        is_scan = not is_text_pdf(pdf_path)
        loai = "SCAN" if is_scan else "TEXT"
        print(f"\n{os.path.basename(pdf_path)}")
        print(f"  Loại: {loai}")
    else:
        print(f"\n{os.path.basename(pdf_path)}")
        print(f"  ❌ File không tồn tại")

print("\n" + "=" * 70)
print("XỬ LÝ FILE PDF SCAN ĐẦUTIÊN")
print("=" * 70)

if os.path.exists(pdf_files[0]):
    print(f"\nXử lý: {os.path.basename(pdf_files[0])}")
    result = process_single_pdf(
        pdf_files[0],
        output_dir="F:/NghienCuuKhoaHoc/Data/processed_json",
        dpi=300,
        silent=False
    )
    
    print(f"\nKết quả:")
    print(f"  Thành công: {result['success']}")
    if result['success']:
        print(f"  File output: {result['output_file']}")
        print(f"  Thống kê: {result['stats']}")
    else:
        print(f"  Lỗi: {result['error']}")
