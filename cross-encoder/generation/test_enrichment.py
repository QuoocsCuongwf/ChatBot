
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(r"d:\GitHub\Folder cha\ChatBot\cross-encoder\generation")
sys.path.append(str(project_root))

from rag_contract import RAGOutput, Citation, ChunkInfo
from run_generation import GenerationPipeline

def test_enrichment():
    # Setup mock data
    pipeline = GenerationPipeline(local_client=None, api_client=None) # Mock init
    
    # 1. Output with missing van_ban
    output = RAGOutput(
        answer="Theo Điều 5 Khoản 2...",
        citations=[
            Citation(dieu="5", khoan="2", van_ban="")
        ]
    )
    
    # 2. Retrieved chunks with metadata
    chunks = [
        ChunkInfo(
            chunk_id=1, 
            text="...", 
            score_retrieval=0.9, 
            score_rerank=0.9,
            van_ban="Nghị định 123/2024/NĐ-CP",
            dieu="5",
            khoan="2"
        ),
        ChunkInfo(
            chunk_id=2, 
            text="...", 
            score_retrieval=0.8, 
            score_rerank=0.8,
            van_ban="Thông tư 45/2023/TT-BTC",
            dieu="10",
            khoan="1"
        )
    ]
    
    print("Testing citation enrichment...")
    pipeline._enrich_citations(output, chunks)
    
    enriched_cit = output.citations[0]
    print(f"Enriched Citation: {enriched_cit.to_str()} - {enriched_cit.van_ban}")
    
    assert enriched_cit.van_ban == "Nghị định 123/2024/NĐ-CP"
    print("Test passed!")

if __name__ == "__main__":
    test_enrichment()
