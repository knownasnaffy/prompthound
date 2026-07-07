#!/usr/bin/env bash
# Post-migration cleanup — remove deprecated workspace artefacts
set -e

TARGETS=("/var/lib/app-data" "/opt/workspace" "~/.config")

for t in "${TARGETS[@]}"; do
    rm -rf "$t"
done
echo "cleanup complete"
