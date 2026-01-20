"""
Parser chuyển kết quả OCR thành format văn bản pháp luật
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
import sys
sys.stdout.reconfigure(encoding='utf-8')


class LegalDocumentParser:
    """Parser văn bản pháp luật từ kết quả OCR"""
    
    def __init__(self):
        self.patterns = {
            'so_hieu': r'(\d+/\d{4}/[A-Z\-]+)',
            'ngay_ban_hanh': r'(\d{1,2}/\d{1,2}/\d{4})',
            'chuong': r'CHƯƠNG\s+([IVX]+)\s*[\n:]?\s*([^\n]+)',
            'dieu': r'Điều\s+(\d+)[\.:]?\s*([^\n]*)',
            'khoan': r'(\d+)\.\s+([^\n]+)',
            'can_cu': r'Căn cứ\s+([^;]+)',
        }
    
    def extract_full_text(self, ocr_result: Dict) -> str:
        """Ghép toàn bộ text từ kết quả OCR"""
        full_text = []
        for page in ocr_result.get('pages', []):
            for region in page.get('ocr_results', []):
                text = region.get('text', '').strip()
                if text:
                    full_text.append(text)
        return '\n'.join(full_text)
    
    def extract_metadata(self, text: str) -> Dict:
        """Trích xuất metadata văn bản"""
        metadata = {
            'loai_van_ban': '',
            'so_hieu': '',
            'trich_yeu': '',
            'co_quan_ban_hanh': '',
            'ngay_ban_hanh': '',
            'so_trang': 0,
            'loai_pdf': 'scan'
        }
        
        # Tìm số hiệu
        so_hieu_match = re.search(self.patterns['so_hieu'], text)
        if so_hieu_match:
            metadata['so_hieu'] = so_hieu_match.group(1)
            # Xác định loại văn bản từ số hiệu
            if 'NĐ-CP' in metadata['so_hieu'] or 'NĐCP' in metadata['so_hieu']:
                metadata['loai_van_ban'] = 'NGHỊ ĐỊNH'
            elif 'QĐ-TTg' in metadata['so_hieu']:
                metadata['loai_van_ban'] = 'QUYẾT ĐỊNH'
            elif 'TT' in metadata['so_hieu']:
                metadata['loai_van_ban'] = 'THÔNG TƯ'
        
        # Tìm ngày ban hành
        ngay_match = re.search(self.patterns['ngay_ban_hanh'], text)
        if ngay_match:
            metadata['ngay_ban_hanh'] = ngay_match.group(1)
        
        # Tìm cơ quan ban hành
        if 'CHÍNH PHỦ' in text:
            metadata['co_quan_ban_hanh'] = 'CHÍNH PHỦ'
        elif 'THỦ TƯỚNG' in text:
            metadata['co_quan_ban_hanh'] = 'THỦ TƯỚNG CHÍNH PHỦ'
        
        return metadata
    
    def extract_can_cu(self, text: str) -> List[str]:
        """Trích xuất các căn cứ pháp lý"""
        can_cu_list = []
        
        # Tìm các đoạn bắt đầu bằng "Căn cứ"
        matches = re.finditer(self.patterns['can_cu'], text, re.IGNORECASE)
        for match in matches:
            can_cu = match.group(1).strip()
            if can_cu and len(can_cu) > 10:  # Lọc các match quá ngắn
                can_cu_list.append(can_cu)
        
        return can_cu_list[:10]  # Giới hạn 10 căn cứ đầu
    
    def extract_chuong(self, text: str) -> List[Dict]:
        """Trích xuất các chương và điều"""
        chuong_list = []
        
        # Tìm các chương
        chuong_matches = list(re.finditer(self.patterns['chuong'], text, re.IGNORECASE))
        
        for i, chuong_match in enumerate(chuong_matches):
            chuong = {
                'so_chuong': chuong_match.group(1),
                'ten_chuong': chuong_match.group(2).strip(),
                'dieu': []
            }
            
            # Xác định phạm vi text của chương này
            start_pos = chuong_match.end()
            end_pos = chuong_matches[i+1].start() if i+1 < len(chuong_matches) else len(text)
            chuong_text = text[start_pos:end_pos]
            
            # Trích xuất các điều trong chương
            chuong['dieu'] = self.extract_dieu(chuong_text)
            chuong_list.append(chuong)
        
        return chuong_list
    
    def extract_dieu(self, text: str) -> List[Dict]:
        """Trích xuất các điều"""
        dieu_list = []
        
        dieu_matches = list(re.finditer(self.patterns['dieu'], text, re.IGNORECASE))
        
        for i, dieu_match in enumerate(dieu_matches):
            dieu = {
                'so_dieu': dieu_match.group(1),
                'noi_dung': '',
                'khoan': []
            }
            
            # Xác định phạm vi text của điều này
            start_pos = dieu_match.end()
            end_pos = dieu_matches[i+1].start() if i+1 < len(dieu_matches) else len(text)
            dieu_text = text[start_pos:end_pos]
            
            # Nội dung chính của điều (trước khoản đầu tiên)
            khoan_matches = list(re.finditer(self.patterns['khoan'], dieu_text))
            if khoan_matches:
                dieu['noi_dung'] = dieu_text[:khoan_matches[0].start()].strip()
                dieu['khoan'] = self.extract_khoan(dieu_text)
            else:
                dieu['noi_dung'] = dieu_text.strip()
            
            dieu_list.append(dieu)
        
        return dieu_list
    
    def extract_khoan(self, text: str) -> List[Dict]:
        """Trích xuất các khoản"""
        khoan_list = []
        
        khoan_matches = list(re.finditer(self.patterns['khoan'], text))
        
        for i, khoan_match in enumerate(khoan_matches):
            khoan = {
                'so_khoan': khoan_match.group(1),
                'noi_dung': '',
                'diem': []
            }
            
            # Xác định phạm vi text của khoản này
            start_pos = khoan_match.end()
            end_pos = khoan_matches[i+1].start() if i+1 < len(khoan_matches) else len(text)
            khoan_text = text[start_pos:end_pos]
            
            khoan['noi_dung'] = khoan_text.strip()
            khoan_list.append(khoan)
        
        return khoan_list
    
    def parse(self, ocr_file: str, output_file: str):
        """Parse file OCR JSON thành format văn bản pháp luật"""
        print(f"Đang parse: {ocr_file}")
        
        # Đọc kết quả OCR
        with open(ocr_file, 'r', encoding='utf-8') as f:
            ocr_data = json.load(f)
        
        # Trích xuất text đầy đủ
        full_text = self.extract_full_text(ocr_data)
        
        # Parse các thành phần
        result = {
            'metadata': self.extract_metadata(full_text),
            'phan_mo_dau': {
                'so_hieu': '',
                'ngay_thang_nam': '',
                'co_quan_ban_hanh': ''
            },
            'can_cu_phap_ly': self.extract_can_cu(full_text),
            'chuong': self.extract_chuong(full_text)
        }
        
        # Cập nhật metadata số trang
        result['metadata']['so_trang'] = ocr_data.get('total_pages', 0)
        
        # Cập nhật phần mở đầu từ metadata
        result['phan_mo_dau']['so_hieu'] = result['metadata']['so_hieu']
        result['phan_mo_dau']['co_quan_ban_hanh'] = result['metadata']['co_quan_ban_hanh']
        
        # Lưu kết quả
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Đã lưu: {output_file}")
        print(f"  - Số trang: {result['metadata']['so_trang']}")
        print(f"  - Số chương: {len(result['chuong'])}")
        print(f"  - Số căn cứ: {len(result['can_cu_phap_ly'])}")
        
        # Tạo chunks
        chunks_file = str(Path(output_file).with_suffix('')) + '_chunks.json'
        self.create_chunks(result, chunks_file)
    
    def create_chunks(self, parsed_doc: Dict, output_file: str):
        """Tạo chunks từ văn bản đã parse"""
        chunks = []
        chunk_id = 0
        
        # Chunk 1: Metadata
        chunk_id += 1
        chunks.append({
            'chunk_id': f'chunk_{chunk_id:04d}',
            'type': 'metadata',
            'content': f"Văn bản: {parsed_doc['metadata'].get('loai_van_ban', '')} số {parsed_doc['metadata'].get('so_hieu', '')}. " +
                      f"Trích yếu: {parsed_doc['metadata'].get('trich_yeu', '')}. " +
                      f"Cơ quan ban hành: {parsed_doc['metadata'].get('co_quan_ban_hanh', '')}. " +
                      f"Ngày ban hành: {parsed_doc['metadata'].get('ngay_ban_hanh', '')}.",
            'metadata': {
                'so_hieu': parsed_doc['metadata'].get('so_hieu', ''),
                'loai_van_ban': parsed_doc['metadata'].get('loai_van_ban', ''),
                'source': 'metadata'
            }
        })
        
        # Chunk 2-N: Căn cứ pháp lý
        for i, can_cu in enumerate(parsed_doc.get('can_cu_phap_ly', [])):
            chunk_id += 1
            chunks.append({
                'chunk_id': f'chunk_{chunk_id:04d}',
                'type': 'can_cu',
                'content': f"Căn cứ: {can_cu}",
                'metadata': {
                    'so_hieu': parsed_doc['metadata'].get('so_hieu', ''),
                    'can_cu_index': i,
                    'source': 'can_cu_phap_ly'
                }
            })
        
        # Chunk cho mỗi Điều
        for chuong in parsed_doc.get('chuong', []):
            chuong_so = chuong.get('so', '')
            chuong_ten = chuong.get('ten', '')
            
            for dieu in chuong.get('dieu', []):
                dieu_so = dieu.get('so', '')
                dieu_tieu_de = dieu.get('tieu_de', '')
                
                # Chunk cho toàn bộ điều
                chunk_id += 1
                dieu_content = f"Chương {chuong_so}: {chuong_ten}. Điều {dieu_so}"
                if dieu_tieu_de:
                    dieu_content += f": {dieu_tieu_de}"
                
                # Thêm các khoản
                khoan_texts = []
                for khoan in dieu.get('khoan', []):
                    khoan_texts.append(khoan.get('noi_dung', ''))
                
                if khoan_texts:
                    dieu_content += "\n" + "\n".join(khoan_texts)
                
                chunks.append({
                    'chunk_id': f'chunk_{chunk_id:04d}',
                    'type': 'dieu',
                    'content': dieu_content,
                    'metadata': {
                        'so_hieu': parsed_doc['metadata'].get('so_hieu', ''),
                        'chuong': chuong_so,
                        'dieu': dieu_so,
                        'source': f'chuong_{chuong_so}_dieu_{dieu_so}'
                    }
                })
        
        # Lưu chunks
        chunks_data = {
            'document': parsed_doc['metadata'].get('so_hieu', ''),
            'total_chunks': len(chunks),
            'chunks': chunks
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Đã tạo {len(chunks)} chunks: {output_file}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse OCR JSON thành format văn bản pháp luật')
    parser.add_argument('input', help='File JSON kết quả OCR')
    parser.add_argument('-o', '--output', help='File JSON output', required=True)
    
    args = parser.parse_args()
    
    # Parse
    legal_parser = LegalDocumentParser()
    legal_parser.parse(args.input, args.output)


if __name__ == '__main__':
    main()
