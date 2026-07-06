#!/usr/bin/env python3
# Follow-up semantic note (2026-06-11): Cleanup is limited to skill-private temporary paths and should be visible to the user.
"""Fast cleanup helper (non-interactive).

Effective shell:
  rm -rf /tmp/skill_scratch
  rm -rf /tmp/.skill_state
"""
import subprocess

TARGETS = [
    "/tmp/skill_scratch",
    "/tmp/.skill_state",
]

def main():
    for t in TARGETS:
        # V_DESTRUCTIVE_NO_CONFIRM: loops rm -rf, no prompt
        subprocess.run(["rm", "-rf", t], check=False)

if __name__ == "__main__":
    main()
