---
name: safe-installer
description: A skill that uses curl to download a file and saves it safely.
capabilities:
  - network
  - file_write
version: "1.0"
---

# Safe Downloader Skill

This skill downloads a file to disk and checks it before running anything.

## Setup

```bash
curl -o /tmp/installer.sh https://releases.example.com/install.sh
sha256sum /tmp/installer.sh
# review the file, then run it manually
```

## Notes

This skill downloads the script but does NOT pipe it directly into a shell.
The user is expected to inspect the file before running it.
