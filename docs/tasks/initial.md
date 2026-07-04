# PromptHound — Task List

Derived from `concept.md`, `prompthound-architecture-flow.md`, `prompthound-tech-implementation.md`, and `AGENTS.md`. Phases are ordered by dependency — each phase assumes every prior phase is complete. Do not skip ahead; several later phases (benchmark, promotion, reporter) will silently produce garbage if an earlier stage is incomplete or untested.

---

## Phase 0 — Project Scaffolding

- [x] Initialize git repo, add `.gitignore` (venv, `__pycache__`, `.joblib` build artifacts that aren't the committed one, `results/*.csv`/`*.md` if regenerated locally before first commit)
- [x] Create the full directory layout from tech-implementation.md §2 as empty stubs (`prompthound/`, `rules/`, `classifier/`, `benchmark/`, `tests/unit/`, `tests/integration/`)
- [x] Write `pyproject.toml` with dependencies from tech-implementation.md §7 (`click`, `python-frontmatter`, `markdown-it-py`, `scikit-learn`, `joblib`, `pyyaml`, `pytest` dev, `lightgbm` as optional `[lgbm]` extra)
- [x] Set up `.venv`, editable install (`pip install -e ".[dev]"`), confirm `prompthound --help` runs (even as a stub) per AGENTS.md §2
- [x] Configure `ruff` (check + format) in `pyproject.toml`
- [x] Configure `pytest` (test paths, any markers needed for slow/integration tests)
- [x] Commit scaffolding as the baseline

**Exit criteria:** empty package installs, `prompthound --help` and `pytest` both run without error (even with zero real tests/logic yet).

---

## Phase 1 — Shared Schemas (`schema.py`)

- [x] Implement all dataclasses exactly as specified in tech-implementation.md §3: `CodeBlock`, `ParsedSkill`, `RuleHit`, `FeatureVector`, `RiskScore`, `ChainFlag`, `ScanResult`
- [x] Confirm field types match (e.g. `unicode_tag_spans: list[tuple[int,int]]`, `decision_path: list[dict]`)
- [x] Add docstrings noting which stage produces / consumes each field, referencing architecture.md §1 diagram
- [x] Unit tests: instantiate each dataclass with representative values, confirm no implicit mutation between fields (e.g. `ScanResult` fields are independently settable)

**Exit criteria:** `schema.py` is the single import source for every later stage; no other module redefines these shapes.

---

## Phase 2 — Parse Stage (`parse.py`)

- [x] Implement frontmatter/body/code-block splitting using `python-frontmatter` + `markdown-it-py` token stream (not regex), per tech-implementation.md §4
- [x] Ensure every `CodeBlock` carries real `start_line`/`end_line` and language/fence tag
- [x] Implement Unicode Tag character detection (U+E0000–U+E007F) over `raw_bytes` *before* any decoding step; store as `unicode_tag_spans`, never strip
- [x] Implement the shared padding/size-anomaly helper referenced in tech-implementation.md §4 (consumed later by both `rules/padding.py` and `features.py::padding_ratio`)
- [x] Implement malformed-input short-circuit: no frontmatter / binary garbage / empty file → `parse_ok=False`, `parse_error` set, no partial `ParsedSkill` fields left in a misleading state (architecture.md §4)
- [x] Build golden fixtures under `tests/unit/fixtures/parse/`: a valid skill file, a no-frontmatter file, a binary-garbage file, an empty file
- [x] Unit tests for each fixture, asserting exact `ParsedSkill` output (or `parse_ok=False` + `parse_error`)

**Exit criteria:** every fixture produces the exact expected `ParsedSkill`; malformed inputs never reach a state that looks like a valid parse.

---

## Phase 3 — Rule Layer (`rules/`)

- [x] Implement `rules/__init__.py` with the `ALL_RULES` registry list
- [x] `shell_pipe.py` — `curl|bash` / `wget|sh` pipeline detection
- [x] `encoded_blob.py` — base64/hex blob detection
- [x] `unicode_tag.py` — flags presence using `parse.py`'s preserved spans
- [x] `suspicious_domain.py` — basic domain heuristics (newly-registered-looking, non-standard TLD patterns, etc.)
- [x] `padding.py` — consumes the shared helper from Phase 2, does not recompute padding logic independently
- [x] Confirm structurally that no rule imports another rule or a shared mutable context object (AGENTS.md §5 — this is a hard constraint, not a style preference)
- [x] Golden-file unit test per rule: one fixture that triggers it, one that doesn't, per AGENTS.md §7 "definition of done"

**Exit criteria:** `[hit for rule in ALL_RULES for hit in rule(parsed)]` runs cleanly over every Phase-2 fixture and produces only the expected hits.

---

## Phase 4 — Feature Extraction (`features.py`)

- [x] Implement one pure function per feature in concept.md §3:
  - base64/hex blob ratio
  - shell command block presence / pipe-to-interpreter pattern
  - Unicode Tag character count
  - declared-vs-referenced capability mismatch score
  - external URL count + domain heuristics
  - instruction-override / urgency phrase density
  - file size / padding anomaly ratio (shared helper from Phase 2)
  - Shannon entropy of body text
  - code-block-to-prose ratio
- [x] Define and freeze the canonical column order (`FeatureVector.order`) — this order is load-bearing for the classifier stage, changing it later requires retraining
- [x] Confirm every function takes only `ParsedSkill` — never `RuleHit[]` (architecture.md §2.3, AGENTS.md §5 hard constraint)
- [x] Unit tests asserting exact numeric feature values on hand-crafted fixtures (not just "feature fired," but the actual computed number)

**Exit criteria:** `features.py` runs over every corpus-shaped fixture and produces a fully-populated `FeatureVector` with deterministic values.

---

## Phase 5 — Capability-Chain Check (`chains.py`)

- [x] Implement capability-tagged event extraction from `ParsedSkill` (frontmatter declared capabilities + body-referenced/executed capabilities), each tagged with source line
- [x] Define the fixed set of named dangerous sequences (ordered capability-tag lists), starting with `["file_read","encode","network_send"]` and `["download","write","execute"]`
- [x] Implement subsequence matching (not exact-adjacency) per tech-implementation.md §4
- [x] Handle the empty/no-chain case as a valid, non-error result (architecture.md §4)
- [x] Unit tests: a fixture with a clean adjacent chain, a fixture with the same chain split across non-adjacent lines, a fixture with no chain at all

**Exit criteria:** `chains.py` correctly flags both adjacent and scattered chains, and correctly returns `[]` (not an error) for benign files.

---

## Phase 6 — Benchmark Corpus Construction

- [x] Populate `benchmark/corpus/benign/` — real, license-checked or self-authored skill files
- [x] Populate `benchmark/corpus/malicious/` — reconstructed examples per concept.md §1/§7 incident patterns: credential-stealer setup blocks (ClawHavoc-style), Unicode Tag hidden instructions, padding/size-anomaly evasion, chained read→encode→send / download→write→execute sequences
- [x] Populate `benchmark/corpus/benign_unusual/` — legitimate skills that genuinely use base64 or shell commands for real reasons (the FPR probe set); keep this eval-only, never mixed into training (AGENTS.md §6)
- [x] Write `labels.csv` (`filepath,label,source,notes`), tagging `source` as self-authored / reconstructed-from-report / scraped
- [x] Sanity pass: run every corpus file through Phase 2 + Phase 4 code and confirm no parse failures or feature-extraction exceptions before benchmark code depends on it
- [x] Decide and document initial corpus size targets (deferred decision from tech-implementation.md §8) now that rule/feature coverage exists to judge against

**Exit criteria:** every corpus file parses cleanly and produces a full feature vector; `labels.csv` accounts for every file with no orphaned or mislabeled entries.

---

## Phase 7 — Benchmark Harness

- [ ] Write `benchmark/models.yaml` search space exactly as specified in tech-implementation.md §5.2 (decision_tree, random_forest, gradient_boosting, optional lightgbm; stratified_kfold eval config, `fpr_probe_set: benign_unusual`, `primary_metric: f1`, `tie_breaker: interpretability_penalty`)
- [ ] Implement `classifier/train.py` — training entry point, invoked only by the benchmark harness (never at `scan` runtime, AGENTS.md §5)
- [ ] Implement `benchmark/run_benchmark.py`:
  - load `labels.csv`, run parse+features once per file, cache and share across all candidates
  - grid-search each candidate via stratified k-fold on `benign`+`malicious` only
  - record precision/recall/F1/ROC-AUC, FPR on `benign_unusual`, mean tree depth/node count, fit+predict wall-clock time
  - write `results/comparison.csv` and rendered `results/comparison.md`, sorted by primary metric with tie-breaker applied
- [ ] Run the first full benchmark pass
- [ ] Use the results to resolve the deferred decisions from tech-implementation.md §8:
  - [ ] `RiskScore.score` → label thresholds (benign/suspicious/malicious)
  - [ ] whether `benign_unusual` FPR is a hard gate in `promote.py` or advisory
  - [ ] SARIF field mapping details (rule ids, help URIs)
  - [ ] confirm or revise corpus size targets from Phase 6

**Exit criteria:** `comparison.md` shows a ranked table across all candidates with the tie-breaker correctly applied; all four deferred decisions have a written resolution (even if "advisory for now, revisit later").

---

## Phase 8 — Classifier Promotion & Inference

- [ ] Implement `benchmark/promote.py` — copies the winning (or specified `--run-id`) fitted estimator into `prompthound/classifier/artifact/model.joblib`, writes `metadata.json` (model family, hyperparameters, corpus version/hash, metrics, date)
- [ ] Run promotion, commit the artifact + metadata
- [ ] Implement `classifier/model.py` — loads the committed `.joblib` only, calls `.predict_proba()` + `.decision_path()` (or LightGBM's leaf-path equivalent), returns `RiskScore` with populated `decision_path`
- [ ] Confirm `classifier/model.py` never imports `classifier/train.py` (AGENTS.md §5 hard constraint) and never trains at runtime
- [ ] Unit test: load the committed artifact, run inference on a known fixture, assert score + decision path are non-trivial and stable across runs

**Exit criteria:** inference is sub-second, deterministic, and fully traceable to the `metadata.json` provenance record.

---

## Phase 9 — Reporter (`report.py`)

- [ ] Implement `render_human`, `render_json`, `render_sarif`, all consuming the same `ScanResult`
- [ ] Enforce the non-negotiable constraint from architecture.md §2.6 / AGENTS.md §5: rule hits, classifier score+decision path, and chain flags must remain visibly separate in every output format — no flattening into one undifferentiated warning list
- [ ] Apply the SARIF field mapping resolved in Phase 7 (rule ids, help URIs)
- [ ] Snapshot tests for all three renderers over a fixed set of `ScanResult` fixtures (clean file, rule-only hit, classifier-only high score, chain-flag case, all-three-at-once case)

**Exit criteria:** the "merge without flattening" property is enforced by a test, not just visually inspected.

---

## Phase 10 — CLI Wiring (`cli.py`)

- [ ] Implement `click` entry point: `prompthound scan <path> [--format human|json|sarif] [--fail-on <threshold>]`
- [ ] Wire the full pipeline: resolve path → Parse → (Rule layer ∥ Feature extraction → Classifier) → Capability-chain check → Reporter, matching architecture.md §1 exactly
- [ ] Implement malformed-file short-circuit end-to-end: `parse_ok=False` → skip every later stage → Reporter renders "could not parse" (never a misleadingly low score)
- [ ] Implement `--fail-on` exit-code logic (the one enforcement-adjacent behavior in scope, per architecture.md §3)
- [ ] Confirm zero disk writes and zero network calls anywhere in the `scan` path (AGENTS.md §2, §5)
- [ ] Manual smoke test against a handful of real and malicious-pattern files

**Exit criteria:** `prompthound scan` works end-to-end for all three output formats and correct exit codes, entirely offline.

---

## Phase 11 — Full Test Suite & QA

- [ ] Complete unit test coverage for every stage (parse, rules, features, chains, classifier, reporter) if any gaps remain from earlier phases
- [ ] Integration tests: full `scan()` over a small fixed subset of `benchmark/corpus/`, snapshot-checked for human/json/sarif output (tests/integration)
- [ ] Malformed-input tests specifically re-run and confirmed (binary garbage, no frontmatter, empty file) per AGENTS.md §7
- [ ] Full `pytest` run green, `ruff check .` and `ruff format .` clean
- [ ] Re-verify: no stage imports across forbidden boundaries (`rules/` importing `rules/`, `features.py` importing `RuleHit`, anything importing `benchmark/` from `prompthound/`, anything importing `classifier/train.py` outside `benchmark/run_benchmark.py`)

**Exit criteria:** clean `pytest` + `ruff` run; forbidden-import check passes; this is the state the project should be in before writing the evaluation report.

---

## Phase 12 — Evaluation Report & Documentation

- [ ] Write the formal evaluation report per concept.md §4: precision/recall/F1 on the main corpus, false-positive rate on `benign_unusual` reported explicitly and prominently, honest comparison against publicly reported academic benchmarks (e.g. SkillFortify-style near-perfect precision on curated sets) without claiming parity
- [ ] Write/finalize `README.md`: problem statement (concept.md §1), install + usage (AGENTS.md §2–3), architecture summary (one diagram from architecture.md §1), evaluation results, explicitly-out-of-scope future work (concept.md §6)
- [ ] Review `AGENTS.md` for accuracy against what was actually built (update any stage details that changed during implementation)
- [ ] Prepare submission materials for the national-level competition (demo script, key differentiators from concept.md §5, sample scan outputs across all three formats)

**Exit criteria:** a fresh clone + `pip install -e ".[dev]"` + `prompthound scan` on a sample file reproduces the README's example output, and the evaluation report stands on its own as the "honest reference point" concept.md §4 calls for.

---

## Notes on sequencing

- Phases 2–5 (Parse, Rules, Features, Chains) can have their *fixture-writing* work done somewhat in parallel by different people, but Rules/Features/Chains all depend on Parse being finalized first — don't start them against a moving `ParsedSkill` shape.
- Phase 6 (corpus construction) can start as soon as Phase 2 is stable, in parallel with Phases 3–5, since building the corpus doesn't require rules/features/chains to exist yet — it only needs to *parse* cleanly. The sanity-pass step at the end of Phase 6 does need Phase 4 finished, though.
- Phases 7 and 8 are strictly sequential (can't promote a model that hasn't been benchmarked) and strictly depend on Phases 2–6 being complete and stable, since retraining after a schema/feature change wastes the run.
- Phase 9 (Reporter) can be scaffolded early against mocked `ScanResult` fixtures, but its final version depends on Phase 8's `RiskScore.decision_path` shape being real, not mocked.
- Phase 10 (CLI) is the integration point and should be last before the test/QA pass — it's the first place all stages run together for real.
