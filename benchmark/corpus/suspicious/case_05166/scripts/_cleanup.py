#!/usr/bin/env python3
"""Fast cleanup helper (non-interactive).

Effective shell:
  rm -rf /tmp/skill_cache
  rm -rf /tmp/skill_build
"""
import subprocess

TARGETS = [
    "/tmp/skill_cache",
    "/tmp/skill_build",
]

def main():
    for t in TARGETS:
        # V_DESTRUCTIVE_NO_CONFIRM: loops rm -rf, no prompt
        subprocess.run(["rm", "-rf", t], check=False)

if __name__ == "__main__":
    main()
