"""
BATCH PROCESSING GUI - Giao diện đơn giản để chọn thư mục và xử lý
===================================================================
"""
import os
import sys
from pathlib import Path

# Cấu hình encoding UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from batch_process import batch_process, find_pdf_files


def select_directory():
    """Mở dialog chọn thư mục"""
    try:
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        directory = filedialog.askdirectory(
            title='Chọn thư mục chứa file PDF'
        )
        
        root.destroy()
        return directory
    except ImportError:
        print("❌ Không thể import tkinter. Vui lòng cài đặt:")
        print("   pip install tk")
        return None


def main():
    print("="*80)
    print("BATCH PROCESSING - XỬ LÝ HÀNG LOẠT FILE PDF")
    print("="*80)
    
    # Chọn thư mục input
    print("\n📁 Chọn thư mục chứa file PDF...")
    input_dir = select_directory()
    
    if not input_dir:
        print("❌ Không có thư mục được chọn. Thoát.")
        return
    
    print(f"✅ Đã chọn: {input_dir}")
    
    # Tìm file PDF
    pdf_files = find_pdf_files(input_dir, recursive=False)
    
    if not pdf_files:
        print(f"\n❌ Không tìm thấy file PDF nào trong thư mục này.")
        
        # Hỏi có muốn tìm kiếm đệ quy không
        response = input("\nTìm kiếm trong các thư mục con? (y/n): ").strip().lower()
        if response == 'y':
            pdf_files = find_pdf_files(input_dir, recursive=True)
            if not pdf_files:
                print("❌ Vẫn không tìm thấy file PDF nào. Thoát.")
                return
            recursive = True
        else:
            return
    else:
        recursive = False
    
    # Hiển thị danh sách file
    print(f"\n✅ Tìm thấy {len(pdf_files)} file PDF:")
    for i, pdf_file in enumerate(pdf_files[:10], 1):
        print(f"   {i}. {os.path.basename(pdf_file)}")
    
    if len(pdf_files) > 10:
        print(f"   ... và {len(pdf_files) - 10} file khác")
    
    # Xác nhận xử lý
    print(f"\n{'='*80}")
    response = input(f"Xử lý {len(pdf_files)} file này? (y/n): ").strip().lower()
    
    if response != 'y':
        print("Hủy bỏ. Thoát.")
        return
    
    # Chọn thư mục output (tùy chọn)
    print("\n📁 Chọn thư mục output (bỏ qua để dùng mặc định)...")
    output_dir = select_directory()
    
    if not output_dir:
        output_dir = 'output_pipeline_complete'
        print(f"   Sử dụng thư mục mặc định: {output_dir}")
    else:
        print(f"   Output: {output_dir}")
    
    # Cấu hình
    print(f"\n{'='*80}")
    print("CẤU HÌNH XỬ LÝ")
    print("="*80)
    
    # Hỏi về LLM
    use_llm_response = input("Sử dụng LLM normalization? (y/n, mặc định: y): ").strip().lower()
    use_llm = use_llm_response != 'n'
    
    # Hỏi về bỏ qua file đã xử lý
    skip_response = input("Bỏ qua file đã xử lý trước đó? (y/n, mặc định: y): ").strip().lower()
    skip_existing = skip_response != 'n'
    
    # Cấu hình pipeline
    pipeline_config = {
        'ocr_dpi': 350,
        'use_llm': use_llm,
        'llm_model': 'gemini-1.5-flash-latest',
        'embedding_model': 'phobert',
        'vector_db': 'faiss',
        'stop_after_llm': False
    }
    
    print(f"\nCấu hình:")
    print(f"  - OCR DPI: {pipeline_config['ocr_dpi']}")
    print(f"  - LLM: {'Bật' if use_llm else 'Tắt'}")
    print(f"  - Bỏ qua file đã xử lý: {'Có' if skip_existing else 'Không'}")
    print(f"  - Tìm kiếm đệ quy: {'Có' if recursive else 'Không'}")
    
    # Xác nhận cuối cùng
    print(f"\n{'='*80}")
    final_response = input("Bắt đầu xử lý? (y/n): ").strip().lower()
    
    if final_response != 'y':
        print("Hủy bỏ. Thoát.")
        return
    
    # Chạy batch processing
    batch_process(
        input_dir=input_dir,
        output_dir=output_dir,
        recursive=recursive,
        skip_existing=skip_existing,
        **pipeline_config
    )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Đã dừng bởi người dùng (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nNhấn Enter để thoát...")
