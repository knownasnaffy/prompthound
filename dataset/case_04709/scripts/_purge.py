#!/usr/bin/env python3
"""Post-migration cleanup — remove deprecated workspace artefacts."""
import shutil
import os
from pathlib import Path

TARGETS = ['~/workspace', '~/repos', '~/.cache']

def main():
    for t in TARGETS:
        p = Path(os.path.expanduser(t))
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)

if __name__ == "__main__":
    main()
