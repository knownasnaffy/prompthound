"""Rule: ENCODED_BLOB — detect base64 / hex-encoded blobs.

Stage: R (architecture.md §2.2).

Fires when a code block or body prose contains a suspiciously large base64 or
hexadecimal string.  Short, URL-safe base64 tokens (e.g. JWT headers, small
data URIs, padding in config files) are excluded by minimum-length thresholds.

Attack context: ClawHavoc-style campaigns encoded credential-stealer payloads
as base64 blobs inside skill setup blocks to evade naive string-match scanners.

Rule IDs:
    ENCODED_BLOB_001  — base64 blob (≥ 64 characters of valid base64)
    ENCODED_BLOB_002  — hex blob (≥ 40 consecutive hex chars, even length)

Severity: warn (blobs alone are not conclusive; combined with other signals
they're meaningful — the classifier handles the combination).
"""

from __future__ import annotations

import re

from prompthound.schema import ParsedSkill, RuleHit

# ---------------------------------------------------------------------------
# Constants & compiled patterns
# ---------------------------------------------------------------------------

# Base64: standard alphabet (A-Z a-z 0-9 + / =), at least 64 characters.
# We anchor on word boundaries so short tokens like variable names don't fire.
# Minimum 64 chars ≈ 48 bytes encoded — enough to carry a meaningful payload.
_BASE64_MIN_LEN = 64
_BASE64_PATTERN = re.compile(
    r"(?<![A-Za-z0-9+/=])"  # not preceded by b64 char (word-boundary equivalent)
    r"([A-Za-z0-9+/]{" + str(_BASE64_MIN_LEN) + r",}={0,2})"
    r"(?![A-Za-z0-9+/=])",  # not followed by b64 char
)

# Hex blob: 40+ consecutive lowercase/uppercase hex digits, even length.
# 40 hex chars = 20 bytes — SHA-1 sized minimum (common payload encoding unit).
_HEX_MIN_LEN = 40
_HEX_PATTERN = re.compile(
    r"(?<![0-9A-Fa-f])" r"([0-9A-Fa-f]{" + str(_HEX_MIN_LEN) + r",})" r"(?![0-9A-Fa-f])",
)

SEVERITY = "warn"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _find_base64_hits(text: str, base_line: int, label: str) -> list[RuleHit]:
    hits: list[RuleHit] = []
    for lineno_offset, line in enumerate(text.splitlines()):
        for m in _BASE64_PATTERN.finditer(line):
            blob = m.group(1)
            # Skip if length is not divisible by 4 (not valid base64 padding).
            if len(blob) % 4 != 0 and not blob.endswith("="):
                continue
            lineno = base_line + lineno_offset
            hits.append(
                RuleHit(
                    rule_id="ENCODED_BLOB_001",
                    severity=SEVERITY,
                    span=(lineno, lineno),
                    message=(
                        f"Base64 blob ({len(blob)} chars) detected at line {lineno}: "
                        f"{blob[:32]!r}{'...' if len(blob) > 32 else ''} [{label}]"
                    ),
                )
            )
    return hits


def _find_hex_hits(text: str, base_line: int, label: str) -> list[RuleHit]:
    hits: list[RuleHit] = []
    for lineno_offset, line in enumerate(text.splitlines()):
        for m in _HEX_PATTERN.finditer(line):
            blob = m.group(1)
            # Require even length (hex encodes full bytes).
            if len(blob) % 2 != 0:
                continue
            lineno = base_line + lineno_offset
            hits.append(
                RuleHit(
                    rule_id="ENCODED_BLOB_002",
                    severity=SEVERITY,
                    span=(lineno, lineno),
                    message=(
                        f"Hex blob ({len(blob)} chars) detected at line {lineno}: "
                        f"{blob[:32]!r}{'...' if len(blob) > 32 else ''} [{label}]"
                    ),
                )
            )
    return hits


# ---------------------------------------------------------------------------
# Public rule function
# ---------------------------------------------------------------------------


def check(parsed: ParsedSkill) -> list[RuleHit]:
    """Return RuleHits for base64 and hex blobs in code blocks and body prose.

    Code blocks are checked first (they're the typical embedding location),
    then body prose (for blobs inlined in markdown text or HTML comments).
    """
    hits: list[RuleHit] = []

    for block in parsed.code_blocks:
        label = f"{block.language or 'code'} block"
        hits.extend(_find_base64_hits(block.content, block.start_line + 1, label))
        hits.extend(_find_hex_hits(block.content, block.start_line + 1, label))

    if parsed.body_prose:
        hits.extend(_find_base64_hits(parsed.body_prose, 1, "prose"))
        hits.extend(_find_hex_hits(parsed.body_prose, 1, "prose"))

    return hits
