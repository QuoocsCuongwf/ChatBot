"""
debug_top5_retrieve.py — In Top-5 retrieval results để debug pipeline

Chạy:
    python debug_top5_retrieve.py
    python debug_top5_retrieve.py --num_queries 10
    python debug_top5_retrieve.py --query "Kinh phí thực hiện nhiệm vụ chuyển giao do ai đảm bảo?"
"""

import json
import sys
import time
import argparse
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent
FAISS_INDEX_DIR = PROJECT_ROOT / "vector_data" / "legal_hf_cosine"
FAISS_INDEX_FILE = FAISS_INDEX_DIR / "index.faiss"
FAISS_METADATA_FILE = FAISS_INDEX_DIR / "metadata.json"
BI_ENCODER_MODEL = "Quockhanh05/Vietnam_legal_embeddings"
CE_MODEL_DIR = PROJECT_ROOT / "cross-encoder" / "outputs" / "models" / "cross_encoder_faiss_matched" / "saved_model"
DEV_FILE = PROJECT_ROOT / "cross-encoder" / "data" / "dev.jsonl"

TOP_K_RETRIEVE = 50   # FAISS top-k
TOP_K_DISPLAY = 5     # Hiển thị top-5


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--query", type=str, default=None, help="Single query to test")
    p.add_argument("--num_queries", type=int, default=5, help="Number of dev queries to test")
    p.add_argument("--top_k", type=int, default=5, help="Top-K to display")
    p.add_argument("--no_ce", action="store_true", help="Skip cross-encoder reranking")
    p.add_argument("--device", type=str, default="cuda", help="Device (cuda/cpu)")
    return p.parse_args()


def load_dev_queries(path, num=5):
    """Load unique positive queries from dev.jsonl with expected info."""
    queries = []
    seen = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if data.get("label") != 1:
                continue
            q = data["query"]
            if q in seen:
                continue
            seen.add(q)
            queries.append({
                "query": q,
                "expected_passage": data.get("passage", "")[:200],
                "expected_meta": data.get("meta", {}),
            })
            if len(queries) >= num:
                break
    return queries


def main():
    args = parse_args()
    top_k_display = args.top_k

    # ─── Step 1: Load FAISS ───
    print("=" * 70)
    print("  DEBUG TOP-5 RETRIEVAL")
    print("=" * 70)

    import faiss
    import numpy as np

    print(f"\n[1/4] Loading FAISS index from {FAISS_INDEX_FILE}...")
    t0 = time.time()
    if not FAISS_INDEX_FILE.exists():
        print(f"  ❌ FAISS index NOT FOUND: {FAISS_INDEX_FILE}")
        return
    index = faiss.read_index(str(FAISS_INDEX_FILE))
    print(f"  ✓ {index.ntotal} vectors loaded ({time.time()-t0:.1f}s)")

    # ─── Step 2: Load Metadata ───
    print(f"\n[2/4] Loading metadata from {FAISS_METADATA_FILE}...")
    t0 = time.time()
    if not FAISS_METADATA_FILE.exists():
        print(f"  ❌ Metadata NOT FOUND: {FAISS_METADATA_FILE}")
        return
    with open(FAISS_METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    print(f"  ✓ {len(metadata)} entries loaded ({time.time()-t0:.1f}s)")

    # Sanity check
    if index.ntotal != len(metadata):
        print(f"  ⚠ MISMATCH: FAISS has {index.ntotal} vectors but metadata has {len(metadata)} entries!")

    # ─── Step 3: Load Bi-encoder ───
    print(f"\n[3/4] Loading bi-encoder: {BI_ENCODER_MODEL}...")
    t0 = time.time()
    from sentence_transformers import SentenceTransformer
    bi_encoder = SentenceTransformer(BI_ENCODER_MODEL, device=args.device)
    print(f"  ✓ Loaded ({time.time()-t0:.1f}s)")

    # ─── Step 4: Load Cross-encoder (optional) ───
    ce_model = None
    if not args.no_ce:
        print(f"\n[4/4] Loading cross-encoder: {CE_MODEL_DIR}...")
        t0 = time.time()
        if CE_MODEL_DIR.exists():
            from sentence_transformers import CrossEncoder
            ce_model = CrossEncoder(str(CE_MODEL_DIR), max_length=256, device=args.device)
            print(f"  ✓ Loaded ({time.time()-t0:.1f}s)")
        else:
            print(f"  ⚠ Cross-encoder NOT FOUND at {CE_MODEL_DIR} — will use FAISS scores only")
    else:
        print(f"\n[4/4] Cross-encoder SKIPPED (--no_ce)")

    # ─── Prepare queries ───
    if args.query:
        queries = [{"query": args.query, "expected_passage": "(custom query)", "expected_meta": {}}]
    else:
        if not DEV_FILE.exists():
            print(f"\n❌ Dev file not found: {DEV_FILE}")
            return
        queries = load_dev_queries(DEV_FILE, num=args.num_queries)
        print(f"\n  Loaded {len(queries)} queries from dev.jsonl")

    # ═══════════════════════════════════════════════════════════════════════════
    # RUN RETRIEVAL
    # ═══════════════════════════════════════════════════════════════════════════

    total_hit_at_1 = 0
    total_hit_at_5 = 0
    total_hit_faiss_at_5 = 0

    for qi, qdata in enumerate(queries):
        query = qdata["query"]
        expected_meta = qdata["expected_meta"]
        expected_chunk_idx = expected_meta.get("chunk_index")

        print("\n" + "═" * 70)
        print(f"  QUERY {qi+1}/{len(queries)}")
        print("═" * 70)
        print(f"  Q: {query}")
        print(f"  Expected: {expected_meta.get('van_ban', '?')[:60]} | "
              f"Chương {expected_meta.get('chuong', '?')} | "
              f"Điều {expected_meta.get('dieu', '?')} | "
              f"Khoản {expected_meta.get('khoan', '?')} | "
              f"chunk_index={expected_chunk_idx}")
        print(f"  Expected passage: {qdata['expected_passage'][:120]}...")

        # ─── FAISS Search ───
        t0 = time.time()
        q_emb = bi_encoder.encode(
            [query], normalize_embeddings=True, convert_to_numpy=True
        ).astype("float32")
        faiss_time = time.time() - t0

        t0 = time.time()
        scores_faiss, ids = index.search(q_emb, TOP_K_RETRIEVE)
        search_time = time.time() - t0

        scores_faiss = scores_faiss[0].tolist()
        ids_list = [i for i in ids[0].tolist() if 0 <= i < len(metadata)]

        # Build candidates
        candidates = []
        seen_texts = set()
        for i, faiss_id in enumerate(ids_list):
            m = metadata[faiss_id]
            text = m.get("text", "")
            text_hash = hash(text[:200])
            if text_hash in seen_texts:
                continue
            seen_texts.add(text_hash)

            meta = m.get("metadata", {})
            # chunk_index = faiss_id (vị trí trong metadata array)
            candidates.append({
                "faiss_id": faiss_id,
                "text": text,
                "score_faiss": scores_faiss[i] if i < len(scores_faiss) else 0.0,
                "score_rerank": 0.0,
                "van_ban": meta.get("van_ban", ""),
                "chuong": meta.get("chuong"),
                "dieu": meta.get("dieu"),
                "khoan": meta.get("khoan"),
                "diem": meta.get("diem"),
                "chunk_index": faiss_id,  # chunk_index chính là vị trí trong FAISS
                "source_file": meta.get("source_file", ""),
            })

        # Check FAISS-only hit@5
        faiss_hit = False
        for c in candidates[:top_k_display]:
            if expected_chunk_idx is not None and c["chunk_index"] == expected_chunk_idx:
                faiss_hit = True
                break
        if faiss_hit:
            total_hit_faiss_at_5 += 1

        # ─── Cross-encoder Rerank ───
        if ce_model and candidates:
            t0 = time.time()
            pairs = [[query, c["text"]] for c in candidates]
            rerank_scores = ce_model.predict(pairs, batch_size=32)
            rerank_time = time.time() - t0
            for i, score in enumerate(rerank_scores):
                candidates[i]["score_rerank"] = float(score)
            candidates.sort(key=lambda x: x["score_rerank"], reverse=True)
        else:
            rerank_time = 0
            for c in candidates:
                c["score_rerank"] = c["score_faiss"]

        # ─── Print Top-5 ───
        print(f"\n  ┌─ TOP-{top_k_display} RESULTS (encode={faiss_time*1000:.0f}ms, "
              f"search={search_time*1000:.0f}ms, rerank={rerank_time*1000:.0f}ms) ─┐")

        hit_at_1 = False
        hit_at_5 = False

        for rank, c in enumerate(candidates[:top_k_display]):
            is_match = (expected_chunk_idx is not None and c["chunk_index"] == expected_chunk_idx)
            match_label = " ✅ HIT" if is_match else ""

            if is_match and rank == 0:
                hit_at_1 = True
            if is_match:
                hit_at_5 = True

            print(f"  │")
            print(f"  │ #{rank+1}  FAISS={c['score_faiss']:.4f}  "
                  f"Rerank={c['score_rerank']:.4f}  "
                  f"chunk_idx={c['chunk_index']}{match_label}")
            print(f"  │    Văn bản: {c['van_ban'][:70]}")
            print(f"  │    Ch.{c['chuong'] or '?'} | Đ.{c['dieu'] or '?'} | "
                  f"K.{c['khoan'] or '?'} | Đ.{c['diem'] or '?'}")
            print(f"  │    Text: {c['text'][:150]}...")

        print(f"  │")

        if hit_at_1:
            total_hit_at_1 += 1
        if hit_at_5:
            total_hit_at_5 += 1

        # Show where expected is if not in top-5
        if not hit_at_5 and expected_chunk_idx is not None:
            found_rank = None
            for rank, c in enumerate(candidates):
                if c["chunk_index"] == expected_chunk_idx:
                    found_rank = rank + 1
                    break
            if found_rank:
                c = candidates[found_rank - 1]
                print(f"  │ ⚠ Expected chunk found at RANK #{found_rank} "
                      f"(FAISS={c['score_faiss']:.4f}, Rerank={c['score_rerank']:.4f})")
            else:
                print(f"  │ ❌ Expected chunk_index={expected_chunk_idx} NOT FOUND in top-{TOP_K_RETRIEVE}!")

        print(f"  └{'─' * 65}┘")

    # ═══════════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════════════════

    n = len(queries)
    print("\n" + "═" * 70)
    print("  SUMMARY")
    print("═" * 70)
    print(f"  Queries tested:      {n}")
    print(f"  FAISS-only Hit@{top_k_display}:   {total_hit_faiss_at_5}/{n} = {total_hit_faiss_at_5/n:.1%}")
    if ce_model:
        print(f"  +Rerank Hit@1:       {total_hit_at_1}/{n} = {total_hit_at_1/n:.1%}")
        print(f"  +Rerank Hit@{top_k_display}:      {total_hit_at_5}/{n} = {total_hit_at_5/n:.1%}")
    else:
        print(f"  Hit@1 (no rerank):   {total_hit_at_1}/{n} = {total_hit_at_1/n:.1%}")
        print(f"  Hit@{top_k_display} (no rerank):  {total_hit_at_5}/{n} = {total_hit_at_5/n:.1%}")
    print("═" * 70)


if __name__ == "__main__":
    main()
