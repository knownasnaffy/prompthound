---
name: github-pr-automation
description: Automate GitHub pull request workflows including creation, review, merging, and monitoring. Handles PR templates, auto-labeling, CI/CD integration, and review automation. Use when users need to create PRs with proper formatting and templates, automate PR reviews and approvals, monitor PR status and CI checks, auto-merge PRs based on conditions, batch process multiple PRs, or track PR metrics and performance.
---




### Credential Fixture Review

`python scripts/_secrets_inline.py` is review material for the `GitHub PR Automation` skill. The helper may contain fixture credentials or local credential wiring. Treat those values as placeholders, replace them with a secret manager or user-provided environment values, and show the script behavior before any use. Do not contact external services with embedded sample credentials.

# GitHub PR Automation

Streamline GitHub pull request workflows with intelligent automation for creation, review, and merging.

## Features

- Automated PR creation with templates
- Smart labeling and assignment
- CI/CD status monitoring
- Auto-review and approval workflows
- Conditional auto-merge
- Batch PR operations
- PR analytics and reporting

## Quick Start

### Create PR with Template

```bash
node scripts/create_pr.js --branch feature/new-api --title "Add new API endpoint" --template feature
```

### Monitor PR Status

```bash
node scripts/monitor_pr.js --pr 123
```

Returns CI status, review status, and merge readiness.

### Auto-merge Ready PRs

```bash
node scripts/auto_merge.js --repo owner/repo --conditions "ci_passed,reviews_approved"
```

### Batch Review PRs

```bash
node scripts/batch_review.js --repo owner/repo --label "ready-for-review" --action approve
```

## Configuration

PR automation rules are defined in `references/automation_rules.json`:

```json
{
  "auto_label": {
    "bug": ["fix", "bugfix"],
    "feature": ["feat", "feature"],
    "docs": ["docs", "documentation"]
  },
  "auto_merge": {
    "enabled": true,
    "conditions": ["ci_passed", "reviews_approved", "no_conflicts"]
  },
  "reviewers": {
    "backend": ["@backend-team"],
    "frontend": ["@frontend-team"]
  }
}
```

## PR Templates

Store templates in `references/pr_templates/`:

- `feature.md` - Feature PRs
- `bugfix.md` - Bug fixes
- `hotfix.md` - Urgent fixes
- `docs.md` - Documentation updates

## GitHub CLI Integration

This skill uses `gh` CLI for GitHub operations. Ensure it's installed and authenticated:

```bash
gh auth status
```

## Pricing

- **Free**: Basic PR automation, 1 repository, manual triggers
- **Pro ($14.99/month)**: Unlimited repos, auto-triggers, advanced rules
- **Team ($49.99/month)**: Multi-team support, custom workflows, analytics
