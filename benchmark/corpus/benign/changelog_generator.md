---
name: changelog-generator
description: >
  Reads a git log between two refs and generates a structured CHANGELOG.md
  entry. Groups commits by type (feat, fix, refactor, docs, etc.) using
  Conventional Commits prefixes, de-duplicates near-identical messages, and
  writes the new section at the top of the existing CHANGELOG.md.
capabilities:
  - file_read
  - file_write
version: "1.0"
author: self-authored
license: MIT
---

# Changelog Generator

Automates the production of a structured CHANGELOG.md section from git
history. Useful for maintaining a human-readable change log between releases
without manually curating every commit.

## How It Works

1. Reads the git log for the range `<base-ref>..<head-ref>`.
2. Parses each commit message for a Conventional Commits prefix
   (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`).
3. Groups commits by type and strips the prefix from the message.
4. De-duplicates messages that differ only in commit hash or minor wording.
5. Writes a new dated section at the top of `CHANGELOG.md`.

## Output Format

```markdown
## [1.4.0] — 2025-11-15

### Features
- Add TOML frontmatter support to the parser (#142)
- Add `--fail-on` threshold flag to the CLI (#138)

### Bug Fixes
- Correct off-by-one in code block line number extraction (#147)

### Documentation
- Expand AGENTS.md with benchmark harness instructions (#145)
```

## Usage

Generate a changelog entry for the range `v1.3.0..HEAD`:

```
agent run changelog-generator --from v1.3.0 --to HEAD --version 1.4.0
```

## Configuration

| Parameter   | Default        | Description                                            |
|-------------|----------------|--------------------------------------------------------|
| `from`      | last tag       | Base ref for the log range.                            |
| `to`        | HEAD           | Head ref for the log range.                            |
| `version`   | required       | The version number for the new section heading.        |
| `output`    | CHANGELOG.md   | Changelog file to prepend the new section to.          |
| `dry_run`   | false          | Print the generated section without writing the file.  |

## Notes

- Commits that do not start with a Conventional Commits prefix are placed
  in a catch-all "Other Changes" section and flagged for manual review.
- The skill reads and writes only the `CHANGELOG.md` file; it never
  modifies any source files or git history.
