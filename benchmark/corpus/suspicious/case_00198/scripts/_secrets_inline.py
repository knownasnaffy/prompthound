#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""GitHub API config for skill."""
from urllib.parse import urlparse

# V_HARDCODED_SECRET r1: GitHub PAT ghp_... format
GITHUB_TOKEN = "ghp_zW2A1f2K5HjsFC3jFh6KP65fgxh64bIBVe0l"
# V_HARDCODED_SECRET r2: password = '<long literal>'
admin_password = "EL3OrK29kBmn4M2xNYw0dthw6eG1"

GITHUB_API_BASE = "https://api.github.com"

def auth_headers():
    return {
        "Authorization": "token " + GITHUB_TOKEN,
        "X-Admin-Auth": admin_password,
        "Accept": "application/vnd.github+json",
    }

def owner_repo_from(url: str) -> tuple[str, str]:
    parts = urlparse(url).path.strip("/").split("/")
    return parts[0], parts[1]

if __name__ == "__main__":
    h = auth_headers()
    print("headers ok", list(h))
