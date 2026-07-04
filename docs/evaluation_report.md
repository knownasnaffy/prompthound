# PromptHound Evaluation Report

## 1. Executive Summary

PromptHound was evaluated on a curated corpus of AI agent skill files to measure its ability to detect malicious instructions, steganographic payloads, and suspicious capability chains. The current evaluation is based on an initial corpus (16 training samples, 5 holdout test samples, and 5 benign-but-unusual probe samples). The best-performing model—a depth-3 Decision Tree—achieved perfect holdout precision and recall (F1=1.000), while maintaining a 20% false positive rate (FPR) on a deliberately challenging probe set of unusual but benign files.

## 2. Evaluation Metrics

**Main Corpus (Holdout Set)**
- **Precision:** 1.000
- **Recall:** 1.000
- **F1-Score:** 1.000
- **ROC-AUC:** 1.000

*Note: These perfect metrics on the holdout set indicate that the engineered features correctly separate the current malicious patterns from standard benign files. However, given the small holdout size (n=5), we expect these metrics to normalize to more realistic levels as the corpus expands.*

**False Positive Rate on `benign_unusual` Probe Set**
- **FPR:** 0.20 (1 out of 5 files flagged)
This metric is explicitly tracked and prioritized. The `benign_unusual` set contains legitimate skill files that use base64 encoding or shell commands for real reasons. A 20% FPR on this challenging set demonstrates that the classifier is not just blinding penalizing any shell command, though there is room for improvement.

## 3. Honest Comparison to Academic Benchmarks

Recent academic frameworks in this space, such as **SkillFortify**, report near-perfect precision and recall on curated benchmarks of agent skill supply chains. PromptHound achieves similar metric performance on its current holdout set (1.000 Precision/Recall). 

However, we **do not claim parity** with these academic frameworks for two reasons:
1. **Corpus Size:** Academic benchmarks often use hundreds or thousands of files. Our current evaluation relies on a much smaller seed corpus (16 train / 5 holdout).
2. **Scope of Tooling:** Frameworks like SkillFortify often employ formal analysis or enterprise-scale behavioral integrity verification (BIV) registries. PromptHound intentionally takes a lighter approach as a "sniffer, not shield" CLI tool for solo developers, running in sub-second time without external network calls.

While PromptHound is not a formal verification engine, it successfully bridges the gap between having no protection and requiring an enterprise security scanner, offering an interpretable and fast risk signal.

## 4. Model Selection and Interpretability

Interpretability is a first-class requirement for PromptHound. The benchmark harness was configured to break ties in F1 scores by preferring simpler, shallower models (the "interpretability penalty").

The selected model is a **Decision Tree (max_depth=3, min_samples_leaf=5, criterion=gini)**. With a mean depth of 1.0 and only 3 nodes, the model's logic is fully transparent. When PromptHound flags a file, the exact decision path (the features and thresholds that triggered the score) is surfaced in the report, rather than hiding behind an opaque neural network score.
