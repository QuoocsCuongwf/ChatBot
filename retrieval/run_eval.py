"""
Script chạy nhanh để đánh giá retrieval
=======================================

Chạy:
  python run_eval.py                         # Đánh giá tất cả models
  python run_eval.py --quick                 # Chỉ đánh giá 50 queries đầu
  python run_eval.py --models legalhf tfidf  # Chỉ đánh giá 2 models
  python run_eval.py --no-rerank             # Không dùng reranking
"""

import os
import sys
import subprocess
from datetime import datetime

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Default configs
CONFIGS = {
    "default": {
        "gold": os.path.join(SCRIPT_DIR, "gold_200_diverse.jsonl"),
        "chunks": os.path.join(PROJECT_ROOT, "output_nghidinh", "chunks_clean_norm.json"),
        "vec_root": os.path.join(PROJECT_ROOT, "vector_data"),
        "models": ["tfidf", "legalhf", "phobert", "dek21"],
        "topk": 10,
        "match_mode": "dieu_khoan",
        "use_rerank": True,
        "rerank_model": "BAAI/bge-reranker-v2-m3",  # Multilingual, tốt cho tiếng Việt
    },
    "quick": {
        "gold": os.path.join(SCRIPT_DIR, "goldset.jsonl"),  # Smaller dataset
        "chunks": os.path.join(PROJECT_ROOT, "output_nghidinh", "chunks_clean_norm.json"),
        "vec_root": os.path.join(PROJECT_ROOT, "vector_data"),
        "models": ["tfidf", "legalhf"],
        "topk": 10,
        "match_mode": "dieu_khoan",
        "use_rerank": False,
    },
    "full": {
        "gold": os.path.join(SCRIPT_DIR, "gold_200_diverse.jsonl"),
        "chunks": os.path.join(PROJECT_ROOT, "output_nghidinh", "chunks_clean_norm.json"),
        "vec_root": os.path.join(PROJECT_ROOT, "vector_data"),
        "models": ["tfidf", "legalhf", "phobert", "dek21"],
        "topk": 20,
        "match_mode": "dieu_khoan",
        "use_rerank": True,
        "rerank_model": "BAAI/bge-reranker-large",
    },
}


def print_banner():
    print("=" * 70)
    print("RETRIEVAL EVALUATION PIPELINE")
    print("=" * 70)


def run_evaluation(config_name: str = "default", **overrides):
    """Run evaluation với config"""
    
    print_banner()
    
    # Get base config
    if config_name not in CONFIGS:
        print(f"❌ Unknown config: {config_name}")
        print(f"   Available: {list(CONFIGS.keys())}")
        return 1
    
    config = CONFIGS[config_name].copy()
    config.update(overrides)
    
    # Validate paths
    if not os.path.isfile(config["gold"]):
        print(f"❌ Gold file not found: {config['gold']}")
        return 1
    
    if not os.path.isfile(config["chunks"]):
        print(f"❌ Chunks file not found: {config['chunks']}")
        return 1
    
    # Print config
    print(f"\nConfig: {config_name}")
    print(f"  Gold: {config['gold']}")
    print(f"  Models: {config['models']}")
    print(f"  Top-K: {config['topk']}")
    print(f"  Use Rerank: {config.get('use_rerank', False)}")
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"eval_results_{timestamp}.xlsx"
    
    # Build command
    eval_script = os.path.join(SCRIPT_DIR, "eval_all_models.py")
    
    cmd = [
        sys.executable,
        eval_script,
        "--gold", config["gold"],
        "--chunks", config["chunks"],
        "--vec_root", config["vec_root"],
        "--models", *config["models"],
        "--topk", str(config["topk"]),
        "--match_mode", config["match_mode"],
        "--output", output_file,
    ]
    
    if not config.get("use_rerank", False):
        cmd.append("--no-rerank")
    elif "rerank_model" in config:
        cmd.extend(["--rerank_model", config["rerank_model"]])
    
    # Run
    print(f"\n{'='*70}")
    print("Running evaluation...")
    print(f"{'='*70}")
    
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    
    if result.returncode == 0:
        print(f"\n✅ Evaluation complete!")
        print(f"   Results: {output_file}")
    else:
        print(f"\n❌ Evaluation failed with code {result.returncode}")
    
    return result.returncode


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick evaluation runner")
    parser.add_argument("--config", default="default", choices=list(CONFIGS.keys()),
                        help="Preset config to use")
    parser.add_argument("--quick", action="store_true", help="Use quick config")
    parser.add_argument("--full", action="store_true", help="Use full config")
    parser.add_argument("--models", nargs="+", help="Override models to evaluate")
    parser.add_argument("--no-rerank", action="store_true", help="Disable reranking")
    parser.add_argument("--gold", help="Override gold file path")
    
    args = parser.parse_args()
    
    # Determine config
    if args.quick:
        config_name = "quick"
    elif args.full:
        config_name = "full"
    else:
        config_name = args.config
    
    # Collect overrides
    overrides = {}
    if args.models:
        overrides["models"] = args.models
    if args.no_rerank:
        overrides["use_rerank"] = False
    if args.gold:
        overrides["gold"] = args.gold
    
    return run_evaluation(config_name, **overrides)


if __name__ == "__main__":
    sys.exit(main())
