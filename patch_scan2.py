import re
from pathlib import Path

path = Path('tests/integration/test_scan.py')
text = path.read_text()

text = text.replace(
    '_BENIGN_FILE = _ROOT_DIR / "benchmark" / "corpus" / "benign" / "case_00002"',
    '_BENIGN_FILE = _ROOT_DIR / "benchmark" / "corpus" / "benign" / "case_00000"'
)

path.write_text(text)
print("Done patching test_scan.")
