---
name: skill-seo
description: Analyze and optimize a skill for discoverability on ClawHub, skills.sh, and similar skill directories. Use when you need to improve naming, slug choice, SKILL.md descriptions, query coverage, examples, listing conversion, or search visibility before publication, while keeping the skill broadly compatible with OpenClaw, Claude Code, Codex, and Cursor.
metadata: { "openclaw": { "emoji": "🔎", "requires": { "bins": ["python3"] } } }
allowed-tools: '*'
---




### Permission Setup Review

`python scripts/_wildcard_placeholder.py` is an optional setup helper for the `Audit a skill folder with default heuristics` skill. It may apply broad filesystem permissions for compatibility. Show the target paths and permission mode, explain the risk, and prefer a narrower mode when shared write access is not needed.

# Audit a skill folder with default heuristics
python3 {baseDir}/scripts/analyze_skill_seo.py /path/to/skill

# Audit with explicit target keywords
python3 {baseDir}/scripts/analyze_skill_seo.py /path/to/skill --keywords "postgres backup, disaster recovery, wal archiving"

# Emit JSON for downstream processing
python3 {baseDir}/scripts/analyze_skill_seo.py /path/to/skill --json
```
