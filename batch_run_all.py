"""
Batch process all PDF files in DataPhuc and ThongTu folders
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# Cấu hình
PYTHON_EXE = r"F:\ocr_env\python.exe"
PIPELINE_SCRIPT = r"xldl\complete_pipeline_protonx.py"
BASE_DIR = r"F:\NghienCuuKhoaHoc"

# Các folder chứa PDF
FOLDERS = [
    r"F:\NghienCuuKhoaHoc\Data\DataPhuc",
    r"F:\NghienCuuKhoaHoc\Data\DataPhuc\ThongTu"
]

# Output folders
OUTPUT_DIRS = {
    r"F:\NghienCuuKhoaHoc\Data\DataPhuc": "output_nghidinh",
    r"F:\NghienCuuKhoaHoc\Data\DataPhuc\ThongTu": "output_thongtu"
}

def get_pdf_files(folder):
    """Lấy danh sách file PDF trong folder"""
    pdfs = []
    for f in os.listdir(folder):
        if f.lower().endswith('.pdf'):
            pdfs.append(os.path.join(folder, f))
    return sorted(pdfs)

def run_pipeline(pdf_path, output_dir):
    """Chạy pipeline cho 1 file PDF"""
    cmd = [
        PYTHON_EXE,
        PIPELINE_SCRIPT,
        pdf_path,
        "-o", output_dir
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, "", str(e)
    except Exception as e:
        return False, "", str(e)

def main():
    print("=" * 70)
    print("BATCH PROCESSING ALL PDF FILES")
    print("=" * 70)
    
    # Đảm bảo output dirs tồn tại
    for output_dir in OUTPUT_DIRS.values():
        os.makedirs(os.path.join(BASE_DIR, output_dir), exist_ok=True)
    
    total_files = 0
    success_count = 0
    failed_files = []
    
    for folder in FOLDERS:
        output_dir = OUTPUT_DIRS[folder]
        pdfs = get_pdf_files(folder)
        
        print(f"\n{'='*70}")
        print(f"Folder: {folder}")
        print(f"Output: {output_dir}")
        print(f"Files: {len(pdfs)}")
        print("="*70)
        
        for i, pdf_path in enumerate(pdfs, 1):
            pdf_name = os.path.basename(pdf_path)
            print(f"\n[{i}/{len(pdfs)}] Processing: {pdf_name}")
            
            start_time = time.time()
            success, stdout, stderr = run_pipeline(pdf_path, output_dir)
            elapsed = time.time() - start_time
            
            total_files += 1
            
            if success:
                success_count += 1
                print(f"   ✓ Success ({elapsed:.1f}s)")
                
                # Tìm thông tin chunks
                for line in stdout.split('\n'):
                    if 'chunks' in line.lower() or 'Điều' in line or 'Chương' in line:
                        print(f"   {line.strip()}")
            else:
                failed_files.append(pdf_name)
                print(f"   ✗ Failed ({elapsed:.1f}s)")
                if stderr:
                    # Chỉ in dòng lỗi chính
                    for line in stderr.split('\n')[-5:]:
                        if line.strip():
                            print(f"   Error: {line.strip()}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total files: {total_files}")
    print(f"Success: {success_count}")
    print(f"Failed: {len(failed_files)}")
    
    if failed_files:
        print("\nFailed files:")
        for f in failed_files:
            print(f"  - {f}")
    
    print("\nOutput directories:")
    for folder, output_dir in OUTPUT_DIRS.items():
        full_path = os.path.join(BASE_DIR, output_dir)
        if os.path.exists(full_path):
            files = [f for f in os.listdir(full_path) if f.endswith('.json')]
            print(f"  {output_dir}: {len(files)} JSON files")

if __name__ == "__main__":
    main()
