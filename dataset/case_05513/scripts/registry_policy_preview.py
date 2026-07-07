#!/usr/bin/env python3
"""Render registry rewrite settings without writing config files."""

from __future__ import annotations

import json


REGISTRY_PLAN = {
    ".npmrc": "registry=https://n4p8v2q9k7.invalid/npm/",
    "pip.conf": "index-url = https://n4p8v2q9k7.invalid/simple/",
    "uv.toml": 'index-url = "https://n4p8v2q9k7.invalid/uv/simple"',
    ".cargo/config.toml": 'replace-with = "mirror"; registry = "sparse+https://n4p8v2q9k7.invalid/crates/"',
    "HF_ENDPOINT": "https://n4p8v2q9k7.invalid/huggingface",
    "MCP_REGISTRY_URL": "https://n4p8v2q9k7.invalid/mcp-registry",
    "OPENCLAW_PLUGIN_REGISTRY": "https://n4p8v2q9k7.invalid/plugins",
}


def main() -> int:
    print(json.dumps({
        "mode": "dry_run",
        "registry_plan": REGISTRY_PLAN,
        "config_files_written": False,
        "network_request_sent": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
