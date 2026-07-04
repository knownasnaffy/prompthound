"""Rule: UNICODE_TAG — flag Unicode Tag character steganography.

Stage: R (architecture.md §2.2).

Unicode Tag characters (U+E0000-U+E007F) are invisible in standard editors and
markdown previews, but are read as semantic content by language models.
Attackers use them to embed hidden instructions inside a skill file that appear
blank to a human reviewer.

This rule does *not* re-scan the raw bytes — it consumes the
``unicode_tag_spans`` field already populated by ``parse.py`` during Stage P.
That field is the single detection site (architecture.md §2.1); this rule just
translates the spans into reportable ``RuleHit`` objects.

Rule ID: UNICODE_TAG_001
Severity: high
"""

from __future__ import annotations

from prompthound.schema import ParsedSkill, RuleHit

RULE_ID = "UNICODE_TAG_001"
SEVERITY = "high"


def check(parsed: ParsedSkill) -> list[RuleHit]:
    """Return a RuleHit for each contiguous Unicode Tag character run.

    ``parsed.unicode_tag_spans`` contains ``(start_char, end_char)`` pairs
    (character offsets into the UTF-8 decoded file text) as populated by
    ``parse.py::_find_unicode_tag_spans()``.  Each distinct run becomes its
    own ``RuleHit`` so the Reporter can point at each injection site
    individually.

    Returns an empty list when no Unicode Tag characters are present —
    absence is a valid, common, benign outcome.
    """
    hits: list[RuleHit] = []

    for start, end in parsed.unicode_tag_spans:
        run_len = end - start
        hits.append(
            RuleHit(
                rule_id=RULE_ID,
                severity=SEVERITY,
                span=(start, end),
                message=(
                    f"Unicode Tag steganography: {run_len} Tag character(s) "
                    f"(U+E0000-U+E007F) at char offsets {start}-{end}. "
                    "These are invisible in standard editors but readable by "
                    "language models and may encode hidden instructions."
                ),
            )
        )

    return hits
