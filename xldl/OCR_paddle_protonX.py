"""
OCR Pipeline: PaddleOCR (Text Detection) + ProtonX Legal (Text Recognition)
Sử dụng PaddleOCR để phát hiện vị trí text boxes, sau đó dùng ProtonX model để nhận dạng text
Optimized for low memory usage
"""
import os
import sys
import json
import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
from paddleocr import PaddleOCR
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from tqdm import tqdm
import torch
import gc
import pdfplumber

# Cấu hình encoding UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Đổi cache HuggingFace sang ổ F để tránh đầy ổ C
os.environ['HF_HOME'] = 'F:/huggingface_cache'
os.environ['TRANSFORMERS_CACHE'] = 'F:/huggingface_cache'

# Cấu hình
POPPLER_PATH = r"D:\apps\Poppler\poppler-25.12.0\Library\bin"
MODEL_NAME = "protonx-models/protonx-legal-tc"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print("=" * 60)
print("HYBRID OCR: PaddleOCR (Detect) + ProtonX Legal (Recognize)")
print("=" * 60)

# Load PaddleOCR cho text detection
print("\n1. Loading PaddleOCR for text detection...")
try:
    paddle_ocr = PaddleOCR(
        use_angle_cls=False,
        lang='vi',
        use_gpu=False,
        show_log=False
    )
    print("   ✓ PaddleOCR loaded")
except Exception as e:
    print(f"   ✗ Error loading PaddleOCR: {e}")
    sys.exit(1)

# Load ProtonX model cho text recognition
print("\n2. Loading ProtonX Legal OCR model...")
try:
    # ProtonX model là T5-based, cần load khác với VisionEncoderDecoder
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    
    print("   Loading tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir='F:/huggingface_cache')
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, cache_dir='F:/huggingface_cache')
    model.to(DEVICE)
    model.eval()
    
    # Processor cho ảnh - sử dụng TrOCR processor
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten", cache_dir='F:/huggingface_cache')
    
    print(f"   ✓ ProtonX model loaded on {DEVICE}")
except Exception as e:
    print(f"   ✗ Error loading model: {e}")
    print("\n   ProtonX model yêu cầu nhiều dung lượng (900MB+)")
    print("   Fallback: Sử dụng VietOCR thay thế...")
    
    # Fallback to VietOCR
    try:
        from vietocr.tool.predictor import Predictor
        from vietocr.tool.config import Cfg
        
        config = Cfg.load_config_from_name('vgg_transformer')
        config['device'] = DEVICE
        config['cnn']['pretrained'] = True
        
        model = Predictor(config)
        processor = None
        tokenizer = None
        print(f"   ✓ VietOCR loaded on {DEVICE}")
    except Exception as e3:
        print(f"   ✗ Failed to load VietOCR: {e3}")
        sys.exit(1)


def detect_text_boxes(image):
    """Sử dụng PaddleOCR để phát hiện text boxes"""
    # Chuyển đổi image nếu cần
    if isinstance(image, Image.Image):
        image = np.array(image)
    
    # PaddleOCR trả về list[list] hoặc None
    result = paddle_ocr.ocr(image, cls=False)
    
    # Debug: kiểm tra kết quả
    if not result:
        print(f"      WARNING: PaddleOCR returned None")
        return []
    
    if not result[0]:
        print(f"      WARNING: PaddleOCR returned empty list")
        return []
    
    boxes = []
    for line in result[0]:
        # line = (box, (text, confidence))
        # Chỉ lấy box
        if isinstance(line, (list, tuple)) and len(line) >= 1:
            box = line[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            boxes.append(box)
    
    return boxes


def recognize_text_protonx(image, box):
    """Sử dụng ProtonX/VietOCR model để nhận dạng text trong box"""
    try:
        # Chuyển box coordinates thành bounding box
        box = np.array(box)
        
        # Kiểm tra box có đúng format không
        if box.ndim != 2 or box.shape[0] != 4 or box.shape[1] != 2:
            # Box không đúng format [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            return ""
        
        box = box.astype(np.int32)
        x_min = int(np.min(box[:, 0]))
        y_min = int(np.min(box[:, 1]))
        x_max = int(np.max(box[:, 0]))
        y_max = int(np.max(box[:, 1]))
        
        # Kiểm tra box có hợp lệ không
        if x_max <= x_min or y_max <= y_min:
            return ""
        
        # Crop image
        if isinstance(image, np.ndarray):
            # Kiểm tra boundaries
            h, w = image.shape[:2]
            x_min = max(0, min(x_min, w-1))
            x_max = max(0, min(x_max, w))
            y_min = max(0, min(y_min, h-1))
            y_max = max(0, min(y_max, h))
            
            if x_max <= x_min or y_max <= y_min:
                return ""
            
            cropped = image[y_min:y_max, x_min:x_max]
            if cropped.size == 0:
                return ""
            cropped_pil = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
        else:
            cropped_pil = image.crop((x_min, y_min, x_max, y_max))
        
        # Nhận dạng
        if processor is not None and tokenizer is not None:
            # Sử dụng ProtonX T5 model
            pixel_values = processor(cropped_pil, return_tensors="pt").pixel_values.to(DEVICE)
            
            with torch.no_grad():
                generated_ids = model.generate(pixel_values)
            
            generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return generated_text.strip()
        else:
            # Fallback: VietOCR
            return model.predict(cropped_pil).strip()
    
    except Exception as e:
        # Chỉ in lỗi nếu không phải lỗi thường gặp
        if "too many indices" not in str(e):
            print(f"   Error in recognition: {e}")
        return ""


def ocr_image_hybrid(image_path):
    """OCR một ảnh sử dụng hybrid approach"""
    print(f"\nProcessing: {image_path}")
    
    # Load image
    if isinstance(image_path, str):
        img_cv = cv2.imread(image_path)
        img_pil = Image.open(image_path)
    else:
        img_pil = image_path
        img_cv = np.array(image_path)
        if img_cv.shape[2] == 3:  # RGB
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
    
    # Resize nếu ảnh quá lớn (tiết kiệm RAM, vẫn giữ chất lượng)
    max_dim = 1800  # Giảm xuống 1800 để tránh memory leak
    h, w = img_cv.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        print(f"   Resizing from {w}x{h} to {new_w}x{new_h} (saving RAM)...")
        img_cv = cv2.resize(img_cv, (new_w, new_h), interpolation=cv2.INTER_AREA)
        img_pil = img_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Clear memory trước khi detect
    gc.collect()
    
    # Step 1: Detect text boxes
    print("   1. Detecting text boxes with PaddleOCR...")
    boxes = detect_text_boxes(img_cv)
    print(f"      Found {len(boxes)} boxes")
    
    # Step 2: Recognize text in each box
    print("   2. Recognizing text with ProtonX model...")
    results = []
    for i, box in enumerate(tqdm(boxes, desc="   Recognizing")):
        text = recognize_text_protonx(img_cv, box)
        if text:
            results.append({
                "box": box,
                "text": text
            })
    
    return results


def process_pdf(pdf_path, output_path=None):
    """Xử lý toàn bộ PDF - tối ưu memory"""
    print(f"\n{'='*60}")
    print(f"Processing PDF: {pdf_path}")
    print(f"{'='*60}")
    
    # Đếm số trang trước
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
    
    print(f"\nTotal pages: {total_pages}")
    print("Processing page by page to save memory...\n")
    
    # Xử lý từng trang một
    all_results = {}
    for page_num in range(1, total_pages + 1):
        print(f"\n--- Page {page_num}/{total_pages} ---")
        
        # Convert chỉ 1 trang (DPI tối ưu cho chất lượng và RAM)
        if os.path.exists(POPPLER_PATH):
            images = convert_from_path(
                pdf_path, 
                dpi=250,  # Tăng từ 200 -> 250 cho chất lượng tốt hơn
                first_page=page_num,
                last_page=page_num,
                poppler_path=POPPLER_PATH
            )
        else:
            images = convert_from_path(
                pdf_path,
                dpi=250,
                first_page=page_num,
                last_page=page_num
            )
        
        if not images:
            continue
            
        image = images[0]
        
        # OCR trang này
        results = ocr_image_hybrid(image)
        
        # Extract text
        page_text = "\n".join([r["text"] for r in results])
        all_results[f"page_{page_num}"] = {
            "page_number": page_num,
            "text": page_text,
            "boxes": results
        }
        
        # Giải phóng memory mạnh mẽ
        del images
        del image
        del results
        gc.collect()
        
        # Mỗi 10 trang, force clear cache
        if page_num % 10 == 0:
            print(f"\n>>> Clearing memory cache (page {page_num})...")
            gc.collect()
            import time
            time.sleep(0.5)  # Cho hệ thống thời gian release memory
    
    # Save results
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Results saved to: {output_path}")
    
    return all_results


if __name__ == "__main__":
    # Test với một trang
    test_pdf = r"path/to/your/test.pdf"
    
    if len(sys.argv) > 1:
        test_pdf = sys.argv[1]
    
    if os.path.exists(test_pdf):
        output_file = test_pdf.replace('.pdf', '_protonx_ocr.json')
        results = process_pdf(test_pdf, output_file)
        
        # In kết quả
        print("\n" + "="*60)
        print("RESULTS PREVIEW")
        print("="*60)
        for page_key, page_data in list(results.items())[:2]:  # Hiển thị 2 trang đầu
            print(f"\n{page_key}:")
            print(page_data["text"][:500])  # 500 ký tự đầu
    else:
        print(f"\nUsage: python {sys.argv[0]} <pdf_file>")
        print(f"Example: python {sys.argv[0]} document.pdf")

import sys
