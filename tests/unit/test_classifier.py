"""Unit tests for Classifier inference (Phase 8).

Tests load the committed ``model.joblib`` artifact and run inference on known
fixtures, asserting that scores, labels, and feature importances are non-trivial
and stable across runs.

Key assertions:
  - A known malicious file produces score > 0.8, label="malicious".
  - A known benign file produces score < 0.2, label="benign".
  - Feature importances are non-empty and have the expected structure.
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

    def test_score_is_high(self, risk):
        """Known malicious file must score > 0.8."""
        assert risk.score > 0.8, f"Expected score > 0.8, got {risk.score}"

    def test_label_is_malicious(self, risk):
        """Score 1.0 must map to label='malicious' (threshold ≥ 0.65)."""
        assert risk.label == "malicious"

    def test_feature_importances_non_empty(self, risk):
        """Feature importances must be non-empty — bare score without path is a black box."""
        assert len(risk.feature_importances) > 0, "feature_importances is empty"

    def test_feature_importances_entries_have_required_keys(self, risk):
        """Every feature_importances entry must have the documented keys."""
        for entry in risk.feature_importances:
            assert "feature" in entry, f"Missing 'feature' key in entry: {entry}"
            assert "importance" in entry, f"Missing 'importance' key in entry: {entry}"

    def test_feature_importances_feature_is_known(self, risk):
        """Feature importances nodes must reference a feature in FEATURE_ORDER."""
        from prompthound.features import FEATURE_ORDER
        for entry in risk.feature_importances:
            assert entry["feature"] in FEATURE_ORDER, (
                f"Unknown feature '{entry['feature']}' in feature_importances. "
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

    def test_score_is_low(self, risk):
        """Known benign file must score < 0.2."""
        assert risk.score < 0.2, f"Expected score < 0.2, got {risk.score}"

    def test_label_is_benign(self, risk):
        """Score 0.0 must map to label='benign' (threshold < 0.3)."""
        assert risk.label == "benign"

    def test_feature_importances_non_empty(self, risk):
        """Benign file feature importances must also be non-empty."""
        assert len(risk.feature_importances) > 0


# ─────────────────────────────────────────────────────────────────────────────
# Determinism / stability tests
# ─────────────────────────────────────────────────────────────────────────────

class TestClassifyDeterminism:
    """Inference must be deterministic — same input produces identical output
    on every call (no randomness, no state mutation)."""

    def test_malicious_score_stable_across_runs(self):
        """Calling classify() twice on the same malicious FeatureVector
        must return identical scores and feature importances."""
        from prompthound.classifier.model import classify
        fv = _parse_and_extract(CORPUS_MALICIOUS)
        risk1 = classify(fv)
        risk2 = classify(fv)
        assert risk1.score == risk2.score
        assert risk1.label == risk2.label
        assert risk1.feature_importances == risk2.feature_importances

    def test_benign_score_stable_across_runs(self):
        """Calling classify() twice on the same benign FeatureVector
        must return identical scores and feature importances."""
        from prompthound.classifier.model import classify
        fv = _parse_and_extract(CORPUS_BENIGN)
        risk1 = classify(fv)
        risk2 = classify(fv)
        assert risk1.score == risk2.score
        assert risk1.label == risk2.label
        assert risk1.feature_importances == risk2.feature_importances

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

    def test_feature_importances_vary_by_sample(self):
        """Feature importances must vary per sample, ensuring the Saabas method
        is genuinely returning local contributions rather than global importances.
        """
        from prompthound.classifier.model import classify
        fv_mal = _parse_and_extract(CORPUS_MALICIOUS)
        fv_ben = _parse_and_extract(CORPUS_BENIGN)
        risk_mal = classify(fv_mal)
        risk_ben = classify(fv_ben)
        
        # We assert that the exact feature lists (names and values) differ
        assert risk_mal.feature_importances != risk_ben.feature_importances, (
            "Feature importances were identical for malicious and benign fixtures! "
            "The model is returning global importances instead of per-sample local contributions."
        )

    def test_feature_importances_can_be_empty_for_solidly_benign(self):
        """A solidly benign file where all splits pushed toward the benign class
        will have no positive contributions, resulting in an empty list.
        This explicitly guards against KeyErrors or unhandled empty lists.
        """
        from prompthound.classifier.model import classify
        # api_schema_validator is known to have 0 positive Saabas contributions
        solid_benign_path = _ROOT / "benchmark" / "corpus" / "benign" / "api_schema_validator.md"
        fv = _parse_and_extract(solid_benign_path)
        risk = classify(fv)
        
        # It's completely valid for a highly benign file to have NO features pushing toward malice
        assert len(risk.feature_importances) == 0, (
            "Expected empty feature importances for a completely clean benign file. "
            "If this failed, the fixture might have gained a slightly positive feature contribution."
        )


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
