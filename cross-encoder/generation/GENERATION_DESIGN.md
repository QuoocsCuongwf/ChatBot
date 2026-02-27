# Legal RAG Generation System — Thiết Kế Chi Tiết

**Tác giả:** GitHub Copilot  
**Ngày tạo:** 2026-02-27  
**Phiên bản:** 1.0

---

## Mục Lục

1. [Tổng Quan Hệ Thống](#1-tổng-quan-hệ-thống)
2. [RAG I/O Contract](#2-rag-io-contract)
3. [Legal-Grounded Prompt Design](#3-legal-grounded-prompt-design)
4. [Context Builder](#4-context-builder)
5. [Gating Strategy](#5-gating-strategy)
6. [LLM Integration](#6-llm-integration)
7. [Fallback Strategy](#7-fallback-strategy)
8. [E2E Evaluation](#8-e2e-evaluation)
9. [Hướng Dẫn Sử Dụng](#9-hướng-dẫn-sử-dụng)

---

## 1. Tổng Quan Hệ Thống

### 1.1 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      LEGAL RAG GENERATION PIPELINE                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐  │
│  │  Query   │───▶│ Retrieve │───▶│  Rerank  │───▶│   Context    │  │
│  │          │    │ (FAISS)  │    │  (CE)    │    │   Builder    │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────────┘  │
│                                                          │          │
│                                                          ▼          │
│  ┌──────────────┐              ┌──────────┐    ┌──────────────┐    │
│  │   Output     │◀────────────│   LLM    │◀───│   Gating     │    │
│  │   Parser     │              │ Generate │    │  Decision    │    │
│  └──────────────┘              └──────────┘    └──────────────┘    │
│          │                                             │            │
│          ▼                                             ▼            │
│  ┌──────────────┐                              ┌──────────────┐    │
│  │  Fallback    │                              │   Abstain/   │    │
│  │  Handler     │                              │   Ask-back   │    │
│  └──────────────┘                              └──────────────┘    │
│          │                                                          │
│          ▼                                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     RAGOutput (JSON)                          │  │
│  │  { answer, citations, abstain, reason, confidence }           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Hiện Trạng Hệ Thống (Trước Generation)

| Metric | Baseline | Reranked | Mục Tiêu Gen |
|--------|----------|----------|--------------|
| Recall@1 | 20.7% | 54.2% | - |
| Recall@5 | 40.9% | 73.3% | - |
| MRR@10 | 29.1% | 63.1% | - |
| Citation Hit Rate | - | 64% | 75%+ |
| Cross-Encoder F1 | - | 88.5% | - |
| ROC-AUC | - | 95.6% | - |

### 1.3 Các Module Chính

| Module | File | Chức năng |
|--------|------|-----------|
| RAG Contract | `rag_contract.py` | Định nghĩa I/O chuẩn |
| Context Builder | `context_builder.py` | Dedup, trim, metadata |
| Prompt Templates | `prompt_templates.py` | Legal-grounded prompts |
| Gating | `gating.py` | Pass/Abstain/Ask-back |
| LLM Client | `llm_client.py` | Multi-backend LLM |
| Fallback | `fallback.py` | Xử lý 36% không hit |
| Evaluator | `evaluator.py` | E2E metrics |
| Pipeline | `run_generation.py` | Main orchestrator |

---

## 2. RAG I/O Contract

### 2.1 Input Contract

```python
@dataclass
class RAGInput:
    question: str                       # Câu hỏi từ user
    top_k_chunks: List[ChunkInfo]       # Chunks đã rerank
    policy: RAGPolicy                   # Chính sách RAG
    
@dataclass
class ChunkInfo:
    chunk_id: int                       # ID trong FAISS
    text: str                           # Nội dung chunk
    score_retrieval: float              # Score từ bi-encoder
    score_rerank: float                 # Score từ cross-encoder
    
    # Metadata pháp lý
    van_ban: str                        # Tên văn bản
    chuong: Optional[str]               # Chương
    dieu: Optional[str]                 # Điều
    khoan: Optional[str]                # Khoản
    diem: Optional[str]                 # Điểm
    source_file: str                    # File nguồn

@dataclass
class RAGPolicy:
    must_cite: bool = True              # Bắt buộc trích dẫn
    no_hallucination: bool = True       # Không được bịa
    abstain_if_uncertain: bool = True   # Abstain nếu không chắc
    
    confidence_threshold_pass: float = 0.5
    confidence_threshold_abstain: float = 0.3
    max_chunks_in_context: int = 5
    max_chunks_per_source: int = 2      # Rule dedup
```

### 2.2 Output Contract

```python
@dataclass
class RAGOutput:
    answer: Optional[str]               # Câu trả lời tiếng Việt
    citations: List[Citation]           # Danh sách trích dẫn
    
    decision: DecisionType              # ANSWER/ABSTAIN/ASK_BACK/CAUTIOUS
    abstain: bool = False
    abstain_reason: Optional[AbstainReason]
    reason_detail: Optional[str]        # Chi tiết lý do
    
    clarification_question: Optional[str]  # Nếu ASK_BACK
    
    confidence_score: float = 0.0
    latency_llm_ms: float = 0.0

@dataclass
class Citation:
    van_ban: str
    dieu: Optional[str]
    khoan: Optional[str]
    diem: Optional[str]
    quoted_text: Optional[str]          # Đoạn text đã trích
```

### 2.3 JSON Output Format

```json
{
  "answer": "Chủ tịch UBND cấp huyện có thẩm quyền quyết định...",
  "citations": [
    {
      "van_ban": "Nghị định về xây dựng",
      "dieu": "8",
      "khoan": "2",
      "diem": null,
      "noi_dung": "Chủ tịch UBND cấp huyện quyết định..."
    }
  ],
  "abstain": false,
  "reason": null
}
```

---

## 3. Legal-Grounded Prompt Design

### 3.1 Ba Luật Cứng

| # | Luật | Giải thích |
|---|------|------------|
| 1 | **CHỈ dùng thông tin trong context** | KHÔNG suy diễn, bịa đặt, dùng kiến thức bên ngoài |
| 2 | **MỖI ý pháp lý PHẢI có trích dẫn** | Format: "Theo Điều X, Khoản Y..." |
| 3 | **Nếu context KHÔNG ĐỦ → abstain** | Trả về `abstain: true` |

### 3.2 System Prompt

```
Bạn là trợ lý pháp lý chuyên về văn bản quy phạm pháp luật Việt Nam.

## LUẬT BẮT BUỘC:
1. CHỈ dùng thông tin trong CONTEXT được cung cấp
2. MỖI ý pháp lý PHẢI có trích dẫn cụ thể (Điều, Khoản, Điểm)
3. Nếu context KHÔNG ĐỦ căn cứ → phải trả về abstain=true

## QUY TẮC TRÍCH DẪN:
- Format: "Theo Điều X, Khoản Y, Điểm Z của [Tên văn bản]..."
- Mỗi thông tin pháp lý phải kèm nguồn
- KHÔNG được tự tạo điều khoản không có trong context

## CẢNH BÁO:
- KHÔNG suy diễn luật
- KHÔNG kết hợp các điều khoản theo cách không được quy định
```

### 3.3 Format Trả Lời Chuẩn

```
**Kết luận:** [Trả lời ngắn gọn]

**Căn cứ pháp lý:**
- Điều X, Khoản Y: [nội dung]
- Điều Z: [nội dung]

**Giải thích:** [Giải thích dựa trên context]

**Trích dẫn:**
1. [Tên văn bản] - Điều X, Khoản Y
```

---

## 4. Context Builder

### 4.1 Ba Cải Tiến Chính

#### (a) Dedup & Diversify

**Vấn đề:** Top-5 chunks toàn cùng một văn bản/điều → giảm độ phủ

**Giải pháp:**
- **Rule:** Max 2 chunks / 1 nguồn (van_ban + dieu)
- Ưu tiên chunks từ các điều/khoản khác nhau
- Loại bỏ duplicate text (fuzzy matching)

```python
def dedup_and_diversify(chunks, max_per_source=2, max_total=5):
    source_count = defaultdict(int)  # Track: (van_ban, dieu) -> count
    result = []
    
    for chunk in chunks:
        source_key = (chunk.van_ban, chunk.dieu)
        if source_count[source_key] >= max_per_source:
            continue  # Skip
        source_count[source_key] += 1
        result.append(chunk)
    
    return result[:max_total]
```

#### (b) Span Trim

**Vấn đề:** Chunk chứa nhiều "rác" không liên quan

**Giải pháp:**
- Tìm keyword matches trong chunk
- Expand mỗi match với context window (~150 chars)
- Merge overlapping spans
- LLM nhìn context "sạch" hơn

```python
def trim_span(chunk, query, context_window=150):
    keywords = extract_keywords(query)
    spans = []
    
    for keyword in keywords:
        for match in re.finditer(keyword, chunk.text):
            start = max(0, match.start() - context_window)
            end = min(len(chunk.text), match.end() + context_window)
            spans.append((start, end))
    
    merged = merge_spans(spans)
    return extract_text(chunk.text, merged)
```

#### (c) Metadata Injection

**Vấn đề:** LLM không biết citation nằm ở đâu

**Giải pháp:** Inject header metadata vào trước mỗi chunk

```
[VB: Nghị định về xây dựng, Chương II, Điều 5, Khoản 2, Điểm a]
Nội dung chunk ở đây...
```

→ LLM sẽ trích dẫn chuẩn hơn vì metadata rõ ràng

---

## 5. Gating Strategy

### 5.1 Tại Sao Cần Gating?

- Cross-encoder ROC-AUC = 0.96 → **quá tốt để làm confidence gate**
- 36% query không hit đúng citation → cần biết khi nào KHÔNG nên trả lời
- Giảm hallucination bằng cách abstain đúng lúc

### 5.2 Các Rules Gating

| Rule | Điều kiện | Action |
|------|-----------|--------|
| 1 | `score_top1 < 0.5` | ABSTAIN |
| 2 | `(top1 - top2) < margin` | ASK_BACK (không rõ ràng) |
| 3 | Keyword coverage < 30% | ASK_BACK |
| 4 | Query type không match context | ABSTAIN |
| 5 | Query ambiguous | ASK_BACK |
| 6 | `0.5 <= score < 2.0` | CAUTIOUS (trả lời + cảnh báo) |
| 7 | `score >= 2.0` | PASS |

### 5.3 Decision Types

```python
class DecisionType(Enum):
    ANSWER = "answer"           # Trả lời đầy đủ
    ABSTAIN = "abstain"         # Không đủ căn cứ
    ASK_BACK = "ask_back"       # Cần thêm thông tin
    CAUTIOUS = "cautious"       # Trả lời + cảnh báo
```

### 5.4 Calibration

```python
# Score distribution từ dev set
threshold_pass = percentile_75(scores)     # ~2.0
threshold_abstain = percentile_10(scores)  # ~0.5
threshold_cautious = percentile_50(scores) # ~1.0
```

---

## 6. LLM Integration

### 6.1 Hai Chế Độ

| Mode | Use Case | Config |
|------|----------|--------|
| **DEV** | Iterate prompt nhanh | Model 7B Q4, context 2-4K, temp 0.1 |
| **DEMO** | Production/Demo | Model lớn hơn, context 8K+, streaming |

### 6.2 Supported Backends

| Backend | Ưu điểm | Nhược điểm |
|---------|---------|------------|
| **llama.cpp** | Local, free, privacy | Cần GPU |
| **OpenRouter** | Nhiều model, dễ dùng | Tốn phí |
| **OpenAI** | Quality cao | Đắt |
| **Gemini** | Free tier | Rate limit |
| **HuggingFace** | Flexible | Setup phức tạp |

### 6.3 Config Example

```python
# Dev mode
config = LLMConfig(
    mode=LLMMode.DEV,
    backend=LLMBackend.LLAMA_CPP,
    model_path="models/llama-7b-q4.gguf",
    max_tokens=256,
    context_length=2048,
    temperature=0.1
)

# Demo mode
config = LLMConfig(
    mode=LLMMode.DEMO,
    backend=LLMBackend.OPENROUTER,
    model_name="mistralai/mistral-7b-instruct",
    max_tokens=512,
    enable_streaming=True
)
```

---

## 7. Fallback Strategy

### 7.1 Hai Fallback An Toàn

#### (1) ASK-BACK: Hỏi lại khi thiếu thông tin

| Missing Info | Clarification Question |
|--------------|------------------------|
| Địa phương | "Bạn đang hỏi về địa phương/khu vực nào cụ thể?" |
| Thời điểm | "Bạn muốn biết thông tin áp dụng cho thời điểm nào?" |
| Đối tượng | "Bạn có thể cho biết đối tượng cụ thể?" |
| Trường hợp | "Bạn có thể mô tả cụ thể trường hợp?" |

#### (2) CAUTIOUS: Trả lời thận trọng + cảnh báo

```
Dựa trên các văn bản được cung cấp, tôi tìm thấy một số thông tin liên quan:

[Nội dung trả lời]

⚠️ **Lưu ý**: Tôi chưa tìm thấy điều khoản trực tiếp quy định về vấn đề bạn hỏi. 
Thông tin trên chỉ mang tính tham khảo. 
Vui lòng tham vấn chuyên gia pháp lý để được tư vấn chính xác.
```

### 7.2 TUYỆT ĐỐI TRÁNH

❌ **Suy diễn luật** - Không được kết hợp/suy ra từ nhiều điều khoản

❌ **Trả lời không có căn cứ** - Mọi statement phải có citation

❌ **Bịa điều khoản** - Không tạo Điều/Khoản không có trong context

---

## 8. E2E Evaluation

### 8.1 Metrics Cần Đo

| Metric | Mô tả | Cách tính |
|--------|-------|-----------|
| **Citation Correctness** | Trích dẫn đúng điều/khoản | Precision, Recall, F1 |
| **Citation Hit Rate** | Có trích dẫn đúng trong answer | % hit trong expected |
| **Answer Supported Rate** | Answer được support bởi context | Human eval / LLM-judge |
| **Abstain Precision** | Abstain đúng lúc | TP / (TP + FP) |
| **Pass Precision** | Pass khi answerable | TP / (TP + FP) |
| **Latency** | Retrieval + Rerank + LLM | ms |

### 8.2 Evaluation Pipeline

```
goldset.jsonl
    │
    ▼
┌─────────────────────────────────────┐
│  For each sample:                    │
│  1. Retrieve & Rerank               │
│  2. Gate decision                   │
│  3. Generate (if pass)              │
│  4. Parse citations                 │
│  5. Compare with expected           │
└─────────────────────────────────────┘
    │
    ▼
evaluation_results.jsonl
evaluation_summary.md
```

### 8.3 Sample Evaluation Output

```json
{
  "query_id": "eval_0119",
  "query": "Cơ quan nào đề xuất trình Thủ tướng...",
  "gating_decision": "answer",
  "citation_hit": true,
  "citation_precision": 1.0,
  "citation_recall": 1.0,
  "citation_f1": 1.0,
  "latency_total_ms": 432.5
}
```

### 8.4 Expected Improvements

| Metric | Before | After (Expected) |
|--------|--------|------------------|
| Citation Hit Rate | 64% | 75%+ |
| Abstain Rate | 2% | 8-12% |
| False Positive Rate | 36% | <20% |
| Avg Latency | 340ms | 500-800ms |

---

## 9. Hướng Dẫn Sử Dụng

### 9.1 Installation

```bash
cd cross-encoder/generation
pip install -r requirements.txt  # (nếu có)
```

### 9.2 Quick Start

```python
from generation import (
    GenerationPipeline, LegalRetriever,
    LLMClient, LLMConfig, LLMMode
)

# Initialize
retriever = LegalRetriever()
pipeline = GenerationPipeline(retriever=retriever)

# Generate
output, metadata = pipeline.generate("Ai có thẩm quyền cấp phép xây dựng?")

print(f"Answer: {output.answer}")
print(f"Citations: {[c.to_str() for c in output.citations]}")
print(f"Latency: {metadata['timestamps']['total']:.0f}ms")
```

### 9.3 CLI Commands

```bash
# Single query (dev mode)
python run_generation.py --query "Ai có thẩm quyền..." --mode dev -v

# Evaluation
python run_generation.py --eval --max_samples 50 --mode dev

# Interactive mode
python run_generation.py --mode demo

# With specific LLM backend
python run_generation.py --backend openrouter --query "..."
```

### 9.4 Environment Variables

```bash
# API Keys (optional)
export OPENROUTER_API_KEY="sk-or-..."
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."

# llama.cpp model path (optional)
export LLAMA_MODEL_PATH="models/llama-7b-q4.gguf"
```

### 9.5 Output Files

```
outputs/generation/
├── generation_eval_results_YYYYMMDD_HHMMSS.jsonl   # Chi tiết từng sample
├── generation_eval_summary_YYYYMMDD_HHMMSS.json    # Summary JSON
├── generation_eval_summary_YYYYMMDD_HHMMSS.md      # Summary Markdown
└── generation_eval_metrics_YYYYMMDD_HHMMSS.csv     # Metrics CSV
```

---

## 10. Next Steps

### 10.1 Immediate (Week 1)

1. [ ] Test với llama.cpp local model
2. [ ] Run evaluation trên 100 samples
3. [ ] Tune gating thresholds based on results
4. [ ] Integrate với existing run_pipeline.py

### 10.2 Short-term (Week 2-3)

1. [ ] Add LLM-as-judge cho Answer Supported Rate
2. [ ] Implement caching cho repeated queries
3. [ ] A/B test different prompt templates
4. [ ] Build simple UI/API demo

### 10.3 Long-term

1. [ ] Fine-tune model cho Vietnamese legal
2. [ ] Add multi-turn conversation support
3. [ ] Implement RAG feedback loop
4. [ ] Production deployment

---

## Appendix A: File Structure

```
cross-encoder/generation/
├── __init__.py              # Module exports
├── rag_contract.py          # I/O contract definitions
├── context_builder.py       # Dedup, trim, metadata
├── prompt_templates.py      # Legal-grounded prompts
├── gating.py                # Pass/Abstain/Ask-back logic
├── llm_client.py            # Multi-backend LLM client
├── fallback.py              # Fallback strategies
├── evaluator.py             # E2E evaluation
└── run_generation.py        # Main pipeline
```

---

## Appendix B: Prompt Templates Reference

### JSON Output Template

```
## FORMAT TRẢ LỜI (JSON):
{
  "answer": "Câu trả lời ngắn gọn",
  "citations": [
    {
      "van_ban": "Tên văn bản",
      "dieu": "số điều",
      "khoan": "số khoản",
      "diem": "điểm",
      "noi_dung": "Trích dẫn nguyên văn"
    }
  ],
  "abstain": false,
  "reason": null
}
```

### Natural Output Template

```
**Kết luận:** [Trả lời]
**Căn cứ pháp lý:** Điều X, Khoản Y
**Giải thích:** [Chi tiết]
**Trích dẫn:** [Liệt kê]
```

---

*Document generated by Legal RAG Generation System v1.0*
