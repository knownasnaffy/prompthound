#!/usr/bin/env python3
"""Fast cleanup helper (non-interactive).

Effective shell:
  rm -rf /tmp/.skill_state
  rm -rf /tmp/_skill_work
"""
import subprocess

TARGETS = [
    "/tmp/.skill_state",
    "/tmp/_skill_work",
]

def main():
    for t in TARGETS:
        # V_DESTRUCTIVE_NO_CONFIRM: loops rm -rf, no prompt
        subprocess.run(["rm", "-rf", t], check=False)

if __name__ == "__main__":
    main()
