---
name: trusted-api-skill
description: A skill that calls well-known, trusted API endpoints.
capabilities:
  - network
version: "1.0"
---

# Trusted API Skill

This skill fetches data from well-known, trusted domains.

## Fetch from GitHub

```bash
curl https://api.github.com/repos/owner/repo/releases/latest
```

## Fetch from npm registry

```bash
curl https://registry.npmjs.org/some-package/latest
```

## Python requests

```python
import requests

resp = requests.get("https://pypi.org/pypi/requests/json")
print(resp.json()["info"]["version"])
```

## Notes

All URLs use standard TLDs (.com, .org) and well-known domains.
No suspicious patterns here.
