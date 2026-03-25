import torch
import time
from sentence_transformers import SentenceTransformer, CrossEncoder
from pathlib import Path

def test_gpu():
    print(f"CUDA available: {torch.cuda.is_available()}")
    if not torch.cuda.is_available():
        return

    device = "cuda"
    bi_model_name = "BAAI/bge-m3"
    ce_model_name = "BAAI/bge-reranker-v2-m3"

    print(f"Loading Bi-encoder to {device}...")
    t0 = time.time()
    bi_model = SentenceTransformer(bi_model_name, device=device)
    print(f"Loaded in {time.time() - t0:.2f}s")

    print(f"Loading Cross-encoder to {device}...")
    t0 = time.time()
    ce_model = CrossEncoder(ce_model_name, device=device)
    print(f"Loaded in {time.time() - t0:.2f}s")

    query = "Hà Nội là gì?"
    passages = ["Hà Nội là thủ đô của Việt Nam."] * 100

    print(f"Encoding 100 passages with Bi-encoder on {device}...")
    t0 = time.time()
    embs = bi_model.encode(passages, batch_size=32)
    print(f"Encoded 100 passages in {time.time() - t0:.2f}s")

    print(f"Reranking 100 pairs with Cross-encoder on {device}...")
    pairs = [[query, p] for p in passages]
    t0 = time.time()
    scores = ce_model.predict(pairs, batch_size=32)
    print(f"Reranked 100 pairs in {time.time() - t0:.2f}s")

    # Test CPU for comparison
    device = "cpu"
    print(f"\nLoading Bi-encoder to {device}...")
    bi_model_cpu = SentenceTransformer(bi_model_name, device=device)
    print(f"Loading Cross-encoder to {device}...")
    ce_model_cpu = CrossEncoder(ce_model_name, device=device)

    print(f"Reranking 100 pairs with Cross-encoder on {device}...")
    t0 = time.time()
    scores = ce_model_cpu.predict(pairs, batch_size=32)
    print(f"Reranked 100 pairs on CPU in {time.time() - t0:.2f}s")

if __name__ == "__main__":
    test_gpu()
