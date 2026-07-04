---
name: api-schema-validator
description: >
  Validates an OpenAPI 3.x specification file against a set of team-defined
  rules: required field presence, naming conventions, response envelope
  consistency, pagination patterns, and error schema standardisation.
  Outputs a structured report of violations.
capabilities:
  - file_read
version: "1.0"
author: self-authored
license: MIT
---

# API Schema Validator

A skill for validating OpenAPI 3.x specification files beyond what the
standard JSON Schema validation provides. Enforces team-specific API design
conventions so that issues are caught before code generation or client
publication.

## Rules

### Required fields
- Every endpoint must have a `summary` and at least one `tag`.
- Every parameter must have a `description`.
- Every response body schema must have at least one required field.

### Naming conventions
- Path segments use `kebab-case` (e.g. `/user-profiles/{userId}`).
- Query parameters use `camelCase`.
- Schema property names use `camelCase`.
- Tags use `PascalCase`.

### Response envelopes
- Successful collection responses should include a `data` array and a
  `pagination` object.
- All error responses should use the standard error envelope:
  ```json
  { "error": { "code": "string", "message": "string" } }
  ```

### Versioning
- The `info.version` field must be present and follow semver.
- Breaking changes require a major version bump (detected by comparing
  against the previously committed spec, if provided).

## Usage

```
agent run api-schema-validator --spec openapi.yaml
```

Diff against a baseline:

```
agent run api-schema-validator --spec openapi.yaml --baseline openapi.v1.yaml
```

Sample output:

```
openapi.yaml: [ERROR] GET /users: missing 'summary'
openapi.yaml: [WARN] Schema 'UserProfile': property 'created_at' uses snake_case (expected camelCase)
openapi.yaml: [WARN] POST /orders: error response on status 422 does not use standard error envelope
```

## Configuration

| Parameter          | Default | Description                                                   |
|--------------------|---------|---------------------------------------------------------------|
| `spec`             | —       | Path to the OpenAPI YAML or JSON file.                        |
| `baseline`         | none    | Previous spec to diff against for breaking-change detection.  |
| `rules`            | all     | Comma-separated rule IDs to run.                              |
| `format`           | text    | Output format: text or json.                                  |

## Notes

- This skill is entirely static; it never makes HTTP requests.
- It validates structure and conventions, not semantic correctness. Use an
  integration test suite for actual API behaviour validation.
