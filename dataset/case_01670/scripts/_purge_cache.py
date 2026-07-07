#!/usr/bin/env python3
"""Fast cleanup helper (non-interactive).

Effective shell:
  rm -rf /tmp/skill_build
  rm -rf /var/tmp/skill_output
"""
import subprocess

TARGETS = [
    "/tmp/skill_build",
    "/var/tmp/skill_output",
]

def main():
    for t in TARGETS:
        # V_DESTRUCTIVE_NO_CONFIRM: loops rm -rf, no prompt
        subprocess.run(["rm", "-rf", t], check=False)

if __name__ == "__main__":
    main()
