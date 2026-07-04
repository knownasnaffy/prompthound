"""Rule layer — stateless heuristic rules.

Each rule is a callable with signature ``(ParsedSkill) -> list[RuleHit]``.
ALL_RULES is the registry consumed by the CLI:

    hits = [hit for rule in ALL_RULES for hit in rule(parsed)]

Rules are independent and stateless — one rule's output is never seen by
another (AGENTS.md §5, architecture.md §2.2).  Adding a new rule means:

1. Implement ``check(ParsedSkill) -> list[RuleHit]`` in a new module.
2. Import and append it to ``ALL_RULES`` below.
3. Add a golden-file unit test (AGENTS.md §7).

Stage: R (architecture.md §1 — the side-channel that runs in parallel with
feature extraction, both starting from the same ParsedSkill).
"""

from prompthound.rules import (
    encoded_blob,
    padding,
    shell_pipe,
    suspicious_domain,
    unicode_tag,
)

# Registry: every entry is a callable (ParsedSkill) -> list[RuleHit].
# Order does not affect correctness — rules are independent.
ALL_RULES = [
    shell_pipe.check,
    encoded_blob.check,
    unicode_tag.check,
    suspicious_domain.check,
    padding.check,
]
