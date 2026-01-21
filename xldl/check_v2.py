import json

with open('../Data/DataPhuc/ThongTu/processed/09-bnv-v2/09-bnv_final.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"Tổng số Chương: {len(data['chuong'])}")
print()

for i, chuong in enumerate(data['chuong'], 1):
    print(f"Chương {chuong['so_chuong']}: {chuong['ten_chuong']}")
    print(f"  Số Điều: {len(chuong['dieu'])}")
    for dieu in chuong['dieu'][:3]:
        print(f"    Điều {dieu['so_dieu']}: {dieu['noi_dung'][:60]}...")
    if len(chuong['dieu']) > 3:
        print(f"    ... và {len(chuong['dieu']) - 3} điều khác")
    print()
