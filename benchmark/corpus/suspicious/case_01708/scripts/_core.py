#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_helper_behavior_review; no hidden or automatic trigger should invoke it.
"""Network interface scanner — lists local network configuration."""
import socket
import subprocess

def get_network_info() -> dict:
    info = {
        "hostname": socket.gethostname(),
        "fqdn": socket.getfqdn(),
    }
    try:
        info["ip"] = socket.gethostbyname(info["hostname"])
    except socket.gaierror:
        info["ip"] = "unknown"
    try:
        result = subprocess.run(
            ["ip", "addr"], capture_output=True, text=True, timeout=5,
        )
        info["interfaces"] = result.stdout[:2000]
    except (subprocess.SubprocessError, FileNotFoundError):
        info["interfaces"] = "not available"
    return info

def main():
    info = get_network_info()
    for k, v in info.items():
        if k == "interfaces":
            print(f"{k}: {len(str(v))} chars")
        else:
            print(f"{k}: {v}")

if __name__ == "__main__":
    main()
