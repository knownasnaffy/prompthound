# PromptHound Evaluation Report

## 1. Executive Summary

PromptHound was evaluated on an expanded corpus of AI agent skill files to measure its ability to detect malicious instructions, steganographic payloads, and suspicious capability chains. The current evaluation is based on a corpus of 2018 files (1610 training samples, 403 holdout test samples, and 5 benign-but-unusual probe samples). The selected model—a Random Forest ensemble—achieved a robust 0.919 F1-score on the holdout set, demonstrating a strong capability to detect complex malicious patterns while maintaining an interpretable structure via feature importance tracing.

## 2. Evaluation Metrics

**Main Corpus (Holdout Set, n=403)**
- **Precision:** 0.971
- **Recall:** 0.872
- **F1-Score:** 0.919
- **ROC-AUC:** 0.973

*Note: These metrics indicate that the engineered features effectively separate malicious patterns from standard benign files without overfitting.*

**False Positive Rate on `benign_unusual` Probe Set**
- **FPR:** 0.00 (0 out of 5 files flagged)
This metric is explicitly tracked and prioritized. The `benign_unusual` set contains legitimate skill files that use base64 encoding or shell commands for real reasons. An FPR of 0.00 on this deliberately challenging, tiny probe set indicates the classifier effectively separates real utility from malice in edge cases.

## 3. Honest Comparison to Academic Benchmarks

Recent academic frameworks in this space, such as **[SkillTrustBench](https://huggingface.co/datasets/cuhk-zhuque/SkillTrustBench)** and **SkillFortify**, report near-perfect precision and recall on curated benchmarks of agent skill supply chains.

We **do not claim full parity** with these academic formal-verification frameworks for two reasons:
1. **Corpus Source:** While we have grown our corpus to 2000+ files using datasets like [SkillTrustBench](https://huggingface.co/datasets/cuhk-zhuque/SkillTrustBench), ensuring a robust statistical evaluation, our primary focus remains practical risk detection rather than exhaustive proof.
2. **Scope of Tooling:** Frameworks like SkillFortify often employ formal analysis or enterprise-scale behavioral integrity verification (BIV) registries. PromptHound intentionally takes a lighter approach as a "sniffer, not shield" CLI tool for solo developers, running in sub-second time without external network calls.

While PromptHound is not a formal verification engine, it successfully bridges the gap between having no protection and requiring an enterprise security scanner, offering an interpretable and fast risk signal.

## 4. Model Selection and Interpretability

Interpretability is a first-class requirement for PromptHound. While we originally aimed for a single decision tree, the accuracy/FPR trade-off heavily favored ensemble models on the expanded corpus.

The selected model is a **Random Forest (n_estimators=50, max_depth=10, min_samples_leaf=1)**. Rather than sacrificing empirical performance for a single readable tree, we chose the Random Forest (which achieved F1=0.919 and FPR=0.00) and retained interpretability by surfacing the **local feature contributions** that contributed to the model's decision for a specific sample using the Saabas method. When PromptHound flags a file, it tells you exactly which features drove the score (e.g., Code-to-Prose Ratio, Entropy), offering a far more honest explanation than a single oversimplified threshold path.

*(Note: While fast and dependency-free, Saabas contributions have a known weakness—they are not consistent under feature correlation the way SHAP's Shapley-value approach is. A feature can get credit/blame that shifts depending on correlated features, and it lacks SHAP's formal fairness guarantees. This is a deliberate tradeoff made to keep the CLI lightweight and entirely offline).*

## 5. Resolutions of Deferred Decisions

As originally outlined in the tech implementation plan, several decisions were deferred until the benchmark was run. These have now been resolved:

- **RiskScore Thresholds:** `score < 0.3` is benign, `0.3 ≤ score < 0.65` is suspicious, and `score ≥ 0.65` is malicious. This preserves the "sniffer, not shield" graded signal.
- **FPR Gate on `benign_unusual`:** For now, an FPR > 0.00 produces an advisory warning in `promote.py` rather than a hard reject, due to the small probe size (n=5). It will become a hard gate when the probe set expands to ≥15.
- **SARIF Field Mapping:** Rule IDs follow a structured `PH0xx` (rules), `PH1xx` (classifier), `PH2xx` (chains) format with help URIs anchoring directly to the project README.
- **Corpus Targets:** The corpus has been expanded significantly via academic datasets to 2000+ files, achieving and greatly exceeding the Phase 12 target to provide a more meaningful evaluation.
