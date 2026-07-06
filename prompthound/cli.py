"""CLI entry point for PromptHound.

Stage: CLI (Stage 0 of architecture.md §1) — thin click wrapper, no business logic.

Pipeline (architecture.md §1):
    File → Parse → [Rules ∥ Features→Classifier] → Chains → Reporter → Output

The CLI assembles a ``ScanResult`` from stage outputs and hands it to the
Reporter.  No stage writes to disk, and ``scan`` makes zero network calls
(AGENTS.md §2, §5).
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from prompthound.schema import ScanResult


@click.group()
def cli() -> None:
    """PromptHound — static risk analysis for AI agent skill files."""


@cli.command()
@click.argument("path", type=click.Path(exists=True, readable=True))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json", "sarif"]),
    default="human",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--fail-on",
    "fail_on",
    type=click.Choice(["suspicious", "malicious"]),
    default=None,
    help="Exit with nonzero status if risk meets this threshold (CI use).",
)
@click.option(
    "-d", "--directory",
    is_flag=True,
    help="Treat path as a directory bundle and recursively scan its contents.",
)
def scan(path: str, output_format: str, fail_on: str | None, directory: bool) -> None:
    """Scan a skill file for risk signals."""
    from prompthound.chains import check_chains
    from prompthound.classifier.model import classify
    from prompthound.features import extract_features
    from prompthound.parse import parse_skill
    from prompthound.rules import ALL_RULES
    from prompthound.schema import ScanResult

    # ── Stage 1: Parse ────────────────────────────────────────────────────────
    if directory:
        from prompthound.flatten import parse_directory
        parsed = parse_directory(path)
    else:
        from prompthound.parse import parse_skill
        parsed = parse_skill(path)

    # ── Malformed-file short-circuit (architecture.md §4) ─────────────────────
    # If parse_ok is False, skip every downstream stage and go straight to the
    # reporter with a "could not parse" result — never produce a misleadingly
    # low risk score from a garbage ParsedSkill.
    if not parsed.parse_ok:
        result = ScanResult(parsed=parsed)
        _render_and_exit(result, output_format, fail_on)
        return  # unreachable, but keeps the type checker happy

    # ── Stage 2a: Rule layer (side-channel, parallel with features) ───────────
    rule_hits = [hit for rule in ALL_RULES for hit in rule(parsed)]

    # ── Stage 2b: Feature extraction → Stage 3: Classifier ───────────────────
    features = extract_features(parsed)
    risk = classify(features)

    # ── Stage 4: Capability-chain check ───────────────────────────────────────
    chain_flags = check_chains(parsed)

    # ── Assemble ScanResult ──────────────────────────────────────────────────
    result = ScanResult(
        parsed=parsed,
        rule_hits=rule_hits,
        features=features,
        risk=risk,
        chain_flags=chain_flags,
    )

    _render_and_exit(result, output_format, fail_on)


# ── Severity ordering for --fail-on ──────────────────────────────────────────
_SEVERITY_RANK: dict[str, int] = {
    "benign": 0,
    "suspicious": 1,
    "malicious": 2,
}


def _render_and_exit(
    result: ScanResult,
    output_format: str,
    fail_on: str | None,
) -> None:
    """Render the result to stdout and exit with the correct code.

    Exit-code logic (architecture.md §3):
      - If ``--fail-on`` is set and the classifier produced a label at or above
        the threshold severity, exit with code 1.
      - If the file could not be parsed, the classifier label is absent; treat
        parse failures as *not* triggering ``--fail-on`` (there is no risk
        score to judge against).
      - Otherwise exit 0.
    """
    from prompthound.report import render_human, render_json, render_sarif

    renderers = {
        "human": render_human,
        "json": render_json,
        "sarif": render_sarif,
    }
    output = renderers[output_format](result)
    click.echo(output)

    # ── --fail-on exit-code logic ────────────────────────────────────────────
    if fail_on is not None and result.risk is not None:
        threshold = _SEVERITY_RANK.get(fail_on, 1)
        actual = _SEVERITY_RANK.get(result.risk.label, 0)
        if actual >= threshold:
            sys.exit(1)

    sys.exit(0)
