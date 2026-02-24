# Deliverables — Cross-Encoder Reranker Pipeline

Generated: 2026-02-25 01:35:28

## Environment

| Item | Value |
|------|-------|
| Python | 3.11.14 |
| GPU | NVIDIA GeForce RTX 3050 Ti Laptop GPU |
| CUDA | True |

## Phase A — EDA Summary

| Dataset | Rows | Pos | Neg | Conflicts | CJK removed |
|---------|------|-----|-----|-----------|-------------|
| train | 2000 | 2000 | 0 | 0 | 0 |
| dev | 719 | 719 | 0 | 0 | 4 |
| train_neg | 2000 | 1000 | 1000 | 5 | 0 |

## Phase B — eval_qa.jsonl

- Records: 322
- CJK filtered: 4
- Easy: 322, Hard: 0

## Phase C — Training

- Base model: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Samples: 13230
- Duration: 2.8 min

## Phase D — Reranker Metrics

**Classification (dev_with_neg)**

| Metric | Value |
|--------|-------|
| accuracy | 0.8797 |
| precision | 0.8583 |
| recall | 0.9096 |
| f1 | 0.8832 |
| roc_auc | 0.9554 |
| n_samples | 1438 |

**Ranking (eval_qa)**

| Metric | Baseline | Reranked |
|--------|----------|----------|
| Recall@1 | 0.205 | 0.4161 |
| Recall@3 | 0.3447 | 0.5093 |
| Recall@5 | 0.3975 | 0.5466 |
| MRR@10 | 0.2871 | 0.4741 |

## Phase E — Pipeline Metrics

| Metric | Value |
|--------|-------|
| total_questions | 50 |
| citation_hit_rate | 0.48 |
| abstain_rate | 0.0 |
| pass_rate | 1.0 |
| refine_rate | 0.0 |
| llm_mode | placeholder |
| answer_correctness | null (human eval required) |
| avg_latency_ms | 147.2 |

## Output Files

| File | Purpose |
|------|---------|
| `outputs/eda/summary.csv` ✓ | EDA statistics table |
| `outputs/eda/summary.md` ✓ | EDA report (markdown) |
| `outputs/eda/plots/label_dist.png` ✓ | Label distribution chart |
| `outputs/eda/plots/query_len.png` ✓ | Query length histogram |
| `outputs/eda/plots/passage_len.png` ✓ | Passage length histogram |
| `outputs/eda/plots/top_vanban.png` ✓ | Top 20 van bản |
| `outputs/eda/plots/top_dieu.png` ✓ | Top 20 điều |
| `outputs/eval/eval_qa.jsonl` ✓ | Ground-truth QA set (≥80 records) |
| `outputs/eval/dev_with_neg.jsonl` ✓ | Dev set with hard negatives |
| `outputs/models/cross_encoder_v1/` ✓ | Trained cross-encoder model |
| `outputs/models/cross_encoder_v1/training_config.json` ✓ | Training hyperparameters |
| `outputs/eval/dev_classification_metrics.json` ✓ | Classification metrics (acc/prec/recall/f1/AUC) |
| `outputs/eval/rerank_metrics.csv` ✓ | Recall@K & MRR@10 baseline vs reranked |
| `outputs/tmp/faiss.index` ✓ | FAISS binary index |
| `outputs/tmp/faiss_mapping.jsonl` ✓ | faiss_id ↔ chunk_index/meta mapping |
| `outputs/eval/pipeline_results.jsonl` ✓ | Per-question pipeline results |
| `outputs/eval/pipeline_summary.csv` ✓ | Pipeline aggregate metrics |
| `outputs/eval/pipeline_summary.md` ✓ | Pipeline report (markdown) |

## Reproduction Commands

```bash
# Full pipeline (first run)
./venv/python.exe run_pipeline.py --phase ALL --seed 42

# Resume after crash
./venv/python.exe run_pipeline.py --phase ALL --resume

# Individual phases
./venv/python.exe run_pipeline.py --phase A
./venv/python.exe run_pipeline.py --phase B
./venv/python.exe run_pipeline.py --phase C --epochs 3 --batch_size 32
./venv/python.exe run_pipeline.py --phase D --topN 50
./venv/python.exe run_pipeline.py --phase E --eval_n 50
./venv/python.exe run_pipeline.py --phase F
```
