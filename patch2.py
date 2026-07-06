import re
from pathlib import Path

path = Path("benchmark/run_benchmark.py")
text = path.read_text()

# fix CSV columns
text = text.replace('"fpr_benign_unusual",', '"fpr_mild", "fpr_severe",')

# fix print FPR(probe)={top['fpr_benign_unusual']:.2f}
text = text.replace("top['fpr_benign_unusual']", "top['fpr_mild']")

# fix metric_col_map
text = text.replace('"f1": "holdout_f1_macro",', '"f1_macro": "holdout_f1_macro",\n        "f1": "holdout_f1_macro",')

# holdout_score for precision and recall: they need average='macro' too because it's a multiclass classification!
text = text.replace("precision_score(y_test, y_pred, zero_division=0)", "precision_score(y_test, y_pred, average='macro', zero_division=0)")
text = text.replace("recall_score(y_test, y_pred, zero_division=0)", "recall_score(y_test, y_pred, average='macro', zero_division=0)")

# cv_score for precision and recall
text = text.replace("precision_score(y_val, y_pred, zero_division=0)", "precision_score(y_val, y_pred, average='macro', zero_division=0)")
text = text.replace("recall_score(y_val, y_pred, zero_division=0)", "recall_score(y_val, y_pred, average='macro', zero_division=0)")

# fpr_probe was fixed, but let's make sure `fpr` tuple unpack is fine
text = text.replace("print(f\"F1={holdout_metrics['holdout_f1_macro']:.3f}  FPR={fpr:.2f}\")", "print(f\"F1={holdout_metrics['holdout_f1_macro']:.3f}  FPR_mild={fpr['fpr_mild']:.2f}\")")

# Wait,roc_auc_score requires multi_class="ovr" for multiclass!
text = text.replace("roc_auc_score(y_val, scores)", "roc_auc_score(y_val, proba, multi_class='ovr')")
text = text.replace("roc_auc_score(y_test, scores)", "roc_auc_score(y_test, proba, multi_class='ovr')")
text = text.replace("scores = proba[:, 1] if proba.shape[1] >= 2 else proba.ravel()", "")
text = text.replace("scores = proba[:, 1]", "")

# Fix roc_auc in cv_score
roc_cv = """        if hasattr(est, "predict_proba"):
            proba = est.predict_proba(X_val)
            if len(set(y_val)) > 1 and proba.shape[1] > 1:
                aucs.append(roc_auc_score(y_val, proba, multi_class='ovr'))"""
text = re.sub(r'        if hasattr\(est, "predict_proba"\):.*?aucs\.append\(roc_auc_score\(y_val, scores\)\)', roc_cv, text, flags=re.DOTALL)

# Fix roc_auc in holdout_score
roc_holdout = """    if hasattr(estimator, "predict_proba") and len(set(y_test)) > 1:
        proba = estimator.predict_proba(X_test)
        if proba.shape[1] > 1:
            metrics["holdout_roc_auc"] = float(roc_auc_score(y_test, proba, multi_class='ovr'))"""
text = re.sub(r'    if hasattr\(estimator, "predict_proba"\) and len\(set\(y_test\)\) > 1:.*?metrics\["holdout_roc_auc"\] = float\(roc_auc_score\(y_test, scores\)\)', roc_holdout, text, flags=re.DOTALL)


path.write_text(text)
print("run_benchmark.py patched successfully again")
