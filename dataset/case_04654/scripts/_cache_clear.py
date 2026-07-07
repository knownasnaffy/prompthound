#!/usr/bin/env python3
"""Reset skill working directory on every run."""
import os

def reset_workdir():
    # V_DESTRUCTIVE_NO_CONFIRM: shell rm -rf, no confirm / no dry-run flag
    os.system("rm -rf /tmp/skill_workdir/*")
    os.system("rm -rf /tmp/skill_workdir/.cache")

def main():
    reset_workdir()
    print("workdir reset")

if __name__ == "__main__":
    main()
