# PromptHound — Architecture & Flow

**Purpose of this doc:** structure and data flow, not tech stack. The question
being answered is "what talks to what, and what does it pass along"
— implementation language, libraries, and file formats for internal state are
a separate decision.

---

## 1. Guiding shape

The whole tool is one **linear pipeline with a side-channel**. A skill file
goes in one end; a risk report comes out the other. Each stage in between does
one job, reads the output of the stage before it, and appends to a shared
result object rather than mutating what came before it.

The side-channel is the **rule layer**, which runs independently of the
feature/classifier path and merges back in at reporting time. This matters
structurally: rule hits and classifier scores are two different kinds of
evidence (deterministic-and-explainable vs. statistical-and-scored), and the
report has to keep them visibly separate rather than blending them into one
opaque number.

```
                    ┌───────────────┐
   SKILL.md  ──────▶│    PARSE      │
                    └───────┬───────┘
                            │  ParsedSkill
                ┌───────────┴────────────┐
                ▼                        ▼
        ┌───────────────┐        ┌───────────────┐
        │  RULE LAYER    │        │ FEATURE        │
        │  (heuristics)  │        │ EXTRACTION      │
        └───────┬────────┘        └───────┬─────────┘
                │ RuleHits[]              │ FeatureVector
                │                         ▼
                │                 ┌───────────────┐
                │                 │  CLASSIFIER    │
                │                 └───────┬─────────┘
                │                         │ RiskScore + SplitPath
                │                         │
                └───────────┬─────────────┘
                            ▼
                  ┌───────────────────┐
                  │ CAPABILITY-CHAIN   │◀── reads ParsedSkill directly
                  │ CHECK              │    (frontmatter vs body)
                  └─────────┬──────────┘
                            │ ChainFlags[]
                            ▼
                  ┌───────────────────┐
                  │   REPORTER         │
                  │ (merge + explain)  │
                  └─────────┬──────────┘
                            ▼
                 human report / --format sarif|json
```

Two things to notice about this shape:

- **Rule layer and feature/classifier path both start from the same
  `ParsedSkill`, independently.** Neither depends on the other's output. This
  is what lets the rule layer stay fast and deterministic even if the
  classifier stage is slow or someday swapped out.
- **Capability-chain check reads the parsed file directly, not the feature
  vector.** It's a structural comparison (declared vs. referenced capabilities,
  sequence detection), not a numeric signal — trying to force it through the
  feature vector would lose the "which two things were chained" detail the
  explanation needs.

## 2. Stage-by-stage flow

### 2.1 Parse **In:** raw file bytes. **Out:** a `ParsedSkill` object
— frontmatter fields (name, description, declared capabilities) separated from
body prose, separated again from code blocks (each tagged with its
language/fence type and position in the file).

This stage is the one place normalization happens: Unicode Tag characters are
*detected and preserved as their own field* here rather than silently stripped,
because their presence is itself a signal three later stages need (rule layer
flags them, feature extraction counts them, reporter has to show *where* they
were). Nothing downstream re-reads the raw file.

### 2.2 Rule layer **In:** `ParsedSkill`. **Out:** a list of `RuleHit`s, each
with: rule id, severity, the exact span of the file that triggered it, and
a one-line human explanation.

Each rule is independent and stateless — one rule firing never suppresses or
depends on another. This is deliberate: it keeps the rule layer trivially
explainable ("rule X fired because Y") and trivially extensible (adding rule
#13 can't break rules #1–12).

### 2.3 Feature extraction **In:** `ParsedSkill`. **Out:** `FeatureVector`
— the numeric encoding described in concept.md §3 (entropy, ratios, counts,
mismatch score, etc).

This stage deliberately does *not* know about rule hits. Keeping it blind to
the rule layer's output means the classifier's signal isn't just "reflecting
back" what the rules already caught — it's a genuinely separate axis of
evidence, which is the whole justification for having both layers instead of
one.

### 2.4 Classifier **In:** `FeatureVector`. **Out:** `RiskScore` (0–1 or
categorical) **plus the decision path** — which features and thresholds the
tree actually split on for this file.

The split path is not an afterthought — it's the main deliverable of this
stage. A bare score with no path would collapse the interpretability goal from
concept.md §2 back into a black box.

### 2.5 Capability-chain check **In:** `ParsedSkill` (frontmatter capabilities
+ body-referenced/executed capabilities). **Out:** `ChainFlags[]` — each one
naming the sequence detected (e.g. *file read → encode → network send*) and
which steps in the file correspond to which link in the chain.

Runs after parse, independent of rule layer and classifier, but is placed last
in the diagram because it's the stage most likely to reference *both*
frontmatter and scattered body locations at once, so it benefits from the file
having already been fully parsed and validated by the time it runs.

### 2.6 Reporter **In:** everything upstream — `RuleHit[]`, `RiskScore` + split
path, `ChainFlags[]`. **Out:** the final report, in human-readable form by
default, or `sarif`/`json` on request.

The reporter's only real job is **merge without flattening**: a developer
reading the report should be able to tell "the classifier thinks this is risky
because of entropy + URL count" apart from "rule #4 fired on a literal `curl
| bash`" apart from "capability chain: read→encode→send detected across lines
12, 34, 51." Collapsing these into a single undifferentiated list of warnings
would undo the traceability that's the whole point of choosing an interpretable
classifier in the first place.

## 3. CLI interaction flow

```bash
prompthound scan path/to/SKILL.md [--format sarif|json] [--fail-on
<threshold>]
```

1. Resolve path → confirm file exists and is markdown-like → hand off to Parse.
2. Run stages 2.1–2.5 as above.
3. Reporter renders output to stdout (human format) or to the requested
structured format.
4. Exit code reflects `--fail-on` threshold if set — this is the one piece of
"enforcement-adjacent" behavior in scope: PromptHound doesn't confine or block
anything itself, but it can hand a CI pipeline a pass/fail signal so *the
pipeline* can act on it. This stays consistent with the "sniffer, not shield"
philosophy — PromptHound reports, the calling process decides.

No stage writes anything to disk by default; the report is the only output
artifact, which keeps a `scan` invocation side-effect-free and safe to run
against untrusted files pulled straight from a marketplace.

## 4. Error handling flow (structural, not exhaustive)

- **Unparseable file** (no frontmatter, binary garbage, etc.) → Parse stage
  short-circuits straight to Reporter with a "could not parse" result rather
  than feeding a partial/garbage `ParsedSkill` into later stages. This avoids
  the failure mode where a malformed file produces a misleadingly low risk
  score just because feature extraction had nothing to measure.
- **Padding/size anomaly** detected during parse → flows into both the rule
  layer (as a rule hit) *and* the feature vector (as a feature) — this is one
  of the few pieces of information that legitimately feeds both paths, since
  "the file is padded to dodge scanners" is both a rule-shaped fact and
  a magnitude-shaped one (how much padding).
- **Empty or missing capability chain** (skill declares nothing / does nothing)
  → chain-check stage returns no flags, not an error; absence of a chain is
  a valid, common, benign outcome and shouldn't be surfaced as a warning.

## 5. Where future-work items would attach (not building now, but shaping the
seams)

Per concept.md §6, these are out of scope for the deliverable — but the
pipeline shape above is deliberately drawn so they'd attach at a stage boundary
rather than requiring a redesign:

- **MCP server integration** would sit as an alternate front door feeding the
  same `Parse` stage.
- **Editor/agent plugins** would call the same pipeline as a library, swapping
  only the Reporter's output target.
- **CI/git hooks** would wrap the CLI's exit code, not touch the pipeline
  internals.
- **Sandboxing/enforcement** would consume the Reporter's output as *input* to
  a separate enforcement process — deliberately kept a stage removed from
  detection, matching the "sniffer, not shield" split.
- **Registry-scale crawling** would run the same per-file pipeline in a loop,
  aggregating `RiskScore`s across many files — nothing about the single-file
  flow changes.

## 6. What's intentionally NOT decided here

- Data structures / serialization format for `ParsedSkill`, `FeatureVector`,
  etc.
- Which library implements the classifier.
- File layout of the codebase (modules/packages).
- Test corpus storage format.

Those are tech-spec decisions for the next pass, once this flow is agreed on.
