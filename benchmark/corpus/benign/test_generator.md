---
name: test-generator
description: >
  Generates unit test stubs for Python functions and classes. Reads a source
  file, identifies public functions and methods, and produces pytest test
  skeletons with docstrings, parameter tables, and TODO markers for the
  developer to fill in.
capabilities:
  - file_read
version: "2.0"
author: self-authored
license: MIT
---

# Test Generator

Automatically scaffolds pytest test files from Python source code. The agent
reads the target source file, discovers public API surface (functions, methods,
classes), and writes a corresponding `test_<module>.py` file with:

- One test function per public function or method.
- Docstring describing what the test should verify.
- A `@pytest.mark.parametrize` placeholder with sample inputs derived from
  the function's type hints and docstring.
- `# TODO:` markers indicating where the developer needs to add assertions.

## Usage

```
agent run test-generator --source src/mymodule.py --output tests/
```

The generated file looks like:

```python
import pytest
from mymodule import my_function


@pytest.mark.parametrize("input, expected", [
    # TODO: add test cases here
])
def test_my_function(input, expected):
    """Test that my_function returns the expected result for valid input."""
    result = my_function(input)
    # TODO: assert result == expected
    raise NotImplementedError("fill in assertion")
```

## Configuration

| Parameter         | Default | Description                                              |
|-------------------|---------|----------------------------------------------------------|
| `skip_private`    | true    | Skip functions/methods starting with `_`.                |
| `skip_dunder`     | true    | Skip `__dunder__` methods.                               |
| `include_classes` | true    | Generate a test class for each source class.             |
| `overwrite`       | false   | Overwrite an existing test file if one already exists.   |

## Notes

- The generated tests are stubs — they will fail until the developer fills in
  the assertions. This is intentional: the skill saves setup time, not
  thinking time.
- The skill reads only the source file you point it at; it does not traverse
  the whole project.
- No test is ever auto-run by this skill.
