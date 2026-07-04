"""Rule: SUSPICIOUS_DOMAIN — domain heuristics for risky URLs.

Stage: R (architecture.md §2.2).

Flags URLs whose hostnames show patterns associated with attacker infrastructure:

    1. Non-standard / uncommon TLDs (not in the well-known list).
    2. High-entropy subdomain labels (random-looking, DGA-style).
    3. IP-address URLs (bypasses domain reputation checks).
    4. Free dynamic-DNS providers commonly used for C2 (duckdns, no-ip, etc.).
    5. Extremely long hostnames (> 50 chars in a single label).

Rule IDs:
    SUSPICIOUS_DOMAIN_001 — non-standard TLD
    SUSPICIOUS_DOMAIN_002 — high-entropy / DGA-like subdomain
    SUSPICIOUS_DOMAIN_003 — raw IP address URL
    SUSPICIOUS_DOMAIN_004 — known free dynamic-DNS provider
    SUSPICIOUS_DOMAIN_005 — abnormally long hostname label

Severity: warn  (domain signals are heuristic; false positives are possible on
legitimate URLs with unusual TLDs, so "warn" rather than "high").
"""

from __future__ import annotations

import math
import re
from collections import Counter

from prompthound.schema import ParsedSkill, RuleHit

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

# Well-known, broadly legitimate TLDs.  Anything not in this set is flagged.
# Intentionally conservative — we list only the most common ones to keep the
# set small and avoid false negatives.
_KNOWN_TLDS = frozenset(
    {
        "com",
        "org",
        "net",
        "edu",
        "gov",
        "mil",
        "int",
        "io",
        "co",
        "ai",
        "dev",
        "app",
        "cloud",
        "tech",
        "uk",
        "us",
        "ca",
        "au",
        "de",
        "fr",
        "jp",
        "cn",
        "in",
        "br",
        "ru",
        "nl",
        "se",
        "no",
        "fi",
        "dk",
        "it",
        "es",
        "pl",
        "pt",
        "be",
        "ch",
        "at",
        "nz",
        "sg",
        "hk",
        "kr",
        "mx",
        "ar",
        "za",
        "eg",
        # common second-level under country codes
        "co.uk",
        "com.au",
        "co.jp",
        "co.in",
        # modern common gTLDs
        "info",
        "biz",
        "name",
        "pro",
        "aero",
        "coop",
        "museum",
        "me",
        "tv",
        "cc",
        "ws",
        "ly",
        "gl",
        "gg",
    }
)

# Free dynamic-DNS providers frequently used for C2 infrastructure.
_DYNAMIC_DNS_SUFFIXES = frozenset(
    {
        "duckdns.org",
        "no-ip.com",
        "no-ip.org",
        "no-ip.biz",
        "noip.com",
        "ddns.net",
        "hopto.org",
        "zapto.org",
        "sytes.net",
        "myftp.org",
        "myftp.biz",
        "myvnc.com",
        "dynalias.com",
        "changeip.com",
        "changeip.net",
        "changeip.org",
        "afraid.org",
        "freedns.afraid.org",
        "mooo.com",
        "3utilities.com",
        "bounceme.net",
        "ddnsking.com",
    }
)

# Regex for extracting URLs from text.
_URL_PATTERN = re.compile(
    r"https?://"  # scheme
    r"([A-Za-z0-9.\-]{1,253})"  # host (capture group 1)
    r"(?::\d+)?"  # optional port
    r"(?:[/?#]\S*)?",  # optional path/query/fragment
    re.IGNORECASE,
)

# Raw IPv4: four octets.
_IPV4_PATTERN = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$")

# Minimum Shannon entropy (bits per character) to flag a label as DGA-like.
_DGA_ENTROPY_THRESHOLD = 3.5
# Minimum label length before entropy check (short random strings are common).
_DGA_MIN_LABEL_LEN = 12
# Maximum single-label length before flagging as abnormally long.
_LONG_LABEL_MAX = 50

SEVERITY = "warn"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _shannon_entropy(s: str) -> float:
    """Compute Shannon entropy (bits/char) for string *s*."""
    if not s:
        return 0.0
    counts = Counter(s.lower())
    total = len(s)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def _is_ipv4(host: str) -> bool:
    m = _IPV4_PATTERN.match(host)
    if not m:
        return False
    return all(0 <= int(g) <= 255 for g in m.groups())


def _extract_hosts(text: str) -> list[tuple[str, int]]:
    """Return list of (hostname, line_number) for all URLs found in *text*.

    line_number is 1-based within *text*.
    """
    result: list[tuple[str, int]] = []
    for lineno_offset, line in enumerate(text.splitlines(), start=1):
        for m in _URL_PATTERN.finditer(line):
            result.append((m.group(1).lower().rstrip("."), lineno_offset))
    return result


def _analyse_host(host: str, lineno: int, base_line: int) -> list[RuleHit]:
    """Run all heuristics against a single *host* and return any RuleHits."""
    hits: list[RuleHit] = []
    actual_line = base_line + lineno - 1  # convert body-relative to file-relative

    # ---- 1. Raw IP address -------------------------------------------------
    if _is_ipv4(host):
        hits.append(
            RuleHit(
                rule_id="SUSPICIOUS_DOMAIN_003",
                severity=SEVERITY,
                span=(actual_line, actual_line),
                message=(
                    f"Raw IP address URL at line {actual_line}: {host!r}. "
                    "Direct IP URLs bypass domain reputation checks."
                ),
            )
        )
        return hits  # IP hits are definitive; skip TLD / entropy checks

    labels = host.split(".")
    tld = labels[-1] if labels else ""

    # Compose effective TLD for two-label check (e.g. co.uk).
    effective_tld = ".".join(labels[-2:]) if len(labels) >= 2 else tld

    # ---- 2. Dynamic DNS suffix check ---------------------------------------
    for suffix in _DYNAMIC_DNS_SUFFIXES:
        if host == suffix or host.endswith("." + suffix):
            hits.append(
                RuleHit(
                    rule_id="SUSPICIOUS_DOMAIN_004",
                    severity=SEVERITY,
                    span=(actual_line, actual_line),
                    message=(
                        f"Free dynamic-DNS provider at line {actual_line}: {host!r}. "
                        "Dynamic-DNS services are frequently used for C2 infrastructure."
                    ),
                )
            )
            return hits  # dynamic DNS is already flagged; no need to pile on

    # ---- 3. Non-standard TLD -----------------------------------------------
    if tld not in _KNOWN_TLDS and effective_tld not in _KNOWN_TLDS:
        hits.append(
            RuleHit(
                rule_id="SUSPICIOUS_DOMAIN_001",
                severity=SEVERITY,
                span=(actual_line, actual_line),
                message=(
                    f"Non-standard TLD at line {actual_line}: {host!r} "
                    f"(TLD: .{tld!r}). Uncommon TLDs are associated with "
                    "newly-registered attacker domains."
                ),
            )
        )

    # ---- 4. High-entropy label (DGA-like) ----------------------------------
    for label in labels[:-1]:  # exclude the TLD itself
        if len(label) >= _DGA_MIN_LABEL_LEN:
            entropy = _shannon_entropy(label)
            if entropy >= _DGA_ENTROPY_THRESHOLD:
                hits.append(
                    RuleHit(
                        rule_id="SUSPICIOUS_DOMAIN_002",
                        severity=SEVERITY,
                        span=(actual_line, actual_line),
                        message=(
                            f"High-entropy subdomain at line {actual_line}: "
                            f"{host!r} (label {label!r} entropy={entropy:.2f} bits/char). "
                            "Random-looking subdomains may indicate DGA or attacker infra."
                        ),
                    )
                )
                break  # one entropy hit per host is enough

    # ---- 5. Abnormally long label ------------------------------------------
    for label in labels:
        if len(label) > _LONG_LABEL_MAX:
            hits.append(
                RuleHit(
                    rule_id="SUSPICIOUS_DOMAIN_005",
                    severity=SEVERITY,
                    span=(actual_line, actual_line),
                    message=(
                        f"Abnormally long hostname label at line {actual_line}: "
                        f"{host!r} (label length {len(label)}). "
                        "Very long labels are unusual and may be used for data exfiltration."
                    ),
                )
            )
            break

    return hits


# ---------------------------------------------------------------------------
# Public rule function
# ---------------------------------------------------------------------------


def check(parsed: ParsedSkill) -> list[RuleHit]:
    """Return RuleHits for suspicious domain patterns in code blocks and prose."""
    hits: list[RuleHit] = []

    for block in parsed.code_blocks:
        for host, lineno in _extract_hosts(block.content):
            hits.extend(_analyse_host(host, lineno, block.start_line + 1))

    if parsed.body_prose:
        for host, lineno in _extract_hosts(parsed.body_prose):
            hits.extend(_analyse_host(host, lineno, 1))

    return hits
