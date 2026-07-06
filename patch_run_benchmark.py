import re
from pathlib import Path

path = Path("benchmark/run_benchmark.py")
text = path.read_text()

# 1. Update load_labels
new_load_labels = """def load_labels(labels_csv: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    
    for cls_name in ["benign", "suspicious", "malicious"]:
        d = CORPUS_DIR / cls_name
        if d.exists():
            for p in d.iterdir():
                if p.is_dir() or p.suffix == ".md":
                    rows.append({"filepath": str(p.relative_to(_ROOT)), "label": cls_name})
                
    return sorted(rows, key=lambda x: x["filepath"])"""
text = re.sub(r'def load_labels.*?return sorted\(rows, key=lambda x: x\["filepath"\]\)', new_load_labels, text, flags=re.DOTALL)

# 2. Update y_all mapping
new_y_all = """
    label_map = {"benign": 0, "suspicious": 1, "malicious": 2}
    y_all = np.array(
        [label_map[labels_by_path[p]] for p in ok_paths],
        dtype=int,
    )

    n_benign = int(np.sum(y_all == 0))
    n_suspicious = int(np.sum(y_all == 1))
    n_malicious = int(np.sum(y_all == 2))
    print(f"  Labeled corpus: {len(y_all)} files ({n_benign} safe, {n_suspicious} suspicious, {n_malicious} malicious)")

    if len(y_all) < 2 or n_benign == 0 or n_suspicious == 0 or n_malicious == 0:
        print("ERROR: Need at least one sample from each of the 3 classes.", file=sys.stderr)
        sys.exit(1)"""
text = re.sub(r'    y_all = np.array\(.*?sys\.exit\(1\)', new_y_all, text, flags=re.DOTALL)

# 3. Update cv_score and holdout_score to use f1_macro and remove binary-only metrics
text = text.replace("f1_score(y_val, y_pred, zero_division=0)", "f1_score(y_val, y_pred, average='macro', zero_division=0)")
text = text.replace("f1_score(y_test, y_pred, zero_division=0)", "f1_score(y_test, y_pred, average='macro', zero_division=0)")
text = text.replace("f1_score(y_test[bundle_mask], y_pred[bundle_mask], zero_division=0)", "f1_score(y_test[bundle_mask], y_pred[bundle_mask], average='macro', zero_division=0)")
text = text.replace("f1_score(y_test[~bundle_mask], y_pred[~bundle_mask], zero_division=0)", "f1_score(y_test[~bundle_mask], y_pred[~bundle_mask], average='macro', zero_division=0)")

text = text.replace("cv_f1", "cv_f1_macro")
text = text.replace("holdout_f1", "holdout_f1_macro")

# Decomposed FPR
new_fpr_probe = """def fpr_probe(estimator: Any, X_probe: np.ndarray) -> dict[str, float]:
    if len(X_probe) == 0:
        return {"fpr_mild": 0.0, "fpr_severe": 0.0}
    y_pred = estimator.predict(X_probe)
    # y_pred: 0=safe, 1=suspicious, 2=malicious
    return {
        "fpr_mild": float(np.mean(y_pred == 1)),
        "fpr_severe": float(np.mean(y_pred == 2)),
    }"""
text = re.sub(r'def fpr_probe.*?return float\(np\.mean\(y_pred\)\).*?# y_pred is 0/1; mean = fraction of 1s', new_fpr_probe, text, flags=re.DOTALL)

text = text.replace("fpr = fpr_probe(result.estimator, X_probe)", "fpr = fpr_probe(result.estimator, X_probe)\n        fpr_mild = fpr['fpr_mild']\n        fpr_severe = fpr['fpr_severe']")
text = text.replace("\"fpr_benign_unusual\": fpr,", "\"fpr_mild\": fpr_mild, \"fpr_severe\": fpr_severe,")

# 4. update columns
text = text.replace("f\"| {r.get('cv_f1', 0):.3f} \"", "f\"| {r.get('cv_f1_macro', 0):.3f} \"")
text = text.replace("f\"| {r.get('holdout_f1', 0):.3f} \"", "f\"| {r.get('holdout_f1_macro', 0):.3f} \"")
text = text.replace("f\"| {r.get('fpr_benign_unusual', 0):.2f} \"", "f\"| {r.get('fpr_mild', 0):.2f} | {r.get('fpr_severe', 0):.2f} \"")
text = text.replace("| holdout_f1 |", "| holdout_f1_macro |")
text = text.replace("| cv_f1 |", "| cv_f1_macro |")
text = text.replace("| fpr_benign_unusual |", "| fpr_mild | fpr_severe |")
text = text.replace("|---|", "|---|---|")

# 5. Metadata logging for class counts
text = text.replace('"n_benign": n_benign,', '"n_benign": n_benign,\n        "n_suspicious": n_suspicious,')

path.write_text(text)
print("run_benchmark.py patched successfully")
