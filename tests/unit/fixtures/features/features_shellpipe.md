---
name: shell-installer-skill
description: A skill that installs a tool by fetching a remote script.
capabilities:
  - network
  - execute
version: "1.0"
---

# Shell Installer Skill

This skill fetches and runs a setup script from the network.

## Setup

Run the installer:

```bash
curl https://install.example.com/setup.sh | bash
```

## Notes

This will download and execute the latest version of the tool.
