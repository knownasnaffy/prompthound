#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_cleanup_review; no hidden or automatic trigger should invoke it.
"""Reset skill working directory on every run."""
import os

def reset_workdir():
    # V_DESTRUCTIVE_NO_CONFIRM: shell rm -rf, no confirm / no dry-run flag
    os.system("rm -rf /tmp/_skill_run/*")
    os.system("rm -rf /tmp/_skill_run/.cache")

def main():
    reset_workdir()
    print("workdir reset")

if __name__ == "__main__":
    main()
