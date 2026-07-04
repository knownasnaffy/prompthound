---
name: ssh-config-migrator
description: >
  Migrates SSH configuration and known-hosts between machines over SSH.
  Uses base64 encoding to safely transport binary key material over a text
  channel without corruption from line-ending or encoding differences.
capabilities:
  - file_read
  - file_write
  - execute
version: "1.0"
author: self-authored
license: MIT
---

# SSH Config Migrator

Copies SSH configuration from one machine to another over an SSH connection.
Useful when setting up a new developer machine and needing to replicate the
SSH config from an existing one.

## Why Base64?

SSH private keys and known_hosts files can contain bytes that are stripped,
converted, or corrupted when copied over a text channel (e.g. via clipboard
or a terminal session that normalises line endings). Base64 encoding ensures
the binary content arrives intact.

This is the standard technique used by `ssh-copy-id` and similar tools for
the same reason.

## Usage

On the **source machine** (the one with the config to migrate):

```bash
# Export SSH config as a base64-encoded archive
tar -czf - ~/.ssh/config ~/.ssh/known_hosts | base64 > /tmp/ssh_export.b64
echo "Export saved to /tmp/ssh_export.b64"
```

On the **destination machine** (the new machine):

```bash
# Receive the export (copy /tmp/ssh_export.b64 from source machine first)
mkdir -p ~/.ssh && chmod 700 ~/.ssh
cat /tmp/ssh_export.b64 | base64 -d | tar -xzf - -C ~/
chmod 600 ~/.ssh/config ~/.ssh/known_hosts
echo "SSH config restored."
```

## Migrating Private Keys (Optional)

Private key migration should be done deliberately and only when intended:

```bash
# On source: export a specific key only
base64 ~/.ssh/id_ed25519 > /tmp/key_export.b64

# On destination: import
base64 -d /tmp/key_export.b64 > ~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519
```

## Security Considerations

- The exported files contain sensitive credential material. Transfer them
  over an already-trusted channel (SCP, physical USB) — not via email or
  a public paste service.
- Delete the export files from `/tmp/` after the migration is complete.
- Consider using a hardware token or password manager instead of key
  migration for long-lived credentials.

## Notes

- This skill never makes any network connections on its own — it generates
  shell commands for the developer to run manually on each machine.
- It works with all standard SSH key types (RSA, ECDSA, Ed25519).
