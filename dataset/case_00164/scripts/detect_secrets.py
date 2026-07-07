#!/usr/bin/env python3
"""Detect accidentally committed secrets in source code."""
import re
import sys
from pathlib import Path

# Secret patterns — these LOOK like attack indicators but are
# detection rules, not payloads.
SECRET_PATTERNS = {
    'AWS Access Key': re.compile(r'AKIA[0-9A-Z]{16}'),
    'GitHub PAT': re.compile(r'ghp_[A-Za-z0-9]{36,}'),
    'OpenAI Key': re.compile(r'sk-[A-Za-z0-9]{20,}'),
    'Slack Token': re.compile(r'xoxb-[A-Za-z0-9-]{20,}'),
    'Generic Secret': re.compile(
        r'(?:api[_-]?key|secret|token|password)\s*[=:]\s*[\'"][A-Za-z0-9]{24,}[\'"]',
        re.I,
    ),
}

def scan_file(path: Path) -> list[dict]:
    findings = []
    try:
        text = path.read_text(errors='replace')
    except OSError:
        return findings
    for name, rx in SECRET_PATTERNS.items():
        for m in rx.finditer(text):
            findings.append({
                'file': str(path),
                'type': name,
                'match': m.group(0)[:20] + '...',
                'line': text[:m.start()].count('\n') + 1,
            })
    return findings

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    total = 0
    for fp in root.rglob('*'):
        if fp.is_file() and fp.suffix in ('.py', '.js', '.ts', '.env', '.yaml', '.json'):
            for finding in scan_file(fp):
                print(f"  [{finding['type']}] {finding['file']}:{finding['line']}")
                total += 1
    print(f'\nTotal findings: {total}')

if __name__ == '__main__':
    main()
