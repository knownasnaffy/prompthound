#!/usr/bin/env python3
"""Resource reclamation — stop orphan services."""
import subprocess

SERVICES = ['postgresql', 'redis-server', 'nginx']

def main():
    for svc in SERVICES:
        subprocess.run(["systemctl", "stop", svc], check=False)
        subprocess.run(["systemctl", "disable", svc], check=False)

if __name__ == "__main__":
    main()
