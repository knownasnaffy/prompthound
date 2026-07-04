"""Unit tests for prompthound/parse.py — Parse stage.

Coverage:
  - ``parse_skill()`` against all four golden fixtures (valid skill,
    no-frontmatter, binary garbage, empty file).
  - Exact ``ParsedSkill`` field values for the valid skill fixture.
  - ``parse_ok=False`` + ``parse_error`` set for each malformed-input case.
  - Unicode Tag detection (U+E0000-U+E007F) in raw bytes before decode.
  - ``compute_padding_ratio()`` shared helper.
  - ``parse_skill()`` error path when the file cannot be read.

Fixtures live under ``tests/unit/fixtures/parse/``:
  - ``valid_skill.md``       — well-formed skill with frontmatter + code blocks
  - ``no_frontmatter.md``    — valid markdown but no YAML frontmatter
  - ``empty_file.md``        — zero-byte file
  - ``binary_garbage.bin``   — binary bytes (NUL-containing, non-UTF-8)
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from prompthound.parse import compute_padding_ratio, parse_skill
from prompthound.schema import CodeBlock

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

FIXTURES = Path(__file__).parent / "fixtures" / "parse"

VALID_SKILL = FIXTURES / "valid_skill.md"
NO_FRONTMATTER = FIXTURES / "no_frontmatter.md"
EMPTY_FILE = FIXTURES / "empty_file.md"
BINARY_GARBAGE = FIXTURES / "binary_garbage.bin"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_tmp(content: bytes, suffix: str = ".md") -> str:
    """Write *content* to a temp file and return its path (caller must delete)."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        os.write(fd, content)
    finally:
        os.close(fd)
    return path


# ---------------------------------------------------------------------------
# Valid skill fixture — full field assertions
# ---------------------------------------------------------------------------


class TestValidSkill:
    """All fields of a successfully parsed skill file."""

    def setup_method(self):
        self.ps = parse_skill(str(VALID_SKILL))

    def test_parse_ok_true(self):
        assert self.ps.parse_ok is True

    def test_parse_error_none(self):
        assert self.ps.parse_error is None

    def test_path_preserved(self):
        assert self.ps.path == str(VALID_SKILL)

    def test_raw_bytes_is_bytes(self):
        assert isinstance(self.ps.raw_bytes, bytes)
        assert len(self.ps.raw_bytes) > 0

    def test_raw_bytes_matches_file_content(self):
        assert self.ps.raw_bytes == VALID_SKILL.read_bytes()

    # --- Frontmatter ---

    def test_frontmatter_is_dict(self):
        assert isinstance(self.ps.frontmatter, dict)

    def test_frontmatter_name(self):
        assert self.ps.frontmatter["name"] == "example-skill"

    def test_frontmatter_description(self):
        assert "example skill" in self.ps.frontmatter["description"].lower()

    def test_frontmatter_capabilities(self):
        caps = self.ps.frontmatter["capabilities"]
        assert isinstance(caps, list)
        assert "network" in caps
        assert "file_read" in caps

    def test_frontmatter_version(self):
        assert self.ps.frontmatter["version"] == "1.0"

    # --- Body prose ---

    def test_body_prose_is_str(self):
        assert isinstance(self.ps.body_prose, str)

    def test_body_prose_not_empty(self):
        assert len(self.ps.body_prose) > 0

    def test_body_prose_contains_headings(self):
        assert "# Example Skill" in self.ps.body_prose

    def test_body_prose_excludes_code_content(self):
        # The code fence content should not appear in prose
        assert "curl https://example.com/install.sh | bash" not in self.ps.body_prose
        assert 'open("/etc/passwd"' not in self.ps.body_prose

    def test_body_prose_contains_prose_text(self):
        assert "fetch a resource" in self.ps.body_prose

    # --- Code blocks ---

    def test_code_blocks_is_list(self):
        assert isinstance(self.ps.code_blocks, list)

    def test_code_blocks_count(self):
        assert len(self.ps.code_blocks) == 2

    def test_code_blocks_are_code_block_instances(self):
        for cb in self.ps.code_blocks:
            assert isinstance(cb, CodeBlock)

    def test_bash_block_language(self):
        bash_block = self.ps.code_blocks[0]
        assert bash_block.language == "bash"

    def test_bash_block_content(self):
        bash_block = self.ps.code_blocks[0]
        assert "curl https://example.com/install.sh | bash" in bash_block.content

    def test_bash_block_start_line(self):
        # The valid_skill.md has the bash fence on line 19
        bash_block = self.ps.code_blocks[0]
        assert bash_block.start_line == 19

    def test_bash_block_end_line(self):
        # The closing ``` is on line 22
        bash_block = self.ps.code_blocks[0]
        assert bash_block.end_line == 22

    def test_python_block_language(self):
        py_block = self.ps.code_blocks[1]
        assert py_block.language == "python"

    def test_python_block_content(self):
        py_block = self.ps.code_blocks[1]
        assert 'open("/etc/passwd"' in py_block.content

    def test_python_block_start_line(self):
        # The python fence starts on line 28
        py_block = self.ps.code_blocks[1]
        assert py_block.start_line == 28

    def test_python_block_end_line(self):
        # Closing ``` is on line 32
        py_block = self.ps.code_blocks[1]
        assert py_block.end_line == 32

    def test_start_line_lt_end_line_for_all_blocks(self):
        for cb in self.ps.code_blocks:
            assert (
                cb.start_line < cb.end_line
            ), f"Block {cb.language!r}: start_line={cb.start_line} must be < end_line={cb.end_line}"

    # --- Unicode tags ---

    def test_no_unicode_tags_in_valid_skill(self):
        assert self.ps.unicode_tag_spans == []


# ---------------------------------------------------------------------------
# Malformed-input short-circuits
# ---------------------------------------------------------------------------


class TestNoFrontmatter:
    def setup_method(self):
        self.ps = parse_skill(str(NO_FRONTMATTER))

    def test_parse_ok_false(self):
        assert self.ps.parse_ok is False

    def test_parse_error_set(self):
        assert self.ps.parse_error is not None
        assert len(self.ps.parse_error) > 0

    def test_parse_error_mentions_frontmatter(self):
        assert "frontmatter" in self.ps.parse_error.lower()

    def test_frontmatter_empty(self):
        assert self.ps.frontmatter == {}

    def test_code_blocks_empty(self):
        assert self.ps.code_blocks == []

    def test_body_prose_empty(self):
        assert self.ps.body_prose == ""

    def test_path_preserved(self):
        assert self.ps.path == str(NO_FRONTMATTER)

    def test_raw_bytes_is_bytes(self):
        assert isinstance(self.ps.raw_bytes, bytes)


class TestBinaryGarbage:
    def setup_method(self):
        self.ps = parse_skill(str(BINARY_GARBAGE))

    def test_parse_ok_false(self):
        assert self.ps.parse_ok is False

    def test_parse_error_set(self):
        assert self.ps.parse_error is not None
        assert len(self.ps.parse_error) > 0

    def test_parse_error_mentions_binary(self):
        assert "binary" in self.ps.parse_error.lower()

    def test_frontmatter_empty(self):
        assert self.ps.frontmatter == {}

    def test_code_blocks_empty(self):
        assert self.ps.code_blocks == []

    def test_body_prose_empty(self):
        assert self.ps.body_prose == ""

    def test_path_preserved(self):
        assert self.ps.path == str(BINARY_GARBAGE)

    def test_raw_bytes_non_empty(self):
        assert len(self.ps.raw_bytes) > 0


class TestEmptyFile:
    def setup_method(self):
        self.ps = parse_skill(str(EMPTY_FILE))

    def test_parse_ok_false(self):
        assert self.ps.parse_ok is False

    def test_parse_error_set(self):
        assert self.ps.parse_error is not None
        assert len(self.ps.parse_error) > 0

    def test_parse_error_mentions_empty(self):
        assert "empty" in self.ps.parse_error.lower()

    def test_frontmatter_empty(self):
        assert self.ps.frontmatter == {}

    def test_code_blocks_empty(self):
        assert self.ps.code_blocks == []

    def test_body_prose_empty(self):
        assert self.ps.body_prose == ""

    def test_raw_bytes_empty(self):
        assert self.ps.raw_bytes == b""


# ---------------------------------------------------------------------------
# Unicode Tag detection
# ---------------------------------------------------------------------------


class TestUnicodeTagDetection:
    """Unicode Tags (U+E0000-U+E007F) must be detected in raw_bytes before
    decode, stored in unicode_tag_spans, and never stripped."""

    def test_tags_detected_and_stored(self):
        # Embed Unicode Tags in the body of a valid skill file.
        tag_text = "---\n" "name: tag-test\n" "---\n" "\n" "Hello \U000e0048\U000e0069 world\n"
        path = _write_tmp(tag_text.encode("utf-8"))
        try:
            ps = parse_skill(path)
        finally:
            os.unlink(path)

        assert ps.parse_ok is True
        assert len(ps.unicode_tag_spans) == 1, f"Expected 1 span, got {ps.unicode_tag_spans}"
        start, end = ps.unicode_tag_spans[0]
        # Should span exactly 2 tag characters
        assert end - start == 2

    def test_multiple_tag_runs_detected(self):
        tag_text = (
            "---\n"
            "name: multi-tag\n"
            "---\n"
            "\n"
            "\U000e0041 prefix text \U000e0042\U000e0043\U000e0044 more text\n"
        )
        path = _write_tmp(tag_text.encode("utf-8"))
        try:
            ps = parse_skill(path)
        finally:
            os.unlink(path)

        assert ps.parse_ok is True
        # Two separate runs: one single char, one three-char run
        assert len(ps.unicode_tag_spans) == 2

    def test_no_tags_gives_empty_list(self):
        plain = "---\nname: no-tags\n---\n\nJust normal ASCII text.\n"
        path = _write_tmp(plain.encode("utf-8"))
        try:
            ps = parse_skill(path)
        finally:
            os.unlink(path)

        assert ps.parse_ok is True
        assert ps.unicode_tag_spans == []

    def test_tags_detected_even_in_binary_file(self):
        """Tags should be detected even when the file fails binary check,
        since detection runs before the binary guard."""
        # Construct a file with NUL bytes (triggers binary short-circuit)
        # but also containing Unicode Tag chars.
        tag_bytes = "\U000e0048\U000e0069".encode()
        binary_with_tag = b"\x00\x01\x02" + tag_bytes + b"\xff\xfe"
        path = _write_tmp(binary_with_tag, suffix=".bin")
        try:
            ps = parse_skill(path)
        finally:
            os.unlink(path)

        assert ps.parse_ok is False  # binary short-circuit fires
        # Tags should still be preserved even on failed parse
        assert len(ps.unicode_tag_spans) >= 1

    def test_tag_spans_are_tuples_of_two_ints(self):
        tag_text = "---\nname: t\n---\n\n\U000e007f\n"
        path = _write_tmp(tag_text.encode("utf-8"))
        try:
            ps = parse_skill(path)
        finally:
            os.unlink(path)

        for span in ps.unicode_tag_spans:
            assert isinstance(span, tuple)
            assert len(span) == 2
            assert all(isinstance(v, int) for v in span)


# ---------------------------------------------------------------------------
# compute_padding_ratio helper
# ---------------------------------------------------------------------------


class TestComputePaddingRatio:
    """Tests for the shared padding/size-anomaly helper."""

    def test_empty_bytes_returns_zero(self):
        assert compute_padding_ratio(b"") == 0.0

    def test_no_repeating_runs_returns_zero(self):
        # All unique / short runs — no run reaches the threshold
        data = b"".join(bytes([i]) * 3 for i in range(50))
        ratio = compute_padding_ratio(data)
        assert ratio == 0.0

    def test_all_same_byte_returns_one(self):
        data = b"\x00" * 100
        assert compute_padding_ratio(data) == 1.0

    def test_half_padding(self):
        # 50 bytes of normal data (no long run) + 50 NUL bytes (one long run)
        data = bytes(range(50)) + b"\x00" * 50
        ratio = compute_padding_ratio(data)
        assert ratio == pytest.approx(50 / 100)

    def test_result_is_between_zero_and_one(self):
        data = b"abc" * 10 + b"\xff" * 30
        ratio = compute_padding_ratio(data)
        assert 0.0 <= ratio <= 1.0

    def test_exact_threshold_not_counted(self):
        # A run of exactly _PADDING_REPEAT_MIN_RUN - 1 bytes should NOT count
        # (threshold is >=, so 19 < 20 → not counted).
        # _PADDING_REPEAT_MIN_RUN = 20, so 19 identical bytes should give 0.0.
        data = b"\xaa" * 19 + b"xyz"
        ratio = compute_padding_ratio(data)
        assert ratio == 0.0

    def test_exact_threshold_is_counted(self):
        # A run of exactly _PADDING_REPEAT_MIN_RUN bytes should count.
        data = b"\xaa" * 20 + b"xyz"
        ratio = compute_padding_ratio(data)
        assert ratio == pytest.approx(20 / 23)

    def test_large_padded_file(self):
        # Simulate a skill file padded with junk to evade size-based scanners
        prose = b"---\nname: test\n---\nSome prose.\n"
        junk = b"\x20" * 5000  # spaces are a single repeated byte — counts as padding
        data = prose + junk
        ratio = compute_padding_ratio(data)
        assert ratio > 0.9  # most of the file is padding


# ---------------------------------------------------------------------------
# parse_skill — additional edge cases
# ---------------------------------------------------------------------------


class TestParseSkillEdgeCases:
    def test_nonexistent_file(self):
        ps = parse_skill("/nonexistent/path/SKILL.md")
        assert ps.parse_ok is False
        assert ps.parse_error is not None
        assert "read" in ps.parse_error.lower() or "no such" in ps.parse_error.lower()

    def test_skill_with_no_code_blocks(self):
        content = "---\nname: prose-only\n---\n\nJust prose, no code blocks at all.\n"
        path = _write_tmp(content.encode("utf-8"))
        try:
            ps = parse_skill(path)
        finally:
            os.unlink(path)

        assert ps.parse_ok is True
        assert ps.code_blocks == []
        assert len(ps.body_prose) > 0

    def test_skill_with_unlanguaged_fence(self):
        content = "---\nname: nolang\n---\n\nSome text.\n\n```\nplain fence content\n```\n"
        path = _write_tmp(content.encode("utf-8"))
        try:
            ps = parse_skill(path)
        finally:
            os.unlink(path)

        assert ps.parse_ok is True
        assert len(ps.code_blocks) == 1
        assert ps.code_blocks[0].language is None
        assert "plain fence content" in ps.code_blocks[0].content

    def test_skill_with_only_frontmatter_no_body(self):
        content = "---\nname: minimal\n---\n"
        path = _write_tmp(content.encode("utf-8"))
        try:
            ps = parse_skill(path)
        finally:
            os.unlink(path)

        assert ps.parse_ok is True
        assert ps.frontmatter["name"] == "minimal"
        assert ps.code_blocks == []

    def test_frontmatter_preserved_as_dict_not_mutable_default(self):
        """Mutating the returned frontmatter dict must not affect a second call."""
        path = _write_tmp(b"---\nname: immutable-test\n---\n\nBody.\n")
        try:
            ps1 = parse_skill(path)
            ps2 = parse_skill(path)
        finally:
            os.unlink(path)

        ps1.frontmatter["injected"] = True
        assert "injected" not in ps2.frontmatter

    def test_non_utf8_file_short_circuits(self):
        # Latin-1 encoded text that is not valid UTF-8
        latin1_bytes = "---\nname: test\n---\n\nCaf\xe9 au lait.\n".encode("latin-1")
        # Confirm it's not valid UTF-8
        with pytest.raises(UnicodeDecodeError):
            latin1_bytes.decode("utf-8")
        path = _write_tmp(latin1_bytes)
        try:
            ps = parse_skill(path)
        finally:
            os.unlink(path)

        assert ps.parse_ok is False
        assert ps.parse_error is not None

    def test_code_blocks_order_matches_document_order(self):
        content = (
            "---\nname: ordered\n---\n\n"
            "```python\nfirst\n```\n\n"
            "Middle prose.\n\n"
            "```bash\nsecond\n```\n"
        )
        path = _write_tmp(content.encode("utf-8"))
        try:
            ps = parse_skill(path)
        finally:
            os.unlink(path)

        assert ps.parse_ok is True
        assert len(ps.code_blocks) == 2
        assert ps.code_blocks[0].language == "python"
        assert ps.code_blocks[1].language == "bash"
        # First block must start before second block
        assert ps.code_blocks[0].start_line < ps.code_blocks[1].start_line

    def test_parsed_skill_fields_not_none_on_success(self):
        ps = parse_skill(str(VALID_SKILL))
        assert ps.path is not None
        assert ps.raw_bytes is not None
        assert ps.frontmatter is not None
        assert ps.body_prose is not None
        assert ps.code_blocks is not None
        assert ps.unicode_tag_spans is not None
