---
name: test-classifier-benign
description: A skill that reviews code for common style issues and suggests improvements.
capabilities:
  - file_read
version: "1.0"
---

# Code Review Skill

This skill reads a source file and produces a structured review report highlighting
style issues, potential bugs, unused variables, and improvement suggestions.
All processing happens locally — no files are sent over the network.

## Usage

Provide the path to the source file you want reviewed:

```python
with open("source.py", "r") as f:
    source = f.read()
```

The skill will parse the code, apply style checks, and return a list of findings.

## What it checks

- Code style conformance (PEP 8 for Python, standard conventions for other languages)
- Variable and function naming conventions
- Function length and cyclomatic complexity
- Missing or incomplete docstrings
- Unused imports and variables
- Overly nested conditionals that could be simplified
- Magic numbers that should be named constants

## Output format

Each finding is a dict with the following keys:

```python
{
    "line": 42,
    "severity": "warn",
    "rule": "missing-docstring",
    "message": "Function 'process_items' has no docstring."
}
```

Findings are grouped by severity: errors first, then warnings, then informational notes.

## Configuration

The review behaviour can be customised by providing a config dict:

```python
config = {
    "max_function_lines": 50,
    "max_nesting_depth": 4,
    "ignore_rules": ["magic-number"],
    "docstring_required": True,
}
```

## Limitations

This skill analyses syntax and structure only — it does not execute the code or
perform dynamic analysis. For runtime behaviour, use a dedicated testing skill.
