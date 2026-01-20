"""
Encode chunks văn bản pháp luật với PhoBERT
"""

import json
import torch
from transformers import AutoTokenizer, AutoModel
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding='utf-8')


class PhoBERTEncoder:
    """Encoder sử dụng PhoBERT"""
    
    def __init__(self, model_name='vinai/phobert-base'):
        """Khởi tạo PhoBERT"""
        print(f"Đang load PhoBERT: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        print("✅ PhoBERT đã sẵn sàng!")
    
    def encode_text(self, text: str) -> list:
        """Encode một đoạn text thành vector embedding"""
        # Tokenize
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=256,
            return_tensors='pt'
        )
        
        # Encode
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Lấy embedding (mean pooling của last hidden state)
        embeddings = outputs.last_hidden_state.mean(dim=1)
        
        return embeddings[0].tolist()
    
    def encode_chunks(self, chunks_file: str, output_file: str):
        """Encode tất cả chunks trong file"""
        print(f"\n📂 Đang đọc chunks: {chunks_file}")
        
        # Đọc chunks
        with open(chunks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = data.get('chunks', [])
        print(f"  - Tổng số chunks: {len(chunks)}")
        
        # Encode từng chunk
        print("\n🔄 Đang encode...")
        encoded_chunks = []
        
        for i, chunk in enumerate(chunks):
            if (i + 1) % 10 == 0:
                print(f"  Đã encode: {i+1}/{len(chunks)}")
            
            # Encode content
            embedding = self.encode_text(chunk['content'])
            
            # Thêm embedding vào chunk
            encoded_chunk = chunk.copy()
            encoded_chunk['embedding'] = embedding
            encoded_chunks.append(encoded_chunk)
        
        # Lưu kết quả
        result = {
            'source_file': chunks_file,
            'model': 'vinai/phobert-base',
            'embedding_dim': len(encoded_chunks[0]['embedding']) if encoded_chunks else 0,
            'total_chunks': len(encoded_chunks),
            'chunks': encoded_chunks
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Đã lưu embeddings: {output_file}")
        print(f"  - Số chunks: {len(encoded_chunks)}")
        print(f"  - Embedding dim: {result['embedding_dim']}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Encode chunks với PhoBERT')
    parser.add_argument('input', help='File JSON chunks')
    parser.add_argument('-o', '--output', help='File JSON output embeddings', required=True)
    parser.add_argument('-m', '--model', default='vinai/phobert-base',
                       help='PhoBERT model name (default: vinai/phobert-base)')
    
    args = parser.parse_args()
    
    # Encode
    encoder = PhoBERTEncoder(model_name=args.model)
    encoder.encode_chunks(args.input, args.output)


if __name__ == '__main__':
    main()
