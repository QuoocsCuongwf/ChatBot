"""
BATCH PROCESSING - Xử lý tất cả file PDF trong thư mục
========================================================
Script này sẽ tự động xử lý tất cả file PDF trong thư mục được chỉ định
"""
import os
import sys
import argparse
from pathlib import Path
from typing import List
import time

# Cấu hình encoding UTF-8 cho Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from complete_pipeline import CompletePipeline


def find_pdf_files(directory: str, recursive: bool = False) -> List[str]:
    """
    Tìm tất cả file PDF trong thư mục
    
    Args:
        directory: Đường dẫn thư mục
        recursive: Tìm kiếm đệ quy trong các thư mục con
        
    Returns:
        Danh sách đường dẫn file PDF
    """
    pdf_files = []
    
    if recursive:
        # Tìm kiếm đệ quy
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
    else:
        # Chỉ tìm trong thư mục hiện tại
        for file in os.listdir(directory):
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(directory, file)
                if os.path.isfile(full_path):
                    pdf_files.append(full_path)
    
    return sorted(pdf_files)


def batch_process(
    input_dir: str,
    output_dir: str = None,
    recursive: bool = False,
    skip_existing: bool = True,
    **pipeline_config
):
    """
    Xử lý hàng loạt tất cả file PDF trong thư mục
    
    Args:
        input_dir: Thư mục chứa file PDF
        output_dir: Thư mục output (mặc định: output_pipeline_complete)
        recursive: Tìm kiếm đệ quy trong thư mục con
        skip_existing: Bỏ qua file đã xử lý
        **pipeline_config: Cấu hình cho pipeline
    """
    
    # Tìm tất cả file PDF
    print(f"\n{'='*80}")
    print(f"TÌM KIẾM FILE PDF TRONG THƯ MỤC: {input_dir}")
    print(f"{'='*80}")
    
    pdf_files = find_pdf_files(input_dir, recursive)
    
    if not pdf_files:
        print(f"❌ Không tìm thấy file PDF nào trong {input_dir}")
        return
    
    print(f"\n✅ Tìm thấy {len(pdf_files)} file PDF:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"   {i}. {os.path.basename(pdf_file)}")
    
    # Khởi tạo pipeline
    output_base = output_dir or 'output_pipeline_complete'
    pipeline = CompletePipeline(pipeline_config)
    
    # Thống kê
    total_files = len(pdf_files)
    processed_files = 0
    skipped_files = 0
    failed_files = []
    
    print(f"\n{'='*80}")
    print(f"BẮT ĐẦU XỬ LÝ {total_files} FILE")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    # Xử lý từng file
    for idx, pdf_file in enumerate(pdf_files, 1):
        file_name = os.path.basename(pdf_file)
        file_stem = Path(pdf_file).stem
        
        print(f"\n{'#'*80}")
        print(f"# FILE {idx}/{total_files}: {file_name}")
        print(f"{'#'*80}")
        
        # Kiểm tra xem file đã được xử lý chưa
        file_output_dir = os.path.join(output_base, file_stem)
        summary_file = os.path.join(file_output_dir, 'pipeline_summary.json')
        
        if skip_existing and os.path.exists(summary_file):
            print(f"⏭️  BỎ QUA: File đã được xử lý trước đó")
            print(f"   Output: {summary_file}")
            skipped_files += 1
            continue
        
        try:
            # Xử lý file
            result = pipeline.run(pdf_file, file_output_dir)
            processed_files += 1
            
            print(f"\n✅ HOÀN THÀNH: {file_name}")
            print(f"   Output: {file_output_dir}")
            
        except KeyboardInterrupt:
            print(f"\n\n⚠️  DỪNG XỬ LÝ (Ctrl+C)")
            print(f"   Đã xử lý: {processed_files}/{total_files} file")
            break
            
        except Exception as e:
            print(f"\n❌ LỖI: {file_name}")
            print(f"   Chi tiết: {str(e)}")
            failed_files.append({
                'file': file_name,
                'error': str(e)
            })
            
            # Hỏi có tiếp tục không
            try:
                response = input("\n   Tiếp tục với file tiếp theo? (y/n): ").strip().lower()
                if response != 'y':
                    print("   Dừng xử lý.")
                    break
            except:
                print("   Tiếp tục...")
    
    # Thống kê kết quả
    elapsed_time = time.time() - start_time
    
    print(f"\n{'='*80}")
    print(f"KẾT QUẢ XỬ LÝ BATCH")
    print(f"{'='*80}")
    print(f"Tổng số file:        {total_files}")
    print(f"Đã xử lý:           {processed_files}")
    print(f"Bỏ qua (đã có):     {skipped_files}")
    print(f"Thất bại:           {len(failed_files)}")
    print(f"Thời gian:          {elapsed_time:.1f} giây ({elapsed_time/60:.1f} phút)")
    
    if processed_files > 0:
        print(f"Trung bình:         {elapsed_time/processed_files:.1f} giây/file")
    
    if failed_files:
        print(f"\n❌ CÁC FILE THẤT BẠI:")
        for item in failed_files:
            print(f"   - {item['file']}: {item['error']}")
    
    print(f"\n📁 Output directory: {output_base}")
    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Xử lý hàng loạt tất cả file PDF trong thư mục',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  # Xử lý tất cả PDF trong thư mục hiện tại
  python batch_process.py .
  
  # Xử lý tất cả PDF trong thư mục cụ thể
  python batch_process.py "Data/pdf_to_json"
  
  # Xử lý đệ quy (bao gồm thư mục con)
  python batch_process.py "Data" --recursive
  
  # Chỉ định thư mục output
  python batch_process.py "Data/pdf_to_json" --output "output_batch"
  
  # Xử lý lại tất cả (không bỏ qua file đã xử lý)
  python batch_process.py "Data/pdf_to_json" --no-skip-existing
  
  # Tắt LLM normalization
  python batch_process.py "Data/pdf_to_json" --no-llm
        """
    )
    
    parser.add_argument(
        'input_dir',
        nargs='?',
        default='.',
        help='Thư mục chứa file PDF (mặc định: thư mục hiện tại)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Thư mục output (mặc định: output_pipeline_complete)'
    )
    
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Tìm kiếm đệ quy trong thư mục con'
    )
    
    parser.add_argument(
        '--no-skip-existing',
        action='store_true',
        help='Xử lý lại tất cả file (không bỏ qua file đã xử lý)'
    )
    
    parser.add_argument(
        '--dpi',
        type=int,
        default=350,
        help='OCR DPI (mặc định: 350)'
    )
    
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Tắt LLM normalization'
    )
    
    parser.add_argument(
        '--stop-after-llm',
        action='store_true',
        help='Dừng sau LLM normalization (trước embedding)'
    )
    
    parser.add_argument(
        '--llm-model',
        default='gemini-1.5-flash-latest',
        help='LLM model (mặc định: gemini-1.5-flash-latest)'
    )
    
    parser.add_argument(
        '--embedding',
        default='phobert',
        choices=['phobert', 'bge-m3', 'vina'],
        help='Embedding model (mặc định: phobert)'
    )
    
    parser.add_argument(
        '--vector-db',
        default='faiss',
        choices=['faiss', 'milvus', 'qdrant'],
        help='Vector DB (mặc định: faiss)'
    )
    
    args = parser.parse_args()
    
    # Kiểm tra thư mục input
    if not os.path.exists(args.input_dir):
        print(f"❌ Thư mục không tồn tại: {args.input_dir}")
        return
    
    if not os.path.isdir(args.input_dir):
        print(f"❌ Đường dẫn không phải là thư mục: {args.input_dir}")
        return
    
    # Cấu hình pipeline
    pipeline_config = {
        'ocr_dpi': args.dpi,
        'use_llm': not args.no_llm,
        'llm_model': args.llm_model,
        'embedding_model': args.embedding,
        'vector_db': args.vector_db,
        'stop_after_llm': args.stop_after_llm
    }
    
    # Chạy batch processing
    batch_process(
        input_dir=args.input_dir,
        output_dir=args.output,
        recursive=args.recursive,
        skip_existing=not args.no_skip_existing,
        **pipeline_config
    )


if __name__ == '__main__':
    main()
