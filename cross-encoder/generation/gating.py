"""
gating.py — Gating Strategy: Khi nào trả lời, khi nào abstain

Với cross-encoder ROC-AUC 0.96, ta có confidence gate rất tốt.

Rules:
1. score_top1 < threshold → ABSTAIN
2. (top1 - top2) < margin → ABSTAIN (không rõ ràng)
3. Query type không match context keywords → ABSTAIN
4. Fallback: ASK_BACK hoặc CAUTIOUS answer
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .rag_contract import (
    ChunkInfo, RAGInput, RAGOutput, RAGPolicy,
    DecisionType, AbstainReason, Citation
)
from .context_builder import ContextBuilder


@dataclass
class GatingConfig:
    """Cấu hình ngưỡng cho gating."""
    
    # Score thresholds
    threshold_pass: float = 2.0           # Score >= này → PASS
    threshold_abstain: float = 0.5        # Score < này → ABSTAIN
    threshold_cautious: float = 1.0       # Giữa abstain và pass → CAUTIOUS
    
    # Margin threshold
    margin_min: float = 1.0               # top1 - top2 < margin → không rõ ràng
    
    # Keyword coverage
    min_keyword_coverage: float = 0.3     # Overlap từ khóa tối thiểu
    
    # Legal keyword requirements
    require_legal_keyword: bool = True    # Bắt buộc có từ khóa pháp lý
    
    # Ask-back triggers
    enable_ask_back: bool = True
    ask_back_on_ambiguous: bool = True


class GatingDecision:
    """Kết quả của gating decision."""
    
    def __init__(
        self,
        decision: DecisionType,
        reason: Optional[AbstainReason] = None,
        reason_detail: str = "",
        confidence: float = 0.0,
        clarification_question: Optional[str] = None
    ):
        self.decision = decision
        self.reason = reason
        self.reason_detail = reason_detail
        self.confidence = confidence
        self.clarification_question = clarification_question
    
    def to_dict(self) -> Dict:
        return {
            "decision": self.decision.value,
            "reason": self.reason.value if self.reason else None,
            "reason_detail": self.reason_detail,
            "confidence": self.confidence,
            "clarification_question": self.clarification_question
        }


class GatingStrategy:
    """
    Strategy để quyết định PASS / ABSTAIN / ASK_BACK / CAUTIOUS.
    
    Pipeline:
    1. Check score threshold
    2. Check score margin (top1 - top2)
    3. Check keyword coverage
    4. Check legal keyword presence
    5. Check query ambiguity
    """
    
    def __init__(self, config: Optional[GatingConfig] = None):
        self.config = config or GatingConfig()
        self.context_builder = ContextBuilder()
        
        # Legal keywords phải có trong context cho mỗi query type
        self.legal_keyword_requirements = {
            "định nghĩa": ["định nghĩa", "là", "được hiểu", "có nghĩa"],
            "điều kiện": ["điều kiện", "phải", "cần", "đáp ứng", "yêu cầu"],
            "thủ tục": ["thủ tục", "trình tự", "bước", "hồ sơ", "đề nghị"],
            "thẩm quyền": ["thẩm quyền", "có quyền", "quyết định", "chịu trách nhiệm"],
            "phí": ["phí", "lệ phí", "mức", "thu", "nộp"],
            "thời hạn": ["thời hạn", "trong vòng", "ngày", "tháng", "kể từ"]
        }
    
    def evaluate(self, rag_input: RAGInput) -> GatingDecision:
        """
        Đánh giá và đưa ra gating decision.
        
        Returns:
            GatingDecision with decision type and reasoning
        """
        
        chunks = rag_input.top_k_chunks
        query = rag_input.question
        
        if not chunks:
            return GatingDecision(
                decision=DecisionType.ABSTAIN,
                reason=AbstainReason.NO_RELEVANT_CHUNK,
                reason_detail="Không tìm thấy chunk liên quan",
                confidence=0.0
            )
        
        # Get scores
        scores = [c.score_rerank for c in chunks]
        top1_score = scores[0] if scores else 0.0
        top2_score = scores[1] if len(scores) > 1 else 0.0
        margin = top1_score - top2_score
        
        # ─────────────────────────────────────────────────────────────────────
        # Rule 1: Score threshold check
        # ─────────────────────────────────────────────────────────────────────
        
        if top1_score < self.config.threshold_abstain:
            return GatingDecision(
                decision=DecisionType.ABSTAIN,
                reason=AbstainReason.LOW_CONFIDENCE,
                reason_detail=f"Top-1 score ({top1_score:.2f}) < threshold ({self.config.threshold_abstain})",
                confidence=top1_score
            )
        
        # ─────────────────────────────────────────────────────────────────────
        # Rule 2: Margin check
        # ─────────────────────────────────────────────────────────────────────
        
        if margin < self.config.margin_min and self.config.enable_ask_back:
            # Scores quá gần nhau → không chắc chắn
            if self.config.ask_back_on_ambiguous:
                return GatingDecision(
                    decision=DecisionType.ASK_BACK,
                    reason=AbstainReason.AMBIGUOUS_QUERY,
                    reason_detail=f"Margin ({margin:.2f}) < threshold ({self.config.margin_min}), kết quả không rõ ràng",
                    confidence=top1_score,
                    clarification_question="Bạn có thể cho biết thêm chi tiết về câu hỏi?"
                )
        
        # ─────────────────────────────────────────────────────────────────────
        # Rule 3: Keyword coverage check
        # ─────────────────────────────────────────────────────────────────────
        
        coverage_info = self.context_builder.check_keyword_coverage(query, chunks)
        
        if coverage_info["coverage"] < self.config.min_keyword_coverage:
            if self.config.enable_ask_back:
                return GatingDecision(
                    decision=DecisionType.ASK_BACK,
                    reason=AbstainReason.MISSING_LEGAL_KEYWORD,
                    reason_detail=f"Keyword coverage ({coverage_info['coverage']:.2%}) thấp. Missing: {coverage_info['missing'][:5]}",
                    confidence=top1_score,
                    clarification_question=self._generate_clarification_question(query, coverage_info)
                )
            else:
                return GatingDecision(
                    decision=DecisionType.CAUTIOUS,
                    reason=AbstainReason.MISSING_LEGAL_KEYWORD,
                    reason_detail=f"Keyword coverage thấp: {coverage_info['coverage']:.2%}",
                    confidence=top1_score
                )
        
        # ─────────────────────────────────────────────────────────────────────
        # Rule 4: Legal keyword requirement check
        # ─────────────────────────────────────────────────────────────────────
        
        if self.config.require_legal_keyword:
            query_types = self.context_builder.detect_query_type(query)
            
            for qtype in query_types:
                required_keywords = self.legal_keyword_requirements.get(qtype, [])
                if required_keywords:
                    all_chunk_text = " ".join(c.text.lower() for c in chunks[:3])
                    has_required = any(kw in all_chunk_text for kw in required_keywords)
                    
                    if not has_required:
                        return GatingDecision(
                            decision=DecisionType.ABSTAIN,
                            reason=AbstainReason.MISSING_LEGAL_KEYWORD,
                            reason_detail=f"Query type '{qtype}' nhưng context thiếu keywords: {required_keywords}",
                            confidence=top1_score
                        )
        
        # ─────────────────────────────────────────────────────────────────────
        # Rule 5: Query ambiguity check
        # ─────────────────────────────────────────────────────────────────────
        
        needs_clarify, clarify_question = self.context_builder.needs_clarification(query)
        
        if needs_clarify and self.config.enable_ask_back:
            return GatingDecision(
                decision=DecisionType.ASK_BACK,
                reason=AbstainReason.AMBIGUOUS_QUERY,
                reason_detail="Query cần được làm rõ",
                confidence=top1_score,
                clarification_question=clarify_question
            )
        
        # ─────────────────────────────────────────────────────────────────────
        # Final decision
        # ─────────────────────────────────────────────────────────────────────
        
        if top1_score >= self.config.threshold_pass:
            return GatingDecision(
                decision=DecisionType.ANSWER,
                confidence=top1_score,
                reason_detail="Passed all checks"
            )
        elif top1_score >= self.config.threshold_cautious:
            return GatingDecision(
                decision=DecisionType.CAUTIOUS,
                reason_detail=f"Score ({top1_score:.2f}) trong khoảng cautious",
                confidence=top1_score
            )
        else:
            return GatingDecision(
                decision=DecisionType.ABSTAIN,
                reason=AbstainReason.LOW_CONFIDENCE,
                reason_detail=f"Score ({top1_score:.2f}) thấp hơn pass threshold",
                confidence=top1_score
            )
    
    def _generate_clarification_question(
        self,
        query: str,
        coverage_info: Dict
    ) -> str:
        """Generate câu hỏi làm rõ thông minh."""
        
        missing = coverage_info.get("missing", [])
        
        # Detect what type of info is missing
        location_keywords = ["tỉnh", "huyện", "xã", "địa phương", "thành phố"]
        time_keywords = ["năm", "tháng", "ngày", "khi", "thời điểm"]
        subject_keywords = ["ai", "đối tượng", "người", "tổ chức"]
        
        missing_lower = [m.lower() for m in missing]
        
        if any(kw in query.lower() for kw in location_keywords):
            return "Bạn đang hỏi về địa phương/khu vực nào cụ thể?"
        elif any(kw in query.lower() for kw in time_keywords):
            return "Bạn đang hỏi về thời điểm nào cụ thể?"
        elif any(kw in missing_lower for kw in subject_keywords):
            return "Bạn có thể cho biết đối tượng cụ thể được không?"
        else:
            return "Bạn có thể mô tả chi tiết hơn về câu hỏi?"
    
    def should_generate(self, decision: GatingDecision) -> bool:
        """Kiểm tra có nên gọi LLM để generate không."""
        return decision.decision in [DecisionType.ANSWER, DecisionType.CAUTIOUS]
    
    def build_gated_output(self, decision: GatingDecision) -> Optional[RAGOutput]:
        """
        Build RAGOutput nếu gating quyết định không cần LLM.
        
        Returns:
            RAGOutput nếu abstain/ask_back, None nếu cần generate
        """
        
        if decision.decision == DecisionType.ANSWER:
            return None  # Cần LLM generate
        
        if decision.decision == DecisionType.CAUTIOUS:
            return None  # Cần LLM generate với cảnh báo
        
        if decision.decision == DecisionType.ABSTAIN:
            return RAGOutput(
                answer=None,
                citations=[],
                decision=DecisionType.ABSTAIN,
                abstain=True,
                abstain_reason=decision.reason,
                reason_detail=decision.reason_detail,
                confidence_score=decision.confidence
            )
        
        if decision.decision == DecisionType.ASK_BACK:
            return RAGOutput(
                answer=None,
                citations=[],
                decision=DecisionType.ASK_BACK,
                abstain=True,
                abstain_reason=decision.reason,
                reason_detail=decision.reason_detail,
                clarification_question=decision.clarification_question,
                confidence_score=decision.confidence
            )
        
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# SCORE CALIBRATION
# ═══════════════════════════════════════════════════════════════════════════════

class ScoreCalibrator:
    """
    Calibrate cross-encoder scores để có thể so sánh across queries.
    """
    
    def __init__(self):
        self.score_history = []
        self.percentiles = {}
    
    def add_scores(self, scores: List[float]):
        """Add scores để học distribution."""
        self.score_history.extend(scores)
        self._update_percentiles()
    
    def _update_percentiles(self):
        """Update percentile thresholds."""
        if len(self.score_history) < 100:
            return
        
        sorted_scores = sorted(self.score_history)
        n = len(sorted_scores)
        
        self.percentiles = {
            "p10": sorted_scores[int(n * 0.10)],
            "p25": sorted_scores[int(n * 0.25)],
            "p50": sorted_scores[int(n * 0.50)],
            "p75": sorted_scores[int(n * 0.75)],
            "p90": sorted_scores[int(n * 0.90)],
        }
    
    def get_percentile(self, score: float) -> float:
        """Get percentile của một score."""
        if not self.score_history:
            return 0.5
        
        below = sum(1 for s in self.score_history if s < score)
        return below / len(self.score_history)
    
    def get_calibrated_config(self) -> GatingConfig:
        """Get GatingConfig calibrated theo score distribution."""
        if not self.percentiles:
            return GatingConfig()
        
        return GatingConfig(
            threshold_pass=self.percentiles.get("p75", 2.0),
            threshold_abstain=self.percentiles.get("p10", 0.5),
            threshold_cautious=self.percentiles.get("p50", 1.0),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def quick_gate(
    chunks: List[ChunkInfo],
    threshold: float = 0.5
) -> Tuple[bool, str]:
    """
    Quick gating check.
    
    Returns:
        (should_generate, reason)
    """
    if not chunks:
        return False, "No chunks available"
    
    top_score = chunks[0].score_rerank
    
    if top_score < threshold:
        return False, f"Top score ({top_score:.2f}) below threshold ({threshold})"
    
    return True, "Passed quick gate"


def compute_gating_metrics(
    decisions: List[GatingDecision],
    ground_truth_answerable: List[bool]
) -> Dict[str, float]:
    """
    Compute gating quality metrics.
    
    Metrics:
    - Abstain precision: abstain đúng lúc
    - Abstain recall: không bỏ sót difficult cases
    - Pass accuracy: pass đúng
    """
    
    if len(decisions) != len(ground_truth_answerable):
        raise ValueError("Decisions and ground truth must have same length")
    
    n = len(decisions)
    if n == 0:
        return {}
    
    # Categorize
    true_positives = 0   # Pass và answerable
    true_negatives = 0   # Abstain và not answerable
    false_positives = 0  # Pass nhưng not answerable (bad!)
    false_negatives = 0  # Abstain nhưng answerable
    
    for decision, is_answerable in zip(decisions, ground_truth_answerable):
        passed = decision.decision in [DecisionType.ANSWER, DecisionType.CAUTIOUS]
        
        if passed and is_answerable:
            true_positives += 1
        elif not passed and not is_answerable:
            true_negatives += 1
        elif passed and not is_answerable:
            false_positives += 1
        else:
            false_negatives += 1
    
    # Calculate metrics
    pass_precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    abstain_precision = true_negatives / (true_negatives + false_negatives) if (true_negatives + false_negatives) > 0 else 0
    
    total_abstains = sum(1 for d in decisions if d.decision in [DecisionType.ABSTAIN, DecisionType.ASK_BACK])
    abstain_rate = total_abstains / n
    
    return {
        "pass_precision": round(pass_precision, 4),
        "abstain_precision": round(abstain_precision, 4),
        "abstain_rate": round(abstain_rate, 4),
        "false_positive_rate": round(false_positives / n, 4),
        "true_positive_rate": round(true_positives / n, 4),
    }
