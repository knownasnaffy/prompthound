"""benchmark/promote.py — Promote a benchmark run's fitted estimator to the shipped artifact.

Usage::

    python benchmark/promote.py --top
    python benchmark/promote.py --run-id decision_tree__0003

Flow (tech-implementation.md §5.3, step 5):
  1. Load ``benchmark/results/comparison.csv`` to locate the target run.
  2. Re-fit the winning model on the full labeled corpus (benign + malicious,
     NO benign_unusual) using the exact hyperparameters from the CSV row.
  3. Dump the fitted estimator to
     ``prompthound/classifier/artifact/model.joblib``.
  4. Write ``prompthound/classifier/artifact/metadata.json`` with full
     provenance: model family, hyperparameters, corpus hash, metrics, date,
     and the risk-score label thresholds resolved in Phase 7
     (benchmark/results/deferred_decisions.md).
  5. Print an advisory warning (not a hard error) when FPR(probe) > 0.40,
     per the policy in deferred_decisions.md §2.

This script is the ONLY thing allowed to overwrite
``prompthound/classifier/artifact/model.joblib`` (AGENTS.md §6).  Never
hand-copy a model file in without running this script — it would break
provenance traceability.

This script must NOT be imported from anywhere inside ``prompthound/``.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import importlib
import inspect
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import yaml

# ── Ensure the project root is importable when run as a script. ───────────────
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prompthound.features import FEATURE_ORDER, extract_features  # noqa: E402
from prompthound.parse import parse_skill  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────
CORPUS_DIR = _HERE / "corpus"
LABELS_CSV = CORPUS_DIR / "labels.csv"
BENIGN_UNUSUAL_DIR = CORPUS_DIR / "benign_unusual"
RESULTS_CSV = _HERE / "results" / "comparison.csv"
MODELS_YAML = _HERE / "models.yaml"
ARTIFACT_DIR = _ROOT / "prompthound" / "classifier" / "artifact"

# ── FPR advisory threshold (deferred_decisions.md §2) ─────────────────────────
FPR_ADVISORY_THRESHOLD = 0.40

# ── Risk score thresholds (deferred_decisions.md §1) ──────────────────────────
RISK_THRESHOLDS = {
    "benign_max": 0.3,     # score < 0.3 → benign
    "suspicious_max": 0.65,  # 0.3 ≤ score < 0.65 → suspicious
    # score ≥ 0.65 → malicious
}


# ─────────────────────────────────────────────────────────────────────────────
# Label + feature loading (mirrors run_benchmark.py, intentionally duplicated
# so promote.py has no dependency on run_benchmark.py)
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


def extract_all_features(
    filepaths: list[Path],
    root: Path,
) -> tuple[np.ndarray, list[Path], list[Path]]:
    """Parse + extract features for every file in ``filepaths``.

    Returns:
        X:       Feature matrix, shape (n_ok, n_features).
        ok:      Paths that parsed cleanly.
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


def corpus_hash(filepaths: list[Path], root: Path) -> str:
    """SHA-256 hash of all corpus file contents in sorted path order.

    Provides provenance tracing: metadata.json records which exact corpus
    version the promoted model was trained on.
    """
    h = hashlib.sha256()
    for fp in sorted(filepaths):
        abs_fp = root / fp if not fp.is_absolute() else fp
        try:
            h.update(abs_fp.read_bytes())
        except OSError:
            pass
    return h.hexdigest()[:16]


# ─────────────────────────────────────────────────────────────────────────────
# CSV reading
# ─────────────────────────────────────────────────────────────────────────────

def load_results_csv(csv_path: Path) -> list[dict[str, str]]:
    """Return all rows from comparison.csv as dicts."""
    if not csv_path.exists():
        print(
            f"ERROR: {csv_path} not found. Run benchmark/run_benchmark.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    rows: list[dict[str, str]] = []
    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append(dict(row))
    return rows


def find_run(rows: list[dict[str, str]], run_id: str | None, top: bool) -> dict[str, str]:
    """Return the target CSV row by run_id or by top rank."""
    if top:
        # Row already sorted: rank=1 is the first row (comparison.csv is pre-sorted)
        rank1 = [r for r in rows if r.get("rank") == "1"]
        if rank1:
            return rank1[0]
        # Fall back: sort by holdout_f1 desc
        rows_sorted = sorted(rows, key=lambda r: float(r.get("holdout_f1_macro", 0)), reverse=True)
        return rows_sorted[0]
    else:
        matches = [r for r in rows if r.get("run_id") == run_id]
        if not matches:
            print(f"ERROR: run_id '{run_id}' not found in {RESULTS_CSV}.", file=sys.stderr)
            print("Available run_ids:", file=sys.stderr)
            for r in rows[:10]:
                print(f"  {r.get('run_id')}", file=sys.stderr)
            sys.exit(1)
        return matches[0]


# ─────────────────────────────────────────────────────────────────────────────
# Model loading from models.yaml
# ─────────────────────────────────────────────────────────────────────────────

def load_estimator_class(model_name: str) -> type:
    """Resolve the estimator class for a named model from models.yaml."""
    with MODELS_YAML.open(encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    for candidate in config.get("candidates", []):
        if candidate["name"] == model_name:
            dotted = candidate["estimator"]
            module_path, _, class_name = dotted.rpartition(".")
            try:
                mod = importlib.import_module(module_path)
                return getattr(mod, class_name)
            except (ImportError, AttributeError) as exc:
                print(f"ERROR: Could not import '{dotted}': {exc}", file=sys.stderr)
                sys.exit(1)

    print(f"ERROR: model '{model_name}' not found in {MODELS_YAML}.", file=sys.stderr)
    sys.exit(1)


def parse_hyperparams(hyperparams_str: str) -> dict[str, Any]:
    """Parse the semicolon-separated hyperparams string from comparison.csv.

    E.g. ``"max_depth=3; min_samples_leaf=5; criterion=gini"``
    → ``{"max_depth": 3, "min_samples_leaf": 5, "criterion": "gini"}``
    """
    params: dict[str, Any] = {}
    for part in hyperparams_str.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key, _, val_str = part.partition("=")
        key = key.strip()
        val_str = val_str.strip()
        # Try int, then float, then None literal, then leave as string.
        if val_str == "None":
            params[key] = None
        elif val_str == "True":
            params[key] = True
        elif val_str == "False":
            params[key] = False
        else:
            try:
                params[key] = int(val_str)
            except ValueError:
                try:
                    params[key] = float(val_str)
                except ValueError:
                    params[key] = val_str
    return params


# ─────────────────────────────────────────────────────────────────────────────
# FPR evaluation on probe set
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_fpr_probe(estimator: Any) -> dict[str, float]:
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
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main promotion logic
# ─────────────────────────────────────────────────────────────────────────────

def promote(run_id: str | None, top: bool, random_state: int = 42) -> None:
    """Locate the target run, refit the model, write artifact + metadata."""

    # ── Load the benchmark results ────────────────────────────────────────────
    print(f"Loading benchmark results from {RESULTS_CSV} …")
    rows = load_results_csv(RESULTS_CSV)
    target = find_run(rows, run_id, top)

    model_name = target["model_name"]
    hyperparams_str = target["hyperparams"]
    run_id_actual = target["run_id"]
    fpr_probe_recorded = float(target.get("fpr_mild", 0))

    print(f"\nTarget run: {run_id_actual}")
    print(f"  Model:       {model_name}")
    print(f"  Hyperparams: {hyperparams_str}")
    print(f"  Holdout F1:  {target.get('holdout_f1_macro', '?')}")
    print(f"  FPR(probe):  {fpr_probe_recorded:.2f}")

    # ── Advisory FPR warning (deferred_decisions.md §2) ───────────────────────
    if fpr_probe_recorded > FPR_ADVISORY_THRESHOLD:
        print(
            f"\n⚠️  WARNING: FPR(probe) = {fpr_probe_recorded:.2f} exceeds advisory "
            f"threshold of {FPR_ADVISORY_THRESHOLD:.2f}.\n"
            f"   This means {fpr_probe_recorded*100:.0f}% of benign_unusual files "
            f"would be false-positives.\n"
            f"   Consider selecting a run with lower FPR before promoting to production.\n"
            f"   (To proceed anyway, the artifact will record this value in metadata.json.)",
        )

    # ── Load all training data (benign + malicious, NOT benign_unusual) ───────
    print("\nLoading corpus labels …")
    label_rows = load_labels(LABELS_CSV)
    # Filter to benign/malicious only (exclude benign_unusual — it's eval-only)
    train_rows = [r for r in label_rows if r["label"] in ("benign", "suspicious", "malicious")]
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
    print(f"  Training corpus: {len(y_all)} files ({n_benign} benign, {n_suspicious} suspicious, {n_malicious} malicious)")

    # ── Load estimator class and parse hyperparameters ────────────────────────
    estimator_class = load_estimator_class(model_name)
    hyperparams = parse_hyperparams(hyperparams_str)

    # Inject random_state if the estimator accepts it
    init_sig = inspect.signature(estimator_class.__init__)
    if "random_state" in init_sig.parameters:
        hyperparams = {**hyperparams, "random_state": random_state}

    # ── Fit on the full training corpus ───────────────────────────────────────
    print(f"\nFitting {model_name}({hyperparams_str}) on full corpus …")
    estimator = estimator_class(**hyperparams)
    t0 = time.perf_counter()
    estimator.fit(X_all, y_all)
    fit_time_s = time.perf_counter() - t0
    print(f"  Fit complete in {fit_time_s:.3f}s")

    # ── Re-evaluate FPR on probe set using the newly fitted model ─────────────
    print("Evaluating FPR on benign_unusual probe set …")
    fpr_actual_dict = evaluate_fpr_probe(estimator)
    fpr_actual = fpr_actual_dict['fpr_mild']
    print(f"  FPR(probe) with full-corpus model: {fpr_actual:.2f}")

    if fpr_actual > FPR_ADVISORY_THRESHOLD:
        print(
            f"\n⚠️  WARNING: Full-corpus model FPR(probe) = {fpr_actual:.2f} "
            f"exceeds advisory threshold of {FPR_ADVISORY_THRESHOLD:.2f}.",
        )

    # ── Write artifact ────────────────────────────────────────────────────────
    import joblib

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    model_path = ARTIFACT_DIR / "model.joblib"
    joblib.dump(estimator, model_path)
    print(f"\nSaved model artifact → {model_path}")

    # ── Compute corpus hash for provenance ────────────────────────────────────
    c_hash = corpus_hash(labeled_paths, _ROOT)

    # ── Build and write metadata.json ─────────────────────────────────────────
    metadata: dict[str, Any] = {
        "run_id": run_id_actual,
        "promoted_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "model_family": model_name,
        "estimator_class": f"{estimator_class.__module__}.{estimator_class.__name__}",
        "hyperparameters": parse_hyperparams(hyperparams_str),
        "feature_order": FEATURE_ORDER,
        "corpus": {
            "n_train_benign": n_benign,
            "n_train_suspicious": n_suspicious,
            "n_train_malicious": n_malicious,
            "n_total": int(len(y_all)),
            "corpus_hash": c_hash,
            "labels_csv": str(LABELS_CSV.relative_to(_ROOT)),
        },
        "benchmark_metrics": {
            "cv_f1_macro": float(target.get("cv_f1_macro", 0)),
            "holdout_f1_macro": float(target.get("holdout_f1_macro", 0)),
            "holdout_precision": float(target.get("holdout_precision", 0)),
            "holdout_recall": float(target.get("holdout_recall", 0)),
            "holdout_roc_auc": float(target.get("holdout_roc_auc", 0)),
            "fpr_mild_benchmark": fpr_probe_recorded,
            "fpr_severe_benchmark": float(target.get("fpr_severe", 0)),
            "fpr_mild_full_corpus": round(fpr_actual, 4),
            "fpr_severe_full_corpus": round(fpr_actual_dict["fpr_severe"], 4),
            "mean_depth": float(target.get("mean_depth", 0)),
            "total_nodes": int(float(target.get("total_nodes", 0))),
            "n_estimators": int(float(target.get("n_estimators", 1))),
        },
        "risk_thresholds": {
            "benign_max": RISK_THRESHOLDS["benign_max"],
            "suspicious_max": RISK_THRESHOLDS["suspicious_max"],
            "description": (
                "score < benign_max → benign; "
                "benign_max ≤ score < suspicious_max → suspicious; "
                "score ≥ suspicious_max → malicious"
            ),
        },
        "fit_time_s": round(fit_time_s, 4),
        "random_state": random_state,
        "fpr_advisory_threshold": FPR_ADVISORY_THRESHOLD,
        "fpr_advisory_exceeded": fpr_actual > FPR_ADVISORY_THRESHOLD,
    }

    metadata_path = ARTIFACT_DIR / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(f"Saved metadata       → {metadata_path}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("PROMOTION COMPLETE")
    print(f"  Run:          {run_id_actual}")
    print(f"  Model:        {model_name}")
    print(f"  Corpus hash:  {c_hash}")
    print(f"  FPR(probe):   {fpr_actual:.2f}"
          + (" ⚠️" if fpr_actual > FPR_ADVISORY_THRESHOLD else " ✓"))
    print(f"  Artifact:     {model_path}")
    print(f"  Metadata:     {metadata_path}")
    print(f"{'='*60}")
    print(
        "\nNext step: commit the artifact:\n"
        "  git add prompthound/classifier/artifact/\n"
        f"  git commit -m 'chore: promote model artifact (run {run_id_actual})'"

    )


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Promote a benchmark run's fitted estimator to the shipped artifact.\n\n"
            "Writes prompthound/classifier/artifact/model.joblib + metadata.json."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--top",
        action="store_true",
        help="Promote the top-ranked run from benchmark/results/comparison.csv.",
    )
    group.add_argument(
        "--run-id",
        metavar="RUN_ID",
        help="Promote a specific run by its run_id (e.g. decision_tree__0003).",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed for the refit (default: 42, matches benchmark run).",
    )
    args = parser.parse_args()

    promote(
        run_id=args.run_id,
        top=args.top,
        random_state=args.random_state,
    )


if __name__ == "__main__":
    main()
