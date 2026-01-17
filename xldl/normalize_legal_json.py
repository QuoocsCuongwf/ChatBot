import json
import re
from tqdm import tqdm
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ---------------- OCR FIX ----------------
OCR_FIX = {
    "quần": "quản",
    "Quần": "Quản",
    "lý": "lý",
    "Tài sắn": "Tài sản",
    "tài sắn": "tài sản",
    "thâm": "thẩm",
    "quyên": "quyền",
    "Hiên": "Hiến",
    "tặc": "tắc",
    "phẩn": "phân",
    "chinh": "chính",
    "Chinh": "Chính",
    "uy": "ủy",
    "Uy": "Ủy",
    "quộc": "quốc",
    "kêt": "kết",
    "câu": "cấu",
    "hạ tằng": "hạ tầng",
    "sắn": "sản",
    "sô": "số",
    "quên": "quyền"
}

def clean_text(text):
    if not text:
        return ""
    for k, v in OCR_FIX.items():
        text = text.replace(k, v)

    text = re.sub(r"[¡\[\]„_€¬•]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def normalize_chuong(s):
    if s in ["J", "l", "I"]:
        return "I"
    if s in ["JJ", "II"]:
        return "II"
    if s == "IV":
        return "IV"
    return s

# ---------------- LOAD ----------------
with open("F:\\NghienCuuKhoaHoc\\Data\\DataPhuc\\127-cp.signed._tài sản côngpdf_scan_processed.json", encoding="utf-8") as f:
    data = json.load(f)

# ---------------- METADATA ----------------
meta = data.get("metadata", {})
for k in meta:
    if isinstance(meta[k], str):
        meta[k] = clean_text(meta[k])

# ---------------- NORMALIZE TREE ----------------
new_chuong = []

for c in tqdm(data["chuong"], desc="Processing chapters"):
    chuong = {
        "so_chuong": normalize_chuong(c["so_chuong"]),
        "ten_chuong": clean_text(c["ten_chuong"]),
        "dieu": []
    }

    for d in c["dieu"]:
        dieu = {
            "so_dieu": d["so_dieu"],
            "tieu_de": clean_text(d.get("tieu_de", "")),
            "khoan": []
        }

        for k in d.get("khoan", []):
            khoan = {
                "so_khoan": k.get("so_khoan"),
                "noi_dung": clean_text(k.get("noi_dung", "")),
                "diem": []
            }

            for m in k.get("diem", []):
                diem = {
                    "so_diem": m.get("so_diem"),
                    "noi_dung": clean_text(m.get("noi_dung", ""))
                }
                khoan["diem"].append(diem)

            dieu["khoan"].append(khoan)

        chuong["dieu"].append(dieu)

    new_chuong.append(chuong)

# ---------------- SAVE ----------------
out = {
    "metadata": meta,
    "chuong": new_chuong
}

with open("127_2025_NDCP_normalized.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("Saved to 127_2025_NDCP_normalized.json")
