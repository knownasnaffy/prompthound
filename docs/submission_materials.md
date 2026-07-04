# PromptHound Submission Materials

## 1. Demo Script

**Context:** The presenter is in a terminal. They have a newly downloaded, third-party AI agent skill file named `awesome-dev-skill.md`. 

**Step 1: The "Looks Good to Me" Phase**
*Presenter:* "I just found this great new skill on a marketplace that claims to optimize my local build process. Let's take a look at it."
```bash
cat awesome-dev-skill.md
```
*Presenter:* "It looks like standard markdown. A description, some setup instructions, nothing obviously wrong. Most developers would just feed this straight into their AI agent."

**Step 2: The Scan**
*Presenter:* "But AI agent supply chains are vulnerable to semantic payloads and invisible steganography. Let's run PromptHound on it."
```bash
prompthound scan awesome-dev-skill.md
```

**Step 3: Explaining the Output**
*(The CLI outputs a high-risk report)*
*Presenter:* "PromptHound caught it instantly, entirely offline. Notice three distinct sections in the report:
1. **Rule Layer:** It caught an embedded hex blob in the setup block.
2. **Classifier Score:** It scored a 0.85 (Malicious). And crucially, because we use an interpretable Random Forest instead of a black-box LLM, it tells us exactly *why* by surfacing the most important features that drove the decision: like unusually high entropy and size-padding anomalies.
3. **Capability Chain:** It noticed that the instructions ask the agent to 'read a file', 'encode it', and 'send it over the network'. Even if those actions are benign individually, chained together they form an exfiltration pipeline."

**Step 4: CI/CD Integration**
*Presenter:* "PromptHound isn't just for manual checks. You can drop it straight into your CI pipeline using standard SARIF output or exit codes."
```bash
prompthound scan awesome-dev-skill.md --fail-on suspicious --format sarif
```
*Presenter:* "PromptHound acts as a sniffer, giving developers and pipelines the clear, interpretable signals they need to stay safe in the new agentic ecosystem."

---

## 2. Key Differentiators

Why PromptHound stands out in the AI agent security space:

1. **Focused on Agent Supply Chains, Not Prompt Injection:** Most tools (e.g., Rebuff, LLM Guard) are built to stop traditional prompt injection at the API boundary. PromptHound targets the **supply chain**—the third-party `SKILL.md` files downloaded from marketplaces, identifying semantic instruction hijacking and invisible payloads.
2. **Sniffer, Not Shield:** We do not attempt to sandbox or block the agent at runtime, which is complex and brittle. PromptHound is a fast, offline static analysis CLI that gives developers the information they need *before* installation.
3. **Interpretable by Construction:** Instead of using an opaque transformer model, PromptHound uses an interpretable Random Forest ensemble. Every classifier score is accompanied by the exact feature importances that drove the score (e.g., "Score: 0.85 driven by body_entropy and padding_ratio"). A developer is never left guessing why a file was flagged.
4. **Merge Without Flattening:** PromptHound preserves the distinction between deterministic rules (e.g., "Found `curl | bash`"), statistical anomalies (e.g., classifier scores), and structural sequences (capability chains). It merges these signals into one report without flattening them into a generic, unhelpful list of warnings.

---

## 3. Sample Scan Outputs

### Standard Human-Readable Output
```text
$ prompthound scan test-skill.md

⚠️  PROMPTHOUND SCAN REPORT: test-skill.md ⚠️
Risk Level: MALICIOUS (Score: 0.85)

--- 1. CLASSIFIER ANALYSIS ---
The statistical model flagged this file as Malicious.
Important Features:
  - body_entropy (Importance: 0.4200)
  - padding_ratio (Importance: 0.3100)

--- 2. RULE HITS ---
[PH001/shell-pipe] HIGH: Detected 'curl | bash' pattern in setup block (Line 14).
[PH003/unicode-tag] HIGH: Detected invisible Unicode Tag characters (Steganography) at byte offset 1024.

--- 3. CAPABILITY CHAINS ---
[PH200/capability-chain] WARNING: Dangerous sequence detected: read → encode → network_send
  - read (Line 22)
  - encode (Line 25)
  - network_send (Line 28)
```

### JSON Output
```json
{
  "file": "test-skill.md",
  "risk_score": 0.85,
  "risk_label": "malicious",
  "feature_importances": [
    {"feature": "body_entropy", "importance": 0.4200},
    {"feature": "padding_ratio", "importance": 0.3100}
  ],
  "rule_hits": [
    {"rule_id": "PH001/shell-pipe", "severity": "high", "line": 14, "message": "Detected 'curl | bash' pattern in setup block"},
    {"rule_id": "PH003/unicode-tag", "severity": "high", "byte_offset": 1024, "message": "Detected invisible Unicode Tag characters"}
  ],
  "capability_chains": [
    {
      "chain_name": "read→encode→network_send",
      "steps": [
        {"capability": "read", "line": 22},
        {"capability": "encode", "line": 25},
        {"capability": "network_send", "line": 28}
      ]
    }
  ]
}
```
