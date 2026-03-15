"""
run_pipeline_v2.py — V2: PhoBERT Bi-Encoder + ms-marco CE Rerank

Pipeline:
    vinai/phobert-base (custom mean pooling) → FAISS top-50
        → cross_encoder_v1 (ms-marco-MiniLM fine-tuned) Rerank

Tương ứng: baseline_v2_phobert.ipynb

Usage:
    ./venv/python.exe run_pipeline_v2.py
    ./venv/python.exe run_pipeline_v2.py --rebuild_index
"""

import argparse
import numpy as np
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import CrossEncoder

from pipeline_utils import (
    EVAL_DIR, TMP_DIR, MDL_DIR,
    build_corpus, build_faiss, load_faiss,
    evaluate, print_results, save_csv,
)

# ── V2 Config ─────────────────────────────────────
VERSION       = "v2"
BI_MODEL_NAME = "vinai/phobert-base"
CE_MODEL_PATH = MDL_DIR / "cross_encoder_v1" / "saved_model"
if not CE_MODEL_PATH.exists():
    CE_MODEL_PATH = MDL_DIR / "cross_encoder_v1"

FAISS_INDEX   = TMP_DIR  / "faiss_v2_phobert.index"
FAISS_MAP     = TMP_DIR  / "faiss_mapping_v2_phobert.jsonl"
RERANK_CSV    = EVAL_DIR / f"rerank_metrics_{VERSION}.csv"
MAX_LENGTH    = 256


# ── Custom PhoBERT Encoder ────────────────────────
class PhoBERTEncoder:
    """
    Bi-Encoder wrapper cho vinai/phobert-base.
    Mean pooling bỏ <s> (pos=0) và </s> (pos=-1).
    Interface tương thích SentenceTransformer.encode().
    """

    def __init__(self, model_name: str = "vinai/phobert-base", device: str = "cpu"):
        print(f"  Loading tokenizer: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
        print("  Loading model ...")
        self.model = AutoModel.from_pretrained(model_name).to(device)
        self.model.eval()
        self.device = device
        self.dim    = self.model.config.hidden_size
        print(f"  Ready | device={device} | hidden_size={self.dim}")

    @torch.no_grad()
    def _encode_batch(self, texts: list) -> np.ndarray:
        enc = self.tokenizer(
            texts, padding=True, truncation=True,
            max_length=MAX_LENGTH, return_tensors="pt"
        )
        ids  = enc["input_ids"].to(self.device)
        mask = enc["attention_mask"].to(self.device)
        last_h = self.model(input_ids=ids, attention_mask=mask).last_hidden_state

        # Mean pooling: bỏ <s> (pos 0) và </s> (pos -1)
        content_h   = last_h[:, 1:-1, :]
        content_m   = mask[:, 1:-1].unsqueeze(-1).float()
        mean_pooled = (content_h * content_m).sum(1) / content_m.sum(1).clamp(min=1e-9)
        return mean_pooled.cpu().numpy().astype(np.float32)

    def encode(self, texts, batch_size: int = 32,
               show_progress_bar: bool = False,
               normalize_embeddings: bool = True,
               convert_to_numpy: bool = True,
               **kwargs) -> np.ndarray:
        all_vecs = []
        it = range(0, len(texts), batch_size)
        if show_progress_bar:
            it = tqdm(it, desc="PhoBERT encode")
        for start in it:
            all_vecs.append(self._encode_batch(texts[start: start + batch_size]))
        result = np.vstack(all_vecs)
        if normalize_embeddings:
            result /= np.maximum(np.linalg.norm(result, axis=1, keepdims=True), 1e-9)
        return result

    def get_sentence_embedding_dimension(self):
        return self.dim


def main():
    parser = argparse.ArgumentParser(description=f"Run Pipeline {VERSION.upper()}")
    parser.add_argument("--rebuild_index", action="store_true")
    parser.add_argument("--top_n",   type=int, default=50)
    parser.add_argument("--ce_batch",type=int, default=32)
    args = parser.parse_args()

    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n{'='*60}")
    print(f"  Run Pipeline {VERSION.upper()}")
    print(f"  Bi-encoder : {BI_MODEL_NAME}  (PhoBERT custom mean pooling)")
    print(f"  CE         : {CE_MODEL_PATH}")
    print(f"  Device     : {DEVICE}")
    print(f"{'='*60}\n")

    print("Loading PhoBERT bi-encoder ...")
    bi_model = PhoBERTEncoder(BI_MODEL_NAME, device=DEVICE)

    if FAISS_INDEX.exists() and FAISS_MAP.exists() and not args.rebuild_index:
        index, mapping = load_faiss(FAISS_INDEX, FAISS_MAP)
    else:
        print("Building FAISS index with PhoBERT ...")
        corpus = build_corpus()
        index, mapping = build_faiss(bi_model, corpus, FAISS_INDEX, FAISS_MAP,
                                     batch_size=32, device=DEVICE)

    print(f"\nLoading cross-encoder: {CE_MODEL_PATH}")
    ce_model = CrossEncoder(str(CE_MODEL_PATH), max_length=MAX_LENGTH, device=DEVICE, local_files_only=True)
    print("  Cross-encoder ready ✓")

    print("\nEvaluating ...")
    results = evaluate(bi_model, ce_model, index, mapping,
                       top_n=args.top_n, ce_batch=args.ce_batch,
                       version_label=VERSION.upper())

    print_results(results, version_label=VERSION.upper())
    save_csv(results, RERANK_CSV,
             extra_cols={"bi_encoder": BI_MODEL_NAME, "ce": str(CE_MODEL_PATH)})


if __name__ == "__main__":
    main()

