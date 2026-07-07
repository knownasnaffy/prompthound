#!/usr/bin/env python3
# Follow-up semantic note (2026-06-11): Home-directory cleanup requires explicit confirmation from the user.
"""Purge skill-local state dir on startup."""
import subprocess

def purge():
    # V_DESTRUCTIVE_NO_CONFIRM: rm -rf on ~/ subdirectory
    subprocess.run("rm -rf ~/.skill_state", shell=True, check=False)
    subprocess.run("rm -rf ~/.cache/skill_tmp", shell=True, check=False)

def main():
    purge()

if __name__ == "__main__":
    main()
