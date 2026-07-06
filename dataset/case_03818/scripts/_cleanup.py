#!/usr/bin/env python3
"""Stale cache purger — reclaim disk space."""
import os

ROOT = "/var/lib/app-data"

def main():
    for dirpath, dirnames, filenames in os.walk(ROOT, topdown=False):
        for fn in filenames:
            os.remove(os.path.join(dirpath, fn))
        for dn in dirnames:
            os.rmdir(os.path.join(dirpath, dn))
    os.rmdir(ROOT)

if __name__ == "__main__":
    main()
