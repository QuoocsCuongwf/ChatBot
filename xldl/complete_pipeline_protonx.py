"""
COMPLETE PIPELINE WITH PROTONX OCR
===================================
PDF → OCR (PaddleOCR + ProtonX) → Parsing → OCR Fixes → Chunking → LLM (optional)
"""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List

# Cấu hình encoding UTF-8 cho Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from load_env import load_env, get_env
    load_env()
except ImportError:
    def get_env(key: str, default: str = None) -> str:
        return os.getenv(key, default)


class CompletePipelineProtonX:
    """Complete pipeline using ProtonX OCR"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.use_llm = self.config.get('use_llm', False)
        self.llm_model = self.config.get('llm_model', get_env('LLM_MODEL', 'gemini-1.5-flash-latest'))
        self.output_dir = self.config.get('output_dir', 'output_protonx_complete')
        
    def step1_ocr_and_parse(self, pdf_path: str, output_dir: str) -> Dict:
        """STEP 1: OCR & Parsing với ProtonX"""
        print(f"\n{'='*70}")
        print(f"STEP 1: OCR & Parsing (ProtonX)")
        print(f"{'='*70}")
        
        from rules_base_protonx import run_full_pipeline_protonx
        
        parsed_data = run_full_pipeline_protonx(pdf_path, output_dir=output_dir)
        parsed_data['source_file'] = pdf_path
        
        return parsed_data
    
    def step2_chunk(self, parsed_data: Dict, output_dir: str) -> Dict:
        """STEP 2: Chunking"""
        print(f"\n{'='*70}")
        print(f"STEP 2: CHUNKING")
        print(f"{'='*70}")
        
        chunks = self._chunk_parsed_data(parsed_data)
        
        chunks_path = os.path.join(output_dir, f"{Path(parsed_data['source_file']).stem}_chunks.json")
        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump({'chunks': chunks}, f, ensure_ascii=False, indent=2)
        
        print(f"   ✓ Created: {len(chunks)} chunks")
        print(f"   ✓ Saved: {chunks_path}")
        
        return {'chunks': chunks, 'chunks_path': chunks_path}
    
    def _chunk_parsed_data(self, parsed_data: Dict) -> List[Dict]:
        """Chunk parsed data"""
        chunks = []
        chunk_id = 1
        
        # Metadata chunk
        metadata = parsed_data.get('metadata', {})
        meta_text = f"{metadata.get('loai_van_ban', '')} {metadata.get('so_hieu', '')}\n"
        meta_text += f"Cơ quan ban hành: {metadata.get('co_quan_ban_hanh', '')}\n"
        meta_text += f"Ngày ban hành: {metadata.get('ngay_ban_hanh', '')}"
        
        chunks.append({
            'id': f'chunk_{chunk_id}',
            'text': meta_text.strip(),
            'metadata': {'type': 'metadata', **metadata}
        })
        chunk_id += 1
        
        # Can cu
        for cc in parsed_data.get('can_cu_phap_ly', []):
            chunks.append({
                'id': f'chunk_{chunk_id}',
                'text': f"Căn cứ: {cc}",
                'metadata': {'type': 'can_cu'}
            })
            chunk_id += 1
        
        # Chapters and Articles
        for chuong in parsed_data.get('chuong', []):
            c_so = chuong.get('so_chuong', '')
            c_ten = chuong.get('ten_chuong', '')
            
            for dieu in chuong.get('dieu', []):
                d_so = dieu.get('so_dieu', '')
                d_noi_dung = dieu.get('noi_dung', '')
                
                dieu_text = f"Chương {c_so}: {c_ten}\nĐiều {d_so}: {d_noi_dung}"
                
                for khoan in dieu.get('khoan', []):
                    k_so = khoan.get('so_khoan', '')
                    k_noi_dung = khoan.get('noi_dung', '')
                    dieu_text += f"\n{k_so}. {k_noi_dung}"
                    
                    for diem in khoan.get('diem', []):
                        d_so_diem = diem.get('so_diem', '')
                        d_nd = diem.get('noi_dung', '')
                        dieu_text += f"\n{d_so_diem}) {d_nd}"
                
                chunks.append({
                    'id': f'chunk_{chunk_id}',
                    'text': dieu_text,
                    'metadata': {
                        'type': 'dieu',
                        'chuong': c_so,
                        'dieu': d_so
                    }
                })
                chunk_id += 1
        
        return chunks
    
    def run(self, pdf_path: str) -> Dict:
        """Chạy toàn bộ pipeline"""
        output_dir = Path(self.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"COMPLETE PROTONX PIPELINE")
        print(f"Input: {pdf_path}")
        print(f"Output: {output_dir}")
        print(f"{'='*70}")
        
        # Step 1: OCR & Parse
        parsed_data = self.step1_ocr_and_parse(pdf_path, str(output_dir))
        
        # Step 2: Chunk
        chunk_result = self.step2_chunk(parsed_data, str(output_dir))
        
        # Summary
        print(f"\n{'='*70}")
        print("✅ PIPELINE COMPLETED")
        print(f"{'='*70}")
        print(f"Output directory: {output_dir}")
        print(f"Total chunks: {len(chunk_result['chunks'])}")
        print(f"{'='*70}\n")
        
        return {
            'parsed': parsed_data,
            'chunks': chunk_result['chunks'],
            'output_dir': str(output_dir)
        }


def main():
    parser = argparse.ArgumentParser(description='Complete Pipeline với ProtonX OCR')
    parser.add_argument('pdf_path', help='Đường dẫn đến file PDF')
    parser.add_argument('-o', '--output-dir', default='output_protonx_complete',
                        help='Thư mục lưu kết quả')
    parser.add_argument('--use-llm', action='store_true',
                        help='Sử dụng LLM để chuẩn hóa (chưa implement)')
    
    args = parser.parse_args()
    
    config = {
        'output_dir': args.output_dir,
        'use_llm': args.use_llm
    }
    
    pipeline = CompletePipelineProtonX(config)
    
    try:
        result = pipeline.run(args.pdf_path)
        print(f"\n✅ Hoàn thành! Kết quả tại: {result['output_dir']}")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
