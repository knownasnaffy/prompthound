import pytest
from pathlib import Path
from prompthound.flatten import parse_directory
from prompthound.schema import ParsedSkill

def test_parse_directory_valid(tmp_path: Path):
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("---\nname: Test\ndescription: Test\n---\nBody", encoding="utf-8")
    
    script_file = tmp_path / "script.py"
    script_file.write_text("print('hello')", encoding="utf-8")
    
    parsed = parse_directory(str(tmp_path))
    assert parsed.parse_ok is True
    assert parsed.source_manifest is not None
    assert len(parsed.source_manifest) == 2
    
    # Check that both members are represented in raw_bytes
    decoded = parsed.raw_bytes.decode("utf-8")
    assert "BEGIN MEMBER" in decoded
    assert "print('hello')" in decoded

def test_parse_directory_missing_skill_md(tmp_path: Path):
    script_file = tmp_path / "script.py"
    script_file.write_text("print('hello')", encoding="utf-8")
    
    parsed = parse_directory(str(tmp_path))
    assert parsed.parse_ok is False
    assert "SKILL.md" in parsed.parse_error

def test_parse_directory_not_a_dir(tmp_path: Path):
    file_path = tmp_path / "not_a_dir.txt"
    file_path.write_text("hello", encoding="utf-8")
    
    parsed = parse_directory(str(file_path))
    assert parsed.parse_ok is False
    assert "No SKILL.md or AGENTS.md entrypoint found in directory" in parsed.parse_error
