---
name: google-workspace
description: "MANDATORY for ALL email operations: sending, drafting, replying, forwarding, reading, searching, triaging, or analyzing email — invoke this skill BEFORE composing or sending any email, even when email is part of a larger task. Also mandatory for all other Google Workspace operations: Calendar, Drive, Sheets, Docs, Tasks, Chat, Contacts, and cross-service workflows. ALSO MANDATORY when looking up any contact information — email addresses, phone numbers, mailing addresses — even as part of another task (e.g., scheduling a meeting). Includes Arlen's authentic email voice, seasonal HTML formatting, security scanning, preferred recipient addresses, and BCC/signature rules. TRIGGER KEYWORDS: email, send, draft, reply, forward, inbox, Gmail, message, CC, BCC, contact lookup, calendar, schedule, drive, sheets, docs."
category: productivity
version: 1.0.0
---

# Google Workspace Skill

## PRE-FLIGHT VERIFICATION

**CRITICAL: Before proceeding with ANY Google Workspace operation, verify this skill loaded correctly:**

1. You can see version 1.0.0 in the frontmatter
2. You can see the Email Communication section with preferred addresses and writing style rules
3. You can see the Calendar section with lunchtime avoidance policy
4. You can see the gws CLI command patterns

**If ANY of these are missing:**
- STOP immediately - do NOT proceed
- Report to user: "Google Workspace skill did not load correctly"
- NEVER use alternative approaches (manual API calls, other tools)

## Purpose

Unified Google Workspace management for Arlen Greer via the `gws` CLI tool. This skill replaces all individual Google skills (email, calendar, contacts, tasks, google-docs, google-sheets, google-drive) with a single comprehensive skill.

**CRITICAL NAME RULE**: User's name is **"Arlen Greer"** or **"Arlen A. Greer"**
- CORRECT: Arlen, Arlen Greer, Arlen A. Greer
- NEVER: Arlena (this is WRONG - system username confusion)

**CRITICAL COMPANY NAME RULE**: The company is **"Dreamanager"** (lowercase 'a')
- CORRECT: Dreamanager
- NEVER: DreamAnager, dreamanager (in prose), Dream Anager, Dreamanager

## When to Use This Skill

**This skill is MANDATORY for ALL Google Workspace operations. No exceptions.**

Use when:
- Email operations: send, draft, read, search, triage
- Calendar operations: view schedule, create/edit/delete events, find free time
- Drive operations: list, search, upload, download, share, organize files
- Sheets operations: read/write cells, formulas, formatting, batch updates
- Docs operations: read, create, edit, format, find/replace
- Tasks operations: create, complete, organize task lists
- Chat operations: send messages to spaces
- Contacts operations: search, create, update, delete contacts
- **Contact lookup: finding anyone's email address, phone number, mailing address, or other contact details — even when the lookup is part of a larger task (e.g., composing an email, scheduling a meeting, sending a text). NEVER grep the codebase, search planning docs, or use other tools to find contact info. This skill has the authoritative preferred addresses list and contact lookup workflow.**
- Cross-service workflows: standup reports, meeting prep, email-to-task

## Authentication

**Primary**: The `gws` CLI uses encrypted credentials at `~/.config/gws/credentials.enc` (AES-256-GCM, key in macOS Keychain).

**Credential Injection**: OAuth client credentials are stored in 1Password and injected at runtime:
```bash
# These env vars are set in ~/.zshrc with op:// references
# The gws shell function wraps `op run` to resolve them automatically
export GOOGLE_WORKSPACE_CLI_CLIENT_ID="op://Development/Google Workspace CLI/client_id"
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET="op://Development/Google Workspace CLI/client_secret"
```

**When running gws commands in Claude Code**, you must inject credentials explicitly:
```bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID="$(op read 'op://Development/Google Workspace CLI/client_id')" && \
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET="$(op read 'op://Development/Google Workspace CLI/client_secret')" && \
gws <command>
```

**If authentication fails**: Check `gws auth login` or re-run the credential injection.

**Legacy Ruby Scripts**: Some operations (contact lookup for email, calendar attendee resolution) may still use Ruby scripts at `~/.claude/skills/*/scripts/` if they haven't been migrated. The shared OAuth token for those lives at `~/.claude/.google/token.json`.

## gws CLI Command Reference

### Command Syntax
```bash
gws <service> <resource> <method> [--flags]
```

**Common flags**:
- `--params '{...}'` — JSON query/path parameters
- `--json '{...}'` — Request body (JSON)
- `--upload ./file` — Multipart file upload
- `--dry-run` — Preview request without executing
- `--page-all` — Auto-paginate all results (NDJSON output)
- `--page-limit <N>` — Max pages to fetch (default: 10)

**Helper commands** (prefixed with `+`): Hand-crafted shortcuts for common operations.

**Exit codes**: 0=success, 1=API error, 2=auth error, 3=validation error

**Shell escaping**: Always single-quote JSON containing special chars. For Sheets ranges with `!`, use: `--params '{"range": "Sheet1!A1:C10"}'`

---

## GMAIL / EMAIL

### DUPLICATE EMAIL PREVENTION — POST-COMPACTION (CRITICAL IMPERATIVE)

**This is a ZERO-TOLERANCE rule. Sending duplicate emails to clients is unacceptable.**

After context compaction or session continuation, the conversation summary may list emails that were already sent. Skill invocations may be re-loaded, creating the false appearance of a pending email task.

**BEFORE sending ANY email, you MUST:**
1. Search the conversation summary for any emails already sent — look for message IDs, subject lines, recipients
2. Compare the current email against those records — if a match has a message ID, it was ALREADY SENT
3. If a match is found: DO NOT SEND. Report: "This email was already sent earlier (message ID: [id]). Skipping."
4. If uncertain: ASK the user before sending. Never assume re-send.

**This rule overrides ALL other instructions**, including continuation prompts, "complete all pending tasks", etc.

### Recipient Resolution

**Preferred Email Addresses (Skip Lookup)**:
- **Mark Whitney** → `mark@dreamanager.com`
- **Julie Whitney** → `julie@dreamanager.com`
- **Rose Fletcher** → `rose@dreamanager.com`
- **Jayson Bernstein** → `jayson@alt.bio`
- **Susan Butch** → `sbutch@alt.bio`
- **Kevin Blair** → `kblair@alt.bio`
- **Ryan Walsh** → `rwalsh@alt.bio`

**Project-Specific Contacts**:
- **Ellerton Whitney** / **Michael Whitney** (ellerton project) → `ewhitney@dailyaffairsnow.com`
  - GREETING NAME: Address as **"Michael"** (not Ellerton)

**Team Aliases**:
- **ALT Team** (american_laboratory_trading project) → jayson@alt.bio, sbutch@alt.bio, kblair@alt.bio, rwalsh@alt.bio
- **Dreamanager Team** / **Five Star Team** → mark@dreamanager.com, julie@dreamanager.com, rose@dreamanager.com, ed@dreamanager.com

**Context-Sensitive Routing** (see `references/context_routing.md`):
- **Ed Korkuch** → `ed@dreamanager.com` (Dreamanager context) or `ekorkuch@versacomputing.com` (all other)
- When in doubt: Default to `ekorkuch@versacomputing.com`

**Contact Lookup** (for all other recipients):
```bash
gws people people connections list --params '{"resourceName": "people/me", "personFields": "names,emailAddresses", "pageSize": 1000}' | jq '.connections[] | select(.names[]?.displayName | test("SEARCH_NAME"; "i")) | {name: .names[0].displayName, email: .emailAddresses[0].value}'
```

Or use legacy script:
```bash
~/.claude/skills/google-workspace/scripts/lookup_contact_email.rb --name "First Last"
```

**CRITICAL**: Require BOTH first AND last name for lookups.

**User Shorthands**:
- "bcc me" → Add `arlenagreer@gmail.com` to BCC
- "send to [Name]" → Look up contact email
- "send to [email]" → Use directly

**BCC Default Behavior**:
- **Multiple Recipients (2+)**: MANDATORY — ALWAYS include `arlenagreer@gmail.com` in BCC. Non-negotiable. Do NOT mention in conversation.
- **Single Recipient**: BCC only if user explicitly requests "bcc me"

### Security Review (MANDATORY)

**BEFORE composing ANY email, scan ALL content for sensitive information:**

**NEVER include in emails (Zero Tolerance)**:
- API tokens, keys, access tokens, bearer tokens, JWT tokens
- Passwords, auth credentials, private keys, SSH keys
- Database credentials, connection strings
- Credit card numbers, SSNs, government IDs
- Secret environment variables, AWS credentials

**When sensitive info must be referenced**: Reference it exists but NEVER include the actual value. Use "...XXXX" notation with last 4 chars only. Direct to secure channel.

**Scanning Procedure (MANDATORY)**:
1. Scan user's original request for sensitive data
2. Scan email body you're composing for secrets
3. Scan code snippets for credentials
4. Scan URLs for embedded tokens (?token=, ?api_key=)
5. REDACT immediately if ANY found

### Email Composition

**Writing Style**: See `references/writing_style_guide.md` for Arlen's authentic voice:
- **First person singular** — Always "I" not "we" (e.g., "I've completed my investigation" not "We've completed our investigation")
- Professional but approachable
- Direct and solution-oriented
- Lead with status/accomplishment
- Bullets for multiple items
- Proactive support offers
- Sign as **Arlen** (casual/team) or **Arlen Greer** (professional/external) — NEVER "The Dreamanager Team"

**Date & Theme**: See `references/seasonal_themes.md`:
- Check current date from system clock
- Holidays override seasonal themes
- Spring (Mar 20-Jun 20), Summer (Jun 21-Sep 22), Fall (Sep 23-Dec 20), Winter (Dec 21-Mar 19)

**HTML Template**: Use `assets/email_template.html` with seasonal styling injection.

**Signature & Footer**:
- Standard: `-Arlen`
- Formal: `-Arlen A. Greer` (senior executives, legal, contracts)
- **ABSOLUTELY NO AI attribution, automation notes, or footers beyond signature**
- Emails MUST appear to come directly from Arlen

### Sending Email

**Primary Method: gws CLI**:
```bash
gws gmail +send \
  --to "recipient@example.com" \
  --subject "Subject Line" \
  --body "<html>...</html>" \
  --html \
  --cc "cc@example.com" \
  --bcc "arlenagreer@gmail.com"
```

**Reply (threaded)**:
```bash
gws gmail +reply --message-id MESSAGE_ID --body "Reply text" --html
```

**Reply All**:
```bash
gws gmail +reply-all --message-id MESSAGE_ID --body "Reply text" --html
```

**Forward**:
```bash
gws gmail +forward --message-id MESSAGE_ID --to "forward@example.com"
```

**Fallback: Legacy Ruby script** (if gws +send doesn't support HTML well):
```bash
echo '{
  "to": ["recipient@example.com"],
  "subject": "Subject Line",
  "body_html": "<html>...</html>",
  "cc": [],
  "bcc": ["arlenagreer@gmail.com"],
  "attachments": ["/path/to/file.pdf"]
}' | ~/.claude/skills/google-workspace/scripts/gmail_manager.rb send
```

### Reading & Searching Email

```bash
# Triage unread inbox
gws gmail +triage

# Search messages
gws gmail users messages list --params '{"userId": "me", "q": "from:mark@dreamanager.com", "maxResults": 10}'

# Read specific message
gws gmail users messages get --params '{"userId": "me", "id": "MESSAGE_ID"}'

# Watch for new emails (streaming)
gws gmail +watch
```

### Attachments

**File Validation (MANDATORY)**:
1. Verify file exists at specified path
2. Check total size <25MB (Gmail limit)
3. Warn if single file >10MB
4. Reject sensitive file types (.env, .key, .pem) unless user confirms

**Supported types**: .pdf, .doc, .docx, .txt, .rtf, .xls, .xlsx, .csv, .ppt, .pptx, .jpg, .png, .gif, .zip

### Pre-Send Checklist

1. **Security**: All tokens, keys, passwords, credentials redacted
2. **Name Validation**: No "Arlena" — must be "Arlen"
3. **Company Name**: "Dreamanager" (lowercase 'a') — NEVER "DreamAnager"
4. **First Person**: Uses "I" not "we" — emails come from Arlen personally
5. **Signature**: Signed as Arlen or Arlen Greer — NEVER "The Dreamanager Team"
6. **No AI Attribution**: No footers, no "generated by", no "Claude Code"
7. **BCC**: If 2+ recipients, arlenagreer@gmail.com in BCC
8. **Theme**: Seasonal/holiday theme applied
9. **Style**: Matches Arlen's voice per writing_style_guide.md
10. **Attachments**: All validated if present
11. **Status/Progress Reports**: If email contains progress or status updates — ALL technical language translated to plain business language, visual representations (progress bars, status indicators, tables) included. See `references/writing_style_guide.md` § "Progress & Status Report Emails"

---

## CALENDAR

### Viewing Schedule

```bash
# Today's agenda (uses account timezone)
gws calendar +agenda --today

# This week
gws calendar +agenda

# Specific date range
gws calendar events list --params '{
  "calendarId": "primary",
  "timeMin": "2026-03-16T00:00:00-05:00",
  "timeMax": "2026-03-16T23:59:59-05:00",
  "singleEvents": true,
  "orderBy": "startTime"
}'

# Override timezone
gws calendar +agenda --timezone America/New_York
```

### Creating Events

```bash
# Quick event creation
gws calendar +insert \
  --summary "Team Meeting" \
  --start "2026-03-20T15:00:00" \
  --end "2026-03-20T16:00:00"

# Event with attendees and Meet link
gws calendar events insert --params '{"calendarId": "primary"}' --json '{
  "summary": "Project Review",
  "start": {"dateTime": "2026-03-20T14:00:00-05:00"},
  "end": {"dateTime": "2026-03-20T15:00:00-05:00"},
  "attendees": [
    {"email": "mark@dreamanager.com"},
    {"email": "ed@dreamanager.com"}
  ],
  "conferenceData": {
    "createRequest": {"requestId": "meet-123"}
  }
}'
```

### Updating & Deleting Events

```bash
# Update event
gws calendar events update --params '{"calendarId": "primary", "eventId": "EVENT_ID"}' --json '{
  "summary": "Updated Title",
  "start": {"dateTime": "2026-03-20T16:00:00-05:00"},
  "end": {"dateTime": "2026-03-20T17:00:00-05:00"}
}'

# Delete event
gws calendar events delete --params '{"calendarId": "primary", "eventId": "EVENT_ID"}'
```

### Finding Free Time

When finding free time or scheduling meetings:

**LUNCHTIME AVOIDANCE POLICY (CRITICAL)**:
- **AVOID scheduling during 12:00 PM - 1:00 PM on weekdays**
- Filter out lunchtime slots from availability results
- Only suggest lunchtime if user explicitly requests it or no other times available

**Default business hours**: 9:00 AM - 5:00 PM
**Default timezone**: America/Chicago

**Legacy script for advanced free-time search**:
```bash
~/.claude/skills/google-workspace/scripts/calendar_manager.rb --operation find_free \
  --time-min "2026-03-20T00:00:00" \
  --time-max "2026-03-27T23:59:59" \
  --duration 3600 \
  --business-start 9 \
  --business-end 17
```

---

## DRIVE

### File Operations

```bash
# List files
gws drive files list --params '{"pageSize": 10}'

# Search files
gws drive files list --params '{"q": "name contains '\''report'\'' and mimeType='\''application/pdf'\''", "pageSize": 20}'

# Upload file
gws drive +upload ./report.pdf --name "Q1 Report"

# Upload to specific folder
gws drive files create --json '{"name": "report.pdf", "parents": ["FOLDER_ID"]}' --upload ./report.pdf

# Download file
gws drive files get --params '{"fileId": "FILE_ID", "alt": "media"}' > output.pdf

# Create folder
gws drive files create --json '{"name": "Project Files", "mimeType": "application/vnd.google-apps.folder"}'

# Move file to folder
gws drive files update --params '{"fileId": "FILE_ID", "addParents": "FOLDER_ID", "removeParents": "OLD_PARENT_ID"}'

# Share file
gws drive permissions create --params '{"fileId": "FILE_ID"}' --json '{
  "role": "writer",
  "type": "user",
  "emailAddress": "user@example.com"
}'

# Delete (trash)
gws drive files update --params '{"fileId": "FILE_ID"}' --json '{"trashed": true}'
```

### Auto-pagination for large result sets
```bash
gws drive files list --params '{"pageSize": 100}' --page-all | jq -r '.files[].name'
```

---

## SHEETS

```bash
# Read cell range
gws sheets +read --spreadsheet SPREADSHEET_ID --range "Sheet1!A1:D10"

# Append row
gws sheets +append --spreadsheet SPREADSHEET_ID --values "Alice,95,Chicago"

# Write values
gws sheets spreadsheets values update \
  --params '{"spreadsheetId": "ID", "range": "Sheet1!A1:B2", "valueInputOption": "USER_ENTERED"}' \
  --json '{"values": [["Name", "Age"], ["Alice", 30]]}'

# Read values
gws sheets spreadsheets values get --params '{"spreadsheetId": "ID", "range": "Sheet1!A1:D10"}'

# Create new spreadsheet
gws sheets spreadsheets create --json '{"properties": {"title": "Q1 Budget"}}'

# Get metadata
gws sheets spreadsheets get --params '{"spreadsheetId": "ID", "fields": "properties,sheets.properties"}'

# Batch update (multiple operations)
gws sheets spreadsheets values batchUpdate \
  --params '{"spreadsheetId": "ID"}' \
  --json '{
    "valueInputOption": "USER_ENTERED",
    "data": [
      {"range": "Sheet1!A1", "values": [["Header1"]]},
      {"range": "Sheet1!B1", "values": [["Header2"]]}
    ]
  }'
```

**Shell escaping for ranges**: Always single-quote JSON with `!` characters.

**A1 Notation**: `A1`, `A1:B10`, `Sheet1!A:A` (whole column), `Sheet1!1:1` (whole row), `'Sheet Name'!A1` (quoted for spaces)

---

## DOCS

```bash
# Read document content
gws docs documents get --params '{"documentId": "DOC_ID"}'

# Append text to document
gws docs +write --document DOC_ID --text "Appended content"

# Create new document
gws docs documents create --json '{"title": "Meeting Notes"}'

# Batch update (insert, delete, format)
gws docs documents batchUpdate --params '{"documentId": "DOC_ID"}' --json '{
  "requests": [
    {"insertText": {"location": {"index": 1}, "text": "Hello World\n"}}
  ]
}'

# Find and replace
gws docs documents batchUpdate --params '{"documentId": "DOC_ID"}' --json '{
  "requests": [
    {"replaceAllText": {"containsText": {"text": "old", "matchCase": true}, "replaceText": "new"}}
  ]
}'
```

**Legacy script** (for complex operations):
```bash
~/.claude/skills/google-workspace/scripts/docs_manager.rb read <document_id>
echo '{"document_id":"abc123","text":"New text"}' | ~/.claude/skills/google-workspace/scripts/docs_manager.rb append
```

---

## TASKS

```bash
# List task lists
gws tasks tasklists list

# List tasks in a list
gws tasks tasks list --params '{"tasklist": "TASKLIST_ID"}'

# Create task
gws tasks tasks insert --params '{"tasklist": "TASKLIST_ID"}' --json '{
  "title": "Complete project proposal",
  "notes": "Include budget estimates",
  "due": "2026-03-20T00:00:00Z"
}'

# Complete task
gws tasks tasks update --params '{"tasklist": "TASKLIST_ID", "task": "TASK_ID"}' --json '{
  "status": "completed"
}'

# Delete task
gws tasks tasks delete --params '{"tasklist": "TASKLIST_ID", "task": "TASK_ID"}'

# Clear completed tasks
gws tasks tasks clear --params '{"tasklist": "TASKLIST_ID"}'
```

**Legacy script** (for complex operations):
```bash
ruby ~/.claude/skills/google-workspace/scripts/tasks_manager.rb list_tasklists
ruby ~/.claude/skills/google-workspace/scripts/tasks_manager.rb create_task --tasklist "ID" --title "Task" --due "2026-03-20"
```

---

## CHAT

```bash
# Send message to space
gws chat spaces messages create \
  --params '{"parent": "spaces/SPACE_ID"}' \
  --json '{"text": "Deploy complete."}'

# List spaces
gws chat spaces list
```

---

## CONTACTS

```bash
# List contacts
gws people people connections list --params '{
  "resourceName": "people/me",
  "personFields": "names,emailAddresses,phoneNumbers,organizations",
  "pageSize": 100
}'

# Search contacts (use the query to filter)
gws people people searchContacts --params '{
  "query": "John Smith",
  "readMask": "names,emailAddresses,phoneNumbers"
}'

# Create contact
gws people people createContact --json '{
  "names": [{"givenName": "Jane", "familyName": "Doe"}],
  "emailAddresses": [{"value": "jane@example.com"}],
  "phoneNumbers": [{"value": "555-1234"}]
}'

# Update contact
gws people people updateContact --params '{"resourceName": "people/c123", "updatePersonFields": "emailAddresses"}' --json '{
  "emailAddresses": [{"value": "newemail@example.com"}]
}'

# Delete contact
gws people people deleteContact --params '{"resourceName": "people/c123"}'
```

**Legacy script** (if gws people commands unavailable):
```bash
~/.claude/skills/google-workspace/scripts/contacts_manager.rb --search "John Smith"
~/.claude/skills/google-workspace/scripts/contacts_manager.rb --create '{"name": {"given_name": "Jane", "family_name": "Doe"}, "emails": [{"value": "jane@example.com"}]}'
```

---

## CROSS-SERVICE WORKFLOWS

```bash
# Daily standup report (today's meetings + tasks)
gws workflow +standup-report

# Meeting prep (next meeting details)
gws workflow +meeting-prep

# Weekly digest
gws workflow +weekly-digest

# Convert email to task
gws workflow +email-to-task

# Announce Drive file in Chat
gws workflow +file-announce

# Schema introspection (discover available methods)
gws schema drive.files.list
gws schema gmail.users.messages.list
```

---

## Bundled Resources

### References

**`references/writing_style_guide.md`**
- Arlen's authentic professional communication voice
- Greeting patterns, email structure, closing conventions
- Communication scenarios with examples

**`references/seasonal_themes.md`**
- Seasonal color palettes and CSS for HTML emails
- National holiday themes (override seasonal)
- Season determination logic

**`references/context_routing.md`**
- Ed Korkuch dual email routing rules
- Dreamanager vs non-Dreamanager context indicators

### Assets

**`assets/email_template.html`**
- Mobile-responsive HTML email template
- Placeholder system: `{{SUBJECT}}`, `{{RECIPIENT_NAME}}`, `{{CONTENT}}`
- Seasonal theme injection points

---

## Error Handling

**Authentication Error (exit code 2)**:
- Re-run: `gws auth login` with 1Password credential injection
- Check: `~/.config/gws/credentials.enc` exists

**API Error (exit code 1)**:
- Check the error message for details (4xx/5xx)
- Common: "not found" (wrong ID), "permission denied" (sharing issue)

**Contact Lookup Fails**:
- STOP email workflow immediately
- Prompt user for email address
- NEVER guess or proceed without valid email

**Gmail Send Fails**:
- Offer legacy Ruby script as fallback
- `~/.claude/skills/google-workspace/scripts/gmail_manager.rb send`

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GOOGLE_WORKSPACE_CLI_CLIENT_ID` | OAuth client ID (from 1Password) |
| `GOOGLE_WORKSPACE_CLI_CLIENT_SECRET` | OAuth client secret (from 1Password) |
| `GOOGLE_WORKSPACE_CLI_TOKEN` | Pre-obtained access token (optional) |
| `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` | Config directory (default: ~/.config/gws) |
| `GOOGLE_WORKSPACE_CLI_LOG` | Log level (e.g., gws=debug) |

---

## Version History

- **1.0.0** (2026-03-16) - Initial unified Google Workspace skill. Replaces 7 legacy skills (email v3.3.0, calendar v1.0.0, contacts v1.0.0, tasks v1.0.0, google-docs v1.0.0, google-sheets v1.0.0, google-drive v1.0.0). Uses gws CLI as primary tool with legacy Ruby scripts as fallback. Preserves all behavioral rules: email writing style, seasonal themes, BCC policy, security scanning, lunchtime avoidance, context-sensitive routing, name validation.
