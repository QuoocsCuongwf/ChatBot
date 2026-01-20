"""
Optimized OCR Pipeline - Balanced accuracy vs simplicity
"""
import os
import sys
import json
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import argparse

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def simple_preprocess(image: np.ndarray, dpi: int = 400) -> np.ndarray:
    """
    Simple but effective preprocessing - matching DataCleaning.py approach
    but with better parameters
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Light denoising only
    denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
    
    # Adaptive thresholding - proven parameters
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 5
    )
    
    return binary


def dual_pass_ocr(image: np.ndarray) -> dict:
    """
    Dual-pass OCR: Run twice with different PSM, pick best
    """
    preprocessed = simple_preprocess(image)
    pil_image = Image.fromarray(preprocessed)
    
    results = []
    
    # Pass 1: PSM 3 (auto page segmentation) - best for full pages
    try:
        config1 = '--oem 1 --psm 3 -l vie'
        text1 = pytesseract.image_to_string(pil_image, config=config1, lang='vie')
        data1 = pytesseract.image_to_data(pil_image, config=config1, lang='vie',
                                          output_type=pytesseract.Output.DICT)
        conf1 = np.mean([int(c) for c in data1['conf'] if c != '-1'])
        results.append({
            'text': text1,
            'confidence': conf1,
            'psm': 3,
            'char_count': len(text1),
            'word_count': len(text1.split())
        })
    except Exception as e:
        print(f"  ⚠️ PSM 3 error: {e}")
    
    # Pass 2: PSM 6 (uniform text block) - good for documents
    try:
        config2 = '--oem 1 --psm 6 -l vie'
        text2 = pytesseract.image_to_string(pil_image, config=config2, lang='vie')
        data2 = pytesseract.image_to_data(pil_image, config=config2, lang='vie',
                                          output_type=pytesseract.Output.DICT)
        conf2 = np.mean([int(c) for c in data2['conf'] if c != '-1'])
        results.append({
            'text': text2,
            'confidence': conf2,
            'psm': 6,
            'char_count': len(text2),
            'word_count': len(text2.split())
        })
    except Exception as e:
        print(f"  ⚠️ PSM 6 error: {e}")
    
    # Select best: prefer more content if confidence is similar
    if not results:
        return {'text': '', 'confidence': 0, 'psm': 0}
    
    if len(results) == 1:
        return results[0]
    
    # If confidence difference < 5%, choose one with more content
    if abs(results[0]['confidence'] - results[1]['confidence']) < 5:
        best = max(results, key=lambda x: x['char_count'])
    else:
        best = max(results, key=lambda x: x['confidence'])
    
    return best


def post_process_text(text: str) -> str:
    """
    Post-process with parser corrections
    """
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from parser import VIETNAMESE_OCR_FIXES, clean_text
        
        # Apply all known fixes
        for wrong, correct in VIETNAMESE_OCR_FIXES.items():
            text = text.replace(wrong, correct)
        
        # Use parser's clean_text function
        text = clean_text(text)
    except ImportError:
        # Basic cleaning
        import re
        text = text.replace('\x0c', '')
        text = text.replace('\r', '')
        text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def process_pdf(pdf_path: str, output_path: str = None, dpi: int = 400, verbose: bool = True):
    """
    Process PDF with optimized OCR pipeline
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"🚀 OPTIMIZED OCR PIPELINE - {os.path.basename(pdf_path)}")
        print(f"{'='*70}")
        print(f"Strategy: Simple preprocessing + Dual-pass OCR + Parser corrections")
        print(f"{'='*70}\n")
    
    # Convert PDF to images
    if verbose:
        print(f"📖 Converting PDF (DPI: {dpi})...")
    
    images = convert_from_path(
        pdf_path,
        dpi=dpi,
        poppler_path=r"D:\apps\Poppler\poppler-25.12.0\Library\bin"
    )
    
    total_pages = len(images)
    if verbose:
        print(f"   ✓ {total_pages} pages\n")
        print(f"🔍 OCR processing...")
    
    # Process pages
    pages_data = []
    for i, image in enumerate(images, 1):
        img_array = np.array(image)
        result = dual_pass_ocr(img_array)
        
        # Post-process
        clean_text = post_process_text(result['text'])
        
        page_data = {
            'page_number': i,
            'text': clean_text,
            'total_chars': len(clean_text),
            'confidence': float(result['confidence']),
            'psm_used': result['psm']
        }
        pages_data.append(page_data)
        
        if verbose:
            print(f"   ✓ Page {i:2d}: {len(clean_text):5d} chars, "
                  f"confidence {result['confidence']:.1f}%, PSM {result['psm']}")
    
    # Combine
    full_text = '\n\n'.join(page['text'] for page in pages_data)
    
    total_chars = sum(page['total_chars'] for page in pages_data)
    avg_confidence = np.mean([page['confidence'] for page in pages_data])
    
    result = {
        'source_file': pdf_path,
        'total_pages': total_pages,
        'dpi': dpi,
        'full_text': full_text,
        'pages': pages_data,
        'total_chars': total_chars,
        'avg_confidence': float(avg_confidence),
        'pipeline': 'optimized_dual_pass'
    }
    
    # Save
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        if verbose:
            print(f"\n💾 Saved: {output_path}")
    
    # Summary
    if verbose:
        print(f"\n{'='*70}")
        print(f"✅ SUMMARY")
        print(f"{'='*70}")
        print(f"Pages:            {total_pages}")
        print(f"Total chars:      {total_chars:,}")
        print(f"Chars/page:       {total_chars/total_pages:.0f}")
        print(f"Avg confidence:   {avg_confidence:.1f}%")
        print(f"{'='*70}\n")
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Optimized OCR Pipeline')
    parser.add_argument('pdf_path', help='Path to PDF')
    parser.add_argument('--output', '-o', help='Output JSON path')
    parser.add_argument('--dpi', type=int, default=400, help='DPI (default: 400)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
    
    args = parser.parse_args()
    
    # Auto output path
    if not args.output:
        base = os.path.splitext(os.path.basename(args.pdf_path))[0]
        output_dir = os.path.join(os.path.dirname(args.pdf_path), '..', 'output_pipeline_ver2')
        os.makedirs(output_dir, exist_ok=True)
        args.output = os.path.join(output_dir, f"{base}_ocr.json")
    
    # Run
    process_pdf(args.pdf_path, args.output, args.dpi, not args.quiet)


if __name__ == '__main__':
    main()
