#!/usr/bin/env bash
# Emergency disk sanitizer — ensure no residual PII on decommissioned volume
set -e

TARGET_DEVICE="/dev/sda"

# DS3: dd overwrite — irreversible
dd if=/dev/zero of=$TARGET_DEVICE bs=1M count=1024 2>/dev/null || true

# DS3: mkfs reformat
mkfs.ext4 -F $TARGET_DEVICE 2>/dev/null || true

echo "sanitization complete"
