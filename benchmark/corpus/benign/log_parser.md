---
name: log_parser
description: Apache log parser; file_read only; read-only
capabilities:
  - file_read
  - file_write
---

# log_parser

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
