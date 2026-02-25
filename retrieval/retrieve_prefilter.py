import json
import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS_PATH = r"D:\GitHub\ChatBot\output_nghidinh\chunks_clean_norm.json"
EMB_PATH    = r"D:\GitHub\ChatBot\vector_data\legal_hf_cosine\embeddings.npy"
MODEL_NAME  = "Quockhanh05/Vietnam_legal_embeddings"
DEVICE      = "cpu"  # chạy ổn rồi đổi cuda

# load once
chunks = json.load(open(CHUNKS_PATH, "r", encoding="utf-8"))
if isinstance(chunks, dict) and "chunks" in chunks:
    chunks = chunks["chunks"]

emb = np.load(EMB_PATH).astype("float32")  # (N, d)
encoder = SentenceTransformer(MODEL_NAME, device=DEVICE)

DOMAIN_TO_MINISTRY = {
    "tư pháp": "bộ tư pháp",
    "tài chính": "bộ tài chính",
    "y tế": "bộ y tế",
    "nội vụ": "bộ nội vụ",
    "tài nguyên": "bộ tài nguyên",
}

DOMAIN_KW = {
    "tư pháp": ["tư pháp", "hộ tịch", "chứng thực", "nuôi con nuôi"],
    "tài chính": ["tài chính", "ngân sách", "thuế", "phí", "lệ phí", "lệ phí trước bạ"],
    "y tế": ["y tế", "khám chữa bệnh", "bảo hiểm y tế"],
    "nội vụ": ["nội vụ", "cán bộ", "công chức"],
    "tài nguyên": ["đất đai", "môi trường", "tài nguyên"],
}

def detect_domain(q: str) -> str:
    ql = q.lower()
    for dom, kws in DOMAIN_KW.items():
        if any(k in ql for k in kws):
            return dom
    return ""

def retrieve_prefilter_ministry(question: str, topk=5, ministry=""):
    q = encoder.encode([question], normalize_embeddings=True).astype("float32")[0]  # (d,)

    # 1) prefilter ids
    if ministry:
        key = ministry.lower()
        ids = [i for i,c in enumerate(chunks) if key in c.get("metadata",{}).get("van_ban","").lower()]
    else:
        ids = list(range(len(chunks)))

    if not ids:
        print("❌ No chunks match ministry filter:", ministry)
        return []

    # 2) rank by cosine (dot product)
    sub = emb[ids]          # (M, d)
    scores = sub @ q        # (M,)
    top_idx = np.argsort(-scores)[:topk]

    results = []
    for rank, j in enumerate(top_idx, 1):
        cid = ids[int(j)]
        c = chunks[cid]
        m = c.get("metadata", {})
        khoan = m.get("khoan", "")
        if khoan is None: khoan = ""
        results.append({
            "rank": rank,
            "score": float(scores[int(j)]),
            "text": c.get("text",""),
            "metadata": {
                "van_ban": m.get("van_ban",""),
                "chuong": m.get("chuong",""),
                "dieu": m.get("dieu",""),
                "khoan": khoan,
                "chunk_id": cid
            }
        })

    print("="*90)
    print("MODE: PREFILTER_MINISTRY |", ministry, "| topk=", topk)
    print("QUESTION:", question)
    print("="*90)
    for r in results:
        md = r["metadata"]
        k = md["khoan"] if md["khoan"] not in ("", None) else "-"
        print(f"[{r['rank']}] score={r['score']:.4f} | {md['van_ban']} | Ch {md['chuong']} | Điều {md['dieu']} | Khoản {k} | id={md['chunk_id']}")
        print("   ", r["text"].replace("\n"," ")[:240], "...")
        print("-"*90)

    return results

def retrieve_auto(question: str, topk=5):
    dom = detect_domain(question)
    ministry = DOMAIN_TO_MINISTRY.get(dom, "")
    if ministry:
        return retrieve_prefilter_ministry(question, topk=topk, ministry=ministry)
    else:
        # nếu không đoán được domain, fallback search toàn bộ
        return retrieve_prefilter_ministry(question, topk=topk, ministry="")
if __name__ == "__main__":
    retrieve_auto("Cấp xã được giao nhiệm vụ gì về lệ phí trước bạ?", topk=5)       