# Retrieval Evaluation Pipeline

Pipeline đánh giá và so sánh hiệu suất retrieval cho Vietnamese Legal Documents.

## 🎯 Tính năng

- **Multi-model evaluation**: So sánh nhiều model cùng lúc (TF-IDF, Legal HF, PhoBERT, Vietnamese Embedding)
- **Reranking**: Cross-encoder reranking với nhiều model (BGE, MiniLM, etc.)
- **Metrics đầy đủ**: Recall@K, MRR, Hit@K
- **Export Excel**: Kết quả xuất ra Excel với formatting đẹp
- **Visualization**: Biểu đồ so sánh các model

## 📁 Cấu trúc files

```
retrieval/
├── eval_all_models.py     # Script đánh giá chính
├── rerankers.py           # Các reranker models
├── run_eval.py            # Script chạy nhanh
├── compare_results.py     # So sánh và phân tích kết quả
├── gold_200_diverse.jsonl # Gold dataset (200 queries)
├── goldset.jsonl          # Gold dataset nhỏ hơn
└── README.md              # File này
```

## 🚀 Cách sử dụng

### 1. Cài đặt dependencies

```bash
pip install sentence-transformers faiss-cpu pandas openpyxl matplotlib joblib scikit-learn
```

### 2. Chạy đánh giá nhanh

```bash
# Đánh giá tất cả models (mặc định)
python retrieval/run_eval.py

# Chế độ quick (ít queries, không rerank)
python retrieval/run_eval.py --quick

# Chế độ full (nhiều queries, rerank với model lớn)
python retrieval/run_eval.py --full

# Chỉ đánh giá một số models
python retrieval/run_eval.py --models legalhf tfidf
```

### 3. Chạy đánh giá chi tiết

```bash
# Đánh giá với các tham số tùy chỉnh
python retrieval/eval_all_models.py \
  --gold retrieval/gold_200_diverse.jsonl \
  --chunks output_nghidinh/chunks_clean_norm.json \
  --models tfidf legalhf phobert dek21 \
  --topk 10 \
  --match_mode dieu_khoan \
  --output eval_results.xlsx

# Không dùng reranking
python retrieval/eval_all_models.py --gold retrieval/goldset.jsonl --no-rerank

# Custom rerank model
python retrieval/eval_all_models.py --gold retrieval/goldset.jsonl \
  --rerank_model BAAI/bge-reranker-large
```

### 4. So sánh kết quả

```bash
# Phân tích 1 file kết quả
python retrieval/compare_results.py eval_results.xlsx --analyze

# So sánh nhiều experiments
python retrieval/compare_results.py eval_v1.xlsx eval_v2.xlsx --chart

# Tạo biểu đồ
python retrieval/compare_results.py eval_results.xlsx --chart
```

## 📊 Output

### Excel file (`eval_results.xlsx`)

Sheet 1: **Retrieval Results**
| Model | Reranked | N | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR | Avg Time (ms) |
|-------|----------|---|----------|----------|----------|-----------|-----|---------------|
| tfidf | No | 200 | 0.2100 | 0.3500 | 0.4200 | 0.5100 | 0.2850 | 5.2 |
| legalhf | No | 200 | 0.3500 | 0.5200 | 0.6100 | 0.7200 | 0.4320 | 25.1 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

Sheet 2: **Config**
- Tham số đã sử dụng
- Timestamp

### Biểu đồ (nếu có matplotlib)
- `comparison_metrics.png`: So sánh Recall@K và MRR giữa các models
- `rerank_comparison.png`: So sánh trước và sau khi rerank

## 🔧 Models được hỗ trợ

### Retrieval Models
| Key | Model | Mô tả |
|-----|-------|-------|
| `tfidf` | TF-IDF | Baseline, sparse retrieval |
| `legalhf` | Quockhanh05/Vietnam_legal_embeddings | Vietnamese legal embeddings |
| `phobert` | vinai/phobert-base | PhoBERT base |
| `dek21` | dangvantuan/vietnamese-embedding | Vietnamese general embedding |

### Reranking Models
| Key | Model | Mô tả |
|-----|-------|-------|
| `bge-reranker-base` | BAAI/bge-reranker-base | BGE reranker |
| `bge-reranker-large` | BAAI/bge-reranker-large | BGE large (chính xác hơn) |
| `bge-reranker-v2-m3` | BAAI/bge-reranker-v2-m3 | Multilingual, tốt cho tiếng Việt |
| `ms-marco-minilm` | cross-encoder/ms-marco-MiniLM-L-6-v2 | Lightweight |

## 📈 Metrics

### Recall@K
Tỷ lệ queries có ít nhất 1 kết quả đúng trong top-K.

### MRR (Mean Reciprocal Rank)
Trung bình của nghịch đảo rank của kết quả đúng đầu tiên.

$$MRR = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{rank_i}$$

### Match Modes
- `dieu`: Khớp văn bản + điều
- `dieu_khoan`: Khớp văn bản + điều + khoản (strict hơn)

## 📝 Gold Data Format

```jsonl
{"question": "Phạm vi điều chỉnh là gì?", "van_ban": "Nghị định 126", "dieu": "1", "khoan": null}
{"question": "Thẩm quyền của Bộ Tài chính?", "van_ban": "Nghị định 126", "dieu": "3", "khoan": "1"}
```

## 🔬 Best Practices

1. **Chạy trên GPU** nếu có: Thêm `--device cuda`
2. **Bắt đầu với quick mode** để kiểm tra setup
3. **So sánh công bằng**: Cùng gold data, cùng match_mode
4. **Reranking tốn thời gian** nhưng thường cải thiện đáng kể
5. **Lưu lại config** trong Excel để reproducible

## ⚠️ Troubleshooting

### Lỗi CUDA out of memory
```bash
# Dùng CPU
python retrieval/run_eval.py --device cpu
```

### Lỗi không tìm thấy model
Kiểm tra:
1. Folder `vector_data/` có đúng structure
2. File `index.faiss` tồn tại cho mỗi model

### Lỗi không tìm thấy chunks
```bash
# Chỉ định path đúng
python retrieval/eval_all_models.py --chunks path/to/chunks.json
```
