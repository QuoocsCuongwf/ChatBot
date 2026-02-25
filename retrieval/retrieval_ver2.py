# retrieve.py
# Usage:
#   python retrieve.py --model legalhf --query "phạm vi điều chỉnh của nghị định này là gì?" --topk 5
#   python retrieve.py --model tfidf   --query "thẩm quyền của chủ tịch ubnd cấp xã?" --topk 5

import os
import json
import argparse
from typing import List, Dict, Any, Tuple

import numpy as np

# Dense retrieval deps
import faiss
from sentence_transformers import SentenceTransformer

# TF-IDF deps
import joblib
from sklearn.metrics.pairwise import linear_kernel


# =========================
# Helpers
# =========================
def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def print_topk(query: str, model_name: str, results: List[Dict[str, Any]]):
    print("=" * 90)
    print(f"MODEL : {model_name}")
    print(f"QUERY : {query}")
    print("-" * 90)
    for r in results:
        md = r.get("meta", {}) or {}
        loc = (
            f"Chương {md.get('chuong')} - Điều {md.get('dieu')} - "
            f"Khoản {md.get('khoan')} - Điểm {md.get('diem')}"
        )
        print(
            f"[{r['rank']}] score={r['score']:.6f} | {md.get('van_ban')} | "
            f"{loc} | chunk={md.get('chunk_index')}"
        )
        snippet = (r.get("text", "") or "").replace("\n", " ").strip()
        print(f"     {snippet[:220]}{'...' if len(snippet) > 220 else ''}")
    print("=" * 90)


# =========================
# Dense retriever (FAISS)
# =========================
def l2_normalize(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    n = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.clip(n, eps, None)

def dense_retrieve(
    query: str,
    topk: int,
    encoder: SentenceTransformer,
    index: faiss.Index,
    chunks: List[Dict[str, Any]],
    assume_index_is_ip_cosine: bool = True,
) -> List[Dict[str, Any]]:
    q_vec = encoder.encode([query], convert_to_numpy=True).astype("float32")
    if assume_index_is_ip_cosine:
        q_vec = l2_normalize(q_vec)

    scores, ids = index.search(q_vec, topk)
    scores = scores[0]
    ids = ids[0]

    results = []
    for rank, (idx, sc) in enumerate(zip(ids, scores), start=1):
        if idx < 0 or idx >= len(chunks):
            continue
        c = chunks[int(idx)]
        results.append({
            "rank": rank,
            "score": float(sc),
            "text": c.get("text", ""),
            "meta": c.get("metadata", {}),
        })
    return results


# =========================
# TF-IDF retriever
# =========================
def tfidf_retrieve(
    query: str,
    topk: int,
    vectorizer,
    tfidf_matrix,
    chunks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    q_vec = vectorizer.transform([query])
    sims = linear_kernel(q_vec, tfidf_matrix).ravel()

    if topk >= len(sims):
        top_idx = np.argsort(-sims)
    else:
        top_idx = np.argpartition(-sims, topk)[:topk]
        top_idx = top_idx[np.argsort(-sims[top_idx])]

    results = []
    for rank, idx in enumerate(top_idx, start=1):
        c = chunks[int(idx)]
        results.append({
            "rank": rank,
            "score": float(sims[int(idx)]),
            "text": c.get("text", ""),
            "meta": c.get("metadata", {}),
        })
    return results


# =========================
# Loaders per model
# =========================
def load_chunks(chunks_path: str) -> List[Dict[str, Any]]:
    data = load_json(chunks_path)
    if not isinstance(data, list):
        raise ValueError(f"chunks file must be a list. Got: {type(data)}")
    return data

def resolve_vec_dir(vec_root: str, model_key: str) -> str:
    """
    Map key (CLI) -> folder name trong vector_data của bạn
    (đúng theo ảnh bạn gửi)
    """
    dir_map = {
        "legalhf": "legal_hf_cosine",
        "phobert": "phobert",
        "dek21": "dek21",
        "tfidf": "tfidf",
    }
    if model_key not in dir_map:
        raise ValueError(f"Unknown model key: {model_key}. Update dir_map.")
    return os.path.join(vec_root, dir_map[model_key])

def build_dense_encoder(model_key: str, device: str) -> SentenceTransformer:
    """
    Map model keys -> model name đã dùng để encode embeddings.
    QUAN TRỌNG: phải trùng với model lúc bạn tạo embeddings.npy.
    """
    name_map = {
        "legalhf": "Quockhanh05/Vietnam_legal_embeddings",
        # Nếu bạn encode phobert bằng SentenceTransformer model khác, thay vào đây.
        # phobert-base raw (transformers) KHÔNG phải sentence-transformers chuẩn.
        # Nhưng nếu bạn đã từng dùng SentenceTransformer("vinai/phobert-base") để encode
        # thì cứ giữ. (khuyến nghị thay bằng một SBERT Vietnamese nếu có)
        "phobert": "vinai/phobert-base",
        "dek21": "dangvantuan/vietnamese-embedding",  # <-- thay đúng model bạn dùng cho dek21
    }
    if model_key not in name_map:
        raise ValueError(f"Unknown dense model key: {model_key}. Update name_map in code.")
    return SentenceTransformer(name_map[model_key], device=device)

def load_faiss_index(vec_dir: str) -> faiss.Index:
    idx_path = os.path.join(vec_dir, "index.faiss")
    if not os.path.isfile(idx_path):
        raise FileNotFoundError(f"❌ Không thấy index.faiss tại: {idx_path}")
    return faiss.read_index(idx_path)

def load_tfidf_store(vec_dir: str):
    import scipy.sparse as sp

    # ảnh bạn gửi: vectorizer.pkl
    cand_vec = [
        os.path.join(vec_dir, "vectorizer.pkl"),
        os.path.join(vec_dir, "vectorizer.joblib"),
    ]
    vec_path = next((p for p in cand_vec if os.path.isfile(p)), None)
    if vec_path is None:
        raise FileNotFoundError(f"❌ Không thấy vectorizer.pkl hoặc vectorizer.joblib trong: {vec_dir}")

    mat_path = os.path.join(vec_dir, "tfidf_matrix.npz")
    if not os.path.isfile(mat_path):
        raise FileNotFoundError(f"❌ Không thấy tfidf_matrix.npz trong: {vec_dir}")

    vectorizer = joblib.load(vec_path)
    tfidf_matrix = sp.load_npz(mat_path)
    return vectorizer, tfidf_matrix


# =========================
# Main
# =========================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=["tfidf", "phobert", "legalhf", "dek21"])
    ap.add_argument("--query", required=True, type=str)
    ap.add_argument("--topk", default=5, type=int)

    ap.add_argument("--chunks_path", default="D:\GitHub\ChatBot\output_nghidinh\chunks_clean_norm.json")
    ap.add_argument("--vec_root", default="vector_data")
    ap.add_argument("--device", default="cuda")  # or "cpu"

    # dense cosine/IP: default TRUE cho legal_hf_cosine
    ap.add_argument("--assume_ip_cosine", action="store_true",
                    help="Normalize query for IP-cosine index (recommended for legal_hf_cosine).")

    args = ap.parse_args()

    chunks = load_chunks(args.chunks_path)
    vec_dir = resolve_vec_dir(args.vec_root, args.model)

    if args.model == "tfidf":
        vectorizer, tfidf_matrix = load_tfidf_store(vec_dir)
        results = tfidf_retrieve(args.query, args.topk, vectorizer, tfidf_matrix, chunks)
        print_topk(args.query, args.model, results)
        return

    encoder = build_dense_encoder(args.model, device=args.device)
    index = load_faiss_index(vec_dir)

    # Nếu bạn dùng legal_hf_cosine thì NÊN bật normalize query.
    # Bạn có thể bật bằng flag --assume_ip_cosine
    results = dense_retrieve(
        args.query,
        args.topk,
        encoder,
        index,
        chunks,
        assume_index_is_ip_cosine=args.assume_ip_cosine,
    )
    print_topk(args.query, args.model, results)


if __name__ == "__main__":
    main()