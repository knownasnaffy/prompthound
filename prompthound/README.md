# PromptHound 🐕

PromptHound is a static risk analysis tool for AI agent skill files. It acts as a "sniffer, not a shield", integrating seamlessly into CI/CD pipelines to detect malicious payloads, obfuscation attempts, and capability mismatches in agent prompt/skill files without causing alert fatigue.

## Features
- **Heuristic Engine**: Detects dangerous interpreter calls (`eval`, `exec`), shell access, base64 obfuscation, and credential exposure.
- **Anti-Dilution Architecture**: Parses companion file "bundles" to ensure malicious payloads cannot be hidden by padding them with massive benign files.
- **Low False Positives**: Powered by a tuned Random Forest model optimized specifically to minimize Severe False Positives (<1.5%) so your developers aren't blocked by noise.
- **Automated CI/CD**: Includes a pre-commit Git hook to automatically block malicious skills before they are pushed.

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/prompthound.git
cd prompthound

# Install dependencies via pip
pip install -e .
```

## CLI Usage

PromptHound provides a robust CLI to scan files. 

Scan a specific file or bundle:
```bash
# Scan a single skill file
prompthound scan /path/to/SKILL.md

# Scan a bundle directory recursively
prompthound scan -d /path/to/skill_bundle/
```

Auto-discover and scan the entire project:
```bash
# Uses predefined known skill directories (.agents/skills, .kiro/skills, etc.)
prompthound scan -p
```

### Output Formats
PromptHound supports multiple output formats for CI/CD integration:
```bash
prompthound scan -p --format json
prompthound scan -p --format sarif
```

## Git Hook Integration

To ensure PromptHound runs automatically when developers commit changes to skill files, install the pre-commit hook:

```bash
cd scripts/
./install_hooks.sh
```

This installs a highly-targeted Python Git hook that uses `git diff --cached` to dynamically scan only the modified files residing in known skill directories (e.g. `.agents/skills`), preventing it from slowing down commits on normal documentation files.
