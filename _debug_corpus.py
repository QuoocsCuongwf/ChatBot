import json

meta = json.load(open('vector_data/legal_hf_cosine/metadata.json', 'r', encoding='utf-8'))

# Check: does the corpus HAVE chunks about specific topics?
topics = {
    'xay dung + phep': lambda t: 'xây dựng' in t and 'phép' in t,
    'phat + xay': lambda t: 'phạt' in t and 'xây' in t,
    'giay phep + xay': lambda t: 'giấy phép' in t and 'xây' in t,
    'xu phat hanh chinh': lambda t: 'xử phạt' in t,
    'ho tich': lambda t: 'hộ tịch' in t,
    'cuong che pha do': lambda t: 'cưỡng chế' in t or 'phá dỡ' in t,
    'xay dung khong phep': lambda t: 'không phép' in t or 'không có giấy phép' in t,
}

for label, fn in topics.items():
    hits = [i for i, m in enumerate(meta) if fn(m.get('text', '').lower())]
    print(f'{label}: {len(hits)} chunks')
    for i in hits[:2]:
        vb = meta[i].get('metadata', meta[i]).get('van_ban', '')[:60]
        print(f'  [{i}] ({vb}) {meta[i]["text"][:100]}')
    print()

# Show what Bộ Xây dựng docs contain
print('=== Chunks from Bo Xay dung ===')
xd_chunks = [i for i, m in enumerate(meta) 
             if 'Xây dựng' in m.get('metadata', m).get('van_ban', '')]
print(f'Total: {len(xd_chunks)} chunks')
for i in xd_chunks[:5]:
    print(f'  [{i}] Dieu {meta[i].get("metadata",meta[i]).get("dieu","?")} | {meta[i]["text"][:100]}')
