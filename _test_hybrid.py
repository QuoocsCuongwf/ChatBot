"""Quick test: verify BM25 hybrid retrieval finds correct chunks."""
import sys, json, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "cross-encoder"))

# Test LegalRetriever hybrid
from generation.run_generation import LegalRetriever

print("=" * 70)
print("Loading LegalRetriever (hybrid BM25 + FAISS + CE) ...")
print("=" * 70)
t0 = time.perf_counter()
retriever = LegalRetriever(device="cuda")
print(f"Loaded in {time.perf_counter() - t0:.1f}s")
print(f"  BM25 ready: {retriever.bm25 is not None}")
print(f"  FAISS ready: {retriever.faiss_index is not None}")
print(f"  CE ready: {retriever.ce_model is not None}")

# Test queries that previously failed
test_queries = [
    "Thủ tục cấp giấy phép xây dựng",
    "Công chức làm công tác hộ tịch cần đáp ứng điều kiện gì",
    "Phân cấp quản lý nhà nước về giáo dục",
    "Thẩm quyền cấp phép hoạt động khoáng sản",
]

for q in test_queries:
    print(f"\n{'─' * 70}")
    print(f"Query: {q}")
    print(f"{'─' * 70}")
    
    chunks = retriever.retrieve_and_rerank(q, top_k_retrieve=100, top_k_rerank=5)
    
    for i, c in enumerate(chunks):
        text_preview = c.text[:120].replace("\n", " ")
        print(f"  #{i+1}  CE={c.score_rerank:+.3f}  FAISS={c.score_retrieval:.3f}  "
              f"id={c.chunk_id}  [{c.van_ban} Đ.{c.dieu} K.{c.khoan}]")
        print(f"       {text_preview}...")

print(f"\n{'=' * 70}")
print("Done!")
