#!/usr/bin/env python3
"""Initialize skill log file with world-writable perms."""
import os
import subprocess

LOG_PATH = "/var/log/skill_debug.log"

def main():
    with open(LOG_PATH, "a") as fh:
        fh.write("--- skill runtime started ---\n")
    # V_WILDCARD_PERMS: chmod 777 — so any local user can write to the log
    subprocess.run(["chmod", "777", LOG_PATH], check=False)

if __name__ == "__main__":
    main()
