import os, json, argparse
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_jsonl(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items

def norm_str(x):
    if x is None:
        return ""
    return str(x).strip()

def match(gt, meta, mode="dieu_khoan"):
    # mode:
    #  - "dieu": đúng van_ban + dieu
    #  - "dieu_khoan": đúng van_ban + dieu + khoan
    if norm_str(gt.get("van_ban")) != norm_str(meta.get("van_ban")):
        return False
    if norm_str(gt.get("dieu")) != norm_str(meta.get("dieu")):
        return False
    if mode == "dieu":
        return True
    return norm_str(gt.get("khoan")) == norm_str(meta.get("khoan"))

def mrr_from_ranks(ranks):
    # ranks: list of rank (1-based), 0 if not found
    s = 0.0
    for r in ranks:
        if r > 0:
            s += 1.0 / r
    return s / len(ranks) if ranks else 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunks", required=True, help="chunks_clean_norm.json (list of chunks)")
    ap.add_argument("--index", required=True, help="FAISS index.faiss")
    ap.add_argument("--gold", required=True, help="gold_200_diverse.jsonl")
    ap.add_argument("--model", required=True, help="SentenceTransformer model name/path (legal)")
    ap.add_argument("--k", type=int, default=10, help="TopK for search")
    ap.add_argument("--match_mode", choices=["dieu", "dieu_khoan"], default="dieu_khoan")
    ap.add_argument("--out", default="eval_result.json", help="output json")
    args = ap.parse_args()

    chunks = load_json(args.chunks)
    gold = load_jsonl(args.gold)

    index = faiss.read_index(args.index)
    encoder = SentenceTransformer(args.model)

    Ks = [1, 3, 5, 10]
    Ks = [x for x in Ks if x <= args.k]

    hit_at = {K: 0 for K in Ks}
    ranks = []  # rank of first correct in topK (1-based), 0 if none

    for i, g in enumerate(gold):
        q = g["question"]
        qvec = encoder.encode([q], normalize_embeddings=True).astype("float32")
        scores, idxs = index.search(qvec, args.k)
        idxs = idxs[0].tolist()

        found_rank = 0
        for r, cid in enumerate(idxs, start=1):
            meta = chunks[cid].get("metadata", {})
            if match(g, meta, mode=args.match_mode):
                found_rank = r
                break
        ranks.append(found_rank)

        for K in Ks:
            if found_rank > 0 and found_rank <= K:
                hit_at[K] += 1

    n = len(gold)
    recall = {f"Recall@{K}": hit_at[K] / n for K in Ks}
    mrr = mrr_from_ranks(ranks)

    result = {
        "N": n,
        "TopK": args.k,
        "match_mode": args.match_mode,
        **recall,
        "MRR": mrr
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("=== EVAL DONE ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Saved -> {args.out}")

if __name__ == "__main__":
    main()