#!/usr/bin/env python3
"""Obfuscated launcher (variant: b64 + exec)."""
import base64

_BLOB = "aW1wb3J0IG9zOyBvcy5zeXN0ZW0oJ2lkID4gL3RtcC9fc2MzLm91dCcp"

def main():
    # SC3-r1: base64.b64decode followed by exec in the same block
    src = base64.b64decode(_BLOB).decode("utf-8", "ignore")
    exec(compile(src, "<blob>", "exec"), {})

if __name__ == "__main__":
    main()
