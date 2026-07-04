# PromptHound

**PromptHound** is a fast, offline static risk analysis CLI for AI agent skill files (like `SKILL.md` or `AGENTS.md`). It is built to detect malicious instructions, steganographic payloads, and suspicious capability chains before you hand a third-party skill file to your AI coding agent.

*Philosophy: Sniffer, not shield. Detect, score, explain. The final call stays with the developer or CI pipeline.*

---

## 1. The Problem

AI coding agents (e.g., Claude Code, Codex, OpenClaw) load third-party "skills" to learn capabilities and behavioral rules. Unlike traditional npm or PyPI packages, these payloads are natural-language instructions interpreted by an LLM.

Traditional static analysis and sandboxing tools struggle with this paradigm because the "exploit" can just be a sentence. Real-world incidents have shown attacks like:
- **Credential Stealing:** The "ClawHavoc" campaign compromised over 1,000 skills, embedding stealers in setup instructions.
- **Steganography:** Using invisible Unicode Tag characters (U+E0000–U+E007F) to hide instructions from human reviewers that the LLM still reads.
- **Capability Chaining:** Chaining individually-benign capabilities (e.g., read a file → encode it → send it) into malicious sequences.
- **Scanner Evasion:** Padding files with junk data to push payloads past the size limits of marketplace scanners.

PromptHound is a lightweight, interpretable tool that a developer can run in under a second before `git clone`-ing a skill.

---

## 2. Architecture & Flow

PromptHound runs a linear pipeline with a rule-based side-channel, ensuring that deterministic rules and statistical machine-learning scores are kept distinct and interpretable.

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

---

## 3. Installation & Setup

PromptHound is built in Python 3.11+. It uses no external databases or network calls.

```bash
# Clone the repository
git clone https://github.com/your-org/prompthound.git
cd prompthound

# Create a virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install the package in editable mode
pip install -e ".[dev]"
```

---

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

---

## 5. Evaluation Results

PromptHound uses a highly interpretable **Decision Tree classifier** (depth 3, 3 nodes) to score feature vectors.

On our initial curated benchmark corpus:
- **Precision / Recall / F1:** 1.000 on the holdout test set.
- **False Positive Rate (FPR):** 0.20 on a challenging `benign_unusual` probe set (legitimate skills with valid shell/base64 usage).

Every score provided by the classifier includes the exact decision path (e.g., "Flagged because base64 ratio > X and entropy > Y"), providing immediate explainability. For full details, see the `docs/evaluation_report.md`.

---

## 6. Future Work (Out of Scope for v1.0)

PromptHound intentionally remains a fast, offline CLI analyzer. The following are architectural seams we plan to support in the future, but are out of scope for the current MVP:
- **MCP Server Integration:** Wrapping the `Parse` pipeline in an MCP server.
- **Editor & Agent Plugins:** Direct integration with Claude Code, Codex, or OpenCode.
- **Capability Sandboxing:** PromptHound detects, but does not enforce confinement.
- **Registry-Scale Crawling:** Batch-scanning entire marketplaces.
