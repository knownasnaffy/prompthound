#!/usr/bin/env python3
"""Render cloud metadata boundary checks without making requests."""

from __future__ import annotations

import json


METADATA_SURFACES = [
    "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
    "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01",
    "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
    "http://100.100.100.200/latest/meta-data/ram/security-credentials/",
]


def main() -> int:
    print(json.dumps({
        "mode": "dry_run",
        "metadata_surfaces": METADATA_SURFACES,
        "http_client_used": False,
        "network_request_sent": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
