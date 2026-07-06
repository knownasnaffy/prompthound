# PromptHound Benchmark Results

| Model | Macro-F1 (All) | Macro-F1 (Bundle) | Macro-F1 (Single) | FPR-Severe | FPR-Mild |
|---|---|---|---|---|---|
| HistGradientBoostingClassifier | 0.7919 | 0.7848 | 1.0000 | 0.0244 | 0.0884 |
| GradientBoostingClassifier | 0.7855 | 0.7809 | 0.9324 | 0.0640 | 0.0274 |
| XGBClassifier | 0.7756 | 0.7716 | 0.9072 | 0.0518 | 0.0183 |
| RandomForestClassifier | 0.7570 | 0.7488 | 1.0000 | 0.0122 | 0.0396 |
| DecisionTreeClassifier | 0.7533 | 0.7473 | 0.9324 | 0.0396 | 0.1128 |
| LogisticRegression | 0.6733 | 0.6638 | 0.8803 | 0.0305 | 0.1311 |