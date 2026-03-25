"""Debug retrieval: trace exact ranking for problem queries."""
import json
import numpy as np
import sys
sys.path.insert(0, 'cross-encoder/generation')
sys.path.insert(0, '.')

# Load FAISS + metadata
import faiss
meta = json.load(open('vector_data/legal_hf_cosine/metadata.json', 'r', encoding='utf-8'))
index = faiss.read_index('vector_data/legal_hf_cosine/index.faiss')
print(f"FAISS: {index.ntotal} vectors, dim={index.d}")

# Load bi-encoder
from sentence_transformers import SentenceTransformer
bi_enc = SentenceTransformer('Quockhanh05/Vietnam_legal_embeddings')

queries = [
    "Thu tuc cap giay phep xay dung",
    "Muc phat doi voi hanh vi xay dung khong phep la bao nhieu",
    "Cong chuc lam cong tac ho tich o dia phuong",
]

for q in queries:
    print(f"\n{'='*60}")
    print(f"QUERY: {q}")
    print('='*60)
    
    # Bi-encoder search
    qvec = bi_enc.encode([q], normalize_embeddings=True)
    D, I = index.search(qvec.astype('float32'), 20)
    
    print(f"\n--- Bi-encoder top-10 (cosine) ---")
    for rank in range(10):
        idx = I[0][rank]
        score = D[0][rank]
        m = meta[idx]
        md = m.get('metadata', m)
        vb = md.get('van_ban', '')[:50]
        dieu = md.get('dieu', '?')
        text_short = m['text'][:80]
        print(f"  #{rank+1} idx={idx} cos={score:.4f} | Dieu {dieu} ({vb}) | {text_short}")
    
    # Check: where are the CORRECT chunks?
    print(f"\n--- Where are relevant chunks? ---")
    if 'xay dung' in q.lower() or 'giay phep' in q.lower():
        target_ids = [i for i, m in enumerate(meta) 
                     if 'giấy phép' in m['text'].lower() and 'xây' in m['text'].lower()]
        for tid in target_ids:
            # Find rank
            rank_pos = np.where(I[0] == tid)[0]
            if len(rank_pos) > 0:
                print(f"  Chunk {tid} found at rank #{rank_pos[0]+1}")
            else:
                # Compute cosine manually
                tvec = index.reconstruct(tid)
                cos = float(np.dot(qvec[0], tvec))
                print(f"  Chunk {tid} NOT in top-20 (cosine={cos:.4f}) | {meta[tid]['text'][:80]}")
    
    if 'ho tich' in q.lower():
        target_ids = [i for i, m in enumerate(meta) if 'hộ tịch' in m['text'].lower()]
        for tid in target_ids[:5]:
            rank_pos = np.where(I[0] == tid)[0]
            if len(rank_pos) > 0:
                print(f"  Chunk {tid} found at rank #{rank_pos[0]+1}")
            else:
                tvec = index.reconstruct(tid)
                cos = float(np.dot(qvec[0], tvec))
                print(f"  Chunk {tid} NOT in top-20 (cosine={cos:.4f}) | {meta[tid]['text'][:60]}")
