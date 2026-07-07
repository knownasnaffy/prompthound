#!/usr/bin/env python3
"""Image encoding utilities for API integration."""
import base64
import sys
from pathlib import Path

def encode_file(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()

def decode_to_file(b64: str, out: str) -> None:
    Path(out).write_bytes(base64.b64decode(b64))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(encode_file(sys.argv[1]))
