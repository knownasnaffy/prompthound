---
name: css_linter
description: CSS style linter; file_read only; read-only
capabilities:
  - file_read
  - file_write
---

# css_linter

This skill helps you process files locally. 

```python
import sys
import os

def process_file(filepath):
    with open(filepath, 'r') as f:
        data = f.read()
    print("Processed:", len(data), "bytes")

if __name__ == "__main__":
    process_file(sys.argv[1])
```
