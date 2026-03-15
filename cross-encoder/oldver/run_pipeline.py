"""
run_pipeline.py — Cross-Encoder Reranker Pipeline for VN Legal Chatbot
Usage:
    ./venv/python.exe run_pipeline.py --phase ALL --seed 42
    ./venv/python.exe run_pipeline.py --phase A --max_rows 2000
    ./venv/python.exe run_pipeline.py --phase C --epochs 2 --batch_size 16
    ./venv/python.exe run_pipeline.py --phase ALL --resume
"""

import argparse
import json
import os
import sys
import time
import re
import csv
import random
import shutil
from datetime import datetime
from pathlib import Path
from collections import Counter

# ─────────────────────────────────────────────
# 0. CONFIG & PATHS
# ─────────────────────────────────────────────
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
OUT_DIR  = ROOT / "outputs"
EDA_DIR  = OUT_DIR / "eda"
EVAL_DIR = OUT_DIR / "eval"
MDL_DIR  = OUT_DIR / "models"
TMP_DIR  = OUT_DIR / "tmp"
LOG_DIR  = OUT_DIR / "logs"

TRAIN_FILE    = DATA_DIR / "train.jsonl"
DEV_FILE      = DATA_DIR / "dev.jsonl"
TRAIN_NEG     = DATA_DIR / "train_with_neg.jsonl"

MODEL_OUT     = MDL_DIR / "cross_encoder_v1"
EVAL_QA_FILE  = EVAL_DIR / "eval_qa.jsonl"
DEV_NEG_FILE  = EVAL_DIR / "dev_with_neg.jsonl"
FAISS_INDEX   = TMP_DIR / "faiss.index"
FAISS_MAP     = TMP_DIR / "faiss_mapping.jsonl"
CLASS_METRICS = EVAL_DIR / "dev_classification_metrics.json"
RERANK_CSV    = EVAL_DIR / "rerank_metrics.csv"
PIPE_RESULTS  = EVAL_DIR / "pipeline_results.jsonl"
PIPE_SUM_CSV  = EVAL_DIR / "pipeline_summary.csv"
PIPE_SUM_MD   = EVAL_DIR / "pipeline_summary.md"
DELIVERABLES  = OUT_DIR / "DELIVERABLES.md"

BASE_CE_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
BASE_BI_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

CJK_RE = re.compile(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]')

# ─────────────────────────────────────────────
# 1. CLI
# ─────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="VN Legal Chatbot Pipeline")
    p.add_argument("--phase", default="ALL",
                   choices=["A","B","C","D","E","F","ALL"])
    p.add_argument("--resume",      action="store_true")
    p.add_argument("--seed",        type=int, default=42)
    p.add_argument("--max_rows",    type=int, default=None)
    p.add_argument("--epochs",      type=int, default=3)
    p.add_argument("--batch_size",  type=int, default=32)
    p.add_argument("--max_length",  type=int, default=256)
    p.add_argument("--topN",        type=int, default=50)
    p.add_argument("--eval_n",      type=int, default=50)
    return p.parse_args()

# ─────────────────────────────────────────────
# 2. UTILITIES
# ─────────────────────────────────────────────
def makedirs():
    for d in [EDA_DIR/"plots", EVAL_DIR, MDL_DIR, TMP_DIR, LOG_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def load_jsonl(path, max_rows=None):
    """Safe JSONL loader — skips malformed lines."""
    rows, errors = [], 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if max_rows and i >= max_rows:
                break
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                errors += 1
    if errors:
        log(f"  ⚠ {errors} malformed lines skipped in {path.name}")
    return rows

def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def write_done(phase, outputs, extra=None):
    marker = {
        "phase": phase,
        "timestamp": datetime.now().isoformat(),
        "outputs": [str(o) for o in outputs],
    }
    if extra:
        marker.update(extra)
    p = LOG_DIR / f"DONE_{phase}.json"
    p.write_text(json.dumps(marker, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"  ✓ Done marker written → {p}")

def check_done(phase, resume):
    """Return True if phase can be skipped (resume mode + all outputs exist)."""
    if not resume:
        return False
    marker = LOG_DIR / f"DONE_{phase}.json"
    if not marker.exists():
        return False
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
        missing = [o for o in data.get("outputs", []) if not Path(o).exists()]
        if missing:
            log(f"  Resume: DONE_{phase}.json exists but missing outputs: {missing}")
            return False
        log(f"  ⏭  Phase {phase} skipped (resume, all outputs present)")
        return True
    except Exception:
        return False

def count_cjk(text):
    return len(CJK_RE.findall(text))

def env_info():
    try:
        import torch
        cuda = torch.cuda.is_available()
        gpu  = torch.cuda.get_device_name(0) if cuda else "N/A"
        vram = round(torch.cuda.get_device_properties(0).total_memory/(1024**3),1) if cuda else 0
    except Exception:
        cuda, gpu, vram = False, "N/A", 0
    try:
        import psutil
        ram = round(psutil.virtual_memory().total/(1024**3),1)
    except Exception:
        ram = "N/A"
    log(f"  Python {sys.version.split()[0]} | CUDA={cuda} | GPU={gpu} | VRAM={vram}GB | RAM={ram}GB")

# ─────────────────────────────────────────────
# 3. PHASE A — EDA & Sanity Check
# ─────────────────────────────────────────────
def phase_a(args):
    log("=" * 60)
    log("PHASE A: EDA & Sanity Check")
    log("=" * 60)
    env_info()

    datasets = {
        "train":    (TRAIN_FILE, load_jsonl(TRAIN_FILE, args.max_rows)),
        "dev":      (DEV_FILE,   load_jsonl(DEV_FILE,   args.max_rows)),
        "train_neg":(TRAIN_NEG,  load_jsonl(TRAIN_NEG,  args.max_rows)),
    }

    required_fields = ["query", "passage", "label", "meta"]
    meta_fields     = ["van_ban", "dieu", "khoan", "chunk_index"]

    summary_rows = []

    for name, (path, rows) in datasets.items():
        log(f"  Analyzing {name} ({len(rows)} rows) ...")
        pos = sum(1 for r in rows if r.get("label") == 1)
        neg = sum(1 for r in rows if r.get("label") == 0)

        # missing fields
        missing_fields = sum(
            1 for r in rows
            if any(f not in r for f in required_fields)
            or any(f not in r.get("meta", {}) for f in meta_fields)
        )

        # label conflicts
        seen = {}
        conflicts = 0
        for r in rows:
            key = (r.get("query",""), r.get("passage",""))
            lbl = r.get("label")
            if key in seen and seen[key] != lbl:
                conflicts += 1
            seen[key] = lbl

        # CJK queries
        cjk_count = sum(1 for r in rows if count_cjk(r.get("query","")) >= 3)

        # duplicate (query, passage) pairs
        pair_counts = Counter((r.get("query",""), r.get("passage","")) for r in rows)
        dup_pairs   = sum(1 for c in pair_counts.values() if c > 1)

        # lengths
        q_lens = [len(r.get("query","")) for r in rows]
        p_lens = [len(r.get("passage","")) for r in rows]
        avg_q  = round(sum(q_lens)/len(q_lens), 1) if q_lens else 0
        avg_p  = round(sum(p_lens)/len(p_lens), 1) if p_lens else 0

        log(f"    rows={len(rows)}, pos={pos}, neg={neg}, conflicts={conflicts}, "
            f"cjk={cjk_count}, dup_pairs={dup_pairs}, missing_fields={missing_fields}")

        summary_rows.append({
            "name": name, "rows": len(rows), "pos": pos, "neg": neg,
            "label_conflicts": conflicts, "cjk_queries": cjk_count,
            "dup_pairs": dup_pairs, "missing_fields": missing_fields,
            "avg_q_len": avg_q, "avg_p_len": avg_p,
        })

        # store for plots
        datasets[name] = (path, rows, summary_rows[-1], q_lens, p_lens)

    # ── Write summary.csv ──
    csv_path = EDA_DIR / "summary.csv"
    fields = ["name","rows","pos","neg","label_conflicts","cjk_queries",
              "dup_pairs","missing_fields","avg_q_len","avg_p_len"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(summary_rows)
    log(f"  Saved {csv_path}")

    # ── Write summary.md ──
    md_path = EDA_DIR / "summary.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# EDA Summary\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("| Dataset | Rows | Pos | Neg | Conflicts | CJK | Dup Pairs | Avg Q Len | Avg P Len |\n")
        f.write("|---------|------|-----|-----|-----------|-----|-----------|-----------|----------|\n")
        for s in summary_rows:
            f.write(f"| {s['name']} | {s['rows']} | {s['pos']} | {s['neg']} | "
                    f"{s['label_conflicts']} | {s['cjk_queries']} | {s['dup_pairs']} | "
                    f"{s['avg_q_len']} | {s['avg_p_len']} |\n")
        f.write("\n## Notes\n")
        for s in summary_rows:
            if s['label_conflicts'] > 0:
                f.write(f"- ⚠ **{s['name']}**: {s['label_conflicts']} label conflicts detected\n")
            if s['cjk_queries'] > 0:
                f.write(f"- ℹ **{s['name']}**: {s['cjk_queries']} CJK queries (excluded from eval)\n")
    log(f"  Saved {md_path}")

    # ── Plots ──
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plot_dir = EDA_DIR / "plots"

    # 1. Label distribution
    fig, ax = plt.subplots(figsize=(8, 4))
    x = range(len(summary_rows))
    labels = [s["name"] for s in summary_rows]
    pos_vals = [s["pos"] for s in summary_rows]
    neg_vals = [s["neg"] for s in summary_rows]
    width = 0.35
    ax.bar([i - width/2 for i in x], pos_vals, width, label="Positive", color="#2196F3")
    ax.bar([i + width/2 for i in x], neg_vals, width, label="Negative", color="#F44336")
    ax.set_xticks(list(x)); ax.set_xticklabels(labels)
    ax.set_title("Label Distribution per Dataset"); ax.set_ylabel("Count")
    ax.legend()
    plt.tight_layout()
    plt.savefig(plot_dir / "label_dist.png", dpi=120)
    plt.close()

    # 2. Query length histogram
    all_q_lens = []
    for name, (_, rows, *_) in datasets.items():
        all_q_lens.extend([len(r.get("query","")) for r in rows])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(all_q_lens, bins=50, color="#4CAF50", edgecolor="white")
    ax.set_title("Query Length Distribution (chars)")
    ax.set_xlabel("Length"); ax.set_ylabel("Count")
    plt.tight_layout()
    plt.savefig(plot_dir / "query_len.png", dpi=120)
    plt.close()

    # 3. Passage length histogram
    all_p_lens = []
    for name, (_, rows, *_) in datasets.items():
        all_p_lens.extend([len(r.get("passage","")) for r in rows])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(all_p_lens, bins=50, color="#FF9800", edgecolor="white")
    ax.set_title("Passage Length Distribution (chars)")
    ax.set_xlabel("Length"); ax.set_ylabel("Count")
    plt.tight_layout()
    plt.savefig(plot_dir / "passage_len.png", dpi=120)
    plt.close()

    # 4. Top van_ban
    all_rows = []
    for name, (_, rows, *_) in datasets.items():
        all_rows.extend(rows)
    van_ban_counts = Counter(r.get("meta",{}).get("van_ban","?") for r in all_rows)
    top_vb = van_ban_counts.most_common(20)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh([t[0] for t in top_vb], [t[1] for t in top_vb], color="#9C27B0")
    ax.set_title("Top 20 Van Bản by Frequency")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(plot_dir / "top_vanban.png", dpi=120)
    plt.close()

    # 5. Top dieu
    dieu_counts = Counter(r.get("meta",{}).get("dieu","?") for r in all_rows)
    top_dieu = dieu_counts.most_common(20)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh([t[0] for t in top_dieu], [t[1] for t in top_dieu], color="#00BCD4")
    ax.set_title("Top 20 Điều by Frequency")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(plot_dir / "top_dieu.png", dpi=120)
    plt.close()

    log("  All 5 plots saved.")

    outputs = [
        csv_path, md_path,
        plot_dir/"label_dist.png", plot_dir/"query_len.png",
        plot_dir/"passage_len.png", plot_dir/"top_vanban.png",
        plot_dir/"top_dieu.png",
    ]
    write_done("A", outputs, {"total_rows": sum(s["rows"] for s in summary_rows)})
    log("Phase A complete ✓")

# ─────────────────────────────────────────────
# 4. PHASE B — Create eval_qa.jsonl
# ─────────────────────────────────────────────
def phase_b(args):
    log("=" * 60)
    log("PHASE B: Create eval_qa.jsonl")
    log("=" * 60)

    random.seed(args.seed)
    dev_rows = load_jsonl(DEV_FILE)
    train_neg_rows = load_jsonl(TRAIN_NEG)

    # Count van_ban frequency in train_with_neg for easy/hard tagging
    vb_freq = Counter(r.get("meta",{}).get("van_ban","") for r in train_neg_rows)

    # Filter CJK
    cjk_filtered = 0
    clean_dev = []
    for r in dev_rows:
        q = r.get("query","").strip()
        if count_cjk(q) >= 3:
            cjk_filtered += 1
        else:
            clean_dev.append(r)
    log(f"  CJK filtered: {cjk_filtered} queries removed from {len(dev_rows)} dev rows")
    log(f"  Clean dev rows: {len(clean_dev)}")

    # Group by (van_ban, dieu, khoan) — keep one per group
    groups = {}
    for r in clean_dev:
        meta = r.get("meta", {})
        key  = (meta.get("van_ban",""), meta.get("dieu",""), meta.get("khoan",""))
        if key not in groups:
            groups[key] = []
        groups[key].append(r)

    log(f"  Unique (van_ban, dieu, khoan) groups: {len(groups)}")

    qa_items = []
    for gid, (key, records) in enumerate(groups.items()):
        r    = random.choice(records)
        meta = r.get("meta", {})
        vb   = meta.get("van_ban","")
        freq = vb_freq.get(vb, 0)
        tag  = "easy" if freq >= 10 else "hard"

        qa_items.append({
            "id": f"eval_{gid+1:04d}",
            "query": r.get("query","").strip(),
            "expected_citations": [{
                "van_ban":     meta.get("van_ban",""),
                "chuong":      meta.get("chuong",""),
                "dieu":        meta.get("dieu",""),
                "khoan":       meta.get("khoan",""),
                "diem":        meta.get("diem",""),
                "chunk_index": meta.get("chunk_index", -1),
            }],
            "tags":       [tag],
            "source":     "dev.jsonl",
            "passage_ref": r.get("passage","")[:200],  # first 200 chars for debug
        })

    log(f"  QA items generated: {len(qa_items)}")

    # If < 80, relax: allow multiple khoan per dieu
    if len(qa_items) < 80:
        log(f"  < 80 items, relaxing dedup to (van_ban, dieu) level...")
        groups2 = {}
        for r in clean_dev:
            meta = r.get("meta", {})
            key  = (meta.get("van_ban",""), meta.get("dieu",""))
            if key not in groups2:
                groups2[key] = []
            groups2[key].append(r)
        # add items not already covered
        existing_ids = {(item["expected_citations"][0]["van_ban"],
                         item["expected_citations"][0]["dieu"],
                         item["expected_citations"][0]["khoan"])
                        for item in qa_items}
        extra_gid = len(qa_items)
        for key, records in groups2.items():
            for r in records:
                meta = r.get("meta",{})
                triple = (meta.get("van_ban",""), meta.get("dieu",""), meta.get("khoan",""))
                if triple not in existing_ids and len(qa_items) < 150:
                    existing_ids.add(triple)
                    vb   = meta.get("van_ban","")
                    freq = vb_freq.get(vb, 0)
                    tag  = "easy" if freq >= 10 else "hard"
                    extra_gid += 1
                    qa_items.append({
                        "id": f"eval_{extra_gid:04d}",
                        "query": r.get("query","").strip(),
                        "expected_citations": [{
                            "van_ban":     meta.get("van_ban",""),
                            "chuong":      meta.get("chuong",""),
                            "dieu":        meta.get("dieu",""),
                            "khoan":       meta.get("khoan",""),
                            "diem":        meta.get("diem",""),
                            "chunk_index": meta.get("chunk_index", -1),
                        }],
                        "tags":       [tag],
                        "source":     "dev.jsonl",
                        "passage_ref": r.get("passage","")[:200],
                    })
        log(f"  QA items after relaxation: {len(qa_items)}")

    random.shuffle(qa_items)
    write_jsonl(EVAL_QA_FILE, qa_items)
    log(f"  Saved {len(qa_items)} QA items → {EVAL_QA_FILE}")

    easy = sum(1 for q in qa_items if "easy" in q["tags"])
    hard = sum(1 for q in qa_items if "hard" in q["tags"])
    log(f"  Tags: easy={easy}, hard={hard}")

    write_done("B", [EVAL_QA_FILE], {
        "qa_count": len(qa_items),
        "cjk_filtered": cjk_filtered,
        "easy": easy,
        "hard": hard,
    })
    log("Phase B complete ✓")

# ─────────────────────────────────────────────
# 5. PHASE C — Train Cross-Encoder
# ─────────────────────────────────────────────
def phase_c(args):
    log("=" * 60)
    log("PHASE C: Train Cross-Encoder")
    log("=" * 60)

    import torch
    from sentence_transformers import CrossEncoder
    from sentence_transformers.cross_encoder.evaluation import CEBinaryClassificationEvaluator
    from torch.utils.data import DataLoader

    device = "cuda" if torch.cuda.is_available() else "cpu"
    log(f"  Device: {device}")

    # ── Build dev_with_neg.jsonl ──
    if not DEV_NEG_FILE.exists():
        log("  Building dev_with_neg.jsonl ...")
        random.seed(args.seed)
        dev_rows     = load_jsonl(DEV_FILE)
        train_neg_rows = load_jsonl(TRAIN_NEG)

        # Index hard negatives by van_ban
        neg_by_vb = {}
        for r in train_neg_rows:
            if r.get("label") == 0:
                vb = r.get("meta",{}).get("van_ban","")
                neg_by_vb.setdefault(vb, []).append(r)

        dev_neg_rows = []
        for r in dev_rows:
            meta = r.get("meta",{})
            vb   = meta.get("van_ban","")
            dieu = meta.get("dieu","")
            dev_neg_rows.append({"query": r["query"], "passage": r["passage"], "label": 1, "meta": meta})

            # Hard negative: same van_ban, different dieu
            candidates = [
                n for n in neg_by_vb.get(vb, [])
                if n.get("meta",{}).get("dieu","") != dieu
            ]
            if not candidates:
                # Fallback: any negative from different van_ban
                all_negs = [n for n in train_neg_rows if n.get("label") == 0 and n.get("meta",{}).get("van_ban","") != vb]
                candidates = all_negs
            if candidates:
                neg = random.choice(candidates)
                dev_neg_rows.append({
                    "query": r["query"],
                    "passage": neg["passage"],
                    "label": 0,
                    "meta": neg.get("meta",{})
                })

        write_jsonl(DEV_NEG_FILE, dev_neg_rows)
        log(f"  Saved {len(dev_neg_rows)} rows → {DEV_NEG_FILE}")
    else:
        log(f"  {DEV_NEG_FILE.name} already exists, skipping build.")

    # ── Prepare training samples ──
    log("  Loading training data ...")
    train_rows = load_jsonl(TRAIN_NEG)
    random.seed(args.seed)
    random.shuffle(train_rows)

    from sentence_transformers import InputExample
    train_samples = [
        InputExample(texts=[r["query"], r["passage"]], label=float(r.get("label",0)))
        for r in train_rows
        if "query" in r and "passage" in r and "label" in r
    ]
    log(f"  Training samples: {len(train_samples)}")

    dev_neg_rows = load_jsonl(DEV_NEG_FILE)
    dev_samples = [
        InputExample(texts=[r["query"], r["passage"]], label=float(r.get("label",0)))
        for r in dev_neg_rows
    ]

    # ── Load & train model ──
    # Use fp16 only on CUDA
    use_fp16 = (device == "cuda")
    log(f"  Base model: {BASE_CE_MODEL}")
    log(f"  Epochs={args.epochs}, Batch={args.batch_size}, MaxLen={args.max_length}, fp16={use_fp16}")

    model = CrossEncoder(BASE_CE_MODEL, num_labels=1, max_length=args.max_length, device=device)

    MODEL_OUT.mkdir(parents=True, exist_ok=True)
    log_file = MODEL_OUT / "train_log.txt"
    t0 = time.time()

    evaluator = CEBinaryClassificationEvaluator.from_input_examples(dev_samples, name="dev")

    model.fit(
        train_dataloader=DataLoader(train_samples, shuffle=True, batch_size=args.batch_size),
        evaluator=evaluator,
        epochs=args.epochs,
        warmup_steps=int(len(train_samples) / args.batch_size * args.epochs * 0.1),
        output_path=str(MODEL_OUT),
        use_amp=use_fp16,
    )

    elapsed = round((time.time() - t0) / 60, 1)
    log(f"  Training done in {elapsed} min")

    # ── Explicitly save model (sentence-transformers v5 requires this) ──
    saved_path = MODEL_OUT / "saved_model"
    model.save(str(saved_path))
    log(f"  Model saved → {saved_path}")

    # ── Save config & log ──
    config = {
        "base_model": BASE_CE_MODEL,
        "saved_path": str(saved_path),
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "max_length": args.max_length,
        "fp16": use_fp16,
        "device": device,
        "train_samples": len(train_samples),
        "dev_samples": len(dev_samples),
        "training_minutes": elapsed,
        "seed": args.seed,
    }
    (MODEL_OUT / "training_config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    log_file.write_text(f"Trained {args.epochs} epochs in {elapsed} min\nConfig: {json.dumps(config, indent=2)}", encoding="utf-8")

    write_done("C", [MODEL_OUT / "training_config.json", saved_path, DEV_NEG_FILE], {
        "train_samples": len(train_samples),
        "training_minutes": elapsed,
        "saved_path": str(saved_path),
    })
    log("Phase C complete ✓")

# ─────────────────────────────────────────────
# 6. PHASE D — Evaluate Reranker
# ─────────────────────────────────────────────
def phase_d(args):
    log("=" * 60)
    log("PHASE D: Evaluate Reranker")
    log("=" * 60)

    import torch
    import faiss
    import numpy as np
    from sentence_transformers import CrossEncoder, SentenceTransformer
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # ── D1: Classification metrics on dev_with_neg ──
    log("  [D1] Classification metrics ...")
    # Prefer the explicitly saved model; fallback to MODEL_OUT (ST v4 style)
    ce_model_path = MODEL_OUT / "saved_model"
    if not ce_model_path.exists():
        ce_model_path = MODEL_OUT
    log(f"  Loading model from {ce_model_path}")
    ce_model = CrossEncoder(str(ce_model_path), max_length=args.max_length, device=device)

    dev_neg_rows = load_jsonl(DEV_NEG_FILE)
    queries   = [r["query"] for r in dev_neg_rows]
    passages  = [r["passage"] for r in dev_neg_rows]
    y_true    = [int(r.get("label",0)) for r in dev_neg_rows]

    scores = ce_model.predict(list(zip(queries, passages)), batch_size=args.batch_size, show_progress_bar=True)
    y_pred = [1 if s >= 0.5 else 0 for s in scores]

    metrics = {
        "accuracy":  round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1":        round(f1_score(y_true, y_pred, zero_division=0), 4),
        "roc_auc":   round(roc_auc_score(y_true, scores), 4),
        "n_samples": len(y_true),
    }
    log(f"  Classification: {metrics}")
    CLASS_METRICS.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"  Saved → {CLASS_METRICS}")

    # ── D2: Build FAISS index ──
    log("  [D2] Building FAISS index ...")
    bi_model = SentenceTransformer(BASE_BI_MODEL, device=device)

    # Collect unique passages with metadata
    all_files = [TRAIN_FILE, DEV_FILE, TRAIN_NEG]
    seen_passages = {}
    for f in all_files:
        for r in load_jsonl(f):
            p = r.get("passage","")
            if p and p not in seen_passages:
                meta = r.get("meta",{})
                seen_passages[p] = {
                    "passage":     p,
                    "chunk_index": meta.get("chunk_index",-1),
                    "van_ban":     meta.get("van_ban",""),
                    "chuong":      meta.get("chuong",""),
                    "dieu":        meta.get("dieu",""),
                    "khoan":       meta.get("khoan",""),
                    "diem":        meta.get("diem",""),
                }

    corpus = list(seen_passages.values())
    log(f"  Corpus size: {len(corpus)} unique passages")

    passages_text = [c["passage"] for c in corpus]
    log("  Encoding passages (GPU batch) ...")
    embeddings = bi_model.encode(
        passages_text, batch_size=64, show_progress_bar=True,
        convert_to_numpy=True, normalize_embeddings=True
    )
    embeddings = embeddings.astype("float32")

    # Build flat inner-product index (normalized → cosine)
    dim   = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    faiss.write_index(index, str(FAISS_INDEX))
    log(f"  FAISS index saved → {FAISS_INDEX}")

    # Save mapping
    mapping = []
    for i, c in enumerate(corpus):
        mapping.append({"faiss_id": i, **c})
    write_jsonl(FAISS_MAP, mapping)
    log(f"  Mapping saved → {FAISS_MAP} ({len(mapping)} entries)")

    # ── D3: Ranking metrics ──
    log("  [D3] Computing ranking metrics ...")
    eval_qa = load_jsonl(EVAL_QA_FILE)
    log(f"  Eval QA: {len(eval_qa)} questions")

    def is_hit(faiss_id, expected_citations, mapping):
        row = mapping[faiss_id]
        for ec in expected_citations:
            ci = ec.get("chunk_index",-2)
            if ci != -1 and row["chunk_index"] == ci:
                return True
            if (row["van_ban"] == ec.get("van_ban","") and
                row["dieu"]    == ec.get("dieu","") and
                row["khoan"]   == ec.get("khoan","")):
                return True
        return False

    topN = args.topN
    results_base  = {"R@1":[],"R@3":[],"R@5":[],"MRR@10":[]}
    results_rerank= {"R@1":[],"R@3":[],"R@5":[],"MRR@10":[]}

    for item in eval_qa:
        query = item["query"]
        ec    = item["expected_citations"]

        # Retrieve
        q_emb = bi_model.encode([query], normalize_embeddings=True, convert_to_numpy=True).astype("float32")
        _, ids = index.search(q_emb, topN)
        ids = ids[0].tolist()

        # Baseline ranking metrics
        for k, key in [(1,"R@1"),(3,"R@3"),(5,"R@5")]:
            hit = any(is_hit(i, ec, mapping) for i in ids[:k] if i >= 0)
            results_base[key].append(1 if hit else 0)
        mrr = 0.0
        for rank, i in enumerate(ids[:10], 1):
            if i >= 0 and is_hit(i, ec, mapping):
                mrr = 1.0 / rank; break
        results_base["MRR@10"].append(mrr)

        # Rerank
        cands = [(mapping[i]["passage"], i) for i in ids if i >= 0]
        if cands:
            pairs   = [[query, c[0]] for c in cands]
            rscores = ce_model.predict(pairs, batch_size=args.batch_size)
            ranked  = sorted(zip(rscores, [c[1] for c in cands]), reverse=True)
            r_ids   = [r[1] for r in ranked]
        else:
            r_ids = []

        for k, key in [(1,"R@1"),(3,"R@3"),(5,"R@5")]:
            hit = any(is_hit(i, ec, mapping) for i in r_ids[:k])
            results_rerank[key].append(1 if hit else 0)
        mrr = 0.0
        for rank, i in enumerate(r_ids[:10], 1):
            if is_hit(i, ec, mapping):
                mrr = 1.0 / rank; break
        results_rerank["MRR@10"].append(mrr)

    def avg(lst): return round(sum(lst)/len(lst), 4) if lst else 0.0

    rerank_rows = [
        {"metric":"Recall@1",  "baseline": avg(results_base["R@1"]),   "reranked": avg(results_rerank["R@1"])},
        {"metric":"Recall@3",  "baseline": avg(results_base["R@3"]),   "reranked": avg(results_rerank["R@3"])},
        {"metric":"Recall@5",  "baseline": avg(results_base["R@5"]),   "reranked": avg(results_rerank["R@5"])},
        {"metric":"MRR@10",    "baseline": avg(results_base["MRR@10"]),"reranked": avg(results_rerank["MRR@10"])},
    ]
    with open(RERANK_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["metric","baseline","reranked"])
        w.writeheader(); w.writerows(rerank_rows)
    log(f"  Rerank metrics:")
    for row in rerank_rows:
        log(f"    {row['metric']}: baseline={row['baseline']}, reranked={row['reranked']}")
    log(f"  Saved → {RERANK_CSV}")

    write_done("D", [CLASS_METRICS, RERANK_CSV, FAISS_INDEX, FAISS_MAP])
    log("Phase D complete ✓")

# ─────────────────────────────────────────────
# 7. PHASE E — Pipeline End-to-End
# ─────────────────────────────────────────────
class LLMClient:
    def __init__(self):
        self.mode = "placeholder"
        self.api_key = None
        if os.environ.get("OPENROUTER_API_KEY"):
            self.mode = "openrouter"
            self.api_key = os.environ["OPENROUTER_API_KEY"]
        elif os.environ.get("GEMINI_API_KEY"):
            self.mode = "gemini"
            self.api_key = os.environ["GEMINI_API_KEY"]
        log(f"  LLMClient mode: {self.mode}")

    def generate(self, query, passages):
        if self.mode == "placeholder":
            return None
        context = "\n\n".join(f"[{i+1}] {p}" for i,p in enumerate(passages))
        prompt  = (f"Dựa vào các đoạn văn bản pháp lý sau:\n{context}\n\n"
                   f"Hãy trả lời câu hỏi: {query}\n"
                   f"Trả lời ngắn gọn, trích dẫn điều khoản cụ thể.")
        try:
            import urllib.request
            if self.mode == "openrouter":
                url  = "https://openrouter.ai/api/v1/chat/completions"
                body = json.dumps({
                    "model": "mistralai/mistral-7b-instruct",
                    "messages": [{"role":"user","content": prompt}]
                }).encode()
                req  = urllib.request.Request(url, data=body, headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                })
                with urllib.request.urlopen(req, timeout=30) as r:
                    resp = json.loads(r.read())
                    return resp["choices"][0]["message"]["content"]
            elif self.mode == "gemini":
                url  = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}"
                body = json.dumps({"contents":[{"parts":[{"text": prompt}]}]}).encode()
                req  = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json"})
                with urllib.request.urlopen(req, timeout=30) as r:
                    resp = json.loads(r.read())
                    return resp["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            log(f"  LLM error: {e}")
            return None
        return None

def phase_e(args):
    log("=" * 60)
    log("PHASE E: Pipeline End-to-End Evaluation")
    log("=" * 60)

    import torch
    import faiss
    import numpy as np
    from sentence_transformers import CrossEncoder, SentenceTransformer

    device = "cuda" if torch.cuda.is_available() else "cpu"
    ce_model_path = MODEL_OUT / "saved_model"
    if not ce_model_path.exists():
        ce_model_path = MODEL_OUT
    log(f"  Loading cross-encoder from {ce_model_path}")
    ce_model = CrossEncoder(str(ce_model_path), max_length=args.max_length, device=device)
    bi_model = SentenceTransformer(BASE_BI_MODEL, device=device)

    # Load FAISS index and mapping
    index   = faiss.read_index(str(FAISS_INDEX))
    mapping = load_jsonl(FAISS_MAP)
    log(f"  FAISS loaded: {index.ntotal} vectors")

    eval_qa = load_jsonl(EVAL_QA_FILE)
    random.seed(args.seed)
    random.shuffle(eval_qa)
    eval_qa = eval_qa[:args.eval_n]
    log(f"  Evaluating {len(eval_qa)} questions")

    llm = LLMClient()

    def is_hit(faiss_id, expected_citations):
        row = mapping[faiss_id]
        for ec in expected_citations:
            ci = ec.get("chunk_index",-2)
            if ci != -1 and row.get("chunk_index") == ci:
                return True
            if (row.get("van_ban") == ec.get("van_ban") and
                row.get("dieu")    == ec.get("dieu") and
                row.get("khoan")   == ec.get("khoan")):
                return True
        return False

    GATE_PASS   = 0.5
    GATE_REFINE = 0.3
    results = []

    for item in eval_qa:
        t0    = time.time()
        query = item["query"]
        ec    = item["expected_citations"]

        # Retrieve
        q_emb = bi_model.encode([query], normalize_embeddings=True, convert_to_numpy=True).astype("float32")
        scores_faiss, ids = index.search(q_emb, args.topN)
        ids = [i for i in ids[0].tolist() if i >= 0]
        scores_faiss = scores_faiss[0].tolist()

        # Rerank
        cands   = [(mapping[i]["passage"], i, sf) for i,sf in zip(ids, scores_faiss) if i < len(mapping)]
        pairs   = [[query, c[0]] for c in cands]
        rscores = ce_model.predict(pairs, batch_size=args.batch_size) if pairs else []
        ranked  = sorted(zip(rscores, cands), reverse=True) if len(rscores) > 0 else []

        reranked_ids    = [c[1] for _, c in ranked]
        reranked_scores = [float(s) for s, _ in ranked]

        # Gate
        max_score = reranked_scores[0] if reranked_scores else 0.0
        if max_score >= GATE_PASS:
            decision = "PASS"
        elif max_score >= GATE_REFINE:
            decision = "REFINE"
            # expand retrieval
            _, ids2   = index.search(q_emb, args.topN * 2)
            ids2      = [i for i in ids2[0].tolist() if i >= 0 and i not in reranked_ids]
            cands2    = [(mapping[i]["passage"], i, 0.0) for i in ids2 if i < len(mapping)]
            pairs2    = [[query, c[0]] for c in cands2]
            rscores2  = ce_model.predict(pairs2, batch_size=args.batch_size) if pairs2 else []
            extra     = sorted(zip(rscores2, cands2), reverse=True) if len(rscores2) > 0 else []
            ranked    = ranked + extra
            ranked.sort(key=lambda x: x[0], reverse=True)
            reranked_ids    = [c[1] for _, c in ranked]
            reranked_scores = [float(s) for s, _ in ranked]
            max_score       = reranked_scores[0] if reranked_scores else 0.0
            if max_score < GATE_PASS:
                decision = "ABSTAIN"
        else:
            decision = "ABSTAIN"

        # Citations predicted = top-3 after reranking
        top3_ids = reranked_ids[:3]
        citations_predicted = [
            {
                "faiss_id":    i,
                "van_ban":     mapping[i].get("van_ban",""),
                "dieu":        mapping[i].get("dieu",""),
                "khoan":       mapping[i].get("khoan",""),
                "chunk_index": mapping[i].get("chunk_index",-1),
            }
            for i in top3_ids if i < len(mapping)
        ]

        # Citation hit (independent of LLM)
        citation_hit = any(is_hit(i, ec) for i in top3_ids if i < len(mapping))

        # LLM answer
        answer = None
        if decision != "ABSTAIN":
            top_passages = [mapping[i]["passage"] for i in top3_ids if i < len(mapping)]
            answer = llm.generate(query, top_passages)
            if decision == "ABSTAIN" or answer is None and llm.mode == "placeholder":
                answer = None  # keep null for placeholder

        if decision == "ABSTAIN":
            answer = "Tôi không tìm thấy thông tin phù hợp."

        latency = round((time.time() - t0) * 1000, 1)

        results.append({
            "id":                 item["id"],
            "query":              query,
            "expected_citations": ec,
            "retrieved_ids":      ids[:10],
            "retrieved_scores":   [round(s,4) for s in scores_faiss[:10]],
            "reranked_ids":       reranked_ids[:10],
            "reranked_scores":    [round(s,4) for s in reranked_scores[:10]],
            "decision":           decision,
            "citations_predicted":citations_predicted,
            "citation_hit":       citation_hit,
            "llm_mode":           llm.mode,
            "answer":             answer,
            "correctness":        None,  # requires human or LLM-as-judge
            "latency_ms":         latency,
        })

    write_jsonl(PIPE_RESULTS, results)
    log(f"  Saved {len(results)} results → {PIPE_RESULTS}")

    # Summary metrics
    n = len(results)
    citation_hit_rate = round(sum(1 for r in results if r["citation_hit"]) / n, 4) if n else 0
    abstain_rate  = round(sum(1 for r in results if r["decision"]=="ABSTAIN") / n, 4) if n else 0
    pass_rate     = round(sum(1 for r in results if r["decision"]=="PASS") / n, 4) if n else 0
    refine_rate   = round(sum(1 for r in results if r["decision"]=="REFINE") / n, 4) if n else 0
    avg_latency   = round(sum(r["latency_ms"] for r in results) / n, 1) if n else 0
    llm_mode_used = results[0]["llm_mode"] if results else "placeholder"

    summary = [
        {"metric":"total_questions",    "value": n},
        {"metric":"citation_hit_rate",  "value": citation_hit_rate},
        {"metric":"abstain_rate",        "value": abstain_rate},
        {"metric":"pass_rate",           "value": pass_rate},
        {"metric":"refine_rate",         "value": refine_rate},
        {"metric":"llm_mode",            "value": llm_mode_used},
        {"metric":"answer_correctness",  "value": "null (human eval required)" if llm_mode_used=="placeholder" else "see pipeline_results.jsonl"},
        {"metric":"avg_latency_ms",      "value": avg_latency},
    ]

    with open(PIPE_SUM_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["metric","value"])
        w.writeheader(); w.writerows(summary)

    with open(PIPE_SUM_MD, "w", encoding="utf-8") as f:
        f.write("# Pipeline Evaluation Summary\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("| Metric | Value |\n|--------|-------|\n")
        for row in summary:
            f.write(f"| {row['metric']} | {row['value']} |\n")
        f.write("\n> Note: `answer_correctness` requires human evaluation or LLM-as-judge when using placeholder mode.\n")

    log(f"  citation_hit_rate={citation_hit_rate}, abstain_rate={abstain_rate}, avg_latency={avg_latency}ms")
    log(f"  Saved → {PIPE_SUM_CSV}, {PIPE_SUM_MD}")

    write_done("E", [PIPE_RESULTS, PIPE_SUM_CSV, PIPE_SUM_MD], {
        "citation_hit_rate": citation_hit_rate,
        "abstain_rate": abstain_rate,
        "llm_mode": llm_mode_used,
    })
    log("Phase E complete ✓")

# ─────────────────────────────────────────────
# 8. PHASE F — Deliverables
# ─────────────────────────────────────────────
def phase_f(args):
    log("=" * 60)
    log("PHASE F: Generate DELIVERABLES.md")
    log("=" * 60)

    # Collect metrics from done markers
    def load_done(phase):
        p = LOG_DIR / f"DONE_{phase}.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

    metrics_d = {}
    if CLASS_METRICS.exists():
        metrics_d = json.loads(CLASS_METRICS.read_text(encoding="utf-8"))

    rerank_data = []
    if RERANK_CSV.exists():
        with open(RERANK_CSV, encoding="utf-8") as f:
            rerank_data = list(csv.DictReader(f))

    pipe_sum = []
    if PIPE_SUM_CSV.exists():
        with open(PIPE_SUM_CSV, encoding="utf-8") as f:
            pipe_sum = list(csv.DictReader(f))

    done_b = load_done("B")
    done_c = load_done("C")

    with open(DELIVERABLES, "w", encoding="utf-8") as f:
        f.write("# Deliverables — Cross-Encoder Reranker Pipeline\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Environment\n\n")
        f.write("| Item | Value |\n|------|-------|\n")
        try:
            import torch
            cuda = torch.cuda.is_available()
            gpu  = torch.cuda.get_device_name(0) if cuda else "N/A"
        except Exception:
            cuda, gpu = False, "N/A"
        f.write(f"| Python | {sys.version.split()[0]} |\n")
        f.write(f"| GPU | {gpu} |\n")
        f.write(f"| CUDA | {cuda} |\n\n")

        f.write("## Phase A — EDA Summary\n\n")
        eda_csv = EDA_DIR / "summary.csv"
        if eda_csv.exists():
            with open(eda_csv, encoding="utf-8") as ef:
                rows = list(csv.DictReader(ef))
            f.write("| Dataset | Rows | Pos | Neg | Conflicts | CJK removed |\n")
            f.write("|---------|------|-----|-----|-----------|-------------|\n")
            for row in rows:
                f.write(f"| {row['name']} | {row['rows']} | {row['pos']} | {row['neg']} | {row['label_conflicts']} | {row['cjk_queries']} |\n")
            f.write("\n")

        f.write("## Phase B — eval_qa.jsonl\n\n")
        f.write(f"- Records: {done_b.get('qa_count','N/A')}\n")
        f.write(f"- CJK filtered: {done_b.get('cjk_filtered','N/A')}\n")
        f.write(f"- Easy: {done_b.get('easy','N/A')}, Hard: {done_b.get('hard','N/A')}\n\n")

        f.write("## Phase C — Training\n\n")
        f.write(f"- Base model: `{BASE_CE_MODEL}`\n")
        f.write(f"- Samples: {done_c.get('train_samples','N/A')}\n")
        f.write(f"- Duration: {done_c.get('training_minutes','N/A')} min\n\n")

        f.write("## Phase D — Reranker Metrics\n\n")
        if metrics_d:
            f.write("**Classification (dev_with_neg)**\n\n")
            f.write("| Metric | Value |\n|--------|-------|\n")
            for k,v in metrics_d.items():
                f.write(f"| {k} | {v} |\n")
            f.write("\n")
        if rerank_data:
            f.write("**Ranking (eval_qa)**\n\n")
            f.write("| Metric | Baseline | Reranked |\n|--------|----------|----------|\n")
            for row in rerank_data:
                f.write(f"| {row['metric']} | {row['baseline']} | {row['reranked']} |\n")
            f.write("\n")

        f.write("## Phase E — Pipeline Metrics\n\n")
        if pipe_sum:
            f.write("| Metric | Value |\n|--------|-------|\n")
            for row in pipe_sum:
                f.write(f"| {row['metric']} | {row['value']} |\n")
            f.write("\n")

        f.write("## Output Files\n\n")
        file_list = [
            ("outputs/eda/summary.csv",                   "EDA statistics table"),
            ("outputs/eda/summary.md",                    "EDA report (markdown)"),
            ("outputs/eda/plots/label_dist.png",          "Label distribution chart"),
            ("outputs/eda/plots/query_len.png",           "Query length histogram"),
            ("outputs/eda/plots/passage_len.png",         "Passage length histogram"),
            ("outputs/eda/plots/top_vanban.png",          "Top 20 van bản"),
            ("outputs/eda/plots/top_dieu.png",            "Top 20 điều"),
            ("outputs/eval/eval_qa.jsonl",                "Ground-truth QA set (≥80 records)"),
            ("outputs/eval/dev_with_neg.jsonl",           "Dev set with hard negatives"),
            ("outputs/models/cross_encoder_v1/",          "Trained cross-encoder model"),
            ("outputs/models/cross_encoder_v1/training_config.json", "Training hyperparameters"),
            ("outputs/eval/dev_classification_metrics.json","Classification metrics (acc/prec/recall/f1/AUC)"),
            ("outputs/eval/rerank_metrics.csv",           "Recall@K & MRR@10 baseline vs reranked"),
            ("outputs/tmp/faiss.index",                   "FAISS binary index"),
            ("outputs/tmp/faiss_mapping.jsonl",           "faiss_id ↔ chunk_index/meta mapping"),
            ("outputs/eval/pipeline_results.jsonl",       "Per-question pipeline results"),
            ("outputs/eval/pipeline_summary.csv",         "Pipeline aggregate metrics"),
            ("outputs/eval/pipeline_summary.md",          "Pipeline report (markdown)"),
        ]
        f.write("| File | Purpose |\n|------|---------|\n")
        for path, desc in file_list:
            exists = "✓" if Path(path).exists() else "✗"
            f.write(f"| `{path}` {exists} | {desc} |\n")

        f.write("\n## Reproduction Commands\n\n")
        f.write("```bash\n")
        f.write("# Full pipeline (first run)\n")
        f.write("./venv/python.exe run_pipeline.py --phase ALL --seed 42\n\n")
        f.write("# Resume after crash\n")
        f.write("./venv/python.exe run_pipeline.py --phase ALL --resume\n\n")
        f.write("# Individual phases\n")
        f.write("./venv/python.exe run_pipeline.py --phase A\n")
        f.write("./venv/python.exe run_pipeline.py --phase B\n")
        f.write("./venv/python.exe run_pipeline.py --phase C --epochs 3 --batch_size 32\n")
        f.write("./venv/python.exe run_pipeline.py --phase D --topN 50\n")
        f.write("./venv/python.exe run_pipeline.py --phase E --eval_n 50\n")
        f.write("./venv/python.exe run_pipeline.py --phase F\n")
        f.write("```\n")

    log(f"  Saved → {DELIVERABLES}")
    write_done("F", [DELIVERABLES])
    log("Phase F complete ✓")

# ─────────────────────────────────────────────
# 9. MAIN
# ─────────────────────────────────────────────
def main():
    args = parse_args()
    random.seed(args.seed)
    makedirs()

    log(f"Pipeline start | phase={args.phase} | resume={args.resume} | seed={args.seed}")
    env_info()

    phases = {
        "A": (phase_a, [EDA_DIR/"summary.csv", EDA_DIR/"summary.md"]),
        "B": (phase_b, [EVAL_QA_FILE]),
        "C": (phase_c, [MODEL_OUT/"training_config.json"]),
        "D": (phase_d, [CLASS_METRICS, RERANK_CSV]),
        "E": (phase_e, [PIPE_RESULTS, PIPE_SUM_CSV]),
        "F": (phase_f, [DELIVERABLES]),
    }

    run_phases = ["A","B","C","D","E","F"] if args.phase == "ALL" else [args.phase]

    for ph in run_phases:
        if check_done(ph, args.resume):
            continue
        fn, _ = phases[ph]
        try:
            fn(args)
        except Exception as e:
            import traceback
            log(f"  ✗ Phase {ph} FAILED: {e}")
            traceback.print_exc()
            log(f"  Fix the error and re-run with --resume to continue from phase {ph}")
            sys.exit(1)

    log("=" * 60)
    log("ALL PHASES COMPLETE ✓")
    log(f"Outputs at: {OUT_DIR}")
    log("=" * 60)

if __name__ == "__main__":
    main()
