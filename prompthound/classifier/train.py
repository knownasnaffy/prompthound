"""classifier/train.py — Training entry point for the benchmark harness.

This module is the ONLY place model fitting happens.  It is:
  - Called exclusively from ``benchmark/run_benchmark.py``.
  - Never imported anywhere inside ``prompthound/`` (verified in test suite).
  - Never invoked at ``scan`` runtime — the scan path only loads a pre-fitted
    ``.joblib`` artifact via ``classifier/model.py`` (AGENTS.md §5).

Public API::

    result = train_model(
        X_train,   # np.ndarray, shape (n_samples, n_features)
        y_train,   # np.ndarray of int (0=benign, 1=malicious)
        estimator_class,   # uninstantiated sklearn-style class
        hyperparams,       # dict of kwargs for the constructor
        feature_names,     # list[str] matching FEATURE_ORDER
        random_state=42,
    )
    # result.estimator   — fitted estimator
    # result.fit_time_s  — wall-clock fit time in seconds

The caller (run_benchmark.py) is responsible for:
  - Feature extraction and caching.
  - Train/test splitting.
  - Cross-validation orchestration.
  - Recording metrics.
  - Calling joblib.dump() to save the artifact.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class TrainResult:
    """Outcome of a single ``train_model`` call.

    Attributes:
        estimator:      Fitted estimator ready for ``.predict_proba()``.
        fit_time_s:     Wall-clock time (seconds) for the ``.fit()`` call.
        feature_names:  The feature column order the estimator was trained on
                        — must match ``FEATURE_ORDER`` from ``features.py``.
        hyperparams:    The hyperparameter dict passed to the constructor.
        model_name:     Friendly name from ``models.yaml`` (e.g. "decision_tree").
    """

    estimator: Any
    fit_time_s: float
    feature_names: list[str]
    hyperparams: dict[str, Any]
    model_name: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    estimator_class: type,
    hyperparams: dict[str, Any],
    feature_names: list[str],
    model_name: str = "",
    random_state: int = 42,
) -> TrainResult:
    """Fit ``estimator_class(**hyperparams)`` on ``(X_train, y_train)``.

    Args:
        X_train:          Training features, shape ``(n_samples, n_features)``.
        y_train:          Training labels, shape ``(n_samples,)``, values in {0, 1}.
        estimator_class:  An uninstantiated sklearn-compatible estimator class.
                          Loaded by run_benchmark.py via importlib from the
                          fully-qualified ``estimator`` field in models.yaml.
        hyperparams:      Constructor kwargs for the estimator.
        feature_names:    List of feature names in column order — stored in the
                          result for provenance tracking.
        model_name:       Human-readable name from models.yaml (optional).
        random_state:     Seed forwarded to the estimator if it accepts
                          ``random_state`` as a constructor kwarg.  Ensures
                          reproducible fits across benchmark runs.

    Returns:
        A ``TrainResult`` with the fitted estimator and wall-clock fit time.

    Raises:
        ValueError:  If ``X_train`` and ``y_train`` have incompatible shapes.
        TypeError:   If ``estimator_class`` does not expose a ``.fit()`` method.
    """
    if len(X_train) != len(y_train):
        raise ValueError(
            f"X_train has {len(X_train)} rows but y_train has {len(y_train)} entries."
        )

    # Inject random_state only when the estimator accepts it — avoids errors
    # for estimators that don't have the parameter (e.g. some custom wrappers).
    import inspect

    init_sig = inspect.signature(estimator_class.__init__)
    if "random_state" in init_sig.parameters:
        hyperparams = {**hyperparams, "random_state": random_state}

    estimator = estimator_class(**hyperparams)

    if not hasattr(estimator, "fit"):
        raise TypeError(
            f"{estimator_class.__name__} does not expose a .fit() method."
        )

    t0 = time.perf_counter()
    estimator.fit(X_train, y_train)
    fit_time_s = time.perf_counter() - t0

    return TrainResult(
        estimator=estimator,
        fit_time_s=fit_time_s,
        feature_names=list(feature_names),
        hyperparams=dict(hyperparams),
        model_name=model_name,
    )


def get_tree_stats(estimator: Any) -> dict[str, float]:
    """Extract interpretability-proxy stats from a tree-based estimator.

    Returns a dict with:
      - ``mean_depth``:    For single trees — the actual tree depth.
                          For ensembles — mean depth across all estimators.
      - ``total_nodes``:  Total number of decision nodes across all trees.
      - ``n_estimators``: Number of trees in the ensemble (1 for single trees).

    Returns all-zero dict for non-tree estimators (e.g. if a non-tree model
    is accidentally passed — graceful rather than raising).
    """
    result: dict[str, float] = {
        "mean_depth": 0.0,
        "total_nodes": 0.0,
        "n_estimators": 1.0,
    }

    # Single sklearn decision tree.
    if hasattr(estimator, "tree_"):
        result["mean_depth"] = float(estimator.tree_.max_depth)
        result["total_nodes"] = float(estimator.tree_.node_count)
        result["n_estimators"] = 1.0
        return result

    # Ensemble: RandomForest, GradientBoosting — access via .estimators_ list.
    estimators_list: list[Any] = []
    if hasattr(estimator, "estimators_"):
        raw = estimator.estimators_
        # GradientBoosting: estimators_ is a 2-D array of shape (n_estimators, n_classes).
        if hasattr(raw, "flatten"):
            estimators_list = list(raw.flatten())
        elif isinstance(raw, list) and raw and isinstance(raw[0], list):
            # list of lists
            estimators_list = [e for sub in raw for e in sub]
        else:
            estimators_list = list(raw)

    # LightGBM: no tree_ attribute; we can query the booster.
    if not estimators_list:
        try:
            booster = estimator.booster_
            n_trees = booster.num_trees()
            depths = []
            for i in range(n_trees):
                df = booster.trees_to_dataframe()
                tree_df = df[df["tree_index"] == i]
                depths.append(tree_df["depth"].max() if "depth" in tree_df.columns else 0)
            result["mean_depth"] = float(sum(depths) / n_trees) if n_trees else 0.0
            result["total_nodes"] = float(len(booster.trees_to_dataframe()))
            result["n_estimators"] = float(n_trees)
        except Exception:
            pass
        return result

    depths = []
    nodes = 0
    for est in estimators_list:
        if hasattr(est, "tree_"):
            depths.append(est.tree_.max_depth)
            nodes += est.tree_.node_count

    result["mean_depth"] = float(sum(depths) / len(depths)) if depths else 0.0
    result["total_nodes"] = float(nodes)
    result["n_estimators"] = float(len(estimators_list))
    return result
