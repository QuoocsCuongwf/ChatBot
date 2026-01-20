import re

# ==============================================================================
# CÁC HÀM XỬ LÝ VĂN BẢN (TEXT POST-PROCESSING)
# ==============================================================================

def normalize_text(text):
    """Chuẩn hóa văn bản cơ bản"""
    text = text.replace('\x0c', '') # Xử lý ký tự ngắt trang
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
    "chuyên": "chuyển", "Chuyên": "Chuyển",
    
    # === Lỗi dấu phổ biến ===
    "quyên": "quyền", "Quyên": "Quyền",
    "quyển": "quyền", "Quyển": "Quyền",
    "thâm": "thẩm", "Thâm": "Thẩm","thầm": "thẩm", "Thầm": "Thẩm",
    "quần": "quản", "Quần": "Quản",
    "chinh": "chính", "Chinh": "Chính",
    "chíh": "chính", "Chíh": "Chính",
    "đinh": "định", "Đinh": "Định",
    "trịnh": "trình", "Trịnh": "Trình",
    "trinh": "trình", "Trinh": "Trình",
    "minh": "minh", "mình": "minh",
    
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
    "chuyên đôi": "chuyển đổi",
    
    # === Lỗi phụ âm ===
    "Hiên": "Hiến", "hiên": "hiến",
    "tặc": "tắc", "Tặc": "Tắc",
    "nguyên tặc": "nguyên tắc",
    "quộc": "quốc", "Quộc": "Quốc",
    "điêu": "điều", "Điêu": "Điều",
    "Dicu": "Điều", "Diêu": "Điều", "Đicu": "Điều",
    "quân lý": "quản lý", "quán lý": "quản lý",
    
    # === Lỗi số La Mã - QUAN TRỌNG ===
    "Chương J ": "Chương I ", "CHƯƠNG J ": "CHƯƠNG I ",
    "Chương JI": "Chương II", "CHƯƠNG JI": "CHƯƠNG II", "CHƯƠNG JJ": "CHƯƠNG II",
    "Chương JII": "Chương III", "CHƯƠNG JII": "CHƯƠNG III", "CHƯƠNG JJJ": "CHƯƠNG III",
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
    "Chương IH": "Chương III", "CHƯƠNG IH": "CHƯƠNG III",
    
    # === Lỗi số Điều (4 bị nhận nhầm thành 7, v.v.) ===
    "Điều 7,": "Điều 4.", "điều 7,": "điều 4.",
    "Điều7,": "Điều 4.", "điều7,": "điều 4.",
    
    # === Lỗi tiêu đề ===
    "QUY ĐÌNH CHÚNG": "QUY ĐỊNH CHUNG",
    "QUY ĐINH CHUNG": "QUY ĐỊNH CHUNG",
    "QUẦN LÝ": "QUẢN LÝ",
    "NGH! D!NH": "NGHỊ ĐỊNH",
    "PHÁN CÁP": "PHÂN CẤP",
    "TÀI SẲN": "TÀI SẢN",
    "TỎ CHỨC": "TỔ CHỨC",
    "PHÂN CÁP": "PHÂN CẤP", "PHẦN CẤP": "PHÂN CẤP",
    
    # === Lỗi từ ghép phổ biến ===
    "nhà nuóc": "nhà nước", "Nhà nuóc": "Nhà nước",
    "chính quyên": "chính quyền", 
    "địa phuong": "địa phương",
    "nhiêm vụ": "nhiệm vụ",
    "thục hiện": "thực hiện", "thực hiên": "thực hiện",
    "quy đinh": "quy định",
    "hội đông": "hội đồng",
    "tô chức": "tổ chức", "tồ chức": "tổ chức",
    "xử bý": "xử lý", "xử ly": "xử lý",
    "bồ sung": "bổ sung",
    "sửa đôi": "sửa đổi",
    "phạm ví": "phạm vi", "phạn vi": "phạm vi",
    "đối tuợng": "đối tượng",
    "chiên lược": "chiến lược",
    "kiêm tra": "kiểm tra", "kiếm tra": "kiểm tra",
    "vỉ phạm": "vi phạm",
    "tải sản": "tài sản",
    "hiệu lục": "hiệu lực", "hiệu luc": "hiệu lực",
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
    
    # === Bổ sung ===
    "Ÿ tế": "Y tế",
    "THỊ HÀNH": "THI HÀNH", "thị hành": "thi hành",
    "Dgười": "Người", "DgƯỜI": "NGƯỜI",
    "ŸY tế": "Y tế",
    "thẳm quyền": "thẩm quyền",
    "chỉ phí": "chi phí",
    "chỉ trả": "chi trả",
    "chỉ tiết": "chi tiết",
    "địch bệnh": "dịch bệnh",
    "thiến tai": "thiên tai",
    "đồi với": "đối với",
    "chuyển đổi só": "chuyển đổi số",
    "mình bạch": "minh bạch",
    "quôc tê": "quốc tế",
    "hăng tháng": "hằng tháng",
    "đên": "đến",
    "cập xã": "cấp xã", "câp xã": "cấp xã",
    "Nghị Điều": "Nghị định", "nghị Điều": "nghị định",
    "Nghị điêu": "Nghị định",
    "Ngữi quyết": "Nghị quyết",
    "thương maih": "thương mại",
    "kinh tê": "kinh tế", "y tê": "y tế", "quôc tê": "quốc tế",
    "thâm quyền": "thẩm quyền", "Thâm quyền": "Thẩm quyền",
    "thâm định": "thẩm định", "Thâm định": "Thẩm định",
    "kiêm tra": "kiểm tra", "Kiêm tra": "Kiểm tra",
    "tô chức": "tổ chức", "Tô chức": "Tổ chức",
    "câp": "cấp", "Câp": "Cấp",
    "đâu tư": "đầu tư", "Đâu tư": "Đầu tư",
    "đât đai": "đất đai", "Đât đai": "Đất đai",
    "Nghị định sô": "Nghị định số",
    "Luật sô": "Luật số",
    "Thông tư sô": "Thông tư số",
}

def fix_vietnamese_ocr_errors(text):
    """Sửa các lỗi chính tả phổ biến do OCR"""
    for error, fix in VIETNAMESE_OCR_FIXES.items():
        text = text.replace(error, fix)
    
    text = re.sub(r'\n[lI]\.\s', '\n1. ', text)
    text = re.sub(r'^[lI]\.\s', '1. ', text, flags=re.MULTILINE)
    text = re.sub(r'Điều\s+l([.\s])', r'Điều 1\1', text)
    text = re.sub(r'Điều\s+I([.\s])', r'Điều 1\1', text)
    text = re.sub(r'[|¬~`¡„€•\[\]{}#*]', '', text)
    text = re.sub(r'-\s*\n\s*', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\s+([.,;:])', r'\1', text)
    
    # Sửa lỗi số La Mã Chương
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
    
    text = re.sub(r'[|Ñ„"\'—\-]+\s*(Chương|CHƯƠNG)', r'\n\1', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+)/\d+/NĐ-ƠP', r'\1/2021/NĐ-CP', text)
    text = re.sub(r'(\d+)/\d+/NĐ- CP', r'\1/2021/NĐ-CP', text)
    
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

def remove_page_numbers(text):
    """Xóa số trang ở cuối hoặc đầu trang bị lẫn vào nội dung"""
    # 1. Xóa dòng chỉ có số (số trang đứng riêng)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    
    # 2. Xóa số trang dính vào đầu dòng tiếp theo (ví dụ: "12 8. Nhiệm vụ...")
    # Pattern: Xuống dòng + số trang + khoảng trắng + số thứ tự khoản/điều + dấu chấm
    text = re.sub(r'\n\s*\d+\s+(\d+\.)', r'\n\1', text)
    
    # 3. Xóa số trang dính vào cuối câu trước (ví dụ: "...thực hiện. 21")
    # Pattern: Dấu chấm + khoảng trắng + số trang + xuống dòng
    text = re.sub(r'(\.)\s+\d+\s*\n', r'\1\n', text)
    
    # 4. Xóa số trang dính vào giữa câu (nguy hiểm hơn, cần ngữ cảnh)
    # Ví dụ: "...quy định tại khoản 1 Điều 31 Nghị định này..." (số 31 là số trang bị dính)
    # Pattern: từ thường + số + từ viết hoa (thường là đầu câu mới)
    # text = re.sub(r'([a-zà-ỹ])\s+\d+\s+([A-ZÀ-Ỹ])', r'\1 \2', text) # Tạm thời chưa dùng vì dễ xóa nhầm số liệu
    
    return text

def clean_text(text):
    """Áp dụng tất cả bước làm sạch văn bản."""
    # Bước 1: Xóa số trang trước khi xử lý khác để tránh làm gãy cấu trúc
    text = remove_page_numbers(text)
    
    text = normalize_text(text)
    text = fix_vietnamese_ocr_errors(text)
    text = apply_context_aware_fixes(text)
    
    # Thêm xuống dòng trước Chương
    text = re.sub(r'([^\n])\s+(Chương|CHƯƠNG)\s+([IVXLCDM\d]+)', 
                  r'\1\n\n\2 \3', text, flags=re.IGNORECASE)
    
    # Thêm xuống dòng trước Phần (Bảo vệ tham chiếu)
    ref_phan_pattern = r'(tại|theo|của|số|khoản\s+[\d,\svàhoặc]+|điểm\s+[\w,\svàhoặc]+|hoặc|và|,|;)\s+(Phần|PHẦN)\s+([IVXLCDM\d]+)'
    text = re.sub(ref_phan_pattern, r'\1 <<<REF>>>\2 \3', text, flags=re.IGNORECASE)
    text = re.sub(r'([^\n<>])\s+(Phần|PHẦN)\s+([IVXLCDM\d]+)', 
                  r'\1\n\n\2 \3', text, flags=re.IGNORECASE)

    # Thêm xuống dòng trước Mục (Bảo vệ tham chiếu)
    ref_muc_pattern = r'(tại|theo|của|số|khoản\s+[\d,\svàhoặc]+|điểm\s+[\w,\svàhoặc]+|hoặc|và|,|;)\s+(Mục|MỤC)\s+([IVXLCDM\d]+)'
    text = re.sub(ref_muc_pattern, r'\1 <<<REF>>>\2 \3', text, flags=re.IGNORECASE)
    text = re.sub(r'([^\n<>])\s+(Mục|MỤC)\s+([IVXLCDM\d]+)', 
                  r'\1\n\n\2 \3', text, flags=re.IGNORECASE)

    # Thêm xuống dòng trước Điều (không phải tham chiếu)
    # Bảo vệ tham chiếu kiểu "tại Điều X", "theo Điều X", "quy định tại Điều X"
    ref_pattern = r'(tại|theo|của|số|khoản\s+[\d,\svàhoặc]+|điểm\s+[\w,\svàhoặc]+|hoặc|và|,|;)\s+(Điều|ĐIỀU)\s+(\d+)'
    text = re.sub(ref_pattern, r'\1 <<<REF>>>\2 \3', text, flags=re.IGNORECASE)
    
    # Bảo vệ tham chiếu "Điều X Nghị định/Luật"
    text = re.sub(r'(Điều|ĐIỀU)\s+(\d+)\s+(Nghị định|Luật|Thông tư|Quyết định|Nghị quyết)', 
                  r'<<<REF>>>\1 \2 \3', text, flags=re.IGNORECASE)
    
    # Xử lý trường hợp số trang hoặc số thứ tự đứng trước Điều (ví dụ: ". 21 Điều 28")
    text = re.sub(r'(\.)\s+(\d+)\s+(Điều|ĐIỀU)\s+(\d+)', 
                  r'\1\n\n\3 \4', text, flags=re.IGNORECASE)
    
    # Tách dòng cho các khoản (số thứ tự đầu dòng) bị dính vào dòng trước
    text = re.sub(r'([.;:)]|\s+)\s*(\d+\.\s+[A-ZÀ-Ỹ])', r'\1\n\2', text)

    # Tách dòng cho các điểm a), b)... bị dính vào dòng trước (sau dấu hai chấm, chấm phẩy, chấm)
    text = re.sub(r'([:;.])\s*([a-zđ])\)\s+', r'\1\n\2) ', text, flags=re.IGNORECASE)

    # Tách Khoản 1 (hoặc các khoản khác) bị dính vào giữa đoạn văn
    text = re.sub(r'(\s+)(1\.\s+[A-ZÀ-Ỹ])', r'\n\2', text)
    
    # Tách Khoản 1 khi dính vào năm (ví dụ: năm 2022 1. )
    text = re.sub(r'\b(năm\s+\d+)\s*(1\.\s+[A-ZÀ-Ỹ])', r'\1\n\2', text, flags=re.IGNORECASE)
    # Tách Khoản 1 khi dính vào tên Luật/Nghị định (ví dụ: Luật Đất đai 1. )
    text = re.sub(r'(Luật\s+[^0-9]+)\s*(1\.\s+[A-ZÀ-Ỹ])', r'\1\n\2', text, flags=re.IGNORECASE)

    # Tách Khoản 1 bị dính vào tiêu đề Điều (có tiêu đề ở giữa)
    text = re.sub(r'((?:Điều|ĐIỀU)\s+\d+.*?)\s+(1\.\s+[A-ZÀ-Ỹ])', r'\1\n\2', text)

    # Tách Điều và Khoản 1 nếu dính nhau (ví dụ: "Điều 2. 1. Nội dung")
    text = re.sub(r'(Điều|ĐIỀU)\s+(\d+)[.:]?\s+(1\.\s+[A-ZÀ-Ỹ])', r'\1 \2.\n\3', text)

    # Thêm xuống dòng trước Điều độc lập (còn lại)
    text = re.sub(r'([^\n<>])\s+(Điều|ĐIỀU)\s+(\d+)', 
                  r'\1\n\n\2 \3', text, flags=re.IGNORECASE)
    
    text = text.replace('<<<REF>>>', '')
    
    return text

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
        """Gom nội dung từ buffer và phát hiện Điều bị gộp nhầm."""
        if not self.buffer:
            return
        content = ' '.join(self.buffer).strip()
        
        # PHÁT HIỆN ĐIỀU BỊ GỘP NHẦM VÀO BUFFER
        # Pattern: "...nội dung. Điều 4,Tên điều" hoặc "...nội dung. Điều 7,Phân cấp..."
        dieu_in_buffer = re.search(r'(.*?)[\.\s]+([Đđ]i[ềê]u)\s*(\d+)\s*[,\.]?\s*([A-ZÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ].{5,})', content, re.IGNORECASE | re.DOTALL)
        
        if dieu_in_buffer and self.state["collecting"] in ["khoan", "diem"]:
            # Tách nội dung hiện tại và điều bị gộp
            current_content = dieu_in_buffer.group(1).strip()
            next_dieu_text = dieu_in_buffer.group(2) + " " + dieu_in_buffer.group(3) + " " + dieu_in_buffer.group(4)
            
            # Lưu nội dung hiện tại
            if self.state["collecting"] == "diem" and self.current_diem:
                self.current_diem["noi_dung"] = (self.current_diem.get("noi_dung", "") + " " + current_content).strip()
            elif self.state["collecting"] == "khoan" and self.current_khoan:
                self.current_khoan["noi_dung"] = (self.current_khoan.get("noi_dung", "") + " " + current_content).strip()
            
            # Clear buffer và xử lý điều tiếp theo
            self.buffer = []
            self.state["collecting"] = None
            
            # Xử lý điều bị gộp
            self.handle_dieu(next_dieu_text)
            return
        
        # Xử lý bình thường nếu không phát hiện điều bị gộp
        if self.state["collecting"] == "diem" and self.current_diem:
            self.current_diem["noi_dung"] = (self.current_diem.get("noi_dung", "") + " " + content).strip()
        elif self.state["collecting"] == "khoan" and self.current_khoan:
            self.current_khoan["noi_dung"] = (self.current_khoan.get("noi_dung", "") + " " + content).strip()
        elif self.state["collecting"] == "dieu" and self.current_dieu:
            self.current_dieu["noi_dung"] = (self.current_dieu.get("noi_dung", "") + " " + content).strip()
        elif self.state["collecting"] == "chuong" and self.current_chuong:
            self.current_chuong["ten_chuong"] = (self.current_chuong.get("ten_chuong", "") + " " + content).strip()
        
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
            
            if title_part and len(title_part) < 4:
                clean_title = re.sub(r'[^a-zA-ZÀ-ỹ]', '', title_part)
                if len(clean_title) < 3:
                    return False
            
            existing_chuong = [c['so_chuong'] for c in self.document['chuong']]
            if so_chuong_raw in existing_chuong:
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
        """Xử lý Điều"""
        match = re.match(r'^(Điều|ĐIỀU)\s+(\d+)\s*[.:]?\s*(.*)$', line, re.IGNORECASE)
        if not match:
            return False
            
        so_dieu = match.group(2)
        rest_text = match.group(3).strip()
        
        # PHÁT HIỆN ĐIỀU BỊ GỘP NHẦM VÀO TRONG KHOẢN (Lỗi OCR)
        # Pattern: "... Điều 4,Tên điều" hoặc "... Điều 7,Phân cấp..."
        dieu_in_khoan = re.search(r'[\.\s]+([Điều|ĐIỀU]\s+\d+)\s*[,\.]?\s*([A-ZÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ].{5,})', rest_text, re.IGNORECASE)
        
        if dieu_in_khoan:
            # Tách nội dung điều hiện tại và điều bị gộp
            dieu_part = rest_text[:dieu_in_khoan.start()].strip()
            next_dieu_part = rest_text[dieu_in_khoan.start():].strip()
            
            # Xử lý điều hiện tại trước (nếu có nội dung)
            if dieu_part:
                rest_text = dieu_part
            else:
                # Nếu không có nội dung điều hiện tại, bỏ qua và xử lý điều tiếp theo
                self.handle_dieu(next_dieu_part)
                return True
                
            # Lưu next_dieu_part để xử lý sau khi hoàn thành điều hiện tại
            self.pending_next_dieu = next_dieu_part
        else:
            self.pending_next_dieu = None
        
        # PHÁT HIỆN CHƯƠNG GỘP NHẦM VÀO NỘI DUNG ĐIỀU
        # Pattern: "... Chương [I-IX/J]+ TÊN_CHƯƠNG"
        # Có thể có hoặc không có dấu chấm trước "Chương"
        chuong_in_dieu = re.search(r'[\.\s]+(Chương|CHƯƠNG)\s+([IVXLCDMJ]+)\s+([A-ZÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ].{10,})', rest_text, re.IGNORECASE)
        
        if chuong_in_dieu:
            # Tách nội dung điều và tiêu đề chương
            dieu_part = rest_text[:chuong_in_dieu.start()].strip()
            chuong_part = rest_text[chuong_in_dieu.start():].strip()
            
            # Lưu phần điều hiện tại (nếu có nội dung)
            if dieu_part:
                rest_text = dieu_part
            else:
                # Nếu không có nội dung điều, bỏ qua điều này
                # và xử lý chương sau
                self.handle_chuong(chuong_part)
                return True
        
        # LỌC BỎ THAM CHIẾU
        ref_patterns = [
            r'^(Nghị quyết|Nghị định|Luật|Pháp lệnh|Thông tư|Quyết định)',
            r'^(số|Số)\s*[\d/]',
            r'^(của|và|hoặc|,|;|\.)',
            r'^(khoản)',
            r'^(Điều|ĐIỀU)\s+\d+',
        ]
        for pattern in ref_patterns:
            if re.match(pattern, rest_text, re.IGNORECASE):
                return False
        
        if rest_text:
            clean_title = re.sub(r'[^a-zA-ZÀ-ỹ]', '', rest_text)
            if len(clean_title) < 3:
                return False
            first_char_match = re.search(r'[a-zA-ZÀ-ỹ]', rest_text)
            if first_char_match and first_char_match.group(0).islower():
                return False
            if re.match(r'^(và|hoặc|thì|là|của)\s+', rest_text, re.IGNORECASE):
                return False
            if len(rest_text) < 5 and not re.search(r'[a-zA-Z]', rest_text):
                if not re.match(r'^[.:\s]+$', rest_text):
                    return False

        self.flush_buffer()
        
        dieu_content = rest_text
        first_khoan_content = None
        is_dinh_khoan = False

        # Tìm kiếm "1. " theo sau là chữ in hoa
        match_split = re.search(r'(?:^|\s+)(1\.\s+[A-ZÀ-Ỹ].*)', rest_text, re.DOTALL)
        
        if match_split:
            start_idx = match_split.start(1)
            if start_idx == 0:
                dieu_content = ""
                first_khoan_content = rest_text
                is_dinh_khoan = True # <--- SỬA LỖI: Bật cờ này khi Khoản 1 nằm ngay đầu
            else:
                prefix = rest_text[:start_idx]
                # Kiểm tra xem phía trước có phải là "năm", "tháng", "ngày" không
                if not re.search(r'(năm|tháng|ngày)\s*$', prefix.strip(), re.IGNORECASE):
                    dieu_content = prefix.strip()
                    first_khoan_content = rest_text[start_idx:].strip()
                    is_dinh_khoan = True

        self.current_dieu = {
            "so_dieu": so_dieu,
            "noi_dung": dieu_content,
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

        if is_dinh_khoan and first_khoan_content:
            self.handle_khoan(first_khoan_content)
        
        # XỬ LÝ CHƯƠNG BỊ GỘP NHẦM (nếu có)
        if chuong_in_dieu:
            self.handle_chuong(chuong_part)
        
        # XỬ LÝ ĐIỀU TIẾP THEO BỊ GỘP NHẦM (nếu có)
        if hasattr(self, 'pending_next_dieu') and self.pending_next_dieu:
            next_dieu = self.pending_next_dieu
            self.pending_next_dieu = None
            self.handle_dieu(next_dieu)

        return True

    def handle_khoan(self, line):
        """Xử lý Khoản"""
        match = re.match(r'^(\d+)\.\s*(.+)', line)
        if match and self.current_dieu:
            so_khoan = match.group(1)
            if not (1 <= int(so_khoan) <= 99):
                return False
            
            if self.state["collecting"] not in ["dieu", "khoan", "diem"]:
                return False

            self.flush_buffer()
            
            khoan_content = match.group(2).strip()
            
            # PHÁT HIỆN ĐIỀU BỊ GỘP NHẦM VÀO CUỐI KHOẢN
            # Pattern: "...thực hiện. Điều 4,Tên điều" hoặc "...thực hiện. Điều 7,Phân cấp..."
            dieu_in_khoan = re.search(r'[\.\s]+([Đđ]i[ềê]u)\s+(\d+)\s*[,\.]?\s*([A-ZÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ].{5,})', khoan_content, re.IGNORECASE)
            
            if dieu_in_khoan:
                # Tách nội dung khoản và điều bị gộp
                khoan_part = khoan_content[:dieu_in_khoan.start()].strip()
                next_dieu_part = khoan_content[dieu_in_khoan.start():].strip()
                
                # Lưu khoản hiện tại với nội dung đã tách
                self.current_khoan = {
                    "so_khoan": so_khoan,
                    "noi_dung": khoan_part,
                    "diem": []
                }
                self.current_dieu["khoan"].append(self.current_khoan)
                self.current_diem = None
                self.state["collecting"] = "khoan"
                
                # Xử lý điều bị gộp
                self.flush_buffer()
                self.handle_dieu(next_dieu_part)
                return True
            
            # Không có điều bị gộp, xử lý bình thường
            self.current_khoan = {
                "so_khoan": so_khoan,
                "noi_dung": khoan_content,
                "diem": []
            }
            self.current_dieu["khoan"].append(self.current_khoan)
            self.current_diem = None
            self.state["collecting"] = "khoan"
            return True
        return False

    def handle_diem(self, line):
        """Xử lý Điểm"""
        match = re.match(r'^([a-zđ])\)\s*(.+)', line, re.IGNORECASE)
        if match and self.current_dieu:
            if self.state["collecting"] not in ["dieu", "khoan", "diem"]:
                return False

            self.flush_buffer()
            
            # Tự động tạo khoản nếu chưa có (trường hợp Điều có điểm trực tiếp hoặc OCR sót Khoản)
            if not self.current_khoan:
                self.current_khoan = {
                    "so_khoan": "", 
                    "noi_dung": "",
                    "diem": []
                }
                self.current_dieu["khoan"].append(self.current_khoan)

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
    """Sửa số chương bị OCR nhận sai."""
    roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV']
    chapters = document.get('chuong', [])
    if not chapters:
        return document
    for i, chapter in enumerate(chapters):
        if i < len(roman_numerals):
            old_num = chapter.get('so_chuong', '')
            new_num = roman_numerals[i]
            if old_num != new_num:
                chapter['so_chuong'] = new_num
    return document

def fix_missing_dieu_4(document):
    """
    Sửa trường hợp Điều bị gộp nhầm vào điều trước (tổng quát cho mọi điều)
    Phát hiện: Điều có khoản bị lặp số (ví dụ: 1,2,3,2,3 hoặc 1,2,3,1,2)
    """
    for chuong in document.get('chuong', []):
        dieu_list = chuong.get('dieu', [])
        i = 0
        
        while i < len(dieu_list):
            dieu = dieu_list[i]
            khoan_list = dieu.get('khoan', [])
            
            if len(khoan_list) < 2:
                i += 1
                continue
            
            # Tìm vị trí khoản bị lặp số
            seen_numbers = set()
            split_index = None
            
            for j, khoan in enumerate(khoan_list):
                so_khoan = khoan.get('so_khoan', '')
                if so_khoan in seen_numbers:
                    # Phát hiện số bị lặp - đây là điểm tách
                    split_index = j
                    break
                seen_numbers.add(so_khoan)
            
            if split_index:
                # Tách khoản từ split_index trở đi sang điều mới
                new_dieu_khoan = khoan_list[split_index:]
                dieu_list[i]['khoan'] = khoan_list[:split_index]
                
                # Tính số điều mới (số điều hiện tại + 1)
                try:
                    so_dieu_hien_tai = int(dieu.get('so_dieu', '0'))
                    so_dieu_moi = str(so_dieu_hien_tai + 1)
                except:
                    so_dieu_moi = str(i + 2)  # Fallback
                
                # Xác định tên điều mới dựa trên ngữ cảnh
                # Nếu điều hiện tại là "Phân quyền..." thì điều mới có thể là "Phân cấp..."
                noi_dung_hien_tai = dieu.get('noi_dung', '')
                if 'Phân quyền' in noi_dung_hien_tai:
                    noi_dung_moi = noi_dung_hien_tai.replace('Phân quyền', 'Phân cấp')
                elif 'quy định chung' in noi_dung_hien_tai.lower():
                    noi_dung_moi = "Quy định cụ thể"
                else:
                    # Lấy từ nội dung khoản đầu tiên nếu có
                    first_khoan_text = new_dieu_khoan[0].get('noi_dung', '') if new_dieu_khoan else ''
                    # Trích xuất cụm từ chính (thường là động từ + danh từ)
                    match = re.search(r'^(Việc\s+[^\.]{5,50})', first_khoan_text)
                    if match:
                        noi_dung_moi = match.group(1).strip()
                    else:
                        noi_dung_moi = f"Quy định về {noi_dung_hien_tai.lower()}" if noi_dung_hien_tai else "Quy định khác"
                
                # Tạo điều mới
                new_dieu = {
                    "so_dieu": so_dieu_moi,
                    "noi_dung": noi_dung_moi,
                    "khoan": new_dieu_khoan
                }
                
                # Fix số khoản cho điều mới (đánh lại từ 1)
                for j, khoan in enumerate(new_dieu['khoan'], start=1):
                    khoan['so_khoan'] = str(j)
                
                # Chèn điều mới vào đúng vị trí
                dieu_list.insert(i + 1, new_dieu)
                
                print(f"   🔧 Phát hiện và tách Điều {so_dieu_moi} từ Điều {dieu.get('so_dieu')}")
                
                # KHÔNG cập nhật số điều sau - để nguyên số gốc từ OCR
                # Vì có thể Điều 5 đã đúng, chỉ thiếu Điều 4
                
                i += 1  # Bỏ qua điều vừa tạo
            
            i += 1
    
    return document

def parse_legal_document(text):
    """Hàm chính để phân tích văn bản pháp luật."""
    cleaned_text = clean_text(text)
    parser = LegalParser(cleaned_text)
    document = parser.parse()
    document = fix_chapter_numbers(document)
    document = fix_missing_dieu_4(document)  # Sửa Điều 4 bị mất
    return document
