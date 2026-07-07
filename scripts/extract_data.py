import json
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompthound.flatten import flatten_bundle
from prompthound.parser import parse_buffer
from prompthound.features import extract_features
from prompthound.capability_chain import check_chains


def main():
    dataset_dir = Path(__file__).parent.parent / "dataset"
    gt_path = dataset_dir / "ground_truth.json"

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
    is_bundle_arr = []

    print(f"Extracting features for {len(gt['test_cases'])} cases...")

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
        is_bundle_arr.append(feature_dict["is_bundle"])

        count += 1
        if count % 100 == 0:
            print(f"Extracted {count} cases...")

    X = np.array(X)
    y = np.array(y)
    is_bundle_arr = np.array(is_bundle_arr)

    out_path = Path(__file__).parent.parent / "data" / "features.npz"
    np.savez(out_path, X=X, y=y, is_bundle=is_bundle_arr)
    print(f"Features saved to {out_path} with shape {X.shape}")


if __name__ == "__main__":
    main()
