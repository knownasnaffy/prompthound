# PromptHound — Tech Implementation

**Purpose of this doc:** the concept doc says *what* PromptHound does and
*why*; the architecture doc says *what talks to what*. This doc says what
actually gets built — language, libraries, module layout, data schemas, and
(the new piece) the benchmark harness used to pick and tune the classifier.
Anything already decided in the other two docs is referenced, not repeated.

---

## 1. Stack choice

**Language: Python 3.11+.**

Reasoning: the classifier work explicitly wants scikit-learn-style decision
trees / GBTs with inspectable split paths (concept.md §2, architecture.md
§2.4), the eval plan wants standard precision/recall/F1 tooling, and
a solo-developer CLI with a five-second startup budget doesn't need anything
more exotic. Python's markdown/YAML parsing ecosystem is also the path of least
resistance for stage 2.1.

| Concern                      | Choice                                              | Why                                                                                 |
|------------------------------|-----------------------------------------------------|-------------------------------------------------------------------------------------|
| CLI framework                | `click`                                             | Subcommands, `--format`/`--fail-on` flags map cleanly to option decorators          |
| Frontmatter/markdown parsing | `python-frontmatter` + `markdown-it-py`             | Frontmatter split is a solved problem; markdown-it gives a token stream for code-block extraction instead of regex-scraping |
| Unicode Tag detection        | stdlib (`unicodedata`, raw codepoint range checks)  | No library needed for a fixed codepoint range (U+E0000–U+E007F)                     |
| Classifier                   | `scikit-learn` (`DecisionTreeClassifier`, `GradientBoostingClassifier`, `RandomForestClassifier`) | Interpretable-by-construction, `.tree_` / `decision_path()` give the split path stage 2.4 requires for free |
| Optional stronger GBT        | `lightgbm` (behind an extra, not a hard dependency) | Only pulled in if the benchmark (§5) shows it's worth the extra dependency weight over sklearn's GBT |
| Model serialization          | `joblib`                                            | Standard for sklearn estimators, smaller/faster than pickle for numpy-heavy objects |
| Output formats               | stdlib `json`; hand-rolled SARIF dict (SARIF is just JSON with a schema) | No SARIF-writing library is worth adding for one schema        |
| Testing                      | `pytest`                                            | Default                                                                             |

No web framework, no database, no async — this is a single-shot CLI process
reading one file and writing to stdout, matching the "no stage writes to disk
by default" rule in architecture.md §3.

## 2. Repo layout

Maps 1:1 onto the pipeline stages in architecture.md §2 so the "seams"
described in architecture.md §5 stay real seams in the code, not just in the
diagram.

```
prompthound/
├── prompthound/
│   ├── cli.py                 # click entry point: scan command, flag parsing, exit codes
│   ├── parse.py                # 2.1 Parse → ParsedSkill
│   ├── rules/
│   │   ├── __init__.py         # rule registry (list of rule callables)
│   │   ├── shell_pipe.py       # curl|bash, wget|sh
│   │   ├── encoded_blob.py     # base64/hex blob detection
│   │   ├── unicode_tag.py      # steganography signal
│   │   ├── suspicious_domain.py
│   │   └── padding.py          # size/padding anomaly (also feeds features, see §4)
│   ├── features.py             # 2.3 Feature extraction → FeatureVector
│   ├── classifier/
│   │   ├── model.py            # load/predict, wraps joblib artifact
│   │   ├── train.py            # training entry point (used by benchmark harness)
│   │   └── artifact/           # committed .joblib model + metadata.json (version, metrics, features used)
│   ├── chains.py                # 2.5 Capability-chain check → ChainFlags
│   ├── report.py                # 2.6 Reporter — human/json/sarif renderers
│   └── schema.py                # shared dataclasses: ParsedSkill, RuleHit, FeatureVector, RiskScore, ChainFlag, ScanResult
├── benchmark/
│   ├── corpus/
│   │   ├── benign/              # real skill files, permissively licensed / self-authored
│   │   ├── malicious/           # reconstructed from takedown writeups (concept.md §4, §7)
│   │   ├── benign_unusual/      # legitimate skills using base64/shell for real reasons — FPR probe set
│   │   └── labels.csv           # filepath,label,source,notes
│   ├── models.yaml               # model + hyperparameter search space (§5.2)
│   ├── run_benchmark.py          # trains/scores every candidate, writes comparison report
│   ├── results/
│   │   ├── comparison.csv        # one row per (model, hyperparams) run
│   │   ├── comparison.md         # human-readable table, regenerated each run
│   │   └── selected_model.json   # which config was promoted to prompthound/classifier/artifact/
│   └── promote.py                # copies the winning run's artifact into the shipped package
├── tests/
│   ├── unit/                     # one test module per stage, golden-file based
│   └── integration/               # full scan() over a handful of corpus files, checked output snapshots
├── pyproject.toml
└── README.md
```

## 3. Shared data schemas (`schema.py`)

These are the objects that cross stage boundaries in architecture.md §1's
diagram. Defined once as dataclasses so every stage imports the same shape
instead of passing around dicts.

```python
@dataclass
class CodeBlock:
    language: str | None
    content: str
    start_line: int
    end_line: int

@dataclass
class ParsedSkill:
    path: str
    raw_bytes: bytes
    frontmatter: dict            # name, description, declared capabilities, etc.
    body_prose: str               # markdown body minus code fences
    code_blocks: list[CodeBlock]
    unicode_tag_spans: list[tuple[int, int]]   # detected-and-preserved, not stripped (architecture.md §2.1)
    parse_ok: bool
    parse_error: str | None       # set when short-circuiting to Reporter (architecture.md §4)

@dataclass
class RuleHit:
    rule_id: str
    severity: str                 # "info" | "warn" | "high"
    span: tuple[int, int]          # byte or line offsets into the file
    message: str                   # one-line human explanation

@dataclass
class FeatureVector:
    values: dict[str, float]       # keyed by feature name, matches concept.md §3 list
    order: list[str]               # canonical column order fed to the classifier

@dataclass
class RiskScore:
    score: float                   # 0-1
    label: str                     # benign | suspicious | malicious (thresholded)
    decision_path: list[dict]      # [{feature, threshold, direction, node_value}, ...]

@dataclass
class ChainFlag:
    chain_name: str                 # e.g. "read→encode→send"
    steps: list[tuple[str, int]]     # (capability, line_number) per link

@dataclass
class ScanResult:
    parsed: ParsedSkill
    rule_hits: list[RuleHit]
    features: FeatureVector | None
    risk: RiskScore | None
    chain_flags: list[ChainFlag]
```

`ScanResult` is the "shared result object" architecture.md §1 refers to — each
stage appends its piece; nothing mutates a prior stage's field. `report.py` is
the only module allowed to read all of it at once.

## 4. Stage implementation notes

Only calling out decisions not already settled by architecture.md.

- **Parse (`parse.py`)**: use `markdown-it-py`'s token stream to get code block
  spans with real line numbers rather than regex over the raw string — needed
  later so `RuleHit.span` and `ChainFlag.steps` can point at exact lines.
  Unicode Tag scan runs over `raw_bytes` before any decoding step, since the
  whole point is catching what a normal editor/preview wouldn't render.
- **Rule layer (`rules/`)**: each rule is a standalone function `(ParsedSkill)
  -> list[RuleHit]` registered in `rules/__init__.py`'s `ALL_RULES` list.
  `cli.py` runs `[hit for rule in ALL_RULES for hit in rule(parsed)]`
  — enforces the "each rule independent and stateless" requirement from
  architecture.md §2.2 at the type level, since a rule literally cannot see
  another rule's output.
- **Feature extraction (`features.py`)**: one function per feature in
  concept.md §3, all pure functions of `ParsedSkill` only — never given
  `RuleHit[]` as input, matching architecture.md §2.3's "deliberately blind to
  the rule layer" requirement. The padding/size anomaly value is computed once
  in a shared helper and consumed by both `rules/padding.py` and
  `features.py::padding_ratio`, per the dual-path note in architecture.md §4.
- **Classifier (`classifier/model.py`)**: at inference time this module does
  *not* train anything — it loads the committed `.joblib` artifact and calls
  `.predict_proba()` + `.decision_path()` (or LightGBM's equivalent leaf-path
  API). Training lives entirely in `classifier/train.py` and is only invoked by
  the benchmark harness, keeping `scan` fast and deterministic.
- **Capability-chain check (`chains.py`)**: implemented as a small fixed set of
  named sequences (declared as ordered lists of capability-tags, e.g.
  `["file_read", "encode", "network_send"]`) matched against
  a capability-tagged event list extracted from `ParsedSkill` (frontmatter
  declared caps + body-referenced caps, each tagged with source line). Matching
  is subsequence search, not exact-adjacency, since a chain can be split across
  non-adjacent lines.
- **Reporter (`report.py`)**: three renderers (`render_human`, `render_json`,
  `render_sarif`) all consuming the same `ScanResult`, each responsible for
  keeping the three evidence types visually distinct per architecture.md §2.6
  — this is a formatting constraint worth enforcing in a snapshot test (§6),
  not just a docstring.

## 5. Benchmark harness — model & hyperparameter selection

This is the piece concept.md and architecture.md describe the *goal* of ("a
tree's splits genuinely mean something") but don't specify how to get there.
The harness's job: given the labeled corpus, try several candidate model
families and hyperparameter settings, score them consistently, and produce an
artifact + a paper trail for why it was picked.

### 5.1 Corpus (`benchmark/corpus/`)

- `benign/` — real, unmodified SKILL.md-style files pulled from public repos or
  self-authored, license-checked.
- `malicious/` — reconstructed examples matching the incident patterns in
  concept.md §1 (credential-stealer setup blocks, Unicode Tag hidden
  instructions, padded files, chained read→encode→send).
- `benign_unusual/` — held out separately, never mixed into the main train/test
  split by default. This is the false-positive probe set concept.md §4 calls
  out as the metric "easy to skip." Legitimate skills that use base64 or shell
  commands for real reasons (e.g. a skill that legitimately curls an install
  script and says so).
- `labels.csv` — `filepath,label,source,notes` where `label ∈ {benign,
  malicious}` and `source` records provenance (self-authored vs.
  reconstructed-from-report vs. scraped) so the eval report can break results
  down by source and not just pretend the corpus is homogeneous.

### 5.2 Search space (`benchmark/models.yaml`)

```yaml
candidates:
  - name: decision_tree
    estimator: sklearn.tree.DecisionTreeClassifier
    grid:
      max_depth: [3, 5, 8, 12, null]
      min_samples_leaf: [1, 5, 10]
      criterion: [gini, entropy]

  - name: random_forest
    estimator: sklearn.ensemble.RandomForestClassifier
    grid:
      n_estimators: [50, 100, 300]
      max_depth: [5, 10, null]
      min_samples_leaf: [1, 5]

  - name: gradient_boosting
    estimator: sklearn.ensemble.GradientBoostingClassifier
    grid:
      n_estimators: [50, 100, 200]
      max_depth: [2, 3, 5]
      learning_rate: [0.01, 0.05, 0.1, 0.2]

  - name: lightgbm      # optional extra; skipped automatically if not installed
    estimator: lightgbm.LGBMClassifier
    grid:
      num_leaves: [15, 31, 63]
      max_depth: [3, 5, -1]
      learning_rate: [0.01, 0.05, 0.1]
      n_estimators: [50, 100, 200]

evaluation:
  split: stratified_kfold
  folds: 5
  test_holdout: 0.2
  fpr_probe_set: benign_unusual
  primary_metric: f1
  tie_breaker: interpretability_penalty   # prefers shallower trees / fewer estimators when F1 is within epsilon
```

`estimator` is a fully-qualified import path so `run_benchmark.py` can
`importlib`-load it generically instead of hardcoding a branch per model
— adding a candidate is a YAML edit, not a code change, which keeps this file
the single place model choice lives.

### 5.3 Run flow (`benchmark/run_benchmark.py`)

1. Load `labels.csv`, run every file through `parse.py` + `features.py` once
   (feature extraction is deterministic and model-independent, so it's cached
   and shared across all candidates rather than recomputed per grid point).
2. For each candidate in `models.yaml`: grid-search over its hyperparameter
   combinations using stratified k-fold on the `benign` + `malicious` split
   (`benign_unusual` stays out of training entirely — it's eval-only, so it
   can't leak into fitting).
3. For each (model, hyperparams) run, record: precision, recall, F1, ROC-AUC on
   the holdout; false positive rate specifically on `benign_unusual`; mean tree
   depth / node count (interpretability proxy); fit + predict wall-clock time.
4. Write every run as a row to `results/comparison.csv` and a rendered
   `results/comparison.md` table, sorted by `primary_metric` with the
   `tie_breaker` applied.
5. `promote.py` takes a run id (or defaults to the top row) and copies its
   fitted estimator into `prompthound/classifier/artifact/model.joblib`,
   alongside a `metadata.json` recording: model family, hyperparameters, corpus
   version/hash, metrics, and date — so the shipped classifier's provenance is
   always traceable back to a specific benchmark row, not just "whatever we
   last trained."

### 5.4 What "winning" means here

Per concept.md §2/§4, raw F1 is not sufficient on its own — a model that's
marginally better on F1 but produces deep, hard-to-summarize trees undercuts
the entire interpretability pitch. The `tie_breaker` in §5.2 encodes that
explicitly: within an epsilon of the top F1, prefer the shallower/simpler
model. This is also why `mean tree depth` and `node count` are recorded as
first-class benchmark outputs, not just debug info — they're part of the
deliverable's evaluation story (concept.md §4's "position results honestly").

### 5.5 Re-running the benchmark

Nothing about `run_benchmark.py` is meant to run in the hot path — it's
a developer/CI-maintainer command, invoked when the corpus grows or a new
candidate is worth trying:

```
python benchmark/run_benchmark.py --models decision_tree,gradient_boosting --folds 5
python benchmark/promote.py --run-id <id>   # or --top
```

## 6. Testing plan

- **Unit tests, one module per stage**, golden-file based: a handful of
  hand-crafted `SKILL.md` fixtures with known expected `RuleHit`s / feature
  values / chain flags, checked exactly. This catches regressions in individual
  rules or features without needing the full corpus.
- **Integration tests**: run `cli.scan()` end-to-end over a small fixed subset
  of `benchmark/corpus/` and snapshot the rendered human/json/sarif output.
  Catches Reporter regressions (e.g. accidentally flattening the three evidence
  types together, which architecture.md §2.6 explicitly warns against).
- **Corpus-level tests are not unit tests** — full-corpus precision/recall
  lives in the benchmark harness (§5), not in `pytest`, since it's slow and its
  "pass/fail" is a threshold judgment call, not a binary assertion.
- **Malformed-input tests**: binary garbage, no-frontmatter files, empty files
  — assert Parse short-circuits to Reporter per architecture.md §4 rather than
  raising or producing a misleadingly low score.

## 7. Dependencies (`pyproject.toml`, sketch)

```
click
python-frontmatter
markdown-it-py
scikit-learn
joblib
pyyaml            # models.yaml, labels round-tripping if needed
pytest            # dev
lightgbm          # optional extra: prompthound[lgbm]
```

Kept intentionally small — this is a CLI meant to run in ~5 seconds before
a `git clone`, so heavyweight or slow-importing dependencies work against the
pitch in concept.md §5.

## 8. Open implementation decisions (deferred, not blocking)

- Exact threshold(s) mapping `RiskScore.score` → `label`
  (benign/suspicious/malicious) — needs a first benchmark run to set sensibly
  rather than guessing.
- Whether `benign_unusual` FPR gets its own hard gate in `promote.py`
  (auto-reject any run above X% FPR) or stays advisory in the comparison table
  for a human to read.
- SARIF field mapping details (rule ids, help URIs) — schema-conformance pass
  once the human/json renderers are stable.
- Corpus size targets per split — concept.md §4 doesn't pin a number; likely
  revisited once initial rule/feature coverage is in and it's clear how many
  malicious examples per incident-pattern are needed for the grid search to be
  meaningful rather than noisy.
