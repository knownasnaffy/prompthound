"""report.py — Stage 5: Reporter.

Consumes a ``ScanResult`` and renders it in three formats:
  - human-readable terminal text (``render_human``)
  - machine-readable JSON (``render_json``)
  - SARIF 2.1.0 (``render_sarif``)

Architecture constraint (architecture.md §2.6, AGENTS.md §5 — hard):
  Rule hits, classifier score + local feature contributions, and capability-chain flags
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


def _translate_line(parsed: ParsedSkill, lineno: int) -> tuple[str, int]:
    """Translate a merged line number back to its original file and line number.
    
    If there is no source_manifest, returns the parsed path and the original line number.
    """
    if not parsed.source_manifest:
        return (parsed.path, lineno)
        
    for span in parsed.source_manifest:
        if span.merged_start <= lineno <= span.merged_end:
            # Map back to original line number
            orig_lineno = span.orig_start + (lineno - span.merged_start)
            return (span.file, orig_lineno)
            
    # Fallback if somehow not in manifest
    return (parsed.path, lineno)


# ── Human renderer ─────────────────────────────────────────────────────────────

def render_human(result: ScanResult) -> str:
    """Render a ``ScanResult`` as human-readable terminal text.

    Structure (architecture.md §2.6 — three sections, never merged):
      1. File summary line
      2. [RULE HITS] — deterministic heuristics
      3. [CLASSIFIER] — ML score + local feature contributions
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
            # UNICODE_TAG uses char offsets; others use line numbers
            if hit.rule_id.startswith("UNICODE_TAG"):
                span_str = f"span=({hit.span[0]}, {hit.span[1]})"
                loc_str = ""
            else:
                fpath, ln_start = _translate_line(parsed, hit.span[0])
                _, ln_end = _translate_line(parsed, hit.span[1])
                span_str = f"lines=({ln_start}, {ln_end})"
                loc_str = f" in {fpath}" if parsed.source_manifest else ""
            lines.append(f"  {sev_tag} {hit.rule_id}  {span_str}{loc_str}")
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
        lines.append("  Important Features:")
        if not risk.feature_importances:
            lines.append("    (no feature importances available)")
        else:
            for feat_info in risk.feature_importances:
                feat = feat_info.get("feature", "?")
                importance = feat_info.get("importance", 0.0)
                lines.append(f"    - {feat} (Importance: {importance:.4f})")

    # ── Section 3: Capability Chains ─────────────────────────────────────────
    lines.append("")
    lines.append("── CAPABILITY CHAINS (structural sequence detection) " + "─" * 18)
    if not result.chain_flags:
        lines.append("  No dangerous capability chains detected.")
    else:
        for flag in result.chain_flags:
            lines.append(f"  CHAIN: {flag.chain_name}")
            for cap_tag, line_no in flag.steps:
                fpath, orig_ln = _translate_line(parsed, line_no)
                loc_str = f"{fpath}:{orig_ln}" if parsed.source_manifest else f"line {orig_ln}"
                lines.append(f"    step: {cap_tag}  ({loc_str})")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


# ── JSON renderer ──────────────────────────────────────────────────────────────

def render_json(result: ScanResult) -> str:
    """Render a ``ScanResult`` as a JSON string.

    Top-level structure keeps the three evidence types in distinct keys
    (architecture.md §2.6):
      - ``"rule_hits"``     — list of rule hit objects
      - ``"classifier"``    — classifier score/label/local feature contributions (or null)
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
    doc_hits = []
    for hit in result.rule_hits:
        if hit.rule_id.startswith("UNICODE_TAG"):
            span_data = list(hit.span)
            file_loc = parsed.path
        else:
            fpath, start = _translate_line(parsed, hit.span[0])
            _, end = _translate_line(parsed, hit.span[1])
            span_data = [start, end]
            file_loc = fpath if parsed.source_manifest else parsed.path
            
        doc_hits.append({
            "rule_id": hit.rule_id,
            "severity": hit.severity,
            "span": span_data,
            "file": file_loc,
            "message": hit.message,
        })
    doc["rule_hits"] = doc_hits

    # Section 2: classifier (null when not run)
    if result.risk is None:
        doc["classifier"] = None
    else:
        risk = result.risk
        doc["classifier"] = {
            "score": risk.score,
            "label": risk.label,
            "feature_importances": risk.feature_importances,
        }

    # Section 3: chain_flags
    doc_flags = []
    for flag in result.chain_flags:
        steps_out = []
        for cap, ln in flag.steps:
            fpath, orig_ln = _translate_line(parsed, ln)
            steps_out.append({
                "capability": cap,
                "line": orig_ln,
                "file": fpath if parsed.source_manifest else parsed.path
            })
        doc_flags.append({
            "chain_name": flag.chain_name,
            "steps": steps_out,
        })
    doc["chain_flags"] = doc_flags

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
            
            if hit.rule_id.startswith("UNICODE_TAG"):
                uri = parsed.path
                start_line = 1
                end_line = 1
            else:
                uri, start_line = _translate_line(parsed, hit.span[0])
                _, end_line = _translate_line(parsed, hit.span[1])
                
            results.append({
                "ruleId": sarif_rule_id,
                "level": level,
                "message": {"text": hit.message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": uri},
                            "region": {
                                "startLine": start_line,
                                "endLine": end_line,
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
                    "featureImportances": risk.feature_importances,
                },
            })

        # ── Capability chains (PH2xx) ────────────────────────────────────────
        for flag in result.chain_flags:
            sarif_rule_id = "PH200/capability-chain"
            _ensure_rule(sarif_rule_id)
            # Start line is the line of the first step in the chain
            if flag.steps:
                start_uri, start_line = _translate_line(parsed, flag.steps[0][1])
            else:
                start_uri, start_line = parsed.path, 1
                
            steps_out = []
            for cap, ln in flag.steps:
                fpath, orig_ln = _translate_line(parsed, ln)
                steps_out.append({"capability": cap, "line": orig_ln, "file": fpath})

            results.append({
                "ruleId": sarif_rule_id,
                "level": "warning",
                "message": {
                    "text": (
                        f"Dangerous capability chain detected: {flag.chain_name}. "
                        f"Steps: "
                        + ", ".join(
                            f"{cap} ({loc['file']}:{loc['line']})" if parsed.source_manifest else f"{cap} (line {loc['line']})"
                            for cap, loc in zip([s[0] for s in flag.steps], steps_out)
                        )
                    )
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": start_uri},
                            "region": {"startLine": start_line},
                        }
                    }
                ],
                "properties": {
                    "evidenceType": "capability-chain",
                    "chainName": flag.chain_name,
                    "steps": steps_out,
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
