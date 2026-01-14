import json
import pandas as pd
from typing import List, Dict, Any
import sys
sys.stdout.reconfigure(encoding='utf-8')

def flatten_json_for_phobert(json_file_path: str, output_csv_path: str = None):
    """
    Làm phẳng dữ liệu JSON văn bản pháp luật để chuẩn bị cho phoBERT
    
    Args:
        json_file_path: Đường dẫn file JSON đầu vào
        output_csv_path: Đường dẫn file CSV đầu ra (tùy chọn)
    
    Returns:
        DataFrame chứa dữ liệu đã làm phẳng
    """
    
    # Đọc file JSON
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    flattened_data = []
    
    # Lấy thông tin metadata
    metadata = data.get('metadata', {})
    
    # Xử lý phần căn cứ pháp lý
    can_cu_phap_ly = data.get('can_cu_phap_ly', [])
    for idx, can_cu in enumerate(can_cu_phap_ly):
        if can_cu.strip():
            flattened_data.append({
                'loai_van_ban': metadata.get('loai_van_ban', ''),
                'so_hieu': metadata.get('so_hieu', ''),
                'ngay_ban_hanh': metadata.get('ngay_ban_hanh', ''),
                'co_quan_ban_hanh': metadata.get('co_quan_ban_hanh', ''),
                'phan': 'can_cu_phap_ly',
                'so_chuong': '',
                'ten_chuong': '',
                'so_dieu': '',
                'tieu_de': '',
                'so_khoan': '',
                'so_diem': '',
                'thu_tu': idx + 1,
                'noi_dung': can_cu.strip()
            })
    
    # Xử lý các chương, điều, khoản, điểm
    for chuong in data.get('chuong', []):
        so_chuong = chuong.get('so_chuong', '')
        ten_chuong = chuong.get('ten_chuong', '')
        
        for dieu in chuong.get('dieu', []):
            so_dieu = dieu.get('so_dieu', '')
            tieu_de = dieu.get('tieu_de', '')
            
            # Nếu có tiêu đề điều, thêm vào data
            if tieu_de.strip():
                flattened_data.append({
                    'loai_van_ban': metadata.get('loai_van_ban', ''),
                    'so_hieu': metadata.get('so_hieu', ''),
                    'ngay_ban_hanh': metadata.get('ngay_ban_hanh', ''),
                    'co_quan_ban_hanh': metadata.get('co_quan_ban_hanh', ''),
                    'phan': 'tieu_de_dieu',
                    'so_chuong': so_chuong,
                    'ten_chuong': ten_chuong,
                    'so_dieu': so_dieu,
                    'tieu_de': tieu_de,
                    'so_khoan': '',
                    'so_diem': '',
                    'thu_tu': 0,
                    'noi_dung': tieu_de.strip()
                })
            
            for khoan in dieu.get('khoan', []):
                so_khoan = khoan.get('so_khoan', '')
                noi_dung_khoan = khoan.get('noi_dung', '')
                
                # Thêm nội dung khoản
                if noi_dung_khoan.strip():
                    flattened_data.append({
                        'loai_van_ban': metadata.get('loai_van_ban', ''),
                        'so_hieu': metadata.get('so_hieu', ''),
                        'ngay_ban_hanh': metadata.get('ngay_ban_hanh', ''),
                        'co_quan_ban_hanh': metadata.get('co_quan_ban_hanh', ''),
                        'phan': 'khoan',
                        'so_chuong': so_chuong,
                        'ten_chuong': ten_chuong,
                        'so_dieu': so_dieu,
                        'tieu_de': tieu_de,
                        'so_khoan': so_khoan,
                        'so_diem': '',
                        'thu_tu': 0,
                        'noi_dung': noi_dung_khoan.strip()
                    })
                
                # Xử lý các điểm
                for diem_idx, diem in enumerate(khoan.get('diem', [])):
                    so_diem = diem.get('so_diem', '')
                    noi_dung_diem = diem.get('noi_dung', '')
                    
                    if noi_dung_diem.strip():
                        flattened_data.append({
                            'loai_van_ban': metadata.get('loai_van_ban', ''),
                            'so_hieu': metadata.get('so_hieu', ''),
                            'ngay_ban_hanh': metadata.get('ngay_ban_hanh', ''),
                            'co_quan_ban_hanh': metadata.get('co_quan_ban_hanh', ''),
                            'phan': 'diem',
                            'so_chuong': so_chuong,
                            'ten_chuong': ten_chuong,
                            'so_dieu': so_dieu,
                            'tieu_de': tieu_de,
                            'so_khoan': so_khoan,
                            'so_diem': so_diem,
                            'thu_tu': diem_idx + 1,
                            'noi_dung': noi_dung_diem.strip()
                        })
    
    # Tạo DataFrame
    df = pd.DataFrame(flattened_data)
    
    # Lưu ra file CSV nếu có đường dẫn
    if output_csv_path:
        df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
        print(f"Đã lưu dữ liệu vào {output_csv_path}")
    
    return df


def prepare_text_for_phobert(df: pd.DataFrame) -> List[str]:
    """
    Chuẩn bị danh sách văn bản để đưa vào phoBERT
    
    Args:
        df: DataFrame chứa dữ liệu đã làm phẳng
    
    Returns:
        List các câu văn bản
    """
    texts = df['noi_dung'].tolist()
    return texts


def create_context_text(df: pd.DataFrame) -> List[str]:
    """
    Tạo văn bản có thêm ngữ cảnh (chương, điều, khoản) để phoBERT hiểu rõ hơn
    
    Args:
        df: DataFrame chứa dữ liệu đã làm phẳng
    
    Returns:
        List các câu văn bản có ngữ cảnh
    """
    context_texts = []
    
    for _, row in df.iterrows():
        context_parts = []
        
        # Thêm thông tin cấu trúc
        if row['so_chuong']:
            context_parts.append(f"Chương {row['so_chuong']}")
        if row['so_dieu']:
            context_parts.append(f"Điều {row['so_dieu']}")
        if row['so_khoan']:
            context_parts.append(f"Khoản {row['so_khoan']}")
        if row['so_diem']:
            context_parts.append(f"Điểm {row['so_diem']}")
        
        # Tạo prefix ngữ cảnh
        if context_parts:
            context_prefix = " - ".join(context_parts) + ": "
        else:
            context_prefix = ""
        
        # Kết hợp ngữ cảnh và nội dung
        full_text = context_prefix + row['noi_dung']
        context_texts.append(full_text)
    
    return context_texts


def encode_with_phobert(texts: List[str], max_length: int = 256):
    """
    Mã hóa văn bản thành vector sử dụng phoBERT
    Yêu cầu: pip install transformers torch
    
    Args:
        texts: Danh sách văn bản cần mã hóa
        max_length: Độ dài tối đa của sequence
    
    Returns:
        Tensor chứa embeddings
    """
    from transformers import AutoModel, AutoTokenizer
    import torch
    
    # Load phoBERT model
    phobert = AutoModel.from_pretrained("vinai/phobert-base-v2")
    tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
    
    embeddings = []
    
    # Xử lý từng batch
    batch_size = 32
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        
        # Tokenize
        inputs = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt"
        )
        
        # Lấy embeddings
        with torch.no_grad():
            outputs = phobert(**inputs)
            # Sử dụng [CLS] token embedding hoặc mean pooling
            # [CLS] token:
            batch_embeddings = outputs.last_hidden_state[:, 0, :]
            # Hoặc mean pooling:
            # batch_embeddings = outputs.last_hidden_state.mean(dim=1)
        
        embeddings.append(batch_embeddings)
    
    # Kết hợp tất cả embeddings
    all_embeddings = torch.cat(embeddings, dim=0)
    
    return all_embeddings


# Ví dụ sử dụng
if __name__ == "__main__":
    # Đường dẫn file JSON
    json_file = r"f:\NghienCuuKhoaHoc\Data\pdf_to_json\124-cp.signed.-tôn giáopdf_v2.json"
    output_csv = r"f:\NghienCuuKhoaHoc\xldl\flattened_data.csv"
    
    # Bước 1: Làm phẳng dữ liệu
    print("Đang làm phẳng dữ liệu...")
    df = flatten_json_for_phobert(json_file, output_csv)
    print(f"Số lượng records: {len(df)}")
    print("\nCác cột trong DataFrame:")
    print(df.columns.tolist())
    print("\n5 dòng đầu tiên:")
    print(df.head())
    
    # Bước 2: Chuẩn bị text cho phoBERT
    print("\n" + "="*50)
    print("Chuẩn bị text cho phoBERT...")
    
    # Option 1: Chỉ lấy nội dung
    texts = prepare_text_for_phobert(df)
    print(f"Số lượng văn bản: {len(texts)}")
    print("Ví dụ văn bản đầu tiên:")
    print(texts)
    
    # Option 2: Lấy nội dung có ngữ cảnh
    context_texts = create_context_text(df)
    print("\nVí dụ văn bản có ngữ cảnh:")
    print(context_texts)
    
    # Bước 3: Encode với phoBERT (bỏ comment để chạy)
    print("\n" + "="*50)
    print("Để encode với phoBERT, cần cài đặt:")
    print("pip install transformers torch")
    print("\nSau đó bỏ comment phần code encode_with_phobert()")
    
    # Uncomment để chạy encoding:
    # print("\nĐang encode với phoBERT...")
    # embeddings = encode_with_phobert(texts[:100], max_length=256)  # Test với 100 câu đầu
    # print(f"Shape của embeddings: {embeddings.shape}")
    # # Lưu embeddings
    # torch.save(embeddings, 'phobert_embeddings.pt')
