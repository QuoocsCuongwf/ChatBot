import os
import json
import argparse
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


def load_chunks(path: str):
    with open(path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    if not isinstance(chunks, list) or len(chunks) == 0:
        raise ValueError("chunks.json must be a non-empty list")
    texts = [c["text"] for c in chunks]
    return chunks, texts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunks", default="output_nghidinh/chunks.json")
    ap.add_argument("--model", default="Quockhanh05/Vietnam_legal_embeddings")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--out_dir", default="vector_data/legal_hf_cosine")
    ap.add_argument("--batch_size", type=int, default=32)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    chunks, texts = load_chunks(args.chunks)

    encoder = SentenceTransformer(args.model, device=args.device)

    emb = encoder.encode(
        texts,
        batch_size=args.batch_size,
        convert_to_numpy=True,
        show_progress_bar=True
    ).astype(np.float32)

    # IMPORTANT: normalize embeddings for cosine
    faiss.normalize_L2(emb)

    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)   # Inner Product + normalized => cosine

    index.add(emb)

    faiss.write_index(index, os.path.join(args.out_dir, "index.faiss"))
    np.save(os.path.join(args.out_dir, "embeddings.npy"), emb)

    print("Saved cosine index to:", args.out_dir)
    print("N =", index.ntotal, "dim =", dim)


if __name__ == "__main__":
    main()