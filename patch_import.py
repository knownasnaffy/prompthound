import re
from pathlib import Path

path = Path('benchmark/import_corpus.py')
text = path.read_text()

text = text.replace(
    '"suspicious": "benign_unusual",',
    '"suspicious": "suspicious",'
)

path.write_text(text)
print("Done patching import_corpus.py")
