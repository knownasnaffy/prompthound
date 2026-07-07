import numpy as np
import yaml
import importlib
import warnings
from pathlib import Path
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import (
    f1_score,
)
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore")


def load_class(class_path):
    module_name, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def compute_fpr(
    y_true,
    y_pred,
    safe_label="safe",
    suspicious_label="suspicious",
    malicious_label="malicious",
):
    # FPR Severe: Safe files predicted as Malicious
    # FPR Mild: Safe files predicted as Suspicious

    safe_mask = y_true == safe_label
    total_safe = np.sum(safe_mask)

    if total_safe == 0:
        return 0.0, 0.0

    predicted_as_malicious = np.sum((y_pred == malicious_label) & safe_mask)
    predicted_as_suspicious = np.sum((y_pred == suspicious_label) & safe_mask)

    fpr_severe = predicted_as_malicious / total_safe
    fpr_mild = predicted_as_suspicious / total_safe

    return fpr_severe, fpr_mild


def main():
    base_dir = Path(__file__).parent
    features_path = base_dir.parent / "data" / "features.npz"
    models_yaml_path = base_dir.parent / "data" / "models.yaml"

    if not features_path.exists():
        print("features.npz not found. Run extract_data.py first.")
        return

    data = np.load(features_path)
    X = data["X"]
    y_raw = data["y"]
    is_bundle_arr = data["is_bundle"]

    le = LabelEncoder()
    y = le.fit_transform(y_raw)

    # 80/20 train/test split, stratified by y
    # We also need to split is_bundle_arr
    X_train, X_test, y_train, y_test, _, is_bundle_test = train_test_split(
        X, y, is_bundle_arr, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Train size: {len(y_train)}, Test size: {len(y_test)}")

    with open(models_yaml_path, "r") as f:
        config = yaml.safe_load(f)

    results = []

    for model_name, model_info in config["models"].items():
        print(f"\n--- Benchmarking {model_name} ---")

        cls = load_class(model_info["class"])
        param_grid = model_info.get("params", {})

        # GridSearchCV
        clf = GridSearchCV(
            estimator=cls(), param_grid=param_grid, cv=3, scoring="f1_macro", n_jobs=-1
        )

        print("Training with GridSearchCV...")
        clf.fit(X_train, y_train)
        print(f"Best parameters: {clf.best_params_}")

        best_model = clf.best_estimator_
        y_pred = best_model.predict(X_test)

        f1_mac = f1_score(y_test, y_pred, average="macro")

        bundle_mask = is_bundle_test == 1
        single_mask = is_bundle_test == 0

        f1_mac_bundle = (
            f1_score(y_test[bundle_mask], y_pred[bundle_mask], average="macro")
            if np.sum(bundle_mask) > 0
            else 0
        )
        f1_mac_single = (
            f1_score(y_test[single_mask], y_pred[single_mask], average="macro")
            if np.sum(single_mask) > 0
            else 0
        )

        y_test_str = le.inverse_transform(y_test)
        y_pred_str = le.inverse_transform(y_pred)
        fpr_severe, fpr_mild = compute_fpr(y_test_str, y_pred_str)

        results.append(
            {
                "Model": model_name,
                "Macro-F1 (All)": f1_mac,
                "Macro-F1 (Bundle)": f1_mac_bundle,
                "Macro-F1 (Single)": f1_mac_single,
                "FPR-Severe": fpr_severe,
                "FPR-Mild": fpr_mild,
            }
        )

        print(f"Macro-F1 (All): {f1_mac:.4f}")
        print(f"Macro-F1 (Bundle): {f1_mac_bundle:.4f}")
        print(f"Macro-F1 (Single): {f1_mac_single:.4f}")
        print(f"FPR-Severe: {fpr_severe:.4f}")
        print(f"FPR-Mild: {fpr_mild:.4f}")

    # Generate Markdown Report
    report = ["# PromptHound Benchmark Results", ""]
    report.append(
        "| Model | Macro-F1 (All) | Macro-F1 (Bundle) | Macro-F1 (Single) | FPR-Severe | FPR-Mild |"
    )
    report.append("|---|---|---|---|---|---|")

    # Sort by F1-Macro descending
    results.sort(key=lambda x: x["Macro-F1 (All)"], reverse=True)

    for r in results:
        row = f"| {r['Model']} | {r['Macro-F1 (All)']:.4f} | {r['Macro-F1 (Bundle)']:.4f} | {r['Macro-F1 (Single)']:.4f} | {r['FPR-Severe']:.4f} | {r['FPR-Mild']:.4f} |"
        report.append(row)

    report_path = base_dir.parent / "benchmark_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report))

    print(f"\nBenchmark completed. Report saved to {report_path}")


if __name__ == "__main__":
    main()
