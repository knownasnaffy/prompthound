"""Unit tests for the Rule Layer (Phase 3).

Each rule has:
- A *triggering* fixture that must produce ≥ 1 RuleHit with the expected rule_id.
- A *non-triggering* (clean) fixture that must produce 0 RuleHits from that rule.

Tests also verify:
- ALL_RULES registry completeness and structural contract.
- No rule imports another rule (checked via module attribute inspection).
- Running ALL_RULES over every Phase-2 parse fixture produces no exceptions.

Architecture note: ``features.py`` must never receive ``RuleHit`` objects
(architecture.md §2.3); this test module does NOT test that boundary — it's
tested in test_features.py.  This file only exercises the rule callables
themselves against ``ParsedSkill`` inputs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from prompthound.parse import parse_skill
from prompthound.rules import (
    ALL_RULES,
    encoded_blob,
    padding,
    shell_pipe,
    suspicious_domain,
    unicode_tag,
)
from prompthound.schema import RuleHit

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

FIXTURES = Path(__file__).parent / "fixtures" / "rules"
PARSE_FIXTURES = Path(__file__).parent / "fixtures" / "parse"


def _parse(filename: str) -> object:
    """Parse a fixture file and assert it succeeded."""
    path = str(FIXTURES / filename)
    parsed = parse_skill(path)
    assert parsed.parse_ok, f"Fixture {filename!r} failed to parse: {parsed.parse_error}"
    return parsed


def _rule_ids(hits: list[RuleHit]) -> set[str]:
    return {h.rule_id for h in hits}


# ---------------------------------------------------------------------------
# ALL_RULES registry tests
# ---------------------------------------------------------------------------


class TestRegistry:
    def test_all_rules_nonempty(self):
        """ALL_RULES must contain at least one entry."""
        assert len(ALL_RULES) >= 1

    def test_all_rules_are_callable(self):
        """Every entry in ALL_RULES must be callable."""
        for rule in ALL_RULES:
            assert callable(rule), f"{rule!r} is not callable"

    def test_all_rules_contains_all_five(self):
        """ALL_RULES must contain every implemented rule check function."""
        expected = {
            shell_pipe.check,
            encoded_blob.check,
            unicode_tag.check,
            suspicious_domain.check,
            padding.check,
        }
        assert expected.issubset(set(ALL_RULES)), f"Missing rules: {expected - set(ALL_RULES)}"

    def test_no_rule_imports_another_rule_module(self):
        """No rule module should import another rule module (AGENTS.md §5).

        We check by inspecting each rule module's ``__dict__`` for references
        to other rule modules.  This is a structural sanity check, not an
        exhaustive import graph analysis.
        """
        rule_modules = [shell_pipe, encoded_blob, unicode_tag, suspicious_domain, padding]
        rule_module_names = {m.__name__ for m in rule_modules}

        for module in rule_modules:
            for name, obj in vars(module).items():
                if hasattr(obj, "__name__") and obj.__name__ in rule_module_names:
                    if obj.__name__ != module.__name__:
                        pytest.fail(
                            f"{module.__name__} references rule module "
                            f"{obj.__name__!r} via attribute {name!r}"
                        )

    def test_all_rules_return_list_of_rulehits(self):
        """Every rule must return a list (possibly empty) when called with a valid ParsedSkill."""
        parsed = _parse("shell_pipe_clean.md")
        for rule in ALL_RULES:
            result = rule(parsed)
            assert isinstance(
                result, list
            ), f"{rule.__module__}.{rule.__qualname__} returned {type(result).__name__}, expected list"
            for item in result:
                assert isinstance(
                    item, RuleHit
                ), f"{rule.__module__}.{rule.__qualname__} returned a non-RuleHit item: {item!r}"


# ---------------------------------------------------------------------------
# SHELL_PIPE rule
# ---------------------------------------------------------------------------


class TestShellPipeRule:
    def test_trigger(self):
        """shell_pipe_trigger.md must produce ≥ 1 SHELL_PIPE_001 hit."""
        parsed = _parse("shell_pipe_trigger.md")
        hits = shell_pipe.check(parsed)
        assert len(hits) >= 1, "Expected ≥ 1 SHELL_PIPE_001 hit"
        assert "SHELL_PIPE_001" in _rule_ids(hits)

    def test_trigger_severity_is_high(self):
        """SHELL_PIPE_001 hits must have severity 'high'."""
        parsed = _parse("shell_pipe_trigger.md")
        hits = shell_pipe.check(parsed)
        for hit in hits:
            assert hit.severity == "high", f"Expected high severity, got {hit.severity!r}"

    def test_trigger_hits_both_patterns(self):
        """The fixture has both curl|bash and wget|sh — both should fire."""
        parsed = _parse("shell_pipe_trigger.md")
        hits = shell_pipe.check(parsed)
        messages = [h.message for h in hits]
        assert any("curl" in m.lower() for m in messages), "Expected a curl|bash hit"
        assert any("wget" in m.lower() for m in messages), "Expected a wget|sh hit"

    def test_clean(self):
        """shell_pipe_clean.md must produce 0 SHELL_PIPE_001 hits."""
        parsed = _parse("shell_pipe_clean.md")
        hits = shell_pipe.check(parsed)
        shell_hits = [h for h in hits if h.rule_id == "SHELL_PIPE_001"]
        assert len(shell_hits) == 0, f"Expected no hits, got: {shell_hits}"

    def test_hit_span_is_tuple_of_two_ints(self):
        """RuleHit.span must be a (start, end) tuple of integers."""
        parsed = _parse("shell_pipe_trigger.md")
        hits = shell_pipe.check(parsed)
        for hit in hits:
            assert isinstance(hit.span, tuple) and len(hit.span) == 2
            assert all(isinstance(v, int) for v in hit.span)

    def test_hit_message_nonempty(self):
        """RuleHit.message must be a non-empty string."""
        parsed = _parse("shell_pipe_trigger.md")
        hits = shell_pipe.check(parsed)
        for hit in hits:
            assert isinstance(hit.message, str) and hit.message.strip()


# ---------------------------------------------------------------------------
# ENCODED_BLOB rule
# ---------------------------------------------------------------------------


class TestEncodedBlobRule:
    def test_trigger_base64(self):
        """encoded_blob_trigger.md must produce ≥ 1 ENCODED_BLOB_001 hit."""
        parsed = _parse("encoded_blob_trigger.md")
        hits = encoded_blob.check(parsed)
        b64_hits = [h for h in hits if h.rule_id == "ENCODED_BLOB_001"]
        assert len(b64_hits) >= 1, "Expected ≥ 1 ENCODED_BLOB_001 hit"

    def test_trigger_hex(self):
        """encoded_blob_trigger.md must produce ≥ 1 ENCODED_BLOB_002 hit."""
        parsed = _parse("encoded_blob_trigger.md")
        hits = encoded_blob.check(parsed)
        hex_hits = [h for h in hits if h.rule_id == "ENCODED_BLOB_002"]
        assert len(hex_hits) >= 1, "Expected ≥ 1 ENCODED_BLOB_002 hit"

    def test_trigger_severity_is_warn(self):
        """ENCODED_BLOB hits must have severity 'warn'."""
        parsed = _parse("encoded_blob_trigger.md")
        hits = encoded_blob.check(parsed)
        for hit in hits:
            assert hit.severity == "warn", f"Expected warn severity, got {hit.severity!r}"

    def test_clean(self):
        """encoded_blob_clean.md must produce 0 hits."""
        parsed = _parse("encoded_blob_clean.md")
        hits = encoded_blob.check(parsed)
        assert len(hits) == 0, f"Expected no hits on clean fixture, got: {hits}"

    def test_hit_message_contains_length(self):
        """ENCODED_BLOB_001 message must mention the blob length."""
        parsed = _parse("encoded_blob_trigger.md")
        hits = encoded_blob.check(parsed)
        b64_hits = [h for h in hits if h.rule_id == "ENCODED_BLOB_001"]
        for hit in b64_hits:
            # Message should contain something like "88 chars" or "(N chars)"
            assert "chars" in hit.message, f"Expected 'chars' in message: {hit.message!r}"


# ---------------------------------------------------------------------------
# UNICODE_TAG rule
# ---------------------------------------------------------------------------


class TestUnicodeTagRule:
    def test_trigger(self):
        """unicode_tag_trigger.md must produce ≥ 1 UNICODE_TAG_001 hit."""
        parsed = _parse("unicode_tag_trigger.md")
        hits = unicode_tag.check(parsed)
        assert len(hits) >= 1, "Expected ≥ 1 UNICODE_TAG_001 hit"
        assert "UNICODE_TAG_001" in _rule_ids(hits)

    def test_trigger_severity_is_high(self):
        """UNICODE_TAG_001 hits must have severity 'high'."""
        parsed = _parse("unicode_tag_trigger.md")
        hits = unicode_tag.check(parsed)
        for hit in hits:
            assert hit.severity == "high"

    def test_trigger_span_matches_parsed_spans(self):
        """Hit spans must match the unicode_tag_spans from parse.py exactly."""
        parsed = _parse("unicode_tag_trigger.md")
        assert len(parsed.unicode_tag_spans) >= 1, "Parse should have detected spans"
        hits = unicode_tag.check(parsed)
        hit_spans = {h.span for h in hits}
        parse_spans = set(parsed.unicode_tag_spans)
        assert (
            hit_spans == parse_spans
        ), f"Rule hit spans {hit_spans} don't match parsed spans {parse_spans}"

    def test_rule_does_not_rescan_raw_bytes(self):
        """unicode_tag.py must consume parsed.unicode_tag_spans, not re-scan raw bytes.

        The rule must not import 're' for scanning or iterate over raw_bytes itself.
        Detection already happened in parse.py (architecture.md §2.1).
        """
        import inspect

        source = inspect.getsource(unicode_tag)
        # Rule must not import 're' — there's nothing to search for here
        assert (
            "import re" not in source
        ), "unicode_tag.py must not import 're'; detection is done in parse.py"
        # Rule must not access raw_bytes directly
        assert "raw_bytes" not in source, (
            "unicode_tag.py must not read raw_bytes; it should only consume "
            "parsed.unicode_tag_spans populated by parse.py"
        )
        # Rule must consume unicode_tag_spans
        assert "unicode_tag_spans" in source, "unicode_tag.py must read parsed.unicode_tag_spans"

    def test_clean(self):
        """unicode_tag_clean.md must produce 0 UNICODE_TAG_001 hits."""
        parsed = _parse("unicode_tag_clean.md")
        hits = unicode_tag.check(parsed)
        assert len(hits) == 0, f"Expected no hits on clean fixture, got: {hits}"

    def test_clean_parse_has_no_spans(self):
        """The clean fixture must have no unicode_tag_spans after parsing."""
        parsed = _parse("unicode_tag_clean.md")
        assert (
            parsed.unicode_tag_spans == []
        ), f"Expected empty spans, got: {parsed.unicode_tag_spans}"


# ---------------------------------------------------------------------------
# SUSPICIOUS_DOMAIN rule
# ---------------------------------------------------------------------------


class TestSuspiciousDomainRule:
    def test_trigger_nonstandard_tld(self):
        """suspicious_domain_trigger.md must produce a SUSPICIOUS_DOMAIN_001 hit."""
        parsed = _parse("suspicious_domain_trigger.md")
        hits = suspicious_domain.check(parsed)
        tld_hits = [h for h in hits if h.rule_id == "SUSPICIOUS_DOMAIN_001"]
        assert len(tld_hits) >= 1, f"Expected SUSPICIOUS_DOMAIN_001 hit, got: {hits}"

    def test_trigger_raw_ip(self):
        """suspicious_domain_trigger.md must produce a SUSPICIOUS_DOMAIN_003 hit."""
        parsed = _parse("suspicious_domain_trigger.md")
        hits = suspicious_domain.check(parsed)
        ip_hits = [h for h in hits if h.rule_id == "SUSPICIOUS_DOMAIN_003"]
        assert len(ip_hits) >= 1, f"Expected SUSPICIOUS_DOMAIN_003 hit, got: {hits}"

    def test_trigger_dynamic_dns(self):
        """suspicious_domain_trigger.md must produce a SUSPICIOUS_DOMAIN_004 hit."""
        parsed = _parse("suspicious_domain_trigger.md")
        hits = suspicious_domain.check(parsed)
        ddns_hits = [h for h in hits if h.rule_id == "SUSPICIOUS_DOMAIN_004"]
        assert len(ddns_hits) >= 1, f"Expected SUSPICIOUS_DOMAIN_004 hit, got: {hits}"

    def test_trigger_severity_is_warn(self):
        """All SUSPICIOUS_DOMAIN hits must have severity 'warn'."""
        parsed = _parse("suspicious_domain_trigger.md")
        hits = suspicious_domain.check(parsed)
        for hit in hits:
            assert hit.severity == "warn", f"Expected warn, got {hit.severity!r}"

    def test_clean(self):
        """suspicious_domain_clean.md must produce 0 hits."""
        parsed = _parse("suspicious_domain_clean.md")
        hits = suspicious_domain.check(parsed)
        assert len(hits) == 0, f"Expected no hits on clean fixture, got: {hits}"

    def test_ip_address_detection(self):
        """Raw IP address URLs must produce SUSPICIOUS_DOMAIN_003, not DOMAIN_001."""
        parsed = _parse("suspicious_domain_trigger.md")
        hits = suspicious_domain.check(parsed)
        ip_hits = [h for h in hits if h.rule_id == "SUSPICIOUS_DOMAIN_003"]
        # The 192.168.1.254 URL should fire _003, not _001 (IP check short-circuits TLD check)
        assert len(ip_hits) >= 1
        for hit in ip_hits:
            assert "192.168.1.254" in hit.message or "IP" in hit.message.upper()


# ---------------------------------------------------------------------------
# PADDING rule
# ---------------------------------------------------------------------------


class TestPaddingRule:
    def test_trigger(self):
        """padding_trigger.md must produce ≥ 1 PADDING_001 hit."""
        parsed = _parse("padding_trigger.md")
        hits = padding.check(parsed)
        assert len(hits) >= 1, "Expected ≥ 1 PADDING_001 hit"
        assert "PADDING_001" in _rule_ids(hits)

    def test_trigger_severity_is_warn(self):
        """PADDING_001 hits must have severity 'warn'."""
        parsed = _parse("padding_trigger.md")
        hits = padding.check(parsed)
        for hit in hits:
            assert hit.severity == "warn"

    def test_trigger_message_contains_percentage(self):
        """The PADDING_001 message must report the padding percentage."""
        parsed = _parse("padding_trigger.md")
        hits = padding.check(parsed)
        assert len(hits) >= 1
        assert "%" in hits[0].message, f"Expected % in message: {hits[0].message!r}"

    def test_trigger_ratio_above_threshold(self):
        """padding_trigger.md must have a padding ratio ≥ 0.20."""
        from prompthound.parse import compute_padding_ratio

        parsed = _parse("padding_trigger.md")
        ratio = compute_padding_ratio(parsed.raw_bytes)
        assert ratio >= 0.20, f"Expected ratio ≥ 0.20, got {ratio:.3f}"

    def test_clean(self):
        """padding_clean.md must produce 0 PADDING_001 hits."""
        parsed = _parse("padding_clean.md")
        hits = padding.check(parsed)
        assert len(hits) == 0, f"Expected no hits on clean fixture, got: {hits}"

    def test_uses_shared_helper(self):
        """padding.py must import compute_padding_ratio from parse.py (not reimplement it)."""
        import inspect

        source = inspect.getsource(padding)
        assert (
            "compute_padding_ratio" in source
        ), "padding.py should call compute_padding_ratio from parse.py"
        assert (
            "from prompthound.parse import compute_padding_ratio" in source
        ), "padding.py should import compute_padding_ratio from parse.py"


# ---------------------------------------------------------------------------
# ALL_RULES integration over all Phase-2 parse fixtures
# ---------------------------------------------------------------------------


class TestAllRulesOverParseFixtures:
    """Run ALL_RULES over the Phase-2 parse fixtures to confirm no exceptions.

    Valid parse fixture → should run cleanly and produce a list.
    parse_ok=False fixtures → rules should still not raise (they'll just
    return empty lists since the parsed fields are empty defaults).
    """

    @pytest.mark.parametrize(
        "fixture_name",
        ["valid_skill.md"],
    )
    def test_all_rules_on_valid_parse_fixture(self, fixture_name: str):
        path = str(PARSE_FIXTURES / fixture_name)
        parsed = parse_skill(path)
        assert parsed.parse_ok, f"Expected {fixture_name} to parse successfully"
        for rule in ALL_RULES:
            result = rule(parsed)
            assert isinstance(result, list), f"{rule} returned {type(result)} on {fixture_name}"

    @pytest.mark.parametrize(
        "fixture_name",
        ["no_frontmatter.md", "empty_file.md", "binary_garbage.bin"],
    )
    def test_all_rules_on_failed_parse_fixture(self, fixture_name: str):
        """Rules must not raise even when parse_ok=False.

        The CLI won't call rules on failed parses, but rules must be
        defensively coded so they don't crash if called anyway.
        """
        path = str(PARSE_FIXTURES / fixture_name)
        parsed = parse_skill(path)
        assert not parsed.parse_ok, f"Expected {fixture_name} to fail parsing"
        for rule in ALL_RULES:
            # Must not raise; result is expected to be an empty list
            result = rule(parsed)
            assert isinstance(
                result, list
            ), f"{rule} returned {type(result)} on failed parse fixture {fixture_name}"

    def test_all_rules_combined_hit_list(self):
        """The one-liner from tech-implementation.md §4 must work without errors."""
        path = str(PARSE_FIXTURES / "valid_skill.md")
        parsed = parse_skill(path)
        assert parsed.parse_ok
        hits = [hit for rule in ALL_RULES for hit in rule(parsed)]
        assert isinstance(hits, list)
        for hit in hits:
            assert isinstance(hit, RuleHit)
