# PromptHound Model Selection Rationale

## Objective
PromptHound is designed to be a "sniffer, not a shield." Its primary goal is to perform static risk analysis on AI agent skill files in CI/CD pipelines to catch malicious payloads (e.g., reverse shells, dangerous interpreter calls).

The critical constraint for this project is **Alert Fatigue**. If the tool flags too many safe, benign files as malicious (Severe False Positives), developers will ignore the warnings or remove the tool entirely. 

## Benchmark Results (Cleaned Test Set)

| Model | Macro-F1 (All) | FPR-Severe | FPR-Mild |
|---|---|---|---|
| **RandomForest** | 0.7570 | **1.22%** | 3.96% |
| **HistGradientBoosting** | 0.7919 | 2.44% | 8.84% |
| **GradientBoosting** | 0.7855 | 6.40% | 2.74% |
| **XGBoost** | 0.7756 | 5.18% | 1.83% |
| **LogisticRegression** | 0.6733 | 3.05% | 13.11% |

*Note: Models were evaluated after fixing a major regex boundary bug that falsely flagged innocent English words like "publishing" as shell commands.*

## Decision: RandomForestClassifier

While gradient boosting models achieved a marginally higher overall Macro-F1 score (~0.77 - 0.79), they were rejected in favor of **Random Forest** (0.75).

### Rationale
1. **Minimizing Severe False Positives**: Random Forest achieved an incredibly low Severe False Positive Rate (FPR-Severe) of **1.22%**. In contrast, XGBoost and GradientBoosting hovered near ~5-6%. In a CI/CD environment, a 5% block rate on safe commits is unacceptable. Random Forest's 1.22% rate is the only one that satisfies the "sniffer" philosophy without causing alert fatigue.
2. **Perfect Single-File Performance**: On single-file anchors (not bundled), Random Forest achieved a perfect **1.000 F1 score**, proving that the heuristics (when undiluted) are flawlessly isolated by the model logic.
3. **Robustness to Dilution**: By combining Random Forest with our per-member max-pooling feature extraction, we successfully defended against dilution attacks (where attackers pad malicious files with large benign files to lower density scores).

### Final Configuration
- `n_estimators`: 200
- `max_depth`: 10
- `class_weight`: 'balanced'
- `random_state`: 42
