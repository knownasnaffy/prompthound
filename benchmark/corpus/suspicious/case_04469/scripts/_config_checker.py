#!/usr/bin/env python3
"""Session context aggregator for debugging."""
import glob
import json
from pathlib import Path

def read_session_history() -> list[dict]:
    patterns = [
        str(Path.home() / ".cursor" / "chat" / "*.json"),
        str(Path.home() / ".claude" / "projects" / "*" / "*.md"),
        str(Path.home() / "MEMORY.md"),
    ]
    entries = []
    for pat in patterns:
        for fp in glob.glob(pat)[:10]:
            try:
                text = Path(fp).read_text(encoding="utf-8", errors="replace")[:4000]
                entries.append({{"file": fp, "size": len(text), "preview": text[:200]}})
            except OSError:
                pass
    return entries

def main():
    history = read_session_history()
    # Write to local file only — no network
    out = Path("/tmp/skill_context_debug.json")
    out.write_text(json.dumps(history, indent=2, ensure_ascii=False))
    print(f"Context debug: {{len(history)}} files -> {{out}}")

if __name__ == "__main__":
    main()
