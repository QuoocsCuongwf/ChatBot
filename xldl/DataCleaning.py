filePath="../Data/VanBanGoc_142-2025-nd-cp.pdf"
import re
import PyPDF2
import sys
sys.stdout.reconfigure(encoding='utf-8')
print("Đang bắt đầu xử lý...")
text = ""
import pdfplumber
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"D:\apps\OCR\tesseract.exe"

from PIL import Image

with pdfplumber.open(filePath) as pdf:
    for page in pdf.pages:
        img = page.to_image(resolution=300).original
        text += pytesseract.image_to_string(img, lang="vie")


print(f"--> Đọc xong PDF. Tổng số ký tự: {len(text)}")
chunks = re.split(r'(\w+\s+\d+[\.:]?)', text)
json_data = []
for i in range(1, len(chunks), 2):
    header = chunks[i].strip()        # Lấy tiêu đề (VD: "Điều 1.")
    content = chunks[i+1].strip()  
    header_lower = header.lower()
    valid_keywords = ['điều', 'điêu', 'ủeu', 'đieu']
    
    # 3. Kiểm tra: Nếu không chứa từ nào trong danh sách trên -> Bỏ qua (continue)
    is_valid = False
    for key in valid_keywords:
        if key in header_lower:
            is_valid = True
            break
            
    if not is_valid:
        continue  # Bỏ qua vòng lặp này, nhảy sang chunk tiếp theo
    # -----------------------------
    so_hieu = header.split()[1].replace('.', '')
    print(f"Bắt được: '{header}'")
    # 2. Xử lý Topic: Lấy dòng đầu tiên của nội dung làm chủ đề
    lines = content.split('\n')
    topic = lines[0].strip()       # Dòng 1 là tiêu đề
    real_content = "\n".join(lines[1:]).strip() # Các dòng sau là nội dung thực

    # 3. Tạo ID
    id_moi = f"dieu_{so_hieu}"
# --- THÊM ĐOẠN NÀY ĐỂ CHẶN TRÙNG LẶP ---
    # Kiểm tra xem ID này đã có trong danh sách chưa
    da_co = False
    for x in json_data:
        if x['id'] == id_moi:
            da_co = True
            break
            
    if da_co:
        continue # Nếu có rồi thì bỏ qua, không thêm nữa
    # ---------------------------------------
    item = {
        "id": id_moi,
        "source": "Nghị định 142/2025/NĐ-CP",
        "topic": topic,
        "content": real_content if real_content else content # Phòng trường hợp điều luật quá ngắn
    }
    json_data.append(item)
print(f"--> Cắt xong. Tổng số đoạn (chunks): {len(chunks)}")
# In ra danh sách các ID đã lấy được
found_ids = [item['id'] for item in json_data]
print("Các điều đã tìm thấy:", found_ids)
# Hàm nhỏ để tìm và in nội dung
def soi_duoi(id_can_tim):
    for item in json_data:
        if item['id'] == id_can_tim:
            print(f"\n--- Cuối nội dung {id_can_tim} ---")
            # In 200 ký tự cuối cùng để xem Điều tiếp theo viết thế nào
            print(item['content'][-200:]) 
            return

# 1. Soi xem Điều 7, 38, 41 đang trốn ở đâu
soi_duoi("dieu_6")   # Điều 7 sẽ nằm ở cuối Điều 6
soi_duoi("dieu_37")  # Điều 38 sẽ nằm ở cuối Điều 37
soi_duoi("dieu_40")  # Điều 41 sẽ nằm ở cuối Điều 40

# 2. Soi xem 2 ông Điều 32 khác nhau thế nào
print("\n--- So sánh 2 Điều 32 ---")
count = 1
for item in json_data:
    if item['id'] == "dieu_32":
        print(f"Điều 32 (lần {count}): {item['topic']}")
        count += 1