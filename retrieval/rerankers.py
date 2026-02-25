"""
Reranking Models cho Vietnamese Legal Documents
================================================

Cung cấp nhiều lựa chọn reranker:
1. Cross-encoder (sentence-transformers)
2. Cohere Rerank (API)
3. Vietnamese-specific models

Usage trong eval_all_models.py
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod

import numpy as np


class BaseReranker(ABC):
    """Abstract base class cho rerankers"""
    
    @abstractmethod
    def rerank(
        self,
        query: str,
        candidates: List[Dict],
        topk: int = 5,
    ) -> List[Dict]:
        """
        Rerank candidates và trả về top-k
        
        Args:
            query: Query string
            candidates: List of dicts với keys: rank, score, text, metadata
            topk: Số kết quả trả về
            
        Returns:
            List reranked với updated rank và score
        """
        pass


class CrossEncoderReranker(BaseReranker):
    """Reranker dùng Cross-Encoder"""
    
    # Các model có thể dùng
    AVAILABLE_MODELS = {
        # Multilingual / Vietnamese-friendly
        "bge-reranker-base": "BAAI/bge-reranker-base",
        "bge-reranker-large": "BAAI/bge-reranker-large",
        "bge-reranker-v2-m3": "BAAI/bge-reranker-v2-m3",  # Multilingual, tốt cho tiếng Việt
        
        # MiniLM (lightweight)
        "ms-marco-minilm": "cross-encoder/ms-marco-MiniLM-L-6-v2",
        "ms-marco-minilm-12": "cross-encoder/ms-marco-MiniLM-L-12-v2",
        
        # Robust
        "ms-marco-electra": "cross-encoder/ms-marco-electra-base",
        
        # Vietnamese-specific (nếu có)
        # Thêm vào đây nếu tìm được model Vietnamese
    }
    
    def __init__(
        self, 
        model_name: str = "bge-reranker-base",
        device: str = "cuda",
        batch_size: int = 32,
    ):
        from sentence_transformers import CrossEncoder
        
        # Resolve model name
        if model_name in self.AVAILABLE_MODELS:
            model_path = self.AVAILABLE_MODELS[model_name]
        else:
            model_path = model_name  # Assume full path
        
        self.model = CrossEncoder(model_path, device=device)
        self.model_name = model_name
        self.batch_size = batch_size
    
    def rerank(
        self,
        query: str,
        candidates: List[Dict],
        topk: int = 5,
    ) -> List[Dict]:
        if not candidates:
            return []
        
        # Prepare pairs
        pairs = [(query, c.get("text", "")) for c in candidates]
        
        # Score in batches
        scores = self.model.predict(pairs, batch_size=self.batch_size)
        
        # Combine with candidates
        scored = []
        for i, c in enumerate(candidates):
            scored.append({
                **c,
                "original_score": c["score"],
                "original_rank": c["rank"],
                "rerank_score": float(scores[i]),
            })
        
        # Sort by rerank score
        scored.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        # Update ranks
        results = []
        for new_rank, item in enumerate(scored[:topk], start=1):
            item["rank"] = new_rank
            item["score"] = item["rerank_score"]
            results.append(item)
        
        return results


class TFIDFReranker(BaseReranker):
    """
    Reranker đơn giản dùng TF-IDF similarity
    Không cần GPU, nhanh
    """
    
    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self._cosine_similarity = cosine_similarity
    
    def rerank(
        self,
        query: str,
        candidates: List[Dict],
        topk: int = 5,
    ) -> List[Dict]:
        if not candidates:
            return []
        
        # Prepare texts
        texts = [c.get("text", "") for c in candidates]
        all_texts = [query] + texts
        
        # Vectorize
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        except ValueError:
            # Nếu không đủ features
            return candidates[:topk]
        
        # Query vector is first
        query_vec = tfidf_matrix[0:1]
        doc_vecs = tfidf_matrix[1:]
        
        # Compute similarities
        sims = self._cosine_similarity(query_vec, doc_vecs).ravel()
        
        # Combine scores
        scored = []
        for i, c in enumerate(candidates):
            scored.append({
                **c,
                "original_score": c["score"],
                "original_rank": c["rank"],
                "tfidf_score": float(sims[i]),
                "rerank_score": float(sims[i]),  # Use tfidf as rerank
            })
        
        # Sort
        scored.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        # Update ranks
        results = []
        for new_rank, item in enumerate(scored[:topk], start=1):
            item["rank"] = new_rank
            item["score"] = item["rerank_score"]
            results.append(item)
        
        return results


class CombinedReranker(BaseReranker):
    """
    Kết hợp nhiều reranker với weighted score
    """
    
    def __init__(
        self,
        rerankers: List[Tuple[BaseReranker, float]],  # [(reranker, weight), ...]
    ):
        self.rerankers = rerankers
    
    def rerank(
        self,
        query: str,
        candidates: List[Dict],
        topk: int = 5,
    ) -> List[Dict]:
        if not candidates:
            return []
        
        # Collect scores from each reranker
        all_scores = []
        for reranker, weight in self.rerankers:
            reranked = reranker.rerank(query, candidates, topk=len(candidates))
            scores = {r["chunk_idx"]: r["rerank_score"] for r in reranked}
            all_scores.append((scores, weight))
        
        # Compute weighted scores
        scored = []
        for c in candidates:
            chunk_idx = c.get("chunk_idx", -1)
            weighted_score = 0.0
            for scores, weight in all_scores:
                if chunk_idx in scores:
                    weighted_score += weight * scores[chunk_idx]
            
            scored.append({
                **c,
                "original_score": c["score"],
                "original_rank": c["rank"],
                "rerank_score": weighted_score,
            })
        
        # Sort
        scored.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        # Update ranks
        results = []
        for new_rank, item in enumerate(scored[:topk], start=1):
            item["rank"] = new_rank
            item["score"] = item["rerank_score"]
            results.append(item)
        
        return results


class RecipocalRankFusionReranker(BaseReranker):
    """
    Reciprocal Rank Fusion (RRF) để combine nhiều retrieval/rerank results
    Paper: https://dl.acm.org/doi/10.1145/1571941.1572114
    """
    
    def __init__(self, k: int = 60):
        self.k = k  # RRF parameter
    
    def fuse_rankings(
        self,
        rankings: List[List[Dict]],
        topk: int = 10,
    ) -> List[Dict]:
        """
        Fuse nhiều rankings bằng RRF
        
        Args:
            rankings: List of ranked results, each with chunk_idx and rank
            topk: Số kết quả trả về
        
        Returns:
            Fused ranking
        """
        # Collect all chunks
        all_chunks = {}  # chunk_idx -> best candidate dict
        rrf_scores = {}  # chunk_idx -> rrf_score
        
        for ranking in rankings:
            for item in ranking:
                chunk_idx = item.get("chunk_idx", -1)
                rank = item.get("rank", 1)
                
                # RRF formula
                rrf_scores[chunk_idx] = rrf_scores.get(chunk_idx, 0) + 1.0 / (self.k + rank)
                
                # Keep best candidate dict
                if chunk_idx not in all_chunks:
                    all_chunks[chunk_idx] = item.copy()
        
        # Sort by RRF score
        sorted_chunks = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Build result
        results = []
        for new_rank, (chunk_idx, rrf_score) in enumerate(sorted_chunks[:topk], start=1):
            item = all_chunks[chunk_idx].copy()
            item["rank"] = new_rank
            item["rrf_score"] = rrf_score
            item["score"] = rrf_score
            results.append(item)
        
        return results
    
    def rerank(
        self,
        query: str,
        candidates: List[Dict],
        topk: int = 5,
    ) -> List[Dict]:
        # For single reranking, just pass through
        # This is mainly for fuse_rankings
        return candidates[:topk]


def get_reranker(
    reranker_type: str = "cross-encoder",
    model_name: str = "bge-reranker-base",
    device: str = "cuda",
    **kwargs
) -> BaseReranker:
    """Factory function để tạo reranker"""
    
    if reranker_type == "cross-encoder":
        return CrossEncoderReranker(model_name, device, **kwargs)
    elif reranker_type == "tfidf":
        return TFIDFReranker()
    elif reranker_type == "rrf":
        return RecipocalRankFusionReranker(**kwargs)
    else:
        raise ValueError(f"Unknown reranker type: {reranker_type}")


# =============================================================================
# QUICK TEST
# =============================================================================
if __name__ == "__main__":
    # Test rerankers
    candidates = [
        {"rank": 1, "score": 0.9, "text": "Điều 1. Phạm vi điều chỉnh", "chunk_idx": 0, "metadata": {}},
        {"rank": 2, "score": 0.8, "text": "Điều 2. Đối tượng áp dụng", "chunk_idx": 1, "metadata": {}},
        {"rank": 3, "score": 0.7, "text": "Điều 3. Giải thích từ ngữ", "chunk_idx": 2, "metadata": {}},
    ]
    query = "Phạm vi điều chỉnh của nghị định là gì?"
    
    # Test TF-IDF reranker
    print("Testing TF-IDF Reranker:")
    tfidf_reranker = TFIDFReranker()
    results = tfidf_reranker.rerank(query, candidates, topk=3)
    for r in results:
        print(f"  Rank {r['rank']}: {r['text'][:50]}... (score: {r['score']:.4f})")
    
    print("\nDone!")
