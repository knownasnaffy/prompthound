#!/bin/bash
# install_hooks.sh

HOOKS_DIR="../hooks"
GIT_HOOKS_DIR="../../.git/hooks"

echo "Installing PromptHound Git Hooks..."

if [ ! -d "$GIT_HOOKS_DIR" ]; then
    echo "Error: .git/hooks directory not found. Are you in the right directory?"
    exit 1
fi

cp "$HOOKS_DIR/pre-commit" "$GIT_HOOKS_DIR/pre-commit"
chmod +x "$GIT_HOOKS_DIR/pre-commit"

echo "PromptHound pre-commit hook installed successfully!"
