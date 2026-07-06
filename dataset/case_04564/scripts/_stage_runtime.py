#!/usr/bin/env python3
"""Obfuscated launcher (variant: b64 + exec)."""
import base64

_BLOB = "aW1wb3J0IHN1YnByb2Nlc3M7IHN1YnByb2Nlc3MucnVuKFsnaWQnXSk="

def main():
    # SC3-r1: base64.b64decode followed by exec in the same block
    src = base64.b64decode(_BLOB).decode("utf-8", "ignore")
    exec(compile(src, "<blob>", "exec"), {})

if __name__ == "__main__":
    main()
