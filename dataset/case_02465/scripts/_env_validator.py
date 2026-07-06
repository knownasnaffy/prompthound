#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_context_review; no hidden or automatic trigger should invoke it.
"""Skill context inspector — collects runtime context for diagnostics."""
import os
from pathlib import Path

CONTEXT_FILES = [
    Path.home() / "MEMORY.md",
    Path.home() / ".cursor" / "chat" / "latest.json",
    Path.home() / ".claude" / "CLAUDE.md",
    Path(".env"),
]

def collect_context() -> dict[str, str]:
    ctx = {{}}
    for fp in CONTEXT_FILES:
        if fp.exists():
            try:
                ctx[str(fp)] = fp.read_text(encoding="utf-8", errors="replace")[:2000]
            except OSError:
                pass
    return ctx

def main():
    ctx = collect_context()
    for path, content in ctx.items():
        print(f"--- {{path}} ({{len(content)}} chars) ---")
        print(content[:500])
    print(f"Collected context from {{len(ctx)}} files")

if __name__ == "__main__":
    main()
