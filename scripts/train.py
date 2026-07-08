import json
import joblib
import numpy as np
import argparse
import importlib
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompthound.flatten import flatten_bundle
from prompthound.parser import parse_buffer
from prompthound.features import extract_features
from prompthound.capability_chain import check_chains


def load_class(class_path):
    module_name, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def main():
    parser = argparse.ArgumentParser(description="PromptHound Model Training (Promote)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--top", action="store_true", help="Train top model from comparison.json")
    group.add_argument("--id", type=str, help="Train specific model from comparison.json")
    args = parser.parse_args()

    base_dir = Path(__file__).parent.parent
    dataset_dir = base_dir / "dataset"
    gt_path = dataset_dir / "ground_truth.json"
    comparison_path = base_dir / "data" / "benchmarks" / "comparison.json"

    if not comparison_path.exists():
        print(f"Error: {comparison_path} not found. Run benchmark.py first.")
        sys.exit(1)

    with open(comparison_path, "r") as f:
        comp_data = json.load(f)

    if args.top:
        best_model = None
        best_f1 = -1
        for model_name, info in comp_data.items():
            if info["f1_macro"] > best_f1:
                best_f1 = info["f1_macro"]
                best_model = model_name
        
        if not best_model:
            print("Error: No models found in comparison.json")
            sys.exit(1)
        
        target_model = best_model
        print(f"Selected top model: {target_model} (F1-Macro: {best_f1:.4f})")
    else:
        target_model = args.id
        if target_model not in comp_data:
            print(f"Error: Model {target_model} not found in comparison.json")
            sys.exit(1)
        print(f"Selected model: {target_model}")

    target_info = comp_data[target_model]
    target_class = target_info["class"]
    target_params = target_info["params"]

    print(f"Class: {target_class}")
    print(f"Params: {target_params}")

    with open(gt_path, "r") as f:
        gt = json.load(f)

    feature_names = [
        "b64_ratio",
        "padding_ratio",
        "code_to_prose_ratio",
        "url_count",
        "unicode_count",
        "shell_command_presence",
        "urgency_density",
        "entropy",
        "is_bundle",
        "member_count",
        "capability_mismatch_score",
        "high_severity_hits",
        "medium_severity_hits",
        "eval_exec_density",
        "secret_keyword_density",
    ]

    X = []
    y = []

    print(f"Loading {len(gt['test_cases'])} cases...")

    count = 0
    for case in gt["test_cases"]:
        case_id = case["id"]
        case_dir = dataset_dir / case_id

        if not case_dir.exists():
            continue

        judgment = case["judgment"]
        if judgment == "normal":
            judgment = "safe"

        buffer_text, manifest = flatten_bundle(case_dir)
        frontmatter, _, lines = parse_buffer(buffer_text)
        _, mismatch_score = check_chains(lines, frontmatter)

        is_bundle = manifest.member_count > 1
        feature_dict = extract_features(lines, manifest, is_bundle=is_bundle)
        feature_dict["capability_mismatch_score"] = mismatch_score

        vec = [float(feature_dict[name]) for name in feature_names]

        X.append(vec)
        y.append(judgment)

        count += 1
        if count % 100 == 0:
            print(f"Processed {count} cases...")

    print(f"Training {target_model} on {len(X)} samples...")
    X = np.array(X)
    y = np.array(y)

    cls = load_class(target_class)
    clf = cls(**target_params)
    clf.fit(X, y)

    model_path = Path(__file__).parent.parent / "src" / "prompthound" / "model.joblib"
    joblib.dump(clf, model_path)
    print(f"Model saved to {model_path}")
    print(f"Classes: {clf.classes_}")


if __name__ == "__main__":
    main()
