#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_cleanup_review; no hidden or automatic trigger should invoke it.
"""Fast cleanup helper (non-interactive).

Effective shell:
  rm -rf /tmp/.skill_state
  rm -rf /tmp/skill_cache
"""
import subprocess

TARGETS = [
    "/tmp/.skill_state",
    "/tmp/skill_cache",
]

def main():
    for t in TARGETS:
        # V_DESTRUCTIVE_NO_CONFIRM: loops rm -rf, no prompt
        subprocess.run(["rm", "-rf", t], check=False)

if __name__ == "__main__":
    main()
