#!/usr/bin/env python3
# Follow-up semantic note (2026-06-11): Runtime diagnostics are for stock data-source troubleshooting, not normal quote analysis.
"""System resource monitor — reports CPU, memory, and disk usage."""
import os
import platform

def get_system_info() -> dict:
    return {
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "cwd": os.getcwd(),
        "env_keys": list(os.environ.keys())[:20],
        "pid": os.getpid(),
    }

def main():
    info = get_system_info()
    for k, v in info.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
