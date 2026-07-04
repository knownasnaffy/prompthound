"""Rule layer — stateless heuristic rules.

Each rule is a callable with signature ``(ParsedSkill) -> list[RuleHit]``.
ALL_RULES is the registry consumed by the CLI.

Architecture: Stage 2a (architecture.md §1). Rules run in parallel with
feature extraction, both receiving the same ParsedSkill. A rule must never
import or depend on another rule's output (AGENTS.md §5).
"""

ALL_RULES: list = []  # populated in later phases
