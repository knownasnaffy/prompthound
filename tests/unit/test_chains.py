"""Unit tests for the Capability-Chain Check (Phase 5).

Tests assert that:
  - An adjacent chain (all steps in one code block) is detected correctly.
  - A scattered chain (steps split across non-adjacent code blocks) is detected.
  - A benign file with no dangerous sequence returns an empty list (not an error).
  - A file with ``parse_ok=False`` returns an empty list without raising.
  - ``ChainFlag`` objects carry the expected shape: ``chain_name`` matches the
    DANGEROUS_CHAINS definition, and ``steps`` is a list of ``(str, int)`` pairs
    ordered by document position.
  - The ``_is_subsequence`` helper correctly returns ``None`` for a missing
    sequence and a list of matched events for a present one.
  - Structural constraints: ``chains.py`` reads only ``ParsedSkill``; it does
    not import ``RuleHit`` or ``FeatureVector``.

Architecture notes (architecture.md §2.5, AGENTS.md §5):
  - ``check_chains`` takes ``ParsedSkill`` directly, not ``FeatureVector``.
  - An empty ``chain_flags`` return is a valid benign outcome, not an error.
  - The chains stage must never see ``RuleHit`` objects.
"""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path

import pytest

from prompthound.chains import (
    DANGEROUS_CHAINS,
    _CapEvent,
    _extract_events,
    _is_subsequence,
    check_chains,
)
from prompthound.parse import parse_skill
from prompthound.schema import ChainFlag, ParsedSkill

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FIXTURES = Path(__file__).parent / "fixtures" / "chains"
PARSE_FIXTURES = Path(__file__).parent / "fixtures" / "parse"


def _parse(filename: str) -> ParsedSkill:
    """Parse a chains fixture and assert it succeeded."""
    path = str(FIXTURES / filename)
    parsed = parse_skill(path)
    assert parsed.parse_ok, f"Fixture {filename!r} failed to parse: {parsed.parse_error}"
    return parsed


def _chain_names(flags: list[ChainFlag]) -> set[str]:
    """Return the set of chain names from a list of ChainFlags."""
    return {f.chain_name for f in flags}


# ---------------------------------------------------------------------------
# Structural / contract tests
# ---------------------------------------------------------------------------


class TestContract:
    """Verify the hard constraints from architecture.md §2.5 and AGENTS.md §5."""

    def test_check_chains_accepts_only_parsed_skill(self) -> None:
        """``check_chains`` must accept a single ``ParsedSkill`` parameter."""
        sig = inspect.signature(check_chains)
        params = list(sig.parameters.values())
        assert len(params) == 1, "check_chains must take exactly one parameter"
        annotation = params[0].annotation
        if annotation is not inspect.Parameter.empty:
            assert annotation is ParsedSkill or annotation == "ParsedSkill"

    def test_chains_module_does_not_import_rulehit(self) -> None:
        """chains.py must not import RuleHit (architecture.md §2.5 hard constraint).

        The chains stage takes ``ParsedSkill`` directly; it must stay
        independent of the rule layer output.
        """
        chains_mod = importlib.import_module("prompthound.chains")
        for name, obj in vars(chains_mod).items():
            if name == "RuleHit" or (hasattr(obj, "__name__") and getattr(obj, "__name__", None) == "RuleHit"):
                pytest.fail(
                    f"chains.py imports/exposes RuleHit as attribute {name!r}; "
                    "chains stage must not depend on rule layer output."
                )

    def test_chains_module_does_not_import_feature_vector(self) -> None:
        """chains.py must not import FeatureVector (architecture.md §2.5).

        The chains stage reads ``ParsedSkill`` directly, not the numeric vector.
        """
        chains_mod = importlib.import_module("prompthound.chains")
        for name, obj in vars(chains_mod).items():
            if name == "FeatureVector" or (
                hasattr(obj, "__name__") and getattr(obj, "__name__", None) == "FeatureVector"
            ):
                pytest.fail(
                    f"chains.py imports/exposes FeatureVector as attribute {name!r}; "
                    "chains stage must not depend on feature vector."
                )

    def test_check_chains_returns_list(self) -> None:
        """``check_chains`` must always return a list (never None or an exception)."""
        parsed = _parse("chain_benign.md")
        result = check_chains(parsed)
        assert isinstance(result, list)

    def test_check_chains_returns_chain_flags(self) -> None:
        """Every element returned by ``check_chains`` must be a ``ChainFlag``."""
        parsed = _parse("chain_adjacent.md")
        flags = check_chains(parsed)
        for flag in flags:
            assert isinstance(flag, ChainFlag), f"Expected ChainFlag, got {type(flag)}"

    def test_dangerous_chains_nonempty(self) -> None:
        """DANGEROUS_CHAINS must define at least two sequences."""
        assert len(DANGEROUS_CHAINS) >= 2

    def test_dangerous_chains_structure(self) -> None:
        """Each entry in DANGEROUS_CHAINS must be a (str, list) tuple."""
        for entry in DANGEROUS_CHAINS:
            assert isinstance(entry, tuple) and len(entry) == 2
            name, sequence = entry
            assert isinstance(name, str) and name
            assert isinstance(sequence, list) and len(sequence) >= 2
            for step in sequence:
                assert isinstance(step, str) and step


# ---------------------------------------------------------------------------
# _is_subsequence unit tests
# ---------------------------------------------------------------------------


class TestIsSubsequence:
    """Tests for the internal greedy subsequence matcher."""

    def _make_events(self, caps_and_lines: list[tuple[str, int]]) -> list[_CapEvent]:
        """Build a sorted list of _CapEvent objects from (cap, line) pairs."""
        return [_CapEvent(cap=cap, line=line, source="body") for cap, line in caps_and_lines]

    def test_empty_sequence_returns_none(self) -> None:
        """An empty target sequence always returns None (no meaningful match)."""
        events = self._make_events([("file_read", 5), ("encode", 10)])
        assert _is_subsequence([], events) is None

    def test_empty_events_returns_none(self) -> None:
        """No events → no subsequence can be found."""
        assert _is_subsequence(["file_read", "encode"], []) is None

    def test_exact_match_single_step(self) -> None:
        """A single-step sequence matches if that cap is anywhere in events."""
        events = self._make_events([("file_read", 3)])
        result = _is_subsequence(["file_read"], events)
        assert result is not None
        assert len(result) == 1
        assert result[0].cap == "file_read"

    def test_adjacent_sequence_matches(self) -> None:
        """A 3-step sequence matches when all caps appear adjacent."""
        events = self._make_events([
            ("file_read", 5),
            ("encode", 6),
            ("network_send", 7),
        ])
        result = _is_subsequence(["file_read", "encode", "network_send"], events)
        assert result is not None
        assert [e.cap for e in result] == ["file_read", "encode", "network_send"]

    def test_scattered_sequence_matches(self) -> None:
        """A 3-step sequence matches when caps are non-adjacent in events."""
        events = self._make_events([
            ("file_read", 3),
            ("network", 8),
            ("encode", 15),
            ("network_send", 27),
        ])
        result = _is_subsequence(["file_read", "encode", "network_send"], events)
        assert result is not None
        assert [e.cap for e in result] == ["file_read", "encode", "network_send"]

    def test_missing_middle_step_returns_none(self) -> None:
        """Returns None when one step in the middle is absent."""
        events = self._make_events([
            ("file_read", 5),
            # "encode" is missing
            ("network_send", 20),
        ])
        result = _is_subsequence(["file_read", "encode", "network_send"], events)
        assert result is None

    def test_missing_first_step_returns_none(self) -> None:
        """Returns None when the first step is absent."""
        events = self._make_events([
            ("encode", 10),
            ("network_send", 20),
        ])
        result = _is_subsequence(["file_read", "encode", "network_send"], events)
        assert result is None

    def test_missing_last_step_returns_none(self) -> None:
        """Returns None when the final step is absent."""
        events = self._make_events([
            ("file_read", 5),
            ("encode", 10),
        ])
        result = _is_subsequence(["file_read", "encode", "network_send"], events)
        assert result is None

    def test_wrong_order_returns_none(self) -> None:
        """Returns None when the caps are present but out of document order."""
        # encode appears *before* file_read — wrong order for the chain.
        events = self._make_events([
            ("encode", 3),
            ("network_send", 6),
            ("file_read", 15),
        ])
        result = _is_subsequence(["file_read", "encode", "network_send"], events)
        assert result is None

    def test_matched_events_carry_line_numbers(self) -> None:
        """Each matched event must carry the correct line number."""
        events = self._make_events([
            ("file_read", 12),
            ("encode", 34),
            ("network_send", 56),
        ])
        result = _is_subsequence(["file_read", "encode", "network_send"], events)
        assert result is not None
        assert [e.line for e in result] == [12, 34, 56]

    def test_duplicate_cap_uses_earliest_remaining(self) -> None:
        """Greedy matching picks the earliest available match for each step."""
        # Two "encode" events; the first one (line 10) should be consumed.
        events = self._make_events([
            ("file_read", 5),
            ("encode", 10),
            ("encode", 18),
            ("network_send", 25),
        ])
        result = _is_subsequence(["file_read", "encode", "network_send"], events)
        assert result is not None
        # Greedy: should pick encode at line 10.
        assert result[1].line == 10


# ---------------------------------------------------------------------------
# _extract_events unit tests
# ---------------------------------------------------------------------------


class TestExtractEvents:
    """Tests for the event extraction function."""

    def test_extract_events_returns_list(self) -> None:
        """``_extract_events`` must return a list."""
        parsed = _parse("chain_benign.md")
        events = _extract_events(parsed)
        assert isinstance(events, list)

    def test_extract_events_sorted_by_line(self) -> None:
        """Events must be sorted by line number (ascending)."""
        parsed = _parse("chain_adjacent.md")
        events = _extract_events(parsed)
        lines = [e.line for e in events]
        assert lines == sorted(lines), "Events must be sorted by line number"

    def test_extract_events_from_frontmatter(self) -> None:
        """Declared capabilities in frontmatter must produce events at line 1."""
        parsed = _parse("chain_benign.md")
        events = _extract_events(parsed)
        frontmatter_events = [e for e in events if e.source == "frontmatter"]
        # chain_benign.md declares file_read and file_write.
        fm_caps = {e.cap for e in frontmatter_events}
        assert "file_read" in fm_caps or "file_write" in fm_caps
        for e in frontmatter_events:
            assert e.line == 1

    def test_extract_events_from_code_blocks(self) -> None:
        """Code block capability references must produce events with line > 1."""
        parsed = _parse("chain_adjacent.md")
        events = _extract_events(parsed)
        body_events = [e for e in events if e.source == "body"]
        assert len(body_events) > 0
        for e in body_events:
            assert e.line > 1, "Body events must have line number > 1"

    def test_no_duplicate_cap_line_pairs(self) -> None:
        """There must be no duplicate (cap, line) pairs in the event list."""
        parsed = _parse("chain_adjacent.md")
        events = _extract_events(parsed)
        pairs = [(e.cap, e.line) for e in events]
        assert len(pairs) == len(set(pairs)), "Duplicate (cap, line) pairs found"

    def test_empty_skill_produces_events_or_empty(self) -> None:
        """A benign skill produces events but must not form a complete dangerous chain.

        Individual dangerous-looking cap keywords (e.g. 'run', 'write') may appear
        in prose context without forming a full chain sequence.  The important contract
        is that check_chains returns [] — not that every cap is absent.
        """
        parsed = _parse("chain_benign.md")
        events = _extract_events(parsed)
        # Events must be a list — even if it's empty.
        assert isinstance(events, list)
        # The caps that do appear must not form a complete dangerous sequence.
        # (Verified more thoroughly by TestBenignChain — here we just assert
        # the event list is well-formed.)
        for e in events:
            assert isinstance(e.cap, str) and e.cap
            assert isinstance(e.line, int) and e.line >= 1


# ---------------------------------------------------------------------------
# check_chains — adjacent chain fixture
# ---------------------------------------------------------------------------


class TestAdjacentChain:
    """chain_adjacent.md — all three steps in one code block."""

    def test_adjacent_chain_detected(self) -> None:
        """The file_read→encode→network_send chain must be detected."""
        parsed = _parse("chain_adjacent.md")
        flags = check_chains(parsed)
        assert len(flags) > 0, "Expected at least one chain flag for chain_adjacent.md"

    def test_exfil_chain_name_present(self) -> None:
        """A flag with chain_name 'file_read→encode→network_send' must be present."""
        parsed = _parse("chain_adjacent.md")
        flags = check_chains(parsed)
        names = _chain_names(flags)
        assert "file_read→encode→network_send" in names, (
            f"Expected 'file_read→encode→network_send' in flags; got: {names}"
        )

    def test_steps_are_list_of_tuples(self) -> None:
        """Each ChainFlag.steps must be a list of (str, int) tuples."""
        parsed = _parse("chain_adjacent.md")
        flags = check_chains(parsed)
        for flag in flags:
            assert isinstance(flag.steps, list)
            for step in flag.steps:
                assert isinstance(step, tuple) and len(step) == 2
                cap, line = step
                assert isinstance(cap, str)
                assert isinstance(line, int)

    def test_steps_count_matches_sequence_length(self) -> None:
        """Steps list length must equal the number of steps in the matched sequence."""
        parsed = _parse("chain_adjacent.md")
        flags = check_chains(parsed)
        chain_defs = dict(DANGEROUS_CHAINS)
        for flag in flags:
            if flag.chain_name in chain_defs:
                expected_len = len(chain_defs[flag.chain_name])
                assert len(flag.steps) == expected_len, (
                    f"Flag {flag.chain_name!r}: expected {expected_len} steps, "
                    f"got {len(flag.steps)}"
                )

    def test_steps_ordered_by_line(self) -> None:
        """Steps within a ChainFlag must be in ascending line order."""
        parsed = _parse("chain_adjacent.md")
        flags = check_chains(parsed)
        for flag in flags:
            lines = [line for _, line in flag.steps]
            assert lines == sorted(lines), (
                f"Steps for {flag.chain_name!r} are not in line order: {lines}"
            )

    def test_step_caps_match_sequence_definition(self) -> None:
        """Step capability tags must match the sequence definition in DANGEROUS_CHAINS."""
        parsed = _parse("chain_adjacent.md")
        flags = check_chains(parsed)
        chain_defs = dict(DANGEROUS_CHAINS)
        for flag in flags:
            if flag.chain_name in chain_defs:
                expected_caps = chain_defs[flag.chain_name]
                actual_caps = [cap for cap, _ in flag.steps]
                assert actual_caps == expected_caps, (
                    f"Steps caps for {flag.chain_name!r}: expected {expected_caps}, "
                    f"got {actual_caps}"
                )

    def test_adjacent_chain_line_numbers_positive(self) -> None:
        """All step line numbers must be positive integers."""
        parsed = _parse("chain_adjacent.md")
        flags = check_chains(parsed)
        for flag in flags:
            for cap, line in flag.steps:
                assert line >= 1, f"Step ({cap!r}, {line}) has non-positive line number"


# ---------------------------------------------------------------------------
# check_chains — scattered chain fixture
# ---------------------------------------------------------------------------


class TestScatteredChain:
    """chain_scattered.md — chain steps split across non-adjacent code blocks."""

    def test_scattered_chain_detected(self) -> None:
        """The chain must be detected even when steps are in separate code blocks."""
        parsed = _parse("chain_scattered.md")
        flags = check_chains(parsed)
        assert len(flags) > 0, "Expected at least one chain flag for chain_scattered.md"

    def test_scattered_exfil_chain_name_present(self) -> None:
        """A flag for the exfil or file_read→network_send chain must be present."""
        parsed = _parse("chain_scattered.md")
        flags = check_chains(parsed)
        names = _chain_names(flags)
        # Accept either the full 3-step or the 2-step variant.
        assert (
            "file_read→encode→network_send" in names
            or "file_read→network_send" in names
        ), f"Expected an exfil chain flag; got: {names}"

    def test_steps_span_multiple_lines(self) -> None:
        """For a scattered chain, step line numbers must not all be equal
        (they come from different code blocks)."""
        parsed = _parse("chain_scattered.md")
        flags = check_chains(parsed)
        # Find the exfil chain flag.
        exfil_flags = [
            f for f in flags
            if "file_read" in f.chain_name
        ]
        assert exfil_flags, "No file_read-based chain flag found"
        flag = exfil_flags[0]
        lines = [line for _, line in flag.steps]
        # At least two distinct line numbers (steps are in different blocks).
        assert len(set(lines)) > 1, (
            f"Expected scattered chain steps on different lines; got lines: {lines}"
        )

    def test_scattered_steps_ordered_ascending(self) -> None:
        """Scattered chain steps must still be in ascending line order."""
        parsed = _parse("chain_scattered.md")
        flags = check_chains(parsed)
        for flag in flags:
            lines = [line for _, line in flag.steps]
            assert lines == sorted(lines), (
                f"Steps for {flag.chain_name!r} not in ascending order: {lines}"
            )


# ---------------------------------------------------------------------------
# check_chains — benign fixture (no dangerous chain)
# ---------------------------------------------------------------------------


class TestBenignChain:
    """chain_benign.md — file_read + file_write only; no dangerous sequence."""

    def test_benign_returns_empty_list(self) -> None:
        """check_chains must return [] for a benign file — not an error."""
        parsed = _parse("chain_benign.md")
        flags = check_chains(parsed)
        assert flags == [], (
            f"Expected [] for benign file; got: {[f.chain_name for f in flags]}"
        )

    def test_benign_no_exfil_chain(self) -> None:
        """No exfiltration chain should be detected in a local file_read+write skill."""
        parsed = _parse("chain_benign.md")
        flags = check_chains(parsed)
        names = _chain_names(flags)
        assert "file_read→encode→network_send" not in names
        assert "file_read→network_send" not in names

    def test_benign_no_download_execute_chain(self) -> None:
        """No download→execute chain should be detected in the benign fixture."""
        parsed = _parse("chain_benign.md")
        flags = check_chains(parsed)
        names = _chain_names(flags)
        assert "download→execute" not in names
        assert "download→write→execute" not in names


# ---------------------------------------------------------------------------
# check_chains — parse failure short-circuit
# ---------------------------------------------------------------------------


class TestParseFailureHandling:
    """check_chains must return [] when ``parse_ok=False`` (architecture.md §4)."""

    def test_failed_parse_returns_empty_list(self) -> None:
        """A ``ParsedSkill`` with ``parse_ok=False`` must return [] without raising."""
        path = str(PARSE_FIXTURES / "empty_file.md")
        parsed = parse_skill(path)
        assert parsed.parse_ok is False
        result = check_chains(parsed)
        assert result == [], f"Expected [] for failed parse; got: {result}"

    def test_binary_garbage_returns_empty_list(self) -> None:
        """Binary garbage (parse_ok=False) must return [] without raising."""
        path = str(PARSE_FIXTURES / "binary_garbage.bin")
        parsed = parse_skill(path)
        assert parsed.parse_ok is False
        result = check_chains(parsed)
        assert result == []

    def test_no_frontmatter_returns_empty_list(self) -> None:
        """A file with no frontmatter (parse_ok=False) must return [] without raising."""
        path = str(PARSE_FIXTURES / "no_frontmatter.md")
        parsed = parse_skill(path)
        assert parsed.parse_ok is False
        result = check_chains(parsed)
        assert result == []


# ---------------------------------------------------------------------------
# check_chains — running against all parse fixtures (robustness)
# ---------------------------------------------------------------------------


class TestRobustness:
    """Running check_chains over various inputs must never raise an exception."""

    @pytest.mark.parametrize("filename", [
        "chain_adjacent.md",
        "chain_scattered.md",
        "chain_benign.md",
    ])
    def test_no_exception_on_chain_fixtures(self, filename: str) -> None:
        """check_chains must not raise for any chain fixture."""
        parsed = _parse(filename)
        result = check_chains(parsed)
        assert isinstance(result, list)

    def test_chain_flag_steps_never_empty_for_detected_chain(self) -> None:
        """Every ChainFlag returned by check_chains must have at least one step."""
        for filename in ("chain_adjacent.md", "chain_scattered.md"):
            parsed = _parse(filename)
            flags = check_chains(parsed)
            for flag in flags:
                assert flag.steps, (
                    f"ChainFlag {flag.chain_name!r} in {filename!r} has empty steps"
                )
