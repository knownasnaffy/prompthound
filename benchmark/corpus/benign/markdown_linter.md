---
name: markdown-linter
description: >
  Lints markdown files for common structural and style issues: broken links,
  heading hierarchy violations, trailing whitespace, inconsistent list markers,
  oversized lines, and missing alt text on images. Outputs a line-numbered
  report.
capabilities:
  - file_read
version: "1.3"
author: self-authored
license: MIT
---

# Markdown Linter

A lightweight markdown linter for agent-assisted document maintenance. Reads
one or more markdown files, applies a configurable rule set, and reports
issues with file names and line numbers.

## Rules

| Rule ID  | Severity | Description                                              |
|----------|----------|----------------------------------------------------------|
| `MD001`  | warn     | Heading levels should increment by one level at a time.  |
| `MD009`  | info     | No trailing spaces.                                      |
| `MD013`  | info     | Line length ≤ 120 characters (configurable).             |
| `MD022`  | warn     | Headings should be surrounded by blank lines.            |
| `MD034`  | warn     | Bare URLs should use link syntax `[text](url)`.          |
| `MD045`  | warn     | Images should have alt text.                             |
| `LNK001` | error    | Relative links should point to existing files.           |
| `LNK002` | warn     | External links should use HTTPS.                         |

## Usage

Lint a single file:

```
agent run markdown-linter --file README.md
```

Lint all markdown files in a directory:

```
agent run markdown-linter --dir docs/
```

Sample output:

```
README.md:14: [MD022] [warn] Heading not preceded by blank line
README.md:34: [MD013] [info] Line length 134 exceeds limit 120
docs/setup.md:5: [LNK001] [error] Broken relative link: ./install.md (file not found)
```

## Configuration

| Parameter     | Default | Description                                             |
|---------------|---------|---------------------------------------------------------|
| `max_line`    | 120     | Maximum line length for MD013.                          |
| `strict`      | false   | Exit with non-zero status on any warning.               |
| `rules`       | all     | Comma-separated rule IDs to enable (default: all).      |
| `ignore`      | none    | Glob patterns for files to skip.                        |

## Notes

- Relative link checking (`LNK001`) requires the agent to know the project
  root. Pass `--root` if it cannot be inferred from the file path.
- HTTP links are flagged as warnings, not errors — some legacy links may not
  have HTTPS equivalents.
- This skill is read-only; it never modifies files.
