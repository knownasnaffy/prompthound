---
name: doc-formatter
description: >
  Converts inline docstrings to markdown reference pages. Reads Python/JS/TS
  source files, extracts docstrings and type signatures, and writes structured
  markdown documentation files. Supports Sphinx/Google/NumPy docstring formats.
capabilities:
  - file_read
  - file_write
version: "1.5"
author: self-authored
license: Apache-2.0
---

# Documentation Formatter

Automatically generates markdown reference documentation from inline docstrings
in Python, JavaScript, or TypeScript source files. The agent parses the source,
extracts function/class/method signatures and their docstrings, and writes one
markdown file per module.

## Output Format

Each generated markdown file has:

- A top-level heading with the module name.
- One section per public function or class.
- Type signatures, parameter tables, return value descriptions, and usage
  examples extracted from the docstring.
- A "See Also" section if the docstring contains cross-references.

Example:

```markdown
# mymodule

## `my_function(x: int, y: int) -> int`

Adds two numbers together.

### Parameters
- `x` (int): The first number.
- `y` (int): The second number.

### Returns
`int`: The sum of `x` and `y`.

### Example
```python
result = my_function(3, 5)
assert result == 8
```
```

## Usage

```
agent run doc-formatter --source src/ --output docs/reference/
```

The agent scans every `.py`, `.js`, and `.ts` file under `src/`, writes one
markdown file per source file into `docs/reference/`, and generates an index
page linking to each module.

## Configuration

| Parameter         | Default        | Description                                       |
|-------------------|----------------|---------------------------------------------------|
| `style`           | auto           | Docstring style: auto, sphinx, google, numpy.     |
| `include_private` | false          | Include functions/methods starting with `_`.     |
| `index_file`      | `index.md`     | Name of the generated index file.                 |
| `overwrite`       | true           | Overwrite existing markdown files.                |

## Notes

- This skill **writes** files into the output directory. Always check the
  generated markdown before committing it to the repo.
- If your source files have inline examples, those are extracted and rendered
  as code blocks in the markdown output.
- This is not a full API doc generator — it only processes the docstrings you
  already wrote. For missing docstrings, the output just shows the signature
  with a "No documentation found" note.
