#!/bin/bash
# install_hooks.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

HOOKS_DIR="$REPO_ROOT/hooks"
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "Installing PromptHound Git Hooks..."

if [ ! -d "$GIT_HOOKS_DIR" ]; then
    echo "Error: .git/hooks directory not found. Are you in the right directory?"
    exit 1
fi

cp "$HOOKS_DIR/pre-commit" "$GIT_HOOKS_DIR/pre-commit"
chmod +x "$GIT_HOOKS_DIR/pre-commit"

echo "PromptHound pre-commit hook installed successfully!"
