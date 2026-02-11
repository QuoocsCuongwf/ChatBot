import json
import random
import requests
from xldl.load_env import load_env, get_env

load_env()

API_URL = "http://localhost:8080/completion"


def ask_llm(text):
    prompt = f"""
Bạn là người dân đang tìm hiểu pháp luật Việt Nam.
Dựa vào đoạn luật sau, hãy tạo 5 câu hỏi người dùng có thể hỏi.
Mỗi câu 1 dòng, tự nhiên.

ĐOẠN LUẬT:
\"{text}\"
"""

    response = requests.post(API_URL, json={
        "prompt": prompt,
        "n_predict": 150,
        "temperature": 0.7,
        "stop": ["\n\n"]
    })

    return response.json()["content"]


# LOAD CHUNKS
with open(get_env("FILE_CHUNKS"), "r", encoding="utf-8") as f:
    chunks = json.load(f)

dataset = []

# POSITIVE
for i, chunk in enumerate(chunks):
    print(f"Processing chunk {i+1}/{len(chunks)}")

    queries_text = ask_llm(chunk["text"])
    queries = [q.strip("-• ").strip() for q in queries_text.split("\n") if len(q.strip()) > 10]

    for q in queries:
        dataset.append({
            "query": q,
            "passage": chunk["text"],
            "label": 1
        })

# NEGATIVE
neg_data = []
for item in dataset:
    while True:
        neg_chunk = random.choice(chunks)
        if neg_chunk["text"] != item["passage"]:
            break

    neg_data.append({
        "query": item["query"],
        "passage": neg_chunk["text"],
        "label": 0
    })

dataset.extend(neg_data)

# SAVE
with open(get_env("DATASET_FILE"), "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print("Done. Total samples:", len(dataset))
