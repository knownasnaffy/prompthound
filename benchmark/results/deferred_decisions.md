# PromptHound — Deferred Decisions Resolution

Resolves the four items listed as open in `tech-implementation.md §8`.
Based on the first full benchmark run (2026-07-04, `comparison.csv`/`comparison.md`).

---

## Decision 1: RiskScore.score → label thresholds

**Decision: score < 0.3 → benign | 0.3 ≤ score < 0.65 → suspicious | score ≥ 0.65 → malicious**

**Rationale:**
The top model (decision_tree, max_depth=3, min_samples_leaf=5, gini) is a depth-1 tree
with 3 nodes. It produces `predict_proba` output that clusters near 0.0 (benign) and
1.0 (malicious) with very little probability mass in between on this corpus.

Given the corpus is small (16 train / 5 test), we set a conservative middle band
(0.3–0.65) to label as "suspicious" rather than collapsing straight to binary. This
preserves the "sniffer, not shield" contract: a developer gets a graded signal rather
than a forced binary decision when the classifier is not fully confident.

- **0.0 – <0.3 → benign**: well below the decision boundary, no action needed.
- **0.3 – <0.65 → suspicious**: worth manual review; some signals present but below the
  malicious threshold. Maps to `--fail-on suspicious` in CI.
- **0.65 – 1.0 → malicious**: above the decision boundary, strong signal.

These thresholds will be revisited after the planned second corpus pass (~30/~30
benign/malicious) when the probability distributions are better calibrated.
They are recorded in `classifier/artifact/metadata.json` at promotion time.

---

## Decision 2: benign_unusual FPR — hard gate in promote.py vs advisory

**Decision: advisory in comparison table for now; add a soft warning (not hard reject) at > 40% FPR.**

**Rationale:**
The best runs in the benchmark achieve FPR(probe) = 0.20 (1/5 benign_unusual files
flagged). The worst random_forest runs reach 0.80.

With only 5 probe files, a hard gate at any threshold would be statistically fragile
(a single extra false positive flips a run from 0.20 → 0.40). Promoting a blanket
hard-reject rule on 5 files would give false confidence in the gate's precision.

**Policy for now:**
- `promote.py` prints a **warning** (not an error) when FPR(probe) > 0.40.
- The human promoter reads the warning and must explicitly acknowledge it.
- The FPR value is recorded in `metadata.json` so it is traceable.

**Revisit trigger:** once the benign_unusual probe set grows to ≥ 15 files, convert to
a hard gate at ≤ 0.20 FPR (i.e. at most 3/15 false positives). That size gives a
meaningful statistical signal.

---

## Decision 3: SARIF field mapping details (rule IDs, help URIs)

**Decision: use stable, lowercase-hyphenated rule IDs; help URIs point to the project README anchor.**

**Rule ID → SARIF ruleId mapping:**

| Module                 | ruleId                    | helpUri anchor            |
|------------------------|---------------------------|---------------------------|
| shell_pipe.py          | `PH001/shell-pipe`        | `#ph001-shell-pipe`       |
| encoded_blob.py        | `PH002/encoded-blob`      | `#ph002-encoded-blob`     |
| unicode_tag.py         | `PH003/unicode-tag`       | `#ph003-unicode-tag`      |
| suspicious_domain.py   | `PH004/suspicious-domain` | `#ph004-suspicious-domain`|
| padding.py             | `PH005/padding-anomaly`   | `#ph005-padding-anomaly`  |
| classifier (score)     | `PH100/classifier-score`  | `#ph100-classifier-score` |
| chains (chain flag)    | `PH200/capability-chain`  | `#ph200-capability-chain` |

**Conventions:**
- PH0xx = rule-layer hits (deterministic heuristics).
- PH1xx = classifier-layer findings (statistical score + local feature contributions).
- PH2xx = capability-chain findings (structural sequence detection).
- `helpUri` base: `https://github.com/<org>/prompthound/blob/main/README.md`
- SARIF `level`: "error" for malicious-threshold hits; "warning" for suspicious;
  "note" for info-severity rule hits.
- `properties.precision` set to "high" for rule-layer (deterministic), "medium" for
  classifier and chain findings (statistical / heuristic).

These mappings are implemented in `report.py` (Phase 9). This decision document is the
reference for that implementation.

---

## Decision 4: Corpus size targets

**Decision: current initial run (10 benign / 10 malicious) confirmed as viable for model selection; target 30/30 before final evaluation report.**

**Rationale from the benchmark:**
The 5-fold stratified CV ran cleanly on the 16-sample train split (≥2 samples per class
per fold, which is the minimum viable). The holdout metrics (F1=1.000) are perfect but
unsurprising on 5 test samples — they confirm the model can fit, not that it generalises
to unseen distributions.

**Targets:**
- **Current corpus (sufficient for Phase 7–8):** 10 benign / 10 malicious / 5 benign_unusual.
  Model selection is valid at this scale: we've identified which family (decision tree,
  shallow) and which hyperparameter region (min_samples_leaf≥5) works.
- **Before final evaluation report (Phase 12):** expand to ≥ 30 benign / ≥ 30 malicious,
  covering all five incident pattern categories from concept.md §1 with at least 3
  examples each. Expand benign_unusual to ≥ 15 files.
- **Source distribution target:** ≥ 50% self-authored or reconstructed-from-report;
  ≤ 50% scraped. All scraped files must be license-checked before commit.

**What the current results tell us (and don't):**
- The features *do* separate benign from malicious reliably on the current corpus —
  the tree finds a clean split at depth 1, which means at least one feature is highly
  discriminative.
- CV F1 of 0.73 (vs holdout F1 of 1.00) suggests some fold variance, consistent with
  a small corpus — not a generalisation concern at this stage.
- The FPR of 0.20 on 5 probe files is a promising signal but not a statistically
  meaningful bound yet.

---

## Summary table

| # | Decision | Status | Revisit trigger |
|---|----------|--------|----------------|
| 1 | RiskScore thresholds: <0.3 benign / 0.3–0.65 suspicious / ≥0.65 malicious | **Resolved** | After 30/30 corpus pass |
| 2 | FPR gate: advisory warning at >40%, not hard reject | **Resolved** | When probe set ≥ 15 files |
| 3 | SARIF rule ID scheme: PH0xx/PH1xx/PH2xx, helpUri to README anchors | **Resolved** | Implemented in Phase 9 (report.py) |
| 4 | Corpus targets: 10/10 now → 30/30 before eval report | **Resolved** | Phase 12 (evaluation report) |
