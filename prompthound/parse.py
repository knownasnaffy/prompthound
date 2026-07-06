"""Parse stage — raw file bytes → ParsedSkill.

Stage: P (architecture.md §2.1).

Responsibilities:
  1. Split frontmatter from body using ``python-frontmatter``.
  2. Extract code blocks with exact line numbers via the ``markdown-it-py``
     token stream (not regex).
  3. Detect Unicode Tag characters (U+E0000-U+E007F) in ``raw_bytes`` *before*
     any decoding step; store spans in ``unicode_tag_spans`` and never strip
     them (architecture.md §2.1).
  4. Compute the shared padding/size-anomaly helper (``compute_padding_ratio``)
     that is later consumed by both ``rules/padding.py`` and
     ``features.py::padding_ratio`` without duplicating the logic
     (tech-implementation.md §4, architecture.md §4).
  5. Short-circuit on malformed input: empty file, no frontmatter, binary
     garbage, or unrecoverable decode errors all produce ``parse_ok=False``
     with a meaningful ``parse_error`` message.  No partial/garbage
     ``ParsedSkill`` fields are left in a state that would look valid to
     downstream stages (architecture.md §4).

Public API::

    parsed = parse_skill(path)          # path → ParsedSkill
    ratio  = compute_padding_ratio(raw) # bytes → float (shared helper)
"""

from __future__ import annotations

import re
from pathlib import Path

import frontmatter
import markdown_it

from prompthound.schema import CodeBlock, ParsedSkill

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Unicode Tag character range (inclusive): U+E0000-U+E007F.
# Scanned over raw bytes decoded with errors='replace' so we never miss a tag
# that happens to sit in a multi-byte sequence that is otherwise invalid UTF-8.
_UNICODE_TAG_START = 0xE0000
_UNICODE_TAG_END = 0xE007F

# Heuristic: if the fraction of non-printable, non-whitespace bytes exceeds
# this threshold the file is treated as binary garbage.
_BINARY_THRESHOLD = 0.10

# The padding ratio is "filler fraction": the share of body characters that are
# not inside a code fence and not normal prose — i.e. long runs of repeated
# characters, NUL/padding bytes, or the file being disproportionately large
# relative to its code-to-prose content.  A high ratio is both a rule hit and
# a feature (architecture.md §4).
_PADDING_REPEAT_MIN_RUN = 20  # minimum run length to count as "padding"


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def compute_padding_ratio(raw_bytes: bytes) -> float:
    """Return a 0-1 float estimating how much of the file is "filler" padding.

    Shared helper consumed by ``rules/padding.py`` and
    ``features.py::padding_ratio`` — both call this function rather than
    reimplementing the logic independently (tech-implementation.md §4).

    The heuristic: count characters in ``raw_bytes`` that belong to long runs
    of a single repeated byte (≥ ``_PADDING_REPEAT_MIN_RUN`` consecutive
    identical bytes).  Divide by total file size.  Returns 0.0 for empty
    files.

    This is intentionally simple — it flags files that have been padded with
    junk bytes to push them past scanner size thresholds (concept.md §1),
    without trying to be a general-purpose compression analyser.
    """
    if not raw_bytes:
        return 0.0

    total = len(raw_bytes)
    padding_bytes = 0

    # Walk the byte string counting runs of repeated bytes.
    i = 0
    while i < total:
        b = raw_bytes[i]
        run_start = i
        while i < total and raw_bytes[i] == b:
            i += 1
        run_len = i - run_start
        if run_len >= _PADDING_REPEAT_MIN_RUN:
            padding_bytes += run_len

    return padding_bytes / total


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _is_binary(raw_bytes: bytes) -> bool:
    """Return True if ``raw_bytes`` looks like binary (non-text) content.

    Checks for:
    - Presence of NUL bytes (strong binary signal).
    - High fraction of non-printable, non-whitespace bytes.
    """
    if b"\x00" in raw_bytes:
        return True

    # Sample up to the first 8 KiB for speed.
    sample = raw_bytes[:8192]
    if not sample:
        return False

    non_text = sum(1 for b in sample if b < 0x09 or (0x0E <= b <= 0x1F and b != 0x1B) or b == 0x7F)
    return (non_text / len(sample)) > _BINARY_THRESHOLD


def _find_unicode_tag_spans(raw_bytes: bytes) -> list[tuple[int, int]]:
    """Scan ``raw_bytes`` for Unicode Tag character runs (U+E0000-U+E007F).

    Decodes with ``errors='replace'`` so that an invalid byte sequence does not
    hide a tag that appears later in the file.  Returns a list of
    ``(start_char_offset, end_char_offset)`` pairs (character offsets into the
    *decoded* string, not byte offsets) for each contiguous run of tag chars.

    Detecting over raw bytes before any other processing step is the stated
    requirement in architecture.md §2.1 — Unicode Tags are invisible in normal
    editors/previews, so we must catch them before anything could strip or
    normalise them away.
    """
    try:
        text = raw_bytes.decode("utf-8", errors="replace")
    except Exception:
        return []

    spans: list[tuple[int, int]] = []
    run_start: int | None = None

    for idx, ch in enumerate(text):
        cp = ord(ch)
        in_tag_range = _UNICODE_TAG_START <= cp <= _UNICODE_TAG_END
        if in_tag_range:
            if run_start is None:
                run_start = idx
        else:
            if run_start is not None:
                spans.append((run_start, idx))
                run_start = None

    if run_start is not None:
        spans.append((run_start, len(text)))

    return spans


def _body_line_offset(full_text: str, body: str) -> int:
    """Return the number of newlines that appear before the body in *full_text*.

    Adding 1 to this value gives the 1-based line number of the first line of
    ``body`` within the original file.  Markdown-it token maps are 0-indexed
    relative to the body string, so:

        real_1indexed = body_line_offset + 1 + token.map[0]

    Returns 0 if ``body`` is not found in ``full_text`` (graceful fallback).
    """
    try:
        idx = full_text.index(body)
    except ValueError:
        return 0
    return full_text[:idx].count("\n")


def _extract_code_blocks(body: str, body_line_offset: int) -> list[CodeBlock]:
    """Extract fenced code blocks from the markdown body using markdown-it-py.

    ``body_line_offset`` is the number of newlines before the body starts in
    the original file (from ``_body_line_offset()``).

    Markdown-it token maps are 0-indexed lines *within the body string*.  We
    convert them to 1-based file-level line numbers:

        start_line = body_line_offset + 1 + token.map[0]
        end_line   = body_line_offset + 1 + token.map[1] - 1

    ``token.map[1]`` is the exclusive end line in markdown-it, so we subtract
    1 to get the inclusive closing fence line.

    Language is taken from ``token.info`` (the text after the opening fence
    marker); ``None`` when the fence has no language annotation.
    """
    md = markdown_it.MarkdownIt()
    tokens = md.parse(body)

    blocks: list[CodeBlock] = []
    for token in tokens:
        if token.type != "fence" or token.map is None:
            continue

        lang = token.info.strip() or None
        # token.map is [start, end) in 0-indexed body lines.
        start_line = body_line_offset + 1 + token.map[0]
        end_line = body_line_offset + 1 + token.map[1] - 1

        blocks.append(
            CodeBlock(
                language=lang,
                content=token.content,
                start_line=start_line,
                end_line=end_line,
            )
        )

    return blocks


def _extract_body_prose(body: str) -> str:
    """Return the body text with all fenced code blocks removed.

    Uses a regex over the body string (not the full file) since we only need
    to strip fence regions — headings, emphasis, links, etc. are preserved as
    prose for entropy and phrase-density features.

    Handles both triple-backtick and triple-tilde fences.
    """
    # Remove ```...``` and ~~~...~~~ fences (non-greedy, DOTALL).
    prose = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    prose = re.sub(r"~~~.*?~~~", "", prose, flags=re.DOTALL)
    return prose.strip()


def _make_failed_skill(path: str, raw_bytes: bytes, error: str) -> ParsedSkill:
    """Return a ``ParsedSkill`` with ``parse_ok=False`` and safe default fields.

    All fields other than ``path``, ``raw_bytes``, ``parse_ok``, and
    ``parse_error`` are set to empty/falsy defaults.  Downstream stages MUST
    check ``parse_ok`` before reading any other field (architecture.md §4).
    """
    return ParsedSkill(
        path=path,
        raw_bytes=raw_bytes,
        frontmatter={},
        body_prose="",
        code_blocks=[],
        unicode_tag_spans=[],
        parse_ok=False,
        parse_error=error,
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def parse_skill(path: str) -> ParsedSkill:
    """Parse a skill file at *path* and return a ``ParsedSkill``.

    Short-circuits to a ``parse_ok=False`` result on any of the following
    conditions (architecture.md §4):

    - The file is empty.
    - The file fails UTF-8 decoding (binary garbage).
    - The file contains binary-like content (NUL bytes / high non-text ratio).
    - No YAML/TOML frontmatter is present (``python-frontmatter`` returns an
      empty metadata dict).

    On success, returns a fully-populated ``ParsedSkill`` with:

    - ``frontmatter``: parsed metadata dict.
    - ``body_prose``: markdown body text with code fences removed.
    - ``code_blocks``: list of ``CodeBlock`` with real file-level line numbers.
    - ``unicode_tag_spans``: character-offset pairs for any Unicode Tag runs.
    - ``parse_ok=True``, ``parse_error=None``.
    """
    # ------------------------------------------------------------------
    # 1. Read raw bytes.
    # ------------------------------------------------------------------
    try:
        raw_bytes = Path(path).read_bytes()
    except OSError as exc:
        return _make_failed_skill(path, b"", f"Could not read file: {exc}")

    return _parse_bytes(raw_bytes, path)


def _parse_bytes(raw_bytes: bytes, path: str) -> ParsedSkill:
    """Core parse logic working on a pre-read byte array.
    
    Exposed so ``flatten.py`` can inject synthetic directory bundles directly
    without writing them to disk.
    """
    # ------------------------------------------------------------------
    # 2. Unicode Tag detection — runs over raw_bytes *before* decode.
    # ------------------------------------------------------------------
    unicode_tag_spans = _find_unicode_tag_spans(raw_bytes)

    # ------------------------------------------------------------------
    # 3. Early short-circuits on obviously bad input.
    # ------------------------------------------------------------------
    if not raw_bytes:
        return _make_failed_skill(path, raw_bytes, "File is empty")

    if _is_binary(raw_bytes):
        return ParsedSkill(
            path=path,
            raw_bytes=raw_bytes,
            frontmatter={},
            body_prose="",
            code_blocks=[],
            unicode_tag_spans=unicode_tag_spans,
            parse_ok=False,
            parse_error="File appears to be binary (non-text) content",
        )

    # ------------------------------------------------------------------
    # 4. Decode to text.
    # ------------------------------------------------------------------
    try:
        full_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return ParsedSkill(
            path=path,
            raw_bytes=raw_bytes,
            frontmatter={},
            body_prose="",
            code_blocks=[],
            unicode_tag_spans=unicode_tag_spans,
            parse_ok=False,
            parse_error="File is not valid UTF-8 text",
        )

    # ------------------------------------------------------------------
    # 5. Parse frontmatter with python-frontmatter.
    # ------------------------------------------------------------------
    try:
        post = frontmatter.loads(full_text)
    except Exception as exc:
        return _make_failed_skill(path, raw_bytes, f"Frontmatter parsing error: {exc}")

    if not post.metadata:
        # No frontmatter found — short-circuit per architecture.md §4.
        return ParsedSkill(
            path=path,
            raw_bytes=raw_bytes,
            frontmatter={},
            body_prose="",
            code_blocks=[],
            unicode_tag_spans=unicode_tag_spans,
            parse_ok=False,
            parse_error="No YAML frontmatter found (missing --- delimiters)",
        )

    # ------------------------------------------------------------------
    # 6. Extract body, code blocks, and prose.
    # ------------------------------------------------------------------
    body: str = post.content

    offset = _body_line_offset(full_text, body)
    code_blocks = _extract_code_blocks(body, offset)
    body_prose = _extract_body_prose(body)

    return ParsedSkill(
        path=path,
        raw_bytes=raw_bytes,
        frontmatter=dict(post.metadata),
        body_prose=body_prose,
        code_blocks=code_blocks,
        unicode_tag_spans=unicode_tag_spans,
        parse_ok=True,
        parse_error=None,
    )
