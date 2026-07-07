import click
import json
import sys
from pathlib import Path

import os
from .flatten import flatten_bundle, flatten_single
from .pipeline import run_pipeline
from .reporter import format_report
from .config import KNOWN_SKILL_DIRS


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """PromptHound: Static risk analysis for AI agent skill files."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument("path", type=click.Path(exists=True), required=False)
@click.option(
    "-d", "--directory", is_flag=True, help="Scan a bundle directory recursively"
)
@click.option(
    "-p",
    "--project",
    is_flag=True,
    help="Scan the current project based on known skill directories",
)
@click.option(
    "--format",
    type=click.Choice(["human", "json", "sarif"]),
    default="human",
    help="Output format",
)
def scan(path, directory, project, format):
    """Scan a skill file or bundle for risks."""
    if project:
        click.echo(
            f"Scanning project for known skill directories... (format: {format})"
        )
        found_any = False
        cwd = Path.cwd()
        for known_dir in KNOWN_SKILL_DIRS:
            target_dir = cwd / known_dir
            if target_dir.exists() and target_dir.is_dir():
                click.echo(f"\nFound skill directory: {known_dir}")
                found_any = True

                # Scan immediate children
                for item in target_dir.iterdir():
                    if item.is_dir():
                        click.echo(f"\n-> Scanning bundle: {item.relative_to(cwd)}")
                        buffer, manifest = flatten_bundle(item)
                        result = run_pipeline(buffer, manifest, is_bundle=True)
                        click.echo(format_report(result, manifest, fmt=format))
                    elif item.suffix == ".md":
                        click.echo(f"\n-> Scanning file: {item.relative_to(cwd)}")
                        buffer, manifest = flatten_single(item)
                        result = run_pipeline(buffer, manifest, is_bundle=False)
                        click.echo(format_report(result, manifest, fmt=format))
        if not found_any:
            click.echo("No known skill directories found in this project.")
        return

    if not path:
        click.echo("Error: Missing argument 'PATH' when not using -p.", err=True)
        sys.exit(1)

    path_obj = Path(path)

    if directory and not path_obj.is_dir():
        click.echo("Error: -d flag used but path is not a directory.", err=True)
        sys.exit(1)

    if not directory and path_obj.is_dir():
        click.echo("Error: Path is a directory but -d flag not provided.", err=True)
        sys.exit(1)

    click.echo(
        f"Scanning {'bundle' if directory else 'file'}: {path} (format: {format})"
    )

    if directory:
        buffer, manifest = flatten_bundle(path_obj)
    else:
        buffer, manifest = flatten_single(path_obj)

    result = run_pipeline(buffer, manifest, is_bundle=directory)
    report = format_report(result, manifest, fmt=format)
    click.echo(report)


if __name__ == "__main__":
    main()
