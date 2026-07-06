"""Integration tests for the full CLI scan pipeline."""

import difflib
from pathlib import Path
import pytest
from click.testing import CliRunner

from prompthound.cli import cli

_ROOT_DIR = Path(__file__).parent.parent.parent
_BENIGN_FILE = _ROOT_DIR / "benchmark" / "corpus" / "benign" / "case_00000"
_MALICIOUS_FILE = _ROOT_DIR / "benchmark" / "corpus" / "malicious" / "case_00001"
_MALFORMED_FILE = _ROOT_DIR / "tests" / "unit" / "fixtures" / "parse" / "no_frontmatter.md"

_SNAPSHOT_DIR = Path(__file__).parent / "snapshots"

def _assert_snapshot(
    rendered: str,
    fixture_name: str,
    renderer: str,
    update: bool,
) -> None:
    snap_path = _SNAPSHOT_DIR / f"scan_{fixture_name}__{renderer}.txt"

    if update or not snap_path.exists():
        snap_path.parent.mkdir(parents=True, exist_ok=True)
        snap_path.write_text(rendered, encoding="utf-8")
        return

    expected = snap_path.read_text(encoding="utf-8")
    if rendered != expected:
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
            f"Snapshot mismatch for scan {fixture_name}/{renderer}.\n"
            f"Run 'pytest tests/integration --snapshot-update' to update.\n\n"
            f"{diff_str}"
        )

@pytest.fixture
def snapshot_update(request: pytest.FixtureRequest) -> bool:
    """Return True if ``--snapshot-update`` was passed on the command line."""
    return request.config.getoption("--snapshot-update", default=False)

@pytest.mark.parametrize("fmt", ["human", "json", "sarif"])
@pytest.mark.parametrize("file_type, file_path", [
    ("benign", _BENIGN_FILE),
    ("malicious", _MALICIOUS_FILE),
    ("malformed", _MALFORMED_FILE),
])
def test_scan_formats(fmt: str, file_type: str, file_path: Path, snapshot_update: bool) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", "-d", str(file_path), "--format", fmt])
    
    assert result.exit_code == 0, f"Expected 0 exit code, got {result.exit_code}: {result.output}"
    assert len(result.output) > 0
    
    # We replace the absolute file path with a generic placeholder in the output so snapshots are stable across environments
    stable_output = result.output.replace(str(file_path), "<TEST_FILE_PATH>")
    
    _assert_snapshot(stable_output, file_type, fmt, snapshot_update)

def test_scan_fail_on_benign() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", "-d", str(_BENIGN_FILE), "--fail-on", "suspicious"])
    # Benign file should not fail
    assert result.exit_code == 0

def test_scan_fail_on_malicious() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", "-d", str(_MALICIOUS_FILE), "--fail-on", "suspicious"])
    # Malicious file should fail because it meets the threshold
    assert result.exit_code == 1

def test_scan_fail_on_malformed() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", str(_MALFORMED_FILE), "--fail-on", "suspicious"])
    # Malformed file short-circuits and does not trigger fail-on
    assert result.exit_code == 0
