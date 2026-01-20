"""
Rules Base - Module sửa lỗi OCR và làm sạch văn bản pháp luật
Sử dụng DataCleaning.py cho OCR và parser.py cho parsing
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
        # Fallback for Python < 3.7
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Import từ DataCleaning.py (xử lý OCR)
from DataCleaning import process_single_pdf, is_text_pdf, extract_text_pdf

# Import từ parser.py (xử lý parsing và làm sạch)
from parser import (
    VIETNAMESE_OCR_FIXES,
    clean_text,
    parse_legal_document,
    fix_chapter_numbers,
    fix_vietnamese_ocr_errors,
    apply_context_aware_fixes
)

def run_full_pipeline(pdf_path, output_dir=None):
    """
    Chạy toàn bộ pipeline: OCR -> Parse -> Clean với sửa lỗi OCR
    
    Args:
        pdf_path: Đường dẫn file PDF
        output_dir: Thư mục lưu kết quả (mặc định: output_pipeline)
    
    Returns:
        dict: Kết quả JSON đã parse và clean với OCR fixes
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {pdf_path}")
    
    # Thiết lập output directory
    if output_dir is None:
        output_dir = Path("output_pipeline")
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Tên file không có extension
    base_name = pdf_path.stem
    
    print(f"\n{'='*60}")
    print(f"RULES BASE PIPELINE - {pdf_path.name}")
    print(f"{'='*60}\n")
    
    # BƯỚC 1: OCR (sử dụng DataCleaning.py)
    print("[1/4] Đang chạy OCR với DataCleaning...")
    
    # Kiểm tra loại PDF
    is_scan = not is_text_pdf(str(pdf_path))
    pdf_type = "scan (ảnh)" if is_scan else "text"
    print(f"   Loại PDF: {pdf_type}")
    
    # Trích xuất text từ PDF
    if is_scan:
        # Sử dụng process_single_pdf từ DataCleaning cho file scan
        result = process_single_pdf(str(pdf_path), str(output_dir), silent=False)
        if not result["success"]:
            raise ValueError(f"OCR thất bại: {result.get('error', 'Unknown error')}")
        
        # Load kết quả đã xử lý
        with open(result["output_file"], 'r', encoding='utf-8') as f:
            parsed_result = json.load(f)
        
        # Lưu metadata
        raw_text = ""  # Không cần lưu raw text cho scan
        ocr_output_path = output_dir / f"{base_name}_ocr_result.json"
        with open(ocr_output_path, 'w', encoding='utf-8') as f:
            json.dump({"type": "scan", "stats": result["stats"]}, f, ensure_ascii=False, indent=2)
        
        print(f"   Đã OCR: {result['stats']['so_trang']} trang")
    else:
        # Trích xuất text trực tiếp
        raw_text = extract_text_pdf(str(pdf_path))
        print(f"   Đã trích xuất: {len(raw_text)} ký tự")
        
        # Lưu raw text
        ocr_output_path = output_dir / f"{base_name}_raw_text.txt"
        with open(ocr_output_path, 'w', encoding='utf-8') as f:
            f.write(raw_text)
        print(f"   Lưu raw text: {ocr_output_path}")
        
        # BƯỚC 2: Parse legal structure (sử dụng parser.py)
        print("\n[2/4] Đang parse cấu trúc văn bản pháp luật...")
        parsed_result = parse_legal_document(raw_text)
        
        # Lưu kết quả parsed
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
        
        print(f"   Chương: {stats['chuong']}, Điều: {stats['dieu']}, Khoản: {stats['khoan']}")
    
    # BƯỚC 3: Áp dụng OCR fixes (sửa lỗi chính tả)
    print("\n[3/4] Đang áp dụng OCR fixes để sửa lỗi chính tả...")
    cleaned_result = apply_ocr_fixes(parsed_result)
    
    ocr_fixed_path = output_dir / f"{base_name}_ocr_fixed.json"
    with open(ocr_fixed_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_result, f, ensure_ascii=False, indent=2)
    print(f"   Đã sửa {count_ocr_fixes(parsed_result, cleaned_result)} lỗi OCR")
    print(f"   Lưu file đã sửa: {ocr_fixed_path}")
    
    # BƯỚC 4: Final clean và fix chapter numbers
    print("\n[4/4] Đang làm sạch cuối cùng...")
    final_result = fix_chapter_numbers(cleaned_result)
    
    final_output_path = output_dir / f"{base_name}_final.json"
    with open(final_output_path, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)
    print(f"   Lưu kết quả cuối: {final_output_path}")
    
    # Tóm tắt
    print(f"\n{'='*60}")
    print("HOÀN THÀNH PIPELINE")
    print(f"{'='*60}")
    if is_scan:
        print(f"OCR result:       {ocr_output_path}")
    else:
        print(f"Raw text:         {ocr_output_path}")
        print(f"Parsed output:    {parsed_output_path}")
    print(f"OCR fixed:        {ocr_fixed_path}")
    print(f"Final output:     {final_output_path}")
    print(f"{'='*60}\n")
    
    return final_result

def apply_ocr_fixes(data):
    """
    Áp dụng OCR fixes cho toàn bộ JSON structure để sửa lỗi chính tả
    Sử dụng từ điển VIETNAMESE_OCR_FIXES từ parser.py
    """
    if isinstance(data, dict):
        return {k: apply_ocr_fixes(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [apply_ocr_fixes(item) for item in data]
    elif isinstance(data, str):
        # Áp dụng fixes từ parser.py
        result = fix_vietnamese_ocr_errors(data)
        result = apply_context_aware_fixes(result)
        return result
    else:
        return data

def count_ocr_fixes(original, fixed):
    """
    Đếm số lượng sửa lỗi OCR đã thực hiện
    """
    count = 0
    
    def compare_strings(orig, fix):
        nonlocal count
        if isinstance(orig, str) and isinstance(fix, str):
            if orig != fix:
                # Đếm số từ khác nhau
                for wrong, correct in VIETNAMESE_OCR_FIXES.items():
                    if wrong in orig:
                        count += orig.count(wrong)
        elif isinstance(orig, dict) and isinstance(fix, dict):
            for key in orig.keys():
                if key in fix:
                    compare_strings(orig[key], fix[key])
        elif isinstance(orig, list) and isinstance(fix, list):
            for i in range(min(len(orig), len(fix))):
                compare_strings(orig[i], fix[i])
    
    compare_strings(original, fixed)
    return count

def fix_existing_json(json_path, output_path=None):
    """
    Sửa lỗi OCR cho file JSON đã tồn tại
    
    Args:
        json_path: Đường dẫn file JSON cần sửa
        output_path: Đường dẫn lưu kết quả (mặc định: ghi đè file gốc)
    
    Returns:
        dict: Kết quả JSON đã được sửa lỗi OCR
    """
    if output_path is None:
        output_path = json_path
    
    print(f"\nĐang sửa lỗi OCR cho file: {json_path}")
    
    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Áp dụng OCR fixes
    fixed_data = apply_ocr_fixes(data)
    
    # Fix chapter numbers nếu có
    if 'chuong' in fixed_data:
        fixed_data = fix_chapter_numbers(fixed_data)
    
    # Lưu kết quả
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)
    
    num_fixes = count_ocr_fixes(data, fixed_data)
    print(f"✅ Đã sửa {num_fixes} lỗi OCR")
    print(f"   Lưu tại: {output_path}")
    
    return fixed_data

def main():
    parser = argparse.ArgumentParser(
        description="Rules Base - Sửa lỗi OCR và làm sạch văn bản pháp luật",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Chế độ sử dụng:

1. Xử lý PDF hoàn chỉnh (OCR -> Parse -> Sửa lỗi):
   python rules_base.py document.pdf
   python rules_base.py document.pdf -o output_custom
   
2. Chỉ sửa lỗi OCR cho file JSON đã tồn tại:
   python rules_base.py -f existing.json
   python rules_base.py -f input.json -o output.json

Ví dụ:
  python rules_base.py "F:/docs/127-NDCP.pdf" -o "F:/results"
  python rules_base.py -f "Data/processed.json" -o "Data/fixed.json"
        """
    )
    
    # Tạo group cho các chế độ
    group = parser.add_mutually_exclusive_group(required=True)
    
    group.add_argument(
        'pdf_path',
        nargs='?',
        help="Đường dẫn đến file PDF cần xử lý"
    )
    
    group.add_argument(
        '-f', '--fix-json',
        metavar='JSON_FILE',
        help="Sửa lỗi OCR cho file JSON đã tồn tại"
    )
    
    parser.add_argument(
        '-o', '--output',
        default=None,
        help="Thư mục/file lưu kết quả (mặc định: output_pipeline hoặc ghi đè file gốc)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.fix_json:
            # Chế độ sửa JSON
            fix_existing_json(args.fix_json, args.output)
        elif args.pdf_path:
            # Chế độ xử lý PDF đầy đủ
            run_full_pipeline(args.pdf_path, args.output)
        else:
            parser.print_help()
            sys.exit(1)
        
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Lỗi: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
