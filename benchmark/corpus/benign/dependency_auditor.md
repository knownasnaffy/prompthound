---
name: dependency-auditor
description: >
  Reads a project's dependency manifest (requirements.txt, package.json,
  pyproject.toml, Cargo.toml) and reports: outdated packages, packages with
  known CVEs (via local advisory database), packages pinned to exact versions
  vs. open ranges, and packages with no reverse-dependency justification.
capabilities:
  - file_read
version: "2.1"
author: self-authored
license: MIT
---

# Dependency Auditor

Static analysis of a project's dependency manifest. The skill reads the
manifest file and produces a structured report covering security,
maintainability, and hygiene. All analysis is performed locally against a
bundled advisory database — no network calls are made at scan time.

## Report Sections

### 1. Outdated packages

Lists packages where a newer version is available in the bundled index,
noting whether the update is a patch, minor, or major bump.

### 2. Known vulnerabilities

Cross-references each dependency against the bundled CVE advisory database
(refreshed when the skill is updated). Each hit includes the CVE ID,
severity (CVSS score), affected version range, and recommended fix version.

### 3. Pin hygiene

| Status         | Meaning                                                     |
|----------------|-------------------------------------------------------------|
| Exact pin      | Version is frozen (`==1.2.3`) — good for reproducibility.  |
| Upper bound    | Version has a ceiling (`<2.0`) — may miss security patches. |
| Open range     | No upper bound (`>=1.0`) — accepts any future version.      |
| No constraint  | Not pinned at all — installs whatever is latest.            |

### 4. Unused dependencies

Flags packages listed in the manifest but not referenced in any import
statement found in the project's source tree.

## Usage

```
agent run dependency-auditor --manifest requirements.txt --source src/
```

Output:

```
[HIGH] requests 2.28.1 — CVE-2023-32681 (CVSS 6.1, fixed in 2.31.0)
[WARN] numpy==1.24.0 — version 1.26.4 available (minor update)
[INFO] boto3>=1.20 — open upper bound; accepts any 1.x release
[INFO] colorama — not imported in src/; may be unused
```

## Configuration

| Parameter          | Default | Description                                       |
|--------------------|---------|---------------------------------------------------|
| `manifest`         | auto    | Manifest file (auto-detected if not specified).   |
| `source`           | .       | Root directory for import scanning.               |
| `min_severity`     | info    | Minimum severity level to report.                 |
| `skip_unused`      | false   | Suppress unused-dependency warnings.              |

## Notes

- This skill is entirely offline. The advisory database is bundled and
  current as of the skill's release date. For real-time CVE lookups,
  use a separate network-enabled scanner.
- The unused-dependency check is heuristic: it looks for import statements
  matching package names. It may miss packages used via entry points or
  plugins with non-obvious import names.
