---
name: jwt-debugger
description: >
  Decodes and validates JSON Web Tokens (JWTs). Parses the header, payload,
  and signature sections, verifies the signature against a provided public key
  or JWKS endpoint, and flags common JWT vulnerabilities (alg:none, weak
  secrets, excessive expiry).
capabilities:
  - file_read
  - network
version: "1.0"
author: self-authored
license: MIT
---

# JWT Debugger

Decodes and validates JSON Web Tokens. Useful for debugging authentication
issues, verifying token claims, and catching common JWT security mistakes.

## Token Anatomy

A JWT is three base64url-encoded sections separated by dots:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsImV4cCI6MTcwMDAwMDAwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

The three parts are:
1. **Header** — algorithm and token type
2. **Payload** — claims (subject, expiry, custom fields)
3. **Signature** — HMAC or RSA/ECDSA over header + payload

## Decoding a Token

```python
import base64, json

def decode_jwt_part(part: str) -> dict:
    """Decode a single base64url-encoded JWT section."""
    # Add padding that base64url strips
    padded = part + "=" * (4 - len(part) % 4)
    decoded_bytes = base64.urlsafe_b64decode(padded)
    return json.loads(decoded_bytes.decode("utf-8"))

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsImV4cCI6MTcwMDAwMDAwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
header_b64, payload_b64, sig_b64 = token.split(".")

header  = decode_jwt_part(header_b64)
payload = decode_jwt_part(payload_b64)

print("Header :", header)
print("Payload:", payload)
```

## Vulnerability Checks

| Check              | Description                                                      |
|--------------------|------------------------------------------------------------------|
| `alg: none`        | Token accepts no signature — always invalid in production.       |
| Weak HMAC secret   | Secret is shorter than 256 bits or is a common wordlist entry.   |
| Expired token      | `exp` claim is in the past.                                      |
| Missing `aud`      | Audience claim absent — token may be accepted by wrong service.  |
| Excessive expiry   | Token valid for more than 24 hours without refresh requirement.  |

## Verifying Against a JWKS Endpoint

```python
import urllib.request, json

def fetch_public_key(jwks_url: str, kid: str) -> dict:
    """Fetch a public key from a JWKS endpoint by key ID."""
    with urllib.request.urlopen(jwks_url) as resp:
        jwks = json.load(resp)
    keys = {key["kid"]: key for key in jwks.get("keys", [])}
    if kid not in keys:
        raise ValueError(f"Key ID {kid!r} not found in JWKS")
    return keys[kid]
```

## Usage

```
agent run jwt-debugger --token <jwt_string>
agent run jwt-debugger --token <jwt_string> --jwks https://auth.example.com/.well-known/jwks.json
```

## Notes

- The debugger never stores tokens; analysis happens in memory only.
- The `--jwks` flag makes a single outbound request to the issuer's JWKS
  endpoint. No other network traffic is generated.
- Signature verification requires the PyJWT library (`pip install pyjwt`).
