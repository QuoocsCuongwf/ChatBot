"""
run_pipeline_v5.py — V5: Fine-tuned Bi-Encoder + Hard Negative CE Rerank

Pipeline:
    legal_hf_finetuned → FAISS top-50
        → cross_encoder_v5fix (medium-hard neg training) Rerank

Tương ứng: baseline_v5_hard_neg_ce.ipynb

Usage:
    ./venv/python.exe run_pipeline_v5.py
    ./venv/python.exe run_pipeline_v5.py --rebuild_index
"""

import argparse
import torch
from sentence_transformers import SentenceTransformer, CrossEncoder

from pipeline_utils import (
    EVAL_DIR, TMP_DIR, MDL_DIR,
    build_corpus, build_faiss, load_faiss,
    evaluate, print_results, save_csv,
)

# ── V5 Config ─────────────────────────────────────
VERSION       = "v5"
FT_BI_PATH    = MDL_DIR / "legal_hf_finetuned" / "final"
CE_MODEL_PATH = MDL_DIR / "cross_encoder_v5fix" / "saved_model"
if not CE_MODEL_PATH.exists():
    CE_MODEL_PATH = MDL_DIR / "cross_encoder_v5fix"

FAISS_INDEX   = TMP_DIR  / "faiss_v4.index"
FAISS_MAP     = TMP_DIR  / "faiss_mapping_v4.jsonl"
RERANK_CSV    = EVAL_DIR / f"rerank_metrics_{VERSION}.csv"


def main():
    parser = argparse.ArgumentParser(description=f"Run Pipeline {VERSION.upper()}")
    parser.add_argument("--rebuild_index", action="store_true")
    parser.add_argument("--top_n",   type=int, default=50)
    parser.add_argument("--ce_batch",type=int, default=32)
    args = parser.parse_args()

    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n{'='*60}")
    print(f"  Run Pipeline {VERSION.upper()}")
    print(f"  Bi-encoder : {FT_BI_PATH}  (fine-tuned)")
    print(f"  CE         : {CE_MODEL_PATH}  (medium-hard neg, cross_encoder_v5fix)")
    print(f"  Device     : {DEVICE}")
    print(f"{'='*60}\n")

    print("Loading fine-tuned bi-encoder ...")
    bi_model = SentenceTransformer(str(FT_BI_PATH), device=DEVICE)
    print(f"  dim={bi_model.get_sentence_embedding_dimension()} ✓")

    if FAISS_INDEX.exists() and FAISS_MAP.exists() and not args.rebuild_index:
        index, mapping = load_faiss(FAISS_INDEX, FAISS_MAP)
    else:
        corpus = build_corpus()
        index, mapping = build_faiss(bi_model, corpus, FAISS_INDEX, FAISS_MAP,
                                     device=DEVICE)

    print(f"\nLoading CE (medium-hard neg): {CE_MODEL_PATH}")
    ce_model = CrossEncoder(str(CE_MODEL_PATH), max_length=256, device=DEVICE, local_files_only=True)
    print("  Cross-encoder ready ✓")

    print("\nEvaluating ...")
    results = evaluate(bi_model, ce_model, index, mapping,
                       top_n=args.top_n, ce_batch=args.ce_batch,
                       version_label=VERSION.upper())

    print_results(results, version_label=VERSION.upper())
    save_csv(results, RERANK_CSV,
             extra_cols={"bi_encoder": str(FT_BI_PATH), "ce": str(CE_MODEL_PATH)})


if __name__ == "__main__":
    main()

