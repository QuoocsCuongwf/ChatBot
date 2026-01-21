"""
Parser.py - Module parse văn bản pháp luật
Simplified version - Tập trung vào độ chính xác
"""
import re

def clean_text(text):
    """Làm sạch text cơ bản"""
    # Xóa ký tự đặc biệt
    text = text.replace('\x0c', '').replace('\r', '')
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Tách dòng cho các cấu trúc
    # Chương
    text = re.sub(r'([^\n])\s*(Chương|CHƯƠNG)\s+([IVXLCDM\d]+)', r'\1\n\n\2 \3', text, flags=re.IGNORECASE)
    
    # Mục
    text = re.sub(r'([^\n])\s*(Mục|MỤC)\s+([IVXLCDM\d]+|[A-Z])', r'\1\n\n\2 \3', text, flags=re.IGNORECASE)
    
    # Điều
    text = re.sub(r'([.;])\s*(Điều|ĐIỀU)\s+(\d+)', r'\1\n\n\2 \3', text, flags=re.IGNORECASE)
    
    # Khoản (bảo vệ "Điều X.")
    text = re.sub(r'(Điều|ĐIỀU)\s+(\d+)\s*\.', r'<<<DIEU_\2>>>.', text)
    text = re.sub(r'([.;])\s+(\d+\.\s+[A-ZÀ-Ỹ])', r'\1\n\2', text)
    text = re.sub(r'<<<DIEU_(\d+)>>>\.', r'Điều \1.', text)
    
    # Điểm
    text = re.sub(r'([:;.])\s*([a-z])\)', r'\1\n\2)', text)
    
    return text.strip()

class SimpleParser:
    """Parser đơn giản chỉ parse Chương và Điều"""
    
    def __init__(self):
        self.result = {
            "metadata": {},
            "chuong": []
        }
        self.current_chuong = None
        self.current_dieu = None
        self.stop_parsing = False
    
    def parse(self, text):
        """Parse văn bản"""
        text = clean_text(text)
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or self.stop_parsing:
                continue
            
            # Dừng tại Phụ lục
            if re.match(r'^\s*(PHỤ\s+LỤC|BIỂU\s+MẪU|MẪU\s+SỐ|CỘNG\s+HÒA)', line, re.IGNORECASE):
                self.stop_parsing = True
                continue
            
            # Parse Chương
            if self._parse_chuong(line):
                continue
            
            # Parse Điều
            if self._parse_dieu(line):
                continue
            
            # Gom nội dung vào Điều hiện tại
            if self.current_dieu and not self.stop_parsing:
                if self.current_dieu.get("noi_dung"):
                    self.current_dieu["noi_dung"] += " " + line
                else:
                    self.current_dieu["noi_dung"] = line
        
        return self.result
    
    def _parse_chuong(self, line):
        """Parse Chương"""
        match = re.match(r'^(Chương|CHƯƠNG)\s+([IVXLCDM\d]+)\s*[-:.]?\s*(.*)$', line, re.IGNORECASE)
        if match:
            so = match.group(2).upper()
            ten = match.group(3).strip()
            
            # Validation: Chỉ chấp nhận I-XX
            if re.match(r'^[IVXLCDM]+$', so):
                try:
                    val = self._roman_to_int(so)
                    if val < 1 or val > 20:
                        return False
                except:
                    return False
            elif re.match(r'^\d+$', so):
                if int(so) > 20:
                    return False
            else:
                return False
            
            self.current_chuong = {
                "so_chuong": so,
                "ten_chuong": ten,
                "dieu": []
            }
            self.result["chuong"].append(self.current_chuong)
            self.current_dieu = None
            return True
        return False
    
    def _parse_dieu(self, line):
        """Parse Điều"""
        match = re.match(r'^(Điều|ĐIỀU)\s+(\d+)\s*[.:]?\s*(.*)$', line, re.IGNORECASE)
        if match:
            so = match.group(2)
            noi_dung = match.group(3).strip()
            
            # Validation: 1-999
            try:
                num = int(so)
                if num < 1 or num > 999:
                    return False
            except:
                return False
            
            # Phải có Chương
            if not self.current_chuong:
                return False
            
            self.current_dieu = {
                "so_dieu": so,
                "noi_dung": noi_dung,
                "khoan": []
            }
            self.current_chuong["dieu"].append(self.current_dieu)
            return True
        return False
    
    def _roman_to_int(self, s):
        """Chuyển số La Mã sang số nguyên"""
        vals = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        total = 0
        prev = 0
        for c in reversed(s):
            val = vals.get(c, 0)
            if val < prev:
                total -= val
            else:
                total += val
            prev = val
        return total

def parse_legal_document(text):
    """Hàm main để parse văn bản"""
    parser = SimpleParser()
    return parser.parse(text)
