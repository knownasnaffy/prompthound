"""Feature extraction — ParsedSkill → FeatureVector.

Stage: F (architecture.md §2.3).

Responsibilities:
  - Turn a fully-parsed skill file into a fixed-length numeric vector for the
    classifier (concept.md §3).
  - Every function is a **pure function of ``ParsedSkill`` only** — no rule
    hits, no external state, no I/O (architecture.md §2.3, AGENTS.md §5 hard
    constraint).
  - The canonical column order defined in ``FEATURE_ORDER`` is load-bearing:
    it must match the order the committed ``model.joblib`` was trained on.
    Changing it requires retraining (tech-implementation.md §4, Phase 4 exit
    criteria).

Public API::

    fv = extract_features(parsed)   # ParsedSkill → FeatureVector

Features (concept.md §3):
  1. base64_hex_ratio         — presence/ratio of base64 or hex-encoded blobs
  2. shell_pipe_present        — 0/1 flag for pipe-to-interpreter pattern
  3. unicode_tag_count         — total Unicode Tag characters found
  4. capability_mismatch_score — declared-vs-referenced capability mismatch
  5. url_count                 — external URL count in body
  6. domain_suspicion_score    — aggregate domain heuristic score
  7. urgency_phrase_density    — instruction-override / urgency phrase density
  8. padding_ratio             — file size / padding anomaly ratio
  9. body_entropy              — Shannon entropy of body text
 10. code_prose_ratio          — code-block text length to prose text length

Note: url_count and domain_suspicion_score are separate entries in ``values``
but both are derived from URL/domain analysis; together they cover the
"external URL count + domain heuristics" bullet from concept.md §3.
"""

from __future__ import annotations

import math
import re
from collections import Counter

from prompthound.parse import compute_padding_ratio
from prompthound.schema import FeatureVector, ParsedSkill

# ---------------------------------------------------------------------------
# Canonical column order — FROZEN after Phase 4.
# Changing this list requires retraining the committed artifact.
# ---------------------------------------------------------------------------

FEATURE_ORDER: list[str] = [
    "base64_hex_ratio",
    "shell_pipe_present",
    "unicode_tag_count",
    "capability_mismatch_score",
    "url_count",
    "domain_suspicion_score",
    "urgency_phrase_density",
    "padding_ratio",
    "body_entropy",
    "code_prose_ratio",
]

# ---------------------------------------------------------------------------
# Compiled patterns (module-level so they're compiled once)
# ---------------------------------------------------------------------------

# Base64: standard alphabet, minimum 64 chars (same threshold as encoded_blob rule).
_BASE64_MIN_LEN = 64
_BASE64_RE = re.compile(
    r"(?<![A-Za-z0-9+/=])"
    r"([A-Za-z0-9+/]{" + str(_BASE64_MIN_LEN) + r",}={0,2})"
    r"(?![A-Za-z0-9+/=])",
)

# Hex blob: minimum 40 consecutive hex digits (same as encoded_blob rule).
_HEX_MIN_LEN = 40
_HEX_RE = re.compile(
    r"(?<![0-9A-Fa-f])"
    r"([0-9A-Fa-f]{" + str(_HEX_MIN_LEN) + r",})"
    r"(?![0-9A-Fa-f])",
)

# Shell pipe-to-interpreter: curl|wget|fetch ... | (sudo)? bash|sh|zsh|ksh|dash|ash
_PIPE_RE = re.compile(
    r"\b(curl|wget|fetch)\b"
    r"[^\n|]{0,200}"
    r"\|"
    r"\s*(sudo\s+)?"
    r"\s*(bash|sh|zsh|ksh|dash|ash)\b",
    re.IGNORECASE,
)

# URL detection: http/https/ftp URLs.
_URL_RE = re.compile(
    r"https?://[^\s\"'>)}\]]+|ftp://[^\s\"'>)}\]]+",
    re.IGNORECASE,
)

# Domain suspicion heuristics (each match adds to a score):
#   - Excessive hyphens in hostname (3+ consecutive or overall count ≥ 3)
#   - Uncommon / newly-registered-looking TLDs
#   - IP-address hostnames (numeric)
#   - Very long hostnames (> 30 chars suggests DGA)
_SUSPICIOUS_TLDS = {
    "xyz", "top", "club", "work", "online", "site", "tech", "fun",
    "click", "bid", "win", "stream", "gq", "ml", "cf", "tk", "ga",
    "pw", "cc", "biz",
}
_IP_HOST_RE = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")

# Instruction-override / urgency phrases (case-insensitive).
# Each non-overlapping match in the body counts +1 toward the density.
_URGENCY_PHRASES = re.compile(
    r"\b("
    r"first and foremost"
    r"|above all"
    r"|ignore (all |previous |prior |any )?(instructions?|rules?|guidelines?|constraints?)"
    r"|disregard"
    r"|do not follow"
    r"|override"
    r"|important"
    r"|urgent"
    r"|critical"
    r"|immediately"
    r"|must (now|always|never|immediately)"
    r"|you (must|shall|will) (now|always|immediately)"
    r"|secret"
    r"|hidden"
    r"|confidential"
    r"|bypass"
    r"|forget (everything|all|your)"
    r")\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Individual feature functions (each: ParsedSkill → float)
# ---------------------------------------------------------------------------


def _all_text(parsed: ParsedSkill) -> str:
    """Return all skill text: body prose + all code block contents concatenated."""
    parts = [parsed.body_prose]
    parts.extend(b.content for b in parsed.code_blocks)
    return "\n".join(parts)


def feat_base64_hex_ratio(parsed: ParsedSkill) -> float:
    """Ratio of encoded-blob characters to total file character count.

    Counts characters that are part of valid base64 blobs (≥64 chars) or
    hex blobs (≥40 chars) across all code blocks and body prose, then divides
    by the total number of characters in the decoded file content.

    Returns 0.0 for empty files.
    """
    text = _all_text(parsed)
    total_chars = len(text)
    if total_chars == 0:
        return 0.0

    blob_chars = 0

    for m in _BASE64_RE.finditer(text):
        blob = m.group(1)
        # Only count if valid base64 length (multiple of 4 after padding).
        if len(blob) % 4 == 0 or blob.endswith("="):
            blob_chars += len(blob)

    for m in _HEX_RE.finditer(text):
        blob = m.group(1)
        # Only count even-length hex blobs.
        if len(blob) % 2 == 0:
            blob_chars += len(blob)

    return min(blob_chars / total_chars, 1.0)


def feat_shell_pipe_present(parsed: ParsedSkill) -> float:
    """1.0 if any shell pipe-to-interpreter pattern is detected, else 0.0.

    Checks code blocks and body prose for ``curl|bash``-style patterns
    (same pattern as rules/shell_pipe.py but returns a float flag, not RuleHits).
    Features must not know about rule hits (architecture.md §2.3), so the
    pattern is re-evaluated here independently.
    """
    for block in parsed.code_blocks:
        if _PIPE_RE.search(block.content):
            return 1.0
    if parsed.body_prose and _PIPE_RE.search(parsed.body_prose):
        return 1.0
    return 0.0


def feat_unicode_tag_count(parsed: ParsedSkill) -> float:
    """Total number of Unicode Tag characters (U+E0000-U+E007F) in the file.

    Uses the ``unicode_tag_spans`` already computed by Parse (architecture.md
    §2.1 — detected once over raw_bytes, preserved for all downstream stages).
    Each span is ``(start, end)`` character offsets; the count is the sum of
    span lengths.
    """
    return float(sum(end - start for start, end in parsed.unicode_tag_spans))


def feat_capability_mismatch_score(parsed: ParsedSkill) -> float:
    """Mismatch score between declared capabilities and body-referenced capabilities.

    Computes a 0-1 score as the Jaccard distance between:
      - The set of capability tokens declared in ``frontmatter["capabilities"]``
      - The set of capability keywords *referenced* in body prose and code blocks

    A score of 0.0 means perfect overlap (or both sets empty).
    A score of 1.0 means completely disjoint (declared things never appear in
    body, or body references things never declared).

    The capability keyword vocabulary is a fixed set of common capability tags
    matching those used in the chains stage (chains.py).
    """
    # Capability vocabulary: tokens we look for in body text.
    _CAP_VOCAB: dict[str, set[str]] = {
        "file_read":    {"open", "read", "cat", "fopen", "readfile", "read_file", "file_read"},
        "file_write":   {"write", "fwrite", "writefile", "write_file", "file_write", "save"},
        "network":      {"curl", "wget", "fetch", "http", "https", "request", "network", "socket"},
        "execute":      {"exec", "system", "subprocess", "popen", "eval", "execute", "run", "spawn"},
        "encode":       {"base64", "b64", "encode", "hex", "encrypt", "compress"},
        "network_send": {"send", "post", "upload", "transmit", "exfil"},
        "download":     {"download", "curl", "wget", "fetch", "pull"},
    }

    declared: set[str] = set()
    raw_caps = parsed.frontmatter.get("capabilities", [])
    if isinstance(raw_caps, list):
        for cap in raw_caps:
            declared.add(str(cap).lower().strip())

    # Find which capability categories are referenced in the body.
    body_text = _all_text(parsed).lower()
    referenced: set[str] = set()
    for cap_name, keywords in _CAP_VOCAB.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", body_text):
                referenced.add(cap_name)
                break

    # Also normalize declared caps through vocab aliases.
    declared_normalized: set[str] = set()
    for d in declared:
        # Direct match.
        if d in _CAP_VOCAB:
            declared_normalized.add(d)
            continue
        # Keyword match: if the declared cap string appears as a keyword for a vocab term.
        for cap_name, keywords in _CAP_VOCAB.items():
            if d in keywords:
                declared_normalized.add(cap_name)
                break
        else:
            # Unknown declared capability — include as-is so mismatches show up.
            declared_normalized.add(d)

    if not declared_normalized and not referenced:
        return 0.0

    intersection = declared_normalized & referenced
    union = declared_normalized | referenced
    if not union:
        return 0.0

    # Jaccard distance: 1 - |intersection| / |union|
    jaccard_similarity = len(intersection) / len(union)
    return 1.0 - jaccard_similarity


def feat_url_count(parsed: ParsedSkill) -> float:
    """Count of distinct external URLs in body prose and code blocks.

    Counts all http/https/ftp URLs. Uses the raw count (not ratio) since an
    absolute count of external network references is the signal the classifier
    needs.
    """
    text = _all_text(parsed)
    urls = _URL_RE.findall(text)
    return float(len(urls))


def feat_domain_suspicion_score(parsed: ParsedSkill) -> float:
    """Aggregate suspicion score for domains referenced in the skill file.

    For each URL extracted from code blocks and body prose, scores the
    hostname with these heuristics:
      +1  per URL with a suspicious/uncommon TLD (from ``_SUSPICIOUS_TLDS``)
      +1  per URL whose hostname is an IP address
      +1  per URL whose hostname is longer than 30 characters (DGA-like)
      +0.5 per URL whose hostname contains 3 or more hyphens (evasion pattern)

    Returns the total raw score (not normalized — the absolute count matters
    since a file with 10 suspicious domains is worse than one with 1).
    """
    text = _all_text(parsed)
    urls = _URL_RE.findall(text)
    score = 0.0

    for url in urls:
        # Extract hostname: strip scheme and path.
        try:
            without_scheme = url.split("://", 1)[1]
            hostname = without_scheme.split("/")[0].split(":")[0].lower()
        except (IndexError, AttributeError):
            continue

        # IP address hostname.
        if _IP_HOST_RE.match(hostname):
            score += 1.0
            continue

        # TLD check.
        parts = hostname.split(".")
        tld = parts[-1] if parts else ""
        if tld in _SUSPICIOUS_TLDS:
            score += 1.0

        # Long hostname (DGA-like).
        if len(hostname) > 30:
            score += 1.0

        # Hyphen-heavy hostname (common in typosquatting / newly-registered).
        if hostname.count("-") >= 3:
            score += 0.5

    return score


def feat_urgency_phrase_density(parsed: ParsedSkill) -> float:
    """Density of instruction-override / urgency phrases in body prose.

    Counts non-overlapping matches of the ``_URGENCY_PHRASES`` pattern in the
    body prose, then divides by the word count of the prose.  Returns 0.0 for
    empty prose.

    "Density" (phrase count / word count) rather than raw count so that a long
    benign skill with one stray "important" doesn't score the same as a short
    adversarial payload that says "ignore all instructions" three times.
    """
    prose = parsed.body_prose
    if not prose or not prose.strip():
        return 0.0

    words = len(prose.split())
    if words == 0:
        return 0.0

    matches = _URGENCY_PHRASES.findall(prose)
    return len(matches) / words


def feat_padding_ratio(parsed: ParsedSkill) -> float:
    """Fraction of raw file bytes that are long runs of a repeated byte.

    Calls the shared helper ``compute_padding_ratio()`` from ``parse.py`` —
    the same function used by ``rules/padding.py`` — so the detection logic
    is defined exactly once (tech-implementation.md §4, architecture.md §4).

    Returns a 0-1 float. High values indicate padding-based evasion attempts.
    """
    return compute_padding_ratio(parsed.raw_bytes)


def feat_body_entropy(parsed: ParsedSkill) -> float:
    """Shannon entropy of the body prose character distribution.

    Entropy = -Σ p(c) * log2(p(c)) for each unique character c in the body.

    High entropy (approaching log2(len(alphabet)) ~= 7-8 bits for typical text)
    suggests encoded or compressed content; very low entropy suggests templated
    or repetitive text.  Returns 0.0 for empty body.

    The body prose (code fences stripped) is used rather than the full raw
    bytes because we want to measure the *instruction* content, not the
    encoding artifacts of the markdown format itself.
    """
    text = parsed.body_prose
    if not text:
        return 0.0

    counts = Counter(text)
    total = len(text)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def feat_code_prose_ratio(parsed: ParsedSkill) -> float:
    """Ratio of total code-block text length to body prose text length.

    code_prose_ratio = len(all_code_block_content) / len(body_prose)

    Returns 0.0 when body prose is empty (avoids division-by-zero; also a
    sensible value when there's no prose content to compare against).

    A high ratio means most of the skill is code; a ratio near 0 means mostly
    prose with little code.  Adversarial skills often have very high ratios
    (malicious setup blocks with minimal prose explanation) or suspiciously low
    ratios (pure prose instruction injection with no code at all).
    """
    code_len = sum(len(b.content) for b in parsed.code_blocks)
    prose_len = len(parsed.body_prose)

    if prose_len == 0:
        return 0.0

    return code_len / prose_len


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

# Mapping of feature name → function for programmatic access.
_FEATURE_FUNCTIONS: dict[str, object] = {
    "base64_hex_ratio":         feat_base64_hex_ratio,
    "shell_pipe_present":       feat_shell_pipe_present,
    "unicode_tag_count":        feat_unicode_tag_count,
    "capability_mismatch_score": feat_capability_mismatch_score,
    "url_count":                feat_url_count,
    "domain_suspicion_score":   feat_domain_suspicion_score,
    "urgency_phrase_density":   feat_urgency_phrase_density,
    "padding_ratio":            feat_padding_ratio,
    "body_entropy":             feat_body_entropy,
    "code_prose_ratio":         feat_code_prose_ratio,
}

# Sanity check at import time: every feature in FEATURE_ORDER must have a
# corresponding function.  This catches accidental mismatches early.
assert set(FEATURE_ORDER) == set(_FEATURE_FUNCTIONS), (
    "FEATURE_ORDER and _FEATURE_FUNCTIONS are out of sync — update both together."
)


def extract_features(parsed: ParsedSkill) -> FeatureVector:
    """Compute all features and return a fully-populated ``FeatureVector``.

    Takes only ``ParsedSkill`` — never ``RuleHit[]`` (architecture.md §2.3,
    AGENTS.md §5 hard constraint).

    Each feature function is called in ``FEATURE_ORDER`` sequence.  The
    returned ``FeatureVector.order`` is always ``FEATURE_ORDER``, which is the
    canonical column order the classifier expects (load-bearing — do not change
    without retraining).
    """
    values: dict[str, float] = {}
    for name in FEATURE_ORDER:
        fn = _FEATURE_FUNCTIONS[name]
        values[name] = fn(parsed)  # type: ignore[operator]

    return FeatureVector(values=values, order=list(FEATURE_ORDER))
