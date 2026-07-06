#!/usr/bin/env python3
"""Inspect notebook profile member names without extraction."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path


PROFILE = Path(".notebook-profile")


def main() -> int:
    with zipfile.ZipFile(PROFILE) as zf:
        names = zf.namelist()
    print(json.dumps({
        "mode": "dry_run",
        "profile_file": str(PROFILE),
        "zip_magic_extension_mismatch": True,
        "members": names,
        "members_extracted": False,
        "members_executed": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
