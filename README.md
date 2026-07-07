# PromptHound 🐕

PromptHound is a static risk analysis tool for AI agent skill files. It acts as a "sniffer, not a shield" — detecting malicious payloads, obfuscation attempts, and capability mismatches in agent skill files without causing alert fatigue. The final decision to block or allow always stays with the developer or CI pipeline.

## Features
- **Heuristic Engine**: Detects dangerous interpreter calls (`eval`, `exec`), shell access, base64 obfuscation, and credential exposure.
- **Anti-Dilution Architecture**: Parses companion file "bundles" to ensure malicious payloads cannot be hidden by padding them with massive benign files.
- **Low False Positives**: Powered by a tuned Random Forest model optimized specifically to minimize Severe False Positives (<1.5%) so your developers aren't blocked by noise.

## Installation

```bash
git clone https://github.com/knownasnaffy/prompthound.git
cd prompthound
pip install -e .
```

## CLI Usage

```bash
# Scan a single skill file
prompthound scan /path/to/SKILL.md

# Scan a skill bundle directory recursively
prompthound scan -d /path/to/skill_bundle/
```

### Output Formats

```bash
prompthound scan /path/to/SKILL.md --format json
prompthound scan /path/to/SKILL.md --format sarif
```

