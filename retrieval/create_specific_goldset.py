"""
Script tạo bộ goldset với câu hỏi cụ thể, liên quan đến nội dung thực tế
của văn bản pháp luật, không phải câu hỏi template chung chung.
"""
import json
import random
import re

def load_metadata(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_key_content(text):
    """Trích xuất nội dung quan trọng từ text"""
    # Loại bỏ prefix như "Theo Điều X", "Khoản Y Điều Z"
    text = re.sub(r'^(Theo |Khoản \d+ )?Điều \d+\s*', '', text)
    text = re.sub(r'^Khoản \d+\s*', '', text)
    return text.strip()

def generate_specific_questions(chunks):
    """Tạo câu hỏi cụ thể dựa trên nội dung thực tế"""
    goldset = []
    question_id = 1
    
    # Patterns để tạo câu hỏi dựa trên nội dung
    question_patterns = {
        "phạm vi điều chỉnh": "Phạm vi điều chỉnh của {van_ban} là gì?",
        "nguyên tắc": "Nguyên tắc {content_key} được quy định như thế nào?",
        "thẩm quyền": "Thẩm quyền của {subject} trong {topic} được quy định ra sao?",
        "trách nhiệm": "Trách nhiệm của {subject} theo quy định là gì?",
        "điều kiện": "Điều kiện để {action} là gì?",
        "thủ tục": "Thủ tục {action} được thực hiện như thế nào?",
        "hồ sơ": "Hồ sơ {action} gồm những gì?",
        "thời hạn": "Thời hạn {action} là bao lâu?",
        "hiệu lực": "{van_ban} có hiệu lực từ khi nào?",
    }
    
    seen_questions = set()
    
    for chunk in chunks:
        text = chunk.get("text", "")
        meta = chunk.get("metadata", {})
        van_ban = meta.get("van_ban", "")
        dieu = meta.get("dieu", "")
        khoan = meta.get("khoan")
        
        if not text or not van_ban or not dieu:
            continue
            
        content = extract_key_content(text)
        content_lower = content.lower()
        
        question = None
        
        # Tạo câu hỏi cụ thể dựa trên nội dung
        if "phạm vi điều chỉnh" in content_lower:
            question = f"Phạm vi điều chỉnh của {van_ban} là gì?"
            
        elif "có hiệu lực" in content_lower or "hiệu lực thi hành" in content_lower:
            question = f"{van_ban} có hiệu lực thi hành từ khi nào?"
            
        elif "nguyên tắc" in content_lower and "bảo đảm" in content_lower:
            # Trích xuất nguyên tắc cụ thể
            if "quyền con người" in content_lower:
                question = f"Nguyên tắc bảo đảm quyền con người trong {van_ban} được quy định thế nào?"
            elif "công khai" in content_lower or "minh bạch" in content_lower:
                question = f"Nguyên tắc công khai, minh bạch theo {van_ban} được quy định ra sao?"
            elif "phân định" in content_lower:
                question = f"Nguyên tắc phân định thẩm quyền theo {van_ban} là gì?"
                
        elif "thẩm quyền" in content_lower:
            # Trích xuất chủ thể có thẩm quyền
            subjects = []
            if "thủ tướng" in content_lower:
                subjects.append("Thủ tướng Chính phủ")
            if "bộ trưởng" in content_lower:
                subjects.append("Bộ trưởng")
            if "chủ tịch" in content_lower and "ủy ban nhân dân" in content_lower:
                subjects.append("Chủ tịch UBND")
            if "ủy ban nhân dân" in content_lower:
                subjects.append("UBND")
            if "hội đồng nhân dân" in content_lower:
                subjects.append("HĐND")
                
            if subjects:
                subject = subjects[0]
                question = f"Thẩm quyền của {subject} theo {van_ban} là gì?"
                
        elif "trách nhiệm" in content_lower:
            if "bộ" in content_lower and "ngành" in content_lower:
                question = f"Trách nhiệm của các bộ, ngành theo {van_ban}?"
            elif "địa phương" in content_lower:
                question = f"Trách nhiệm của chính quyền địa phương theo {van_ban}?"
                
        elif "hồ sơ" in content_lower:
            if "đăng ký" in content_lower:
                question = f"Hồ sơ đăng ký theo {van_ban} gồm những gì?"
            elif "cấp phép" in content_lower:
                question = f"Hồ sơ xin cấp phép theo {van_ban} bao gồm gì?"
                
        elif "thời hạn" in content_lower or re.search(r'\d+\s*(ngày|tháng|năm)', content_lower):
            if "giải quyết" in content_lower:
                question = f"Thời hạn giải quyết theo {van_ban} là bao lâu?"
            elif "hiệu lực" in content_lower:
                question = f"Thời hạn hiệu lực theo {van_ban} là bao lâu?"
                
        elif "điều kiện" in content_lower:
            if "hoạt động" in content_lower:
                question = f"Điều kiện hoạt động theo {van_ban} là gì?"
            elif "đăng ký" in content_lower:
                question = f"Điều kiện đăng ký theo {van_ban} là gì?"
                
        elif "cơ quan" in content_lower and ("chức năng" in content_lower or "nhiệm vụ" in content_lower):
            question = f"Chức năng, nhiệm vụ của cơ quan theo {van_ban}?"
            
        elif "xử phạt" in content_lower or "vi phạm" in content_lower:
            question = f"Quy định xử lý vi phạm theo {van_ban}?"
            
        elif "chuyển tiếp" in content_lower:
            question = f"Điều khoản chuyển tiếp của {van_ban} quy định gì?"
            
        elif "đối tượng áp dụng" in content_lower:
            question = f"Đối tượng áp dụng của {van_ban} gồm những ai?"
            
        elif "quản lý" in content_lower and "nhà nước" in content_lower:
            if "tài chính" in content_lower:
                question = f"Quy định quản lý nhà nước về tài chính theo {van_ban}?"
            elif "y tế" in content_lower:
                question = f"Quy định quản lý nhà nước về y tế theo {van_ban}?"
            elif "giáo dục" in content_lower:
                question = f"Quy định quản lý nhà nước về giáo dục theo {van_ban}?"
            elif "nông nghiệp" in content_lower:
                question = f"Quy định quản lý nhà nước về nông nghiệp theo {van_ban}?"
                
        elif "phân cấp" in content_lower or "phân quyền" in content_lower:
            question = f"Nội dung phân cấp, phân quyền theo {van_ban} tại Điều {dieu}?"
            
        # Nếu có câu hỏi và chưa trùng
        if question and question not in seen_questions:
            seen_questions.add(question)
            
            entry = {
                "qid": f"Q{question_id:03d}",
                "question": question,
                "ground_truth": [{
                    "van_ban": van_ban,
                    "dieu": dieu,
                    "khoan": khoan
                }]
            }
            goldset.append(entry)
            question_id += 1
            
            # Giới hạn số câu hỏi
            if question_id > 200:
                break
    
    return goldset

def generate_from_templates_smart(chunks):
    """Tạo câu hỏi từ templates nhưng dựa trên nội dung cụ thể"""
    goldset = []
    question_id = 1
    
    # Lọc các chunks có nội dung quan trọng
    important_chunks = []
    for chunk in chunks:
        text = chunk.get("text", "").lower()
        meta = chunk.get("metadata", {})
        
        # Chỉ chọn chunks có nội dung thực sự quan trọng
        important_keywords = [
            "phạm vi điều chỉnh", "đối tượng áp dụng", "nguyên tắc",
            "thẩm quyền", "trách nhiệm", "điều kiện", "hồ sơ", 
            "thủ tục", "thời hạn", "hiệu lực", "xử phạt", "vi phạm",
            "chuyển tiếp", "quy định chung", "thi hành"
        ]
        
        if any(kw in text for kw in important_keywords):
            important_chunks.append(chunk)
    
    return important_chunks

def main():
    # Load metadata
    metadata_path = "d:/GitHub/ChatBot/vector_data/legal_hf/metadata.json"
    print(f"Loading metadata from {metadata_path}...")
    chunks = load_metadata(metadata_path)
    print(f"Loaded {len(chunks)} chunks")
    
    # Generate goldset
    print("Generating specific questions...")
    goldset = generate_specific_questions(chunks)
    print(f"Generated {len(goldset)} specific questions")
    
    # Save goldset
    output_path = "d:/GitHub/ChatBot/retrieval/gold_specific.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in goldset:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"Saved goldset to {output_path}")
    
    # Show sample
    print("\nSample questions:")
    for entry in goldset[:10]:
        print(f"  {entry['qid']}: {entry['question']}")

if __name__ == "__main__":
    main()
