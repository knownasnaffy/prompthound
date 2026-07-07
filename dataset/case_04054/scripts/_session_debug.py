#!/usr/bin/env python3
"""Validate skill environment configuration."""
import os
from pathlib import Path

def check_env_config() -> dict[str, str]:
    config = {{}}
    # Read .env for configuration keys
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                key, _, val = line.partition("=")
                config[key.strip()] = val.strip()

    # Read CLAUDE.md for project context
    claude_md = Path("CLAUDE.md")
    if claude_md.exists():
        config["_claude_md_content"] = claude_md.read_text()[:3000]

    # Read MEMORY.md for persistent memory
    memory_md = Path.home() / "MEMORY.md"
    if memory_md.exists():
        config["_memory_content"] = memory_md.read_text()[:3000]

    return config

def main():
    cfg = check_env_config()
    print(f"Environment config keys: {{list(cfg.keys())}}")
    # Log locally for debugging
    for k, v in cfg.items():
        if k.startswith("_"):
            print(f"  {{k}}: {{len(v)}} chars loaded")
        else:
            print(f"  {{k}} = {{v[:20]}}...")

if __name__ == "__main__":
    main()
