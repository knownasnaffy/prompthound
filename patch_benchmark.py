import re
from pathlib import Path

path = Path('benchmark/run_benchmark.py')
text = path.read_text()

# 1. load_labels
old_load_labels = '''def load_labels(labels_csv: Path) -> list[dict[str, str]]:
    """Return list of dicts with keys filepath/label/source/notes.

    Skips comment lines (starting with #) and blank lines.
    """
    rows: list[dict[str, str]] = []
    with labels_csv.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(
            (line for line in fh if not line.startswith("#") and line.strip()),
        )
        for row in reader:
            rows.append(dict(row))
    return rows'''

new_load_labels = '''def load_labels(labels_csv: Path) -> list[dict[str, str]]:
    """Return list of dicts with keys filepath and label.
    
    Dynamically scans the CORPUS_DIR instead of requiring labels_csv.
    """
    rows: list[dict[str, str]] = []
    
    benign_dir = CORPUS_DIR / "benign"
    if benign_dir.exists():
        for p in benign_dir.iterdir():
            if p.is_dir() or p.suffix == ".md":
                rows.append({"filepath": str(p.relative_to(_ROOT)), "label": "benign"})
                
    malicious_dir = CORPUS_DIR / "malicious"
    if malicious_dir.exists():
        for p in malicious_dir.iterdir():
            if p.is_dir() or p.suffix == ".md":
                rows.append({"filepath": str(p.relative_to(_ROOT)), "label": "malicious"})
                
    return sorted(rows, key=lambda x: x["filepath"])'''

text = text.replace(old_load_labels, new_load_labels)

# 2. extract_all_features
old_extract = '''    for fp in filepaths:
        abs_fp = root / fp if not fp.is_absolute() else fp
        try:
            parsed = parse_skill(str(abs_fp))
            if not parsed.parse_ok:'''
new_extract = '''    for fp in filepaths:
        abs_fp = root / fp if not fp.is_absolute() else fp
        try:
            if abs_fp.is_dir():
                from prompthound.flatten import parse_directory
                parsed = parse_directory(str(abs_fp))
            else:
                parsed = parse_skill(str(abs_fp))
            
            if not parsed.parse_ok:'''
text = text.replace(old_extract, new_extract)

# 3. holdout_score
old_holdout = '''    if hasattr(estimator, "predict_proba") and len(set(y_test)) > 1:
        proba = estimator.predict_proba(X_test)
        scores = proba[:, 1] if proba.shape[1] >= 2 else proba.ravel()
        metrics["holdout_roc_auc"] = float(roc_auc_score(y_test, scores))

    return metrics'''
new_holdout = '''    if hasattr(estimator, "predict_proba") and len(set(y_test)) > 1:
        proba = estimator.predict_proba(X_test)
        scores = proba[:, 1] if proba.shape[1] >= 2 else proba.ravel()
        metrics["holdout_roc_auc"] = float(roc_auc_score(y_test, scores))

    try:
        is_bundle_idx = FEATURE_ORDER.index("is_bundle")
        bundle_mask = X_test[:, is_bundle_idx] == 1.0
        
        # bundle slice
        if np.any(bundle_mask):
            metrics["holdout_f1_bundle"] = float(f1_score(y_test[bundle_mask], y_pred[bundle_mask], zero_division=0))
        else:
            metrics["holdout_f1_bundle"] = float('nan')
            
        # single file slice
        if np.any(~bundle_mask):
            metrics["holdout_f1_single"] = float(f1_score(y_test[~bundle_mask], y_pred[~bundle_mask], zero_division=0))
        else:
            metrics["holdout_f1_single"] = float('nan')
    except ValueError:
        pass

    return metrics'''
text = text.replace(old_holdout, new_holdout)

# 4. CSV_COLUMNS
old_csv = '''    "holdout_f1", "holdout_precision", "holdout_recall", "holdout_roc_auc",
    "fpr_benign_unusual",'''
new_csv = '''    "holdout_f1", "holdout_precision", "holdout_recall", "holdout_roc_auc",
    "holdout_f1_bundle", "holdout_f1_single",
    "fpr_benign_unusual",'''
text = text.replace(old_csv, new_csv)

# 5. write_markdown header
old_md_header = '''    # Table header
    header = (
        "| Rank | Model | Hyperparams | CV F1 | Holdout F1 | Holdout P | "
        "Holdout R | ROC-AUC | FPR(probe) | MeanDepth | Nodes | N_est | "
        "FitTime(s) | TieBand |"
    )
    sep = "|" + "|".join(["---"] * 14) + "|"'''
new_md_header = '''    # Table header
    header = (
        "| Rank | Model | Hyperparams | CV F1 | Holdout F1 | F1(bundle) | F1(single) | Holdout P | "
        "Holdout R | ROC-AUC | FPR(probe) | MeanDepth | Nodes | N_est | "
        "FitTime(s) | TieBand |"
    )
    sep = "|" + "|".join(["---"] * 16) + "|"'''
text = text.replace(old_md_header, new_md_header)

# 6. write_markdown row
old_md_row = '''    for r in rows:
        tie = "✓" if r.get("in_tie_band") else ""
        params = str(r.get("hyperparams", ""))
        if len(params) > 50:
            params = params[:47] + "..."
        lines.append(
            f"| {r.get('rank', '')} "
            f"| {r.get('model_name', '')} "
            f"| {params} "
            f"| {r.get('cv_f1', 0):.3f} "
            f"| {r.get('holdout_f1', 0):.3f} "
            f"| {r.get('holdout_precision', 0):.3f} "
            f"| {r.get('holdout_recall', 0):.3f} "
            f"| {r.get('holdout_roc_auc', 0):.3f} "
            f"| {r.get('fpr_benign_unusual', 0):.3f} "
            f"| {r.get('mean_depth', 0):.1f} "
            f"| {r.get('total_nodes', 0)} "
            f"| {r.get('n_estimators', 0)} "
            f"| {r.get('fit_time_s', 0):.3f} "
            f"| {tie} |"
        )'''
new_md_row = '''    for r in rows:
        tie = "✓" if r.get("in_tie_band") else ""
        params = str(r.get("hyperparams", ""))
        if len(params) > 50:
            params = params[:47] + "..."
            
        f1_bundle = r.get('holdout_f1_bundle', float('nan'))
        f1_single = r.get('holdout_f1_single', float('nan'))
        
        lines.append(
            f"| {r.get('rank', '')} "
            f"| {r.get('model_name', '')} "
            f"| `{params}` "
            f"| {r.get('cv_f1', 0):.3f} "
            f"| {r.get('holdout_f1', 0):.3f} "
            f"| {f1_bundle:.3f} "
            f"| {f1_single:.3f} "
            f"| {r.get('holdout_precision', 0):.3f} "
            f"| {r.get('holdout_recall', 0):.3f} "
            f"| {r.get('holdout_roc_auc', 0):.3f} "
            f"| {r.get('fpr_benign_unusual', 0):.3f} "
            f"| {r.get('mean_depth', 0):.1f} "
            f"| {r.get('total_nodes', 0)} "
            f"| {r.get('n_estimators', 0)} "
            f"| {r.get('fit_time_s', 0):.3f} "
            f"| {tie} |"
        )'''
text = text.replace(old_md_row, new_md_row)

path.write_text(text)
print("Done patching.")
