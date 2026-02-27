"""
prompt_templates.py — Legal-Grounded Prompts với bắt buộc trích dẫn

3 Luật cứng:
1. Chỉ dùng thông tin trong context
2. Mỗi ý pháp lý phải có trích dẫn (Điều/Khoản)
3. Nếu context không đủ → abstain hoặc hỏi lại

Format trả lời:
- Kết luận ngắn
- Căn cứ pháp lý (Điều… Khoản…)
- Giải thích ngắn theo đúng đoạn context
- Trích dẫn (liệt kê)
"""

from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum


class PromptStyle(Enum):
    """Phong cách prompt."""
    STRUCTURED_JSON = "structured_json"      # Output JSON có cấu trúc
    NATURAL_VI = "natural_vi"                # Output tiếng Việt tự nhiên
    CONCISE = "concise"                      # Ngắn gọn, súc tích
    DETAILED = "detailed"                    # Chi tiết, đầy đủ


@dataclass
class PromptConfig:
    """Cấu hình prompt."""
    style: PromptStyle = PromptStyle.STRUCTURED_JSON
    max_answer_length: int = 500
    require_json_output: bool = True
    include_examples: bool = True
    language: str = "vi"


class LegalPromptBuilder:
    """
    Builder cho Legal-Grounded Prompts.
    
    Đảm bảo:
    - LLM chỉ dùng thông tin trong context
    - Bắt buộc trích dẫn điều/khoản
    - Abstain khi không đủ căn cứ
    """
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM PROMPTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    SYSTEM_PROMPT_VI = """Bạn là trợ lý pháp lý chuyên về văn bản quy phạm pháp luật Việt Nam.

## LUẬT BẮT BUỘC:
1. **CHỈ dùng thông tin trong CONTEXT được cung cấp** - KHÔNG được suy diễn, bịa đặt, hoặc dùng kiến thức bên ngoài.
2. **MỖI ý pháp lý PHẢI có trích dẫn** cụ thể (Điều, Khoản, Điểm).
3. **Nếu context KHÔNG ĐỦ căn cứ** để trả lời → phải trả về abstain=true.

## QUY TẮC TRÍCH DẪN:
- Format: "Theo Điều X, Khoản Y, Điểm Z của [Tên văn bản]..."
- Mỗi thông tin pháp lý phải kèm nguồn
- KHÔNG được tự tạo điều khoản không có trong context

## CẢNH BÁO:
- KHÔNG suy diễn luật
- KHÔNG kết hợp các điều khoản theo cách không được quy định
- KHÔNG trả lời nếu context không chứa thông tin liên quan đến câu hỏi"""

    SYSTEM_PROMPT_EN = """You are a legal assistant specializing in Vietnamese legal documents.

## MANDATORY RULES:
1. ONLY use information from the provided CONTEXT - NO inference, fabrication, or external knowledge.
2. EVERY legal statement MUST have a citation (Điều/Khoản/Điểm).
3. If context is INSUFFICIENT → return abstain=true.

## CITATION FORMAT:
- "Theo Điều X, Khoản Y, Điểm Z của [Document name]..."
- Every legal information must have source
- DO NOT create articles/clauses not in context"""

    # ═══════════════════════════════════════════════════════════════════════════
    # OUTPUT FORMATS
    # ═══════════════════════════════════════════════════════════════════════════
    
    OUTPUT_FORMAT_JSON = """## FORMAT TRẢ LỜI (JSON):
```json
{
  "answer": "Câu trả lời ngắn gọn, súc tích",
  "citations": [
    {
      "van_ban": "Tên văn bản",
      "dieu": "số điều",
      "khoan": "số khoản (nếu có)",
      "diem": "điểm (nếu có)",
      "noi_dung": "Trích dẫn nguyên văn từ context"
    }
  ],
  "abstain": false,
  "reason": null
}
```

Nếu KHÔNG ĐỦ căn cứ:
```json
{
  "answer": null,
  "citations": [],
  "abstain": true,
  "reason": "Không tìm thấy quy định liên quan trong context"
}
```"""

    OUTPUT_FORMAT_NATURAL = """## FORMAT TRẢ LỜI:

**Kết luận:** [Trả lời ngắn gọn]

**Căn cứ pháp lý:**
- Điều X, Khoản Y: [nội dung]
- Điều Z: [nội dung]

**Giải thích:** [Giải thích dựa trên context]

**Trích dẫn:**
1. [Tên văn bản] - Điều X, Khoản Y
2. ...

Nếu KHÔNG ĐỦ căn cứ, trả lời:
"Tôi không tìm thấy quy định cụ thể trong các văn bản được cung cấp để trả lời câu hỏi này."
"""

    # ═══════════════════════════════════════════════════════════════════════════
    # EXAMPLES
    # ═══════════════════════════════════════════════════════════════════════════
    
    EXAMPLE_GOOD = """## VÍ DỤ TRẢ LỜI ĐÚNG:

Câu hỏi: "Ai có thẩm quyền quyết định việc cưỡng chế phá dỡ công trình?"

Context:
[1] [VB: Nghị định về xây dựng, Chương II, Điều 8, Khoản 2]
Chủ tịch Ủy ban nhân dân cấp huyện quyết định cưỡng chế phá dỡ công trình xây dựng vi phạm trên địa bàn.

Trả lời:
```json
{
  "answer": "Chủ tịch Ủy ban nhân dân cấp huyện có thẩm quyền quyết định việc cưỡng chế phá dỡ công trình xây dựng vi phạm trên địa bàn.",
  "citations": [
    {
      "van_ban": "Nghị định về xây dựng",
      "dieu": "8",
      "khoan": "2",
      "diem": null,
      "noi_dung": "Chủ tịch Ủy ban nhân dân cấp huyện quyết định cưỡng chế phá dỡ công trình xây dựng vi phạm trên địa bàn"
    }
  ],
  "abstain": false,
  "reason": null
}
```"""

    EXAMPLE_ABSTAIN = """## VÍ DỤ ABSTAIN ĐÚNG CÁCH:

Câu hỏi: "Mức phí cấp giấy phép xây dựng là bao nhiêu?"

Context:
[1] [VB: Nghị định về xây dựng, Chương II, Điều 5]
Hồ sơ đề nghị cấp giấy phép xây dựng bao gồm đơn đề nghị, bản vẽ thiết kế...

Trả lời:
```json
{
  "answer": null,
  "citations": [],
  "abstain": true,
  "reason": "Context chỉ cung cấp thông tin về hồ sơ đề nghị cấp phép, không có quy định về mức phí"
}
```"""

    # ═══════════════════════════════════════════════════════════════════════════
    # PROMPT BUILDERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def __init__(self, config: Optional[PromptConfig] = None):
        self.config = config or PromptConfig()
    
    def build_system_prompt(self) -> str:
        """Build system prompt."""
        base = self.SYSTEM_PROMPT_VI if self.config.language == "vi" else self.SYSTEM_PROMPT_EN
        
        # Add output format
        if self.config.require_json_output:
            base += "\n\n" + self.OUTPUT_FORMAT_JSON
        else:
            base += "\n\n" + self.OUTPUT_FORMAT_NATURAL
        
        # Add examples
        if self.config.include_examples:
            base += "\n\n" + self.EXAMPLE_GOOD
            base += "\n\n" + self.EXAMPLE_ABSTAIN
        
        return base
    
    def build_user_prompt(
        self,
        question: str,
        context: str,
        additional_instructions: Optional[str] = None
    ) -> str:
        """Build user prompt với question và context."""
        
        prompt = f"""## CONTEXT (Các đoạn văn bản pháp lý):
{context}

## CÂU HỎI:
{question}

## YÊU CẦU:
- Trả lời dựa TRÊN VÀ CHỈ DỰA TRÊN context ở trên
- Trích dẫn cụ thể Điều/Khoản/Điểm
- Nếu context không đủ thông tin → abstain=true"""
        
        if additional_instructions:
            prompt += f"\n\n## CHỈ DẪN BỔ SUNG:\n{additional_instructions}"
        
        if self.config.require_json_output:
            prompt += "\n\n## TRẢ LỜI (JSON):"
        else:
            prompt += "\n\n## TRẢ LỜI:"
        
        return prompt
    
    def build_full_prompt(
        self,
        question: str,
        context: str,
        include_system: bool = True
    ) -> str:
        """Build full prompt (system + user)."""
        
        if include_system:
            system = self.build_system_prompt()
            user = self.build_user_prompt(question, context)
            return f"{system}\n\n---\n\n{user}"
        else:
            return self.build_user_prompt(question, context)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CHAT FORMAT BUILDERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def build_chat_messages(
        self,
        question: str,
        context: str
    ) -> List[Dict[str, str]]:
        """Build messages cho chat-based LLMs."""
        return [
            {"role": "system", "content": self.build_system_prompt()},
            {"role": "user", "content": self.build_user_prompt(question, context)}
        ]
    
    def build_llama_prompt(
        self,
        question: str,
        context: str
    ) -> str:
        """Build prompt cho Llama format."""
        system = self.build_system_prompt()
        user = self.build_user_prompt(question, context)
        
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
    
    def build_mistral_prompt(
        self,
        question: str,
        context: str
    ) -> str:
        """Build prompt cho Mistral format."""
        system = self.build_system_prompt()
        user = self.build_user_prompt(question, context)
        
        return f"""<s>[INST] {system}

{user} [/INST]"""

    def build_chatml_prompt(
        self,
        question: str,
        context: str
    ) -> str:
        """Build prompt cho ChatML format (nhiều model support)."""
        system = self.build_system_prompt()
        user = self.build_user_prompt(question, context)
        
        return f"""<|im_start|>system
{system}<|im_end|>
<|im_start|>user
{user}<|im_end|>
<|im_start|>assistant
"""


# ═══════════════════════════════════════════════════════════════════════════════
# SPECIALIZED PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

class SpecializedPrompts:
    """Prompts chuyên biệt cho các loại câu hỏi pháp lý."""
    
    @staticmethod
    def definition_prompt(term: str, context: str) -> str:
        """Prompt cho câu hỏi định nghĩa."""
        return f"""## CONTEXT:
{context}

## CÂU HỎI:
"{term}" được định nghĩa như thế nào theo quy định pháp luật?

## YÊU CẦU:
1. Tìm định nghĩa chính xác trong context
2. Trích dẫn Điều/Khoản chứa định nghĩa
3. Nếu không có định nghĩa → abstain

## TRẢ LỜI (JSON):"""
    
    @staticmethod
    def procedure_prompt(procedure: str, context: str) -> str:
        """Prompt cho câu hỏi thủ tục."""
        return f"""## CONTEXT:
{context}

## CÂU HỎI:
Thủ tục "{procedure}" được thực hiện như thế nào?

## YÊU CẦU:
1. Liệt kê các bước theo trình tự (nếu có trong context)
2. Trích dẫn Điều/Khoản cho mỗi bước
3. Nếu context thiếu thông tin → abstain

## TRẢ LỜI (JSON):"""
    
    @staticmethod
    def authority_prompt(action: str, context: str) -> str:
        """Prompt cho câu hỏi thẩm quyền."""
        return f"""## CONTEXT:
{context}

## CÂU HỎI:
Ai có thẩm quyền {action}?

## YÊU CẦU:
1. Xác định cơ quan/cá nhân có thẩm quyền từ context
2. Trích dẫn Điều/Khoản quy định thẩm quyền
3. Nếu không rõ → abstain

## TRẢ LỜI (JSON):"""


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

def validate_prompt_length(prompt: str, max_tokens: int = 4096) -> Dict[str, any]:
    """Validate prompt không vượt quá token limit."""
    # Rough estimate: ~1.5 chars per token cho Vietnamese
    estimated_tokens = int(len(prompt) / 1.5)
    
    return {
        "prompt_length": len(prompt),
        "estimated_tokens": estimated_tokens,
        "max_tokens": max_tokens,
        "is_valid": estimated_tokens <= max_tokens,
        "overflow": max(0, estimated_tokens - max_tokens)
    }
