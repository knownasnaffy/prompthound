# PromptHound — Concept

**Scope:** CLI tool. Static risk analysis for AI agent skill files (`SKILL.md`,
`AGENTS.md`, and similar markdown-driven capability packages).

**Philosophy:** Sniffer, not shield. Detect, score, explain. Final call stays
with the developer or CI pipeline.

---

## 1. Problem statement

AI coding agents (Claude Code, OpenClaw, Codex, etc.) now load third-party
"skills" — markdown files that declare capabilities and instruct the agent's
behavior at runtime, often fetched from public marketplaces or GitHub. This is
a fundamentally different supply chain than npm or PyPI: the payload isn't
machine code, it's natural-language instruction interpreted by a model.
Traditional scanners (static analysis, sandboxing, dependency signing) don't
map cleanly onto this because there's no fixed grammar to parse — the "exploit"
can just be a sentence.

This has already produced large-scale real incidents:
- A coordinated campaign ("ClawHavoc") compromised over 1,000 skills on the
  OpenClaw marketplace (ClawHub), delivering credential stealers through
  instructions embedded in setup code blocks.
- Independent audits found roughly a third of sampled skills carried some
  security flaw, with a smaller but nonzero fraction carrying confirmed
  malicious payloads (credential exfiltration, arbitrary command execution).
- A distinct technique uses Unicode Tag characters (U+E0000–U+E007F) to hide
  instructions inside a skill file — invisible in a normal editor or markdown
  preview, but read as semantic content by the model.
- Marketplace scanners have been evaded by padding malicious files with junk
  data past the size threshold scanners bother processing.
- Attacks increasingly chain individually-benign-looking capabilities (read
  a file → encode it → send it over the network) rather than tripping a single
  obvious rule. The common thread: existing marketplace scanners (VirusTotal,
  ClawScan-style tools) catch known signatures but miss semantic instruction
  hijacking, steganographic payloads, and capability chains — and they don't
  explain *why* something is risky, which makes triage slow for a developer
  deciding whether to install a skill.

## 2. What PromptHound does (MVP)

```bash
prompthound scan path/to/SKILL.md
```

Pipeline:

1. **Parse** — split frontmatter (declared name/description/capabilities) from
body content and code blocks.
2. **Rule layer** — fast heuristic checks for known-bad patterns: `curl | bash`
/ `wget | sh` pipelines, base64/hex blobs, Unicode Tag character presence,
suspicious or newly-registered-looking domains, abnormal file-size padding.
3. **Feature extraction** — turn the file into a numeric feature vector (see
§3).
4. **Classifier** — a Random Forest scores risk from the feature vector. Chosen over an opaque transformer classifier specifically because it stays interpretable: every score traces back to which features fired.
5. **Capability-chain check** — compare what the frontmatter *declares* the
skill needs against what the body actually references or executes, and flag
known dangerous sequences (file read → encode → network send; download → write
→ execute) even when no single step looks malicious alone.
6. **Explanation output** — human-readable risk report plus `--format
sarif|json` for CI consumption. Every flagged item names the rule or feature
that triggered it, no LLM-generated prose required for the core report.

## 3. Feature set for the classifier

- Presence/ratio of base64 or hex-encoded blobs
- Shell command block presence, pipe-to-interpreter patterns
- Unicode Tag character count (steganography signal)
- Declared-capability vs. referenced-capability mismatch score (frontmatter vs.
  body)
- External URL count and basic domain heuristics
- Instruction-override / urgency phrase density ("first and foremost,"
  "important," all-caps runs)
- File size / padding anomaly relative to code-to-prose ratio
- Shannon entropy of body text
- **Code-block-to-prose ratio**: Normal skills have instructions explaining what to do. Malicious payloads often just dump a massive block of code and say "run this." This ties directly back to the classifier prioritizing interpretability — the contribution isn't "train a model," it's picking features that make the features genuinely mean something a developer can act on.

## 4. Evaluation plan

- Build a small labeled corpus: benign skills pulled from public GitHub skill
  repos, malicious examples reconstructed from published takedown reports (Unit
  42, Orca Security, Cloud Security Alliance write-ups) and awareness repos.
- Report standard precision / recall / F1.
- Explicitly test false positive rate on benign-but-unusual skills (legitimate
  skills that use base64 or shell commands for real reasons) — this is the
  metric that's easy to skip and usually decides whether a tool is actually
  usable versus just noisy.
- Position results against what's publicly reported for comparable academic
  work (e.g. formal-analysis frameworks in this space report near-perfect
  precision on curated benchmarks) — not to claim parity, but to have an honest
  reference point.

## 5. Why this angle over generic prompt-injection detection

Generic "classify this prompt as injection or not" is saturated — Rebuff, LLM
Guard, ProtectAI's DeBERTa classifier, and Meta's Prompt Guard already cover
that ground with production-scale training data. Skill-file supply chain
security is newer, actively being written about through 2026, and the closest
serious work (formal capability-sandboxing frameworks, large-registry
behavioral-integrity scanners) is academic or enterprise-scale, not
a lightweight tool a developer runs before installing a skill. A focused,
interpretable, open source CLI that a solo developer can actually run in five
seconds before `git clone`-ing a skill fills a real gap between "nothing" and
"enterprise registry auditing."

## 6. Explicitly out of scope for the course deliverable

- MCP server integration
- Claude Code / Codex / OpenCode plugins
- CI/CD and git hook integrations
- Capability sandboxing / enforcement (only detection, not confinement)
- Large-scale registry crawling These stay in the README as future work. The
  deadline deliverable is the CLI, the classifier, and the evaluation report.

## 7. Sources consulted

- Palo Alto Networks Unit 42 — OpenClaw/ClawHub skill marketplace threat
  analysis
- Orca Security — attack primitives in an AI agent skill marketplace
- Cloud Security Alliance AI Safety Initiative — SKILL.md agent context
  poisoning research note
- Darkreading — ClawHub malicious skills coverage
- CSO Online — AI coding agent supply chain attacks
- arXiv — formal analysis frameworks for agent skill supply chains
  (SkillFortify)
- Unit 42 — behavioral integrity verification across the OpenClaw skill
  registry (BIV)

