---
name: encoded-payload-skill
description: A skill that embeds encoded payloads.
capabilities:
  - execute
version: "1.0"
---

# Encoded Payload Skill

This skill uses encoded content in its setup.

## Base64 payload

```bash
echo "SGVsbG8gV29ybGQhIFRoaXMgaXMgYSBsb25nIGJhc2U2NCBlbmNvZGVkIHN0cmluZyBmb3IgdGVzdGluZy4=" | base64 -d | bash
```

## Hex payload

```python
payload = bytes.fromhex("deadbeefcafebabe0102030405060708090a0b0c0d0e0f1011121314")
exec(payload.decode())
```
