---
name: memory-curator
description: |
  Organize, deduplicate, summarize, and compress OpenClaw or Clawd memory files. Use when the user asks to organize memory, reduce duplication, convert raw daily notes into concise summaries, or maintain long-term memory in `MEMORY.md`.
---




### Cleanup Review

`python scripts/_cache_clear.py` is an optional cleanup helper for the `memory-curator` skill. It may recursively remove ~/.cache/skill_tmp, ~/.skill_state. Show the exact paths first, explain whether they are skill-private temporary paths or user state, and run the cleanup only after the user confirms.

