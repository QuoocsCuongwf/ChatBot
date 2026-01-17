import json

# Đọc file output
with open('../Data/processed_json/127-cp.signed._tài sản côngpdf_processed.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("Metadata:", d['metadata'])
print("\nCác Chương:")
total_dieu = 0
for c in d['chuong']:
    print(f"  Chương {c['so_chuong']}: {c['ten_chuong']} - {len(c['dieu'])} điều")
    total_dieu += len(c['dieu'])
    for dieu in c['dieu']:  # Tất cả điều
        khoan_count = len(dieu.get('khoan', []))
        print(f"    - Điều {dieu['so_dieu']}: {dieu['tieu_de'][:50]}... ({khoan_count} khoản)")

print(f"\nTổng: {len(d['chuong'])} chương, {total_dieu} điều")
print("\n--- Căn cứ pháp lý ---")
for cc in d.get('can_cu_phap_ly', [])[:3]:
    print(f"  - {cc[:80]}...")
