"""
run_generation.py — Main Generation Pipeline

Integrates:
1. Retrieval (FAISS + Bi-encoder)
2. Reranking (Cross-encoder)
3. Context Building (Dedup, Trim, Metadata)
4. Gating (Pass/Abstain/Ask-back)
5. Generation (LLM)
6. Fallback (Cautious/Ask-back)
7. Evaluation

Usage:
    python run_generation.py --mode dev --eval
    python run_generation.py --mode demo --query "Ai có thẩm quyền..."
    python run_generation.py --eval --max_samples 50
"""

import argparse
import json
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Add parent path
sys.path.append(str(Path(__file__).parent.parent))

# Imports
from generation.rag_contract import (
    RAGInput, RAGOutput, ChunkInfo, Citation, RAGPolicy,
    create_rag_input, parse_rag_output, DecisionType
)
from generation.context_builder import ContextBuilder, build_context_for_generation
from generation.prompt_templates import LegalPromptBuilder, PromptConfig, PromptStyle
from generation.gating import GatingStrategy, GatingConfig, GatingDecision
from generation.llm_client import LLMClient, LLMConfig, LLMBackend, LLMMode
from generation.fallback import FallbackStrategy, apply_fallback_if_needed
from generation.evaluator import (
    GenerationEvaluator, EvalSample, EvalResult, EvalSummary,
    load_goldset, create_goldset_from_eval_qa
)


def load_dev_jsonl(dev_path: Path) -> List["EvalSample"]:
    """
    Load dev.jsonl format (from cross-encoder/data/).
    
    Format: {"query": "...", "passage": "...", "label": 1, "meta": {...}}
    """
    samples = []
    seen_queries = set()  # Deduplicate
    
    with open(dev_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                query = data.get("query", "")
                
                # Skip if already seen (avoid duplicates)
                if query in seen_queries:
                    continue
                seen_queries.add(query)
                
                # Only use label=1 (positive samples)
                if data.get("label") != 1:
                    continue
                
                # Extract expected citation from meta
                meta = data.get("meta", {})
                expected_citations = [{
                    "van_ban": meta.get("van_ban", ""),
                    "chuong": meta.get("chuong"),
                    "dieu": meta.get("dieu"),
                    "khoan": meta.get("khoan"),
                    "diem": meta.get("diem"),
                    "chunk_index": meta.get("chunk_index")
                }]
                
                sample = EvalSample(
                    query_id=f"dev_{i}",
                    query=query,
                    expected_citations=expected_citations,
                    expected_answer=data.get("passage")  # Use passage as reference
                )
                samples.append(sample)
                
            except json.JSONDecodeError:
                continue
    
    return samples


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG & PATHS
# ═══════════════════════════════════════════════════════════════════════════════

ROOT = Path(__file__).parent
PROJECT_ROOT = ROOT.parent.parent  # ChatBot/
DATA_DIR = ROOT / "data"
EVAL_DIR = ROOT / "outputs" / "eval"
TMP_DIR = ROOT / "outputs" / "tmp"
GEN_EVAL_DIR = ROOT / "outputs" / "generation"

# Model paths - using actual paths from existing pipeline
# ROOT.parent = cross-encoder/, so outputs is there
CE_MODEL = ROOT.parent / "outputs" / "models" / "cross_encoder_faiss_matched" / "saved_model"

# FAISS index and metadata - using legal_hf_cosine (normalized IP index)
FAISS_INDEX_DIR = PROJECT_ROOT / "vector_data" / "legal_hf_cosine"
FAISS_INDEX_FILE = FAISS_INDEX_DIR / "index.faiss"
FAISS_METADATA_FILE = FAISS_INDEX_DIR / "metadata.json"

# Bi-encoder model - MUST match the model used to build FAISS index
BI_ENCODER_MODEL = "Quockhanh05/Vietnam_legal_embeddings"

# Goldset - in retrieval folder
GOLDSET_FILE = PROJECT_ROOT / "retrieval" / "goldset.jsonl"

# Dev data for evaluation - use cross-encoder data (parent of generation/)
EVAL_QA_FILE = ROOT.parent / "data" / "dev.jsonl"


# ═══════════════════════════════════════════════════════════════════════════════
# RETRIEVER (Wrapper for existing infrastructure)
# ═══════════════════════════════════════════════════════════════════════════════

class LegalRetriever:
    """
    Retriever wrapper that uses existing FAISS index and Cross-encoder.
    """
    
    def __init__(
        self,
        faiss_index_path: Optional[Path] = None,
        faiss_mapping_path: Optional[Path] = None,
        ce_model_path: Optional[Path] = None,
        device: str = "cuda"
    ):
        self.device = device
        self.faiss_index = None
        self.faiss_mapping = None
        self.bi_encoder = None
        self.ce_model = None
        
        # Try to load existing components
        self._load_components(faiss_index_path, faiss_mapping_path, ce_model_path)
    
    def _load_components(
        self,
        faiss_index_path: Optional[Path],
        faiss_mapping_path: Optional[Path],
        ce_model_path: Optional[Path]
    ):
        """Load retriever components."""
        
        try:
            import faiss
            import numpy as np
            from sentence_transformers import SentenceTransformer, CrossEncoder
            
            # Load FAISS index - use correct path
            index_path = faiss_index_path or FAISS_INDEX_FILE
            if index_path.exists():
                self.faiss_index = faiss.read_index(str(index_path))
                print(f"[Retriever] Loaded FAISS index: {self.faiss_index.ntotal} vectors")
            else:
                print(f"[Retriever] Warning: FAISS index not found at {index_path}")
            
            # Load metadata (JSON array format from legal_hf)
            mapping_path = faiss_mapping_path or FAISS_METADATA_FILE
            if mapping_path.exists():
                with open(mapping_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                # Convert format: [{text, metadata}, ...] -> [{passage, van_ban, ...}, ...]
                self.faiss_mapping = []
                for item in raw_data:
                    entry = {
                        "passage": item.get("text", ""),
                        **item.get("metadata", {})
                    }
                    self.faiss_mapping.append(entry)
                print(f"[Retriever] Loaded metadata: {len(self.faiss_mapping)} entries")
            else:
                print(f"[Retriever] Warning: Metadata not found at {mapping_path}")
            
            # Load bi-encoder - MUST match model used to build FAISS index
            self.bi_encoder = SentenceTransformer(
                BI_ENCODER_MODEL,
                device=self.device
            )
            print(f"[Retriever] Loaded bi-encoder: {BI_ENCODER_MODEL}")
            
            # Load cross-encoder
            ce_path = ce_model_path or CE_MODEL
            if ce_path.exists():
                self.ce_model = CrossEncoder(str(ce_path), max_length=256, device=self.device)
                print(f"[Retriever] Loaded cross-encoder: {ce_path}")
            
        except Exception as e:
            print(f"[Retriever] Warning: Could not load components: {e}")
    
    def retrieve_and_rerank(
        self,
        query: str,
        top_k_retrieve: int = 50,
        top_k_rerank: int = 10
    ) -> List[ChunkInfo]:
        """
        Retrieve and rerank chunks for a query.
        
        Returns:
            List of ChunkInfo sorted by rerank score
        """
        
        if not self.faiss_index or not self.faiss_mapping:
            print("[Retriever] Warning: Using placeholder chunks")
            return self._get_placeholder_chunks(query)
        
        import numpy as np
        
        # Encode query
        q_emb = self.bi_encoder.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype("float32")
        
        # Search FAISS
        scores_faiss, ids = self.faiss_index.search(q_emb, top_k_retrieve)
        scores_faiss = scores_faiss[0].tolist()
        ids = [i for i in ids[0].tolist() if i >= 0 and i < len(self.faiss_mapping)]
        
        # Get candidate chunks with deduplication
        candidates = []
        seen_texts = set()  # Deduplicate by text hash
        
        for i, faiss_id in enumerate(ids):
            mapping = self.faiss_mapping[faiss_id]
            text = mapping.get("text", "")
            
            # Skip duplicates
            text_hash = hash(text[:200])  # Hash first 200 chars for dedup
            if text_hash in seen_texts:
                continue
            seen_texts.add(text_hash)
            
            meta = mapping.get("metadata", {})  # nested metadata dict
            chunk = ChunkInfo(
                chunk_id=faiss_id,
                text=text,
                score_retrieval=scores_faiss[i] if i < len(scores_faiss) else 0.0,
                score_rerank=0.0,
                van_ban=meta.get("van_ban", ""),
                chuong=meta.get("chuong"),
                dieu=meta.get("dieu"),
                khoan=meta.get("khoan"),
                diem=meta.get("diem"),
                source_file=meta.get("source_file", "")
            )
            candidates.append(chunk)
        
        # Rerank
        if self.ce_model and candidates:
            pairs = [[query, c.text] for c in candidates]
            rerank_scores = self.ce_model.predict(pairs, batch_size=32)
            
            for i, score in enumerate(rerank_scores):
                candidates[i].score_rerank = float(score)
            
            # Sort by rerank score
            candidates.sort(key=lambda x: x.score_rerank, reverse=True)
        else:
            # No cross-encoder: use retrieval scores as rerank scores
            for c in candidates:
                c.score_rerank = c.score_retrieval
            candidates.sort(key=lambda x: x.score_rerank, reverse=True)
        
        return candidates[:top_k_rerank]
    
    def _get_placeholder_chunks(self, query: str) -> List[ChunkInfo]:
        """Get placeholder chunks for testing."""
        return [
            ChunkInfo(
                chunk_id=0,
                text="[Placeholder] Đây là nội dung mẫu cho testing.",
                score_retrieval=0.5,
                score_rerank=1.0,
                van_ban="Nghị định mẫu",
                dieu="1"
            )
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATION PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

class GenerationPipeline:
    """
    End-to-end Legal RAG Generation Pipeline.
    
    Pipeline:
    1. Retrieve & Rerank
    2. Context Building
    3. Gating Decision
    4. LLM Generation
    5. Fallback (if needed)
    6. Output Parsing
    """
    
    def __init__(
        self,
        retriever: Optional[LegalRetriever] = None,
        llm_client: Optional[LLMClient] = None,
        mode: LLMMode = LLMMode.DEV
    ):
        # Initialize components
        self.retriever = retriever or LegalRetriever()
        self.llm_client = llm_client or LLMClient()
        
        # Pipeline components
        self.context_builder = ContextBuilder()
        self.prompt_builder = LegalPromptBuilder()
        
        # Adjust gating thresholds based on whether cross-encoder is loaded
        if self.retriever.ce_model is not None:
            # Cross-encoder mode: trained model outputs negative logits
            # Note: text format mismatch lowers scores, so use looser thresholds
            gating_config = GatingConfig(
                threshold_pass=-8.0,      # > -8 is likely relevant
                threshold_abstain=-11.5,  # < -11.5 is clearly not relevant
                threshold_cautious=-10.0, # uncertain zone
                margin_min=1.0            # require 1.0 logit gap
            )
        else:
            # Bi-encoder only mode: cosine scores are 0-1
            gating_config = GatingConfig(
                threshold_pass=0.6,      # Lowered for cosine
                threshold_abstain=0.3,   # Lowered for cosine  
                threshold_cautious=0.5,  # Lowered for cosine
                margin_min=0.05          # Much smaller for cosine
            )
            print("[Pipeline] Using bi-encoder only mode (adjusted gating thresholds)")
        
        self.gating = GatingStrategy(gating_config)
        self.fallback = FallbackStrategy()
        
        # Config
        self.mode = mode
        self.top_k_chunks = 5
        
        print(f"[Pipeline] Initialized in {mode.value} mode")
        print(f"[Pipeline] LLM backend: {self.llm_client.config.backend.value}")
    
    def generate(
        self,
        query: str,
        verbose: bool = False
    ) -> Tuple[RAGOutput, Dict]:
        """
        Generate answer for a query.
        
        Returns:
            (RAGOutput, metadata_dict)
        """
        
        metadata = {
            "query": query,
            "timestamps": {},
            "decisions": {}
        }
        
        start_time = time.time()
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 1: Retrieve & Rerank
        # ─────────────────────────────────────────────────────────────────────
        
        t0 = time.time()
        chunks = self.retriever.retrieve_and_rerank(query, top_k_rerank=self.top_k_chunks * 2)
        metadata["timestamps"]["retrieve_rerank"] = (time.time() - t0) * 1000
        
        if verbose:
            print(f"[1] Retrieved {len(chunks)} chunks, top score: {chunks[0].score_rerank:.2f}" if chunks else "[1] No chunks")
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 2: Context Building
        # ─────────────────────────────────────────────────────────────────────
        
        t0 = time.time()
        processed_chunks, context_string = self.context_builder.build(
            chunks=chunks,
            query=query,
            max_chunks=self.top_k_chunks
        )
        metadata["timestamps"]["context_build"] = (time.time() - t0) * 1000
        metadata["context_tokens_est"] = int(len(context_string) / 1.5)
        
        if verbose:
            print(f"[2] Context built: {len(processed_chunks)} chunks, ~{metadata['context_tokens_est']} tokens")
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 3: Gating Decision
        # ─────────────────────────────────────────────────────────────────────
        
        rag_input = RAGInput(
            question=query,
            top_k_chunks=processed_chunks,
            policy=RAGPolicy()
        )
        
        gating_decision = self.gating.evaluate(rag_input)
        metadata["decisions"]["gating"] = gating_decision.to_dict()
        
        if verbose:
            print(f"[3] Gating: {gating_decision.decision.value} (confidence: {gating_decision.confidence:.2f})")
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 4: Generate or Fallback
        # ─────────────────────────────────────────────────────────────────────
        
        if not self.gating.should_generate(gating_decision):
            # Early exit with gating response
            output = self.gating.build_gated_output(gating_decision)
            metadata["timestamps"]["total"] = (time.time() - start_time) * 1000
            metadata["skipped_generation"] = True
            
            if verbose:
                print(f"[4] Skipped generation (gating: {gating_decision.decision.value})")
            
            return output, metadata
        
        # Build prompt
        prompt = self.prompt_builder.build_full_prompt(
            question=query,
            context=context_string
        )
        
        # Generate
        t0 = time.time()
        llm_response = self.llm_client.generate(prompt)
        metadata["timestamps"]["llm"] = (time.time() - t0) * 1000
        
        if verbose:
            print(f"[4] LLM generated in {metadata['timestamps']['llm']:.0f}ms")
        
        # Parse response
        output = parse_rag_output(llm_response.text)
        output.latency_llm_ms = metadata["timestamps"]["llm"]
        output.raw_response = llm_response.text
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 5: Apply Fallback if needed
        # ─────────────────────────────────────────────────────────────────────
        
        if gating_decision.decision == DecisionType.CAUTIOUS:
            # Apply cautious fallback
            fallback_decision = self.fallback.evaluate(query, processed_chunks)
            
            if fallback_decision.fallback_type.value != "none":
                output = self.fallback.build_cautious_response(
                    fallback_decision,
                    output.answer or "",
                    output.citations
                )
                metadata["decisions"]["fallback"] = fallback_decision.to_dict()
                
                if verbose:
                    print(f"[5] Applied fallback: {fallback_decision.fallback_type.value}")
        
        metadata["timestamps"]["total"] = (time.time() - start_time) * 1000
        
        return output, metadata
    
    def generate_batch(
        self,
        queries: List[str],
        verbose: bool = False
    ) -> List[Tuple[RAGOutput, Dict]]:
        """Generate answers for multiple queries."""
        
        results = []
        
        for i, query in enumerate(queries):
            if verbose:
                print(f"\n[{i+1}/{len(queries)}] {query[:50]}...")
            
            output, metadata = self.generate(query, verbose=verbose)
            results.append((output, metadata))
        
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def parse_args():
    parser = argparse.ArgumentParser(description="Legal RAG Generation Pipeline")
    
    # Mode
    parser.add_argument("--mode", choices=["dev", "demo"], default="dev",
                       help="Pipeline mode: dev (fast) or demo (quality)")
    
    # Single query
    parser.add_argument("--query", type=str, default=None,
                       help="Single query to process")
    
    # Evaluation
    parser.add_argument("--eval", action="store_true",
                       help="Run evaluation on goldset")
    parser.add_argument("--max_samples", type=int, default=50,
                       help="Max samples for evaluation")
    parser.add_argument("--goldset", type=str, default=None,
                       help="Path to goldset JSONL file")
    
    # LLM config
    parser.add_argument("--backend", type=str, default=None,
                       choices=["llama_cpp", "openrouter", "openai", "gemini", "placeholder"],
                       help="LLM backend")
    parser.add_argument("--model", type=str, default=None,
                       help="Model name or path")
    
    # Output
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--output", type=str, default=None,
                       help="Output file path")
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Setup directories
    GEN_EVAL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Configure LLM
    llm_config = LLMConfig(
        mode=LLMMode.DEV if args.mode == "dev" else LLMMode.DEMO,
        max_tokens=256 if args.mode == "dev" else 512,
        context_length=2048 if args.mode == "dev" else 4096,
        temperature=0.1
    )
    
    if args.backend:
        llm_config.backend = LLMBackend(args.backend)
    if args.model:
        if args.backend == "llama_cpp":
            llm_config.model_path = args.model
        else:
            llm_config.model_name = args.model
    
    llm_client = LLMClient(llm_config)
    
    # Initialize pipeline
    print("=" * 60)
    print("Legal RAG Generation Pipeline")
    print("=" * 60)
    
    retriever = LegalRetriever()
    pipeline = GenerationPipeline(
        retriever=retriever,
        llm_client=llm_client,
        mode=LLMMode.DEV if args.mode == "dev" else LLMMode.DEMO
    )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Mode: Single Query
    # ─────────────────────────────────────────────────────────────────────────
    
    if args.query:
        print(f"\nQuery: {args.query}\n")
        
        output, metadata = pipeline.generate(args.query, verbose=args.verbose)
        
        print("\n" + "=" * 40)
        print("RESULT:")
        print("=" * 40)
        
        if output.abstain:
            print(f"[ABSTAIN] {output.reason_detail}")
            if output.clarification_question:
                print(f"Question: {output.clarification_question}")
        else:
            print(f"Answer: {output.answer}")
            print(f"\nCitations:")
            for cit in output.citations:
                print(f"  - {cit.to_str()}")
        
        print(f"\nLatency: {metadata['timestamps']['total']:.0f}ms")
        
        # Save if output path specified
        if args.output:
            result = {
                "query": args.query,
                "output": output.to_dict(),
                "metadata": metadata
            }
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\nSaved to {args.output}")
        
        return
    
    # ─────────────────────────────────────────────────────────────────────────
    # Mode: Evaluation
    # ─────────────────────────────────────────────────────────────────────────
    
    if args.eval:
        print("\n" + "=" * 40)
        print("EVALUATION MODE")
        print("=" * 40)
        
        # Load goldset (dev.jsonl from cross-encoder/data/)
        goldset_path = Path(args.goldset) if args.goldset else EVAL_QA_FILE
        
        if not goldset_path.exists():
            print(f"Error: Goldset not found: {goldset_path}")
            return
        
        # Use custom loader for dev.jsonl format
        samples = load_dev_jsonl(goldset_path)
        print(f"Loaded {len(samples)} unique samples from {goldset_path}")
        
        if args.max_samples:
            samples = samples[:args.max_samples]
            print(f"Using first {len(samples)} samples")
        
        # Create gating config adjusted for bi-encoder only mode if CE not loaded
        if retriever.ce_model is None:
            eval_gating_config = GatingConfig(
                threshold_pass=0.6,
                threshold_abstain=0.3,
                threshold_cautious=0.5,
                margin_min=0.05,
                enable_ask_back=False  # Disable for evaluation
            )
        else:
            # Cross-encoder mode: new FAISS-matched model outputs positive scores ~(-5 to +11)
            eval_gating_config = GatingConfig(
                threshold_pass=8.0,       # High confidence score
                threshold_abstain=-5.0,   # Very low score
                threshold_cautious=3.0,   # Moderate score
                margin_min=0.1,           # Small margin needed
                enable_ask_back=False     # Disable for evaluation
            )
        eval_gating = GatingStrategy(eval_gating_config)
        
        # Create evaluator with adjusted gating
        evaluator = GenerationEvaluator(
            llm_client=llm_client,
            output_dir=GEN_EVAL_DIR,
            gating_strategy=eval_gating
        )
        
        # Run evaluation
        def retriever_fn(query: str) -> List[ChunkInfo]:
            return retriever.retrieve_and_rerank(query)
        
        results, summary = evaluator.evaluate_batch(
            samples=samples,
            retriever_fn=retriever_fn,
            verbose=args.verbose,
            max_samples=args.max_samples
        )
        
        # Print summary
        print("\n" + "=" * 40)
        print("EVALUATION SUMMARY")
        print("=" * 40)
        print(f"Total samples: {summary.total_samples}")
        print(f"Citation Hit Rate: {summary.citation_hit_rate:.2%}")
        print(f"Avg Citation F1: {summary.avg_citation_f1:.4f}")
        print(f"Pass Rate: {summary.pass_rate:.2%}")
        print(f"Abstain Rate: {summary.abstain_rate:.2%}")
        print(f"Avg Latency: {summary.avg_latency_total_ms:.0f}ms")
        
        # Save results
        saved_paths = evaluator.save_results(results, summary)
        
        return
    
    # ─────────────────────────────────────────────────────────────────────────
    # Interactive mode
    # ─────────────────────────────────────────────────────────────────────────
    
    print("\nInteractive mode. Type 'quit' to exit.\n")
    
    while True:
        try:
            query = input("Query: ").strip()
            
            if query.lower() in ["quit", "exit", "q"]:
                break
            
            if not query:
                continue
            
            output, metadata = pipeline.generate(query, verbose=args.verbose)
            
            print("\n" + "-" * 40)
            if output.abstain:
                print(f"[{output.decision.value.upper()}] {output.reason_detail}")
                if output.clarification_question:
                    print(f"❓ {output.clarification_question}")
            else:
                print(f"Answer: {output.answer}")
                if output.citations:
                    print(f"Citations: {', '.join(c.to_str() for c in output.citations)}")
            print(f"[{metadata['timestamps']['total']:.0f}ms]")
            print("-" * 40 + "\n")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()
