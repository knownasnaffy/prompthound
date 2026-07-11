import click
import sys
from pathlib import Path
from rich.console import Console

from .flatten import flatten_bundle, flatten_single
from .pipeline import run_pipeline
from .reporter import format_report
from .config import KNOWN_SKILL_DIRS

console = Console()


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
        console.print(
            f"Scanning project for known skill directories... (format: {format})"
        )
        found_any = False
        cwd = Path.cwd()
        for known_dir in KNOWN_SKILL_DIRS:
            target_dir = cwd / known_dir
            if target_dir.exists() and target_dir.is_dir():
                console.print(
                    f"\nFound skill directory: [bold blue]{known_dir}[/bold blue]"
                )
                found_any = True

                # Scan immediate children
                for item in target_dir.iterdir():
                    if item.is_dir():
                        console.print(
                            f"\n-> Scanning bundle: [bold cyan]{item.relative_to(cwd)}[/bold cyan]"
                        )
                        buffer, manifest = flatten_bundle(item)
                        result = run_pipeline(buffer, manifest, is_bundle=True)
                        report = format_report(result, manifest, fmt=format)
                        if format == "human":
                            console.print(report)
                        else:
                            click.echo(report)
                    elif item.suffix == ".md":
                        console.print(
                            f"\n-> Scanning file: [bold cyan]{item.relative_to(cwd)}[/bold cyan]"
                        )
                        buffer, manifest = flatten_single(item)
                        result = run_pipeline(buffer, manifest, is_bundle=False)
                        report = format_report(result, manifest, fmt=format)
                        if format == "human":
                            console.print(report)
                        else:
                            click.echo(report)
        if not found_any:
            console.print(
                "[yellow]No known skill directories found in this project.[/yellow]"
            )
        return

    if not path:
        console.print(
            "[bold red]Error: Missing argument 'PATH' when not using -p.[/bold red]",
            style="red",
        )
        sys.exit(1)

    path_obj = Path(path)

    if directory and not path_obj.is_dir():
        console.print(
            "[bold red]Error: -d flag used but path is not a directory.[/bold red]",
            style="red",
        )
        sys.exit(1)

    if not directory and path_obj.is_dir():
        console.print(
            "[bold red]Error: Path is a directory but -d flag not provided.[/bold red]",
            style="red",
        )
        sys.exit(1)

    console.print(
        f"Scanning {'bundle' if directory else 'file'}: [bold cyan]{path}[/bold cyan] (format: {format})"
    )

    if directory:
        buffer, manifest = flatten_bundle(path_obj)
    else:
        buffer, manifest = flatten_single(path_obj)

    result = run_pipeline(buffer, manifest, is_bundle=directory)
    report = format_report(result, manifest, fmt=format)
    if format == "human":
        console.print(report)
    else:
        click.echo(report)


if __name__ == "__main__":
    main()
