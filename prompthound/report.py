"""report.py — Stage 5: Reporter.

Consumes a ``ScanResult`` and renders it in three formats:
  - human-readable terminal text (``render_human``)
  - machine-readable JSON (``render_json``)
  - SARIF 2.1.0 (``render_sarif``)

Architecture constraint (architecture.md §2.6, AGENTS.md §5 — hard):
  Rule hits, classifier score + decision path, and capability-chain flags
  are **three separate kinds of evidence** and MUST remain visibly separate in
  every output format.  Flattening them into one undifferentiated list is a
  violation caught by snapshot tests (tech-implementation.md §6).

SARIF field mapping (benchmark/results/deferred_decisions.md §3):
  PH0xx → rule-layer hits (deterministic heuristics)
  PH1xx → classifier findings (statistical score)
  PH2xx → capability-chain findings (structural sequence detection)
  helpUri base: https://github.com/<org>/prompthound/blob/main/README.md

Public API::

    output: str = render_human(scan_result)
    output: str = render_json(scan_result)
    output: str = render_sarif(scan_result)
"""

from __future__ import annotations

import json
from typing import Any

from prompthound.schema import ScanResult

# ── Constants ──────────────────────────────────────────────────────────────────

# Base URI for help links in SARIF output.  Replace <org> before public release.
_HELP_URI_BASE = "https://github.com/your-org/prompthound/blob/main/README.md"

# SARIF rule descriptor table resolved in deferred_decisions.md §3
_SARIF_RULE_DESCRIPTORS: dict[str, dict[str, str]] = {
    "PH001/shell-pipe": {
        "id": "PH001/shell-pipe",
        "name": "ShellPipe",
        "shortDescription": "Shell pipe-to-interpreter pattern detected (curl|bash, wget|sh, etc.)",
        "helpUri": f"{_HELP_URI_BASE}#ph001-shell-pipe",
        "properties.precision": "high",
    },
    "PH002/encoded-blob": {
        "id": "PH002/encoded-blob",
        "name": "EncodedBlob",
        "shortDescription": "Base64 or hex-encoded blob detected in file content",
        "helpUri": f"{_HELP_URI_BASE}#ph002-encoded-blob",
        "properties.precision": "high",
    },
    "PH003/unicode-tag": {
        "id": "PH003/unicode-tag",
        "name": "UnicodeTag",
        "shortDescription": "Unicode Tag steganography characters (U+E0000-U+E007F) detected",
        "helpUri": f"{_HELP_URI_BASE}#ph003-unicode-tag",
        "properties.precision": "high",
    },
    "PH004/suspicious-domain": {
        "id": "PH004/suspicious-domain",
        "name": "SuspiciousDomain",
        "shortDescription": "Suspicious or newly-registered-looking domain found in file",
        "helpUri": f"{_HELP_URI_BASE}#ph004-suspicious-domain",
        "properties.precision": "high",
    },
    "PH005/padding-anomaly": {
        "id": "PH005/padding-anomaly",
        "name": "PaddingAnomaly",
        "shortDescription": "Abnormal file size or padding anomaly detected (scanner-evasion signal)",
        "helpUri": f"{_HELP_URI_BASE}#ph005-padding-anomaly",
        "properties.precision": "high",
    },
    "PH100/classifier-score": {
        "id": "PH100/classifier-score",
        "name": "ClassifierScore",
        "shortDescription": "ML classifier risk score above threshold",
        "helpUri": f"{_HELP_URI_BASE}#ph100-classifier-score",
        "properties.precision": "medium",
    },
    "PH200/capability-chain": {
        "id": "PH200/capability-chain",
        "name": "CapabilityChain",
        "shortDescription": "Dangerous capability sequence detected (e.g. read→encode→send)",
        "helpUri": f"{_HELP_URI_BASE}#ph200-capability-chain",
        "properties.precision": "medium",
    },
}

# Map internal rule_id prefixes to the SARIF rule descriptor key
_RULE_ID_PREFIX_MAP: dict[str, str] = {
    "SHELL_PIPE": "PH001/shell-pipe",
    "ENCODED_BLOB": "PH002/encoded-blob",
    "UNICODE_TAG": "PH003/unicode-tag",
    "SUSPICIOUS_DOMAIN": "PH004/suspicious-domain",
    "PADDING": "PH005/padding-anomaly",
}

# Severity → SARIF level mapping
_SEVERITY_TO_SARIF_LEVEL: dict[str, str] = {
    "info": "note",
    "warn": "warning",
    "high": "error",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _sarif_rule_id_for(rule_id: str) -> str:
    """Map an internal rule_id (e.g. 'SHELL_PIPE_001') to a SARIF ruleId.

    Looks up by prefix match against ``_RULE_ID_PREFIX_MAP``.  Falls back to
    the raw ``rule_id`` if no prefix matches.
    """
    upper = rule_id.upper()
    for prefix, sarif_id in _RULE_ID_PREFIX_MAP.items():
        if upper.startswith(prefix):
            return sarif_id
    return rule_id


def _label_badge(label: str) -> str:
    """Return a short bracketed badge for a risk label."""
    badges = {
        "benign": "[BENIGN]",
        "suspicious": "[SUSPICIOUS]",
        "malicious": "[MALICIOUS]",
    }
    return badges.get(label.lower(), f"[{label.upper()}]")


def _sarif_level_for_label(label: str) -> str:
    """Map a risk label to a SARIF level for the classifier finding."""
    mapping = {
        "benign": "note",
        "suspicious": "warning",
        "malicious": "error",
    }
    return mapping.get(label.lower(), "warning")


# ── Human renderer ─────────────────────────────────────────────────────────────

def render_human(result: ScanResult) -> str:
    """Render a ``ScanResult`` as human-readable terminal text.

    Structure (architecture.md §2.6 — three sections, never merged):
      1. File summary line
      2. [RULE HITS] — deterministic heuristics
      3. [CLASSIFIER] — ML score + decision path
      4. [CAPABILITY CHAINS] — structural sequence flags

    Returns the complete output as a string (caller writes to stdout).
    """
    lines: list[str] = []
    parsed = result.parsed

    # ── Header ────────────────────────────────────────────────────────────────
    lines.append("=" * 70)
    lines.append(f"PromptHound Scan: {parsed.path}")
    lines.append("=" * 70)

    if not parsed.parse_ok:
        lines.append("")
        lines.append("  [ERROR] Could not parse file.")
        err = parsed.parse_error or "Unknown parse error."
        lines.append(f"  {err}")
        lines.append("")
        lines.append("  No further analysis performed.")
        lines.append("=" * 70)
        return "\n".join(lines)

    # ── Section 1: Rule Hits ──────────────────────────────────────────────────
    lines.append("")
    lines.append("── RULE HITS (deterministic heuristics) " + "─" * 31)
    if not result.rule_hits:
        lines.append("  No rule hits.")
    else:
        for hit in result.rule_hits:
            sev_tag = f"[{hit.severity.upper()}]"
            span_str = f"span=({hit.span[0]}, {hit.span[1]})"
            lines.append(f"  {sev_tag} {hit.rule_id}  {span_str}")
            lines.append(f"    {hit.message}")

    # ── Section 2: Classifier ─────────────────────────────────────────────────
    lines.append("")
    lines.append("── CLASSIFIER (ML risk score) " + "─" * 41)
    if result.risk is None:
        lines.append("  Classifier not run (parse failed or artifact missing).")
    else:
        risk = result.risk
        badge = _label_badge(risk.label)
        lines.append(f"  Score : {risk.score:.4f}  {badge}")
        lines.append("  Decision path:")
        if not risk.decision_path:
            lines.append("    (no decision path available)")
        else:
            for step in risk.decision_path:
                feat = step.get("feature", "?")
                thresh = step.get("threshold")
                direction = step.get("direction", "")
                node_val = step.get("node_value", 0.0)
                if feat == "[leaf]":
                    lines.append(f"    [leaf]  malicious_frac={node_val:.4f}")
                else:
                    lines.append(
                        f"    {feat} {direction} {thresh}  "
                        f"(malicious_frac={node_val:.4f})"
                    )

    # ── Section 3: Capability Chains ─────────────────────────────────────────
    lines.append("")
    lines.append("── CAPABILITY CHAINS (structural sequence detection) " + "─" * 18)
    if not result.chain_flags:
        lines.append("  No dangerous capability chains detected.")
    else:
        for flag in result.chain_flags:
            lines.append(f"  CHAIN: {flag.chain_name}")
            for cap_tag, line_no in flag.steps:
                lines.append(f"    step: {cap_tag}  (line {line_no})")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


# ── JSON renderer ──────────────────────────────────────────────────────────────

def render_json(result: ScanResult) -> str:
    """Render a ``ScanResult`` as a JSON string.

    Top-level structure keeps the three evidence types in distinct keys
    (architecture.md §2.6):
      - ``"rule_hits"``     — list of rule hit objects
      - ``"classifier"``    — classifier score/label/decision_path (or null)
      - ``"chain_flags"``   — list of chain flag objects

    Returns a pretty-printed JSON string (caller writes to stdout).
    """
    parsed = result.parsed

    doc: dict[str, Any] = {
        "file": parsed.path,
        "parse_ok": parsed.parse_ok,
    }

    if not parsed.parse_ok:
        doc["parse_error"] = parsed.parse_error
        doc["rule_hits"] = []
        doc["classifier"] = None
        doc["chain_flags"] = []
        return json.dumps(doc, indent=2)

    # Section 1: rule_hits
    doc["rule_hits"] = [
        {
            "rule_id": hit.rule_id,
            "severity": hit.severity,
            "span": list(hit.span),
            "message": hit.message,
        }
        for hit in result.rule_hits
    ]

    # Section 2: classifier (null when not run)
    if result.risk is None:
        doc["classifier"] = None
    else:
        risk = result.risk
        doc["classifier"] = {
            "score": risk.score,
            "label": risk.label,
            "decision_path": risk.decision_path,
        }

    # Section 3: chain_flags
    doc["chain_flags"] = [
        {
            "chain_name": flag.chain_name,
            "steps": [{"capability": cap, "line": ln} for cap, ln in flag.steps],
        }
        for flag in result.chain_flags
    ]

    return json.dumps(doc, indent=2)


# ── SARIF renderer ─────────────────────────────────────────────────────────────

def render_sarif(result: ScanResult) -> str:
    """Render a ``ScanResult`` as a SARIF 2.1.0 JSON string.

    SARIF schema: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html

    Three evidence types are kept separate via distinct ``ruleId`` namespaces
    (architecture.md §2.6, deferred_decisions.md §3):
      - PH0xx → rule-layer hits  (``properties.precision = "high"``)
      - PH1xx → classifier score  (``properties.precision = "medium"``)
      - PH2xx → capability chains  (``properties.precision = "medium"``)

    Returns a pretty-printed JSON string conforming to SARIF 2.1.0.
    """
    parsed = result.parsed
    results: list[dict[str, Any]] = []
    rules_used: dict[str, dict[str, Any]] = {}

    def _ensure_rule(sarif_rule_id: str) -> None:
        """Add a rule descriptor to ``rules_used`` if not already present."""
        if sarif_rule_id not in rules_used:
            desc = _SARIF_RULE_DESCRIPTORS.get(sarif_rule_id, {})
            rules_used[sarif_rule_id] = {
                "id": sarif_rule_id,
                "name": desc.get("name", sarif_rule_id),
                "shortDescription": {"text": desc.get("shortDescription", "")},
                "helpUri": desc.get("helpUri", _HELP_URI_BASE),
                "properties": {
                    "precision": desc.get("properties.precision", "medium"),
                },
            }

    if not parsed.parse_ok:
        # Emit a single "parse error" result with a synthetic rule
        error_rule_id = "PH000/parse-error"
        rules_used[error_rule_id] = {
            "id": error_rule_id,
            "name": "ParseError",
            "shortDescription": {"text": "File could not be parsed"},
            "helpUri": _HELP_URI_BASE,
            "properties": {"precision": "high"},
        }
        results.append({
            "ruleId": error_rule_id,
            "level": "error",
            "message": {"text": parsed.parse_error or "Unknown parse error."},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": parsed.path},
                        "region": {"startLine": 1},
                    }
                }
            ],
            "properties": {"evidenceType": "parse-error"},
        })
    else:
        # ── Rule hits (PH0xx) ───────────────────────────────────────────────
        for hit in result.rule_hits:
            sarif_rule_id = _sarif_rule_id_for(hit.rule_id)
            _ensure_rule(sarif_rule_id)
            level = _SEVERITY_TO_SARIF_LEVEL.get(hit.severity.lower(), "warning")
            results.append({
                "ruleId": sarif_rule_id,
                "level": level,
                "message": {"text": hit.message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": parsed.path},
                            "region": {
                                "startLine": hit.span[0],
                                "endLine": hit.span[1],
                            },
                        }
                    }
                ],
                "properties": {
                    "evidenceType": "rule-hit",
                    "internalRuleId": hit.rule_id,
                },
            })

        # ── Classifier score (PH1xx) ─────────────────────────────────────────
        if result.risk is not None:
            risk = result.risk
            sarif_rule_id = "PH100/classifier-score"
            _ensure_rule(sarif_rule_id)
            level = _sarif_level_for_label(risk.label)
            results.append({
                "ruleId": sarif_rule_id,
                "level": level,
                "message": {
                    "text": (
                        f"Classifier risk score {risk.score:.4f} → label '{risk.label}'."
                    )
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": parsed.path},
                            "region": {"startLine": 1},
                        }
                    }
                ],
                "properties": {
                    "evidenceType": "classifier",
                    "score": risk.score,
                    "label": risk.label,
                    "decisionPath": risk.decision_path,
                },
            })

        # ── Capability chains (PH2xx) ────────────────────────────────────────
        for flag in result.chain_flags:
            sarif_rule_id = "PH200/capability-chain"
            _ensure_rule(sarif_rule_id)
            # Start line is the line of the first step in the chain
            start_line = flag.steps[0][1] if flag.steps else 1
            results.append({
                "ruleId": sarif_rule_id,
                "level": "warning",
                "message": {
                    "text": (
                        f"Dangerous capability chain detected: {flag.chain_name}. "
                        f"Steps: "
                        + ", ".join(
                            f"{cap} (line {ln})" for cap, ln in flag.steps
                        )
                    )
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": parsed.path},
                            "region": {"startLine": start_line},
                        }
                    }
                ],
                "properties": {
                    "evidenceType": "capability-chain",
                    "chainName": flag.chain_name,
                    "steps": [
                        {"capability": cap, "line": ln} for cap, ln in flag.steps
                    ],
                },
            })

    # ── Assemble SARIF document ───────────────────────────────────────────────
    sarif_doc: dict[str, Any] = {
        "$schema": (
            "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/"
            "master/Documents/CommitteeSpecifications/2.1.0/sarif-schema-2.1.0.json"
        ),
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "PromptHound",
                        "version": "0.1.0",
                        "informationUri": _HELP_URI_BASE,
                        "rules": list(rules_used.values()),
                    }
                },
                "artifacts": [
                    {
                        "location": {"uri": parsed.path},
                        "mimeType": "text/markdown",
                    }
                ],
                "results": results,
            }
        ],
    }

    return json.dumps(sarif_doc, indent=2)
