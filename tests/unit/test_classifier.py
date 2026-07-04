"""Unit tests for Classifier inference (Phase 8).

Tests load the committed ``model.joblib`` artifact and run inference on known
fixtures, asserting that scores, labels, and decision paths are non-trivial
and stable across runs.

Key assertions:
  - A known malicious file produces score=1.0, label="malicious".
  - A known benign file produces score=0.0, label="benign".
  - Decision paths are non-empty and have the expected structure.
  - Running inference twice on the same input yields identical results
    (determinism guarantee).
  - ``model.py`` never imports ``classifier/train.py`` (AGENTS.md §5 hard
    constraint).
  - The artifact is load-bearing: ``FileNotFoundError`` raised when missing
    (not a silent default score).

Fixtures used:
  - ``benchmark/corpus/malicious/clawhavoc_shell_pipe.md``  — known malicious
  - ``benchmark/corpus/benign/code_review_assistant.md``    — known benign

These are committed corpus files; their feature values (and therefore
classifier outputs) must remain stable once the model artifact is committed.
If they change, re-run ``python benchmark/promote.py --top`` and update the
expected values in this test.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ── Paths ─────────────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parents[2]
CORPUS_MALICIOUS = _ROOT / "benchmark" / "corpus" / "malicious" / "clawhavoc_shell_pipe.md"
CORPUS_BENIGN = _ROOT / "benchmark" / "corpus" / "benign" / "code_review_assistant.md"
ARTIFACT_DIR = _ROOT / "prompthound" / "classifier" / "artifact"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _parse_and_extract(path: Path):
    """Parse a skill file and extract its FeatureVector."""
    from prompthound.features import extract_features
    from prompthound.parse import parse_skill

    parsed = parse_skill(str(path))
    assert parsed.parse_ok, f"Parse failed for {path}: {parsed.parse_error}"
    return extract_features(parsed)


# ─────────────────────────────────────────────────────────────────────────────
# Boundary / constraint tests
# ─────────────────────────────────────────────────────────────────────────────

class TestModelModuleConstraints:
    """Structural constraints from AGENTS.md §5 and architecture.md §2.4."""

    def test_model_py_does_not_import_train_py(self):
        """model.py must never import classifier/train.py (AGENTS.md §5 hard constraint)."""
        model_path = _ROOT / "prompthound" / "classifier" / "model.py"
        source = model_path.read_text(encoding="utf-8")
        assert "from prompthound.classifier.train" not in source, (
            "model.py imports train.py — this violates the hard constraint in AGENTS.md §5"
        )
        assert "import train" not in source, (
            "model.py imports train.py — this violates the hard constraint in AGENTS.md §5"
        )
        assert "classifier.train" not in source, (
            "model.py references classifier.train — violates AGENTS.md §5"
        )

    def test_artifact_files_exist(self):
        """Both model.joblib and metadata.json must be committed."""
        assert (ARTIFACT_DIR / "model.joblib").exists(), (
            "model.joblib not found — run: python benchmark/promote.py --top"
        )
        assert (ARTIFACT_DIR / "metadata.json").exists(), (
            "metadata.json not found — run: python benchmark/promote.py --top"
        )

    def test_metadata_has_required_fields(self):
        """metadata.json must carry all provenance fields written by promote.py."""
        import json
        metadata = json.loads((ARTIFACT_DIR / "metadata.json").read_text(encoding="utf-8"))

        required_fields = [
            "run_id",
            "promoted_at",
            "model_family",
            "estimator_class",
            "hyperparameters",
            "feature_order",
            "corpus",
            "benchmark_metrics",
            "risk_thresholds",
        ]
        for field in required_fields:
            assert field in metadata, f"metadata.json missing required field: '{field}'"

    def test_metadata_feature_order_length(self):
        """feature_order in metadata must have exactly 10 features (concept.md §3)."""
        import json

        from prompthound.features import FEATURE_ORDER

        metadata = json.loads((ARTIFACT_DIR / "metadata.json").read_text(encoding="utf-8"))
        assert len(metadata["feature_order"]) == 10
        assert metadata["feature_order"] == FEATURE_ORDER, (
            "metadata.json feature_order does not match FEATURE_ORDER in features.py — "
            "re-run promote.py if FEATURE_ORDER changed"
        )

    def test_classify_raises_on_missing_artifact(self, tmp_path, monkeypatch):
        """classify() must raise FileNotFoundError when the artifact is missing,
        not silently return a default score (architecture.md §4)."""
        from prompthound.classifier import model as model_module

        # Temporarily redirect the artifact path to a nonexistent directory
        monkeypatch.setattr(model_module, "_MODEL_PATH", tmp_path / "nonexistent.joblib")
        # Clear the lru_cache so the monkeypatched path is used
        model_module._load_artifact.cache_clear()

        fv = _parse_and_extract(CORPUS_BENIGN)
        with pytest.raises(FileNotFoundError):
            model_module.classify(fv)

        # Restore cache so subsequent tests use the real artifact
        model_module._load_artifact.cache_clear()


# ─────────────────────────────────────────────────────────────────────────────
# Core inference tests
# ─────────────────────────────────────────────────────────────────────────────

class TestClassifyMalicious:
    """Inference on a known malicious skill file."""

    @pytest.fixture(scope="class")
    def risk(self):
        from prompthound.classifier.model import classify
        fv = _parse_and_extract(CORPUS_MALICIOUS)
        return classify(fv)

    def test_score_is_one(self, risk):
        """Known malicious file must score 1.0 (pure malicious leaf)."""
        assert risk.score == 1.0, f"Expected score=1.0, got {risk.score}"

    def test_label_is_malicious(self, risk):
        """Score 1.0 must map to label='malicious' (threshold ≥ 0.65)."""
        assert risk.label == "malicious"

    def test_decision_path_non_empty(self, risk):
        """Decision path must be non-empty — bare score without path is a black box."""
        assert len(risk.decision_path) > 0, "decision_path is empty"

    def test_decision_path_has_leaf(self, risk):
        """Last entry must be the leaf node (feature='[leaf]')."""
        assert risk.decision_path[-1]["feature"] == "[leaf]", (
            f"Last decision_path entry is not a leaf: {risk.decision_path[-1]}"
        )

    def test_decision_path_leaf_value_is_one(self, risk):
        """Malicious leaf node_value must be 1.0 (pure malicious node)."""
        leaf = risk.decision_path[-1]
        assert leaf["node_value"] == 1.0, (
            f"Expected leaf node_value=1.0 for malicious file, got {leaf['node_value']}"
        )

    def test_decision_path_entries_have_required_keys(self, risk):
        """Every decision path entry (including leaf) must have the documented keys."""
        for entry in risk.decision_path:
            assert "feature" in entry, f"Missing 'feature' key in entry: {entry}"
            assert "threshold" in entry, f"Missing 'threshold' key in entry: {entry}"
            assert "direction" in entry, f"Missing 'direction' key in entry: {entry}"
            assert "node_value" in entry, f"Missing 'node_value' key in entry: {entry}"

    def test_decision_nodes_have_valid_direction(self, risk):
        """Non-leaf decision nodes must have direction '<=' or '>'."""
        for entry in risk.decision_path:
            if entry["feature"] != "[leaf]":
                assert entry["direction"] in ("<=", ">"), (
                    f"Invalid direction '{entry['direction']}' in entry: {entry}"
                )

    def test_decision_nodes_feature_is_known(self, risk):
        """Non-leaf decision nodes must reference a feature in FEATURE_ORDER."""
        from prompthound.features import FEATURE_ORDER
        for entry in risk.decision_path:
            if entry["feature"] != "[leaf]":
                assert entry["feature"] in FEATURE_ORDER, (
                    f"Unknown feature '{entry['feature']}' in decision_path. "
                    f"Valid features: {FEATURE_ORDER}"
                )

    def test_risk_score_is_risk_score_dataclass(self, risk):
        """classify() must return a RiskScore instance, not a raw dict or tuple."""
        from prompthound.schema import RiskScore
        assert isinstance(risk, RiskScore)


class TestClassifyBenign:
    """Inference on a known benign skill file."""

    @pytest.fixture(scope="class")
    def risk(self):
        from prompthound.classifier.model import classify
        fv = _parse_and_extract(CORPUS_BENIGN)
        return classify(fv)

    def test_score_is_zero(self, risk):
        """Known benign file must score 0.0 (pure benign leaf)."""
        assert risk.score == 0.0, f"Expected score=0.0, got {risk.score}"

    def test_label_is_benign(self, risk):
        """Score 0.0 must map to label='benign' (threshold < 0.3)."""
        assert risk.label == "benign"

    def test_decision_path_non_empty(self, risk):
        """Benign file decision path must also be non-empty."""
        assert len(risk.decision_path) > 0

    def test_decision_path_has_leaf(self, risk):
        """Last entry must be the leaf node."""
        assert risk.decision_path[-1]["feature"] == "[leaf]"

    def test_decision_path_leaf_value_is_zero(self, risk):
        """Benign leaf node_value must be 0.0 (pure benign node)."""
        leaf = risk.decision_path[-1]
        assert leaf["node_value"] == 0.0, (
            f"Expected leaf node_value=0.0 for benign file, got {leaf['node_value']}"
        )

    def test_decision_path_longer_than_malicious(self, risk):
        """Benign path traverses two decision nodes (depth-1 tree has 2 splits
        before the benign leaf), so path length should be > 1 decision node."""
        # path: [root split, second split, leaf] = length 3
        assert len(risk.decision_path) >= 2, (
            f"Expected benign path ≥ 2 entries, got {len(risk.decision_path)}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Determinism / stability tests
# ─────────────────────────────────────────────────────────────────────────────

class TestClassifyDeterminism:
    """Inference must be deterministic — same input produces identical output
    on every call (no randomness, no state mutation)."""

    def test_malicious_score_stable_across_runs(self):
        """Calling classify() twice on the same malicious FeatureVector
        must return identical scores and decision paths."""
        from prompthound.classifier.model import classify
        fv = _parse_and_extract(CORPUS_MALICIOUS)
        risk1 = classify(fv)
        risk2 = classify(fv)
        assert risk1.score == risk2.score
        assert risk1.label == risk2.label
        assert risk1.decision_path == risk2.decision_path

    def test_benign_score_stable_across_runs(self):
        """Calling classify() twice on the same benign FeatureVector
        must return identical scores and decision paths."""
        from prompthound.classifier.model import classify
        fv = _parse_and_extract(CORPUS_BENIGN)
        risk1 = classify(fv)
        risk2 = classify(fv)
        assert risk1.score == risk2.score
        assert risk1.label == risk2.label
        assert risk1.decision_path == risk2.decision_path

    def test_malicious_and_benign_scores_differ(self):
        """The malicious and benign fixture must produce different scores —
        if both return the same score the classifier isn't discriminating."""
        from prompthound.classifier.model import classify
        fv_mal = _parse_and_extract(CORPUS_MALICIOUS)
        fv_ben = _parse_and_extract(CORPUS_BENIGN)
        risk_mal = classify(fv_mal)
        risk_ben = classify(fv_ben)
        assert risk_mal.score != risk_ben.score, (
            f"Malicious and benign files produced the same score ({risk_mal.score}) "
            "— classifier is not discriminating"
        )
        assert risk_mal.label != risk_ben.label


# ─────────────────────────────────────────────────────────────────────────────
# Performance / sub-second test
# ─────────────────────────────────────────────────────────────────────────────

class TestClassifyPerformance:
    """Inference must be sub-second — scan path has a 5s startup budget
    (AGENTS.md §2) and the classifier must not dominate it."""

    def test_inference_is_sub_second(self):
        """classify() must complete in under 1 second after artifact is loaded."""
        import time

        from prompthound.classifier.model import classify

        fv = _parse_and_extract(CORPUS_MALICIOUS)
        # Warm up the lru_cache (first call loads from disk)
        classify(fv)

        # Time the second call (pure inference, no disk I/O)
        t0 = time.perf_counter()
        classify(fv)
        elapsed = time.perf_counter() - t0

        assert elapsed < 1.0, (
            f"classify() took {elapsed:.3f}s — must be sub-second (AGENTS.md §2)"
        )
