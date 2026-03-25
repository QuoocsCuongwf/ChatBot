"""
test_e2e_generation.py — End-to-End Generation Quality Test

Chạy N samples qua pipeline đầy đủ (context build → gating → LLM → parse → eval)
với real LLM (Qwen local hoặc API), so sánh citations với expected.

Usage:
    # Quick smoke test (3 samples, placeholder — kiểm tra pipeline logic)
    python test_e2e_generation.py --quick

    # Real test với Qwen local (5 samples)
    python test_e2e_generation.py --backend huggingface --samples 5

    # Full test (tất cả 323 queries)
    python test_e2e_generation.py --backend huggingface --samples 0
"""

import argparse
import json
import sys
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional

sys.path.append(str(Path(__file__).parent.parent))

from generation.rag_contract import (
    RAGInput, ChunkInfo, Citation, RAGPolicy,
    parse_rag_output, DecisionType, LLMTier
)
from generation.context_builder import ContextBuilder
from generation.prompt_templates import LegalPromptBuilder, PromptConfig
from generation.gating import GatingStrategy, GatingConfig


@dataclass
class E2EResult:
    query_id: str
    query: str
    decision: str = ""
    tier: str = ""
    top1_score: float = 0.0
    margin: float = 0.0
    semantic_sim: float = 0.0
    lexical_overlap: float = 0.0
    num_citations_expected: int = 0
    num_citations_parsed: int = 0
    citation_hit: bool = False
    answer_preview: str = ""
    latency_llm_ms: float = 0.0
    error: Optional[str] = None
    trimmed_context_len: int = 0


def load_reranked_jsonl(path: Path) -> List[Dict]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def record_to_chunks(rec: Dict) -> List[ChunkInfo]:
    chunks = []
    for item in rec.get("top5_reranked", []):
        meta = item.get("metadata", item.get("meta", {}))
        chunk = ChunkInfo(
            chunk_id=item.get("chunk_id", item.get("chunk_index", item.get("faiss_id", -1))),
            text=item.get("text", item.get("passage", "")),
            score_retrieval=item.get("score_retrieval", 0.0),
            score_rerank=item.get("ce_score", item.get("score", 0.0)),
            van_ban=item.get("van_ban", meta.get("van_ban", "")),
            chuong=item.get("chuong", meta.get("chuong")),
            dieu=item.get("dieu", meta.get("dieu")),
            khoan=item.get("khoan", meta.get("khoan")),
            diem=item.get("diem", meta.get("diem")),
        )
        chunks.append(chunk)
    return chunks


def run_e2e_test(
    records: List[Dict],
    backend: str = "placeholder",
    verbose: bool = True
) -> List[E2EResult]:
    """Run end-to-end test and return results."""

    # --- Setup gating (CE sigmoid mode) ---
    gating_config = GatingConfig(
        threshold_pass=0.5,
        threshold_abstain=0.05,
        threshold_cautious=0.3,
        margin_min=0.001,
        margin_scale=100.0,
        tier_local_min_score=0.9,
        tier_local_min_margin=0.005,
        tier_api_min_score=0.05,
        enable_ask_back=False,
        score_is_sigmoid=True,
    )
    gating = GatingStrategy(gating_config)
    builder = ContextBuilder()
    prompt_builder = LegalPromptBuilder(PromptConfig(require_json_output=True))

    # --- Setup LLM ---
    llm_client = None
    if backend != "placeholder":
        from generation.llm_client import LLMClient, LLMConfig, LLMBackend
        be = LLMBackend(backend)
        config = LLMConfig(backend=be)
        if be == LLMBackend.HUGGINGFACE:
            from generation.llm_client import select_local_model_for_vram
            config.model_name = select_local_model_for_vram()
            config.max_new_tokens = 512
        llm_client = LLMClient(config)
        print(f"[LLM] Backend: {backend}, Model: {config.model_name}")
    else:
        print("[LLM] Placeholder mode — skipping actual generation, testing pipeline logic only")

    results: List[E2EResult] = []

    for i, rec in enumerate(records):
        qid = rec.get("id", f"q_{i}")
        query = rec.get("query", "")
        expected_citations = rec.get("expected_citations", [])
        chunks = record_to_chunks(rec)

        res = E2EResult(
            query_id=qid,
            query=query,
            num_citations_expected=len(expected_citations),
        )

        if verbose:
            print(f"\n{'='*60}")
            print(f"[{i+1}/{len(records)}] {qid}: {query[:80]}")

        # --- Step 1: Context Build ---
        policy = RAGPolicy()
        processed_chunks, context_string = builder.build(
            chunks=chunks,
            query=query,
            max_chunks=policy.max_chunks_in_context,
            enable_dedup=True,
            enable_trim=True,
            enable_metadata=True,
        )
        res.trimmed_context_len = len(context_string)

        if verbose:
            print(f"  [1] Context: {len(chunks)} chunks → {len(processed_chunks)} after dedup, "
                  f"trimmed len={res.trimmed_context_len}")

        # --- Step 2: Gating ---
        rag_input = RAGInput(
            question=query,
            top_k_chunks=processed_chunks,
            policy=policy,
        )
        decision = gating.evaluate(rag_input)
        res.decision = decision.decision.value
        res.tier = decision.tier.value
        res.top1_score = chunks[0].score_rerank if chunks else 0.0
        res.margin = decision.margin
        res.semantic_sim = decision.semantic_similarity
        res.lexical_overlap = decision.lexical_overlap

        if verbose:
            print(f"  [2] Gating: {res.decision} / Tier={res.tier} "
                  f"(score={res.top1_score:.4f}, margin={res.margin:.6f}, "
                  f"sem_sim={res.semantic_sim:.4f}, lex_ovl={res.lexical_overlap:.2f})")

        # --- Step 3: Generation ---
        if decision.decision not in (DecisionType.ANSWER, DecisionType.CAUTIOUS):
            if verbose:
                print(f"  [3] Skipped (gating={res.decision})")
            results.append(res)
            continue

        if llm_client is None:
            # Placeholder: simulate answer with chunk metadata
            top = processed_chunks[0] if processed_chunks else None
            if top and top.dieu:
                simulated = json.dumps({
                    "answer": f"Theo Điều {top.dieu} của {top.van_ban}...",
                    "citations": [{"van_ban": top.van_ban, "dieu": top.dieu,
                                   "khoan": top.khoan, "diem": top.diem}],
                    "abstain": False
                }, ensure_ascii=False)
            else:
                simulated = json.dumps({
                    "answer": "Placeholder answer.",
                    "citations": [],
                    "abstain": False
                })
            output = parse_rag_output(simulated)
            res.latency_llm_ms = 0
        else:
            use_compact = backend in ("huggingface", "qwen")
            sys_prompt = prompt_builder.build_system_prompt(compact=use_compact)
            usr_prompt = prompt_builder.build_user_prompt(question=query, context=context_string)

            t0 = time.time()
            llm_response = llm_client.generate(usr_prompt, system_prompt=sys_prompt)
            res.latency_llm_ms = (time.time() - t0) * 1000

            if llm_response.error:
                res.error = llm_response.error
                if verbose:
                    print(f"  [3] LLM ERROR: {llm_response.error}")
                results.append(res)
                continue

            output = parse_rag_output(llm_response.text)

        res.num_citations_parsed = len(output.citations)
        res.answer_preview = (output.answer or "")[:100].replace("\n", " ")

        if verbose:
            print(f"  [3] LLM: {res.latency_llm_ms:.0f}ms, "
                  f"citations={res.num_citations_parsed}, "
                  f"answer={res.answer_preview[:60]}...")

        # --- Step 4: Citation Hit Check ---
        if not output.abstain and output.citations and expected_citations:
            for cit in output.citations:
                for ec in expected_citations:
                    if cit.matches(ec):
                        res.citation_hit = True
                        break
                if res.citation_hit:
                    break

        if verbose:
            hit_str = "HIT" if res.citation_hit else "MISS"
            print(f"  [4] Citation: {hit_str} "
                  f"(parsed={res.num_citations_parsed}, expected={res.num_citations_expected})")

        results.append(res)

    return results


def print_summary(results: List[E2EResult]):
    n = len(results)
    if n == 0:
        print("No results.")
        return

    # Counts
    pass_count = sum(1 for r in results if r.decision in ("answer", "cautious"))
    abstain_count = sum(1 for r in results if r.decision in ("abstain", "ask_back"))
    citation_hits = sum(1 for r in results if r.citation_hit)
    errors = sum(1 for r in results if r.error)

    tier_counts = {}
    for r in results:
        tier_counts[r.tier] = tier_counts.get(r.tier, 0) + 1

    avg_latency = (sum(r.latency_llm_ms for r in results if r.latency_llm_ms > 0)
                   / max(1, sum(1 for r in results if r.latency_llm_ms > 0)))
    avg_ctx_len = sum(r.trimmed_context_len for r in results) / n

    # Print
    print("\n" + "=" * 60)
    print("  END-TO-END GENERATION TEST SUMMARY")
    print("=" * 60)
    print(f"  Total samples:       {n}")
    print(f"  Pass Rate:           {pass_count}/{n} ({pass_count/n:.1%})")
    print(f"  Abstain/AskBack:     {abstain_count}/{n} ({abstain_count/n:.1%})")
    print(f"  Citation Hit Rate:   {citation_hits}/{n} ({citation_hits/n:.1%})")
    print(f"  Errors:              {errors}/{n} ({errors/n:.1%})")
    print(f"  Avg LLM Latency:     {avg_latency:.0f}ms")
    print(f"  Avg Context Length:  {avg_ctx_len:.0f} chars")
    print()
    print("  Tier Routing:")
    for tier_name in ["local", "api", "none"]:
        cnt = tier_counts.get(tier_name, 0)
        bar = "█" * int(cnt / n * 30)
        print(f"    {tier_name:8s}  {cnt:4d}  ({cnt/n:.1%})  {bar}")

    # Citation Hit Rate breakdown by tier
    print("\n  Citation Hit by Tier:")
    for tier_name in ["local", "api"]:
        tier_results = [r for r in results if r.tier == tier_name]
        if tier_results:
            hits = sum(1 for r in tier_results if r.citation_hit)
            print(f"    {tier_name:8s}: {hits}/{len(tier_results)} ({hits/len(tier_results):.1%})")

    # Citation Hit by score bucket
    print("\n  Citation Hit by Score Bucket:")
    for lo, hi, label in [(0.99, 1.01, ">=0.99"), (0.9, 0.99, "0.9-0.99"), (0.5, 0.9, "0.5-0.9"), (0, 0.5, "<0.5")]:
        bucket = [r for r in results if lo <= r.top1_score < hi]
        if bucket:
            hits = sum(1 for r in bucket if r.citation_hit)
            print(f"    Score {label:8s}: {hits}/{len(bucket)} ({hits/len(bucket):.1%})")

    # Worst cases (MISS with high score)
    misses = [r for r in results if not r.citation_hit and r.decision in ("answer", "cautious")]
    if misses:
        misses_sorted = sorted(misses, key=lambda r: -r.top1_score)
        print(f"\n  Top-5 High-Score Misses:")
        for r in misses_sorted[:5]:
            print(f"    {r.query_id}: score={r.top1_score:.4f}, "
                  f"cit_parsed={r.num_citations_parsed}, "
                  f"query={r.query[:50]}...")

    print()


def main():
    parser = argparse.ArgumentParser(description="End-to-end generation quality test")
    parser.add_argument("--data", type=str, default=None,
                        help="Path to reranked JSONL (default: auto-detect)")
    parser.add_argument("--samples", type=int, default=5,
                        help="Number of samples (0=all)")
    parser.add_argument("--backend", type=str, default="placeholder",
                        choices=["placeholder", "huggingface", "gemini", "openrouter"],
                        help="LLM backend")
    parser.add_argument("--quick", action="store_true",
                        help="Quick test: 3 samples, placeholder")
    parser.add_argument("--verbose", "-v", action="store_true", default=True)
    parser.add_argument("--quiet", "-q", action="store_true")
    parser.add_argument("--save", type=str, default=None,
                        help="Save results to JSONL file")

    args = parser.parse_args()

    if args.quiet:
        args.verbose = False
    if args.quick:
        args.samples = 3
        args.backend = "placeholder"

    # Find data file
    if args.data:
        data_path = Path(args.data)
    else:
        candidates = [
            Path(__file__).parent.parent / "data" / "pipeline_results_v5_1.jsonl",
            Path(__file__).parent / "data" / "pipeline_results_v5_1.jsonl",
        ]
        data_path = None
        for c in candidates:
            if c.exists():
                data_path = c
                break
        if data_path is None:
            print("ERROR: Cannot find pipeline_results_v5_1.jsonl. Use --data to specify path.")
            sys.exit(1)

    records = load_reranked_jsonl(data_path)
    print(f"Loaded {len(records)} records from {data_path}")

    if args.samples > 0:
        records = records[:args.samples]
        print(f"Using first {args.samples} samples")

    # Run
    results = run_e2e_test(records, backend=args.backend, verbose=args.verbose)

    # Summary
    print_summary(results)

    # Optional save
    if args.save:
        save_path = Path(args.save)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r.__dict__, ensure_ascii=False, default=str) + "\n")
        print(f"Results saved to {save_path}")


if __name__ == "__main__":
    main()
