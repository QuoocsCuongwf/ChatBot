import glob
import json
import os

folder_path = "./output_nghidinh"   # thư mục chứa các file json

all_data = []
chunky=[]

for file_path in glob.glob(os.path.join(folder_path, "*final.json")):

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)   # nếu file là JSON chuẩn
            all_data.append(data)
        except json.JSONDecodeError:
            print("❌ Lỗi JSON:", file_path)

import json
import glob

def build_chunks_from_file(path):
    chunks = []

    with open(path, "r", encoding="utf-8") as f:
        vb = json.load(f)

    ten_vb = vb.get("ten_van_ban", "")

    for chuong in vb.get("chuong", []):
        chuong_so = chuong.get("chuong_so")

        for dieu in chuong.get("dieu", []):
            dieu_so = dieu.get("dieu_so")
            dieu_nd = dieu.get("noi_dung", "")
            if not dieu.get("khoan"):
                # 🔹 Không có khoản → chunk ở mức điều
                text = (
                    f"Điều {dieu_so} – {ten_vb}\n"
                    f"{dieu_nd}"
                )

                chunks.append({
                    "text": text,
                    "metadata": {
                        "van_ban": ten_vb,
                        "chuong": chuong_so,
                        "dieu": dieu_so,
                        "khoan": None,
                        "diem": None,
                        "source_file": path
                    }
                })
                continue    

            for khoan in dieu.get("khoan", []):
                khoan_so = khoan.get("khoan_so")
                khoan_nd = khoan.get("noi_dung", "")

                # 🔹 Nếu có điểm → chunk theo điểm
                if khoan.get("diem"):
                    for diem in khoan["diem"]:
                        diem_so = diem.get("diem_so")
                        diem_nd = diem.get("noi_dung", "")

                        text = (
                            f"Điểm {diem_so} Khoản {khoan_so} Điều {dieu_so} – {ten_vb}\n"
                            f"{diem_nd}"
                        )

                        chunks.append({
                            "text": text,
                            "metadata": {
                                "van_ban": ten_vb,
                                "chuong": chuong_so,
                                "dieu": dieu_so,
                                "khoan": khoan_so,
                                "diem": diem_so,
                                "source_file": path
                            }
                        })

                # 🔹 Không có điểm → chunk ở mức khoản
                else:
                    text = (
                        f"Khoản {khoan_so} Điều {dieu_so} – {ten_vb}\n"
                        f"{khoan_nd}"
                    )

                    chunks.append({
                        "text": text,
                        "metadata": {
                            "van_ban": ten_vb,
                            "chuong": chuong_so,
                            "dieu": dieu_so,
                            "khoan": khoan_so,
                            "diem": None,
                            "source_file": path
                        }
                    })

    return chunks
file_chunks = build_chunks_from_file(file_path)
chunky.extend(file_chunks)
output_path = "./output_nghidinh/chunks.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(chunky, f, ensure_ascii=False, indent=2)

print(f"✅ Đã lưu {len(chunky)} chunks vào {output_path}")
print(f"✅ Đã xử lý {len(all_data)} file JSON.")
print(f"✅ Tổng số chunk tạo được: {len(chunky)}")
print(f"✅ Đã xử lý {len(all_data)} file JSON.")
print(f"✅ Tổng số chunk tạo được: {len(chunky)}")

