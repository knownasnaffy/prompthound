"""Capability-chain check — ParsedSkill → list[ChainFlag].

Stage: CH (architecture.md §2.5).

Responsibilities:
  1. Extract a sequence of capability-tagged events from ``ParsedSkill``
     (frontmatter declared capabilities + body-referenced capabilities),
     each tagged with the source line number where the capability was found.
  2. Match that event sequence against a fixed set of named dangerous
     sequences using *subsequence* search (not exact-adjacency) so a chain
     split across non-adjacent lines still fires
     (tech-implementation.md §4).
  3. Return a ``list[ChainFlag]`` — one entry per matched dangerous sequence.
     An empty list is a valid, non-error result; absence of a chain is a
     normal benign outcome (architecture.md §4).

This stage reads ``ParsedSkill`` directly — not the ``FeatureVector``.  It
needs line-level spans for its explanations, which the numeric vector doesn't
carry (architecture.md §2.5, AGENTS.md §5).

Public API::

    flags = check_chains(parsed)    # ParsedSkill → list[ChainFlag]

Dangerous sequences defined here (tech-implementation.md §4):
  - ``"file_read→encode→network_send"``  : read a file, encode it, send it out
  - ``"download→write→execute"``         : download a payload, write it, run it

Additional sequences are defined in ``DANGEROUS_CHAINS`` and can be extended
by adding entries to that list — no other code changes needed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from prompthound.schema import ChainFlag, ParsedSkill

# ---------------------------------------------------------------------------
# Capability vocabulary
# ---------------------------------------------------------------------------
# Maps a capability tag to the set of keywords that signal its presence in
# body text (code blocks and prose).  Each keyword is matched as a whole word
# (\\b boundaries) to avoid false positives like "request" matching "req".
#
# The vocabulary deliberately mirrors the one used in features.py for
# ``feat_capability_mismatch_score`` so that the two stages give consistent
# answers about what "counts" as a capability reference.

_CAP_KEYWORDS: dict[str, list[str]] = {
    "file_read": [
        "open", "read", "cat", "fopen", "readfile", "read_file",
        "file_read", "fgets", "fgetc",
    ],
    "file_write": [
        "write", "fwrite", "writefile", "write_file", "file_write",
        "save", "fputs", "fputc", "truncate",
    ],
    "encode": [
        "base64", "b64encode", "b64", "encode", "hex", "binascii",
        "compress", "zlib", "gzip", "encrypt",
    ],
    "network_send": [
        "send", "post", "upload", "transmit", "exfil", "sendall",
        "requests.post", "urllib.request.urlopen",
    ],
    "network": [
        "curl", "wget", "fetch", "http", "https", "request", "network",
        "socket", "connect", "urlopen",
    ],
    "download": [
        "download", "curl", "wget", "fetch", "pull", "urllib.request",
        "requests.get", "urlretrieve",
    ],
    "execute": [
        "exec", "system", "subprocess", "popen", "eval", "execute",
        "run", "spawn", "os.system", "os.popen", "call", "check_call",
        "check_output",
    ],
}

# Pre-compile patterns: map each capability tag to a single compiled regex
# that matches any of its keywords as whole words.  Done at module load time
# so per-file scanning is fast.
_CAP_PATTERNS: dict[str, re.Pattern[str]] = {
    cap: re.compile(
        r"\b(?:" + "|".join(re.escape(kw) for kw in keywords) + r")\b",
        re.IGNORECASE,
    )
    for cap, keywords in _CAP_KEYWORDS.items()
}

# ---------------------------------------------------------------------------
# Dangerous chain definitions
# ---------------------------------------------------------------------------
# Each entry is a ``(name, sequence)`` pair where ``sequence`` is an ordered
# list of capability tags that must appear as a *subsequence* in the event
# list (not necessarily adjacent).
#
# To add a new dangerous sequence: append a tuple to this list.  No other
# code changes needed.

DANGEROUS_CHAINS: list[tuple[str, list[str]]] = [
    # Classic credential / data exfiltration chain.
    ("file_read→encode→network_send", ["file_read", "encode", "network_send"]),
    # Payload delivery chain.
    ("download→write→execute", ["download", "file_write", "execute"]),
    # Minimal two-step encode + send (a subset of the full exfil chain but
    # alarming on its own when combined with file ops elsewhere).
    ("file_read→network_send", ["file_read", "network_send"]),
    # Download and immediately execute (no intermediate write required).
    ("download→execute", ["download", "execute"]),
]

# ---------------------------------------------------------------------------
# Internal data type
# ---------------------------------------------------------------------------


@dataclass
class _CapEvent:
    """A single capability tag observed at a specific line in the file."""

    cap: str
    """The capability tag, e.g. ``"file_read"``."""

    line: int
    """1-based line number in the source file where the capability keyword was
    found."""

    source: str
    """Where the event came from: ``"frontmatter"`` or ``"body"``."""


# ---------------------------------------------------------------------------
# Event extraction
# ---------------------------------------------------------------------------


def _extract_events(parsed: ParsedSkill) -> list[_CapEvent]:
    """Return all capability events found in *parsed*, ordered by line number.

    Sources scanned:
    1. **Frontmatter** ``capabilities`` list — each declared cap is treated as
       an event at line 1 (frontmatter line numbers are not individually tracked
       by Parse; line 1 is the conventional frontmatter reference).
    2. **Code blocks** — each block's content is scanned line-by-line using the
       block's ``start_line`` offset so events carry real file-level line numbers.
    3. **Body prose** — scanned line-by-line using the actual line positions
       within the parsed body.  (Prose line numbers are approximated from the
       code block boundaries — see inline comment.)

    Events are deduplicated per (cap, line) pair so that a single line
    mentioning "base64" twice only contributes one event for "encode".
    The result is sorted by line number so subsequence matching naturally
    follows document order.
    """
    seen: set[tuple[str, int]] = set()
    events: list[_CapEvent] = []

    def _add(cap: str, line: int, source: str) -> None:
        key = (cap, line)
        if key not in seen:
            seen.add(key)
            events.append(_CapEvent(cap=cap, line=line, source=source))

    # ------------------------------------------------------------------
    # 1. Frontmatter declared capabilities.
    # ------------------------------------------------------------------
    raw_caps = parsed.frontmatter.get("capabilities", [])
    if isinstance(raw_caps, list):
        for raw_cap in raw_caps:
            cap_str = str(raw_cap).lower().strip()
            # Normalise: if the declared string is directly a known cap tag, use it.
            if cap_str in _CAP_KEYWORDS:
                _add(cap_str, 1, "frontmatter")
            else:
                # Try to match against keywords of each cap.
                for cap, keywords in _CAP_KEYWORDS.items():
                    if cap_str in keywords:
                        _add(cap, 1, "frontmatter")
                        break

    # ------------------------------------------------------------------
    # 2. Code blocks — scanned line-by-line with real file line numbers.
    # ------------------------------------------------------------------
    for block in parsed.code_blocks:
        block_lines = block.content.splitlines()
        for rel_idx, line_text in enumerate(block_lines):
            # block.start_line is 1-based and points to the opening fence.
            # Content starts one line after the opening fence.
            file_line = block.start_line + 1 + rel_idx
            for cap, pattern in _CAP_PATTERNS.items():
                if pattern.search(line_text):
                    _add(cap, file_line, "body")

    # ------------------------------------------------------------------
    # 3. Body prose — scanned line-by-line.
    #
    # ParsedSkill doesn't store body-prose line offsets directly.  We
    # approximate prose line numbers by finding the prose text inside the
    # full decoded body.  Since code blocks are stripped from prose, the
    # remaining lines are non-code prose lines — we iterate over the
    # *original body* line by line and skip lines that fall inside a code
    # block span, to get correct file-level line numbers.
    # ------------------------------------------------------------------
    # Determine the 1-based start of the body within the full file.
    # parse.py stores the body as `post.content` after frontmatter splitting;
    # body starts after the closing "---" delimiter.  We approximate by
    # counting frontmatter newlines: the body offset is
    #   (number of "---" + frontmatter lines) + 1.
    # A simpler approximation: iterate body_prose lines and map them to
    # approximate file lines by counting from the frontmatter boundary.
    # For prose, precision to the line is sufficient — sub-line accuracy is
    # not required by the schema.
    _scan_prose_lines(parsed, _add)

    events.sort(key=lambda e: e.line)
    return events


def _code_block_line_ranges(parsed: ParsedSkill) -> list[tuple[int, int]]:
    """Return the (start, end) 1-based line ranges of all code blocks."""
    return [(b.start_line, b.end_line) for b in parsed.code_blocks]


def _in_code_block(line: int, ranges: list[tuple[int, int]]) -> bool:
    """Return True if *line* falls inside any code block range."""
    return any(start <= line <= end for start, end in ranges)


def _scan_prose_lines(parsed: ParsedSkill, add_fn) -> None:
    """Scan body_prose for capability keywords, adding events via *add_fn*.

    To get file-level line numbers for prose we walk through body_prose
    line by line.  We estimate the body's starting line by counting
    newlines in the frontmatter delimiter block.

    The frontmatter block occupies lines 1..N where N is the number of lines
    in the raw frontmatter section (between the two "---" delimiters).  Rather
    than re-parsing, we use a conservative estimate:

        body_start_line = raw_bytes frontmatter newline count + 1

    If ``raw_bytes`` decode fails (shouldn't happen at this stage), we fall
    back to line 1.
    """
    if not parsed.body_prose:
        return

    try:
        full_text = parsed.raw_bytes.decode("utf-8", errors="replace")
    except Exception:
        full_text = ""

    # Locate the body within the full text to get an accurate line offset.
    # body_prose has code fences stripped; we need the *body* (with fences).
    # We estimate by finding the second "---" delimiter.
    body_offset_line = _estimate_body_start_line(full_text)
    code_ranges = _code_block_line_ranges(parsed)

    # We need to map prose lines back to file lines.  Since body_prose has
    # code fences removed, the lines in body_prose are a *subset* of the body
    # lines.  We walk the full body lines and skip code-block lines.
    full_lines = full_text.splitlines()
    # Build the list of non-code-block body lines with their file line numbers.
    non_code_lines: list[tuple[int, str]] = []
    for idx, line_text in enumerate(full_lines):
        file_line = idx + 1  # 1-based
        if file_line < body_offset_line:
            continue
        if _in_code_block(file_line, code_ranges):
            continue
        non_code_lines.append((file_line, line_text))

    # Scan only the non-code body lines.
    for file_line, line_text in non_code_lines:
        for cap, pattern in _CAP_PATTERNS.items():
            if pattern.search(line_text):
                add_fn(cap, file_line, "body")


def _estimate_body_start_line(full_text: str) -> int:
    """Return the 1-based line number where the body content begins.

    Scans for the second ``---`` delimiter that closes the frontmatter block.
    Returns 1 as a fallback if no frontmatter is found.
    """
    lines = full_text.splitlines()
    found_first = False
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "---":
            if not found_first:
                found_first = True
            else:
                # The body starts on the line *after* the closing ``---``.
                return idx + 2  # idx is 0-based; +1 for 1-based, +1 for next line
    # No closing delimiter found — body starts at line 1 as a fallback.
    return 1


# ---------------------------------------------------------------------------
# Subsequence matching
# ---------------------------------------------------------------------------


def _is_subsequence(
    sequence: list[str],
    events: list[_CapEvent],
) -> list[_CapEvent] | None:
    """Check whether *sequence* appears as a subsequence in *events*.

    Returns the matched ``_CapEvent`` objects (one per step in *sequence*) in
    order if found, or ``None`` if the sequence is not present.

    Subsequence matching means each step must appear *after* the previous one
    in document order (by line number), but they need not be adjacent.
    Multiple separate chains in the same file are reported as a single hit
    per dangerous sequence — this matches the reporting semantics in
    ``ChainFlag`` (one flag per detected sequence type).

    When multiple events match the same step (e.g., "encode" appears on lines
    5, 12, and 20), the *earliest remaining* match is chosen so the reported
    steps cover the smallest window in the file.  This is a greedy approach:
    it may miss a valid chain starting later if the earliest match for step N
    blocks a valid chain, but it is fast (O(n) per sequence) and gives good
    results in practice.
    """
    if not sequence or not events:
        return None

    matched: list[_CapEvent] = []
    event_idx = 0

    for step_cap in sequence:
        # Find the next event matching this step, starting from event_idx.
        while event_idx < len(events) and events[event_idx].cap != step_cap:
            event_idx += 1

        if event_idx >= len(events):
            # This step wasn't found — sequence is not present.
            return None

        matched.append(events[event_idx])
        event_idx += 1  # Advance past the matched event for the next step.

    return matched


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def check_chains(parsed: ParsedSkill) -> list[ChainFlag]:
    """Detect dangerous capability chains in *parsed* and return ``ChainFlag``\\s.

    Takes ``ParsedSkill`` directly (not ``FeatureVector``) — it needs line-level
    spans for step reporting that the numeric vector doesn't carry
    (architecture.md §2.5, AGENTS.md §5).

    Returns an empty list when:
      - No dangerous sequences are detected.
      - ``parsed.parse_ok`` is ``False`` (the caller / CLI should skip this
        stage, but we handle it gracefully anyway).
      - The file has no body or declares no capabilities.

    An empty return is not an error — it is the expected result for benign
    files (architecture.md §4).
    """
    if not parsed.parse_ok:
        return []

    events = _extract_events(parsed)
    if not events:
        return []

    flags: list[ChainFlag] = []

    for chain_name, sequence in DANGEROUS_CHAINS:
        matched = _is_subsequence(sequence, events)
        if matched is None:
            continue

        steps = [(event.cap, event.line) for event in matched]
        flags.append(ChainFlag(chain_name=chain_name, steps=steps))

    return flags
