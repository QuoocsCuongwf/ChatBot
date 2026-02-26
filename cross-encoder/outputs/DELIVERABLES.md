# Deliverables — Cross-Encoder Reranker Pipeline

Generated: 2026-02-26 03:16:06

## Environment
- Python: 3.11.14  
- GPU: NVIDIA GeForce RTX 3050 Ti Laptop GPU

## Phase D — Classification Metrics

| Metric | Value |
|--------|-------|
| accuracy | 0.8797 |
| precision | 0.8447 |
| recall | 0.9305 |
| f1 | 0.8855 |
| roc_auc | 0.9564 |
| n_samples | 1438 |

## Phase D — Ranking Metrics

| Metric | Baseline | Reranked |
|--------|----------|----------|
| Recall@1 | 0.2074 | 0.4458 |
| Recall@3 | 0.3529 | 0.5511 |
| Recall@5 | 0.4087 | 0.5789 |
| MRR@10 | 0.2908 | 0.5036 |

## Phase E — Pipeline Metrics

| Metric | Value |
|--------|-------|
| total_questions | 50 |
| citation_hit_rate | 0.64 |
| abstain_rate | 0.02 |
| pass_rate | 0.98 |
| avg_latency_ms | 340.8 |

## Reproduction

```bash
# Chạy notebook: run_pipeline.ipynb (Run All)
# Hoặc script:   ./venv/python.exe run_pipeline.py --phase ALL --seed 42
```
