import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer

# CONFIG 
CHUNKS_PATH = "output_nghidinh/chunks_clean.json"
OUT_DIR = os.path.join("vector_data", "legal_hf")   # thư mục output riêng

MODEL_NAME = "Quockhanh05/Vietnam_legal_embeddings"

os.makedirs(OUT_DIR, exist_ok=True)

# = LOAD DATA 
chunks = json.load(open(CHUNKS_PATH, "r", encoding="utf-8"))
texts = [c["text"] for c in chunks]

# LOAD ENCODER 
encoder = SentenceTransformer(
    "Quockhanh05/Vietnam_legal_embeddings",
    device="cuda"   # 👈 BẬT GPU
)

#  ENCODE 
embeddings = encoder.encode(
    texts,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True   
).astype("float32")

# =SAVE =
np.save(f"{OUT_DIR}/embeddings.npy", embeddings)

with open(f"{OUT_DIR}/metadata.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)


print("✅ Done encoding:", embeddings.shape)
