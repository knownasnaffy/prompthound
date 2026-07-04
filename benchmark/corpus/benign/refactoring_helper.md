---
name: refactoring-helper
description: >
  Identifies refactoring opportunities in Python source files: long functions,
  duplicate code blocks, deeply nested conditionals, feature envy, and data
  clumps. Produces a prioritised list of suggested refactorings with
  before/after sketches.
capabilities:
  - file_read
version: "1.0"
author: self-authored
license: MIT
---

# Refactoring Helper

Static analysis skill that surfaces refactoring opportunities in Python code.
Designed to be run before a major clean-up sprint, or as a regular code-health
check during development.

## Detected Patterns

### Long functions
Functions with more than 30 statements (configurable). Suggests splitting into
smaller, single-purpose helpers.

### Duplicate code
Code blocks that are structurally identical or near-identical across different
functions or modules. Suggests extracting to a shared helper.

### Deep nesting
Conditional or loop nesting deeper than 3 levels. Suggests early returns,
guard clauses, or extracting the inner logic.

### Feature envy
Functions that access fields of another class more than their own class's
fields. Suggests moving the function closer to the data it operates on.

### Data clumps
Groups of 3 or more parameters that appear together in multiple function
signatures. Suggests grouping them into a named dataclass or namedtuple.

### Dead code
Imports, variables, or functions that are never referenced. Suggests removal.

## Usage

```
agent run refactoring-helper --source src/mymodule.py
```

Scan an entire package:

```
agent run refactoring-helper --source src/ --recursive
```

Sample output:

```yaml
refactorings:
  - file: src/processor.py
    function: process_batch
    line: 87
    pattern: long_function
    statements: 54
    suggestion: "Split into process_single_item() and aggregate_results()."
    priority: high

  - file: src/utils.py
    lines: [23, 67]
    pattern: duplicate_code
    similarity: 0.91
    suggestion: "Extract repeated validation logic to validate_input()."
    priority: medium
```

## Configuration

| Parameter           | Default | Description                                                    |
|---------------------|---------|----------------------------------------------------------------|
| `max_statements`    | 30      | Function length threshold for long-function detection.         |
| `max_nesting`       | 3       | Nesting depth threshold.                                       |
| `dup_threshold`     | 0.85    | Similarity threshold for duplicate code detection (0-1).      |
| `recursive`         | false   | Scan all Python files under the source directory.              |
| `output`            | stdout  | Write report to a file instead of stdout.                      |

## Notes

- This skill is read-only and makes no changes to source files.
- Suggested refactorings are advisory — apply judgement before acting on them.
- The duplicate-code detector works on AST structure, not text similarity,
  so renaming variables does not hide a duplicate from detection.
