---
name: csv_to_json
description: CSV to JSON converter; file_read and write; no network
capabilities:
  - file_read
  - file_write
---

# csv_to_json

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
