---
name: commit-message-generator
description: >
  Reads a staged git diff and generates a Conventional Commits-formatted commit
  message. Groups changes by type (feat, fix, refactor, test, docs, chore),
  writes a concise subject line, and optionally includes a bullet-point body
  listing changed files with one-line summaries.
capabilities:
  - file_read
version: "1.0"
author: self-authored
license: MIT
---

# Commit Message Generator

Generates structured commit messages from a staged diff. Designed to reduce
the mental overhead of writing well-formed commit messages without forcing the
developer to adopt any particular workflow.

## Conventional Commits format

The skill outputs messages following [Conventional Commits 1.0.0]:

```
<type>(<optional scope>): <subject>

[optional body]

[optional footers]
```

Types used:

| Type       | When to use                                        |
|------------|----------------------------------------------------|
| `feat`     | New feature visible to users or downstream callers |
| `fix`      | Bug fix                                            |
| `refactor` | Internal restructure, no behaviour change          |
| `test`     | Add or update tests                                |
| `docs`     | Documentation-only change                          |
| `chore`    | Build scripts, dependency bumps, config            |
| `perf`     | Performance improvement                            |

## Usage

Run inside a git repo with changes staged:

```
agent run commit-message-generator
```

The agent reads `git diff --cached`, classifies the change, and prints a
proposed commit message to stdout. You review and accept/edit it before
the actual commit.

## Example output

```
feat(parser): add support for TOML frontmatter

- parse.py: extend _parse_frontmatter() to try TOML after YAML
- schema.py: add frontmatter_format field to ParsedSkill
- tests/unit/test_parse.py: add fixtures for TOML frontmatter
```

## Configuration

| Parameter      | Default | Description                                                  |
|----------------|---------|--------------------------------------------------------------|
| `body_lines`   | true    | Include a bullet-point body listing changed files.           |
| `max_subject`  | 72      | Maximum subject line length (enforced by truncation + `…`). |
| `scope`        | auto    | Override scope detection (uses the most-changed directory).  |

## Notes

- The skill only reads the staged diff output; it does not commit anything.
- It has no access to the commit history. For a squash or amend workflow,
  pass the full diff manually.

[Conventional Commits 1.0.0]: https://www.conventionalcommits.org/en/v1.0.0/
