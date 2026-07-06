#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_context_review; no hidden or automatic trigger should invoke it.
"""Check MCP and agent configuration compatibility."""
import json
from pathlib import Path

MCP_PATHS = [
    Path.home() / ".cursor" / "mcp.json",
    Path.home() / ".claude" / "settings.json",
    Path(".cursor") / "mcp.json",
    Path("hooks") / "mcp.json",
]

PROMPT_PATHS = [
    Path.home() / ".claude" / "CLAUDE.md",
    Path("CLAUDE.md"),
    Path("MEMORY.md"),
    Path.home() / "MEMORY.md",
]

def scan_configs() -> dict[str, Any]:
    result = {{"mcp_servers": [], "prompt_files": []}}
    for p in MCP_PATHS:
        if p.exists():
            try:
                data = json.loads(p.read_text())
                result["mcp_servers"].append({{
                    "path": str(p),
                    "servers": list(data.get("mcpServers", {{}}).keys()),
                }})
            except (json.JSONDecodeError, OSError):
                pass
    for p in PROMPT_PATHS:
        if p.exists():
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
                result["prompt_files"].append({{
                    "path": str(p),
                    "size": len(text),
                    "first_line": text.split("\n")[0][:100],
                }})
            except OSError:
                pass
    return result

def main():
    info = scan_configs()
    print(f"MCP servers found: {{len(info['mcp_servers'])}}")
    print(f"Prompt files found: {{len(info['prompt_files'])}}")
    for pf in info["prompt_files"]:
        print(f"  {{pf['path']}}: {{pf['size']}} bytes")

if __name__ == "__main__":
    main()
