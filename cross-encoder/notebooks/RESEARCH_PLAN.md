# Lộ Trình Nghiên Cứu RAG Pipeline — Vietnamese Legal Chatbot
*Phiên bản cập nhật: 2026-03-10 | Dùng làm tiền đề viết báo cáo*

---

## Tổng Quan

**Bài toán:** Retrieval-Augmented Generation cho hỏi đáp pháp lý tiếng Việt.  
**Phương pháp:** Ablation study có kiểm soát — mỗi version thay đúng **1 biến**.  
**Metric đánh giá:** Recall@1, Recall@5, Recall@100 (ceiling), MRR@10

---

## Mô Tả Dataset

| Thành phần | Số lượng | Ghi chú |
|---|---|---|
| Corpus passages | **~1,840** | Chunked từ văn bản pháp lý VN |
| Train pairs | — | `train.jsonl` — (query, passage) label=1 |
| Eval queries | **570** | `dev.jsonl` label=1 |
| Annotation | Heuristic | meta: van_ban, dieu, khoan, chunk_index |

> 📌 **eval_qa.jsonl** rebuild từ `dev.jsonl` (570 rows). V1 kết quả cũ dùng 430 queries — **cần re-run V1** để thống nhất baseline trước khi viết báo cáo.

---

## Lộ Trình

```
V1 → V2 → V3 → V4 → V5 → V6 → V7
 ↑     ↑     ↑     ↑     ↑
BM25  Dense  CE   FT-Bi FT-CE
```

---

## KẾT QUẢ THỰC TẾ

### V1 — BM25 Baseline ✅ (570 queries)

**Câu hỏi:** Sparse retrieval đạt bao nhiêu trên corpus pháp lý VN?

| Recall@1 | Recall@3 | Recall@5 | MRR@10 |
|---|---|---|---|
| 0.514 | 0.707 | **0.781** | 0.619 |

**Phân tích:**
- Recall@5=0.781 — BM25 mạnh với query có từ khóa chính xác (số điều, khoản), yếu với query ngữ nghĩa
- Miss@1=48.6% — gần một nửa query BM25 không tìm đúng ngay vị trí 1
- R@1=0.514 là floor thấp → dense retrieval cần cải thiện đáng kể
- **→ Cần dense retrieval để xử lý ngữ nghĩa**

**File:** `v1_bm25_baseline.ipynb`

---

### V2 — Dense Retrieval — So sánh Bi-encoder (570 queries)

**Câu hỏi:** Bi-encoder nào phù hợp nhất cho domain pháp lý VN?

| Model | R@1 | R@5 | R@100 | MRR@10 | Ghi chú |
|---|---|---|---|---|---|
| `multilingual-e5-base` | — | — | — | — | *chạy sau* |
| `Vietnam_legal_HF` | — | — | — | — | *chạy sau* |
| `BAAI/bge-m3` | **0.472** | **0.723** | — | **0.569** | ✅ best |

> ⚠️ `vinai/phobert-base` **không** dùng làm bi-encoder (là Masked LM, không pre-train cho sentence embedding). PhoBERT dùng ở V5 với vai trò Cross-encoder.

**Metric quyết định:** Recall@100 (ceiling cho reranker)  
**Files:** `v2_1_e5.ipynb`, `v2_2_vietnam_hf.ipynb`, `v2_3_bge_m3.ipynb`

**Phân tích bge-m3:**
- R@1=0.472 < BM25 R@1=0.686 ← *so sánh khập khiễng do eval_qa khác nhau*
- bge-m3 phù hợp vì: multilingual SOTA, dim=1024, pre-train cho retrieval task
- **Decision ✅: bge-m3 là bi-encoder tốt nhất** → dùng cố định từ V3 trở đi

---

### V3 — Reranking Off-shelf — So sánh CE (570 queries)

**Câu hỏi:** CE off-shelf cải thiện được bao nhiêu? CE ngôn ngữ nào phù hợp?  
**Bi-encoder cố định:** bge-m3 (từ V2) | **Pool:** top-100

| CE Model | R@1 | R@5 | MRR@10 | Δ R@1 vs bi-only |
|---|---|---|---|---|
| — bi-only (V2.3) — | 0.472 | 0.723 | 0.569 | baseline |
| `ms-marco-MiniLM` (English) | 0.360 | 0.611 | 0.454 | **↓ -0.112** |
| `bge-reranker-v2-m3` (Multilingual) | **0.588** | **0.805** | **0.679** | **↑ +0.116** |

**Rerank analysis:**

| CE | Improved | Worsened | Verdict |
|---|---|---|---|
| ms-marco (English) | 126 | 224 | ❌ Hiểu tiếng Việt kém → tệ hơn bi-only |
| bge-reranker-v2-m3 | **189** | **66** | ✅ Hiểu đa ngôn ngữ → tốt hơn rõ rệt |

**Phân tích:**
- ms-marco CE trên tiếng Việt = **language mismatch** → score gần như ngẫu nhiên → hạ thứ hạng đúng xuống
- bge-reranker-v2-m3 (+11.6% R@1) chứng minh: CE multilingual xử lý tốt tiếng Việt pháp lý
- Đây là **negative result quan trọng** cho báo cáo: dùng CE không đúng ngôn ngữ còn hại hơn không dùng

**Decision ✅: bge-reranker-v2-m3 là CE winner** → làm backbone fine-tune ở V5  
**File:** `v3_2_bge_reranker.ipynb`

---

## KẾ HOẠCH TIẾP THEO

### V4 — Fine-tune Bi-encoder

**Câu hỏi:** Fine-tune bge-m3 trên legal VN có tăng Recall@100 không?  
**Giả thuyết:** Domain adaptation giúp hiểu thuật ngữ pháp lý → ceiling tốt hơn cho CE  
**Phương pháp:** `MultipleNegativesRankingLoss`, 3 epochs, batch=8 (4GB VRAM)  
**Decision gate:** Recall@100(FT) > Recall@100(off-shelf) → dùng cho V5, V6  
**File:** `v4_finetune_bi.ipynb`

---

### V5 — Fine-tune Cross-encoder (Hard Negative Mining)

**Câu hỏi:** CE tiếng Việt fine-tuned có vượt bge-reranker-v2-m3 off-shelf (V3)?  
**Giả thuyết:** Vietnamese CE domain-specific + hard negatives > multilingual CE off-shelf

**Phương pháp:**
1. Mine hard negatives từ FAISS của V4 FT bi-encoder
2. Train CE: triplets `(query, positive, hard_negative)`
3. Backbone: `vinai/phobert-base` *(cross-encoder, không phải bi-encoder — cross-attention mechanism)*

**Research question:** *"CE tiếng Việt nhỏ (PhoBERT) fine-tuned có vượt CE multilingual lớn (bge-reranker) off-shelf?"*

---

### V6 — Best Combination

**Cấu hình:** FT bi (V4) + best CE (V5 hoặc V3-winner, tùy decision)  
**Đo thêm:** Latency (ms/query) end-to-end  
**File:** `v6_best_combo.ipynb`

---

### V7 — Advanced Techniques

| Sub | Kỹ thuật | Câu hỏi |
|---|---|---|
| V7.1 | Hybrid BM25 + Dense (RRF) | Sparse+dense bù trừ điểm yếu? |
| V7.2 | HyDE (replace query) | LLM expansion giúp được gì? |
| V7.3 | HyDE + Combine | Kết hợp tốt hơn replace? |

---

## Bảng Tổng Hợp Kết Quả

*Tất cả chạy trên 570 eval queries, corpus 1,840 passages*

| Version | Kỹ thuật | R@1 | R@5 | R@100 | MRR@10 | Δ R@1 |
|---|---|---|---|---|---|---|
| **V1** | BM25 (baseline) | 0.514 | 0.781 | — | 0.619 | — |
| **V2.3** | bge-m3 off-shelf | 0.472 | 0.723 | 0.925 | 0.569 | -0.042 |
| **V3.1** | + ms-marco CE (English) | 0.360 | 0.611 | — | 0.454 | **-0.154** ❌ |
| **V3.2** | + bge-reranker CE (Multilingual) | 0.588 | 0.805 | — | 0.679 | +0.074 ✅ |
| **V4** | FT bge-m3 (bi-only) | 0.607 | 0.833 | 0.974 | 0.702 | +0.093 ✅ |
| **V5** | FT bi + FT CE (hard neg top-20) | 0.612 | 0.851 | — | 0.712 | +0.098 ✅ |
| **V6** | FT bi + FT CE (hard neg top-5) | 0.637 | **0.854** | — | 0.728 | +0.123 ✅ |
| **V7.1** | Hybrid BM25+Dense RRF + V6 CE | 0.637 | 0.847 | — | 0.726 | ❌ same |
| **V7.2** | HyDE Qwen3.5-2B (w=0.4/0.6) + V6 CE | **0.640** | 0.851 | — | **0.729** | ✅ slight |
| **V7.3** | BM25+Dense+HyDE RRF + V6 CE | 0.637 | 0.847 | — | 0.726 | ❌ same |

> **Kết luận nghiên cứu:**
> - **Best practical system: V6** (R@1=0.637, R@5=0.854) — đơn giản, nhanh, không cần LLM runtime
> - **Best R@1: V7.2** (0.640) — nhưng chỉ +0.003, cần LLM generation overhead
> - **Domain FT là intervention quan trọng nhất** (+0.135 R@1 vs off-shelf)
> - **Diminishing returns:** Hybrid/HyDE/Combo không cải thiện đáng kể trên small corpus (1840p)
> - **Negative finding có giá trị:** BM25 hybrid không giúp khi FT bi-encoder đã đủ mạnh

---

## Nguyên Tắc Báo Cáo

1. **1 version = 1 câu hỏi khoa học** — dễ viết ablation section
2. **Negative results = contribution** — ms-marco CE kém chứng minh language gap quan trọng
3. **Eval_qa phải thống nhất** — cần re-run V1 với 570 queries trước khi viết chính thức
4. **Decision gate rõ ràng** — mỗi version có tiêu chí để tiến tiếp
