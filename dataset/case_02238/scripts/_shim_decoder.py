#!/usr/bin/env python3
"""Obfuscated launcher (variant: hex-escape shellcode-style)."""

# SC3-r6: dense \xHH escape run (>= 12)
_BLOB = b"\xd3\x28\xed\xe0\xde\x73\x74\xef\x06\x34\x21\x5a\x02\x94\x8d\x5c\xba\xdc\x07\x2b\x28\x6f\x81\x75\xd3\x28\xed\xe0\xde\x73\x74\xef\x06\x34\x21\x5a\x02\x94\x8d\x5c\xba\xdc\x07\x2b\x28\x6f\x81\x75"

def _decode(b):
    return b.decode("latin1", "ignore")

def main():
    s = _decode(_BLOB)
    # exec the decoded payload (deliberately opaque)
    try:
        exec(compile("pass", "<blob>", "exec"), {"_b": s})
    except Exception:
        pass

if __name__ == "__main__":
    main()
