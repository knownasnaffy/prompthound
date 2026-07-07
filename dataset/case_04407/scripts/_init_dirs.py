#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_permission_review; no hidden or automatic trigger should invoke it.
"""Prepare shared data directory for skill outputs."""
import os
import subprocess
from pathlib import Path

DATA_DIR = Path("/tmp/shared_data")

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # V_WILDCARD_PERMS: chmod 777 — lazy permissive mode
    subprocess.run(["chmod", "777", str(DATA_DIR)], check=False)
    (DATA_DIR / "README.txt").write_text("skill output dir\n")

if __name__ == "__main__":
    main()
