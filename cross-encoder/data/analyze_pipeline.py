import json
from collections import defaultdict

PATH = r'd:\GitHub\ChatBot\cross-encoder\data\pipeline_results_v5_1.jsonl'

with open(PATH, 'r', encoding='utf-8') as f:
    records = [json.loads(l) for l in f if l.strip()]

print(f"{'='*60}")
print(f"TỔNG SỐ RECORD: {len(records)}")
print(f"{'='*60}")

# ── 1. Overall metrics
hit1 = sum(1 for r in records if r.get('hit@1'))
hit3 = sum(1 for r in records if r.get('hit@3'))
hit5 = sum(1 for r in records if r.get('hit@5'))
mrr  = sum(r.get('mrr', 0) for r in records) / len(records)
print(f"\n[METRICS]")
print(f"  Hit@1 = {hit1}/{len(records)} = {hit1/len(records)*100:.1f}%")
print(f"  Hit@3 = {hit3}/{len(records)} = {hit3/len(records)*100:.1f}%")
print(f"  Hit@5 = {hit5}/{len(records)} = {hit5/len(records)*100:.1f}%")
print(f"  MRR   = {mrr:.4f}")

# ── 2. Cấu trúc keys
print(f"\n[STRUCTURE]")
print(f"  top-level keys: {list(records[0].keys())}")
r0 = records[0]
print(f"  expected_citations: {json.dumps(r0['expected_citations'], ensure_ascii=False)[:200]}")
top_keys = list(r0['top5_reranked'][0].keys()) if r0.get('top5_reranked') else []
print(f"  top5_reranked[0] keys: {top_keys}")

# ── 3. Kiểm tra van_ban mismatch
print(f"\n[VAN_BAN MISMATCH CHECK]")
mismatch_count = 0
for r in records:
    if not r.get('hit@1') and r.get('top5_reranked') and r.get('expected_citations'):
        exp_vb = r['expected_citations'][0].get('van_ban','').strip()[:50]
        top_vb = r['top5_reranked'][0].get('van_ban','').strip()[:50]
        if exp_vb != top_vb:
            mismatch_count += 1
print(f"  Van_ban mismatch khi miss@1: {mismatch_count}/{len(records)-hit1}")

# ── 4. Kiểm tra ce_score distribution của hit vs miss
hit_scores  = [r['top5_reranked'][0]['ce_score'] for r in records if r.get('hit@1') and r.get('top5_reranked')]
miss_scores = [r['top5_reranked'][0]['ce_score'] for r in records if not r.get('hit@1') and r.get('top5_reranked')]
if hit_scores:
    print(f"\n[CE_SCORE DISTRIBUTION]")
    print(f"  Hit@1  avg score: {sum(hit_scores)/len(hit_scores):.4f}  min:{min(hit_scores):.4f}  max:{max(hit_scores):.4f}")
    print(f"  Miss@1 avg score: {sum(miss_scores)/len(miss_scores):.4f}  min:{min(miss_scores):.4f}  max:{max(miss_scores):.4f}")

# ── 5. Trường hợp miss@1 nhưng hit@3,@5 (hit ở rank cao hơn)
late_hit = [r for r in records if not r.get('hit@1') and r.get('hit@5')]
print(f"\n[MISS@1 NHƯNG HIT@5: {len(late_hit)} cases — chunks có câu trả lời nhưng bị rank sai]")
for r in late_hit[:3]:
    hits = [c for c in r['top5_reranked'] if c.get('hit')]
    exp_dieu = r['expected_citations'][0].get('dieu') if r.get('expected_citations') else '?'
    top1 = r['top5_reranked'][0]
    print(f"  Query: {r['query'][:60]}")
    print(f"    Expected Dieu: {exp_dieu}")
    print(f"    Top1 ce_score={top1['ce_score']:.4f} Dieu={top1.get('dieu')} hit={top1.get('hit')}")
    if hits:
        print(f"    First hit: rank={hits[0]['rank']} ce_score={hits[0]['ce_score']:.4f} Dieu={hits[0].get('dieu')}")
    print()

# ── 6. Kiểm tra expected_citations fields đầy đủ không
print(f"[EXPECTED CITATION FIELD COMPLETENESS]")
has_dieu  = sum(1 for r in records if r.get('expected_citations') and r['expected_citations'][0].get('dieu'))
has_khoan = sum(1 for r in records if r.get('expected_citations') and r['expected_citations'][0].get('khoan'))
has_vb    = sum(1 for r in records if r.get('expected_citations') and r['expected_citations'][0].get('van_ban'))
has_pass  = sum(1 for r in records if r.get('expected_citations') and r['expected_citations'][0].get('passage'))
print(f"  has van_ban : {has_vb}/{len(records)}")
print(f"  has dieu    : {has_dieu}/{len(records)}")
print(f"  has khoan   : {has_khoan}/{len(records)}")
print(f"  has passage : {has_pass}/{len(records)}")

# ── 7. Xem 2 case miss@1 tiêu biểu
print(f"\n[SAMPLE MISS@1 CASES]")
misses = [r for r in records if not r.get('hit@1')]
for r in misses[:2]:
    exp = r['expected_citations'][0] if r.get('expected_citations') else {}
    top1 = r['top5_reranked'][0] if r.get('top5_reranked') else {}
    print(f"  Query: {r['query'][:70]}")
    print(f"    EXPECTED: dieu={exp.get('dieu')} khoan={exp.get('khoan')} van_ban={str(exp.get('van_ban',''))[:40]}")
    print(f"    TOP1 GOT: dieu={top1.get('dieu')} khoan={top1.get('khoan')} van_ban={str(top1.get('van_ban',''))[:40]} ce_score={top1.get('ce_score')}")
    print()

# ── 8. Kiểm tra duplicate query
queries = [r['query'] for r in records]
dup_queries = {q for q in queries if queries.count(q) > 1}
print(f"[DUPLICATE QUERIES: {len(dup_queries)}]")

# ── 9. ce_score = 0 or NaN
zero_scores = [r for r in records if r.get('top5_reranked') and r['top5_reranked'][0].get('ce_score', 1) == 0]
print(f"\n[CE_SCORE == 0 count: {len(zero_scores)}]")

print(f"\n{'='*60}")
print("DONE")
