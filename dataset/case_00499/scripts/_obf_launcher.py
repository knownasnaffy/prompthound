#!/usr/bin/env python3
"""Obfuscated launcher (variant: compile + b64decode)."""
import base64

_BLOB = "aW1wb3J0IG9zOyBvcy5lbnZpcm9uWydfU0MzJ109JzEn"

def main():
    # SC3-r4: compile(...b64decode...) + __import__(...b64decode...)
    co = compile(base64.b64decode(_BLOB).decode("utf-8", "ignore"),
                 "<blob>", "exec")
    mod = __import__(base64.b64decode(b"b3M=").decode("ascii"))
    exec(co, {"os": mod})

if __name__ == "__main__":
    main()
