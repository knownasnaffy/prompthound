# AGENTS.md — PromptHound

This file is for AI coding agents (and future-you) working in this repo. It
covers setup, the commands you'll run constantly, and the project conventions
that aren't obvious from reading one file in isolation. Full design context
lives in `concept.md`, `prompthound-architecture-flow.md`, and
`prompthound-tech-implementation.md` — read those before making structural
changes, not just this file.

---

## 1. Project in one paragraph

PromptHound is a CLI (`prompthound scan <file>`) that statically analyzes AI
agent skill files (`SKILL.md`, `AGENTS.md`-style capability packages) for risk
signals: shell pipe patterns, encoded blobs, Unicode Tag steganography,
capability mismatches, and dangerous capability chains. Philosophy is "sniffer,
not shield" — it scores and explains, it never blocks. Python 3.11+, `click`
CLI, `scikit-learn` classifier, SARIF/JSON output for CI.

## 2. Setup

```bash
# create and activate a virtualenv (use whatever venv tool you like; venv shown here)
test -d .venv || python3.11 -m venv .venv
source .venv/bin/activate

# install package in editable mode + dev extras
pip install -e ".[dev]"

# optional: LightGBM candidate for the benchmark harness (not required to run the CLI)
pip install -e ".[lgbm]"

# sanity check the CLI is wired up
prompthound --help
```

There is no database, no external service, and no network call anywhere in the
`scan` path — if `prompthound scan` ever seems to need network access, that's
a bug, not a missing credential. (The benchmark harness is also fully offline;
the corpus is committed under `benchmark/corpus/`.)

The shipped classifier artifact (`prompthound/classifier/artifact/model.joblib`
+ `metadata.json`) is committed to the repo. You do not need to run the
benchmark or train anything to use or develop against the CLI — only touch the
benchmark harness when you're deliberately changing model selection (see §6).

## 3. Commands you'll use constantly

```bash
# run the CLI against a file
prompthound scan path/to/SKILL.md
prompthound scan path/to/SKILL.md --format json
prompthound scan path/to/SKILL.md --format sarif
prompthound scan path/to/SKILL.md --fail-on suspicious # nonzero exit code for CI use

# run the full test suite
pytest

# run just one stage's unit tests (fast inner loop when editing e.g. rules)
pytest tests/unit/test_rules.py -v
pytest tests/unit/test_features.py -v

# run integration tests (full scan() over fixture corpus, snapshot-checked)
pytest tests/integration -v

# re-run a snapshot update after an intentional Reporter output change
pytest tests/integration --snapshot-update

# lint / format (adjust to whatever's configured in pyproject.toml)
ruff check .
ruff format .

# re-run the model benchmark (slow — only when corpus or models.yaml changes)
python benchmark/run_benchmark.py --models decision_tree,random_forest,gradient_boosting --folds 5
python benchmark/promote.py --top # or --run-id <id> to promote a specific run
```

If you add a new rule, feature, or model candidate, there should be
a corresponding test or benchmark row before it's considered done — see §7.

## 4. Repo map (quick reference)

```
prompthound/
├── cli.py            # click entry point — thin, no business logic
├── parse.py          # Stage 1: raw file → ParsedSkill
├── rules/            # Stage 2a: stateless heuristic rules (side-channel)
├── features.py       # Stage 2b: ParsedSkill → FeatureVector
├── classifier/        # Stage 3: FeatureVector → RiskScore (+ decision path)
├── chains.py          # Stage 4: capability declared-vs-referenced + sequence detection
├── report.py          # Stage 5: merges everything, renders human/json/sarif
└── schema.py           # shared dataclasses used across every stage boundary
benchmark/             # model selection harness — see §6, separate from the shipped package
tests/                 # unit (per-stage, golden-file) + integration (full scan, snapshot)
```

Full stage-by-stage responsibilities are in
`prompthound-tech-implementation.md` §4 — don't re-derive them from scratch,
that doc is the source of truth.

## 5. Conventions that matter (read before editing)

- **Rules are independent and stateless.** Every function in `rules/` has the
  signature `(ParsedSkill) -> list[RuleHit]` and is registered in
  `rules/__init__.py::ALL_RULES`. A rule must never import or depend on another
  rule, and must never see another rule's output. This is enforced
  structurally, not just by convention — don't add a shared mutable context
  object to "coordinate" rules.
- **Feature extraction never sees rule hits.** `features.py` takes only
  `ParsedSkill`. If you're tempted to pass `RuleHit[]` into a feature function
  because "the rule already found this," that's a sign the feature and the rule
  are redundant — flag it in the PR instead of wiring them together, since
  keeping the two evidence axes independent is a deliberate design choice (see
  architecture doc §1, §2.3).
- **The classifier module never trains at runtime.** `classifier/model.py` only
  loads the committed `.joblib` artifact and predicts. All training code lives
  in `classifier/train.py` and is only ever invoked from `benchmark/`. If
  `scan` is doing anything that takes more than a fraction of a second,
  something has leaked from the wrong place.
- **The capability-chain check reads `ParsedSkill` directly, not
  `FeatureVector`.** It needs line-level spans for its explanations, which the
  numeric feature vector doesn't carry.
- **Reporter must keep evidence types visibly separate.** Rule hits, classifier
  score + decision path, and chain flags are three different kinds of evidence
  and must not be flattened into one undifferentiated list in any output
  format. This is covered by an integration snapshot test — if you change
  `report.py` and a snapshot test fails, don't just update the snapshot without
  checking you haven't merged the sections.
- **No stage writes to disk, and `scan` makes no network calls.** The whole
  point is that it's safe to run against an untrusted file straight from
  a marketplace. Don't add caching-to-disk, telemetry, or "check for updates"
  behavior to the `scan` path without discussing it first — it breaks a stated
  safety property, not just a style guideline.
- **Malformed input short-circuits at Parse.** If `ParsedSkill.parse_ok` is
  `False`, every later stage should be skipped, and the Reporter should render
  a "could not parse" result — never let a partial/garbage `ParsedSkill` flow
  downstream and produce a misleadingly low score.
- **`benchmark/` is not part of the shipped package.** It has its own corpus,
  its own YAML-driven model search space, and its own promote step. Don't
  import from `benchmark/` in `prompthound/`, and don't import from
  `prompthound/classifier/train.py` anywhere except
  `benchmark/run_benchmark.py`.

## 6. Working with the benchmark harness

Only touch this when deliberately changing model selection, adding a feature
that should affect training, or growing the labeled corpus.

- Model candidates and their hyperparameter grids live in
  `benchmark/models.yaml` — add a new candidate by adding a YAML entry with
  a fully-qualified `estimator` import path, not by writing a new branch of
  Python.
- `benchmark/corpus/benign_unusual/` is the false-positive probe set. It is
  **eval-only** — never let it leak into the training split. If you add files
  here, they must be genuinely benign skills that legitimately use things like
  base64 or shell commands, not just more ordinary benign examples.
- `run_benchmark.py` writes every (model, hyperparameter) run to
  `benchmark/results/comparison.csv`/`.md`. Don't hand-edit those files
  — they're regenerated.
- The tie-breaker in `models.yaml` prefers shallower/simpler models when F1 is
  close — this is intentional (interpretability is a first-class requirement,
  not an afterthought) and shouldn't be "fixed" to just chase the highest F1.
- `promote.py` is the only thing allowed to overwrite
  `prompthound/classifier/artifact/model.joblib`. It also writes
  `metadata.json` recording which run produced it — never hand-copy a model
  file in without updating that metadata, or the shipped classifier's
  provenance becomes untraceable.

## 7. Definition of done for common change types

- **New rule**: add function to `rules/`, register in `ALL_RULES`, add
  a golden-file unit test with at least one triggering and one non-triggering
  fixture.
- **New feature**: add to `features.py`, update the canonical column order, add
  a unit test, and — if it's meant to actually move the classifier's behavior
  — add a note in the next benchmark run rather than assuming it helps.
- **New rule/feature that affects output text**: check whether it also needs
  a corresponding SARIF/JSON field, and update the integration snapshot tests
  deliberately (not via blind `--snapshot-update`).
- **New model candidate**: add to `models.yaml`, run `run_benchmark.py`, check
  `comparison.md` before promoting — don't promote a model that wasn't the
  actual top (or explicitly justified tie-break) row.
- **Any change touching `parse.py`**: re-run the malformed-input tests
  specifically; this stage is the one place a bug can silently produce
  a misleadingly low risk score downstream.

## 8. Explicitly out of scope (don't build unprompted)

Per `concept.md` §6, these are deliberately deferred past the course
deliverable. The pipeline is shaped so they'd attach at a boundary later
(`prompthound-architecture-flow.md` §5), but don't start implementing them
without being asked:

- MCP server integration
- Editor/agent plugins (Claude Code, Codex, OpenCode, etc.)
- CI/git hook integrations (beyond the exit-code contract `--fail-on` already
  provides)
- Capability sandboxing / enforcement
- Registry-scale crawling
