"""Rule: PADDING — flag abnormal file-size padding / junk-byte evasion.

Stage: R (architecture.md §2.2).

Marketplace scanners and size-gated tools can be evaded by padding a malicious
file with junk bytes to push it past the threshold they bother processing.
This rule flags files where a large fraction of the raw bytes consist of long
runs of a single repeated byte — the signature of padding rather than real
content.

The detection logic lives entirely in ``parse.py::compute_padding_ratio()``.
This rule does *not* reimplement that logic; it imports and calls the shared
helper as specified in tech-implementation.md §4 and architecture.md §4.

The same ratio is also consumed as a numeric feature by
``features.py::padding_ratio``.  That dual-path feeding is intentional and
documented in architecture.md §4.

Rule ID: PADDING_001
Severity: warn  (padding alone is not conclusive — it's often a
                 false-positive on compressed/binary-adjacent content)
"""

from __future__ import annotations

from prompthound.parse import compute_padding_ratio
from prompthound.schema import ParsedSkill, RuleHit

RULE_ID = "PADDING_001"
SEVERITY = "warn"

# Threshold: files where ≥ 20 % of raw bytes are padding runs are flagged.
# This is conservative enough to avoid firing on legitimately repetitive text
# while catching files stuffed with hundreds of NUL / space runs.
_PADDING_THRESHOLD = 0.20


def check(parsed: ParsedSkill) -> list[RuleHit]:
    """Return a RuleHit when the file's padding ratio exceeds the threshold.

    Calls ``compute_padding_ratio(parsed.raw_bytes)`` — the shared helper from
    ``parse.py`` — so the detection logic is defined exactly once
    (tech-implementation.md §4).

    Returns at most one RuleHit (either the whole file is padded or it isn't).
    """
    if parsed.source_manifest:
        # Max-pool across members
        lines = parsed.raw_bytes.splitlines(keepends=True)
        max_ratio = 0.0
        best_span = (0, len(parsed.raw_bytes))
        for span in parsed.source_manifest:
            member_bytes = b"".join(lines[span.merged_start - 1:span.merged_end])
            ratio = compute_padding_ratio(member_bytes)
            if ratio > max_ratio:
                max_ratio = ratio
                # The exact byte span is hard to compute without re-encoding, 
                # but rules use line or byte offsets. Let's just use the line offset 
                # for the span since it will be translated by the reporter anyway.
                # Actually, RuleHit.span expects byte or line offsets depending on the rule.
                # The original returned (0, len(parsed.raw_bytes)).
                # We can approximate or just return (span.merged_start, span.merged_end)
                best_span = (span.merged_start, span.merged_end)
                
        ratio = max_ratio
        span = best_span
    else:
        ratio = compute_padding_ratio(parsed.raw_bytes)
        span = (0, len(parsed.raw_bytes))

    if ratio < _PADDING_THRESHOLD:
        return []

    pct = ratio * 100
    return [
        RuleHit(
            rule_id=RULE_ID,
            severity=SEVERITY,
            span=span,
            message=(
                f"Abnormal padding detected: {pct:.1f}% of file bytes are long "
                "runs of a single repeated byte. This pattern is associated with "
                "padding-based scanner evasion (concept.md §1)."
            ),
        )
    ]
