import click
import json
import sys
from pathlib import Path

from .flatten import flatten_bundle, flatten_single
from .pipeline import run_pipeline
from .reporter import format_report

@click.group()
def main():
    """PromptHound: Static risk analysis for AI agent skill files."""
    pass

@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('-d', '--directory', is_flag=True, help='Scan a bundle directory recursively')
@click.option('--format', type=click.Choice(['human', 'json', 'sarif']), default='human', help='Output format')
def scan(path, directory, format):
    """Scan a skill file or bundle for risks."""
    path_obj = Path(path)
    
    if directory and not path_obj.is_dir():
        click.echo("Error: -d flag used but path is not a directory.", err=True)
        sys.exit(1)
    
    if not directory and path_obj.is_dir():
        click.echo("Error: Path is a directory but -d flag not provided.", err=True)
        sys.exit(1)
        
    click.echo(f"Scanning {'bundle' if directory else 'file'}: {path} (format: {format})")
    
    if directory:
        buffer, manifest = flatten_bundle(path_obj)
    else:
        buffer, manifest = flatten_single(path_obj)
    
    result = run_pipeline(buffer, manifest, is_bundle=directory)
    report = format_report(result, manifest, fmt=format)
    click.echo(report)

if __name__ == '__main__':
    main()
