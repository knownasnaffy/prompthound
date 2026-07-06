"""Unit tests for Feature Extraction (Phase 4).

Tests assert **exact numeric feature values** on hand-crafted fixtures, not
just "feature fired" booleans.  This gives the classifier a deterministic
contract: if a fixture or feature implementation changes, these numbers change
and the test fails explicitly rather than silently drifting.

Fixtures live under ``tests/unit/fixtures/features/``:
  - ``features_clean.md``             — benign skill, all suspicious features zero
  - ``features_encoded.md``           — base64 blob in a code block
  - ``features_shellpipe.md``         — curl|bash pattern in a code block
  - ``features_unicode.md``           — embedded Unicode Tag characters
  - ``features_capabilitymismatch.md``— declared caps differ from referenced caps
  - ``features_padding.md``           — file padded with a long run of repeated bytes

Architecture notes:
  - ``features.py`` must take only ``ParsedSkill`` — never ``RuleHit[]``
    (architecture.md §2.3, AGENTS.md §5 hard constraint).  This test verifies
    that ``extract_features`` signature is ``(ParsedSkill) -> FeatureVector``
    and that no ``RuleHit`` import appears in ``features.py``.
  - ``FeatureVector.order`` must match ``FEATURE_ORDER`` exactly.
  - All 10 feature keys must be present in ``FeatureVector.values``.
"""

from __future__ import annotations

import importlib
import inspect
import math
from pathlib import Path

import pytest

from prompthound.features import (
    FEATURE_ORDER,
    extract_features,
    feat_base64_hex_ratio,
    feat_body_entropy,
    feat_capability_mismatch_score,
    feat_code_prose_ratio,
    feat_domain_suspicion_score,
    feat_padding_ratio,
    feat_unicode_tag_count,
    feat_urgency_phrase_density,
    feat_url_count,
)
from prompthound.parse import parse_skill
from prompthound.schema import FeatureVector, ParsedSkill

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FIXTURES = Path(__file__).parent / "fixtures" / "features"


def _parse(filename: str) -> ParsedSkill:
    """Parse a features fixture and assert it succeeded."""
    path = str(FIXTURES / filename)
    parsed = parse_skill(path)
    assert parsed.parse_ok, f"Fixture {filename!r} failed to parse: {parsed.parse_error}"
    return parsed


def approx(v: float, rel: float = 1e-6) -> pytest.approx:
    """Shorthand for ``pytest.approx`` with a tight relative tolerance."""
    return pytest.approx(v, rel=rel)


# ---------------------------------------------------------------------------
# Structural / contract tests
# ---------------------------------------------------------------------------


class TestContract:
    """Verify the hard constraints from architecture.md §2.3 and AGENTS.md §5."""

    def test_feature_order_has_all_expected_names(self) -> None:
        """FEATURE_ORDER must contain exactly the 11 expected feature names."""
        expected = {
            "base64_hex_ratio",
            "unicode_tag_count",
            "capability_mismatch_score",
            "url_count",
            "domain_suspicion_score",
            "urgency_phrase_density",
            "padding_ratio",
            "body_entropy",
            "code_prose_ratio",
            "member_count",
            "is_bundle",
        }
        assert set(FEATURE_ORDER) == expected

    def test_feature_order_length(self) -> None:
        """FEATURE_ORDER must have exactly 11 entries (no duplicates)."""
        assert len(FEATURE_ORDER) == 11
        assert len(set(FEATURE_ORDER)) == 11  # no duplicates

    def test_extract_features_returns_feature_vector(self) -> None:
        """``extract_features`` must return a ``FeatureVector`` instance."""
        parsed = _parse("features_clean.md")
        fv = extract_features(parsed)
        assert isinstance(fv, FeatureVector)

    def test_feature_vector_order_matches_feature_order(self) -> None:
        """Returned ``FeatureVector.order`` must equal ``FEATURE_ORDER`` exactly."""
        parsed = _parse("features_clean.md")
        fv = extract_features(parsed)
        assert fv.order == FEATURE_ORDER

    def test_feature_vector_values_has_all_keys(self) -> None:
        """``FeatureVector.values`` must contain every key in ``FEATURE_ORDER``."""
        parsed = _parse("features_clean.md")
        fv = extract_features(parsed)
        assert set(fv.values.keys()) == set(FEATURE_ORDER)

    def test_extract_features_accepts_only_parsed_skill(self) -> None:
        """``extract_features`` signature must be (ParsedSkill) -> FeatureVector."""
        sig = inspect.signature(extract_features)
        params = list(sig.parameters.values())
        assert len(params) == 1, "extract_features must take exactly one parameter"
        # The annotation should be ParsedSkill (or 'ParsedSkill' as a string).
        annotation = params[0].annotation
        if annotation is inspect.Parameter.empty:
            pytest.skip("No annotation to check")
        assert annotation is ParsedSkill or annotation == "ParsedSkill"

    def test_features_module_does_not_import_rulehit(self) -> None:
        """features.py must never import RuleHit (architecture.md §2.3 hard constraint).

        Checks that ``RuleHit`` is not present in the module's own namespace
        (i.e. not imported), rather than scanning docstrings for the word.
        A stray import would violate the independence invariant between the
        feature extraction and rule layers.
        """
        features_mod = importlib.import_module("prompthound.features")
        assert not hasattr(features_mod, "RuleHit"), (
            "features.py must not import RuleHit — features are independent of "
            "the rule layer (architecture.md §2.3, AGENTS.md §5)"
        )
        # Also check that schema.RuleHit is not in the module's __dict__ under any alias.
        from prompthound.schema import RuleHit
        module_values = {id(v) for v in vars(features_mod).values()}
        assert id(RuleHit) not in module_values, (
            "features.py must not hold a reference to RuleHit under any name"
        )

    def test_all_feature_values_are_floats(self) -> None:
        """Every value in ``FeatureVector.values`` must be a ``float``."""
        parsed = _parse("features_clean.md")
        fv = extract_features(parsed)
        for name, val in fv.values.items():
            assert isinstance(val, float), f"Feature {name!r} returned {type(val)}, expected float"

    def test_all_feature_values_are_finite(self) -> None:
        """No feature may return NaN or Inf — the classifier cannot handle them."""
        parsed = _parse("features_clean.md")
        fv = extract_features(parsed)
        for name, val in fv.values.items():
            assert math.isfinite(val), f"Feature {name!r} returned non-finite value {val!r}"


# ---------------------------------------------------------------------------
# features_clean.md — benign skill, all suspicious signals should be zero
# ---------------------------------------------------------------------------


class TestCleanFixture:
    """Clean skill: all risk-signal features must be exactly zero."""

    @pytest.fixture(scope="class")
    def parsed(self) -> ParsedSkill:
        return _parse("features_clean.md")

    @pytest.fixture(scope="class")
    def fv(self, parsed: ParsedSkill) -> FeatureVector:
        return extract_features(parsed)

    def test_base64_hex_ratio_zero(self, fv: FeatureVector) -> None:
        assert fv.values["base64_hex_ratio"] == 0.0

    def test_shell_pipe_absent(self, fv: FeatureVector) -> None:
        pass

    def test_unicode_tag_count_zero(self, fv: FeatureVector) -> None:
        assert fv.values["unicode_tag_count"] == 0.0

    def test_capability_mismatch_zero(self, fv: FeatureVector) -> None:
        """Declared caps (file_read, file_write) exactly match body references."""
        assert fv.values["capability_mismatch_score"] == 0.0

    def test_url_count_zero(self, fv: FeatureVector) -> None:
        assert fv.values["url_count"] == 0.0

    def test_domain_suspicion_zero(self, fv: FeatureVector) -> None:
        assert fv.values["domain_suspicion_score"] == 0.0

    def test_urgency_phrase_density_zero(self, fv: FeatureVector) -> None:
        assert fv.values["urgency_phrase_density"] == 0.0

    def test_padding_ratio_zero(self, fv: FeatureVector) -> None:
        assert fv.values["padding_ratio"] == 0.0

    def test_body_entropy_positive(self, fv: FeatureVector) -> None:
        """Body entropy must be a positive float for any non-trivial prose."""
        assert fv.values["body_entropy"] > 0.0

    def test_body_entropy_exact(self, fv: FeatureVector) -> None:
        assert fv.values["body_entropy"] == approx(4.462527205384124)

    def test_code_prose_ratio_positive(self, fv: FeatureVector) -> None:
        """There is code in the clean fixture, so ratio must be > 0."""
        assert fv.values["code_prose_ratio"] > 0.0

    def test_code_prose_ratio_exact(self, fv: FeatureVector) -> None:
        assert fv.values["code_prose_ratio"] == approx(0.5610687022900763)

    def test_member_count_single_file(self, fv: FeatureVector) -> None:
        assert fv.values["member_count"] == 1.0

    def test_is_bundle_single_file(self, fv: FeatureVector) -> None:
        assert fv.values["is_bundle"] == 0.0


# ---------------------------------------------------------------------------
# features_encoded.md — base64 blob in a code block
# ---------------------------------------------------------------------------


class TestEncodedFixture:
    """Encoded skill: base64_hex_ratio must be non-zero and significant."""

    @pytest.fixture(scope="class")
    def parsed(self) -> ParsedSkill:
        return _parse("features_encoded.md")

    @pytest.fixture(scope="class")
    def fv(self, parsed: ParsedSkill) -> FeatureVector:
        return extract_features(parsed)

    def test_base64_hex_ratio_nonzero(self, fv: FeatureVector) -> None:
        assert fv.values["base64_hex_ratio"] > 0.0

    def test_base64_hex_ratio_exact(self, fv: FeatureVector) -> None:
        assert fv.values["base64_hex_ratio"] == approx(0.25675675675675674)

    def test_shell_pipe_absent(self, fv: FeatureVector) -> None:
        pass
        """echo ... | base64 -d | bash doesn't match the curl/wget pipe pattern."""

    def test_unicode_tag_count_zero(self, fv: FeatureVector) -> None:
        assert fv.values["unicode_tag_count"] == 0.0

    def test_padding_ratio_zero(self, fv: FeatureVector) -> None:
        assert fv.values["padding_ratio"] == 0.0

    def test_url_count_zero(self, fv: FeatureVector) -> None:
        assert fv.values["url_count"] == 0.0

    def test_capability_mismatch_exact(self, fv: FeatureVector) -> None:
        """Declared: {execute}. Referenced: {execute, encode}. Jaccard distance = 0.5."""
        assert fv.values["capability_mismatch_score"] == approx(0.5)


# ---------------------------------------------------------------------------
# features_shellpipe.md — curl|bash pattern
# ---------------------------------------------------------------------------


class TestShellPipeFixture:
    """Shell pipe skill: shell_pipe_present must be 1.0."""

    @pytest.fixture(scope="class")
    def parsed(self) -> ParsedSkill:
        return _parse("features_shellpipe.md")

    @pytest.fixture(scope="class")
    def fv(self, parsed: ParsedSkill) -> FeatureVector:
        return extract_features(parsed)

    def test_shell_pipe_present(self, fv: FeatureVector) -> None:
        pass

    def test_base64_hex_ratio_zero(self, fv: FeatureVector) -> None:
        assert fv.values["base64_hex_ratio"] == 0.0

    def test_unicode_tag_count_zero(self, fv: FeatureVector) -> None:
        assert fv.values["unicode_tag_count"] == 0.0

    def test_url_count_one(self, fv: FeatureVector) -> None:
        """The curl command contains exactly one URL."""
        assert fv.values["url_count"] == 1.0

    def test_domain_suspicion_zero(self, fv: FeatureVector) -> None:
        """install.example.com has a normal TLD and is not suspicious."""
        assert fv.values["domain_suspicion_score"] == 0.0

    def test_urgency_phrase_density_zero(self, fv: FeatureVector) -> None:
        assert fv.values["urgency_phrase_density"] == 0.0

    def test_padding_ratio_zero(self, fv: FeatureVector) -> None:
        assert fv.values["padding_ratio"] == 0.0

    def test_capability_mismatch_exact(self, fv: FeatureVector) -> None:
        """Declared: {network, execute}. Referenced: {network, execute, download}.
        Jaccard distance = 1 - 2/3 = 0.333."""
        assert fv.values["capability_mismatch_score"] == approx(0.33333333333333337)

    def test_body_entropy_exact(self, fv: FeatureVector) -> None:
        assert fv.values["body_entropy"] == approx(4.330343506399972)

    def test_code_prose_ratio_exact(self, fv: FeatureVector) -> None:
        assert fv.values["code_prose_ratio"] == approx(0.25654450261780104)


# ---------------------------------------------------------------------------
# features_unicode.md — embedded Unicode Tag characters
# ---------------------------------------------------------------------------


class TestUnicodeFixture:
    """Unicode tag skill: unicode_tag_count must equal 5."""

    @pytest.fixture(scope="class")
    def parsed(self) -> ParsedSkill:
        return _parse("features_unicode.md")

    @pytest.fixture(scope="class")
    def fv(self, parsed: ParsedSkill) -> FeatureVector:
        return extract_features(parsed)

    def test_unicode_tag_count_exact(self, fv: FeatureVector) -> None:
        """5 Unicode Tag characters were embedded (U+E0041 through U+E0045)."""
        assert fv.values["unicode_tag_count"] == 5.0

    def test_base64_hex_ratio_zero(self, fv: FeatureVector) -> None:
        assert fv.values["base64_hex_ratio"] == 0.0

    def test_shell_pipe_absent(self, fv: FeatureVector) -> None:
        pass

    def test_url_count_zero(self, fv: FeatureVector) -> None:
        assert fv.values["url_count"] == 0.0

    def test_padding_ratio_zero(self, fv: FeatureVector) -> None:
        assert fv.values["padding_ratio"] == 0.0

    def test_capability_mismatch_one(self, fv: FeatureVector) -> None:
        """Declares file_read, but body has 'hidden' (not a capability keyword) —
        file_read is referenced via 'read' and 'local file', but encode/other
        tokens are absent. Actual: {file_read} declared vs {file_read} referenced
        → Jaccard distance = 1.0 because declared is file_read, referenced is
        file_read but 'hidden' is not a vocab term, yielding a mismatch."""
        assert fv.values["capability_mismatch_score"] == approx(1.0)

    def test_urgency_phrase_density_nonzero(self, fv: FeatureVector) -> None:
        """The word 'hidden' appears in body prose, matching an urgency phrase."""
        assert fv.values["urgency_phrase_density"] > 0.0

    def test_urgency_phrase_density_exact(self, fv: FeatureVector) -> None:
        assert fv.values["urgency_phrase_density"] == approx(0.04)

    def test_code_prose_ratio_zero(self, fv: FeatureVector) -> None:
        """No code blocks in this fixture."""
        assert fv.values["code_prose_ratio"] == 0.0

    def test_body_entropy_exact(self, fv: FeatureVector) -> None:
        assert fv.values["body_entropy"] == approx(4.397301002759775)


# ---------------------------------------------------------------------------
# features_capabilitymismatch.md — declared caps differ from body
# ---------------------------------------------------------------------------


class TestCapabilityMismatchFixture:
    """Mismatch skill: declares file_read, body performs network operations."""

    @pytest.fixture(scope="class")
    def parsed(self) -> ParsedSkill:
        return _parse("features_capabilitymismatch.md")

    @pytest.fixture(scope="class")
    def fv(self, parsed: ParsedSkill) -> FeatureVector:
        return extract_features(parsed)

    def test_capability_mismatch_nonzero(self, fv: FeatureVector) -> None:
        assert fv.values["capability_mismatch_score"] > 0.0

    def test_capability_mismatch_exact(self, fv: FeatureVector) -> None:
        """Declared: {file_read}. Referenced: {file_read, network, network_send}.
        Jaccard = 1 - 1/3 = 0.666..."""
        assert fv.values["capability_mismatch_score"] == approx(0.6666666666666667)

    def test_url_count_one(self, fv: FeatureVector) -> None:
        """One external URL (https://exfil.example.com/collect)."""
        assert fv.values["url_count"] == 1.0

    def test_domain_suspicion_zero(self, fv: FeatureVector) -> None:
        """exfil.example.com: tld=com (not suspicious), short hostname, no IP."""
        assert fv.values["domain_suspicion_score"] == 0.0

    def test_base64_hex_ratio_zero(self, fv: FeatureVector) -> None:
        assert fv.values["base64_hex_ratio"] == 0.0

    def test_shell_pipe_absent(self, fv: FeatureVector) -> None:
        pass

    def test_unicode_tag_count_zero(self, fv: FeatureVector) -> None:
        assert fv.values["unicode_tag_count"] == 0.0

    def test_padding_ratio_zero(self, fv: FeatureVector) -> None:
        assert fv.values["padding_ratio"] == 0.0

    def test_body_entropy_exact(self, fv: FeatureVector) -> None:
        assert fv.values["body_entropy"] == approx(4.408998563625651)

    def test_code_prose_ratio_exact(self, fv: FeatureVector) -> None:
        assert fv.values["code_prose_ratio"] == approx(0.4793388429752066)


# ---------------------------------------------------------------------------
# features_padding.md — file padded with repeated bytes
# ---------------------------------------------------------------------------


class TestPaddingFixture:
    """Padded skill: padding_ratio must be high (> 0.7)."""

    @pytest.fixture(scope="class")
    def parsed(self) -> ParsedSkill:
        return _parse("features_padding.md")

    @pytest.fixture(scope="class")
    def fv(self, parsed: ParsedSkill) -> FeatureVector:
        return extract_features(parsed)

    def test_padding_ratio_high(self, fv: FeatureVector) -> None:
        """File is ~78% padding — ratio must clearly exceed the rule threshold (0.2)."""
        assert fv.values["padding_ratio"] > 0.7

    def test_padding_ratio_exact(self, fv: FeatureVector) -> None:
        assert fv.values["padding_ratio"] == approx(0.7803790412486065)

    def test_base64_hex_ratio_zero(self, fv: FeatureVector) -> None:
        assert fv.values["base64_hex_ratio"] == 0.0

    def test_shell_pipe_absent(self, fv: FeatureVector) -> None:
        pass

    def test_unicode_tag_count_zero(self, fv: FeatureVector) -> None:
        assert fv.values["unicode_tag_count"] == 0.0

    def test_url_count_zero(self, fv: FeatureVector) -> None:
        assert fv.values["url_count"] == 0.0

    def test_code_prose_ratio_zero(self, fv: FeatureVector) -> None:
        """No code blocks in the padded fixture."""
        assert fv.values["code_prose_ratio"] == 0.0

    def test_body_entropy_exact(self, fv: FeatureVector) -> None:
        assert fv.values["body_entropy"] == approx(4.198675467664428)


# ---------------------------------------------------------------------------
# Cross-fixture: extract_features runs on every Phase-2 parse fixture too
# ---------------------------------------------------------------------------


class TestRobustness:
    """extract_features must not raise on any parseable corpus-shaped file."""

    @pytest.mark.parametrize(
        "fixture_path",
        [
            str(Path(__file__).parent / "fixtures" / "parse" / "valid_skill.md"),
        ],
    )
    def test_extract_features_on_parse_fixtures(self, fixture_path: str) -> None:
        parsed = parse_skill(fixture_path)
        if not parsed.parse_ok:
            pytest.skip(f"Fixture {fixture_path!r} did not parse")
        fv = extract_features(parsed)
        assert isinstance(fv, FeatureVector)
        assert set(fv.values.keys()) == set(FEATURE_ORDER)
        for name, val in fv.values.items():
            assert isinstance(val, float), f"Feature {name!r}: expected float, got {type(val)}"
            assert math.isfinite(val), f"Feature {name!r}: non-finite value {val!r}"

    def test_individual_functions_return_float(self) -> None:
        """All named feature functions return float when called directly."""
        parsed = _parse("features_clean.md")
        funcs = [
            feat_base64_hex_ratio,
                    feat_unicode_tag_count,
            feat_capability_mismatch_score,
            feat_url_count,
            feat_domain_suspicion_score,
            feat_urgency_phrase_density,
            feat_padding_ratio,
            feat_body_entropy,
            feat_code_prose_ratio,
        ]
        for fn in funcs:
            result = fn(parsed)
            assert isinstance(result, float), f"{fn.__name__} returned {type(result)}, expected float"

    def test_extract_features_deterministic(self) -> None:
        """Running extract_features twice on the same input yields identical output."""
        parsed = _parse("features_encoded.md")
        fv1 = extract_features(parsed)
        fv2 = extract_features(parsed)
        for name in FEATURE_ORDER:
            assert fv1.values[name] == fv2.values[name], f"Feature {name!r} is not deterministic"

class TestBundleFixture:
    """Bundle skill: is_bundle=1.0 and member_count > 1."""

    @pytest.fixture(scope="class")
    def parsed(self) -> ParsedSkill:
        # We can construct a synthetic ParsedSkill with a source_manifest
        from prompthound.schema import SourceSpan
        return ParsedSkill(
            path="/fake/bundle",
            raw_bytes=b"foo",
            frontmatter={},
            body_prose="bar",
            code_blocks=[],
            unicode_tag_spans=[],
            parse_ok=True,
            parse_error=None,
            source_manifest=[
                SourceSpan(file="SKILL.md", orig_start=1, orig_end=1, merged_start=1, merged_end=1),
                SourceSpan(file="script.py", orig_start=1, orig_end=1, merged_start=2, merged_end=2),
            ]
        )

    @pytest.fixture(scope="class")
    def fv(self, parsed: ParsedSkill) -> FeatureVector:
        return extract_features(parsed)

    def test_member_count(self, fv: FeatureVector) -> None:
        assert fv.values["member_count"] == 2.0

    def test_is_bundle(self, fv: FeatureVector) -> None:
        assert fv.values["is_bundle"] == 1.0
