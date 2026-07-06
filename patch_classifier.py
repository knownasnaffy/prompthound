import re
from pathlib import Path

path = Path('tests/unit/test_classifier.py')
text = path.read_text()

# 1. Fix paths
text = text.replace(
    'CORPUS_MALICIOUS = _ROOT / "benchmark" / "corpus" / "malicious" / "clawhavoc_shell_pipe.md"',
    'CORPUS_MALICIOUS = _ROOT / "benchmark" / "corpus" / "malicious" / "case_00001"'
)
text = text.replace(
    'CORPUS_BENIGN = _ROOT / "benchmark" / "corpus" / "benign" / "code_review_assistant.md"',
    'CORPUS_BENIGN = _ROOT / "benchmark" / "corpus" / "benign" / "case_00000"'
)
text = text.replace(
    'solid_benign_path = _ROOT / "benchmark" / "corpus" / "benign" / "api_schema_validator.md"',
    'solid_benign_path = _ROOT / "benchmark" / "corpus" / "benign" / "case_00002"'
)

# 2. Fix parse_and_extract
old_extract = '''def _parse_and_extract(path: Path):
    """Parse a skill file and extract its FeatureVector."""
    from prompthound.features import extract_features
    from prompthound.parse import parse_skill

    parsed = parse_skill(str(path))
    assert parsed.parse_ok, f"Parse failed for {path}: {parsed.parse_error}"
    return extract_features(parsed)'''

new_extract = '''def _parse_and_extract(path: Path):
    """Parse a skill file and extract its FeatureVector."""
    from prompthound.features import extract_features
    from prompthound.parse import parse_skill
    from prompthound.flatten import parse_directory

    if path.is_dir():
        parsed = parse_directory(str(path))
    else:
        parsed = parse_skill(str(path))
    assert parsed.parse_ok, f"Parse failed for {path}: {parsed.parse_error}"
    return extract_features(parsed)'''

text = text.replace(old_extract, new_extract)

path.write_text(text)
print("Done patching classifier tests.")
