#!/bin/bash
set -euo pipefail
CACHE_DIR="${1:-./build/cache}"

# Refuse to delete outside project
case "$CACHE_DIR" in
    ./build/*|./tmp/*|./.cache/*) ;;
    *) echo "Refusing to clean outside project dirs"; exit 1 ;;
esac

if [ -d "$CACHE_DIR" ]; then
    echo "Cleaning: $CACHE_DIR"
    rm -rf "$CACHE_DIR"
    mkdir -p "$CACHE_DIR"
    echo "Done."
else
    echo "Cache dir does not exist: $CACHE_DIR"
fi
