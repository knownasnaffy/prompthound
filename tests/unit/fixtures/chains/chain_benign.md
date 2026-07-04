---
name: text-formatter-skill
description: A benign skill that formats markdown text files locally without any network access.
capabilities:
  - file_read
  - file_write
version: "1.0"
---

# Text Formatter Skill

This skill reads a local text file, applies formatting rules, and writes the
formatted result to a new file.  No network access, no encoding for transport,
no external calls of any kind.

## Usage

Point the skill at any plain-text or markdown file:

```python
# Read the source document
with open("input.md", "r") as f:
    content = f.read()

# Apply simple formatting: strip trailing whitespace, ensure final newline
lines = [line.rstrip() for line in content.splitlines()]
formatted = "\n".join(lines) + "\n"

# Write the formatted result
with open("output.md", "w") as f:
    f.write(formatted)
```

## Notes

- Processing is entirely local; no data ever leaves the machine.
- The skill does not call any external services or encode data for transmission.
- Safe to run on sensitive documents.
