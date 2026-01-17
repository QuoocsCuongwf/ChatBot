import re

# ==============================================================================
# CÁC HÀM XỬ LÝ VĂN BẢN (TEXT POST-PROCESSING)
# ==============================================================================

def normalize_text(text):
    """Chuẩn hóa văn bản cơ bản"""
    text = text.replace("\r", "")
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# Từ điển sửa lỗi OCR mở rộng cho tiếng Việt pháp luật
VIETNAMESE_OCR_FIXES = {
    # === Lỗi quy/qủy - phổ biến nhất ===
    "qủy": "quy", "Qủy": "Quy",
    "qủyết": "quyết", "Qủyết": "Quyết",
    "qủyền": "quyền", "Qủyền": "Quyền",
    "qủyển": "quyền", "qủyện": "quyền",
    "dủyệt": "duyệt", "Dủyệt": "Duyệt",
    "ngủyện": "nguyện", "Ngủyện": "Nguyện",
    "chủyển": "chuyển", "Chủyển": "Chuyển",
    "chủyền": "chuyển", "chủyên": "chuyển",
    "ngủyên": "nguyên", "Ngủyên": "Nguyên",
    
    # === Lỗi dấu phổ biến ===
    "quyên": "quyền", "Quyên": "Quyền",
    "quyển": "quyền", "Quyển": "Quyền",
    "thâm": "thẩm", "Thâm": "Thẩm",
    "quần": "quản", "Quần": "Quản",
    "chinh": "chính", "Chinh": "Chính",
    "chíh": "chính", "Chíh": "Chính",
    "đinh": "định", "Đinh": "Định",
    "trịnh": "trình", "Trịnh": "Trình",
    "trinh": "trình", "Trinh": "Trình",
    
    # === Lỗi nguyên âm ===
    "tài sắn": "tài sản", "Tài sắn": "Tài sản",
    "tài sảri": "tài sản",
    "săn": "sản", "Săn": "Sản",
    "sắn": "sản", "Sắn": "Sản",
    "phẩn": "phân", "Phẩn": "Phân",
    "hạ tằng": "hạ tầng", "hạ tâng": "hạ tầng",
    "kêt": "kết", "Kêt": "Kết",
    "sô": "số", "Sô": "Số",
    "địa bản": "địa bàn",
    
    # === Lỗi phụ âm ===
    "Hiên": "Hiến", "hiên": "hiến",
    "tặc": "tắc", "Tặc": "Tắc",
    "nguyên tặc": "nguyên tắc",
    "quộc": "quốc", "Quộc": "Quốc",
    "điêu": "điều", "Điêu": "Điều",
    "Dicu": "Điều", "Diêu": "Điều", "Đicu": "Điều",
    
    # === Lỗi số La Mã - QUAN TRỌNG ===
    "Chương J ": "Chương I ", "CHƯƠNG J ": "CHƯƠNG I ",
    "Chương JI": "Chương II", "CHƯƠNG JI": "CHƯƠNG II",
    "Chương JII": "Chương III", "CHƯƠNG JII": "CHƯƠNG III",
    "Chương JV": "Chương IV", "CHƯƠNG JV": "CHƯƠNG IV",
    "Chương V ": "Chương V ",
    # Lỗi II bị nhận sai thành H
    "Chương H": "Chương II", "CHƯƠNG H": "CHƯƠNG II",
    # Lỗi III bị nhận sai
    "mm „Chương II": "Chương III", "mm „CHƯƠNG II": "CHƯƠNG III",
    "mm Chương II": "Chương III", "mm CHƯƠNG II": "CHƯƠNG III",
    "Chương II mm": "Chương III", "CHƯƠNG II mm": "CHƯƠNG III",
    "Chương II M": "Chương III", "CHƯƠNG II M": "CHƯƠNG III",
    "Chương IIm": "Chương III", "CHƯƠNG IIm": "CHƯƠNG III",
    "Chương m": "Chương III", "CHƯƠNG m": "CHƯƠNG III",
    "Chương M": "Chương III", "CHƯƠNG M": "CHƯƠNG III",
    "Chương lII": "Chương III", "CHƯƠNG lII": "CHƯƠNG III",
    "Chương lll": "Chương III", "CHƯƠNG lll": "CHƯƠNG III",
    "Chương IlI": "Chương III", "CHƯƠNG IlI": "CHƯƠNG III",
    "Chương Ill": "Chương III", "CHƯƠNG Ill": "CHƯƠNG III",
    "Chương 1I": "Chương II", "Chương I1": "Chương II",
    "Chương 1II": "Chương III", "Chương II1": "Chương III",
    "Mục J": "Mục I", "MỤC J": "MỤC I",
    
    # === Lỗi tiêu đề ===
    "QUY ĐÌNH CHÚNG": "QUY ĐỊNH CHUNG",
    "QUY ĐINH CHUNG": "QUY ĐỊNH CHUNG",
    "QUẦN LÝ": "QUẢN LÝ",
    "NGH! D!NH": "NGHỊ ĐỊNH",
    "PHÁN CÁP": "PHÂN CẤP",
    "TÀI SẲN": "TÀI SẢN",
    "TỎ CHỨC": "TỔ CHỨC",
    
    # === Lỗi từ ghép phổ biến ===
    "nhà nuóc": "nhà nước", "Nhà nuóc": "Nhà nước",
    "chính quyên": "chính quyền", 
    "địa phuong": "địa phương",
    "nhiêm vụ": "nhiệm vụ",
    "thục hiện": "thực hiện", "thực hiên": "thực hiện",
    "quy đinh": "quy định",
    "hội đông": "hội đồng",
    "tô chức": "tổ chức", "tồ chức": "tổ chức",
    "xử bý": "xử lý",
    "bồ sung": "bổ sung",
    "sửa đôi": "sửa đổi",
    "phạm ví": "phạm vi", "phạn vi": "phạm vi",
    "đối tuợng": "đối tượng",
    "chiên lược": "chiến lược",
    "kiêm tra": "kiểm tra", "kiếm tra": "kiểm tra",
    "vỉ phạm": "vi phạm",
    "tải sản": "tài sản",
    "hiệu lục": "hiệu lực",
    "trực thuôc": "trực thuộc",
    "ảnh hướng": "ảnh hưởng",
    "kết cầu": "kết cấu", "kệt cấu": "kết cấu",
    "quân lý": "quản lý", "quán lý": "quản lý",
    "Thú tướng": "Thủ tướng",
    "Thú trưởng": "Thủ trưởng",
    "nhârí": "nhân",
    "sửdụng": "sử dụng",
    "đôi với": "đối với",
    "đôivới": "đối với",
    "chỉtiết": "chi tiết",
    "chỉ tiêt": "chi tiết",
    "điều chuyền": "điều chuyển",
    "chông lân": "chồng lấn",
    "chông chéo": "chồng chéo",
    "thông nhât": "thống nhất",
    "thông nhất": "thống nhất",
    "đông bộ": "đồng bộ",
    "tông thê": "tổng thể",
    "Uy ban": "Ủy ban",
    "Tô chức": "Tổ chức",
    
    # === Ký tự đặc biệt/nhiễu ===
    "  ": " ",
}


def fix_vietnamese_ocr_errors(text):
    """Sửa các lỗi chính tả phổ biến do OCR"""
    # 1. Áp dụng từ điển sửa lỗi
    for error, fix in VIETNAMESE_OCR_FIXES.items():
        text = text.replace(error, fix)
    
    # 2. Sửa lỗi số 1 bị nhận thành 'l' hoặc 'I'
    text = re.sub(r'\n[lI]\.\s', '\n1. ', text)
    text = re.sub(r'^[lI]\.\s', '1. ', text, flags=re.MULTILINE)
    
    # 3. Sửa lỗi số điều
    text = re.sub(r'Điều\s+l([.\s])', r'Điều 1\1', text)
    text = re.sub(r'Điều\s+I([.\s])', r'Điều 1\1', text)
    
    # 4. Xóa ký tự nhiễu
    text = re.sub(r'[|¬~`¡„€•\[\]{}ũ]', '', text)
    
    # 5. Gộp từ bị ngắt dòng
    text = re.sub(r'-\s*\n\s*', '', text)
    
    # 6. Chuẩn hóa khoảng trắng
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\s+([.,;:])', r'\1', text)
    
    # 7. Sửa số la mã Chương - xử lý các lỗi OCR phổ biến
    # Pattern mm trước Chương II là dấu hiệu của Chương III bị nhận sai
    text = re.sub(r'mm\s*[„"\'"]?\s*(Chương|CHƯƠNG)\s+II\b', r'\1 III', text, flags=re.IGNORECASE)
    text = re.sub(r'(Chương|CHƯƠNG)\s+II\s*mm?\b', r'\1 III', text, flags=re.IGNORECASE)
    text = re.sub(r'(Chương|CHƯƠNG)\s+II\s*M\b', r'\1 III', text, flags=re.IGNORECASE)
    text = re.sub(r'(Chương|CHƯƠNG)\s+m\b', r'\1 III', text, flags=re.IGNORECASE)
    text = re.sub(r'(Chương|CHƯƠNG)\s+M\b', r'\1 III', text, flags=re.IGNORECASE)
    text = re.sub(r'(Chương|CHƯƠNG)\s+H\b', r'\1 II', text, flags=re.IGNORECASE)
    text = re.sub(r'(Chương|CHƯƠNG)\s+lII\b', r'\1 III', text, flags=re.IGNORECASE)
    text = re.sub(r'(Chương|CHƯƠNG)\s+IlI\b', r'\1 III', text, flags=re.IGNORECASE)
    text = re.sub(r'(Chương|CHƯƠNG)\s+Ill\b', r'\1 III', text, flags=re.IGNORECASE)
    text = re.sub(r'(Chương|CHƯƠNG)\s+lll\b', r'\1 III', text, flags=re.IGNORECASE)
    text = re.sub(r'(Chương|CHƯƠNG)\s+JI\b', r'\1 II', text, flags=re.IGNORECASE)
    text = re.sub(r'(Chương|CHƯƠNG)\s+J([^a-zA-Z])', r'\1 I\2', text, flags=re.IGNORECASE)
    
    # Xóa ký tự nhiễu trước Chương
    text = re.sub(r'[|Ñ„"\'—\-]+\s*(Chương|CHƯƠNG)', r'\n\1', text, flags=re.IGNORECASE)
    
    return text


def apply_context_aware_fixes(text):
    """Sửa lỗi OCR theo ngữ cảnh pháp luật"""
    patterns = [
        (r'Ủy ban nhân dàn', 'Ủy ban nhân dân'),
        (r'Hội đông nhân dân', 'Hội đồng nhân dân'),
        (r'Quôc hội', 'Quốc hội'),
        (r'Chính phù', 'Chính phủ'),
        (r'Nghị đinh', 'Nghị định'),
        (r'Quyêt định', 'Quyết định'),
        (r'Thông tu', 'Thông tư'),
        (r'Luât', 'Luật'),
        (r'trình tụ', 'trình tự'),
        (r'thủ tuc', 'thủ tục'),
        (r'phân câp', 'phân cấp'),
        (r'Bộ truởng', 'Bộ trưởng'),
        (r'Thủ tuớng', 'Thủ tướng'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def clean_text(text):
    """Áp dụng tất cả bước làm sạch văn bản."""
    text = normalize_text(text)
    text = fix_vietnamese_ocr_errors(text)
    text = apply_context_aware_fixes(text)
    
    # Thêm xuống dòng trước Chương
    text = re.sub(r'([^\n])\s+(Chương|CHƯƠNG)\s+([IVXLCDM\d]+)', 
                  r'\1\n\n\2 \3', text, flags=re.IGNORECASE)
    
    # Thêm xuống dòng trước Điều (không phải tham chiếu)
    # Bảo vệ tham chiếu kiểu "tại Điều X", "theo Điều X", "quy định tại Điều X"
    ref_pattern = r'(tại|theo|của|số|khoản\s*\d+)\s+(Điều|ĐIỀU)\s+(\d+)'
    text = re.sub(ref_pattern, r'\1 <<<REF>>>\2 \3', text, flags=re.IGNORECASE)
    
    # Bảo vệ tham chiếu "Điều X Nghị định/Luật"
    text = re.sub(r'(Điều|ĐIỀU)\s+(\d+)\s+(Nghị định|Luật|Thông tư|Quyết định|Nghị quyết)', 
                  r'<<<REF>>>\1 \2 \3', text, flags=re.IGNORECASE)
    
    # Thêm xuống dòng trước Điều độc lập (còn lại)
    text = re.sub(r'([^\n<>])\s+(Điều|ĐIỀU)\s+(\d+)', 
                  r'\1\n\n\2 \3', text, flags=re.IGNORECASE)
    
    text = text.replace('<<<REF>>>', '')
    
    return text


# ==============================================================================
# PARSER CLASS
# ==============================================================================

class LegalParser:
    def __init__(self, text):
        self.lines = text.split('\n')
        self.document = {
            "metadata": {
                "loai_van_ban": "", "so_hieu": "", "trich_yeu": "",
                "co_quan_ban_hanh": "", "ngay_ban_hanh": "", "so_trang": 0
            },
            "phan_mo_dau": {"so_hieu": "", "ngay_thang_nam": "", "co_quan_ban_hanh": ""},
            "can_cu_phap_ly": [],
            "chuong": []
        }
        self.current_chuong = None
        self.current_dieu = None
        self.current_khoan = None
        self.current_diem = None
        self.state = {"collecting": None}
        self.buffer = []
        self.pending_chuong_title = False

    def flush_buffer(self):
        """Gom nội dung từ buffer."""
        if not self.buffer:
            return
        content = ' '.join(self.buffer).strip()
        
        if self.state["collecting"] == "diem" and self.current_diem:
            self.current_diem["noi_dung"] = content
        elif self.state["collecting"] == "khoan" and self.current_khoan:
            self.current_khoan["noi_dung"] = content
        elif self.state["collecting"] == "dieu" and self.current_dieu:
            self.current_dieu["noi_dung"] = content
        elif self.state["collecting"] == "chuong" and self.current_chuong:
            self.current_chuong["ten_chuong"] = content
        
        self.buffer = []
        self.state["collecting"] = None

    def parse_metadata(self):
        """Phân tích metadata."""
        full_text = '\n'.join(self.lines[:100])
        
        # Số hiệu
        patterns = [
            r'Số[:\s]+(\d+/\d+/[A-ZĐ\-]+)',
            r'(\d+/\d+/NĐ-CP)',
            r'(\d+/\d+/QĐ-TTg)',
        ]
        for pattern in patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                self.document["metadata"]["so_hieu"] = match.group(1)
                self.document["phan_mo_dau"]["so_hieu"] = match.group(1)
                break
        
        # Loại văn bản
        match = re.search(r'(NGHỊ ĐỊNH|QUYẾT ĐỊNH|THÔNG TƯ|LUẬT|PHÁP LỆNH|NGHỊ QUYẾT)', full_text)
        if match:
            self.document["metadata"]["loai_van_ban"] = match.group(1)
        
        # Ngày ban hành
        match = re.search(r'ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})', full_text)
        if match:
            self.document["metadata"]["ngay_ban_hanh"] = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
        
        # Cơ quan
        if "CHÍNH PHỦ" in full_text.upper():
            self.document["metadata"]["co_quan_ban_hanh"] = "CHÍNH PHỦ"
            self.document["phan_mo_dau"]["co_quan_ban_hanh"] = "CHÍNH PHỦ"

    def parse_structure(self):
        """Phân tích cấu trúc."""
        can_cu_buffer = []
        is_can_cu_section = False

        for line in self.lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Căn cứ pháp lý
            if re.match(r'^Căn cứ\s+', line_stripped, re.IGNORECASE) and not is_can_cu_section:
                is_can_cu_section = True
                self.flush_buffer()
                can_cu_buffer.append(line_stripped)
                continue
            
            if is_can_cu_section:
                can_cu_buffer.append(line_stripped)
                if not line_stripped.endswith(';'):
                    self.document["can_cu_phap_ly"].append(' '.join(can_cu_buffer).strip())
                    can_cu_buffer = []
                    is_can_cu_section = False
                continue

            # Tiêu đề chương từ dòng sau
            if self.pending_chuong_title and self.current_chuong:
                if not re.match(r'^(Điều|ĐIỀU)\s+\d+', line_stripped):
                    self.current_chuong["ten_chuong"] = line_stripped
                    self.pending_chuong_title = False
                    self.state["collecting"] = None
                    continue
                else:
                    self.pending_chuong_title = False

            # Nhận diện cấu trúc
            if self.handle_chuong(line_stripped):
                continue
            if self.handle_dieu(line_stripped):
                continue
            if self.handle_khoan(line_stripped):
                continue
            if self.handle_diem(line_stripped):
                continue

            # Buffer
            if self.state["collecting"]:
                self.buffer.append(line_stripped)

        self.flush_buffer()

    def handle_chuong(self, line):
        """Xử lý Chương"""
        match = re.match(r'^(Chương|CHƯƠNG)\s+([IVXLCDM\d]+)\s*[-:.]?\s*(.*)$', line, re.IGNORECASE)
        if match:
            so_chuong_raw = match.group(2).upper()
            title_part = match.group(3).strip()
            title_part = re.sub(r'^[-–—]\s*', '', title_part)
            
            # Loại bỏ Chương giả (tiêu đề quá ngắn hoặc không hợp lý)
            # Ví dụ: "Chương II mm" là lỗi OCR
            if title_part and len(title_part) < 4:
                clean_title = re.sub(r'[^a-zA-ZÀ-ỹ]', '', title_part)
                if len(clean_title) < 3:
                    return False  # Tiêu đề không hợp lệ
            
            # Kiểm tra trùng lặp chương
            existing_chuong = [c['so_chuong'] for c in self.document['chuong']]
            if so_chuong_raw in existing_chuong:
                # Nếu chương đã tồn tại, không thêm mới mà tiếp tục với chương hiện tại
                for c in self.document['chuong']:
                    if c['so_chuong'] == so_chuong_raw:
                        self.current_chuong = c
                        break
                return True
            
            self.flush_buffer()
            
            dieu_match = re.search(r'(Điều|ĐIỀU)\s+(\d+)', title_part, re.IGNORECASE)
            
            if dieu_match:
                chapter_title = title_part[:dieu_match.start()].strip()
                self.current_chuong = {
                    "so_chuong": so_chuong_raw,
                    "ten_chuong": chapter_title,
                    "dieu": []
                }
                self.document["chuong"].append(self.current_chuong)
                self.current_dieu = self.current_khoan = self.current_diem = None
                self.pending_chuong_title = False
                self.state["collecting"] = None
                
                remainder = title_part[dieu_match.start():].strip()
                self.handle_dieu(remainder)
            else:
                self.current_chuong = {
                    "so_chuong": so_chuong_raw,
                    "ten_chuong": title_part,
                    "dieu": []
                }
                self.document["chuong"].append(self.current_chuong)
                self.current_dieu = self.current_khoan = self.current_diem = None
                
                if not title_part:
                    self.pending_chuong_title = True
                    self.state["collecting"] = "chuong"
                else:
                    self.state["collecting"] = None
                    self.pending_chuong_title = False
            
            return True
        return False

    def handle_dieu(self, line):
        """Xử lý Điều - chỉ nhận Điều thực sự, không phải tham chiếu"""
        # Chỉ nhận nếu Điều ở đầu dòng (sau clean_text đã tách dòng)
        match = re.match(r'^(Điều|ĐIỀU)\s+(\d+)\s*[.:]?\s*(.*)$', line, re.IGNORECASE)
        if not match:
            return False
            
        so_dieu = match.group(2)
        rest_text = match.group(3).strip()
        dieu_num = int(so_dieu)
        
        # === LỌC BỎ THAM CHIẾU ===
        
        # 1. Loại trừ nếu rest_text bắt đầu bằng tên văn bản (tham chiếu)
        ref_patterns = [
            r'^(Nghị quyết|Nghị định|Luật|Pháp lệnh|Thông tư|Quyết định)',
            r'^(số|Số)\s*[\d/]',  # "Điều 21 số 35/2024"
            r'^(của|và|,)',  # "Điều 21 của Luật...", "Điều 21, Điều 22"
            r'^(khoản)',  # "Điều 21 khoản 1"
        ]
        for pattern in ref_patterns:
            if re.match(pattern, rest_text, re.IGNORECASE):
                return False
        
        # 2. Loại trừ số điều lớn bất thường (thường là tham chiếu)
        if dieu_num > 50:  
            # Kiểm tra xem có tiêu đề hợp lệ không
            # Điều thực thường có tiêu đề dài, ví dụ: "Điều 3. Quản lý, sử dụng..."
            if not rest_text or len(rest_text) < 10:
                return False
            # Nếu tiêu đề chỉ là một từ ngắn như "Nghị.", "a ", thì là tham chiếu
            if len(rest_text.split()) < 3 and not rest_text.isupper():
                return False
        
        # 3. Tiêu đề không hợp lệ (quá ngắn, chỉ có ký tự đặc biệt)
        if rest_text:
            # Loại bỏ tiêu đề chỉ có 1-2 ký tự hoặc chỉ có chữ cái đơn
            clean_title = re.sub(r'[^a-zA-ZÀ-ỹ]', '', rest_text)
            if len(clean_title) < 3:
                return False
            # Loại bỏ tiêu đề bắt đầu bằng chữ thường (tham chiếu giữa câu)
            if rest_text[0].islower():
                return False

        self.flush_buffer()
        
        # Tách tiêu đề và nội dung
        tieu_de = rest_text
        noi_dung = ""
        
        # Nếu có khoản 1 trong cùng dòng
        khoan_match = re.search(r'\s+(\d+)\.\s+', rest_text)
        if khoan_match:
            tieu_de = rest_text[:khoan_match.start()].strip()
            noi_dung = rest_text[khoan_match.start():].strip()
        
        self.current_dieu = {
            "so_dieu": so_dieu,
            "tieu_de": tieu_de,
            "noi_dung": noi_dung,
            "khoan": []
        }
        
        if not self.current_chuong:
            if not self.document["chuong"]:
                self.document["chuong"].append({
                    "so_chuong": "", 
                    "ten_chuong": "QUY ĐỊNH CHUNG", 
                    "dieu": []
                })
            self.current_chuong = self.document["chuong"][-1]
        
        self.current_chuong["dieu"].append(self.current_dieu)
        self.current_khoan = self.current_diem = None
        self.state["collecting"] = "dieu"
        return True

    def handle_khoan(self, line):
        """Xử lý Khoản"""
        match = re.match(r'^(\d+)\.\s+(.+)', line)
        if match and self.current_dieu:
            so_khoan = match.group(1)
            
            # Chỉ nhận khoản 1-99
            if not (1 <= int(so_khoan) <= 99):
                return False
            
            if self.state["collecting"] not in ["dieu", "khoan", "diem"]:
                return False

            self.flush_buffer()
            
            self.current_khoan = {
                "so_khoan": so_khoan,
                "noi_dung": match.group(2).strip(),
                "diem": []
            }
            self.current_dieu["khoan"].append(self.current_khoan)
            self.current_diem = None
            self.state["collecting"] = "khoan"
            return True
        return False

    def handle_diem(self, line):
        """Xử lý Điểm"""
        match = re.match(r'^([a-zđ])\)\s+(.+)', line, re.IGNORECASE)
        if match and self.current_khoan:
            if self.state["collecting"] not in ["khoan", "diem"]:
                return False

            self.flush_buffer()
            
            self.current_diem = {
                "so_diem": match.group(1).lower(),
                "noi_dung": match.group(2).strip()
            }
            self.current_khoan["diem"].append(self.current_diem)
            self.state["collecting"] = "diem"
            return True
        return False
        
    def parse(self):
        """Thực hiện phân tích."""
        self.parse_metadata()
        self.parse_structure()
        return self.document


def fix_chapter_numbers(document):
    """
    Post-processing: Sửa số chương bị OCR nhận sai.
    Dựa vào thứ tự xuất hiện để gán lại số La Mã đúng.
    """
    roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    
    chapters = document.get('chuong', [])
    if not chapters:
        return document
    
    # Gán lại số chương theo thứ tự
    for i, chapter in enumerate(chapters):
        if i < len(roman_numerals):
            old_num = chapter.get('so_chuong', '')
            new_num = roman_numerals[i]
            if old_num != new_num:
                chapter['so_chuong'] = new_num
    
    return document


def parse_legal_document(text):
    """Hàm chính để phân tích văn bản pháp luật."""
    cleaned_text = clean_text(text)
    parser = LegalParser(cleaned_text)
    document = parser.parse()
    
    # Post-processing: sửa số chương
    document = fix_chapter_numbers(document)
    
    return document
