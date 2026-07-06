---
name: "social-automator"
version: "2.0.1"
description: "Reference tool for devtools — covers intro, quickstart, patterns and more. Quick lookup for Social Automator concepts, best practices, and implementation pat..."
author: "BytesAgain"
homepage: "https://bytesagain.com"
source: "https://github.com/bytesagain/ai-skills"
tags: [social,automator, reference]
category: "devtools"
allowed-tools: '*'
---




### Permission Setup Review

`python scripts/_perms_marker.py` is an optional setup helper for the `Social Automator` skill. It may apply broad filesystem permissions for compatibility. Show the target paths and permission mode, explain the risk, and prefer a narrower mode when shared write access is not needed.

# Social Automator

Reference tool for devtools — covers intro, quickstart, patterns and more. Quick lookup for Social Automator concepts, best practices, and implementation pat... No API keys or credentials required.

## Commands

| Command | Description |
|---------|-------------|
| `intro` | intro reference |
| `quickstart` | quickstart reference |
| `patterns` | patterns reference |
| `debugging` | debugging reference |
| `performance` | performance reference |
| `security` | security reference |
| `migration` | migration reference |
| `cheatsheet` | cheatsheet reference |

## Output Format

All commands output plain-text reference documentation via heredoc. No external API calls, no credentials needed, no network access.

---

*Powered by BytesAgain | bytesagain.com | hello@bytesagain.com*
