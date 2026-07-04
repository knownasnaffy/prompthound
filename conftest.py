"""Root conftest.py — registers custom pytest CLI options used across the test suite."""

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--snapshot-update",
        action="store_true",
        default=False,
        help="Overwrite stored snapshots with current rendered output.",
    )
