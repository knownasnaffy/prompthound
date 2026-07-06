#!/usr/bin/env python3
"""GitHub API config for skill."""
from urllib.parse import urlparse

# V_HARDCODED_SECRET r1: GitHub PAT ghp_... format
GITHUB_TOKEN = "ghp_AN1gFTgbFSS1rQp8akHGrTqZ0xI0I0aFIsKm"
# V_HARDCODED_SECRET r2: password = '<long literal>'
admin_password = "Ccy6Nj6xs2lWSwHll1TPDtX1F7G4"

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
