import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

DOMAIN_KW = {
    "tư pháp": ["tư pháp", "hộ tịch", "chứng thực", "nuôi con nuôi", "bồi thường nhà nước", "luật hộ tịch"],
    "tài chính": ["tài chính", "ngân sách", "thuế", "phí", "lệ phí", "kho bạc"],
    "nội vụ": ["nội vụ", "cán bộ", "công chức", "biên chế"],
    "tài nguyên": ["đất đai", "sổ đỏ", "tài nguyên", "môi trường"],
}
DOMAIN_TO_MINISTRY = {
    "tư pháp": "bộ tư pháp",
    "tài chính": "bộ tài chính",
    "y tế": "bộ y tế",
    "nội vụ": "bộ nội vụ",
    "tài nguyên": "bộ tài nguyên",
}
def detect_domain(question: str):
    q = question.lower()
    hits = []
    for dom, kws in DOMAIN_KW.items():
        for kw in kws:
            if kw in q:
                hits.append(dom)
                break
    # ưu tiên 1 domain rõ nhất (nếu nhiều, lấy cái đầu)
    return hits[0] if hits else ""

def load_chunks(path):
    data = json.load(open(path, "r", encoding="utf-8"))
    if isinstance(data, dict) and "chunks" in data:
        data = data["chunks"]
    return data

def retrieve_joint(
    question,
    topk=5,
    topn=600,
    chunks_path=r"D:\GitHub\ChatBot\output_nghidinh\chunks_clean_norm.json",
    index_path=r"D:\GitHub\ChatBot\vector_data\legal_hf_cosine\index.faiss",
    model_name="Quockhanh05/Vietnam_legal_embeddings",
    device="cuda",
):
    chunks = load_chunks(chunks_path)
    index  = faiss.read_index(index_path)
    encoder = SentenceTransformer(model_name, device=device)

    q_emb = encoder.encode([question], normalize_embeddings=True).astype("float32")
    scores, ids = index.search(q_emb, topn)
    scores, ids = scores[0].tolist(), ids[0].tolist()

    # 1) auto detect domain
    dom = detect_domain(question)

    # 2) define filter keywords from domain
    filter_kws = DOMAIN_KW.get(dom, [])
    filter_kws = [k.lower() for k in filter_kws]

    # 3) candidates after filtering (if dom detected)
    filtered = []
    if dom:
        for idx, sc in zip(ids, scores):
            if idx < 0 or idx >= len(chunks):
                continue
            ch = chunks[idx]
            meta = ch.get("metadata", {})
            vb = str(meta.get("van_ban","")).lower()
            tx = str(ch.get("text","")).lower()

            # pass if any domain keyword appears in van_ban or text
            ministry = DOMAIN_TO_MINISTRY.get(dom, "")
            if ministry:
                # khóa theo đúng bộ
                if ministry not in vb:
                    continue

            # (optional) nếu query có cụm đặc thù thì bắt buộc match
            q_lower = question.lower()
            if "lệ phí trước bạ" in q_lower:
                if "lệ phí trước bạ" not in tx and "trước bạ" not in tx:
                    continue

            filtered.append((idx, float(sc)))

    # 4) fallback logic
    if dom and len(filtered) > 0:
        chosen = sorted(filtered, key=lambda x: x[1], reverse=True)[:topk]
        mode = f"FILTERED({dom})"
    else:
        chosen = [(idx, float(sc)) for idx, sc in zip(ids, scores) if 0 <= idx < len(chunks)][:topk]
        mode = "BASE(no-filter)" if not dom else f"FALLBACK(no-hit:{dom})"

    # 5) build results
    results = []
    for rank, (idx, sc) in enumerate(chosen, start=1):
        ch = chunks[idx]
        meta = ch.get("metadata", {})
        khoan = meta.get("khoan", "")
        if khoan is None: khoan = ""
        results.append({
            "rank": rank,
            "score": sc,
            "text": ch.get("text",""),
            "metadata": {
                "van_ban": meta.get("van_ban",""),
                "chuong": meta.get("chuong",""),
                "dieu": meta.get("dieu",""),
                "khoan": khoan,
                "nguon": meta.get("nguon",""),
                "chunk_id": idx
            }
        })

    print("="*90)
    print("MODE:", mode, "| topn=", topn, "| topk=", topk)
    print("QUESTION:", question)
    print("="*90)
    for r in results:
        md = r["metadata"]
        k = md["khoan"] if md["khoan"] not in ("", None) else "-"
        print(f"[{r['rank']}] score={r['score']:.4f} | {md['van_ban']} | Ch {md['chuong']} | Điều {md['dieu']} | Khoản {k} | id={md['chunk_id']}")
        print("   ", r["text"].replace("\n"," ")[:240], "...")
        print("-"*90)

    return {"mode": mode, "question": question, "results": results}

retrieve_joint("Thẩm quyền của cấp xã trong lĩnh vực tư pháp là gì?", topn=600, topk=5)
retrieve_joint("Cấp xã được giao nhiệm vụ gì về lệ phí trước bạ?", topn=600, topk=5)