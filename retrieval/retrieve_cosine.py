import argparse
import json
import os
from typing import Any, Dict, List, Optional

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


def load_chunks(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"chunks_clean.json not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not isinstance(chunks, list) or len(chunks) == 0:
        raise ValueError("chunks_clean.json must be a non-empty list")

    for i, c in enumerate(chunks):
        if "metadata" not in c or c["metadata"] is None:
            c["metadata"] = {}
        if "id" not in c or c["id"] is None:
            c["id"] = f"chunk_{i:06d}"

    return chunks


def l2_normalize(v: np.ndarray) -> np.ndarray:
    v = v.astype(np.float32)
    faiss.normalize_L2(v)
    return v


def get_source(md: Dict[str, Any]) -> Any:
    # Your chunks use 'source_file'
    return md.get("nguon") or md.get("source_file") or md.get("source") or md.get("file")


def pretty_meta(md: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "van_ban": md.get("van_ban"),
        "chuong": md.get("chuong"),
        "dieu": md.get("dieu"),
        "khoan": md.get("khoan"),
        "diem": md.get("diem"),
        "nguon": get_source(md),
        "page": md.get("page"),
    }


def passes_filter(md: Dict[str, Any], filter_source: Optional[str], filter_vanban: Optional[str]) -> bool:
    if filter_source:
        src = str(get_source(md) or "")
        if filter_source.lower() not in src.lower():
            return False
    if filter_vanban:
        vb = str(md.get("van_ban") or "")
        if filter_vanban.lower() not in vb.lower():
            return False
    return True


def build_hit(rank: int, idx: int, score: float, chunk: Dict[str, Any], preview_chars: int) -> Dict[str, Any]:
    md = chunk.get("metadata") or {}
    return {
        "rank": rank,
        "faiss_id": int(idx),
        "score": float(score),  # cosine similarity in [-1,1] (usually 0..1 for good matches)
        "chunk_id": chunk.get("id"),
        "metadata": pretty_meta(md),
        "text_preview": (chunk.get("text") or "")[:preview_chars],
    }


def retrieve_cosine(
    question: str,
    chunks: List[Dict[str, Any]],
    index: faiss.Index,
    encoder: SentenceTransformer,
    topk: int,
    preview_chars: int,
    filter_source: Optional[str],
    filter_vanban: Optional[str],
    oversample: int = 80,
) -> Dict[str, Any]:
    q_vec = encoder.encode([question], convert_to_numpy=True, show_progress_bar=False).astype(np.float32)
    q_vec = l2_normalize(q_vec)  # cosine mode: always normalize query

    search_k = max(topk, oversample)
    scores, ids = index.search(q_vec, search_k)

    kept = []
    for idx, sc in zip(ids[0], scores[0]):
        if idx < 0:
            continue
        chunk = chunks[int(idx)]
        md = chunk.get("metadata") or {}
        if not passes_filter(md, filter_source, filter_vanban):
            continue
        kept.append((int(idx), float(sc), chunk))
        if len(kept) >= topk:
            break

    hits = [build_hit(r, idx, sc, ch, preview_chars) for r, (idx, sc, ch) in enumerate(kept, start=1)]

    return {
        "question": question,
        "topk": topk,
        "cosine": True,
        "filter_source": filter_source,
        "filter_vanban": filter_vanban,
        "hits": hits,
    }


def main():
    ap = argparse.ArgumentParser(description="Cosine retrieval (FAISS IndexFlatIP + normalized vectors)")
    ap.add_argument("-q", "--question", required=True)
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--chunks", default="output_nghidinh/chunks_clean.json")
    ap.add_argument("--index", default="vector_data/legal_hf_cosine/index.faiss")
    ap.add_argument("--model", default="Quockhanh05/Vietnam_legal_embeddings")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--preview_chars", type=int, default=700)
    ap.add_argument("--show_debug", action="store_true")

    ap.add_argument("--filter_source", default=None, help="Substring match in source_file (e.g. 'qlyBTP' or '120-cp')")
    ap.add_argument("--filter_vanban", default=None, help="Substring match in van_ban (e.g. 'Bộ Tư pháp')")

    args = ap.parse_args()

    chunks = load_chunks(args.chunks)

    if not os.path.exists(args.index):
        raise FileNotFoundError(f"FAISS index not found: {args.index}")
    index = faiss.read_index(args.index)

    if args.show_debug:
        print("===== DEBUG =====")
        print("Chunks:", len(chunks))
        print("Index ntotal:", index.ntotal)
        try:
            print("Index dim (d):", index.d)
        except Exception:
            pass
        try:
            print("Metric type:", index.metric_type, "(IP=1, L2=0)")
        except Exception:
            pass
        print("=================")

    # Mapping check
    if index.ntotal != len(chunks):
        raise RuntimeError(
            f"Mismatch! index.ntotal={index.ntotal} but len(chunks)={len(chunks)}.\n"
            "=> Mapping lệch: index và chunks_clean.json không cùng thứ tự / không cùng N."
        )

    # IMPORTANT: cosine index should be IP
    if getattr(index, "metric_type", None) != faiss.METRIC_INNER_PRODUCT:
        raise RuntimeError(
            f"Index metric_type={index.metric_type} is not IP. "
            "Bạn đang không dùng cosine index. Hãy build lại bằng build_faiss_cosine.py"
        )

    encoder = SentenceTransformer(args.model, device=args.device)

    out = retrieve_cosine(
        question=args.question,
        chunks=chunks,
        index=index,
        encoder=encoder,
        topk=args.topk,
        preview_chars=args.preview_chars,
        filter_source=args.filter_source,
        filter_vanban=args.filter_vanban,
    )

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()