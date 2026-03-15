"""
run_pipeline_v3.py — V3: Vietnam_legal_HF Bi-Encoder (off-the-shelf) + ms-marco CE Rerank

Pipeline:
    Quockhanh05/Vietnam_legal_embeddings (domain-specific, chưa fine-tune) → FAISS top-50
        → cross_encoder_v1 (ms-marco-MiniLM fine-tuned) Rerank

Tương ứng: baseline_v3_legal_hf.ipynb

Usage:
    ./venv/python.exe run_pipeline_v3.py
    ./venv/python.exe run_pipeline_v3.py --rebuild_index
"""

import argparse
import torch
from sentence_transformers import SentenceTransformer, CrossEncoder

from pipeline_utils import (
    EVAL_DIR, TMP_DIR, MDL_DIR,
    build_corpus, build_faiss, load_faiss,
    evaluate, print_results, save_csv,
)

# ── V3 Config ─────────────────────────────────────
VERSION       = "v3"
BI_MODEL_NAME = "Quockhanh05/Vietnam_legal_embeddings"   # off-the-shelf, chưa fine-tune
CE_MODEL_PATH = MDL_DIR / "cross_encoder_v1" / "saved_model"
if not CE_MODEL_PATH.exists():
    CE_MODEL_PATH = MDL_DIR / "cross_encoder_v1"

FAISS_INDEX   = TMP_DIR  / "faiss_v3_legal_hf.index"    # index riêng cho V3
FAISS_MAP     = TMP_DIR  / "faiss_mapping_v3_legal_hf.jsonl"
RERANK_CSV    = EVAL_DIR / f"rerank_metrics_{VERSION}.csv"


def main():
    parser = argparse.ArgumentParser(description=f"Run Pipeline {VERSION.upper()}")
    parser.add_argument("--rebuild_index", action="store_true",
                        help="Force rebuild FAISS index với fine-tuned bi-encoder")
    parser.add_argument("--top_n",   type=int, default=50)
    parser.add_argument("--ce_batch",type=int, default=32)
    args = parser.parse_args()

    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n{'='*60}")
    print(f"  Run Pipeline {VERSION.upper()}")
    print(f"  Bi-encoder : {BI_MODEL_NAME}  (off-the-shelf)")
    print(f"  CE         : {CE_MODEL_PATH}  (ms-marco)")
    print(f"  Device     : {DEVICE}")
    print(f"{'='*60}\n")

    # ── Load Vietnam_legal_HF (off-the-shelf) ──
    print(f"Loading bi-encoder: {BI_MODEL_NAME}")
    bi_model = SentenceTransformer(BI_MODEL_NAME, device=DEVICE)
    print(f"  dim={bi_model.get_sentence_embedding_dimension()} ✓")

    # ── FAISS index ──
    if FAISS_INDEX.exists() and FAISS_MAP.exists() and not args.rebuild_index:
        print("Loading existing FAISS index (Vietnam_legal_HF) ...")
        index, mapping = load_faiss(FAISS_INDEX, FAISS_MAP)
    else:
        print("Building FAISS index with Vietnam_legal_HF ...")
        corpus = build_corpus()
        index, mapping = build_faiss(bi_model, corpus, FAISS_INDEX, FAISS_MAP,
                                     device=DEVICE)

    # ── Load Cross-Encoder ──
    print(f"\nLoading cross-encoder: {CE_MODEL_PATH}")
    ce_model = CrossEncoder(str(CE_MODEL_PATH), max_length=256, device=DEVICE, local_files_only=True)
    print("  Cross-encoder ready ✓")

    # ── Evaluate ──
    print("\nEvaluating ...")
    results = evaluate(bi_model, ce_model, index, mapping,
                       top_n=args.top_n, ce_batch=args.ce_batch,
                       version_label=VERSION.upper())

    print_results(results, version_label=VERSION.upper())
    save_csv(results, RERANK_CSV,
             extra_cols={"bi_encoder": BI_MODEL_NAME, "ce": str(CE_MODEL_PATH)})


if __name__ == "__main__":
    main()

