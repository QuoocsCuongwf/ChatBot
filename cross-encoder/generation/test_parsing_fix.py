import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(r"d:\GitHub\Folder cha\ChatBot\cross-encoder\generation")
sys.path.append(str(project_root))

from rag_contract import parse_rag_output, Citation, DecisionType

def test_json_parsing():
    print("Testing JSON parsing...")
    
    # Test case 1: Standard JSON
    raw_json = '{"answer": "Test answer", "citations": [{"van_ban": "VB1", "dieu": "1"}], "abstain": false}'
    output = parse_rag_output(raw_json)
    print(f"Case 1: answer='{output.answer}', citations={len(output.citations)}, abstain={output.abstain}")
    assert output.answer == "Test answer"
    assert len(output.citations) == 1
    assert not output.abstain

    # Test case 2: JSON with refusal
    raw_refusal = '{"refusal": "I cannot answer this."}'
    output = parse_rag_output(raw_refusal)
    print(f"Case 2: answer='{output.answer}', citations={len(output.citations)}, abstain={output.abstain}")
    assert output.abstain == True
    assert output.answer == "I cannot answer this."

    # Test case 3: JSON embedded in markdown
    raw_md = "Here is the result:\n```json\n" + raw_json + "\n```"
    output = parse_rag_output(raw_md)
    print(f"Case 3: answer='{output.answer}', citations={len(output.citations)}, abstain={output.abstain}")
    assert output.answer == "Test answer"

    # Test case 6: Junk prefix (quote-colon-quote)
    raw_junk = '": {"answer": "Clean answer", "abstain": false}'
    output = parse_rag_output(raw_junk)
    print(f"Case 6: answer='{output.answer}', abstain={output.abstain}")
    assert output.answer == "Clean answer"

    # Test 3: Broken JSON prefix (seen in UI)
    broken_json = '": null, "citations": [], "abstain": true, "reason": "Context không đủ thông tin để trả lời"}'
    output = parse_rag_output(broken_json)
    print(f"\nTest 3 (Broken JSON prefix):")
    print(f"Abstain: {output.abstain}")
    print(f"Answer: {output.answer}")
    assert output.abstain is True
    assert "Context không đủ thông tin" in output.answer

    # Test case 9: Empty JSON citations should fall back to text
    raw_empty_json_cits = '{"answer": "Theo Điều 5 của Nghị định XYZ...", "citations": [{}, {}]}'
    output = parse_rag_output(raw_empty_json_cits)
    print(f"Case 9: citations={len(output.citations)}, first={output.citations[0].to_str() if output.citations else 'NONE'}")
    assert len(output.citations) >= 1
    assert "Điều 5" in output.citations[0].to_str()

def test_natural_text_parsing():
    print("\nTesting natural text parsing...")
    
    # Test case 4: Natural text with citations (Standard order)
    raw_text = """
    Kết luận: Đây là câu trả lời.
    Trích dẫn:
    Theo Điều 5 và Khoản 2 Điều 8 của Nghị định ABC.
    """
    output = parse_rag_output(raw_text)
    print(f"Case 4: answer='{output.answer}', citations={[(c.dieu, c.khoan) for c in output.citations]}")
    assert "Đây là câu trả lời" in output.answer
    dies = [c.dieu for c in output.citations]
    assert "5" in dies
    assert "8" in dies

    # Test case 8: Structured Markdown answer
    raw_structured = """
    {"answer": "### Nguyên tắc\\nTheo Điều 73 Khoản 1 của Nghị định, việc phân cấp quản lý...\\n\\n### Chủ thể\\nTheo Điều 74 của Nghị định, UBND cấp tỉnh chịu trách nhiệm...", "citations": [], "abstain": false}
    """
    output = parse_rag_output(raw_structured)
    print(f"Case 8: answer has headings: {'###' in output.answer}")
    assert "### Nguyên tắc" in output.answer
    assert "### Chủ thể" in output.answer

    # Test case 5: Explicit abstain in natural text
    raw_abstain = "Tôi không tìm thấy quy định nào liên quan đến vấn đề này trong context."
    output = parse_rag_output(raw_abstain)
    print(f"Case 5: abstain={output.abstain}, reason='{output.reason_detail}'")
    assert output.abstain == True

if __name__ == "__main__":
    try:
        test_json_parsing()
        test_natural_text_parsing()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
