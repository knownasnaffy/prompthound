import json
import sys
from pathlib import Path

def main():
    base_dir = Path(__file__).parent.parent
    comparison_path = base_dir / "data" / "benchmarks" / "comparison.json"
    
    if not comparison_path.exists():
        print(f"Error: {comparison_path} not found.")
        sys.exit(1)

    with open(comparison_path, "r") as f:
        data = json.load(f)

    if not data:
        print("No models found in comparison.json.")
        sys.exit(1)

    best_f1_macro = max(m["f1_macro"] for m in data.values())
    min_fpr_severe = min(m["fpr_severe"] for m in data.values())
    min_fpr_mild = min(m["fpr_mild"] for m in data.values())

    print("=== Model Comparison Report ===\n")

    for name, m in data.items():
        print(f"Model: {name}")
        pros = []
        cons = []

        # Overall Accuracy
        if m["f1_macro"] >= best_f1_macro * 0.99:
            pros.append("Top-tier overall accuracy (F1 Macro).")
        elif m["f1_macro"] < best_f1_macro * 0.90:
            cons.append("Low overall accuracy compared to peers.")

        # FPR Severe
        if m["fpr_severe"] <= min_fpr_severe * 1.1 or m["fpr_severe"] < 0.02:
            pros.append("Excellent (very low) severe false positive rate.")
        elif m["fpr_severe"] > 0.05:
            cons.append(f"High severe false positive rate ({m['fpr_severe']:.2%}).")

        # FPR Mild
        if m["fpr_mild"] <= min_fpr_mild * 1.1 or m["fpr_mild"] < 0.03:
            pros.append("Excellent (very low) mild false positive rate.")
        elif m["fpr_mild"] > 0.10:
            cons.append(f"High mild false positive rate ({m['fpr_mild']:.2%}).")

        # Single vs Bundle
        if m.get("f1_single", 0) == 1.0:
            pros.append("Perfect F1 on single files.")
        elif m.get("f1_single", 0) < 0.9:
            cons.append("Weaker performance on single files.")

        if m.get("f1_bundle", 0) > 0.77:
            pros.append("Strong performance on bundled files.")
        elif m.get("f1_bundle", 0) < 0.70:
            cons.append("Weaker performance on bundled files.")

        if not pros:
            pros.append("Average performance across metrics.")
        if not cons:
            cons.append("No major weaknesses detected.")

        print("  Benefits:")
        for p in sorted(set(pros)):
            print(f"    + {p}")
        print("  Demerits:")
        for c in sorted(set(cons)):
            print(f"    - {c}")
        
        print(f"  Summary: F1={m['f1_macro']:.3f} | FPR_Severe={m['fpr_severe']:.3f} | FPR_Mild={m['fpr_mild']:.3f}\n")

if __name__ == "__main__":
    main()
