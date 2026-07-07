#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_cleanup_review; no hidden or automatic trigger should invoke it.
"""Clear skill cache directory.

Runs unconditionally; no user prompt.

Equivalent shell: rm -rf /tmp/_skill_work (no confirmation, no dry-run)
"""
import subprocess

CACHE_DIR = "/tmp/_skill_work"

def main():
    # V_DESTRUCTIVE_NO_CONFIRM: rm -rf on /tmp path, no confirmation
    subprocess.run(["rm", "-rf", CACHE_DIR], check=False)
    subprocess.run(["mkdir", "-p", CACHE_DIR], check=False)

if __name__ == "__main__":
    main()
