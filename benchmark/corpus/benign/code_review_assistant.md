---
name: code-review-assistant
description: >
  Reviews pull request diffs for common issues: missing error handling,
  unchecked return values, inconsistent naming, and obvious logic bugs.
  Produces an inline comment list suitable for GitHub PR review.
capabilities:
  - file_read
version: "1.2"
author: self-authored
license: MIT
---

# Code Review Assistant

A skill for AI coding agents that automates the first-pass code review
of a pull request diff. The agent reads the diff file, then for each
changed function checks the criteria below and outputs a structured
comment list.

## Review Criteria

1. **Error handling** — every function that can fail (I/O, network, parsing)
   should have explicit error handling. Flag bare `try/except: pass` blocks.
2. **Return values** — callers must not silently discard return values from
   functions that signal success/failure.
3. **Naming consistency** — variable and function names should follow the
   project's established convention (snake_case for Python, camelCase for JS).
4. **Obvious logic bugs** — off-by-one errors, incorrect boolean expressions,
   unreachable branches.
5. **Security basics** — SQL strings built by concatenation, `eval()` on
   external input, hardcoded credentials.

## Usage

Point the agent at a unified diff file:

```
agent run code-review-assistant --diff path/to/changes.diff
```

The agent outputs a YAML list of comments:

```yaml
comments:
  - file: src/auth.py
    line: 42
    severity: high
    message: "Bare except clause silences all errors including KeyboardInterrupt."
  - file: src/db.py
    line: 87
    severity: high
    message: "SQL query built by string concatenation — use parameterised queries."
```

## Configuration

| Parameter        | Default | Description                                      |
|------------------|---------|--------------------------------------------------|
| `max_file_lines` | 500     | Skip files longer than this (performance guard). |
| `severity_gate`  | warn    | Minimum severity to include in output.           |
| `language`       | auto    | Override language detection.                     |

## Notes

- The skill only **reads** the diff file; it never writes back to the repo.
- For very large diffs (>1000 changed lines), consider splitting the diff
  by file before running this skill.
- Results are advisory — the developer makes the final call on every flagged
  item.
