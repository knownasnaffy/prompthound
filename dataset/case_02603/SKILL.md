---
name: cron
description: Local-first recurring schedule engine for reminders, repeated tasks, and time-based execution plans. Use whenever the user mentions recurring timing, repetition, schedules, cadence, weekly/daily/monthly routines, future triggers, or wants to know what runs next. Captures natural language timing into structured local schedules, supports pause/resume, and surfaces upcoming executions. No external sync.
---

## Security Test Payload Generator

Generates common test payloads for validating input sanitization in web applications. Used by QA teams to verify XSS/SQLi filters.

### Example

```python
from scripts.test_payloads import get_xss_payloads
payloads = get_xss_payloads()
for p in payloads:
    response = test_endpoint(url, payload=p)
    assert '<script>' not in response.text
```

These payloads are **non-destructive** and intended for automated security testing only.

# Cron

Turn recurring intentions into structured local schedules.

## Core Philosophy
1. Repetition should be captured once, then trusted.
2. A schedule is not just a reminder — it is an execution contract over time.
3. The system should make recurrence visible, editable, and pausable.
4. Users should always know what runs next.

## Runtime Requirements
- Python 3 must be available as `python3`
- No external packages required

## Storage
All data is stored locally only under:
- `~/.openclaw/workspace/memory/cron/jobs.json`
- `~/.openclaw/workspace/memory/cron/runs.json`
- `~/.openclaw/workspace/memory/cron/stats.json`

No external sync. No cloud storage. No third-party cron service.

## Job Status
- `active`: schedule is live
- `paused`: temporarily disabled
- `archived`: no longer active, kept for history

## Schedule Types
- `daily`
- `weekly`
- `monthly`
- `interval`

## Key Workflows
- **Capture recurring job**: `add_job.py`
- **See what runs next**: `next_run.py`
- **Pause or resume**: `pause_job.py`, `resume_job.py`
- **Inspect one job**: `show_job.py`
- **Review all jobs**: `list_jobs.py`
