import pytest
import os
from prompthound.flatten import flatten_bundle, flatten_single, SourceSpan


def test_flatten_single(tmp_path):
    f = tmp_path / "SKILL.md"
    f.write_text("Hello\nWorld", encoding="utf-8")

    buffer, manifest = flatten_single(f)
    assert buffer == "Hello\nWorld"
    assert manifest.member_count == 1

    assert manifest.get_source(0) == (str(f), 0)
    assert manifest.get_source(1) == (str(f), 1)


def test_flatten_bundle(tmp_path):
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()

    f1 = bundle_dir / "SKILL.md"
    f1.write_text("Anchor", encoding="utf-8")

    f2 = bundle_dir / "setup.sh"
    f2.write_text("echo", encoding="utf-8")

    buffer, manifest = flatten_bundle(bundle_dir)
    lines = buffer.split("\n")

    assert "--- BEGIN MEMBER: SKILL.md ---" in lines
    assert "--- BEGIN MEMBER: setup.sh ---" in lines

    assert manifest.member_count == 2

    # Let's find SKILL.md's content
    anchor_idx = lines.index("Anchor")
    filepath, orig_line = manifest.get_source(anchor_idx)
    assert filepath == "SKILL.md"
    assert orig_line == 0
