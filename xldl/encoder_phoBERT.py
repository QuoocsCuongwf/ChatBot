from transformers import AutoTokenizer, AutoModel
import torch
import json
import numpy as np
import pickle  # Thêm thư viện pickle
from underthesea import word_tokenize
from load_env import load_env, get_env
import os

# Config & Load Model
load_env()
model_name = "vinai/phobert-base"
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading PhoBERT on {device}...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
model.to(device)
model.eval()

def preprocess(text):
    if not text: return ""
    return word_tokenize(text, format="text")

def split_and_embed(text, max_seq_length=256, overlap=32):
    # Tokenize (no special tokens)
    inputs = tokenizer(text, return_tensors="pt", add_special_tokens=False)
    input_ids = inputs["input_ids"][0]
    total_tokens = len(input_ids)

    # Sliding Window logic
    max_tokens_content = max_seq_length - 2  
    stride = max_tokens_content - overlap
    chunks_ids = []

    if total_tokens <= max_tokens_content:
        chunks_ids.append(input_ids)
    else:
        for i in range(0, total_tokens, stride):
            chunk = input_ids[i : i + max_tokens_content]
            chunks_ids.append(chunk)

    vectors = []
    sub_texts = []

    for chunk in chunks_ids:
        # Add special tokens manually: <s> + content + </s>
        full_input_ids = torch.cat([
            torch.tensor([tokenizer.cls_token_id]),
            chunk,
            torch.tensor([tokenizer.sep_token_id])
        ])

        input_ids_batch = full_input_ids.unsqueeze(0).to(device)
        attention_mask = torch.ones_like(input_ids_batch).to(device)

        with torch.no_grad():
            outputs = model(input_ids=input_ids_batch, attention_mask=attention_mask)

        # Mean Pooling (excluding CLS/SEP tokens)
        token_embeddings = outputs.last_hidden_state[:, 1:-1, :] 
        vec = token_embeddings.mean(dim=1).squeeze().cpu().numpy()

        # L2 Normalization
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        vectors.append(vec)
        sub_texts.append(tokenizer.decode(chunk, skip_special_tokens=True))

    return vectors, sub_texts

# Main execution
file_path = get_env("FILE_CHUNKS")
print(f"Reading file: {file_path}")

with open(file_path, "r", encoding="utf-8") as f:
    chunks = json.load(f)

final_embeddings = []
final_metadata = []

print(f"Processing {len(chunks)} documents...")

for idx, chunk in enumerate(chunks):
    raw_text = chunk.get("text", "")
    if not raw_text.strip(): continue

    preprocessed_text = preprocess(raw_text)
    vecs, segments = split_and_embed(preprocessed_text)
    
    if idx % 10 == 0:
        print(f"Doc {idx}: {len(vecs)} vectors")

    for i, vec in enumerate(vecs):
        final_embeddings.append(vec)
        
        new_meta = chunk.copy()
        new_meta["text"] = segments[i]
        new_meta["chunk_id"] = f"{idx}_{i}"
        final_metadata.append(new_meta)

# --- SAVE RESULTS ---
embeddings_matrix = np.array(final_embeddings)

# 1. Save separate files (optional backup)
embeddings_file = get_env("EMBEDDINGS_FILE")
metadata_file = get_env("METADATA_FILE")

if embeddings_file:
    np.save(embeddings_file, embeddings_matrix)
if metadata_file:
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(final_metadata, f, ensure_ascii=False, indent=2)

# 2. Save Combined Vector Store (.pkl)
vector_store_path = get_env("VECTOR_STORE")

if vector_store_path:
    # Ensure directory exists
    os.makedirs(os.path.dirname(vector_store_path), exist_ok=True)
    
    print(f"Saving combined vector store to: {vector_store_path}")
    
    store_data = {
        "embeddings": embeddings_matrix,
        "metadata": final_metadata
    }
    
    with open(vector_store_path, "wb") as f:
        pickle.dump(store_data, f)

print(f"Completed. Total vectors: {embeddings_matrix.shape[0]}")