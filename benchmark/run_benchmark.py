"""benchmark/run_benchmark.py — Model selection benchmark harness.

Usage::

    python benchmark/run_benchmark.py
    python benchmark/run_benchmark.py --models decision_tree,random_forest
    python benchmark/run_benchmark.py --models decision_tree --folds 5
    python benchmark/run_benchmark.py --models decision_tree,gradient_boosting --folds 5

Flow (tech-implementation.md §5.3):
  1. Load labels.csv → build benign/malicious split + benign_unusual probe set.
  2. Run parse + feature extraction once per file, cache results.
  3. For each candidate in models.yaml (filtered by --models if given):
       a. Grid-search over hyperparameter combinations.
       b. Stratified k-fold CV on benign+malicious only.
       c. Final metrics on held-out test split.
       d. FPR on benign_unusual probe set.
       e. Tree depth / node count (interpretability proxy).
       f. Fit + predict wall-clock time.
  4. Write benchmark/results/comparison.csv and comparison.md, sorted by
     primary_metric with tie_breaker applied.

``benign_unusual`` is NEVER mixed into training (AGENTS.md §6).  It is only
used as an eval probe to measure false-positive rate.

This script must NOT be imported from anywhere inside ``prompthound/``.
"""

from __future__ import annotations

import argparse
import csv
import importlib
import itertools
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import yaml

# ── Ensure the project root is importable even when run as a script. ──────────
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prompthound.classifier.train import TrainResult, get_tree_stats, train_model  # noqa: E402
from prompthound.features import FEATURE_ORDER, extract_features  # noqa: E402
from prompthound.parse import parse_skill  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────
CORPUS_DIR = _HERE / "corpus"
LABELS_CSV = CORPUS_DIR / "labels.csv"
BENIGN_UNUSUAL_DIR = CORPUS_DIR / "benign_unusual"
RESULTS_DIR = _HERE / "results"
MODELS_YAML = _HERE / "models.yaml"


# ── sklearn imports (imported here so the rest of the module stays importable
#    even before sklearn is installed during testing). ─────────────────────────
def _sklearn_imports() -> tuple[Any, Any, Any]:
    from sklearn.metrics import (
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )
    from sklearn.model_selection import StratifiedKFold, train_test_split

    return (
        (f1_score, precision_score, recall_score, roc_auc_score),
        StratifiedKFold,
        train_test_split,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Label loading
# ─────────────────────────────────────────────────────────────────────────────

def load_labels(labels_csv: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    
    for cls_name in ["benign", "suspicious", "malicious"]:
        d = CORPUS_DIR / cls_name
        if d.exists():
            for p in d.iterdir():
                if p.is_dir() or p.suffix == ".md":
                    rows.append({"filepath": str(p.relative_to(_ROOT)), "label": cls_name})
                
    return sorted(rows, key=lambda x: x["filepath"])


# ─────────────────────────────────────────────────────────────────────────────
# Feature extraction with caching
# ─────────────────────────────────────────────────────────────────────────────

def extract_all_features(
    filepaths: list[Path],
    root: Path,
) -> tuple[np.ndarray, list[Path], list[Path]]:
    """Parse + extract features for every file in ``filepaths``.

    Returns:
        X:       Feature matrix, shape (n_ok, n_features).
        ok:      Paths that parsed cleanly (same order as X rows).
        failed:  Paths that failed to parse.
    """
    X_rows: list[list[float]] = []
    ok: list[Path] = []
    failed: list[Path] = []

    for fp in filepaths:
        abs_fp = root / fp if not fp.is_absolute() else fp
        try:
            if abs_fp.is_dir():
                from prompthound.flatten import parse_directory
                parsed = parse_directory(str(abs_fp))
            else:
                parsed = parse_skill(str(abs_fp))
            
            if not parsed.parse_ok:
                print(f"  [SKIP] {fp}: parse error — {parsed.parse_error}", file=sys.stderr)
                failed.append(fp)
                continue
            fv = extract_features(parsed)
            X_rows.append([fv.values[name] for name in FEATURE_ORDER])
            ok.append(fp)
        except Exception as exc:
            print(f"  [SKIP] {fp}: exception — {exc}", file=sys.stderr)
            failed.append(fp)

    X = np.array(X_rows, dtype=float) if X_rows else np.empty((0, len(FEATURE_ORDER)))
    return X, ok, failed


# ─────────────────────────────────────────────────────────────────────────────
# Hyperparameter grid expansion
# ─────────────────────────────────────────────────────────────────────────────

def expand_grid(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
    """Return the cartesian product of a hyperparameter grid dict."""
    if not grid:
        return [{}]
    keys = list(grid.keys())
    values = [grid[k] for k in keys]
    return [dict(zip(keys, combo, strict=False)) for combo in itertools.product(*values)]


# ─────────────────────────────────────────────────────────────────────────────
# Estimator loading
# ─────────────────────────────────────────────────────────────────────────────

def load_estimator_class(dotted_path: str) -> type | None:
    """Import and return an estimator class from a dotted module path.

    Returns ``None`` if the module is unavailable (e.g. lightgbm not installed).
    """
    module_path, _, class_name = dotted_path.rpartition(".")
    try:
        mod = importlib.import_module(module_path)
        return getattr(mod, class_name)
    except (ImportError, ModuleNotFoundError, AttributeError):
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Cross-validation scoring
# ─────────────────────────────────────────────────────────────────────────────

def cv_score(
    estimator_class: type,
    hyperparams: dict[str, Any],
    X: np.ndarray,
    y: np.ndarray,
    n_folds: int,
    random_state: int = 42,
) -> dict[str, float]:
    """Run stratified k-fold CV and return mean metrics.

    Returns dict with keys: cv_f1_macro, cv_precision, cv_recall, cv_roc_auc.
    """
    (f1_score, precision_score, recall_score, roc_auc_score), StratifiedKFold, _ = (
        _sklearn_imports()
    )

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)

    f1s, precs, recs, aucs = [], [], [], []

    for train_idx, val_idx in skf.split(X, y):
        X_tr, X_val = X[train_idx], X[val_idx]
        y_tr, y_val = y[train_idx], y[val_idx]

        result = train_model(
            X_tr, y_tr, estimator_class, hyperparams,
            feature_names=FEATURE_ORDER, random_state=random_state,
        )
        est = result.estimator

        y_pred = est.predict(X_val)
        f1s.append(f1_score(y_val, y_pred, average='macro', zero_division=0))
        precs.append(precision_score(y_val, y_pred, average='macro', zero_division=0))
        recs.append(recall_score(y_val, y_pred, average='macro', zero_division=0))

        if hasattr(est, "predict_proba"):
            proba = est.predict_proba(X_val)
            if len(set(y_val)) > 1 and proba.shape[1] > 1:
                aucs.append(roc_auc_score(y_val, proba, multi_class='ovr'))

    return {
        "cv_f1_macro": float(np.mean(f1s)) if f1s else 0.0,
        "cv_precision": float(np.mean(precs)) if precs else 0.0,
        "cv_recall": float(np.mean(recs)) if recs else 0.0,
        "cv_roc_auc": float(np.mean(aucs)) if aucs else 0.0,
    }


def holdout_score(
    estimator: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> dict[str, float]:
    """Score a fitted estimator on the holdout test set."""
    (f1_score, precision_score, recall_score, roc_auc_score), _, _ = _sklearn_imports()

    y_pred = estimator.predict(X_test)
    metrics: dict[str, float] = {
        "holdout_f1_macro": float(f1_score(y_test, y_pred, average='macro', zero_division=0)),
        "holdout_precision": float(precision_score(y_test, y_pred, average='macro', zero_division=0)),
        "holdout_recall": float(recall_score(y_test, y_pred, average='macro', zero_division=0)),
        "holdout_roc_auc": 0.0,
    }

    if hasattr(estimator, "predict_proba") and len(set(y_test)) > 1:
        proba = estimator.predict_proba(X_test)
        
        metrics["holdout_roc_auc"] = float(roc_auc_score(y_test, proba, multi_class='ovr'))

    try:
        is_bundle_idx = FEATURE_ORDER.index("is_bundle")
        bundle_mask = X_test[:, is_bundle_idx] == 1.0
        
        # bundle slice
        if np.any(bundle_mask):
            metrics["holdout_f1_macro_bundle"] = float(f1_score(y_test[bundle_mask], y_pred[bundle_mask], average='macro', zero_division=0))
        else:
            metrics["holdout_f1_macro_bundle"] = float('nan')
            
        # single file slice
        if np.any(~bundle_mask):
            metrics["holdout_f1_macro_single"] = float(f1_score(y_test[~bundle_mask], y_pred[~bundle_mask], average='macro', zero_division=0))
        else:
            metrics["holdout_f1_macro_single"] = float('nan')
    except ValueError:
        pass

    return metrics


def fpr_probe(estimator: Any, X_probe: np.ndarray) -> dict[str, float]:
    if len(X_probe) == 0:
        return {"fpr_mild": 0.0, "fpr_severe": 0.0}
    y_pred = estimator.predict(X_probe)
    # y_pred: 0=safe, 1=suspicious, 2=malicious
    return {
        "fpr_mild": float(np.mean(y_pred == 1)),
        "fpr_severe": float(np.mean(y_pred == 2)),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Single candidate benchmark
# ─────────────────────────────────────────────────────────────────────────────

def benchmark_candidate(
    candidate: dict[str, Any],
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    X_probe: np.ndarray,
    n_folds: int,
    random_state: int = 42,
) -> list[dict[str, Any]]:
    """Grid-search one candidate, return a list of result dicts (one per combo).

    Each result dict has keys suitable for the CSV columns.
    """
    name = candidate["name"]
    estimator_path = candidate["estimator"]
    grid = candidate.get("grid", {})

    estimator_class = load_estimator_class(estimator_path)
    if estimator_class is None:
        print(f"  [SKIP] {name}: estimator '{estimator_path}' not available.", file=sys.stderr)
        return []

    combos = expand_grid(grid)
    print(f"\n  [{name}] {len(combos)} hyperparameter combinations …")

    rows: list[dict[str, Any]] = []

    for i, params in enumerate(combos, 1):
        param_str = ", ".join(f"{k}={v}" for k, v in params.items()) or "(default)"
        print(f"    ({i}/{len(combos)}) {param_str}", end=" ", flush=True)

        # ── CV metrics ────────────────────────────────────────────────────
        cv_metrics = cv_score(
            estimator_class, params, X_train, y_train,
            n_folds=n_folds, random_state=random_state,
        )

        # ── Fit final model on full training split ─────────────────────
        t_fit_start = time.perf_counter()  # noqa: F841
        result: TrainResult = train_model(
            X_train, y_train, estimator_class, params,
            feature_names=FEATURE_ORDER,
            model_name=name,
            random_state=random_state,
        )
        t_predict_start = time.perf_counter()

        # ── Holdout metrics ───────────────────────────────────────────────
        holdout_metrics = holdout_score(result.estimator, X_test, y_test)

        t_predict_end = time.perf_counter()

        # ── FPR probe ─────────────────────────────────────────────────────
        fpr = fpr_probe(result.estimator, X_probe)
        fpr_mild = fpr['fpr_mild']
        fpr_severe = fpr['fpr_severe']

        # ── Interpretability stats ────────────────────────────────────────
        tree_stats = get_tree_stats(result.estimator)

        print(f"F1={holdout_metrics['holdout_f1_macro']:.3f}  FPR_mild={fpr['fpr_mild']:.2f}")

        row: dict[str, Any] = {
            "run_id": f"{name}__{i:04d}",
            "model_name": name,
            "hyperparams": "; ".join(f"{k}={v}" for k, v in params.items()),
            **cv_metrics,
            **holdout_metrics,
            "fpr_mild": round(fpr_mild, 4),
            "fpr_severe": round(fpr_severe, 4),
            "mean_depth": round(tree_stats["mean_depth"], 2),
            "total_nodes": int(tree_stats["total_nodes"]),
            "n_estimators": int(tree_stats["n_estimators"]),
            "fit_time_s": round(result.fit_time_s, 4),
            "predict_time_s": round(t_predict_end - t_predict_start, 4),
        }
        rows.append(row)

    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Tie-breaker sorting
# ─────────────────────────────────────────────────────────────────────────────

def _interpretability_penalty(row: dict[str, Any]) -> float:
    """Lower is better (simpler / shallower model).

    Composite penalty: weighted sum of mean_depth and log(total_nodes).
    Used as a secondary sort key when F1 scores are within epsilon.
    """
    depth = float(row.get("mean_depth", 0) or 0)
    nodes = float(row.get("total_nodes", 1) or 1)
    n_est = float(row.get("n_estimators", 1) or 1)
    import math
    return depth + math.log1p(nodes) + math.log1p(n_est)


def sort_results(
    rows: list[dict[str, Any]],
    primary_metric: str,
    tie_breaker: str,
    epsilon: float,
) -> list[dict[str, Any]]:
    """Sort rows by primary_metric (desc), breaking ties with tie_breaker.

    Within epsilon of the top score, prefer rows with a lower
    interpretability penalty (shallower/simpler).
    """
    if not rows:
        return rows

    # Map metric name to the column name in the row dict.
    metric_col_map = {
        "f1_macro": "holdout_f1_macro",
        "f1": "holdout_f1_macro",
        "holdout_f1_macro": "holdout_f1_macro",
        "roc_auc": "holdout_roc_auc",
        "precision": "holdout_precision",
        "recall": "holdout_recall",
    }
    col = metric_col_map.get(primary_metric, primary_metric)

    top_score = max((float(r.get(col, 0) or 0) for r in rows), default=0.0)

    def sort_key(row: dict[str, Any]) -> tuple[int, float, float]:
        score = float(row.get(col, 0) or 0)
        is_tied = (top_score - score) <= epsilon
        if is_tied:
            # Tie band items come first (group 0). Sort by penalty (lower better), then score (higher better)
            return (0, _interpretability_penalty(row), -score)
        else:
            # Outside tie band items come next (group 1). Sort by score (higher better)
            return (1, 0.0, -score)

    sorted_rows = sorted(rows, key=sort_key)

    # Annotate each row with its rank and whether it's in the tie band.
    for rank, row in enumerate(sorted_rows, 1):
        row["rank"] = rank
        row["in_tie_band"] = abs(float(row.get(col, 0) or 0) - top_score) <= epsilon

    return sorted_rows


# ─────────────────────────────────────────────────────────────────────────────
# Output writers
# ─────────────────────────────────────────────────────────────────────────────

CSV_COLUMNS = [
    "rank", "run_id", "model_name", "hyperparams",
    "cv_f1_macro", "cv_precision", "cv_recall", "cv_roc_auc",
    "holdout_f1_macro", "holdout_precision", "holdout_recall", "holdout_roc_auc",
    "holdout_f1_macro_bundle", "holdout_f1_macro_single",
    "fpr_mild", "fpr_severe",
    "mean_depth", "total_nodes", "n_estimators",
    "fit_time_s", "predict_time_s",
    "in_tie_band",
]


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {path}")


def write_markdown(rows: list[dict[str, Any]], path: Path, run_meta: dict[str, Any]) -> None:
    """Render a human-readable comparison table."""
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# PromptHound — Benchmark Results\n")
    lines.append(f"**Date:** {run_meta.get('date', 'unknown')}  ")
    lines.append(f"**Corpus:** {run_meta.get('n_train', '?')} train "
                 f"({run_meta.get('n_benign', '?')} benign / "
                 f"{run_meta.get('n_malicious', '?')} malicious) | "
                 f"{run_meta.get('n_test', '?')} test holdout | "
                 f"{run_meta.get('n_probe', '?')} benign_unusual probe  ")
    lines.append(f"**CV folds:** {run_meta.get('n_folds', '?')}  ")
    lines.append(f"**Models evaluated:** {run_meta.get('models_run', '?')}  ")
    lines.append("")
    lines.append("Sorted by holdout F1 (desc). Tie-band (≤ε) prefers shallower/simpler models.")
    lines.append("")

    # Table header
    header = (
        "| Rank | Model | Hyperparams | CV F1 | Holdout F1 | F1(bundle) | F1(single) | Holdout P | "
        "Holdout R | ROC-AUC | FPR(probe) | MeanDepth | Nodes | N_est | "
        "FitTime(s) | TieBand |"
    )
    sep = "|" + "|".join(["---"] * 16) + "|"
    lines.append(header)
    lines.append(sep)

    for r in rows:
        tie = "✓" if r.get("in_tie_band") else ""
        params = str(r.get("hyperparams", ""))
        if len(params) > 50:
            params = params[:47] + "..."
        lines.append(
            f"| {r.get('rank', '')} "
            f"| {r.get('model_name', '')} "
            f"| {params} "
            f"| {r.get('cv_f1_macro', 0):.3f} "
            f"| {r.get('holdout_f1_macro', 0):.3f} "
            f"| {r.get('holdout_precision', 0):.3f} "
            f"| {r.get('holdout_recall', 0):.3f} "
            f"| {r.get('holdout_roc_auc', 0):.3f} "
            f"| {r.get('fpr_mild', 0):.2f} | {r.get('fpr_severe', 0):.2f} "
            f"| {r.get('mean_depth', 0):.1f} "
            f"| {r.get('total_nodes', 0)} "
            f"| {r.get('n_estimators', 0)} "
            f"| {r.get('fit_time_s', 0):.3f} "
            f"| {tie} |"
        )

    lines.append("")
    lines.append("> **FPR(probe):** false-positive rate on `benign_unusual/` — "
                 "all files are genuinely benign, so any flag is a false positive.")
    lines.append("> **TieBand:** ✓ means holdout F1 is within ε of the top row; "
                 "within the band the tie-breaker (interpretability penalty) applies.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="PromptHound model selection benchmark harness."
    )
    parser.add_argument(
        "--models",
        default="",
        help="Comma-separated list of candidate names to run (default: all).",
    )
    parser.add_argument(
        "--folds",
        type=int,
        default=None,
        help="Number of CV folds (overrides models.yaml).",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed for reproducibility.",
    )
    args = parser.parse_args()

    # ── Load config ───────────────────────────────────────────────────────────
    with MODELS_YAML.open(encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    eval_cfg = config.get("evaluation", {})
    n_folds = args.folds if args.folds is not None else int(eval_cfg.get("folds", 5))
    test_holdout = float(eval_cfg.get("test_holdout", 0.2))
    primary_metric = eval_cfg.get("primary_metric", "f1")
    epsilon = float(eval_cfg.get("tie_breaker_epsilon", 0.02))
    random_state = args.random_state

    filter_models: set[str] = set()
    if args.models:
        filter_models = {m.strip() for m in args.models.split(",") if m.strip()}

    candidates = config.get("candidates", [])
    if filter_models:
        candidates = [c for c in candidates if c["name"] in filter_models]
    if not candidates:
        print("No candidates to run. Check --models filter or models.yaml.", file=sys.stderr)
        sys.exit(1)

    # ── Load labels ───────────────────────────────────────────────────────────
    print("Loading labels …")
    label_rows = load_labels(LABELS_CSV)
    labeled_paths = [Path(r["filepath"]) for r in label_rows]
    labels_by_path = {Path(r["filepath"]): r["label"] for r in label_rows}

    # ── Extract features (cached — done once, shared across all candidates) ──
    print(f"Extracting features for {len(labeled_paths)} labeled files …")
    X_all, ok_paths, failed_paths = extract_all_features(labeled_paths, root=_ROOT)

    if failed_paths:
        print(f"  Warning: {len(failed_paths)} file(s) skipped due to parse errors.")


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
        sys.exit(1)

    # ── Train/test split (stratified) ─────────────────────────────────────────
    _, _, train_test_split = _sklearn_imports()
    X_train, X_test, y_train, y_test = train_test_split(
        X_all, y_all,
        test_size=test_holdout,
        stratify=y_all,
        random_state=random_state,
    )
    print(f"  Train: {len(y_train)}  Test: {len(y_test)}")

    # ── Extract benign_unusual probe features ─────────────────────────────────
    probe_paths = sorted(BENIGN_UNUSUAL_DIR.glob("*.md"))
    print(f"\nExtracting features for {len(probe_paths)} benign_unusual probe files …")
    X_probe, ok_probe, _ = extract_all_features(
        [p.relative_to(_ROOT) for p in probe_paths], root=_ROOT
    )
    print(f"  Probe set: {len(ok_probe)} files ready.")

    # ── Run each candidate ────────────────────────────────────────────────────
    import datetime
    all_rows: list[dict[str, Any]] = []

    for candidate in candidates:
        rows = benchmark_candidate(
            candidate=candidate,
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            X_probe=X_probe,
            n_folds=n_folds,
            random_state=random_state,
        )
        all_rows.extend(rows)

    if not all_rows:
        print("No results produced. Exiting.", file=sys.stderr)
        sys.exit(1)

    # ── Sort with tie-breaker ─────────────────────────────────────────────────
    sorted_rows = sort_results(all_rows, primary_metric, "interpretability_penalty", epsilon)

    # ── Write outputs ─────────────────────────────────────────────────────────
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(sorted_rows, RESULTS_DIR / "comparison.csv")

    run_meta = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "n_train": len(y_train),
        "n_test": len(y_test),
        "n_benign": n_benign,
        "n_suspicious": n_suspicious,
        "n_malicious": n_malicious,
        "n_probe": len(ok_probe),
        "n_folds": n_folds,
        "models_run": ", ".join(c["name"] for c in candidates),
    }
    write_markdown(sorted_rows, RESULTS_DIR / "comparison.md", run_meta)

    # ── Summary ───────────────────────────────────────────────────────────────
    top = sorted_rows[0]
    print(f"\n{'='*60}")
    print(f"TOP RUN: {top['run_id']}")
    print(f"  Holdout F1={top['holdout_f1_macro']:.3f}  "
          f"FPR(probe)={top['fpr_mild']:.2f}  "
          f"MeanDepth={top['mean_depth']:.1f}  "
          f"Nodes={top['total_nodes']}")
    print(f"  Params: {top['hyperparams']}")
    print(f"{'='*60}")
    print("\nNext step: python benchmark/promote.py --top")


if __name__ == "__main__":
    main()
