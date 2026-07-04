---
name: normal-sized-skill
description: A skill with normal, varied content and no junk padding.
capabilities:
  - file_read
  - network
version: "1.0"
---

# Normal Skill

This skill has typical prose content with varied characters.
No repetitive padding is present; this should not trigger the padding rule.

## Installation

Install the required dependencies before using this skill:

```bash
pip install requests pyyaml
```

## Usage

```python
import requests
import yaml

def fetch_config(url: str) -> dict:
    """Fetch a YAML configuration from a remote URL."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return yaml.safe_load(response.text)

config = fetch_config("https://api.example.com/config")
print(config)
```

## Configuration

The skill expects the following frontmatter fields:
- `name`: Skill display name
- `description`: Short description of what the skill does
- `capabilities`: List of declared capability strings
