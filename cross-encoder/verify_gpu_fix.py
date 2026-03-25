import torch
import sys
from pathlib import Path

# Add project paths
GEN_DIR = Path(r"d:\GitHub\Folder cha\ChatBot\cross-encoder\generation")
CE_ROOT = GEN_DIR.parent
if str(CE_ROOT) not in sys.path:
    sys.path.insert(0, str(CE_ROOT))

from generation.retrieval_rerank import RetrievalReranker

def verify_gpu():
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if not torch.cuda.is_available():
        print("ERROR: CUDA not available!")
        return

    print("Initializing RetrievalReranker with device='cuda'...")
    # Using small dummy corpus if possible or just letting it load default
    # To speed up, we just check model loading
    try:
        reranker = RetrievalReranker(device="cuda")
        
        print(f"Reranker device: {reranker.device}")
        
        # Check Bi-encoder
        bi_device = next(reranker.bi_model.parameters()).device
        bi_dtype = next(reranker.bi_model.parameters()).dtype
        print(f"Bi-encoder device: {bi_device}, dtype: {bi_dtype}")
        
        # Check Cross-encoder
        ce_device = next(reranker.ce_model.model.parameters()).device
        ce_dtype = next(reranker.ce_model.model.parameters()).dtype
        print(f"Cross-encoder device: {ce_device}, dtype: {ce_dtype}")
        
        if "cuda" in str(bi_device) and "cuda" in str(ce_device):
            print("SUCCESS: Both models are on GPU!")
        else:
            print("FAILURE: Models are NOT on GPU!")
            
        if bi_dtype == torch.float16 or ce_dtype == torch.float16:
            print("SUCCESS: FP16 is enabled!")
            
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_gpu()
