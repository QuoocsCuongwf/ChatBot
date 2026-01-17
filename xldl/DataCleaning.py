import os
import sys
import json
import shutil
import cv2
import numpy as np
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from tkinter import Tk, filedialog
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import glob
import time
import multiprocessing
import re

# ==============================================================================
# CẤU HÌNH HỆ THỐNG
# ==============================================================================

# 1. Đường dẫn đến thư mục bin của Poppler.
#    Để trống nếu đã thêm vào PATH của hệ thống.
POPPLER_PATH = r"D:\apps\Poppler\poppler-25.12.0\Library\bin"

# 2. Đường dẫn đến file thực thi Tesseract OCR.
#    Để trống nếu đã thêm vào PATH của hệ thống.
TESSERACT_PATH = r"D:\apps\OCR\tesseract.exe"

# 3. Cấu hình xử lý song song và chất lượng
MAX_WORKERS = min(2, multiprocessing.cpu_count())  # Giảm số luồng để tiết kiệm RAM
DPI_SETTING = 300  # DPI mặc định cho PDF text
SCAN_DPI = 350     # DPI cho scan (Tăng lên để OCR chính xác hơn)
BATCH_SIZE = 4     # Số trang xử lý mỗi batch

def check_system_dependencies():
    """
    Kiểm tra sự tồn tại của Tesseract và Poppler.
    Ưu tiên sử dụng biến môi trường PATH, sau đó mới đến đường dẫn hardcode.
    """
    global POPPLER_PATH, TESSERACT_PATH

    print("🔍 Kiểm tra Tesseract và Poppler...")

    # Kiểm tra Tesseract
    if TESSERACT_PATH and os.path.exists(TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        print("   - Tesseract: OK (sử dụng đường dẫn cấu hình)")
    elif shutil.which("tesseract"):
        TESSERACT_PATH = shutil.which("tesseract")
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        print("   - Tesseract: OK (tìm thấy trong PATH hệ thống)")
    else:
        print("   - ⚠️  CẢNH BÁO: Không tìm thấy Tesseract OCR. Vui lòng cài đặt và/hoặc cập nhật TESSERACT_PATH.")
        TESSERACT_PATH = None # Đánh dấu là không có sẵn

    # Kiểm tra Poppler
    if POPPLER_PATH and os.path.exists(POPPLER_PATH):
        print("   - Poppler: OK (sử dụng đường dẫn cấu hình)")
    elif any(shutil.which(cmd) for cmd in ["pdftoppm", "pdfinfo"]):
         # Poppler không cần set path global, pdf2image sẽ tự tìm nếu có trong PATH
        POPPLER_PATH = None # Đánh dấu là không cần path hardcode
        print("   - Poppler: OK (tìm thấy trong PATH hệ thống)")
    else:
        print("   - ⚠️  CẢNH BÁO: Không tìm thấy Poppler. Vui lòng cài đặt và/hoặc cập nhật POPPLER_PATH.")
        POPPLER_PATH = None

# Gọi hàm kiểm tra ngay khi khởi chạy
check_system_dependencies()


# ==============================================================================
# CÁC HÀM XỬ LÝ ẢNH VÀ OCR (TỐI ƯU HÓA)
# ==============================================================================

def is_text_pdf(pdf_path):
    """Kiểm tra xem PDF là dạng text (có thể copy) hay dạng scan (ảnh)"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages: return False
            # Kiểm tra 3 trang đầu để chắc chắn (tránh trường hợp trang bìa là ảnh)
            for i in range(min(3, len(pdf.pages))):
                page = pdf.pages[i]
                text = page.extract_text()
                if text and len(text.strip()) > 50:
                    return True
            return False
    except Exception:
        return False

def extract_text_pdf(pdf_path):
    """Trích xuất text trực tiếp từ PDF dạng text"""
    full_text = ""
    has_ocr_tools = TESSERACT_PATH and (POPPLER_PATH or any(shutil.which(cmd) for cmd in ["pdftoppm", "pdfinfo"]))
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            
            # Nếu text quá ít (có thể là trang scan/ảnh trong file text), thử OCR fallback
            if (text is None or len(text.strip()) < 300) and has_ocr_tools:
                try:
                    # Convert trang cụ thể sang ảnh để OCR
                    images = convert_from_path(
                        pdf_path,
                        dpi=SCAN_DPI,
                        poppler_path=POPPLER_PATH,
                        first_page=i+1,
                        last_page=i+1
                    )
                    if images:
                        ocr_text = ocr_single_page(images[0])
                        # Nếu OCR ra nhiều chữ hơn đáng kể thì lấy kết quả OCR
                        if len(ocr_text.strip()) > (len(text.strip()) if text else 0):
                            text = ocr_text
                except Exception as e:
                    print(f"   ⚠️ Lỗi OCR fallback trang {i+1}: {e}")
            
            full_text += (text or "") + "\n"
    return full_text

def preprocess_image_for_ocr(pil_image):
    """
    Xử lý ảnh trước khi OCR để tăng độ chính xác.
    Sử dụng phương pháp nhẹ hơn để không làm mất thông tin.
    """
    img_cv = np.array(pil_image)
    
    # Chuyển sang grayscale nếu cần
    if len(img_cv.shape) == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_cv
    
    # Sử dụng GaussianBlur nhẹ để giảm nhiễu trước khi phân ngưỡng
    denoised_gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Sử dụng Adaptive Thresholding với tham số tối ưu cho DPI 400
    # Block size 31, C=10 giúp tách chữ tốt hơn, tránh làm rỗng nét
    binary = cv2.adaptiveThreshold(
        denoised_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 5
    )
    
    return Image.fromarray(binary)

def ocr_single_page(img_data):
    """
    OCR một trang đơn lẻ với cấu hình Tesseract tối ưu.
    - PSM 3: Tự động phân vùng trang (tốt cho trang văn bản đầy đủ).
    - OEM 1: Sử dụng mạng LSTM.
    """
    try:
        custom_config = r'--oem 1 --psm 3 -l vie'
        processed_img = preprocess_image_for_ocr(img_data)
        text = pytesseract.image_to_string(processed_img, config=custom_config)
        return text
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""

def ocr_from_images_parallel(images, silent=False):
    """Trích xuất text từ danh sách ảnh với xử lý song song."""
    total = len(images)
    if total == 0:
        return ""
    if not TESSERACT_PATH:
        if not silent: print("\n   ❌ Không thể OCR vì không tìm thấy Tesseract.")
        return ""
    
    import gc
    results = []
    
    # Xử lý từng batch để tiết kiệm RAM
    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch_images = images[batch_start:batch_end]
        batch_results = [""] * len(batch_images)
        
        if len(batch_images) <= 2:
            # Batch nhỏ: xử lý tuần tự
            for i, img in enumerate(batch_images):
                if not silent: 
                    print(f"   🔄 Đang xử lý OCR: {batch_start + i + 1}/{total} trang...", end='\r')
                batch_results[i] = ocr_single_page(img)
                del img  # Giải phóng ảnh sau khi xử lý
        else:
            # Batch lớn: xử lý song song
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                future_to_idx = {executor.submit(ocr_single_page, img): idx for idx, img in enumerate(batch_images)}
                
                completed_futures = as_completed(future_to_idx)
                if not silent:
                    completed_futures = tqdm(completed_futures, total=len(batch_images), 
                                            desc=f"   OCR batch {batch_start//BATCH_SIZE + 1}", leave=False)

                for future in completed_futures:
                    idx = future_to_idx[future]
                    try:
                        batch_results[idx] = future.result()
                    except Exception as e:
                        if not silent: print(f"   ⚠️ Lỗi trang {batch_start + idx + 1}: {str(e)[:50]}")
        
        results.extend(batch_results)
        
        # Giải phóng bộ nhớ sau mỗi batch
        del batch_images
        del batch_results
        gc.collect()
    
    if not silent: print(f"\n   ✓ Hoàn thành OCR: {total} trang")
    return "\n".join(results)

# ==============================================================================
# MODULE PARSER (TÍCH HỢP TRỰC TIẾP ĐỂ TỐI ƯU HÓA)
# ==============================================================================

def clean_text(text):
    """Làm sạch văn bản cơ bản và xử lý lỗi OCR."""
    text = text.replace('\x0c', '')
    
    # 1. Sửa lỗi chính tả OCR tiếng Việt phổ biến
    # qủy -> quy (qủy định -> quy định, qủyền -> quyền)
    text = re.sub(r'\bqủy\b', 'quy', text, flags=re.IGNORECASE) 
    text = re.sub(r'qủy([a-zà-ỹ])', r'quy\1', text, flags=re.IGNORECASE) # qủyền -> quyền
    
    # thắm quyền -> thẩm quyền
    text = re.sub(r'\bthắm\s+quyền\b', 'thẩm quyền', text, flags=re.IGNORECASE)
    text = re.sub(r'\bthẳm\s+quyền\b', 'thẩm quyền', text, flags=re.IGNORECASE)
    
    # Ÿ tế -> Y tế
    text = text.replace('Ÿ tế', 'Y tế')
    
    # Dgười -> Người
    text = re.sub(r'\bDgười\b', 'Người', text)
    text = re.sub(r'\bDgƯỜI\b', 'NGƯỜI', text)

    # Diều/Điêu -> Điều (đã có ở ngoài nhưng đưa vào đây cho gọn)
    text = re.sub(r'\b(Diều|Điêu|Dìêu)\b', 'Điều', text)
    text = re.sub(r'\b(Khoán|Khoàn)\b', 'Khoản', text)

    # 2. Sửa lỗi số La Mã của Chương và định dạng Chương
    # Xử lý các biến thể lỗi OCR của số La Mã
    text = re.sub(r'(Chương|CHƯƠNG)\s+U\b', r'\1 II', text, flags=re.IGNORECASE)
    text = re.sub(r'(Chương|CHƯƠNG)\s+IH\b', r'\1 III', text, flags=re.IGNORECASE)
    text = re.sub(r'(Chương|CHƯƠNG)\s+Il\b', r'\1 II', text, flags=re.IGNORECASE)
    text = re.sub(r'(Chương|CHƯƠNG)\s+IlI\b', r'\1 III', text, flags=re.IGNORECASE)
    
    # 3. Tách dòng cho Chương và Điều nếu bị dính
    # Tìm dấu chấm/chấm phẩy/khoảng trắng, theo sau là Điều/Chương + Số
    # Thêm \n trước Điều/Chương để parser nhận diện được
    
    # Xử lý Điều: "...nội dung. Điều 5..." -> "...nội dung.\nĐiều 5..."
    text = re.sub(r'([.;])\s+(Điều|ĐIỀU)\s+(\d+)', r'\1\n\2 \3', text)
    
    # Xử lý Chương: "...nội dung. Chương II..." -> "...nội dung.\nChương II..."
    text = re.sub(r'([.;])\s+(Chương|CHƯƠNG)\s+([IVXLCDM\d]+|II|III)', r'\1\n\2 \3', text, flags=re.IGNORECASE)
    
    # Xử lý số trang hoặc rác dính trước Chương ở đầu dòng (do OCR ghép dòng)
    # Ví dụ: "13 Chương III" -> "\nChương III"
    text = re.sub(r'\n\d+\s+(Chương|CHƯƠNG)', r'\n\1', text, flags=re.IGNORECASE)
    
    return text

def parse_legal_document(text):
    """
    Phân tích văn bản pháp luật thành cấu trúc JSON.
    Sử dụng Regex chặt chẽ để tránh nhận diện nhầm tham chiếu Điều khoản.
    """
    doc = {
        "metadata": {},
        "phan_mo_dau": {},
        "can_cu_phap_ly": [],
        "chuong": []
    }
    
    lines = text.split('\n')
    
    # Regex patterns tối ưu: Bắt buộc có dấu chấm (.) hoặc hai chấm (:) sau số
    # Ví dụ: "Điều 1." hoặc "Điều 1:" -> OK
    # Ví dụ: "Điều 15;" hoặc "Điều 16 Nghị định" -> Bỏ qua (đây là tham chiếu)
    re_dieu = re.compile(r'^\s*Điều\s+(\d+)\s*[\.:]\s*(.*)$', re.IGNORECASE)
    re_chuong = re.compile(r'^\s*Chương\s+([IVXLCDM\d]+)(?:[\s\.:]+(.*))?$', re.IGNORECASE)
    re_khoan = re.compile(r'^\s*(\d+)\.\s+(.*)$')
    re_diem = re.compile(r'^\s*([a-zđ])\)\s+(.*)$')
    
    current_chuong = None
    current_dieu = None
    current_khoan = None
    
    # Buffer để tích lũy nội dung nhiều dòng
    buffer_content = []
    
    def flush_buffer():
        nonlocal buffer_content
        if not buffer_content:
            return
            
        content = " ".join(buffer_content).strip()
        buffer_content.clear() # Xóa buffer sau khi dùng
        
        if current_khoan:
            if current_khoan.get("diem"):
                 # Nếu đã có điểm, nội dung này nối vào điểm cuối cùng
                 current_khoan["diem"][-1]["noi_dung"] += " " + content
            else:
                 current_khoan["noi_dung"] += " " + content
        elif current_dieu:
            current_dieu["noi_dung"] = (current_dieu.get("noi_dung", "") + " " + content).strip()
            
    for line in lines:
        line = line.strip()
        if not line: continue
            
        # 1. Kiểm tra Chương
        match_chuong = re_chuong.match(line)
        if match_chuong:
            flush_buffer()
            current_chuong = {
                "so_chuong": match_chuong.group(1),
                "ten_chuong": match_chuong.group(2) or "",
                "dieu": []
            }
            doc["chuong"].append(current_chuong)
            current_dieu = None
            current_khoan = None
            continue
            
        # 2. Kiểm tra Điều (QUAN TRỌNG: Regex chặt chẽ ở đây)
        match_dieu = re_dieu.match(line)
        if match_dieu:
            flush_buffer()
            current_dieu = {
                "so_dieu": match_dieu.group(1),
                "tieu_de": match_dieu.group(2),
                "noi_dung": "",
                "khoan": []
            }
            if current_chuong is None:
                current_chuong = {"so_chuong": "", "ten_chuong": "", "dieu": []}
                doc["chuong"].append(current_chuong)
            current_chuong["dieu"].append(current_dieu)
            current_khoan = None
            continue
            
        # 3. Kiểm tra Khoản
        match_khoan = re_khoan.match(line)
        if match_khoan and current_dieu:
            flush_buffer()
            current_khoan = {
                "so_khoan": match_khoan.group(1),
                "noi_dung": match_khoan.group(2),
                "diem": []
            }
            current_dieu["khoan"].append(current_khoan)
            continue
            
        # 4. Kiểm tra Điểm
        match_diem = re_diem.match(line)
        if match_diem and current_khoan:
            flush_buffer()
            diem = {
                "so_diem": match_diem.group(1),
                "noi_dung": match_diem.group(2)
            }
            current_khoan["diem"].append(diem)
            continue
            
        # Nội dung thường (nối vào buffer)
        buffer_content.append(line)
        
    flush_buffer() # Flush lần cuối
    return doc

# ==============================================================================
# HÀM XỬ LÝ CHÍNH
# ==============================================================================

def process_single_pdf(pdf_path, output_dir=None, dpi=None, silent=False):
    """
    Xử lý một file PDF đơn lẻ: trích xuất, làm sạch, và phân tích cấu trúc.
    """
    if dpi is None: dpi = DPI_SETTING
    
    result = {"success": False, "input_file": pdf_path, "output_file": None, "stats": {}, "error": None}
    filename = os.path.basename(pdf_path)
    
    try:
        is_scan = not is_text_pdf(pdf_path)
        num_pages = 0
        raw_text = ""

        if not is_scan:
            if not silent: print(f"   📄 Đang xử lý: {filename} (PDF dạng text)")
            raw_text = extract_text_pdf(pdf_path)
            with pdfplumber.open(pdf_path) as pdf:
                num_pages = len(pdf.pages)
        else:
            if not POPPLER_PATH and not any(shutil.which(cmd) for cmd in ["pdftoppm", "pdfinfo"]):
                 raise RuntimeError("Poppler không có sẵn để xử lý PDF dạng ảnh.")
            if not TESSERACT_PATH:
                 raise RuntimeError("Tesseract không có sẵn để xử lý PDF dạng ảnh.")

            current_dpi = SCAN_DPI
            if not silent:
                print(f"   📄 Đang xử lý: {filename} (PDF dạng ảnh/scan)")
                print(f"      >> Chuyển PDF sang ảnh (DPI: {current_dpi})...")
            
            # Lấy số trang trước bằng pdfplumber (nhẹ)
            with pdfplumber.open(pdf_path) as pdf:
                num_pages = len(pdf.pages)
            
            if not silent: print(f"      >> Bắt đầu OCR cho {num_pages} trang (theo batch {BATCH_SIZE} trang)...")
            
            # Xử lý từng batch để tiết kiệm RAM
            import gc
            all_text = []
            
            for batch_start in range(0, num_pages, BATCH_SIZE):
                batch_end = min(batch_start + BATCH_SIZE, num_pages)
                
                if not silent:
                    print(f"      >> Đang xử lý trang {batch_start + 1}-{batch_end}/{num_pages}...", end='\r')
                
                # Convert chỉ batch này
                batch_images = convert_from_path(
                    pdf_path, 
                    dpi=current_dpi, 
                    poppler_path=POPPLER_PATH,
                    first_page=batch_start + 1,
                    last_page=batch_end
                )
                
                # OCR batch
                for img in batch_images:
                    text = ocr_single_page(img)
                    all_text.append(text)
                
                # Giải phóng bộ nhớ
                del batch_images
                gc.collect()
            
            raw_text = "\n".join(all_text)
            if not silent: print(f"\n      >> Hoàn thành OCR {num_pages} trang.")

        # Áp dụng làm sạch nâng cao (xử lý Chương dính dòng, lỗi số La Mã)
        raw_text = clean_text(raw_text)

        if not raw_text.strip():
            raise ValueError("Không trích xuất được nội dung từ file PDF.")

        # Phân tích cấu trúc bằng module parser
        final_json = parse_legal_document(raw_text)
        final_json["metadata"]["so_trang"] = num_pages
        final_json["metadata"]["loai_pdf"] = "scan" if is_scan else "text"
        
        # Lưu file
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_filename = os.path.join(output_dir, os.path.splitext(filename)[0] + "_processed.json")
        else:
            output_filename = os.path.splitext(pdf_path)[0] + "_processed.json"
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_json, f, ensure_ascii=False, indent=2)
        
        num_chuong = len(final_json.get('chuong', []))
        num_dieu = sum(len(c.get('dieu', [])) for c in final_json.get('chuong', []))
        
        result.update({
            "success": True,
            "output_file": output_filename,
            "stats": {"so_trang": num_pages, "so_chuong": num_chuong, "so_dieu": num_dieu}
        })
        
        if not silent:
            print(f"      ✅ Hoàn thành! Phân tích được {num_chuong} Chương, {num_dieu} Điều.")
            
    except Exception as e:
        result["error"] = str(e)
        if not silent:
            print(f"      ❌ Lỗi: {str(e)}")
    
    return result

def process_multiple_pdfs(pdf_paths, output_dir=None):
    """
    Xử lý nhiều file PDF một cách tuần tự để quản lý bộ nhớ tốt hơn.
    """
    total_files = len(pdf_paths)
    results = {"total": total_files, "success": 0, "failed": 0, "files": []}
    
    print("="*70)
    print(f"🚀 BẮT ĐẦU XỬ LÝ {total_files} FILE PDF")
    print("="*70)
    
    start_time = time.time()
    
    for pdf_path in tqdm(pdf_paths, desc="Tổng tiến trình", unit="file"):
        result = process_single_pdf(
            pdf_path,
            output_dir=output_dir,
            silent=True # Tắt log chi tiết trong vòng lặp
        )
        results["files"].append(result)
        if result["success"]:
            results["success"] += 1
        else:
            results["failed"] += 1
        
        # Dọn dẹp bộ nhớ sau mỗi file để tránh tràn RAM với các file lớn
        import gc
        gc.collect()
    
    elapsed_time = time.time() - start_time
    
    # In báo cáo tổng kết
    print("\n" + "="*70)
    print("📊 BÁO CÁO KẾT QUẢ")
    print("="*70)
    print(f"   - Tổng số file: {results['total']}")
    print(f"   - ✅ Thành công: {results['success']}")
    print(f"   - ❌ Thất bại:  {results['failed']}")
    print(f"   - ⏱️  Thời gian:   {elapsed_time:.2f} giây ({elapsed_time/60:.2f} phút)")
    
    if results["failed"] > 0:
        print("\n❌ DANH SÁCH FILE LỖI:")
        for r in results["files"]:
            if not r["success"]:
                print(f"   - {os.path.basename(r['input_file'])}: {r['error']}")
    print("="*70)
    
    return results

# ==============================================================================
# GIAO DIỆN DÒNG LỆNH VÀ CÁC API PHỤ
# ==============================================================================

def main_cli():
    """Giao diện dòng lệnh chính."""
    print("="*70)
    print("HỆ THỐNG TRÍCH XUẤT VĂN BẢN PHÁP LUẬT")
    print("="*70)
    
    # Tự động ẩn cửa sổ Tkinter không cần thiết
    root = Tk()
    root.withdraw()
    
    print("\nChọn chế độ xử lý:")
    print("  1. Xử lý một file PDF")
    print("  2. Xử lý nhiều file PDF")
    print("  3. Xử lý tất cả PDF trong một thư mục")
    print("  0. Thoát")
    
    choice = input("\n>> Nhập lựa chọn (0-3): ").strip()
    
    if choice == "1":
        pdf_path = filedialog.askopenfilename(title="Chọn file PDF", filetypes=[("PDF files", "*.pdf")])
        if pdf_path:
            output_dir = os.path.dirname(pdf_path) # Mặc định lưu cùng thư mục
            process_single_pdf(pdf_path, output_dir)
    
    elif choice == "2":
        pdf_paths = filedialog.askopenfilenames(title="Chọn các file PDF", filetypes=[("PDF files", "*.pdf")])
        if pdf_paths:
            output_dir = filedialog.askdirectory(title="Chọn thư mục lưu kết quả")
            if output_dir:
                process_multiple_pdfs(list(pdf_paths), output_dir)
    
    elif choice == "3":
        folder_path = filedialog.askdirectory(title="Chọn thư mục chứa PDF")
        if folder_path:
            recursive = input(">> Tìm trong thư mục con? (y/n): ").strip().lower() == 'y'
            search_pattern = os.path.join(folder_path, "**" if recursive else "", "*.pdf")
            pdf_files = glob.glob(search_pattern, recursive=recursive)
            if pdf_files:
                output_dir = os.path.join(folder_path, "processed_output")
                process_multiple_pdfs(pdf_files, output_dir)
            else:
                print("❌ Không tìm thấy file PDF nào.")
    
    elif choice == "0":
        print("👋 Tạm biệt!")
    
    else:
        print("❌ Lựa chọn không hợp lệ.")

def clean_existing_json(json_path, output_path=None):
    """API: Áp dụng lại logic làm sạch cho một file JSON đã được xử lý."""
    if not output_path:
        output_path = json_path
        
    with open(json_path, 'r', encoding='utf-8') as f:
        raw_text_from_json = json.dumps(json.load(f))

    # Sử dụng hàm clean_text từ parser
    cleaned_text = clean_text(raw_text_from_json)
    
    cleaned_data = json.loads(cleaned_text)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Đã làm sạch và ghi đè file: {output_path}")
    return cleaned_data

if __name__ == "__main__":
    # Đảm bảo encoding utf-8 cho stdout
    sys.stdout.reconfigure(encoding='utf-8')
    main_cli()