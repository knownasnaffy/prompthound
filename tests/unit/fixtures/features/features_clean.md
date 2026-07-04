---
name: clean-formatter-skill
description: A skill that formats text documents and saves them locally.
capabilities:
  - file_read
  - file_write
version: "1.0"
---

# Document Formatter Skill

This skill reads a text document, formats it, and writes the result back.
All processing is done locally on disk.

## Usage

Provide a path to the document you want to format:

```python
with open("input.txt", "r") as f:
    data = f.read()

formatted = data.strip().upper()

with open("output.txt", "w") as f:
    f.write(formatted)
```

## Notes

This skill only accesses local files on disk.
