"""
So sánh và phân tích kết quả Retrieval
======================================

Công dụng:
  - So sánh kết quả từ nhiều experiments
  - Tạo biểu đồ so sánh
  - Phân tích error cases
  - Xuất báo cáo chi tiết

Usage:
  python compare_results.py eval_results_1.xlsx eval_results_2.xlsx
  python compare_results.py --analyze eval_results.xlsx
"""

import os
import json
import argparse
from typing import List, Dict, Any, Optional
from collections import defaultdict

# Excel & Data
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# Visualization
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def load_excel_results(filepath: str) -> pd.DataFrame:
    """Load results từ Excel file"""
    if not HAS_PANDAS:
        raise ImportError("Cần cài pandas: pip install pandas openpyxl")
    return pd.read_excel(filepath, sheet_name="Retrieval Results")


def load_json_results(filepath: str) -> Dict:
    """Load results từ JSON file"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_results(files: List[str]) -> pd.DataFrame:
    """So sánh kết quả từ nhiều files"""
    all_data = []
    
    for filepath in files:
        filename = os.path.basename(filepath)
        
        if filepath.endswith(".xlsx"):
            df = load_excel_results(filepath)
            df["Source"] = filename
            all_data.append(df)
        elif filepath.endswith(".json"):
            data = load_json_results(filepath)
            # Convert to DataFrame
            rows = []
            for item in data.get("base_results", []):
                item["Source"] = filename
                item["Reranked"] = "No"
                rows.append(item)
            for item in data.get("reranked_results", []):
                item["Source"] = filename
                item["Reranked"] = "Yes"
                rows.append(item)
            if rows:
                all_data.append(pd.DataFrame(rows))
    
    if not all_data:
        raise ValueError("Không tìm thấy data hợp lệ")
    
    return pd.concat(all_data, ignore_index=True)


def create_comparison_chart(
    df: pd.DataFrame,
    output_path: str = "comparison_chart.png",
    metrics: List[str] = None,
):
    """Tạo biểu đồ so sánh"""
    if not HAS_MATPLOTLIB:
        print("⚠️ Cần cài matplotlib: pip install matplotlib")
        return
    
    if metrics is None:
        # Tìm các cột Recall@K và MRR
        metrics = [c for c in df.columns if c.startswith("Recall@") or c == "MRR"]
    
    if not metrics:
        print("⚠️ Không tìm thấy metrics để vẽ")
        return
    
    # Lọc chỉ lấy base results (không rerank) để so sánh công bằng
    df_base = df[df["Reranked"] == "No"].copy()
    
    if df_base.empty:
        df_base = df.copy()
    
    # Plot
    fig, axes = plt.subplots(1, len(metrics), figsize=(5*len(metrics), 5))
    
    if len(metrics) == 1:
        axes = [axes]
    
    colors = plt.cm.Set2(range(len(df_base["Model"].unique())))
    
    for ax, metric in zip(axes, metrics):
        models = df_base["Model"].unique()
        values = [df_base[df_base["Model"] == m][metric].values[0] for m in models]
        
        bars = ax.bar(models, values, color=colors[:len(models)])
        ax.set_xlabel("Model")
        ax.set_ylabel(metric)
        ax.set_title(metric)
        ax.set_ylim(0, 1)
        
        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                   f"{val:.3f}", ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Đã lưu biểu đồ: {output_path}")
    plt.close()


def create_rerank_comparison_chart(
    df: pd.DataFrame,
    output_path: str = "rerank_comparison.png",
):
    """So sánh trước và sau khi rerank"""
    if not HAS_MATPLOTLIB:
        print("⚠️ Cần cài matplotlib: pip install matplotlib")
        return
    
    models = df["Model"].unique()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = range(len(models))
    width = 0.35
    
    # Get MRR values
    mrr_base = []
    mrr_rerank = []
    
    for model in models:
        base_val = df[(df["Model"] == model) & (df["Reranked"] == "No")]["MRR"]
        rerank_val = df[(df["Model"] == model) & (df["Reranked"] == "Yes")]["MRR"]
        
        mrr_base.append(base_val.values[0] if len(base_val) > 0 else 0)
        mrr_rerank.append(rerank_val.values[0] if len(rerank_val) > 0 else 0)
    
    bars1 = ax.bar([i - width/2 for i in x], mrr_base, width, label='Base', color='steelblue')
    bars2 = ax.bar([i + width/2 for i in x], mrr_rerank, width, label='+ Rerank', color='darkorange')
    
    ax.set_xlabel('Model')
    ax.set_ylabel('MRR')
    ax.set_title('Base vs Reranked Performance')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()
    ax.set_ylim(0, 1)
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.02,
               f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.02,
               f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Đã lưu biểu đồ: {output_path}")
    plt.close()


def analyze_results(df: pd.DataFrame):
    """Phân tích kết quả chi tiết"""
    print("\n" + "="*70)
    print("ANALYSIS SUMMARY")
    print("="*70)
    
    # Best model by MRR
    df_base = df[df["Reranked"] == "No"]
    if not df_base.empty:
        best_model = df_base.loc[df_base["MRR"].idxmax()]
        print(f"\n🏆 Best Base Model (by MRR): {best_model['Model']}")
        print(f"   MRR: {best_model['MRR']:.4f}")
        
        # Find Recall columns
        recall_cols = [c for c in df_base.columns if c.startswith("Recall@")]
        for col in recall_cols:
            print(f"   {col}: {best_model[col]:.4f}")
    
    # Rerank improvement
    df_rerank = df[df["Reranked"] == "Yes"]
    if not df_rerank.empty and not df_base.empty:
        print("\n📈 Reranking Improvement:")
        for model in df["Model"].unique():
            base_mrr = df_base[df_base["Model"] == model]["MRR"].values
            rerank_mrr = df_rerank[df_rerank["Model"] == model]["MRR"].values
            
            if len(base_mrr) > 0 and len(rerank_mrr) > 0:
                improvement = rerank_mrr[0] - base_mrr[0]
                pct = (improvement / base_mrr[0] * 100) if base_mrr[0] > 0 else 0
                print(f"   {model}: {improvement:+.4f} ({pct:+.1f}%)")
    
    # Model ranking
    print("\n📊 Model Ranking (by MRR):")
    sorted_df = df_base.sort_values("MRR", ascending=False)
    for i, (_, row) in enumerate(sorted_df.iterrows(), 1):
        print(f"   {i}. {row['Model']}: {row['MRR']:.4f}")
    
    print("="*70)


def export_summary(df: pd.DataFrame, output_path: str):
    """Xuất summary ra file"""
    summary = {
        "models": df["Model"].unique().tolist(),
        "best_model_base": None,
        "best_model_reranked": None,
        "improvements": {},
    }
    
    df_base = df[df["Reranked"] == "No"]
    df_rerank = df[df["Reranked"] == "Yes"]
    
    if not df_base.empty:
        best = df_base.loc[df_base["MRR"].idxmax()]
        summary["best_model_base"] = {
            "model": best["Model"],
            "mrr": float(best["MRR"]),
        }
    
    if not df_rerank.empty:
        best = df_rerank.loc[df_rerank["MRR"].idxmax()]
        summary["best_model_reranked"] = {
            "model": best["Model"],
            "mrr": float(best["MRR"]),
        }
    
    # Calculate improvements
    for model in df["Model"].unique():
        base_mrr = df_base[df_base["Model"] == model]["MRR"].values
        rerank_mrr = df_rerank[df_rerank["Model"] == model]["MRR"].values
        
        if len(base_mrr) > 0 and len(rerank_mrr) > 0:
            summary["improvements"][model] = {
                "base_mrr": float(base_mrr[0]),
                "rerank_mrr": float(rerank_mrr[0]),
                "improvement": float(rerank_mrr[0] - base_mrr[0]),
            }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Đã xuất summary: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="So sánh và phân tích kết quả retrieval")
    parser.add_argument("files", nargs="*", help="Files Excel/JSON kết quả để so sánh")
    parser.add_argument("--analyze", action="store_true", help="Phân tích chi tiết")
    parser.add_argument("--chart", action="store_true", help="Tạo biểu đồ so sánh")
    parser.add_argument("--output", default="comparison", help="Prefix cho output files")
    
    args = parser.parse_args()
    
    if not args.files:
        # Tìm file gần nhất
        import glob
        files = glob.glob("eval_results_*.xlsx") + glob.glob("eval_results_*.json")
        if files:
            args.files = [max(files, key=os.path.getctime)]
            print(f"Using latest file: {args.files[0]}")
        else:
            print("❌ Cần ít nhất 1 file kết quả")
            parser.print_help()
            return 1
    
    if not HAS_PANDAS:
        print("❌ Cần cài pandas: pip install pandas openpyxl")
        return 1
    
    # Load và merge data
    try:
        df = compare_results(args.files)
    except Exception as e:
        print(f"❌ Lỗi load data: {e}")
        return 1
    
    # Print table
    print("\n📋 Results Summary:")
    print(df.to_string(index=False))
    
    # Analyze
    if args.analyze or len(args.files) == 1:
        analyze_results(df)
    
    # Charts
    if args.chart or len(args.files) > 1:
        create_comparison_chart(df, f"{args.output}_metrics.png")
        
        if "Yes" in df["Reranked"].values and "No" in df["Reranked"].values:
            create_rerank_comparison_chart(df, f"{args.output}_rerank.png")
    
    # Export summary
    export_summary(df, f"{args.output}_summary.json")
    
    return 0


if __name__ == "__main__":
    exit(main())
