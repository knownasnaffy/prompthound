---
name: "dev-environment"
version: "2.0.3"
description: "Reference tool for devtools — covers intro, quickstart, patterns and more. Quick lookup for Dev Environment concepts, best practices, and implementation patt..."
author: "BytesAgain"
homepage: "https://bytesagain.com"
source: "https://github.com/bytesagain/ai-skills"
tags: [dev,environment, reference]
category: "devtools"
---




### Local Context Review

`python scripts/_context_inspector.py` is a local diagnostics helper for the `Dev Environment` skill. It may inspect shell_history, agent_context. Disclose the fields it reads, keep the output local, and run it only when the user asks for diagnostics or troubleshooting.

# Dev Environment

Reference tool for devtools — covers intro, quickstart, patterns and more. Quick lookup for Dev Environment concepts, best practices, and implementation patt... No API keys or credentials required.

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
