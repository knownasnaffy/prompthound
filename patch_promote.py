import re
from pathlib import Path

path = Path("benchmark/promote.py")
text = path.read_text()

# Update load_labels
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

# Update target run holdout f1
text = text.replace("target.get('holdout_f1', '?')", "target.get('holdout_f1_macro', '?')")
text = text.replace("rows_sorted = sorted(rows, key=lambda r: float(r.get(\"holdout_f1\", 0)), reverse=True)", "rows_sorted = sorted(rows, key=lambda r: float(r.get(\"holdout_f1_macro\", 0)), reverse=True)")


# Update y_all mapping
new_y_all = """    train_rows = [r for r in label_rows if r["label"] in ("benign", "suspicious", "malicious")]
    labeled_paths = [Path(r["filepath"]) for r in train_rows]
    labels_by_path = {Path(r["filepath"]): r["label"] for r in train_rows}

    print(f"Extracting features for {len(labeled_paths)} files (full corpus) …")
    X_all, ok_paths, failed_paths = extract_all_features(labeled_paths, root=_ROOT)

    if failed_paths:
        print(f"  Warning: {len(failed_paths)} file(s) skipped.", file=sys.stderr)

    label_map = {"benign": 0, "suspicious": 1, "malicious": 2}
    y_all = np.array(
        [label_map[labels_by_path[p]] for p in ok_paths],
        dtype=int,
    )
    n_benign = int(np.sum(y_all == 0))
    n_suspicious = int(np.sum(y_all == 1))
    n_malicious = int(np.sum(y_all == 2))
    print(f"  Training corpus: {len(y_all)} files ({n_benign} benign, {n_suspicious} suspicious, {n_malicious} malicious)")"""
text = re.sub(r'    train_rows = \[r for r in label_rows if r\["label"\] in \("benign", "malicious"\)\].*?print\(f"  Training corpus: \{len\(y_all\)\} files \(\{n_benign\} benign, \{n_malicious\} malicious\)"\)', new_y_all, text, flags=re.DOTALL)


# FPR probe
new_fpr_probe = """def evaluate_fpr_probe(estimator: Any) -> dict[str, float]:
    probe_paths = sorted(BENIGN_UNUSUAL_DIR.glob("*.md"))
    if not probe_paths:
        return {"fpr_mild": 0.0, "fpr_severe": 0.0}

    X_probe, ok_probe, _ = extract_all_features(
        [p.relative_to(_ROOT) for p in probe_paths], root=_ROOT
    )

    if len(X_probe) == 0:
        return {"fpr_mild": 0.0, "fpr_severe": 0.0}

    y_pred = estimator.predict(X_probe)
    return {
        "fpr_mild": float(np.mean(y_pred == 1)),
        "fpr_severe": float(np.mean(y_pred == 2)),
    }"""
text = re.sub(r'def evaluate_fpr_probe.*?return float\(np\.mean\(y_pred\)\)', new_fpr_probe, text, flags=re.DOTALL)

# FPR usage
text = text.replace("fpr_probe_recorded = float(target.get(\"fpr_benign_unusual\", 0))", "fpr_probe_recorded = float(target.get(\"fpr_mild\", 0))")
text = text.replace("fpr_actual = evaluate_fpr_probe(estimator)", "fpr_actual_dict = evaluate_fpr_probe(estimator)\n    fpr_actual = fpr_actual_dict['fpr_mild']")

# metadata
text = text.replace('"n_train_benign": n_benign,', '"n_train_benign": n_benign,\n            "n_train_suspicious": n_suspicious,')
text = text.replace('"cv_f1": float(target.get("cv_f1", 0)),', '"cv_f1_macro": float(target.get("cv_f1_macro", 0)),')
text = text.replace('"holdout_f1": float(target.get("holdout_f1", 0)),', '"holdout_f1_macro": float(target.get("holdout_f1_macro", 0)),')
text = text.replace('"fpr_benign_unusual_benchmark": fpr_probe_recorded,', '"fpr_mild_benchmark": fpr_probe_recorded,\n            "fpr_severe_benchmark": float(target.get("fpr_severe", 0)),')
text = text.replace('"fpr_benign_unusual_full_corpus": round(fpr_actual, 4),', '"fpr_mild_full_corpus": round(fpr_actual, 4),\n            "fpr_severe_full_corpus": round(fpr_actual_dict["fpr_severe"], 4),')

path.write_text(text)
print("promote.py patched successfully")
