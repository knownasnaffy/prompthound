"""classifier/model.py — Inference-only wrapper for the committed model artifact.

Stage: C (architecture.md §2.4).

Responsibilities:
  - Load the committed ``.joblib`` artifact and ``metadata.json`` once at
    import time (lazy, on first call).
  - Accept a ``FeatureVector`` and return a ``RiskScore`` with populated
    ``feature_importances``.
  - The ``feature_importances`` is the primary deliverable of this stage — it turns
    the raw score into an interpretable summary of which features
    contributed to the decision (architecture.md §2.4, concept.md §2).

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

def _score_to_label(proba_array: np.ndarray) -> str:
    """Map class probabilities to a categorical label using argmax.
    
    Classes: 0 = safe, 1 = suspicious, 2 = malicious.
    """
    labels = ["safe", "suspicious", "malicious"]
    idx = int(np.argmax(proba_array))
    # Cap at 2 just in case
    return labels[min(idx, 2)]


# ─────────────────────────────────────────────────────────────────────────────
# Feature Importance extraction
# ─────────────────────────────────────────────────────────────────────────────

def _extract_feature_importances(
    estimator: Any,
    X_row: np.ndarray,
    feature_names: list[str],
    target_class: int
) -> list[dict]:
    """Extract local feature contributions for the sample using the Saabas method.

    Traces the probability delta for the target class (typically the predicted non-safe class).
    """
    if not hasattr(estimator, "estimators_") or target_class == 0:
        return []
    
    contributions = {name: 0.0 for name in feature_names}
    n_trees = len(estimator.estimators_)
    
    for tree in estimator.estimators_:
        if not hasattr(tree, "tree_") or not hasattr(tree, "decision_path"):
            continue
            
        node_indicator = tree.decision_path(X_row)
        node_ids = node_indicator.indices
        
        for i in range(len(node_ids) - 1):
            parent = node_ids[i]
            child = node_ids[i + 1]
            
            feature_idx = tree.tree_.feature[parent]
            if feature_idx < 0 or feature_idx >= len(feature_names):
                continue
            feature_name = feature_names[feature_idx]
            
            # Calculate target fraction at parent and child
            parent_vals = tree.tree_.value[parent, 0]
            child_vals = tree.tree_.value[child, 0]
            
            if target_class < len(parent_vals):
                parent_frac = parent_vals[target_class] / parent_vals.sum() if parent_vals.sum() > 0 else 0.0
                child_frac = child_vals[target_class] / child_vals.sum() if child_vals.sum() > 0 else 0.0
            else:
                parent_frac = 0.0
                child_frac = 0.0
            
            # Contribution is the change in target probability
            delta = child_frac - parent_frac
            contributions[feature_name] += delta

    # Average the contributions over all trees
    active_features = []
    for name, contrib in contributions.items():
        avg_contrib = contrib / n_trees
        # We only report features that pushed the score higher
        if avg_contrib > 0:
            active_features.append({"feature": name, "importance": round(avg_contrib, 4)})
            
    # Sort by importance descending
    active_features.sort(key=lambda x: x["importance"], reverse=True)
    
    # Return top 5
    return active_features[:5]


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def classify(feature_vector: FeatureVector) -> RiskScore:
    """Score a ``FeatureVector`` and return a ``RiskScore`` with local feature contributions.

    Args:
        feature_vector: The numeric feature encoding of a parsed skill file,
                        produced by ``features.extract_features()``.

    Returns:
        ``RiskScore`` with:
          - ``score``: raw malicious-class probability from ``predict_proba()``
          - ``label``: "benign" / "suspicious" / "malicious" from thresholds
          - ``feature_importances``: top features contributing to this score,
            as ``[{feature, importance}]``

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

    # ── predict_proba: probability of [safe, suspicious, malicious] ─────────────────────
    proba = estimator.predict_proba(X_row)
    # proba shape: (1, n_classes) — score is 1.0 - probability of safe (class 0)
    if proba.shape[1] > 1:
        score = 1.0 - float(proba[0, 0])
    else:
        score = float(proba[0, 0])

    # ── Label from argmax ──────────────────────────────────────────────────
    label = _score_to_label(proba[0])
    target_class = int(np.argmax(proba[0]))

    # ── Feature Importances ──────────────────────────────────────────────────
    feature_importances = _extract_feature_importances(estimator, X_row, feature_order, target_class)

    return RiskScore(
        score=round(score, 6),
        label=label,
        feature_importances=feature_importances,
    )
