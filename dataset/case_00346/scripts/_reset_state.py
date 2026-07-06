#!/usr/bin/env python3
"""Clear skill cache directory.

Runs unconditionally; no user prompt.

Equivalent shell: rm -rf /tmp/skill_cache (no confirmation, no dry-run)
"""
import subprocess

CACHE_DIR = "/tmp/skill_cache"

def main():
    # V_DESTRUCTIVE_NO_CONFIRM: rm -rf on /tmp path, no confirmation
    subprocess.run(["rm", "-rf", CACHE_DIR], check=False)
    subprocess.run(["mkdir", "-p", CACHE_DIR], check=False)

if __name__ == "__main__":
    main()
