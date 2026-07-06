# PromptHound Benchmark Results

| Model | Macro-F1 (All) | Macro-F1 (Bundle) | Macro-F1 (Single) | FPR-Severe | FPR-Mild |
|---|---|---|---|---|---|
| GradientBoostingClassifier | 0.7759 | 0.7712 | 0.9324 | 0.0610 | 0.0213 |
| XGBClassifier | 0.7750 | 0.7717 | 0.8803 | 0.0579 | 0.0183 |
| LGBMClassifier | 0.7709 | 0.7648 | 0.9562 | 0.0579 | 0.1189 |
| DecisionTreeClassifier | 0.7537 | 0.7468 | 0.9562 | 0.0457 | 0.0915 |
| RandomForestClassifier | 0.7528 | 0.7444 | 1.0000 | 0.0152 | 0.0457 |
| LogisticRegression | 0.6686 | 0.6676 | 0.4453 | 0.0610 | 0.1189 |