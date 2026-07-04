"""CLI entry point for PromptHound.

Stage: CLI (Stage 0 of architecture.md §1) — thin click wrapper, no business logic.
"""
import click


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
def scan(path: str, output_format: str, fail_on: str | None) -> None:
    """Scan a skill file for risk signals."""
    raise NotImplementedError("scan command not yet implemented")
