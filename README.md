# PromptHound 🐕

PromptHound is a static risk analysis tool for AI agent skill files. It acts as a "sniffer, not a shield" — detecting malicious payloads, obfuscation attempts, and capability mismatches in agent skill files without causing alert fatigue. The final decision to block or allow always stays with the developer or CI pipeline.

## Features
- **Heuristic Engine**: Detects dangerous interpreter calls (`eval`, `exec`), shell access, base64 obfuscation, and credential exposure.
- **Anti-Dilution Architecture**: Parses companion file "bundles" to ensure malicious payloads cannot be hidden by padding them with massive benign files.
- **Low False Positives**: Powered by a tuned Random Forest model optimized specifically to minimize Severe False Positives (<1.5%) so your developers aren't blocked by noise.

## 1. Initial Setup

First, clone the repository and set up a Python virtual environment:

```bash
git clone https://github.com/knownasnaffy/prompthound.git
cd prompthound
python -m venv .venv
source ./.venv/bin/activate
```

## 2. Using the CLI

To use the PromptHound CLI with the pre-trained model, install the required dependencies:

```bash
pip install -e .
```

You can now scan skill files and bundles:

```bash
# Scan a single skill file
prompthound scan /path/to/SKILL.md

# Scan a skill bundle directory recursively
prompthound scan -d /path/to/skill_bundle/

# Scan the current project for known skill directories
prompthound scan -p

# Output as JSON or SARIF
prompthound scan /path/to/SKILL.md --format json
```

## 3. Web App

PromptHound also includes a Streamlit web app. Install the `app` dependencies to run it:

```bash
pip install -e ".[app]"
streamlit run app.py
```

## 4. Development & Training

If you want to train the model, run benchmarks, or contribute to the project, install the `dev` dependencies:

```bash
pip install -e ".[dev]"
```

The `scripts/` directory contains tools for the ML pipeline. Run them in this order:

1. **Extract Data**: Reads the dataset and extracts features into `data/features.npz`. This file contains the numerical features required for training.
   ```bash
   python scripts/extract_data.py
   ```
2. **Benchmark**: Benchmarks multiple models (defined in `data/models.yaml`) and generates `benchmark_report.md`.
   ```bash
   python scripts/benchmark.py
   ```
3. **Train Model**: Trains the Random Forest model on the extracted features and saves it as `src/prompthound/model.joblib`.
   ```bash
   python scripts/train.py
   ```
4. **Error Analysis**: Analyzes false negatives from the dataset to help improve feature engineering.
   ```bash
   python scripts/error_analysis.py
   ```

## 5. Integrations

### Git Hooks
You can install a pre-commit hook to automatically scan skills before they are committed:
```bash
./scripts/install_hooks.sh
```

### verify_skill Agent Skill Integration
*Pending - coming soon.*


## 6. Comparison with Alternative Tools

Other security scanners take different architectural approaches:

- **[NVIDIA SkillSpector](https://github.com/NVIDIA/skillspector)**: Sends skills to LLMs for semantic evaluation and queries OSV.dev for live vulnerability data.
- **[Cisco skill-scanner](https://github.com/cisco-ai-defense/skill-scanner)**: Combines static YARA rules with LLM-as-a-judge and behavioral dataflow analysis, specifically targeting OpenAI Codex and Cursor Agent rules.
- **[Tencent AI-Infra-Guard](https://github.com/Tencent/AI-Infra-Guard)**: A heavy, full-stack AI Red Teaming platform requiring Docker. It bundles jailbreak evaluation, infrastructure scanning, and agent testing.

PromptHound is built for environments with strict constraints:
- **Air-gapped.** PromptHound relies on a local Random Forest classifier and offline heuristics. It makes zero network calls. Skill files never leave your machine, and scans finish in milliseconds.
- **Deterministic evidence.** The classifier surfaces the local feature contributions (via Saabas decomposition) that drove each score. Scores and contributions are exactly reproducible across CI runs without LLM-as-a-judge variance.

Use the LLM-backed suites above for deep semantic analysis or ecosystem auditing. Use PromptHound for offline, sub-second pre-commit hooks.

## 7. Acknowledgements

Our evaluation corpus and dataset generation heavily rely on the following open-source datasets:
- **[cuhk-zhuque/SkillTrustBench](https://huggingface.co/datasets/cuhk-zhuque/SkillTrustBench)**
- **[yoonholee/agent-skill-malware](https://huggingface.co/datasets/yoonholee/agent-skill-malware)**
