"""
rag_contract.py — Định nghĩa Input/Output Contract cho Legal RAG System

Mục tiêu:
- Chuẩn hóa format đầu vào/đầu ra cho LLM
- Dễ dàng đo lường: Answer Pass Rate, Faithfulness, Citation Correctness
- Tương thích với các LLM khác nhau (local llama.cpp, API, etc.)
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from enum import Enum
import json
import re


# ═══════════════════════════════════════════════════════════════════════════════
# 1. ENUMS & CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

class DecisionType(Enum):
    ANSWER = "answer"           # Trả lời đầy đủ với citation
    ABSTAIN = "abstain"         # Không đủ căn cứ để trả lời
    ASK_BACK = "ask_back"       # Cần thêm thông tin từ user
    CAUTIOUS = "cautious"       # Trả lời thận trọng với cảnh báo


class AbstainReason(Enum):
    NO_RELEVANT_CHUNK = "no_relevant_chunk"
    LOW_CONFIDENCE = "low_confidence"
    MISSING_LEGAL_KEYWORD = "missing_legal_keyword"
    AMBIGUOUS_QUERY = "ambiguous_query"
    OUT_OF_SCOPE = "out_of_scope"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. INPUT CONTRACT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ChunkInfo:
    """Thông tin một chunk được retrieve/rerank."""
    
    chunk_id: int                      # ID trong FAISS index
    text: str                          # Nội dung chunk
    score_retrieval: float             # Score từ bi-encoder/FAISS
    score_rerank: float                # Score từ cross-encoder
    
    # Metadata pháp lý
    van_ban: str = ""                  # Tên văn bản (Nghị định, Thông tư, ...)
    chuong: Optional[str] = None       # Chương
    dieu: Optional[str] = None         # Điều
    khoan: Optional[str] = None        # Khoản
    diem: Optional[str] = None         # Điểm
    source_file: str = ""              # File nguồn
    
    # Span info (sau khi trim)
    trimmed_text: Optional[str] = None # Text đã được trim
    highlight_spans: List[tuple] = field(default_factory=list)  # [(start, end), ...]
    
    def get_citation_str(self) -> str:
        """Tạo chuỗi citation chuẩn: Điều X, Khoản Y, Điểm Z."""
        parts = []
        if self.dieu:
            parts.append(f"Điều {self.dieu}")
        if self.khoan:
            parts.append(f"Khoản {self.khoan}")
        if self.diem:
            parts.append(f"Điểm {self.diem}")
        return ", ".join(parts) if parts else "N/A"
    
    def get_full_citation(self) -> str:
        """Citation đầy đủ với tên văn bản."""
        citation = self.get_citation_str()
        if self.van_ban:
            return f"{citation} - {self.van_ban}"
        return citation
    
    def get_metadata_header(self) -> str:
        """Tạo header metadata để inject vào context."""
        parts = [f"[VB: {self.van_ban}"]
        if self.chuong:
            parts.append(f"Chương {self.chuong}")
        if self.dieu:
            parts.append(f"Điều {self.dieu}")
        if self.khoan:
            parts.append(f"Khoản {self.khoan}")
        if self.diem:
            parts.append(f"Điểm {self.diem}")
        return ", ".join(parts) + "]"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RAGPolicy:
    """Chính sách bắt buộc cho Legal RAG."""
    
    # Luật cứng
    must_cite: bool = True              # Bắt buộc trích dẫn điều/khoản
    no_hallucination: bool = True       # Không được bịa thông tin
    abstain_if_uncertain: bool = True   # Abstain nếu không đủ căn cứ
    
    # Ngưỡng quyết định
    confidence_threshold_pass: float = 0.5    # Score tối thiểu để PASS
    confidence_threshold_abstain: float = 0.3 # Dưới mức này → ABSTAIN
    margin_threshold: float = 0.2             # Khoảng cách top1-top2
    
    # Giới hạn
    max_chunks_in_context: int = 5
    max_chunks_per_source: int = 2      # Dedup: tối đa 2 chunk/văn bản
    min_keyword_overlap: float = 0.3    # Overlap từ khóa tối thiểu
    
    # Ask-back triggers
    ask_back_keywords: List[str] = field(default_factory=lambda: [
        "địa phương", "thời điểm", "đối tượng", "trường hợp", "cụ thể"
    ])


@dataclass
class RAGInput:
    """Input chuẩn cho LLM trong Legal RAG."""
    
    question: str                       # Câu hỏi từ user
    top_k_chunks: List[ChunkInfo]       # Danh sách chunks đã rerank
    policy: RAGPolicy                   # Chính sách RAG
    
    # Metadata bổ sung
    query_id: Optional[str] = None
    retrieved_at: Optional[str] = None
    total_retrieve_time_ms: float = 0.0
    total_rerank_time_ms: float = 0.0
    
    # Gating decision (từ Gating module)
    gating_decision: Optional[DecisionType] = None
    gating_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["gating_decision"] = self.gating_decision.value if self.gating_decision else None
        return result
    
    def get_context_for_llm(self) -> str:
        """Tạo context string để đưa vào prompt."""
        context_parts = []
        for i, chunk in enumerate(self.top_k_chunks, 1):
            header = chunk.get_metadata_header()
            text = chunk.trimmed_text or chunk.text
            context_parts.append(f"[{i}] {header}\n{text}")
        return "\n\n".join(context_parts)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. OUTPUT CONTRACT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Citation:
    """Một trích dẫn pháp lý trong câu trả lời."""
    
    van_ban: str                        # Tên văn bản
    chuong: Optional[str] = None
    dieu: Optional[str] = None
    khoan: Optional[str] = None
    diem: Optional[str] = None
    
    # Liên kết với chunk
    chunk_id: Optional[int] = None      # ID chunk nguồn
    span_start: Optional[int] = None    # Vị trí bắt đầu trong text
    span_end: Optional[int] = None      # Vị trí kết thúc trong text
    quoted_text: Optional[str] = None   # Đoạn text được trích dẫn
    
    def matches(self, expected: Dict) -> bool:
        """Kiểm tra citation có khớp với expected không."""
        # Exact match on dieu/khoan/diem
        if self.dieu and expected.get("dieu"):
            if str(self.dieu) != str(expected.get("dieu")):
                return False
        if self.khoan and expected.get("khoan"):
            if str(self.khoan) != str(expected.get("khoan")):
                return False
        if self.diem and expected.get("diem"):
            if str(self.diem) != str(expected.get("diem")):
                return False
        return True
    
    def to_str(self) -> str:
        parts = []
        if self.dieu:
            parts.append(f"Điều {self.dieu}")
        if self.khoan:
            parts.append(f"Khoản {self.khoan}")
        if self.diem:
            parts.append(f"Điểm {self.diem}")
        citation = ", ".join(parts) if parts else "N/A"
        if self.van_ban:
            citation += f" ({self.van_ban})"
        return citation
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RAGOutput:
    """Output chuẩn từ LLM trong Legal RAG."""
    
    # Kết quả chính
    answer: Optional[str] = None        # Câu trả lời tiếng Việt
    citations: List[Citation] = field(default_factory=list)
    
    # Quyết định
    decision: DecisionType = DecisionType.ANSWER
    abstain: bool = False
    abstain_reason: Optional[AbstainReason] = None
    reason_detail: Optional[str] = None  # Chi tiết lý do abstain
    
    # Ask-back (nếu cần)
    clarification_question: Optional[str] = None
    
    # Metadata
    confidence_score: float = 0.0       # Điểm tin cậy tổng
    latency_llm_ms: float = 0.0         # Thời gian LLM inference
    raw_response: Optional[str] = None  # Response gốc từ LLM
    
    # Evaluation markers
    supported_by_context: Optional[bool] = None  # Answer có được support bởi context?
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["decision"] = self.decision.value
        result["abstain_reason"] = self.abstain_reason.value if self.abstain_reason else None
        result["citations"] = [c.to_dict() for c in self.citations]
        return result
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. FACTORY & PARSING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_rag_input(
    question: str,
    chunks: List[Dict],
    policy: Optional[RAGPolicy] = None
) -> RAGInput:
    """Tạo RAGInput từ kết quả retrieve/rerank."""
    
    if policy is None:
        policy = RAGPolicy()
    
    chunk_infos = []
    for chunk in chunks:
        meta = chunk.get("metadata", chunk.get("meta", {}))
        chunk_info = ChunkInfo(
            chunk_id=chunk.get("chunk_id", chunk.get("faiss_id", -1)),
            text=chunk.get("text", chunk.get("passage", "")),
            score_retrieval=chunk.get("score_retrieval", chunk.get("faiss_score", 0.0)),
            score_rerank=chunk.get("score_rerank", chunk.get("rerank_score", 0.0)),
            van_ban=meta.get("van_ban", ""),
            chuong=meta.get("chuong"),
            dieu=meta.get("dieu"),
            khoan=meta.get("khoan"),
            diem=meta.get("diem"),
            source_file=meta.get("source_file", ""),
        )
        chunk_infos.append(chunk_info)
    
    return RAGInput(
        question=question,
        top_k_chunks=chunk_infos,
        policy=policy
    )


def parse_rag_output(raw_response: str, expected_format: str = "structured") -> RAGOutput:
    """
    Parse response từ LLM thành RAGOutput.
    
    Hỗ trợ 2 format:
    1. structured: JSON có cấu trúc
    2. natural: Text tự nhiên với markers
    """
    
    output = RAGOutput(raw_response=raw_response)
    
    # Thử parse JSON trước
    try:
        # Tìm JSON block trong response
        json_match = re.search(r'\{[\s\S]*\}', raw_response)
        if json_match:
            data = json.loads(json_match.group())
            
            # Parse answer
            output.answer = data.get("answer") or data.get("ket_luan")
            
            # Parse abstain
            output.abstain = data.get("abstain", False)
            if output.abstain:
                output.decision = DecisionType.ABSTAIN
                reason = data.get("reason") or data.get("ly_do")
                if reason:
                    output.reason_detail = reason
            
            # Parse citations
            citations_data = data.get("citations") or data.get("trich_dan") or []
            for cit in citations_data:
                citation = Citation(
                    van_ban=cit.get("van_ban", ""),
                    dieu=cit.get("dieu"),
                    khoan=cit.get("khoan"),
                    diem=cit.get("diem"),
                    quoted_text=cit.get("quoted_text") or cit.get("noi_dung")
                )
                output.citations.append(citation)
            
            return output
            
    except (json.JSONDecodeError, AttributeError):
        pass
    
    # Fallback: parse natural text
    output.answer = raw_response
    
    # Tìm các pattern citation trong text
    # Pattern: Điều X, Khoản Y, Điểm Z
    citation_patterns = [
        r'(?:Điều|điều)\s*(\d+)',
        r'(?:Khoản|khoản)\s*(\d+)',
        r'(?:Điểm|điểm)\s*([a-zđ])'
    ]
    
    dieu_matches = re.findall(r'(?:Điều|điều)\s*(\d+)', raw_response)
    khoan_matches = re.findall(r'(?:Khoản|khoản)\s*(\d+)', raw_response)
    diem_matches = re.findall(r'(?:Điểm|điểm)\s*([a-zđ])', raw_response)
    
    # Tạo citations từ các matches
    if dieu_matches:
        for dieu in set(dieu_matches):
            citation = Citation(van_ban="", dieu=dieu)
            output.citations.append(citation)
    
    # Kiểm tra abstain markers
    abstain_markers = [
        "không tìm thấy", "không đủ căn cứ", "không có thông tin",
        "thiếu thông tin", "không thể xác định", "cần thêm thông tin"
    ]
    if any(marker in raw_response.lower() for marker in abstain_markers):
        output.abstain = True
        output.decision = DecisionType.ABSTAIN
        output.reason_detail = "Detected abstain marker in response"
    
    return output


# ═══════════════════════════════════════════════════════════════════════════════
# 5. VALIDATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def validate_output_against_policy(output: RAGOutput, policy: RAGPolicy) -> List[str]:
    """Kiểm tra output có tuân thủ policy không."""
    violations = []
    
    # Kiểm tra phải có citation
    if policy.must_cite and output.answer and not output.abstain:
        if len(output.citations) == 0:
            violations.append("VIOLATION: Answer without citation (must_cite=True)")
    
    return violations


def compute_citation_correctness(
    output: RAGOutput, 
    expected_citations: List[Dict]
) -> Dict[str, float]:
    """Tính toán Citation Correctness metrics."""
    
    if not expected_citations:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "exact_match": 1.0}
    
    if not output.citations:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "exact_match": 0.0}
    
    # Count matches
    matched_expected = set()
    matched_output = set()
    
    for i, out_cit in enumerate(output.citations):
        for j, exp_cit in enumerate(expected_citations):
            if out_cit.matches(exp_cit):
                matched_expected.add(j)
                matched_output.add(i)
    
    precision = len(matched_output) / len(output.citations) if output.citations else 0
    recall = len(matched_expected) / len(expected_citations) if expected_citations else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    exact_match = 1.0 if len(matched_expected) == len(expected_citations) else 0.0
    
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "exact_match": exact_match
    }
