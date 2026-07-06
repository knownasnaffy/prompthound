# Recursive Directory Scanning (Completed)

This plan outlines the approach to recursively scan directories for PromptHound, utilizing a single synthetic buffer with a source manifest for provenance tracking.

## Completed Tasks

1. **Rebuild Corpus Structure**: 
    - Dropped existing corpus to utilize actual skill bundles (folders) instead of flattening out auxiliary files on import.
    - Preserved `import_corpus.py` logic to accurately build `benchmark/corpus/`.

2. **Schema Update (`schema.py`)**:
    - Added `SourceSpan` dataclass to implement the **Line Map** concept, representing the mapping between the synthetic merged buffer and original source files.
    - Added `source_manifest: list[SourceSpan] | None` to `ParsedSkill`.

3. **Directory Flattening (`flatten.py`)**:
    - Implemented `parse_directory()` to gather all files in a folder, wrap auxiliary files in artificial markdown fences (e.g., `--- BEGIN MEMBER: helper.py ---`), and yield a single byte stream.

4. **Parser Adjustment (`parse.py`)**:
    - Factored out core parsing from `parse_skill()` into `_parse_bytes()` to allow `flatten.py` to pipe in the merged bytes without hitting the disk again.

5. **Feature Vector Enhancements (`features.py`)**:
    - Max-pooled extraction applied using `source_manifest` to prevent signal dilution (e.g., `base64_hex_ratio`, `padding_ratio`).
    - Added two new features to `FEATURE_ORDER`: `member_count` and `is_bundle`.

6. **Rules Update (`rules/padding.py`)**:
    - Rule heuristics updated to utilize `source_manifest` max-pooling where appropriate, avoiding false positives driven by large chunks of code appended into a single stream.

7. **Reporter Updates (`report.py`)**:
    - Introduced `_translate_line()` to dynamically map the synthetic line numbers produced by SARIF and Human output back to their true file of origin.

8. **CLI Interface (`cli.py`)**:
    - Added `-d, --directory` flag to trigger `parse_directory()` instead of standard parsing.

9. **Benchmark & Evaluation**:
    - Updated `run_benchmark.py` and `promote.py` to evaluate the 11 features on the new corpus, reporting `holdout_f1_bundle` and `holdout_f1_single` slices in `comparison.md`.
    - Executed benchmark, selected `decision_tree__0002` (F1=0.806), and promoted artifact.

10. **Testing**:
    - Wrote unit tests for `flatten.py` and features logic.
    - Updated integration tests to accommodate new fixtures and features.
