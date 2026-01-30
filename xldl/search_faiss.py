import os, json, argparse
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

MODEL_MAP = {
    "legal_hf": "Quockhanh05/Vietnam_legal_embeddings",
    "dek21": "huyydangg/DEk21_hcmute_embedding",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=["legal_hf", "dek21"])
    ap.add_argument("--query", required=True)
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    args = ap.parse_args()

    vec_dir = os.path.join("vector_data", args.model)
    index = faiss.read_index(os.path.join(vec_dir, "index.faiss"))
    with open(os.path.join(vec_dir, "metadata.json"), "r", encoding="utf-8") as f:
        meta = json.load(f)

    encoder = SentenceTransformer(MODEL_MAP[args.model], device=args.device)
    q = encoder.encode([args.query], normalize_embeddings=True).astype("float32")

    D, I = index.search(q, args.topk)

    print(f"\nMODEL={args.model} | topk={args.topk}")
    print("QUERY:", args.query)
    for r, (s, idx) in enumerate(zip(D[0].tolist(), I[0].tolist()), 1):
        item = meta[int(idx)]
        md = item.get("metadata", {})
        print(f"\n#{r} score={float(s):.4f}")
        print(f"- {md.get('van_ban')} | Chương {md.get('chuong')} | Điều {md.get('dieu')} | Khoản {md.get('khoan')} | Điểm {md.get('diem')}")
        print(item.get("text","")[:240].replace("\n"," "), "...")
    print()

if __name__ == "__main__":
    main()
