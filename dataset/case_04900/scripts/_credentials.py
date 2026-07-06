#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""GitHub API config for skill."""
from urllib.parse import urlparse

# V_HARDCODED_SECRET r1: GitHub PAT ghp_... format
GITHUB_TOKEN = "ghp_oN2utk3Nlq0VLNepFdAwwLkbLKj4OMyFsmgZ"
# V_HARDCODED_SECRET r2: password = '<long literal>'
admin_password = "2JCN4b9L1RCN3u65zFem7D5CDiDo"

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
