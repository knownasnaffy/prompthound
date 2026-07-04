"""classifier/model.py — Inference-only wrapper for the committed model artifact.

Stage: C (architecture.md §2.4).

Responsibilities:
  - Load the committed ``.joblib`` artifact and ``metadata.json`` once at
    import time (lazy, on first call).
  - Accept a ``FeatureVector`` and return a ``RiskScore`` with a populated
    ``decision_path``.
  - The ``decision_path`` is the primary deliverable of this stage — it turns
    the raw score into an interpretable trace of which features and thresholds
    led to the decision (architecture.md §2.4, concept.md §2).

Constraints (AGENTS.md §5, hard):
  - This module NEVER imports ``classifier/train.py``.
  - This module NEVER trains at runtime — only loads and predicts.
  - If the artifact is missing, raise a clear ``FileNotFoundError`` rather than
    silently returning a default score.

Public API::

    risk = classify(feature_vector)   # FeatureVector → RiskScore

The thresholds that map a raw probability to a label string
(benign / suspicious / malicious) come from ``metadata.json``, so the
inference logic stays in sync with whatever thresholds were recorded at
promotion time, without hard-coding them here.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from prompthound.schema import FeatureVector, RiskScore

# ── Artifact paths ─────────────────────────────────────────────────────────────
_ARTIFACT_DIR = Path(__file__).resolve().parent / "artifact"
_MODEL_PATH = _ARTIFACT_DIR / "model.joblib"
_METADATA_PATH = _ARTIFACT_DIR / "metadata.json"


# ─────────────────────────────────────────────────────────────────────────────
# Artifact loading (lazy, cached — loaded once per process)
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _load_artifact() -> tuple[Any, dict]:
    """Load and cache the fitted estimator and metadata.

    Returns:
        (estimator, metadata_dict)

    Raises:
        FileNotFoundError: if model.joblib or metadata.json are missing.
    """
    import joblib

    if not _MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model artifact not found: {_MODEL_PATH}\n"
            "Run 'python benchmark/promote.py --top' to generate it."
        )
    if not _METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Metadata not found: {_METADATA_PATH}\n"
            "Run 'python benchmark/promote.py --top' to generate it."
        )

    estimator = joblib.load(_MODEL_PATH)
    metadata = json.loads(_METADATA_PATH.read_text(encoding="utf-8"))
    return estimator, metadata


# ─────────────────────────────────────────────────────────────────────────────
# Label thresholding
# ─────────────────────────────────────────────────────────────────────────────

def _score_to_label(score: float, thresholds: dict) -> str:
    """Map a raw probability score to a categorical label.

    Thresholds come from ``metadata.json["risk_thresholds"]`` and were
    resolved in Phase 7 (benchmark/results/deferred_decisions.md §1):
      - score < benign_max   → "benign"
      - benign_max ≤ score < suspicious_max → "suspicious"
      - score ≥ suspicious_max → "malicious"
    """
    benign_max = float(thresholds.get("benign_max", 0.3))
    suspicious_max = float(thresholds.get("suspicious_max", 0.65))

    if score < benign_max:
        return "benign"
    elif score < suspicious_max:
        return "suspicious"
    else:
        return "malicious"


# ─────────────────────────────────────────────────────────────────────────────
# Decision path extraction
# ─────────────────────────────────────────────────────────────────────────────

def _extract_decision_path_sklearn(
    estimator: Any,
    X_row: np.ndarray,
    feature_names: list[str],
) -> list[dict]:
    """Extract the decision path from a scikit-learn tree estimator.

    Uses ``estimator.decision_path()`` which returns a sparse indicator matrix
    of shape ``(1, n_nodes)``.  We then look up each visited node's split
    feature and threshold from ``estimator.tree_``.

    Returns a list of dicts, one per decision node visited (leaf nodes are
    omitted — they carry no split information):
      - ``feature``    (str)   — feature name
      - ``threshold``  (float) — the split threshold value
      - ``direction``  (str)   — ``"<="`` if the sample went left, ``">"`` if right
      - ``node_value`` (float) — raw leaf/impurity value at this node
                                 (fraction of malicious samples reaching it)

    For a leaf node (feature index == TREE_UNDEFINED = -2), we add a summary
    entry with ``feature="[leaf]"`` recording the final class distribution.
    """
    tree = estimator.tree_

    # decision_path returns a csr_matrix; .indices gives the visited node ids.
    indicator = estimator.decision_path(X_row)
    node_ids = indicator.indices  # shape: (n_nodes_visited_for_sample_0,)

    TREE_UNDEFINED = -2  # sklearn sentinel for leaf nodes
    path: list[dict] = []

    for node_id in node_ids:
        feature_idx = tree.feature[node_id]

        if feature_idx == TREE_UNDEFINED:
            # Leaf node — record class distribution as a summary entry
            node_vals = tree.value[node_id, 0]  # shape (n_classes,)
            total = float(node_vals.sum())
            malicious_frac = float(node_vals[1] / total) if total > 0 else 0.0
            path.append({
                "feature": "[leaf]",
                "threshold": None,
                "direction": None,
                "node_value": round(malicious_frac, 4),
            })
        else:
            # Decision node — determine which branch the sample took
            feature_name = (
                feature_names[feature_idx]
                if feature_idx < len(feature_names)
                else f"feature_{feature_idx}"
            )
            threshold = float(tree.threshold[node_id])
            sample_value = float(X_row[0, feature_idx])
            direction = "<=" if sample_value <= threshold else ">"

            # node_value: fraction of malicious samples at this node
            node_vals = tree.value[node_id, 0]
            total = float(node_vals.sum())
            malicious_frac = float(node_vals[1] / total) if total > 0 else 0.0

            path.append({
                "feature": feature_name,
                "threshold": round(threshold, 6),
                "direction": direction,
                "node_value": round(malicious_frac, 4),
            })

    return path


def _extract_decision_path_ensemble(
    estimator: Any,
    X_row: np.ndarray,
    feature_names: list[str],
) -> list[dict]:
    """Extract a summarised decision path from an ensemble estimator.

    For RandomForest / GradientBoosting, ``decision_path()`` returns paths
    across all constituent trees.  We extract the path from the first tree
    as a representative summary, and annotate it with the ensemble vote.

    This keeps the output human-readable (one representative path, not one
    path per tree) while preserving traceability.
    """
    # Get the first tree from the ensemble
    estimators_list: list[Any] = []
    if hasattr(estimator, "estimators_"):
        raw = estimator.estimators_
        if hasattr(raw, "flatten"):
            estimators_list = list(raw.flatten())
        elif isinstance(raw, list) and raw and isinstance(raw[0], list):
            estimators_list = [e for sub in raw for e in sub]
        else:
            estimators_list = list(raw)

    if not estimators_list:
        return []

    first_tree = estimators_list[0]
    if not hasattr(first_tree, "tree_"):
        return []

    return _extract_decision_path_sklearn(first_tree, X_row, feature_names)


def _extract_decision_path(
    estimator: Any,
    X_row: np.ndarray,
    feature_names: list[str],
) -> list[dict]:
    """Dispatch to the correct decision-path extractor for the estimator type.

    Supports:
      - sklearn ``DecisionTreeClassifier`` — direct tree_ attribute
      - sklearn ensembles (RandomForest, GradientBoosting) — first-tree summary
      - LightGBM — falls back to empty list (leaf-path API differs significantly)

    Returns an empty list for unknown estimator types rather than raising.
    """
    # Single sklearn decision tree
    if hasattr(estimator, "tree_") and hasattr(estimator, "decision_path"):
        return _extract_decision_path_sklearn(estimator, X_row, feature_names)

    # sklearn ensemble: has estimators_ list
    if hasattr(estimator, "estimators_"):
        return _extract_decision_path_ensemble(estimator, X_row, feature_names)

    # LightGBM or other: return empty — graceful degradation
    return []


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def classify(feature_vector: FeatureVector) -> RiskScore:
    """Score a ``FeatureVector`` and return a ``RiskScore`` with decision path.

    Args:
        feature_vector: The numeric feature encoding of a parsed skill file,
                        produced by ``features.extract_features()``.

    Returns:
        ``RiskScore`` with:
          - ``score``: raw malicious-class probability from ``predict_proba()``
          - ``label``: "benign" / "suspicious" / "malicious" from thresholds
          - ``decision_path``: ordered list of split decisions that produced
            this score, as ``[{feature, threshold, direction, node_value}]``

    Raises:
        FileNotFoundError: if the model artifact or metadata.json are missing.
    """
    estimator, metadata = _load_artifact()

    # Build the feature row in the exact column order the model was trained on.
    # Use the feature_order from metadata.json as the authoritative order —
    # this stays correct even if FEATURE_ORDER in features.py is later edited.
    feature_order: list[str] = metadata.get("feature_order", feature_vector.order)
    row_values = [feature_vector.values.get(name, 0.0) for name in feature_order]
    X_row = np.array([row_values], dtype=float)

    # ── predict_proba: probability of [benign, malicious] ─────────────────────
    proba = estimator.predict_proba(X_row)
    # proba shape: (1, n_classes) — extract malicious-class probability
    if proba.shape[1] >= 2:
        score = float(proba[0, 1])
    else:
        score = float(proba[0, 0])

    # ── Label from thresholds in metadata ────────────────────────────────────
    thresholds = metadata.get("risk_thresholds", {})
    label = _score_to_label(score, thresholds)

    # ── Decision path ────────────────────────────────────────────────────────
    decision_path = _extract_decision_path(estimator, X_row, feature_order)

    return RiskScore(
        score=round(score, 6),
        label=label,
        decision_path=decision_path,
    )
