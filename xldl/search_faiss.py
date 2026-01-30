import os, json, argparse
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from encoder_phoBERT import preprocess, split_and_embed

MODEL_MAP = {
    "legal_hf": "Quockhanh05/Vietnam_legal_embeddings",
    "dek21": "huyydangg/DEk21_hcmute_embedding",
    "phobert": "vinai/phobert-base",
}

def encode_phobert(query, device="cuda"):
    """Encode query using PhoBERT model from encoder_phoBERT.py"""
    # Preprocess with word tokenization
    preprocessed_query = preprocess(query)
    
    # Get embeddings using split_and_embed from encoder_phoBERT.py
    vectors, _ = split_and_embed(preprocessed_query, max_seq_length=256, overlap=32)
    
    # Return the first vector (or average if multiple chunks)
    if len(vectors) == 1:
        vec = vectors[0]
    else:
        # If query is split into multiple chunks, average them
        vec = np.mean(vectors, axis=0)
        # Re-normalize after averaging
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
    
    return vec.astype("float32").reshape(1, -1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=["legal_hf", "dek21", "phobert"])
    ap.add_argument("--query", required=True)
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    args = ap.parse_args()

    vec_dir = os.path.join("vector_data", args.model)
    index = faiss.read_index(os.path.join(vec_dir, "index.faiss"))
    with open(os.path.join(vec_dir, "metadata.json"), "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Encode query based on model type
    if args.model == "phobert":
        q = encode_phobert(args.query, device=args.device)
    else:
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
