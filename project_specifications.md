# PromptHound — Project Specifications

## 1. Project Overview
- **Name:** PromptHound
- **Type:** CLI Tool
- **Purpose:** Static risk analysis for AI agent skill files (e.g., `SKILL.md`, `AGENTS.md`) and multi-file skill bundles.
- **Philosophy:** "Sniffer, not shield. Detect, score, explain." The tool provides detection and explanation of risks, leaving the final execution or block decision to the developer or CI pipeline.

## 2. Core Features & Use Cases
- **Single-File Scan:** Analyze a standalone skill markdown file.
  - *Command:* `prompthound scan path/to/SKILL.md`
- **Bundle Scan:** Recursively analyze a directory containing an anchor skill file along with auxiliary files (scripts, configs, etc.).
  - *Command:* `prompthound scan path/to/skill-dir/ -d`

## 3. System Architecture & Pipeline

### 3.1 Flattening (Bundle Mode Only)
- **Merge-Before-Parse:** All files in the bundle are concatenated into a single synthetic buffer before parsing. This ensures the unit of analysis matches how the agent consumes the bundle at runtime.
- **Fencing:** Every non-anchor member (including prose) is wrapped in a synthetic fence (`--- BEGIN MEMBER: <path> ---` / `--- END MEMBER ---`).
- **Binary/Non-UTF-8 Files:** Represented by an empty fence to accurately count towards bundle size and member count without injecting spurious signal.
- **Deterministic Ordering:** Members are sorted by relative path to ensure reproducible scans.
- **SourceSpan Manifest:** Tracks the original file and line offsets for every segment in the merged buffer, enabling accurate location reporting later on.
- **Size Limits:** Enforces a bundle size and file-count cap. Exceeding this cap results in a truncated scan with a warning.

### 3.2 Parse
- Separates the frontmatter (name, description, declared capabilities) from the body content and code blocks. Operates identically on single files or flattened bundles.

### 3.3 Rule Layer
- Executes fast heuristic checks for known-bad patterns across the flattened buffer:
  - `curl | bash` / `wget | sh` pipelines
  - Base64 or Hex encoded blobs
  - Unicode Tag characters (steganography)
  - Suspicious or newly-registered domains
  - Abnormal file-size padding

### 3.4 Feature Extraction
- Generates a numeric feature vector for classification.
- **Core Features:** 
  - Base64/hex blob presence/ratio
  - Shell command block presence
  - Unicode Tag character count
  - Declared vs. referenced capability mismatch score
  - External URL count
  - Instruction-override / urgency phrase density
  - File size / padding anomaly
  - Shannon entropy of body text
  - Code-block-to-prose ratio
- **Bundle-Specific Features:**
  - `is_bundle` (boolean)
  - `member_count` (integer)
- **Anti-Dilution Mechanism:** Ratio features (e.g., `padding_ratio`) are computed *per member*, with the maximum value taken across the bundle. Count-based features are summed.

### 3.5 Classifier
- **Model:** Random Forest. Chosen for its interpretability so every risk score can be traced back to specific features.
- **Architecture:** A single model scores both single files and bundles, differentiated by the `is_bundle` and `member_count` features.

### 3.6 Capability-Chain Check
- Compares declared capabilities against what the body actually references or executes.
- Flags known dangerous sequences (e.g., file read → encode → network send), even if the steps are split across different files within the bundle.

### 3.7 Output & Reporting
- **Human-Readable Report:** Clearly explains the risk score, naming the specific rules or features that triggered it.
- **CI/CD Integration:** Supports structured output via `--format sarif|json`.
- **Traceability:** Utilizes the `SourceSpan` manifest to pinpoint the exact file and line number for any flagged item in a bundle.

## 4. Evaluation Plan
- **Dataset / Corpus:** A labeled corpus spanning three classes (`safe`, `suspicious`, `malicious`), including both single-file and bundle examples.
- **Metrics:** Precision, Recall, and Macro-F1 (`f1_macro`).
- **False Positive Tracking:**
  - `fpr_severe`: Safe files incorrectly scored as `malicious`.
  - `fpr_mild`: Safe files incorrectly scored as `suspicious`.
- **Probe Set:** A dedicated, held-out set of benign-but-unusual skills (e.g., legitimate scripts using base64 or multiple helpers) to test the robustness of bundle-specific features.

## 5. Out of Scope (For MVP)
*The following features are excluded from the initial deliverable and remain as future work:*
- MCP server integration.
- Direct plugins for AI agents (Claude Code, OpenClaw, Codex, etc.).
- Automated CI/CD and git hook integrations.
- Capability sandboxing or enforcement (detection only).
- Large-scale registry crawling and bulk analysis.
