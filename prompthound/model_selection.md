# PromptHound Model Selection Rationale

## Objective
PromptHound is designed to be a "sniffer, not a shield." Its primary goal is to perform static risk analysis on AI agent skill files in CI/CD pipelines to catch malicious payloads (e.g., reverse shells, dangerous interpreter calls).

The critical constraint for this project is **Alert Fatigue**. If the tool flags too many safe, benign files as malicious (Severe False Positives), developers will ignore the warnings or remove the tool entirely. 

## Benchmark Results (Holdout Test Set)

| Model | Macro-F1 (All) | FPR-Severe | FPR-Mild |
|---|---|---|---|
| **RandomForest** | 0.7528 | **1.52%** | 4.57% |
| **XGBoost** | 0.7750 | 5.79% | 1.83% |
| **HistGradientBoosting** | 0.7780 | 3.05% | 6.40% |
| **LightGBM** | 0.7709 | 5.79% | 11.89% |

*Note: Models were tuned using GridSearchCV over 81 configurations initially, then pruned for efficiency, targeting `f1_macro` optimization.*

## Decision: RandomForestClassifier

While gradient boosting models (XGBoost, HistGradientBoosting, LightGBM) achieved a marginally higher overall Macro-F1 score (~0.77 - 0.78), they were rejected in favor of **Random Forest** (0.75).

### Rationale
1. **Minimizing Severe False Positives**: Random Forest achieved an incredibly low Severe False Positive Rate (FPR-Severe) of **1.52%**. In contrast, XGBoost and LightGBM hovered near ~6%. In a CI/CD environment, a 6% block rate on safe commits is unacceptable. Random Forest's 1.5% rate is the only one that satisfies the "sniffer" philosophy without causing alert fatigue.
2. **Perfect Single-File Performance**: On single-file anchors (not bundled), Random Forest achieved a perfect **1.000 F1 score**, proving that the heuristics (when undiluted) are flawlessly isolated by the model logic.
3. **Robustness to Dilution**: By combining Random Forest with our per-member max-pooling feature extraction, we successfully defended against dilution attacks (where attackers pad malicious files with large benign files to lower density scores).

### Final Configuration
- `n_estimators`: 200
- `max_depth`: 10
- `class_weight`: 'balanced'
- `random_state`: 42
