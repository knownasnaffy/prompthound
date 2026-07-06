"""Shared data schemas for PromptHound.

These dataclasses define every object that crosses a stage boundary in the
pipeline described in architecture.md §1.  Defining them once here means every
stage imports the *same* shape instead of passing around plain dicts — the
single-source-of-truth requirement stated in tech-implementation.md §3.

Pipeline overview (architecture.md §1)::

    SKILL.md ──▶ PARSE ──▶ RULE LAYER ──────────────────────────────────┐
                      │                                                   │
                      └──▶ FEATURE EXTRACTION ──▶ CLASSIFIER ────────────┤
                      │                                                   │
                      └──▶ CAPABILITY-CHAIN CHECK ──────────────────────▶┤
                                                                          │
                                                                          ▼
                                                                    REPORTER
                                                                    (ScanResult)

Stage tags used in per-field docstrings:
    P   = Parse (parse.py)
    R   = Rule layer (rules/)
    F   = Feature extraction (features.py)
    C   = Classifier (classifier/model.py)
    CH  = Capability-chain check (chains.py)
    REP = Reporter (report.py)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CodeBlock:
    """A single fenced code block extracted from the skill file body.

    Produced by: P (parse.py) via markdown-it-py token stream.
    Consumed by:
      - R  (rules/)           — shell_pipe, encoded_blob rules inspect ``content``
      - F  (features.py)      — code-block-to-prose ratio, shell pattern features
      - CH (chains.py)        — body-referenced capability extraction

    Using the token stream (not regex) guarantees that ``start_line`` /
    ``end_line`` are real file-line numbers, which ``RuleHit.span`` and
    ``ChainFlag.steps`` need to point at exact source locations
    (tech-implementation.md §4).
    """

    language: str | None
    """Language tag from the opening fence (e.g. ``"bash"``, ``"python"``).
    ``None`` if the fence had no language annotation."""

    content: str
    """Raw text inside the fence, excluding the fence markers themselves."""

    start_line: int
    """1-based line number of the opening fence in the original file."""

    end_line: int
    """1-based line number of the closing fence in the original file."""


@dataclass
class SourceSpan:
    """Line mapping for an auxiliary file flattened into a synthetic bundle."""
    file: str
    orig_start: int
    orig_end: int
    merged_start: int
    merged_end: int


@dataclass
class ParsedSkill:
    """Fully parsed representation of a skill file.

    Produced by: P (parse.py).
    Consumed by:
      - R  (rules/)           — all rules take ``ParsedSkill`` as their sole input
      - F  (features.py)      — all feature functions take ``ParsedSkill`` only
      - CH (chains.py)        — reads frontmatter + body directly for chain detection
      - REP (report.py)       — reads ``path``, ``parse_ok``, ``parse_error`` for the
                                "could not parse" short-circuit render

    When ``parse_ok`` is ``False``, all fields other than ``path``,
    ``raw_bytes``, ``parse_ok``, and ``parse_error`` MUST be treated as
    meaningless defaults — no downstream stage should read them
    (architecture.md §4).  The CLI enforces this by skipping every stage after
    Parse if ``parse_ok is False``.
    """

    path: str
    """Filesystem path to the scanned file (used only for display/reporting)."""

    raw_bytes: bytes
    """Verbatim file contents as read from disk.

    The Unicode Tag scan in Parse runs over ``raw_bytes`` *before* any decoding
    step — this is intentional, because the whole point is catching what a
    normal markdown preview would not render (architecture.md §2.1).
    """

    frontmatter: dict
    """Parsed YAML/TOML frontmatter as a plain dict.

    Expected keys (all optional — malformed/missing files will have an empty
    dict here alongside ``parse_ok=False``): ``name``, ``description``,
    ``capabilities`` (list of declared capability strings), and any other
    author-defined metadata.
    """

    body_prose: str
    """Markdown body text with code fences removed.

    Used by F for Shannon entropy, urgency-phrase density, and
    code-block-to-prose ratio features.
    """

    code_blocks: list[CodeBlock]
    """All fenced code blocks in document order, each with line-number spans."""

    unicode_tag_spans: list[tuple[int, int]]
    """Character-offset pairs ``(start, end)`` of each Unicode Tag character
    run detected in the file (codepoints U+E0000-U+E007F).

    Detected-and-preserved, never stripped (architecture.md §2.1).  The
    presence is itself a signal consumed by three later stages:
      - R  (rules/unicode_tag.py)  — flags the file
      - F  (features.py)           — counts total tag characters as a feature
      - REP (report.py)            — shows *where* tags appear in the output
    """

    parse_ok: bool
    """``True`` if the file was parsed successfully; ``False`` on any
    short-circuit condition (no frontmatter, binary garbage, empty file).

    The CLI checks this flag before running any downstream stage
    (architecture.md §4).
    """

    parse_error: str | None
    """Human-readable description of the parse failure, or ``None`` on success.

    Set alongside ``parse_ok=False``; passed directly to the Reporter so it can
    render a "could not parse" result rather than a misleadingly low risk score.
    """

    source_manifest: list[SourceSpan] | None = None
    """Mapping of synthetic line numbers to original files for directory bundles.
    
    Populated by ``flatten.py`` when scanning directories with ``-d``.
    Used by the Reporter to translate line numbers in rules and chains, and
    by ``features.py`` to max-pool feature extraction across members.
    """


@dataclass
class RuleHit:
    """A single heuristic rule match found in a skill file.

    Produced by: R (rules/) — one instance per trigger, zero or more per rule.
    Consumed by: REP (report.py) exclusively.

    Rules are stateless and independent — one ``RuleHit`` never suppresses or
    depends on another (architecture.md §2.2, AGENTS.md §5).  Features.py
    deliberately never sees ``RuleHit`` objects (architecture.md §2.3).
    """

    rule_id: str
    """Stable identifier for the rule, e.g. ``"SHELL_PIPE_001"``.

    Used as the SARIF ``ruleId`` field (architecture.md §2.6).
    """

    severity: str
    """One of ``"info"``, ``"warn"``, or ``"high"``."""

    span: tuple[int, int]
    """``(start, end)`` byte or line offsets into the file that triggered the
    rule.  The Reporter uses this to show the exact offending excerpt."""

    message: str
    """One-line human-readable explanation of why the rule fired, e.g.
    ``"curl | bash pipeline detected in bash code block at line 14"``."""


@dataclass
class FeatureVector:
    """Numeric encoding of a skill file for the classifier.

    Produced by: F (features.py).
    Consumed by: C (classifier/model.py) — the only consumer.

    Features.py takes only ``ParsedSkill`` as input; it never receives
    ``RuleHit`` objects.  This keeps the classifier's evidence axis genuinely
    independent from the rule layer's axis (architecture.md §2.3, AGENTS.md §5).

    ``order`` is load-bearing: changing the column order requires retraining the
    committed artifact (tech-implementation.md §4, Phase 4 exit criteria).
    """

    values: dict[str, float | int]
    """Feature values keyed by feature name.

    Must contain exactly the features listed in concept.md §3:
      - ``base64_hex_ratio``         — presence/ratio of encoded blobs
      - ``shell_pipe_present``       — 0/1 flag for pipe-to-interpreter pattern
      - ``unicode_tag_count``        — total Unicode Tag characters found
      - ``capability_mismatch_score``— declared-vs-referenced mismatch
      - ``url_count``                — external URL count
      - ``domain_suspicion_score``   — domain heuristic aggregate
      - ``urgency_phrase_density``   — instruction-override phrase density
      - ``padding_ratio``            — file size / padding anomaly ratio
      - ``body_entropy``             — Shannon entropy of body text
      - ``code_prose_ratio``         — code-block-to-prose ratio
    """

    order: list[str]
    """Canonical column order passed to the classifier's ``predict`` call.

    Matches the column order the model was trained on.  Frozen after Phase 4.
    """


@dataclass
class RiskScore:
    """Classifier output for a skill file.

    Produced by: C (classifier/model.py).
    Consumed by: REP (report.py).

    The ``feature_importances`` (local feature contributions via Saabas decomposition)
    is the primary deliverable of the classifier stage — it's what makes the risk
    score interpretable rather than a black-box number (architecture.md §2.4, concept.md §2).
    """

    score: float
    """Continuous risk probability in ``[0.0, 1.0]``."""

    label: str
    """Categorical risk label: ``"benign"``, ``"suspicious"``, or
    ``"malicious"``, determined by applying the thresholds resolved in
    Phase 7 (tech-implementation.md §8).
    """

    feature_importances: list[dict]
    """Ordered list of the top features that contributed to this score, representing local feature contributions via Saabas decomposition.
    Each entry has the keys:
      - ``feature``    (str)   — feature name from ``FeatureVector.order``
      - ``importance`` (float) — feature importance weight (contribution delta)

    An empty list is valid when the model doesn't produce meaningful importances.
    """


@dataclass
class ChainFlag:
    """A detected dangerous capability sequence in a skill file.

    Produced by: CH (chains.py).
    Consumed by: REP (report.py).

    Chain detection uses *subsequence* matching, not exact-adjacency, so a
    chain split across non-adjacent lines still fires (tech-implementation.md
    §4).  An empty ``chain_flags`` list in ``ScanResult`` is a valid, benign
    outcome — absence of a chain is not an error (architecture.md §4).
    """

    chain_name: str
    """Human-readable name for the detected sequence, e.g.
    ``"file_read→encode→network_send"`` or ``"download→write→execute"``."""

    steps: list[tuple[str, int]]
    """Ordered list of ``(capability_tag, line_number)`` pairs, one per link in
    the chain.  ``capability_tag`` is the internal tag matched (e.g.
    ``"file_read"``); ``line_number`` is the 1-based file line where the
    matching capability was referenced.
    """


@dataclass
class ScanResult:
    """The shared result object that accumulates every stage's output.

    This is the "shared result object" architecture.md §1 refers to: each stage
    appends its piece; no stage mutates a prior stage's field.

    Produced by: the CLI (cli.py), which assembles this from stage outputs.
    Consumed by: REP (report.py) — the only module allowed to read all fields
    at once (AGENTS.md §5).

    The Reporter MUST keep the three evidence types visibly separate in every
    output format (architecture.md §2.6):
      - Rule hits         → ``rule_hits``
      - Classifier output → ``risk`` + ``risk.feature_importances``
      - Chain flags       → ``chain_flags``
    Flattening them into one list is a violation checked by snapshot tests.
    """

    parsed: ParsedSkill
    """Stage P output.  Always present; ``parsed.parse_ok`` signals whether
    downstream fields are meaningful."""

    rule_hits: list[RuleHit] = field(default_factory=list)
    """Stage R output.  Empty list (not ``None``) when no rules fire or when
    ``parsed.parse_ok`` is ``False`` and the rule stage was skipped."""

    features: FeatureVector | None = None
    """Stage F output.  ``None`` when ``parsed.parse_ok`` is ``False``."""

    risk: RiskScore | None = None
    """Stage C output.  ``None`` when ``parsed.parse_ok`` is ``False`` or when
    the classifier artifact is not loaded."""

    chain_flags: list[ChainFlag] = field(default_factory=list)
    """Stage CH output.  Empty list when no chains are detected or when
    ``parsed.parse_ok`` is ``False``."""
