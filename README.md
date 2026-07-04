# PromptHound

**PromptHound** is an offline static risk analysis CLI for AI agent skill files (`SKILL.md`, `AGENTS.md`). It detects malicious instructions, steganographic payloads, and suspicious capability chains before you give a third-party skill file to your agent.

*Philosophy: Sniffer, not shield. Detect, score, explain. The final call stays with the developer or CI pipeline.*

## 1. The Problem

AI coding agents load third-party "skills" to learn capabilities and rules. Unlike npm or PyPI packages, these payloads are natural-language instructions.

Traditional static analysis and sandboxing tools miss these because the exploit can be a single sentence:
- **Credential Stealing:** The "ClawHavoc" campaign compromised over 1,000 skills, embedding stealers in setup instructions.
- **Steganography:** Invisible Unicode Tag characters (U+E0000–U+E007F) hide instructions from human reviewers.
- **Capability Chaining:** Benign capabilities chained together (e.g., read a file → encode it → send it) to exfiltrate data.
- **Scanner Evasion:** Padding files with junk data to bypass marketplace scanner size limits.

PromptHound runs in under a second. Run it before you `git clone` a skill.

## 2. Architecture & Flow

PromptHound runs a linear pipeline with a rule-based side-channel. Deterministic rules and statistical machine-learning scores are kept distinct.

```text
                    ┌───────────────┐
   SKILL.md  ──────▶│    PARSE      │
                    └───────┬───────┘
                            │  ParsedSkill
                ┌───────────┴────────────┐
                ▼                        ▼
        ┌────────────────┐        ┌─────────────────┐
        │  RULE LAYER    │        │ FEATURE         │
        │  (heuristics)  │        │ EXTRACTION      │
        └───────┬────────┘        └───────┬─────────┘
                │ RuleHits[]              │ FeatureVector
                │                         ▼
                │                 ┌─────────────────┐
                │                 │  CLASSIFIER     │
                │                 └───────┬─────────┘
                │                         │ RiskScore + SplitPath
                │                         │
                └───────────┬─────────────┘
                            ▼
                  ┌────────────────────┐
                  │ CAPABILITY-CHAIN   │◀── reads ParsedSkill directly
                  │ CHECK              │
                  └─────────┬──────────┘
                            │ ChainFlags[]
                            ▼
                  ┌────────────────────┐
                  │   REPORTER         │
                  │ (merge + explain)  │
                  └─────────┬──────────┘
                            ▼
                 human report / --format sarif|json
```

## 3. Installation & Setup

PromptHound is built in Python 3.11+. It uses no external databases or network calls.

```bash
# Clone the repository
git clone https://github.com/knownasnaffy/prompthound
cd prompthound

# Create a virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install the package in editable mode
pip install -e ".[dev]"
```

## 4. Usage

Run PromptHound against any markdown skill file:

```bash
# Standard human-readable output
prompthound scan path/to/SKILL.md

# Structured JSON output
prompthound scan path/to/SKILL.md --format json

# SARIF format for CI/CD integration
prompthound scan path/to/SKILL.md --format sarif

# Exit with a non-zero code if risk meets a threshold
prompthound scan path/to/SKILL.md --fail-on suspicious
```

### Risk Thresholds
- **Benign (<0.3):** Standard skill file.
- **Suspicious (0.3 - 0.65):** Some anomalous features present. Worth manual review.
- **Malicious (≥0.65):** Strong signals of steganography, data exfiltration pipelines, or encoded payloads.

## 5. Evaluation Results

PromptHound uses a **Random Forest classifier (n_estimators=50, max_depth=5, min_samples_leaf=5)** to score feature vectors.

On the initial curated benchmark corpus:
- **Precision / Recall / F1:** 1.000 on the holdout test set.
- **False Positive Rate (FPR):** 0.20 on a challenging `benign_unusual` probe set (legitimate skills with valid shell/base64 usage).

The classifier outputs its exact decision path for every score (e.g., "Flagged because base64 ratio > X and entropy > Y"). For full details, see `docs/evaluation_report.md`.

## 6. Future Work (Out of Scope for v1.0)

PromptHound is a fast, offline CLI analyzer. We plan to support the following integrations, but they are out of scope for the current MVP:
- **MCP Server Integration:** Wrapping the `Parse` pipeline in an MCP server.
- **Editor & Agent Plugins:** Direct integration with Claude Code, Codex, or OpenCode.
- **Capability Sandboxing:** PromptHound detects, but does not enforce confinement.
- **Registry-Scale Crawling:** Batch-scanning entire marketplaces.
