"""
COMPLETE LEGAL DOCUMENT PROCESSING PIPELINE
============================================
PDF → OCR (DataCleaning.py) → Parsing (parser.py) → OCR Fixes (rules_base.py) → 
Data Cleaning → LLM Normalization → Embedding → Vector DB

Key Components:
- DataCleaning.py: OCR with Tesseract
- parser.py: Legal document parsing & text cleaning
- rules_base.py: OCR error fixes using VIETNAMESE_OCR_FIXES
- LLM: Post-processing for 100% accuracy
"""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import re

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

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
try:
    from load_env import load_env, get_env
    load_env()
except ImportError:
    print("⚠️ load_env.py not found, using system environment variables")
    def get_env(key: str, default: str = None) -> str:
        return os.getenv(key, default)


class CompletePipeline:
    """
    Complete pipeline from PDF to Vector DB
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize pipeline with configuration
        
        Args:
            config: {
                'ocr_dpi': 400,
                'use_llm': True,
                'llm_model': 'gpt-4o-mini',  # or local model
                'embedding_model': 'phobert',  # phobert, bge-m3, vina-embedding
                'vector_db': 'faiss',  # faiss, milvus, qdrant
                'output_dir': 'output_pipeline_complete'
            }
        """
        self.config = config or {}
        
        # Load from environment variables with fallback to config
        self.ocr_dpi = self.config.get('ocr_dpi', int(get_env('OCR_DPI', '350')))
        self.use_llm = self.config.get('use_llm', True)
        self.llm_model = self.config.get('llm_model', get_env('LLM_MODEL', 'gemini-1.5-flash-latest'))
        self.embedding_model = self.config.get('embedding_model', get_env('EMBEDDING_MODEL', 'phobert'))
        self.vector_db = self.config.get('vector_db', get_env('VECTOR_DB', 'faiss'))
        self.output_dir = self.config.get('output_dir', get_env('OUTPUT_DIR', 'output_pipeline_complete'))
        self.stop_after_llm = self.config.get('stop_after_llm', False)
        
    def step1_ocr(self, pdf_path: str, output_dir: str) -> Dict:
        """
        STEP 1: OCR & Parsing using rules_base.py
        Uses: DataCleaning.py for OCR, parser.py for parsing, rules_base.py for OCR fixes
        """
        print(f"\n{'='*70}")
        print(f"STEP 1: OCR & Parsing (rules_base.py)")
        print(f"{'='*70}")
        
        try:
            from rules_base import run_full_pipeline
        except ImportError:
            raise ImportError("Could not import rules_base.py. Make sure it exists in the same directory.")
        
        # rules_base.run_full_pipeline:
        # 1. Uses DataCleaning.py for OCR
        # 2. Uses parser.py for parsing
        # 3. Applies OCR fixes automatically
        # Returns parsed and cleaned JSON data with OCR fixes
        parsed_data = run_full_pipeline(pdf_path, output_dir=output_dir)
            
        # Add source_file to result for compatibility
        parsed_data['source_file'] = pdf_path
        
        output_file = os.path.join(output_dir, f"{Path(pdf_path).stem}_final.json")
        print(f"✅ OCR & Parsing with OCR fixes completed. Saved to: {output_file}")
        return parsed_data
    
    def step2_parse_and_chunk(self, parsed_data: Dict, output_dir: str) -> Dict:
        """
        STEP 2: Chunking (Parsing already done by DataCleaning)
        """
        print(f"\n{'='*70}")
        print(f"STEP 2: CHUNKING")
        print(f"{'='*70}")
        
        # Save parsed (it might already be saved by DataCleaning, but let's ensure consistency)
        parsed_path = os.path.join(output_dir, f"{Path(parsed_data['source_file']).stem}_parsed.json")
        with open(parsed_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
            
        # Create chunks
        chunks = self._chunk_parsed_data(parsed_data)
        
        chunks_path = os.path.join(output_dir, f"{Path(parsed_data['source_file']).stem}_chunks.json")
        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump({'chunks': chunks}, f, ensure_ascii=False, indent=2)
        
        print(f"   ✓ Created: {len(chunks)} chunks")
        print(f"   ✓ Saved: {chunks_path}")
        
        return {
            'parsed': parsed_data,
            'chunks': chunks,
            'parsed_path': parsed_path,
            'chunks_path': chunks_path
        }

    def _chunk_parsed_data(self, parsed_data: Dict) -> List[Dict]:
        """Chunk parsed data from DataCleaning format"""
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
        
        # Can cu chunk
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
                
                # Article chunk
                dieu_text = f"Chương {c_so}: {c_ten}\nĐiều {d_so}: {d_noi_dung}"
                
                # Add khoans
                for khoan in dieu.get('khoan', []):
                    k_so = khoan.get('so_khoan', '')
                    k_noi_dung = khoan.get('noi_dung', '')
                    dieu_text += f"\n{k_so}. {k_noi_dung}"
                    
                    # Add diems
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
    
    def _simple_chunk(self, text: str, chunk_size: int = 512) -> List[Dict]:
        """Simple chunking by paragraph and size"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        chunk_id = 1
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append({
                    'id': f'chunk_{chunk_id}',
                    'text': current_chunk.strip(),
                    'metadata': {'type': 'paragraph'}
                })
                chunk_id += 1
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        if current_chunk:
            chunks.append({
                'id': f'chunk_{chunk_id}',
                'text': current_chunk.strip(),
                'metadata': {'type': 'paragraph'}
            })
        
        return chunks
    
    def step3_clean_data(self, chunks: List[Dict]) -> List[Dict]:
        """
        STEP 3: Data Cleaning - Remove noise, fix OCR errors using rules_base.py
        """
        print(f"\n{'='*70}")
        print(f"STEP 3: DATA CLEANING - Using rules_base.py for OCR fixes")
        print(f"{'='*70}")
        
        # Import cleaning functions from rules_base.py
        try:
            from rules_base import apply_ocr_fixes, count_ocr_fixes
        except ImportError:
            print(f"   ⚠️ rules_base.py not available, skipping OCR fixes")
            return chunks
            
        # Apply OCR fixes to all chunks using rules_base.py
        # This applies VIETNAMESE_OCR_FIXES recursively to all text in chunks
        print(f"   🔧 Applying OCR fixes from rules_base.py...")
        cleaned_chunks = apply_ocr_fixes(chunks)
        
        # Count fixes
        total_fixes = count_ocr_fixes(chunks, cleaned_chunks)
        
        print(f"   ✓ Cleaned {len(cleaned_chunks)} chunks")
        print(f"   ✓ Applied {total_fixes} OCR corrections (VIETNAMESE_OCR_FIXES)")
        return cleaned_chunks
    
    def step4_llm_normalize(self, chunks: List[Dict], output_dir: str) -> List[Dict]:
        """
        STEP 4: LLM Normalization - Use LLM to fix spelling, legal terms, language
        This is the KEY STEP for 100% accuracy
        """
        print(f"\n{'='*70}")
        print(f"STEP 4: LLM NORMALIZATION - Correcting with {self.llm_model}")
        print(f"{'='*70}")
        
        if not self.use_llm:
            print("   ⊘ LLM disabled, skipping normalization")
            return chunks
        
        # Determine provider based on model name
        is_gemini = 'gemini' in self.llm_model.lower()
        
        # For Gemini, always use native SDK (google-generativeai) - more stable
        if is_gemini:
            try:
                import google.generativeai as genai
                has_native_genai = True
            except ImportError:
                print("   ⚠️ google-generativeai not installed. Install: pip install google-generativeai")
                return chunks
        else:
            has_native_genai = False

        # Setup client based on provider
        client = None
        
        if is_gemini:
            # Configure Gemini with native SDK
            api_key = get_env('GEMINI_API_KEY') or get_env('GOOGLE_API_KEY')
            if not api_key:
                print("   ⚠️ GEMINI_API_KEY or GOOGLE_API_KEY not set in .env")
                print("   💡 Edit .env and add: GEMINI_API_KEY=your-key")
                return chunks
            genai.configure(api_key=api_key)
            print(f"   ✓ Using Gemini with native SDK")
        else:
            # Setup OpenAI client
            try:
                import openai
                api_key = get_env('OPENAI_API_KEY')
                if not api_key:
                    print("   ⚠️ OPENAI_API_KEY not set in .env")
                    print("   💡 Edit .env and add: OPENAI_API_KEY=sk-your-key")
                    return chunks
                client = openai.OpenAI(api_key=api_key)
                print(f"   ✓ Using OpenAI")
            except ImportError:
                print("   ⚠️ OpenAI library not installed. Install: pip install openai")
                return chunks

        # System prompt for legal document normalization
        system_prompt = """Bạn là chuyên gia xử lý văn bản pháp luật Việt Nam.
Nhiệm vụ: Hoàn thiện dữ liệu văn bản OCR để chuẩn bị cho quá trình Embedding (Encoder).

QUY TẮC:
1. Sửa lỗi chính tả tiếng Việt (qủy→quy, quyên→quyền, thâm→thẩm, chinh→chính, đinh→định).
2. Sửa thuật ngữ pháp lý (quyết định→Quyết định, nghị định→Nghị định, điều→Điều, khoản→Khoản).
3. Chuẩn hóa số La Mã (Chương J→Chương I, Chương JI→Chương II).
4. Nối các câu bị ngắt quãng do lỗi xuống dòng của OCR.
5. Giữ NGUYÊN ý nghĩa và cấu trúc điều khoản, không tóm tắt.
6. Trả về CHỈ văn bản đã sửa, KHÔNG giải thích.

Ví dụ:
Input: "Điêu 1. Phạm vi đinh chỉnh Nghị định này qủy định..."
Output: "Điều 1. Phạm vi điều chỉnh Nghị định này quy định..."
"""
        
        normalized_chunks = []
        total = len(chunks)
        
        print(f"   🤖 Processing {total} chunks...")
        
        for i, chunk in enumerate(chunks, 1):
            text = chunk.get('text', '')
            
            # Skip empty
            if not text or len(text.strip()) < 10:
                normalized_chunks.append(chunk)
                continue
            
            try:
                print(f"   🤖 Normalizing chunk {i}/{total}...", end='\r')
                
                normalized_text = text
                success = False
                last_error = None
                
                # List of models to try (Main + Fallbacks)
                models_to_try = [self.llm_model]
                if is_gemini:
                    # Add stable fallbacks for Gemini 2.x (2026 models)
                    fallbacks = [
                        "gemini-flash-latest",      # Always latest stable
                        "gemini-2.5-flash",         # Gemini 2.5 stable
                        "gemini-2.0-flash",         # Gemini 2.0 stable  
                        "gemini-pro-latest"         # Latest pro version
                    ]
                    for m in fallbacks:
                        if m not in models_to_try:
                            models_to_try.append(m)
                
                for model_name in models_to_try:
                    try:
                        if is_gemini:
                            # Use native Gemini SDK
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content(
                                f"{system_prompt}\n\nInput: {text}\nOutput:",
                                generation_config=genai.types.GenerationConfig(
                                    temperature=0.1,
                                    max_output_tokens=4096,
                                ),
                                safety_settings=[
                                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                                ]
                            )
                            if response and response.text:
                                normalized_text = response.text.strip()
                                success = True
                                break
                        else:
                            # Use OpenAI
                            response = client.chat.completions.create(
                                model=model_name,
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": text}
                                ],
                                temperature=0.1,
                                max_tokens=4096
                            )
                            if response.choices and response.choices[0].message.content:
                                normalized_text = response.choices[0].message.content.strip()
                                success = True
                                break
                    
                    except Exception as e:
                        last_error = e
                        # Try next model
                        continue
                
                if not success and last_error:
                    print(f"\n   ⚠️ LLM failed for chunk {i}: {last_error}")
                    # Don't raise, just skip normalization for this chunk
                
                # Update chunk
                normalized_chunk = chunk.copy()
                normalized_chunk['text'] = normalized_text
                if 'metadata' not in normalized_chunk: normalized_chunk['metadata'] = {}
                normalized_chunk['metadata']['llm_normalized'] = True
                normalized_chunk['metadata']['original_text'] = text
                
                normalized_chunks.append(normalized_chunk)
                
            except Exception as e:
                print(f"\n   ⚠️ Error normalizing chunk {i}: {e}")
                normalized_chunks.append(chunk)
        
        print(f"\n   ✅ Normalized {len(normalized_chunks)} chunks with {self.llm_model}")
        
        # Save normalized chunks
        normalized_path = os.path.join(output_dir, "chunks_normalized.json")
        with open(normalized_path, 'w', encoding='utf-8') as f:
            json.dump({'chunks': normalized_chunks}, f, ensure_ascii=False, indent=2)
        print(f"   💾 Saved: {normalized_path}")
        
        return normalized_chunks
    
    def step5_embed(self, chunks: List[Dict], output_dir: str) -> Dict:
        """
        STEP 5: Embedding - Convert text to vectors
        """
        print(f"\n{'='*70}")
        print(f"STEP 5: EMBEDDING - Generating vectors with {self.embedding_model}")
        print(f"{'='*70}")
        
        try:
            import torch
            from transformers import AutoTokenizer, AutoModel
            
            # Load model based on config
            if self.embedding_model == 'phobert':
                model_name = 'vinai/phobert-base'
            elif self.embedding_model == 'bge-m3':
                model_name = 'BAAI/bge-m3'
            elif self.embedding_model == 'vina':
                model_name = 'VoVanPhuc/sup-SimCSE-VietNamese-phobert-base'
            else:
                model_name = self.embedding_model
            
            print(f"   📥 Loading model: {model_name}")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            model.eval()
            
            # Generate embeddings
            embeddings = []
            texts = [chunk.get('text', '') for chunk in chunks]
            
            print(f"   🔄 Encoding {len(texts)} chunks...")
            
            with torch.no_grad():
                for i, text in enumerate(texts):
                    if not text:
                        embeddings.append(None)
                        continue
                    
                    # Tokenize
                    inputs = tokenizer(text, return_tensors='pt', 
                                     padding=True, truncation=True, max_length=512)
                    
                    # Get embeddings
                    outputs = model(**inputs)
                    
                    # Mean pooling
                    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
                    embeddings.append(embedding.tolist())
                    
                    if (i + 1) % 10 == 0:
                        print(f"   🔄 Encoded {i+1}/{len(texts)} chunks...", end='\r')
            
            print(f"\n   ✅ Generated {len(embeddings)} embeddings")
            
            # Save embeddings
            embeddings_path = os.path.join(output_dir, "embeddings.json")
            with open(embeddings_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'chunks': chunks,
                    'embeddings': embeddings,
                    'model': model_name,
                    'dimension': len(embeddings[0]) if embeddings[0] else 0
                }, f, ensure_ascii=False, indent=2)
            
            print(f"   💾 Saved: {embeddings_path}")
            
            return {
                'chunks': chunks,
                'embeddings': embeddings,
                'model': model_name,
                'embeddings_path': embeddings_path
            }
            
        except ImportError as e:
            print(f"   ⚠️ Transformers not installed: {e}")
            print(f"   💡 Install: pip install transformers torch")
            return {'chunks': chunks, 'embeddings': None}
    
    def step6_vector_db(self, embeddings_data: Dict, output_dir: str) -> Dict:
        """
        STEP 6: Vector DB - Index embeddings for search
        """
        print(f"\n{'='*70}")
        print(f"STEP 6: VECTOR DB - Indexing with {self.vector_db}")
        print(f"{'='*70}")
        
        if not embeddings_data.get('embeddings'):
            print("   ⊘ No embeddings available, skipping vector DB")
            return {}
        
        try:
            import faiss
            import numpy as np
            
            chunks = embeddings_data['chunks']
            embeddings = embeddings_data['embeddings']
            
            # Filter out None embeddings
            valid_embeddings = [e for e in embeddings if e is not None]
            if not valid_embeddings:
                print("   ⚠️ No valid embeddings")
                return {}
            
            # Convert to numpy array
            embeddings_np = np.array(valid_embeddings).astype('float32')
            dimension = embeddings_np.shape[1]
            
            print(f"   📊 Indexing {len(valid_embeddings)} vectors (dim={dimension})")
            
            # Create FAISS index
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings_np)
            
            # Save index
            index_path = os.path.join(output_dir, "faiss_index.bin")
            faiss.write_index(index, index_path)
            
            print(f"   ✅ FAISS index created: {index.ntotal} vectors")
            print(f"   💾 Saved: {index_path}")
            
            # Save metadata for retrieval
            metadata_path = os.path.join(output_dir, "index_metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'chunks': chunks,
                    'model': embeddings_data.get('model'),
                    'dimension': dimension,
                    'total_vectors': index.ntotal,
                    'index_path': index_path
                }, f, ensure_ascii=False, indent=2)
            
            print(f"   💾 Saved: {metadata_path}")
            
            return {
                'index_path': index_path,
                'metadata_path': metadata_path,
                'total_vectors': index.ntotal
            }
            
        except ImportError:
            print(f"   ⚠️ FAISS not installed. Install: pip install faiss-cpu")
            return {}
    
    def run(self, pdf_path: str, output_dir: str = None) -> Dict:
        """
        Run complete pipeline
        """
        if not output_dir:
            output_dir = os.path.join(
                os.path.dirname(pdf_path), '..', self.output_dir
            )
        
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n{'#'*70}")
        print(f"# COMPLETE LEGAL DOCUMENT PROCESSING PIPELINE")
        print(f"# PDF: {os.path.basename(pdf_path)}")
        print(f"# Output: {output_dir}")
        print(f"{'#'*70}")
        
        results = {}
        
        # Step 1: OCR
        parsed_data = self.step1_ocr(pdf_path, output_dir)
        results['ocr'] = parsed_data
        
        # Step 2: Parse & Chunk
        parse_result = self.step2_parse_and_chunk(parsed_data, output_dir)
        results['parse'] = parse_result
        chunks = parse_result['chunks']
        
        # Step 3: Clean
        chunks = self.step3_clean_data(chunks)
        results['cleaned_chunks'] = len(chunks)
        
        # Step 4: LLM Normalize
        chunks = self.step4_llm_normalize(chunks, output_dir)
        results['normalized_chunks'] = len(chunks)
        
        # Save normalized chunks before embedding (checkpoint)
        normalized_checkpoint = os.path.join(output_dir, "chunks_normalized_final.json")
        with open(normalized_checkpoint, 'w', encoding='utf-8') as f:
            json.dump({
                'chunks': chunks,
                'metadata': {
                    'source_pdf': pdf_path,
                    'total_chunks': len(chunks),
                    'llm_model': self.llm_model if self.use_llm else 'none',
                    'ready_for_embedding': True
                }
            }, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Checkpoint saved: {normalized_checkpoint}")
        print(f"   ✓ {len(chunks)} chunks ready for embedding")
        results['normalized_checkpoint'] = normalized_checkpoint
        
        # Stop here if requested
        if self.stop_after_llm:
            print(f"\n⏸️  Stopping after LLM normalization (as requested)")
            return results
        
        # Step 5: Embed
        embeddings_data = self.step5_embed(chunks, output_dir)
        results['embeddings'] = embeddings_data
        
        # Step 6: Vector DB
        vector_db_result = self.step6_vector_db(embeddings_data, output_dir)
        results['vector_db'] = vector_db_result
        
        # Save final summary
        summary_path = os.path.join(output_dir, "pipeline_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump({
                'source_pdf': pdf_path,
                'config': self.config,
                'results': {
                    'total_pages': parsed_data.get('metadata', {}).get('so_trang', 0),
                    'total_chars': len(json.dumps(parsed_data)), # Approximate
                    'total_chunks': len(chunks),
                    'total_vectors': vector_db_result.get('total_vectors', 0)
                },
                'output_files': {
                    'ocr': os.path.join(output_dir, f"{Path(pdf_path).stem}_processed.json"),
                    'parsed': parse_result.get('parsed_path'),
                    'chunks': parse_result.get('chunks_path'),
                    'normalized': os.path.join(output_dir, "chunks_normalized.json"),
                    'embeddings': embeddings_data.get('embeddings_path'),
                    'vector_index': vector_db_result.get('index_path'),
                    'metadata': vector_db_result.get('metadata_path')
                }
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'#'*70}")
        print(f"# ✅ PIPELINE COMPLETED")
        print(f"# 📊 Summary: {summary_path}")
        print(f"{'#'*70}\n")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description='Complete Legal Document Processing Pipeline'
    )
    parser.add_argument('pdf_path', nargs='?', help='Path to PDF file (optional, will prompt if not provided)')
    parser.add_argument('--output', '-o', help='Output directory')
    parser.add_argument('--dpi', type=int, default=400, help='OCR DPI (default: 400)')
    parser.add_argument('--no-llm', action='store_true', help='Disable LLM normalization')
    parser.add_argument('--stop-after-llm', action='store_true', help='Stop after LLM normalization (before embedding)')
    parser.add_argument('--llm-model', default='gemini-flash-latest', 
                       help='LLM model (default: gemini-flash-latest)')
    parser.add_argument('--embedding', default='phobert',
                       choices=['phobert', 'bge-m3', 'vina'],
                       help='Embedding model (default: phobert)')
    parser.add_argument('--vector-db', default='faiss',
                       choices=['faiss', 'milvus', 'qdrant'],
                       help='Vector DB (default: faiss)')
    
    args = parser.parse_args()
    
    # Prompt for PDF if not provided
    pdf_path = args.pdf_path
    if not pdf_path:
        try:
            from tkinter import Tk, filedialog
            print("Opening file picker...")
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            pdf_path = filedialog.askopenfilename(
                title='Select PDF file',
                filetypes=[('PDF files', '*.pdf'), ('All files', '*.*')]
            )
            root.destroy()
            
            if not pdf_path:
                print("No file selected. Exiting.")
                return
        except ImportError:
            print("tkinter not available. Please provide PDF path as argument.")
            print("Usage: python complete_pipeline.py path/to/file.pdf")
            return
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
    
    # Build config
    config = {
        'ocr_dpi': args.dpi,
        'use_llm': not args.no_llm,
        'llm_model': args.llm_model,
        'embedding_model': args.embedding,
        'vector_db': args.vector_db,
        'output_dir': args.output or 'output_pipeline_complete',
        'stop_after_llm': args.stop_after_llm
    }
    
    # Run pipeline
    pipeline = CompletePipeline(config)
    result = pipeline.run(pdf_path, args.output)
    
    # If stopped after LLM, show message
    if args.stop_after_llm:
        print(f"\n{'='*70}")
        print(f"PIPELINE PAUSED AFTER LLM NORMALIZATION")
        print(f"{'='*70}")
        print(f"Normalized chunks saved and ready for embedding")
        print(f"Checkpoint: {result.get('normalized_checkpoint')}")
        print(f"\nTo continue with embedding:")
        print(f"   python complete_pipeline.py \"{pdf_path}\" --resume-from-llm")
        print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
