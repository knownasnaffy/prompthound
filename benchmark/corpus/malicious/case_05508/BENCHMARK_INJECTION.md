# P0 Normal-Base Injection Fixture

Base normal sample: `case_03084`

Injected P0 pack: `SOURCE_ARTIFACT_MISMATCH`

This fixture preserves the original normal skill context and adds an
inert scanner benchmark injection. It is intended for static scanner
validation only.

Safety boundary:

- No real sensitive files or environment values are read.
- No cloud metadata endpoint is contacted.
- No native command chain is executed.
- No registry, package manager, model registry, or plugin registry
  configuration is modified.
- No hidden container member or bundled artifact is executed.
- No network request is sent.
