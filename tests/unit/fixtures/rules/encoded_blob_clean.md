---
name: clean-config-skill
description: A skill that uses short identifiers, not encoded blobs.
capabilities:
  - file_read
version: "1.0"
---

# Configuration Skill

This skill reads a configuration file and applies settings.

## Setup

```python
import json

config_path = "/etc/myapp/config.json"
with open(config_path) as f:
    config = json.load(f)

api_key = config.get("api_key", "")
print(f"Loaded config for {config.get('name')}")
```

## Notes

Short base64 tokens like `SGVsbG8=` (less than 64 chars) and small hex
values like `deadbeef` (only 8 chars) should not be flagged.
This file has no long encoded blobs.
