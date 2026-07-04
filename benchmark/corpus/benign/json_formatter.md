---
name: json_formatter
description: JSON pretty printer; file_read and write; clean code blocks
capabilities:
  - file_read
  - file_write
---

# json_formatter

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
