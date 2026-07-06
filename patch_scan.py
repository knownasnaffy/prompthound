import re
from pathlib import Path

path = Path('tests/integration/test_scan.py')
text = path.read_text()

text = text.replace(
    '_BENIGN_FILE = _ROOT_DIR / "benchmark" / "corpus" / "benign" / "api_schema_validator.md"',
    '_BENIGN_FILE = _ROOT_DIR / "benchmark" / "corpus" / "benign" / "case_00002"'
)
text = text.replace(
    '_MALICIOUS_FILE = _ROOT_DIR / "benchmark" / "corpus" / "malicious" / "clawhavoc_shell_pipe.md"',
    '_MALICIOUS_FILE = _ROOT_DIR / "benchmark" / "corpus" / "malicious" / "case_00001"'
)

text = text.replace('["scan", str(file_path)', '["scan", "-d", str(file_path)')
text = text.replace('["scan", str(_BENIGN_FILE)', '["scan", "-d", str(_BENIGN_FILE)')
text = text.replace('["scan", str(_MALICIOUS_FILE)', '["scan", "-d", str(_MALICIOUS_FILE)')
# Wait, malformed file is a file not a directory:
text = text.replace('["scan", "-d", str(_MALFORMED_FILE)', '["scan", str(_MALFORMED_FILE)')

path.write_text(text)
print("Done patching test_scan.")
