# import argparse
# import json
# import os
# from typing import Any, Dict, List, Optional, Tuple

# import numpy as np
# import faiss
# from sentence_transformers import SentenceTransformer


# # =========================
# # Data loading
# # =========================
# def load_chunks(chunks_path: str) -> List[Dict[str, Any]]:
#     if not os.path.exists(chunks_path):
#         raise FileNotFoundError(f"chunks.json not found: {chunks_path}")

#     with open(chunks_path, "r", encoding="utf-8") as f:
#         chunks = json.load(f)

#     if not isinstance(chunks, list) or len(chunks) == 0:
#         raise ValueError("chunks.json must be a non-empty list")

#     # Ensure each chunk has id + metadata
#     for i, c in enumerate(chunks):
#         if not isinstance(c, dict):
#             raise ValueError(f"Chunk #{i} is not a dict")
#         if "text" not in c:
#             raise ValueError(f"Chunk #{i} missing 'text'")
#         if "metadata" not in c or c["metadata"] is None:
#             c["metadata"] = {}
#         if "id" not in c or c["id"] is None:
#             c["id"] = f"chunk_{i:06d}"
#     return chunks


# def get_source(md: Dict[str, Any]) -> Any:
#     # Your chunks use source_file; normalize to one output field
#     return md.get("nguon") or md.get("source_file") or md.get("source") or md.get("file")


# def pretty_meta(md: Dict[str, Any]) -> Dict[str, Any]:
#     return {
#         "van_ban": md.get("van_ban"),
#         "chuong": md.get("chuong"),
#         "dieu": md.get("dieu"),
#         "khoan": md.get("khoan"),
#         "diem": md.get("diem"),
#         "nguon": get_source(md),
#         "page": md.get("page"),
#     }


# # =========================
# # Cosine helpers
# # =========================
# def l2_normalize(v: np.ndarray) -> np.ndarray:
#     v = v.astype(np.float32)
#     faiss.normalize_L2(v)
#     return v


# def passes_filter(md: Dict[str, Any], filter_source: Optional[str], filter_vanban: Optional[str]) -> bool:
#     if filter_source:
#         src = str(get_source(md) or "")
#         if filter_source.lower() not in src.lower():
#             return False
#     if filter_vanban:
#         vb = str(md.get("van_ban") or "")
#         if filter_vanban.lower() not in vb.lower():
#             return False
#     return True


# # =========================
# # Build cosine index (IP + normalized embeddings)
# # =========================
# def build_cosine_index(
#     chunks: List[Dict[str, Any]],
#     encoder: SentenceTransformer,
#     batch_size: int,
# ) -> Tuple[faiss.Index, np.ndarray]:
#     texts = [(c.get("text") or "").strip() for c in chunks]
#     texts = [t if t else " " for t in texts]

#     emb = encoder.encode(
#         texts,
#         batch_size=batch_size,
#         convert_to_numpy=True,
#         show_progress_bar=True
#     ).astype(np.float32)

#     if emb.ndim != 2:
#         raise RuntimeError(f"Embeddings must be 2D. Got shape={emb.shape}")

#     # Normalize embeddings => cosine
#     faiss.normalize_L2(emb)

#     dim = emb.shape[1]
#     index = faiss.IndexFlatIP(dim)
#     index.add(emb)

#     # sanity: must be IP
#     if index.metric_type != faiss.METRIC_INNER_PRODUCT:
#         raise RuntimeError("Cosine index build failed: metric is not IP")

#     return index, emb


# def save_index(out_dir: str, index: faiss.Index, emb: np.ndarray, chunks_path: str, model: str):
#     os.makedirs(out_dir, exist_ok=True)
#     index_path = os.path.join(out_dir, "index.faiss")
#     emb_path = os.path.join(out_dir, "embeddings.npy")
#     manifest_path = os.path.join(out_dir, "manifest.json")

#     faiss.write_index(index, index_path)
#     np.save(emb_path, emb)

#     manifest = {
#         "chunks_path": chunks_path,
#         "model": model,
#         "faiss_index": "IndexFlatIP",
#         "metric_type": int(index.metric_type),  # expect 1
#         "cosine": True,
#         "ntotal": int(index.ntotal),
#         "dim": int(index.d),
#     }
#     with open(manifest_path, "w", encoding="utf-8") as f:
#         json.dump(manifest, f, ensure_ascii=False, indent=2)

#     return index_path


# def load_index_or_build(
#     out_dir: str,
#     chunks: List[Dict[str, Any]],
#     encoder: SentenceTransformer,
#     batch_size: int,
#     chunks_path: str,
#     model: str,
#     rebuild: bool,
# ) -> faiss.Index:
#     index_path = os.path.join(out_dir, "index.faiss")

#     if (not rebuild) and os.path.exists(index_path):
#         index = faiss.read_index(index_path)

#         # HARD FAIL if not cosine/IP
#         if getattr(index, "metric_type", None) != faiss.METRIC_INNER_PRODUCT:
#             raise RuntimeError(
#                 f"Found existing index but metric_type={index.metric_type} != IP.\n"
#                 f"Index at: {index_path}\n"
#                 "=> Đây không phải cosine index. Xóa/rebuild hoặc dùng --rebuild."
#             )

#         if index.ntotal != len(chunks):
#             raise RuntimeError(
#                 f"Existing index ntotal={index.ntotal} != len(chunks)={len(chunks)}.\n"
#                 "=> Mapping lệch. Hãy dùng --rebuild để build lại đúng thứ tự chunks.json."
#             )

#         return index

#     # Build new cosine index
#     index, emb = build_cosine_index(chunks, encoder, batch_size=batch_size)
#     saved_path = save_index(out_dir, index, emb, chunks_path=chunks_path, model=model)
#     print(f"✅ Built & saved COSINE index to: {saved_path}")
#     return index


# # =========================
# # Retrieval
# # =========================
# def retrieve_cosine(
#     question: str,
#     chunks: List[Dict[str, Any]],
#     index: faiss.Index,
#     encoder: SentenceTransformer,
#     topk: int,
#     preview_chars: int,
#     filter_source: Optional[str],
#     filter_vanban: Optional[str],
#     oversample: int = 80,
# ) -> Dict[str, Any]:
#     # Encode + normalize query
#     q_vec = encoder.encode([question], convert_to_numpy=True, show_progress_bar=False).astype(np.float32)
#     q_vec = l2_normalize(q_vec)

#     # Search more then filter down
#     search_k = max(topk, oversample)
#     scores, ids = index.search(q_vec, search_k)

#     hits = []
#     for idx, sc in zip(ids[0], scores[0]):
#         if idx < 0:
#             continue
#         chunk = chunks[int(idx)]
#         md = chunk.get("metadata") or {}
#         if not passes_filter(md, filter_source, filter_vanban):
#             continue

#         hits.append({
#             "rank": len(hits) + 1,
#             "faiss_id": int(idx),
#             "score": float(sc),  # cosine similarity
#             "chunk_id": chunk.get("id"),
#             "metadata": pretty_meta(md),
#             "text_preview": (chunk.get("text") or "")[:preview_chars],
#         })

#         if len(hits) >= topk:
#             break

#     return {
#         "question": question,
#         "topk": topk,
#         "cosine": True,
#         "filter_source": filter_source,
#         "filter_vanban": filter_vanban,
#         "hits": hits,
#     }


# # =========================
# # CLI
# # =========================
# def main():
#     ap = argparse.ArgumentParser(description="ONE-FILE Cosine Retrieval (build + search, no L2)")
#     ap.add_argument("-q", "--question", required=True, help="Câu hỏi truy vấn")

#     ap.add_argument("--chunks", default="output_nghidinh/chunks_clean.json", help="Path to chunks.json")
#     ap.add_argument("--out_dir", default="vector_data/cosine_only", help="Where cosine index is stored")
#     ap.add_argument("--model", default="Quockhanh05/Vietnam_legal_embeddings", help="Encoder model")
#     ap.add_argument("--device", default="cuda", help="cuda or cpu")
#     ap.add_argument("--batch_size", type=int, default=32)

#     ap.add_argument("--topk", type=int, default=5)
#     ap.add_argument("--preview_chars", type=int, default=700)
#     ap.add_argument("--show_debug", action="store_true")
#     ap.add_argument("--rebuild", action="store_true", help="Force rebuild cosine index")

#     # Filters (optional)
#     ap.add_argument("--filter_source", default=None, help="Substring match in source_file (e.g. 'qlyBTP' or '120-cp')")
#     ap.add_argument("--filter_vanban", default=None, help="Substring match in van_ban (e.g. 'Bộ Tư pháp')")

#     args = ap.parse_args()

#     # Load chunks
#     chunks = load_chunks(args.chunks)

#     # Load encoder
#     encoder = SentenceTransformer(args.model, device=args.device)

#     # Load or build cosine index
#     index = load_index_or_build(
#         out_dir=args.out_dir,
#         chunks=chunks,
#         encoder=encoder,
#         batch_size=args.batch_size,
#         chunks_path=args.chunks,
#         model=args.model,
#         rebuild=args.rebuild
#     )

#     # Final hard check
#     if index.metric_type != faiss.METRIC_INNER_PRODUCT:
#         raise RuntimeError("FATAL: index is not IP => not cosine. Something is wrong.")

#     if args.show_debug:
#         print("===== DEBUG =====")
#         print("Chunks:", len(chunks))
#         print("Index ntotal:", index.ntotal)
#         print("Index dim (d):", index.d)
#         print("Metric type:", index.metric_type, "(expect IP=1)")
#         print("Index path dir:", args.out_dir)
#         print("=================")

#     # Retrieve
#     out = retrieve_cosine(
#         question=args.question,
#         chunks=chunks,
#         index=index,
#         encoder=encoder,
#         topk=args.topk,
#         preview_chars=args.preview_chars,
#         filter_source=args.filter_source,
#         filter_vanban=args.filter_vanban,
#     )

#     print(json.dumps(out, ensure_ascii=False, indent=2))


# if __name__ == "__main__":
#     main()
import faiss
import os
index = faiss.read_index(r"D:\GitHub\ChatBot\vector_data\legal_hf_cosine\index.faiss")
print(index.metric_type)
print(index.metric_type == faiss.METRIC_INNER_PRODUCT)
# print("Saved at:", os.path.abspath(os.path.join(index, "index.faiss")))