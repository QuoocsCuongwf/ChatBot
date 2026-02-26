import os, json, csv
from pathlib import Path

files = [
    ('outputs/eda/summary.csv',                                  'EDA summary'),
    ('outputs/eda/summary.md',                                   'EDA report'),
    ('outputs/eda/plots/label_dist.png',                         'Plot: label dist'),
    ('outputs/eda/plots/query_len.png',                          'Plot: query len'),
    ('outputs/eda/plots/passage_len.png',                        'Plot: passage len'),
    ('outputs/eda/plots/top_vanban.png',                         'Plot: top van ban'),
    ('outputs/eda/plots/top_dieu.png',                           'Plot: top dieu'),
    ('outputs/eval/eval_qa.jsonl',                               'Eval QA set'),
    ('outputs/eval/dev_with_neg.jsonl',                          'Dev with negatives'),
    ('outputs/models/cross_encoder_v1/training_config.json',     'Training config'),
    ('outputs/models/cross_encoder_v1/saved_model/config.json',  'Model config'),
    ('outputs/eval/dev_classification_metrics.json',             'Classification metrics'),
    ('outputs/eval/rerank_metrics.csv',                          'Rerank metrics'),
    ('outputs/tmp/faiss.index',                                  'FAISS index'),
    ('outputs/tmp/faiss_mapping.jsonl',                          'FAISS mapping'),
    ('outputs/eval/pipeline_results.jsonl',                      'Pipeline results'),
    ('outputs/eval/pipeline_summary.csv',                        'Pipeline summary'),
    ('outputs/eval/pipeline_summary.md',                         'Pipeline report'),
    ('outputs/DELIVERABLES.md',                                  'Deliverables'),
]

ok, missing_list = 0, []
print("=== OUTPUT VERIFICATION ===")
for f, desc in files:
    exists = os.path.exists(f)
    size = os.path.getsize(f) if exists else 0
    status = 'OK' if exists else 'MISSING'
    print(f"  {status:7s} {desc:35s} {size:>10,} bytes")
    if exists: ok += 1
    else: missing_list.append(f)

print()
print(f"RESULT: {ok}/{len(files)} files present", "✓ ALL OK" if not missing_list else f"✗ MISSING: {missing_list}")

# eval_qa count
if os.path.exists('outputs/eval/eval_qa.jsonl'):
    n = sum(1 for _ in open('outputs/eval/eval_qa.jsonl', encoding='utf-8'))
    print(f"eval_qa records: {n}", "✓" if n >= 80 else "✗")

print()
print("=== KEY METRICS ===")
if os.path.exists('outputs/eval/dev_classification_metrics.json'):
    cm = json.loads(open('outputs/eval/dev_classification_metrics.json').read())
    print("Classification (dev_with_neg):")
    for k,v in cm.items():
        print(f"  {k}: {v}")

print()
if os.path.exists('outputs/eval/rerank_metrics.csv'):
    print("Ranking metrics:")
    with open('outputs/eval/rerank_metrics.csv') as f:
        for row in csv.DictReader(f):
            diff = round(float(row['reranked']) - float(row['baseline']), 4)
            print(f"  {row['metric']:12s}: baseline={row['baseline']}, reranked={row['reranked']}  (+{diff})")

print()
if os.path.exists('outputs/eval/pipeline_summary.csv'):
    print("Pipeline metrics:")
    with open('outputs/eval/pipeline_summary.csv') as f:
        for row in csv.DictReader(f):
            print(f"  {row['metric']:25s}: {row['value']}")
