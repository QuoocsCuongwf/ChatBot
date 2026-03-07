"""
pipeline_utils.py — Shared utilities for run_pipeline_vX.py
"""

import json
import csv
import time
import numpy as np
import faiss
import torch
from pathlib import Path
from tqdm import tqdm


# ── Paths ──────────────────────────────────────────
ROOT     = Path(__file__).parent
DATA_DIR = ROOT / "data"
EVAL_DIR = ROOT / "outputs" / "eval"
TMP_DIR  = ROOT / "outputs" / "tmp"
MDL_DIR  = ROOT / "outputs" / "models"

TRAIN_FILE   = DATA_DIR / "train.jsonl"
DEV_FILE     = DATA_DIR / "dev.jsonl"
TRAIN_NEG    = DATA_DIR / "train_with_neg.jsonl"
EVAL_QA_FILE = EVAL_DIR / "eval_qa.jsonl"


# ── Data loading ─────────────────────────────────
def load_jsonl(path, max_rows=None):
    rows, errors = [], 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if max_rows and i >= max_rows:
                break
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                errors += 1
    if errors:
        print(f"  ⚠ {errors} malformed lines in {Path(path).name}")
    return rows


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def avg(lst):
    return round(sum(lst) / len(lst), 4) if lst else 0.0


# ── Corpus builder ────────────────────────────────
def build_corpus():
    """Thu thập tất cả unique passages từ train/dev/train_neg."""
    seen = {}
    for path in [TRAIN_FILE, DEV_FILE, TRAIN_NEG]:
        for r in load_jsonl(path):
            p = r.get("passage", "")
            if p and p not in seen:
                meta = r.get("meta", {})
                seen[p] = {
                    "passage":     p,
                    "chunk_index": meta.get("chunk_index", -1),
                    "van_ban":     meta.get("van_ban",  ""),
                    "chuong":      meta.get("chuong",   ""),
                    "dieu":        meta.get("dieu",     ""),
                    "khoan":       meta.get("khoan",    ""),
                    "diem":        meta.get("diem",     ""),
                }
    return list(seen.values())


# ── FAISS ─────────────────────────────────────────
def build_faiss(bi_model, corpus, index_path, map_path, batch_size=64, device="cuda"):
    """Encode corpus + build FAISS IndexFlatIP, lưu vào disk."""
    texts = [c["passage"] for c in corpus]
    print(f"  Encoding {len(texts)} passages ...")
    t0 = time.time()
    embeddings = bi_model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype("float32")
    print(f"  Encoded in {time.time()-t0:.1f}s | shape={embeddings.shape}")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, str(index_path))

    mapping = [{"faiss_id": i, **c} for i, c in enumerate(corpus)]
    write_jsonl(map_path, mapping)
    print(f"  FAISS → {index_path} | Mapping → {map_path}")
    return index, mapping


def load_faiss(index_path, map_path):
    """Load FAISS index + mapping từ disk."""
    index   = faiss.read_index(str(index_path))
    mapping = load_jsonl(map_path)
    print(f"  FAISS loaded: {index.ntotal} vectors | mapping: {len(mapping)} entries")
    return index, mapping


# ── Hit check ────────────────────────────────────
def is_hit(faiss_id, expected_citations, mapping):
    row = mapping[faiss_id]
    for ec in expected_citations:
        ci = ec.get("chunk_index", -2)
        if ci != -1 and row["chunk_index"] == ci:
            return True
        if (row["van_ban"] == ec.get("van_ban", "") and
                row["dieu"]    == ec.get("dieu",    "") and
                row["khoan"]   == ec.get("khoan",   "")):
            return True
    return False


# ── Core eval loop ────────────────────────────────
def evaluate(bi_model, ce_model, index, mapping,
             top_n=50, ce_batch=32, version_label="",
             save_results=None):
    """
    Chạy eval với bi_model + ce_model trên eval_qa.jsonl.
    Trả về dict metrics.

    save_results: Path | None — nếu có, lưu pipeline_results.jsonl
                  chi tiết từng query (query, rank_bi, rank_ce, top5_reranked).
    """
    eval_qa = load_jsonl(EVAL_QA_FILE)
    print(f"  Eval QA: {len(eval_qa)} questions")

    r_base   = {"R@1": [], "R@3": [], "R@5": [], "MRR@10": []}
    r_rerank = {"R@1": [], "R@3": [], "R@5": [], "MRR@10": []}
    per_query = []   # pipeline_results.jsonl

    desc = f"Eval {version_label}" if version_label else "Evaluating"
    for item in tqdm(eval_qa, desc=desc):
        query = item["query"]
        ec    = item["expected_citations"]

        # ── Retrieve ──
        q_emb = bi_model.encode(
            [query], normalize_embeddings=True, convert_to_numpy=True
        ).astype("float32")
        _, ids = index.search(q_emb, top_n)
        ids    = ids[0].tolist()

        # ── Baseline metrics ──
        for k, key in [(1, "R@1"), (3, "R@3"), (5, "R@5")]:
            r_base[key].append(
                1 if any(is_hit(i, ec, mapping) for i in ids[:k] if i >= 0) else 0
            )
        mrr_base = 0.0
        for rank, i in enumerate(ids[:10], 1):
            if i >= 0 and is_hit(i, ec, mapping):
                mrr_base = 1.0 / rank
                break
        r_base["MRR@10"].append(mrr_base)

        # rank_bi: vị trí passage đúng trong bi-encoder output (1-based, -1 nếu miss)
        rank_bi = -1
        for rank, i in enumerate(ids, 1):
            if i >= 0 and is_hit(i, ec, mapping):
                rank_bi = rank
                break

        # ── Rerank ──
        if ce_model is not None:
            cands     = [(mapping[i]["passage"], i) for i in ids if i >= 0]
            rscores   = ce_model.predict(
                [[query, c[0]] for c in cands], batch_size=ce_batch
            ) if cands else []
            ranked    = sorted(zip(rscores, [c[1] for c in cands]), reverse=True)
            r_ids     = [r[1] for r in ranked]
            score_map = {c[1]: float(s) for s, c in zip(rscores, cands)}
        else:
            r_ids     = ids
            score_map = {}

        for k, key in [(1, "R@1"), (3, "R@3"), (5, "R@5")]:
            r_rerank[key].append(
                1 if any(is_hit(i, ec, mapping) for i in r_ids[:k]) else 0
            )
        mrr_ce  = 0.0
        rank_ce = -1
        for rank, i in enumerate(r_ids[:10], 1):
            if is_hit(i, ec, mapping):
                mrr_ce  = 1.0 / rank
                rank_ce = rank
                break
        r_rerank["MRR@10"].append(mrr_ce)

        # ── Chi tiết từng query ──
        if save_results is not None:
            top5 = []
            for rank, fid in enumerate(r_ids[:5], 1):
                if fid < 0 or fid >= len(mapping):
                    continue
                m = mapping[fid]
                top5.append({
                    "rank":        rank,
                    "hit":         is_hit(fid, ec, mapping),
                    "ce_score":    round(score_map.get(fid, 0.0), 4),
                    "van_ban":     m.get("van_ban", ""),
                    "dieu":        m.get("dieu", ""),
                    "khoan":       m.get("khoan", ""),
                    "chunk_index": m.get("chunk_index", -1),
                    "passage":     m.get("passage", "")[:300],
                })
            per_query.append({
                "id":                 item.get("id", ""),
                "query":              query,
                "expected_citations": ec,
                "rank_bi":            rank_bi,
                "rank_ce":            rank_ce,
                "hit@1":              int(r_rerank["R@1"][-1]),
                "hit@3":              int(r_rerank["R@3"][-1]),
                "hit@5":              int(r_rerank["R@5"][-1]),
                "mrr":                round(mrr_ce, 4),
                "top5_reranked":      top5,
            })

    if save_results is not None and per_query:
        write_jsonl(save_results, per_query)
        print(f"  Pipeline results → {save_results} ({len(per_query)} rows) ✓")

    return {
        "baseline": {m: avg(r_base[k])   for k, m in [("R@1","Recall@1"),("R@3","Recall@3"),("R@5","Recall@5"),("MRR@10","MRR@10")]},
        "reranked": {m: avg(r_rerank[k]) for k, m in [("R@1","Recall@1"),("R@3","Recall@3"),("R@5","Recall@5"),("MRR@10","MRR@10")]},
    }


# ── Print + save results ──────────────────────────
def print_results(results, version_label=""):
    b = results["baseline"]
    r = results["reranked"]
    print(f"\n── {version_label} Results ──")
    print(f"  {'Metric':<12} {'Baseline':>10} {'Reranked':>10} {'Δ':>8}")
    print("  " + "-" * 44)
    for metric in ["Recall@1", "Recall@3", "Recall@5", "MRR@10"]:
        bv = b[metric]
        rv = r[metric]
        d  = rv - bv
        print(f"  {metric:<12} {bv:>10.4f} {rv:>10.4f} {d:>+8.4f}")


def save_csv(results, out_path, extra_cols=None):
    """Lưu results ra CSV."""
    rows = []
    for metric in ["Recall@1", "Recall@3", "Recall@5", "MRR@10"]:
        row = {
            "metric":   metric,
            "baseline": results["baseline"][metric],
            "reranked": results["reranked"][metric],
        }
        if extra_cols:
            row.update(extra_cols)
        rows.append(row)
    fields = list(rows[0].keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"  Saved → {out_path} ✓")
