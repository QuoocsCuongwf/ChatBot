# retrieve.py
import os, json, argparse
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def load_chunks(chunks_path: str):
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    # hỗ trợ cả dạng {"chunks":[...]}
    if isinstance(chunks, dict) and "chunks" in chunks:
        chunks = chunks["chunks"]
    return chunks

def safe_meta(m: dict, key: str, default=""):
    if not isinstance(m, dict):
        return default
    return m.get(key, default)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", "-q", required=True, help="Câu hỏi truy vấn")
    # thêm args
    ap.add_argument("--topn", type=int, default=300, help="Search rộng trước khi lọc")
    ap.add_argument("--filter_kw", default="", help='Ví dụ: "tư pháp" hoặc "Bộ Tư pháp"')
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--chunks_path", default="output_nghidinh/chunks_clean.json")
    ap.add_argument("--index_path", default="vector_data/legal_hf_cosine/index.faiss")
    ap.add_argument("--model_name", default="Quockhanh05/Vietnam_legal_embeddings")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--save_json", default="", help="Nếu muốn lưu output ra file json")
    args = ap.parse_args()

    # 1) Load chunks + index
    chunks = load_chunks(args.chunks_path)
    index = faiss.read_index(args.index_path)

    # 2) Load encoder (same model khi build embeddings)
    encoder = SentenceTransformer(args.model_name, device=args.device)

    # 3) Encode query (normalize để IP = cosine)
    q_emb = encoder.encode([args.question], normalize_embeddings=True)
    q_emb = np.asarray(q_emb, dtype="float32")

    # 4) Search
    # 4) Search rộng
    scores, ids = index.search(q_emb, args.topn)
    scores, ids = scores[0].tolist(), ids[0].tolist()

    kw = args.filter_kw.strip().lower()

    candidates = []
    for idx, score in zip(ids, scores):
        if idx < 0 or idx >= len(chunks):
            continue
        ch = chunks[idx]
        meta = ch.get("metadata", {})
        vb = str(meta.get("van_ban","")).lower()
        tx = str(ch.get("text","")).lower()

        if kw:
            if (kw not in vb) and (kw not in tx):
                continue

        candidates.append((idx, float(score)))

    # lấy topk sau lọc
    candidates = sorted(candidates, key=lambda x: x[1], reverse=True)[:args.topk]
    results = []
    for rank, (idx, score) in enumerate(zip(ids, scores), start=1):
        if idx < 0 or idx >= len(chunks):
            continue
        ch = chunks[idx]
        meta = ch.get("metadata", {})
        results.append({
            "rank": rank,
            "score": float(score),
            "text": ch.get("text", ""),
            "metadata": {
                "van_ban": safe_meta(meta, "van_ban"),
                "chuong": safe_meta(meta, "chuong"),
                "dieu": safe_meta(meta, "dieu"),
                "khoan": safe_meta(meta, "khoan"),
                "nguon": safe_meta(meta, "nguon"),
                "chunk_id": idx
            }
        })

    out = {
        "question": args.question,
        "topk": args.topk,
        "results": results
    }

    # 5) Print đẹp cho giảng viên xem
    print("=" * 90)
    print("QUESTION:", args.question)
    print("=" * 90)
    for r in results:
        md = r["metadata"]
        print(f"[{r['rank']}] score={r['score']:.4f} | {md['van_ban']} | Chương {md['chuong']} | Điều {md['dieu']} | Khoản {md['khoan']} | chunk_id={md['chunk_id']}")
        preview = r["text"].replace("\n", " ")
        print("    ", preview[:260] + ("..." if len(preview) > 260 else ""))
        print("-" * 90)

    # 6) Optional save
    if args.save_json:
        os.makedirs(os.path.dirname(args.save_json) or ".", exist_ok=True)
        with open(args.save_json, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print("✅ Saved:", args.save_json)

if __name__ == "__main__":
    main()