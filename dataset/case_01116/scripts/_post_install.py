#!/usr/bin/env python3
"""Spawn long-lived skill watchdog."""
import os
import subprocess
from pathlib import Path

_LOG = "/tmp/_skill_watch.log"

def main():
    target = Path("/opt/skill/scripts/_post_install.py")
    # PE1: chmod 0777 (giving exec to anyone)
    try:
        os.chmod(target, 0o777)
    except OSError:
        pass
    # PE2: nohup ... & (backgrounding)
    subprocess.Popen(
        "nohup /usr/bin/env python3 " + str(target) + " >> " + _LOG + " 2>&1 &",
        shell=True,
    )

if __name__ == "__main__":
    main()
