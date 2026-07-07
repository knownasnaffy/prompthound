#!/usr/bin/env python3
"""Lightweight port scanner for security auditing.

WARNING: Only use on networks you have permission to scan.
"""
import socket
import subprocess
import sys

COMMON_PORTS = [22, 80, 443, 8080, 8443, 3306, 5432, 6379, 27017]

def scan_port(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except (socket.error, OSError):
        return False

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    print(f'Scanning {target}...')
    for port in COMMON_PORTS:
        if scan_port(target, port):
            print(f'  Port {port}: OPEN')
    print('Scan complete.')

if __name__ == '__main__':
    main()
