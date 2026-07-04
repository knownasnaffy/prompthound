"""Integration snapshot tests for prompthound/report.py.

Tests all three renderers (render_human, render_json, render_sarif) over all
six ScanResult fixture cases:
  - clean
  - rule_only
  - classifier_only
  - chain_only
  - all_three
  - parse_fail

Snapshot mechanism
------------------
Snapshots are stored as plain text files under::

    tests/integration/snapshots/<fixture_name>__<renderer>.txt

On first run (or when ``--snapshot-update`` is passed to pytest), the test
writes the current rendered output as the reference snapshot.  On subsequent
runs, the rendered output is compared against the stored snapshot character-
by-character; any diff causes the test to fail with a clear message showing
what changed.

To regenerate all snapshots after an intentional output change::

    pytest tests/integration --snapshot-update

Separation-of-evidence invariant (architecture.md §2.6, AGENTS.md §5)
----------------------------------------------------------------------
An explicit structural test verifies that the three evidence sections are
present and disjoint:
  - human output: the three section headers appear in order and are never merged
  - JSON output: the top-level keys ``rule_hits``, ``classifier``,
    ``chain_flags`` are always present and never collapsed
  - SARIF output: ruleId namespaces PH0xx / PH1xx / PH2xx appear only in their
    expected sections, never mixed
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from prompthound.report import render_human, render_json, render_sarif
from tests.integration.fixtures_reporter import (
    fixture_all_three,
    fixture_chain_only,
    fixture_classifier_only,
    fixture_clean,
    fixture_parse_fail,
    fixture_rule_only,
)

# ── Snapshot helpers ───────────────────────────────────────────────────────────

_SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


def _snapshot_path(fixture_name: str, renderer: str) -> Path:
    return _SNAPSHOT_DIR / f"{fixture_name}__{renderer}.txt"


def _assert_snapshot(
    rendered: str,
    fixture_name: str,
    renderer: str,
    update: bool,
) -> None:
    """Compare ``rendered`` against its stored snapshot.

    If ``update`` is True (``--snapshot-update`` flag), write the new content
    instead of comparing.
    """
    snap_path = _snapshot_path(fixture_name, renderer)

    if update or not snap_path.exists():
        snap_path.parent.mkdir(parents=True, exist_ok=True)
        snap_path.write_text(rendered, encoding="utf-8")
        return  # first write is always a pass

    expected = snap_path.read_text(encoding="utf-8")
    if rendered != expected:
        # Build a human-readable diff for the failure message
        import difflib

        diff_lines = list(
            difflib.unified_diff(
                expected.splitlines(keepends=True),
                rendered.splitlines(keepends=True),
                fromfile=f"snapshot/{snap_path.name}",
                tofile=f"rendered/{snap_path.name}",
                n=4,
            )
        )
        diff_str = "".join(diff_lines)
        pytest.fail(
            f"Snapshot mismatch for {fixture_name}/{renderer}.\n"
            f"Run 'pytest tests/integration --snapshot-update' to update.\n\n"
            f"{diff_str}"
        )


@pytest.fixture
def snapshot_update(request: pytest.FixtureRequest) -> bool:
    """Return True if ``--snapshot-update`` was passed on the command line."""
    return request.config.getoption("--snapshot-update", default=False)


# ── Parametrized snapshot test ─────────────────────────────────────────────────

_FIXTURES = {
    "clean": fixture_clean,
    "rule_only": fixture_rule_only,
    "classifier_only": fixture_classifier_only,
    "chain_only": fixture_chain_only,
    "all_three": fixture_all_three,
    "parse_fail": fixture_parse_fail,
}

_RENDERERS = {
    "human": render_human,
    "json": render_json,
    "sarif": render_sarif,
}


@pytest.mark.parametrize("fixture_name", list(_FIXTURES.keys()))
@pytest.mark.parametrize("renderer_name", list(_RENDERERS.keys()))
def test_snapshot(
    fixture_name: str,
    renderer_name: str,
    snapshot_update: bool,
) -> None:
    """Render each fixture with each renderer; compare or write the snapshot."""
    result = _FIXTURES[fixture_name]()
    renderer = _RENDERERS[renderer_name]
    rendered = renderer(result)

    assert isinstance(rendered, str), (
        f"{renderer_name} must return a string, got {type(rendered)}"
    )
    assert len(rendered) > 0, f"{renderer_name} must return non-empty output"

    _assert_snapshot(rendered, fixture_name, renderer_name, snapshot_update)


# ── Separation-of-evidence invariant tests ────────────────────────────────────
#
# These tests are independent of snapshots.  They assert structural properties
# that must hold for ANY valid ScanResult, not just the specific snapshot values.
# If render_human / render_json / render_sarif ever flatten the three evidence
# types together, these tests will catch it.
#
# The invariant tested: with a result that has *all three* evidence types,
# each evidence type must appear in its own dedicated section / key / ruleId
# namespace — and not bleed into another section.


class TestHumanSeparation:
    """render_human keeps the three sections distinct and in order."""

    def test_three_section_headers_present(self) -> None:
        output = render_human(fixture_all_three())
        assert "RULE HITS" in output
        assert "CLASSIFIER" in output
        assert "CAPABILITY CHAINS" in output

    def test_section_order_is_rules_classifier_chains(self) -> None:
        output = render_human(fixture_all_three())
        pos_rules = output.index("RULE HITS")
        pos_classifier = output.index("CLASSIFIER")
        pos_chains = output.index("CAPABILITY CHAINS")
        assert pos_rules < pos_classifier < pos_chains, (
            "Sections must appear in order: RULE HITS < CLASSIFIER < CAPABILITY CHAINS"
        )

    def test_rule_hit_content_not_in_classifier_section(self) -> None:
        """SHELL_PIPE_001 rule id must not appear after the CLASSIFIER header."""
        output = render_human(fixture_all_three())
        classifier_section_start = output.index("── CLASSIFIER")
        chains_section_start = output.index("── CAPABILITY CHAINS")
        classifier_section = output[classifier_section_start:chains_section_start]
        assert "SHELL_PIPE_001" not in classifier_section, (
            "Rule hit IDs must not bleed into the CLASSIFIER section"
        )

    def test_chain_content_not_in_rule_section(self) -> None:
        """Chain names must not appear in the RULE HITS section."""
        output = render_human(fixture_all_three())
        rule_section_end = output.index("── CLASSIFIER")
        rule_section = output[:rule_section_end]
        assert "file_read→encode→network_send" not in rule_section, (
            "Chain names must not bleed into the RULE HITS section"
        )

    def test_classifier_content_not_in_chains_section(self) -> None:
        """Score / decision-path content must not appear in the CAPABILITY CHAINS section."""
        output = render_human(fixture_all_three())
        chains_section_start = output.index("── CAPABILITY CHAINS")
        chains_section = output[chains_section_start:]
        assert "Score" not in chains_section, (
            "Classifier score line must not appear in CAPABILITY CHAINS section"
        )

    def test_parse_fail_shows_error_not_analysis(self) -> None:
        """Parse failure renders an error message, never fake analysis sections."""
        output = render_human(fixture_parse_fail())
        assert "[ERROR]" in output
        assert "No further analysis performed" in output
        # We must NOT show fake rule/classifier/chain sections for a failed parse
        assert "RULE HITS" not in output
        assert "CLASSIFIER (ML risk score)" not in output
        assert "CAPABILITY CHAINS" not in output

    def test_clean_file_shows_no_hits(self) -> None:
        output = render_human(fixture_clean())
        assert "No rule hits" in output
        assert "No dangerous capability chains" in output

    def test_rule_only_has_no_classifier_score(self) -> None:
        output = render_human(fixture_rule_only())
        assert "Classifier not run" in output

    def test_chain_only_has_no_rule_hits(self) -> None:
        output = render_human(fixture_chain_only())
        assert "No rule hits" in output

    def test_chain_only_has_no_classifier_score(self) -> None:
        output = render_human(fixture_chain_only())
        assert "Classifier not run" in output

    def test_chain_only_shows_chain_name(self) -> None:
        output = render_human(fixture_chain_only())
        assert "file_read→encode→network_send" in output


class TestJsonSeparation:
    """render_json keeps the three evidence keys at the top level, never merged."""

    def _parsed(self, fixture_name: str) -> dict:
        result = _FIXTURES[fixture_name]()
        return json.loads(render_json(result))

    def test_top_level_keys_always_present_for_valid_parse(self) -> None:
        for name in ("clean", "rule_only", "classifier_only", "chain_only", "all_three"):
            doc = self._parsed(name)
            assert "rule_hits" in doc, f"{name}: missing 'rule_hits' key"
            assert "classifier" in doc, f"{name}: missing 'classifier' key"
            assert "chain_flags" in doc, f"{name}: missing 'chain_flags' key"

    def test_top_level_keys_for_parse_fail(self) -> None:
        doc = self._parsed("parse_fail")
        assert "parse_error" in doc
        # still present — just empty
        assert "rule_hits" in doc
        assert "classifier" in doc
        assert "chain_flags" in doc

    def test_rule_hits_is_a_list(self) -> None:
        doc = self._parsed("all_three")
        assert isinstance(doc["rule_hits"], list)

    def test_chain_flags_is_a_list(self) -> None:
        doc = self._parsed("all_three")
        assert isinstance(doc["chain_flags"], list)

    def test_classifier_is_dict_when_present(self) -> None:
        doc = self._parsed("classifier_only")
        assert isinstance(doc["classifier"], dict)

    def test_classifier_is_null_when_absent(self) -> None:
        doc = self._parsed("rule_only")
        assert doc["classifier"] is None

    def test_rule_hit_fields(self) -> None:
        doc = self._parsed("rule_only")
        hit = doc["rule_hits"][0]
        assert "rule_id" in hit
        assert "severity" in hit
        assert "span" in hit
        assert "message" in hit

    def test_classifier_dict_has_required_keys(self) -> None:
        doc = self._parsed("classifier_only")
        cls = doc["classifier"]
        assert "score" in cls
        assert "label" in cls
        assert "feature_importances" in cls

    def test_feature_importances_not_in_rule_hits(self) -> None:
        doc = self._parsed("all_three")
        for hit in doc["rule_hits"]:
            assert "feature_importances" not in hit, (
                "feature_importances must not appear inside rule_hits entries"
            )

    def test_chain_step_fields(self) -> None:
        doc = self._parsed("chain_only")
        flag = doc["chain_flags"][0]
        assert "chain_name" in flag
        assert "steps" in flag
        step = flag["steps"][0]
        assert "capability" in step
        assert "line" in step

    def test_rule_hits_not_inside_classifier(self) -> None:
        doc = self._parsed("all_three")
        cls = doc["classifier"]
        assert "rule_hits" not in cls, (
            "rule_hits must not be nested inside the classifier object"
        )

    def test_chain_flags_not_inside_classifier(self) -> None:
        doc = self._parsed("all_three")
        cls = doc["classifier"]
        assert "chain_flags" not in cls, (
            "chain_flags must not be nested inside the classifier object"
        )

    def test_output_is_valid_json(self) -> None:
        for name in _FIXTURES:
            result = _FIXTURES[name]()
            rendered = render_json(result)
            # Should not raise
            doc = json.loads(rendered)
            assert isinstance(doc, dict)


class TestSarifSeparation:
    """render_sarif keeps PH0xx / PH1xx / PH2xx ruleIds in their namespaces."""

    def _sarif(self, fixture_name: str) -> dict:
        result = _FIXTURES[fixture_name]()
        return json.loads(render_sarif(result))

    def _run(self, fixture_name: str) -> dict:
        return self._sarif(fixture_name)["runs"][0]

    def test_sarif_schema_and_version(self) -> None:
        sarif = self._sarif("clean")
        assert sarif["version"] == "2.1.0"
        assert "$schema" in sarif

    def test_sarif_structure(self) -> None:
        sarif = self._sarif("clean")
        assert "runs" in sarif
        run = sarif["runs"][0]
        assert "tool" in run
        assert "results" in run
        assert "artifacts" in run

    def test_rule_hits_use_ph0xx_namespace(self) -> None:
        run = self._run("rule_only")
        for result in run["results"]:
            assert result["ruleId"].startswith("PH0"), (
                f"Rule hit result must have PH0xx ruleId, got {result['ruleId']}"
            )

    def test_classifier_uses_ph1xx_namespace(self) -> None:
        run = self._run("classifier_only")
        rule_ids = [r["ruleId"] for r in run["results"]]
        assert any(rid.startswith("PH1") for rid in rule_ids), (
            "Classifier result must have PH1xx ruleId"
        )

    def test_chain_flags_use_ph2xx_namespace(self) -> None:
        run = self._run("chain_only")
        rule_ids = [r["ruleId"] for r in run["results"]]
        assert any(rid.startswith("PH2") for rid in rule_ids), (
            "Chain flag result must have PH2xx ruleId"
        )

    def test_all_three_namespaces_present_in_all_three(self) -> None:
        run = self._run("all_three")
        rule_ids = [r["ruleId"] for r in run["results"]]
        ph0 = [rid for rid in rule_ids if rid.startswith("PH0")]
        ph1 = [rid for rid in rule_ids if rid.startswith("PH1")]
        ph2 = [rid for rid in rule_ids if rid.startswith("PH2")]
        assert ph0, "Expected at least one PH0xx result for rule hits"
        assert ph1, "Expected at least one PH1xx result for classifier"
        assert ph2, "Expected at least one PH2xx result for chain flags"

    def test_rule_hit_results_have_evidence_type_property(self) -> None:
        run = self._run("rule_only")
        for result in run["results"]:
            assert result.get("properties", {}).get("evidenceType") == "rule-hit", (
                "Rule hit SARIF results must have evidenceType='rule-hit'"
            )

    def test_classifier_result_has_evidence_type_property(self) -> None:
        run = self._run("classifier_only")
        for result in run["results"]:
            assert result.get("properties", {}).get("evidenceType") == "classifier", (
                "Classifier SARIF result must have evidenceType='classifier'"
            )

    def test_chain_result_has_evidence_type_property(self) -> None:
        run = self._run("chain_only")
        for result in run["results"]:
            assert result.get("properties", {}).get("evidenceType") == "capability-chain", (
                "Chain SARIF result must have evidenceType='capability-chain'"
            )

    def test_ph0xx_result_not_in_ph1xx_namespace(self) -> None:
        run = self._run("all_three")
        for result in run["results"]:
            rid = result["ruleId"]
            ev_type = result.get("properties", {}).get("evidenceType", "")
            if rid.startswith("PH0"):
                assert ev_type == "rule-hit", (
                    f"PH0xx ruleId must have evidenceType='rule-hit', got '{ev_type}'"
                )
            if rid.startswith("PH1"):
                assert ev_type == "classifier", (
                    f"PH1xx ruleId must have evidenceType='classifier', got '{ev_type}'"
                )
            if rid.startswith("PH2"):
                assert ev_type == "capability-chain", (
                    f"PH2xx ruleId must have evidenceType='capability-chain', got '{ev_type}'"
                )

    def test_parse_fail_uses_ph000(self) -> None:
        run = self._run("parse_fail")
        rule_ids = [r["ruleId"] for r in run["results"]]
        assert any(rid.startswith("PH000") for rid in rule_ids), (
            "Parse failure must produce a PH000/parse-error result"
        )

    def test_clean_file_has_benign_classifier_level(self) -> None:
        run = self._run("clean")
        classifier_results = [
            r for r in run["results"] if r["ruleId"].startswith("PH1")
        ]
        assert len(classifier_results) == 1
        assert classifier_results[0]["level"] == "note", (
            "Benign classifier score must map to SARIF level 'note'"
        )

    def test_malicious_label_maps_to_error_level(self) -> None:
        run = self._run("classifier_only")
        classifier_results = [
            r for r in run["results"] if r["ruleId"].startswith("PH1")
        ]
        assert len(classifier_results) == 1
        assert classifier_results[0]["level"] == "error", (
            "Malicious classifier label must map to SARIF level 'error'"
        )

    def test_output_is_valid_json(self) -> None:
        for name in _FIXTURES:
            result = _FIXTURES[name]()
            rendered = render_sarif(result)
            doc = json.loads(rendered)
            assert isinstance(doc, dict)

    def test_rules_in_tool_driver_match_results(self) -> None:
        """Every ruleId referenced in results must have a descriptor in tool.driver.rules."""
        run = self._run("all_three")
        driver_rule_ids = {r["id"] for r in run["tool"]["driver"]["rules"]}
        for result in run["results"]:
            assert result["ruleId"] in driver_rule_ids, (
                f"ruleId '{result['ruleId']}' has no descriptor in tool.driver.rules"
            )
