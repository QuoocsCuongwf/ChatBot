"""
Rules Base ProtonX - Module sử dụng OCR_paddle_protonX.py cho OCR
Kết hợp PaddleOCR detection + ProtonX recognition
"""
import os
import sys
import json
import argparse
from pathlib import Path

# Cấu hình encoding UTF-8 cho Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Import từ OCR_paddle_protonX.py
from OCR_paddle_protonX import process_pdf as process_pdf_protonx

# Import từ parser.py
from parser import (
    VIETNAMESE_OCR_FIXES,
    clean_text,
    parse_legal_document,
    fix_chapter_numbers,
    fix_vietnamese_ocr_errors,
    apply_context_aware_fixes
)

def apply_ocr_fixes(parsed_data):
    """Áp dụng sửa lỗi OCR cho toàn bộ parsed data"""
    fixed_data = parsed_data.copy()
    
    # Sửa metadata
    if 'metadata' in fixed_data:
        for key, value in fixed_data['metadata'].items():
            if isinstance(value, str):
                fixed_data['metadata'][key] = fix_vietnamese_ocr_errors(value)
    
    # Sửa căn cứ
    if 'can_cu_phap_ly' in fixed_data:
        fixed_data['can_cu_phap_ly'] = [
            fix_vietnamese_ocr_errors(cc) for cc in fixed_data['can_cu_phap_ly']
        ]
    
    # Sửa các chương, điều, khoản
    if 'chuong' in fixed_data:
        for chuong in fixed_data['chuong']:
            if 'ten_chuong' in chuong:
                chuong['ten_chuong'] = fix_vietnamese_ocr_errors(chuong['ten_chuong'])
            
            if 'dieu' in chuong:
                for dieu in chuong['dieu']:
                    if 'noi_dung' in dieu:
                        dieu['noi_dung'] = fix_vietnamese_ocr_errors(dieu['noi_dung'])
                    
                    if 'khoan' in dieu:
                        for khoan in dieu['khoan']:
                            if 'noi_dung' in khoan:
                                khoan['noi_dung'] = fix_vietnamese_ocr_errors(khoan['noi_dung'])
                            
                            if 'diem' in khoan:
                                for diem in khoan['diem']:
                                    if 'noi_dung' in diem:
                                        diem['noi_dung'] = fix_vietnamese_ocr_errors(diem['noi_dung'])
    
    return fixed_data


def count_ocr_fixes(original, fixed):
    """Đếm số lượng sửa lỗi OCR"""
    count = 0
    
    def count_differences(obj1, obj2):
        nonlocal count
        if isinstance(obj1, dict) and isinstance(obj2, dict):
            for key in obj1:
                if key in obj2:
                    count_differences(obj1[key], obj2[key])
        elif isinstance(obj1, list) and isinstance(obj2, list):
            for i in range(min(len(obj1), len(obj2))):
                count_differences(obj1[i], obj2[i])
        elif isinstance(obj1, str) and isinstance(obj2, str):
            if obj1 != obj2:
                count += 1
    
    count_differences(original, fixed)
    return count


def run_full_pipeline_protonx(pdf_path, output_dir=None):
    """
    Pipeline sử dụng PaddleOCR + ProtonX: OCR -> Parse -> Clean
    
    Args:
        pdf_path: Đường dẫn file PDF
        output_dir: Thư mục lưu kết quả
    
    Returns:
        dict: Kết quả JSON đã parse và clean
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {pdf_path}")
    
    # Thiết lập output directory
    if output_dir is None:
        output_dir = Path("output_protonx_pipeline")
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    base_name = pdf_path.stem
    
    print(f"\n{'='*70}")
    print(f"PROTONX PIPELINE - {pdf_path.name}")
    print(f"{'='*70}\n")
    
    # BƯỚC 1: OCR với PaddleOCR + ProtonX
    print("[1/4] Đang chạy OCR với PaddleOCR + ProtonX...")
    
    ocr_output_path = output_dir / f"{base_name}_protonx_ocr.json"
    ocr_results = process_pdf_protonx(str(pdf_path), str(ocr_output_path))
    
    # Trích xuất text từ kết quả OCR
    full_text = ""
    for page_key, page_data in ocr_results.items():
        full_text += page_data["text"] + "\n\n"
    
    print(f"   ✓ Đã OCR: {len(ocr_results)} trang")
    print(f"   ✓ Tổng text: {len(full_text)} ký tự")
    
    # BƯỚC 2: Parse legal structure
    print("\n[2/4] Đang parse cấu trúc văn bản pháp luật...")
    parsed_result = parse_legal_document(full_text)
    
    parsed_output_path = output_dir / f"{base_name}_parsed.json"
    with open(parsed_output_path, 'w', encoding='utf-8') as f:
        json.dump(parsed_result, f, ensure_ascii=False, indent=2)
    
    # Thống kê
    stats = {
        'chuong': len(parsed_result.get('chuong', [])),
        'dieu': 0,
        'khoan': 0
    }
    for chuong in parsed_result.get('chuong', []):
        stats['dieu'] += len(chuong.get('dieu', []))
        for dieu in chuong.get('dieu', []):
            stats['khoan'] += len(dieu.get('khoan', []))
    
    print(f"   ✓ Chương: {stats['chuong']}, Điều: {stats['dieu']}, Khoản: {stats['khoan']}")
    
    # BƯỚC 3: Áp dụng OCR fixes
    print("\n[3/4] Đang áp dụng OCR fixes...")
    cleaned_result = apply_ocr_fixes(parsed_result)
    
    ocr_fixed_path = output_dir / f"{base_name}_ocr_fixed.json"
    with open(ocr_fixed_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_result, f, ensure_ascii=False, indent=2)
    
    fixes_count = count_ocr_fixes(parsed_result, cleaned_result)
    print(f"   ✓ Đã sửa {fixes_count} lỗi OCR")
    
    # BƯỚC 4: Final clean
    print("\n[4/4] Đang làm sạch cuối cùng...")
    final_result = fix_chapter_numbers(cleaned_result)
    
    final_output_path = output_dir / f"{base_name}_final.json"
    with open(final_output_path, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)
    
    # Tóm tắt
    print(f"\n{'='*70}")
    print("✅ HOÀN THÀNH PROTONX PIPELINE")
    print(f"{'='*70}")
    print(f"OCR result:       {ocr_output_path}")
    print(f"Parsed output:    {parsed_output_path}")
    print(f"OCR fixed:        {ocr_fixed_path}")
    print(f"Final output:     {final_output_path}")
    print(f"{'='*70}\n")
    
    return final_result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rules Base Pipeline với ProtonX OCR')
    parser.add_argument('pdf_path', help='Đường dẫn đến file PDF')
    parser.add_argument('-o', '--output-dir', default='output_protonx_pipeline',
                        help='Thư mục lưu kết quả (mặc định: output_protonx_pipeline)')
    
    args = parser.parse_args()
    
    try:
        result = run_full_pipeline_protonx(args.pdf_path, args.output_dir)
        print(f"\n✅ Thành công! Kết quả được lưu tại: {args.output_dir}")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
