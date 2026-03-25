"""Diagnostic: trace exactly what chunks go into the LLM context."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "cross-encoder"))

from generation.run_generation import LegalRetriever
from generation.context_builder import ContextBuilder
from generation.rag_contract import RAGPolicy

retriever = LegalRetriever(device="cuda")
context_builder = ContextBuilder(policy=RAGPolicy())

queries = [
    "Thủ tục cấp giấy phép xây dựng",
    "Công chức làm công tác hộ tịch cần đáp ứng điều kiện gì",
    "Phân cấp quản lý nhà nước về giáo dục",
]

TOP_K_CHUNKS = 5  # same as pipeline

for q in queries:
    print(f"\n{'='*80}")
    print(f"QUERY: {q}")
    print(f"{'='*80}")
    
    # Step 1: Retrieve (same as pipeline: top_k_rerank = top_k_chunks * 2 = 10)
    chunks = retriever.retrieve_and_rerank(q, top_k_rerank=TOP_K_CHUNKS * 2)
    
    print(f"\n--- RETRIEVED {len(chunks)} chunks (before context build) ---")
    for i, c in enumerate(chunks):
        preview = c.text[:80].replace("\n", " ")
        print(f"  [{i+1}] CE={c.score_rerank:+.3f}  id={c.chunk_id:4d}  "
              f"[{c.van_ban[:40]}.. Đ.{c.dieu} K.{c.khoan}]")
        print(f"       {preview}...")
    
    # Step 2: Context build (dedup + trim → max_chunks=5)
    processed, context_string = context_builder.build(
        chunks=chunks, query=q, max_chunks=TOP_K_CHUNKS
    )
    
    print(f"\n--- CONTEXT SENT TO LLM: {len(processed)} chunks, ~{len(context_string)} chars ---")
    for i, c in enumerate(processed):
        preview = (c.trimmed_text or c.text)[:100].replace("\n", " ")
        print(f"  [{i+1}] CE={c.score_rerank:+.3f}  id={c.chunk_id:4d}  "
              f"[Đ.{c.dieu} K.{c.khoan}]  {preview}...")
    
    # Show actual context string
    print(f"\n--- RAW CONTEXT STRING (first 2000 chars) ---")
    print(context_string[:2000])
    print(f"... (total {len(context_string)} chars)")

print("\n\nDone!")
