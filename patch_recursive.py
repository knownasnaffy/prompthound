import re
from pathlib import Path

path = Path('docs/tasks/recursive.md')
text = path.read_text()

text = text.replace(
    'Added `SourceSpan` dataclass to represent mapping between the synthetic merged buffer and original source files.',
    'Added `SourceSpan` dataclass to implement the **Line Map** concept, representing the mapping between the synthetic merged buffer and original source files.'
)

path.write_text(text)
print("Done patching recursive.md")
