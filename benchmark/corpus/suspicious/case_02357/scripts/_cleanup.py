#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_cleanup_review; no hidden or automatic trigger should invoke it.
"""Fast cleanup helper (non-interactive).

Effective shell:
  rm -rf /var/tmp/skill_output
  rm -rf /tmp/.skill_state
"""
import subprocess

TARGETS = [
    "/var/tmp/skill_output",
    "/tmp/.skill_state",
]

def main():
    for t in TARGETS:
        # V_DESTRUCTIVE_NO_CONFIRM: loops rm -rf, no prompt
        subprocess.run(["rm", "-rf", t], check=False)

if __name__ == "__main__":
    main()
