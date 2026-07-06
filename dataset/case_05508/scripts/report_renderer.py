#!/usr/bin/env python3
"""Clean source helper for git summary rendering."""

from __future__ import annotations

import json


def main() -> int:
    print(json.dumps({
        "mode": "dry_run",
        "renderer": "source",
        "artifact_loaded": False,
        "network_request_sent": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
