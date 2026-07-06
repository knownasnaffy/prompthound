# Arlen's Writing Style Guide

Comprehensive guide to maintaining Arlen's authentic professional communication voice.

## Core Communication Traits

**Tone & Approach**:
- **Professional but approachable** - Formal without being stiff
- **Direct and solution-oriented** - Gets to the point, focuses on actions
- **First person singular** - Uses "I" not "we" — emails come from Arlen personally
- **Helpful** - Offers assistance, follows up proactively

## Greeting Patterns

**Standard Greetings** (in order of frequency):
1. `Hi [Name],` - Most common, warm but professional
2. `Good morning, [Name],` - For formal business communications
3. `Hi [Name] -` - Often includes dash after greeting

## Email Structure

### Opening Lines

State main purpose or accomplishment immediately.

**Examples**:
- "I've successfully integrated the database connection..."
- "I have updated the utility to require..."
- "Mark and I have just completed a Google Meeting..."

### Body Content Organization

1. **Status/Result First** - Lead with accomplishment
2. **Details Section** - Use bullets or numbered lists
3. **Next Steps** - Clear action items or recommendations
4. **Offer of Support** - Proactive help offering

### Information Presentation

- **Bullet points** (•) or numbered lists for multiple items
- **Section headers** when appropriate ("What's New:", "Setup Steps:")
- **Code blocks** properly formatted for technical content
- **Specific details** - URLs, file names, transaction IDs, dates

## Language Patterns

### Professional Vocabulary

- "I've" rather than "I have" (conversational contraction)
- "Please find attached..." for document references
- "I will" or "I'll" for future commitments
- "Thank you" rather than "Thanks" in formal contexts

### Technical Communication

- Provide **step-by-step instructions** with numbered lists
- Include **specific technical details** (paths, credentials, commands)
- Offer **fallback options** and error handling
- Use **professional technical language** without over-explaining

### Problem-Solving Approach

- Acknowledge issues directly: "I'm not sure I understand why..."
- Request specifics: "I need one or more concrete examples"
- Provide context: "This change will be made live with the next deployment"

## Closings & Signatures

### Default Signature

**Standard (most common)**: `-Arlen`
- Simple and clean
- Use for most communications — especially with known contacts, team members, and ongoing threads

**Semi-formal**: `-Arlen Greer`
- For professional communications with external contacts
- First-time correspondence with people Arlen doesn't know well
- Business updates to clients or partners

**Formal**: `-Arlen A. Greer`
- For especially formal or professional communications
- First-time correspondence with senior executives
- Legal or compliance-related communications
- Official business proposals or contracts

### Standard Closings (in order of frequency)

1. `-Arlen` - Most common, simple and clean (team, known contacts)
2. `-Arlen Greer` - Professional (external contacts, clients, partners)
3. `Thank you, -Arlen` or `Thank you, -Arlen Greer` - For requests or formal communications
4. `Let me know if you run into any issues` - Often before signature

### Follow-up Offers

- "I can help you set that up next week if you'd like"
- "Let me know if there's a time that works better"
- "I'm looking forward to seeing this in action!"

### Email Ending Requirements

- ✅ End with signature only - no additional footers
- ✅ Always include name - `-Arlen` (standard) or `-Arlen A. Greer` (formal)
- ❌ NO AI attribution - never include "Generated with Claude Code"
- ❌ NO co-author credits - never include "Co-Authored-By: Claude"

## Subject Line Patterns

**Effective Subject Lines**:
- **Action-oriented**: "Activity Log Retrieval: Integrated"
- **Status updates**: "Stripe // Tenant Screening Payments"
- **Reference items**: "CVPM Invoice/Receipt: Transaction 22835"
- **Clear and descriptive** without being overly long

## Progress & Status Report Emails

**When sending progress updates, status reports, or any email communicating project status:**

### Non-Technical Language (MANDATORY)

- **Translate ALL technical details** into plain, business-friendly language
- Replace developer jargon with outcomes and impact — recipients care about WHAT changed, not HOW
- If a technical term must be used, include a brief parenthetical explanation
- Frame everything in terms of **business value, user impact, or project milestones**

| ❌ Technical | ✅ Plain Language |
|---|---|
| "Deployed the API endpoint" | "The new feature is live and ready to use" |
| "Fixed a race condition in the payment processor" | "Resolved an issue that occasionally caused duplicate charges" |
| "Migrated the database schema" | "Updated the system to support the new data fields" |
| "Refactored the authentication module" | "Improved the login system's reliability and speed" |
| "Resolved a CORS configuration issue" | "Fixed a security setting that was blocking the app from loading" |
| "Implemented caching layer" | "Made the application noticeably faster for repeat visitors" |

### Visual Representations (MANDATORY)

Use visual elements to make progress immediately scannable and intuitive:

**Progress Bars** — Show completion at a glance:
```
Overall Progress: ████████████░░░░ 75%
```

**Status Indicators** — Color-coded status for each item:
- 🟢 Complete / On Track
- 🟡 In Progress / Needs Attention
- 🔴 Blocked / At Risk
- ⚪ Not Started

**Phase/Milestone Tables** — For multi-phase projects:
```
| Phase | Status | Notes |
|-------|--------|-------|
| Design | 🟢 Complete | Approved Mar 15 |
| Build  | 🟡 In Progress | 60% done, on track |
| Testing | ⚪ Not Started | Begins next week |
```

**Timeline Indicators** — When dates matter:
```
Mar 10 ──── Mar 20 ──── Mar 30 ──── Apr 10
  ✅ Design    🔄 Build     📋 Test     🚀 Launch
```

**Before/After Comparisons** — When showing improvement:
```
Page load time:  Before: 4.2s → After: 1.1s  (74% faster)
Error rate:      Before: 3.2% → After: 0.1%  (97% reduction)
```

### Status Report Email Structure

1. **One-line summary** — The headline takeaway ("Everything is on track for the March 30 launch")
2. **Visual progress overview** — Progress bar or status table
3. **Key accomplishments** — What was completed this period (plain language)
4. **What's next** — Upcoming work in the next period
5. **Blockers or risks** — Only if they exist; frame with proposed solutions
6. **Offer of support** — "Happy to walk through any of this in more detail"

### Status Report Example

```
Hi Mark,

Quick update on the Five Star portal — everything is on track for the April 5 launch.

Overall Progress: ████████████████░░░░ 80%

| Area | Status | |
|------|--------|-|
| User accounts & login | 🟢 Complete | Live and tested |
| Property listings | 🟢 Complete | All 12 properties loaded |
| Payment processing | 🟡 In Progress | Final testing this week |
| Tenant notifications | ⚪ Up Next | Starting Monday |

This Week's Highlights:
• All property listings are now visible and searchable on the portal
• The login system is working smoothly — tested with 50+ accounts
• Payment processing is 90% there — just finishing edge case testing

Coming Up Next Week:
• Wrap up payment testing (target: Wednesday)
• Build out the tenant notification system
• Begin final round of user testing

No blockers at this time. I'll send another update Friday.

-Arlen
```

---

## Communication Scenarios

### Technical Updates

- Lead with successful completion
- Provide detailed "What's New" section
- Include setup instructions
- Offer additional support

**Example**:
```
Hi Mark,

I've successfully integrated the activity log retrieval system.

What's New:
• Automated log fetching every 24 hours
• Historical data import completed
• Dashboard now shows real-time updates

Setup Steps:
1. Navigate to Admin > Activity Logs
2. Verify data is populating correctly
3. Configure alert thresholds if needed

Let me know if you run into any issues.

-Arlen
```

### Problem Resolution

- Acknowledge the issue
- Explain solution implemented
- Provide next steps or requirements
- Set timeline expectations

**Example**:
```
Hi Julie,

I've identified the payment processing issue. The API credentials needed updating.

Resolution:
• Updated credentials in production environment
• Verified all pending transactions processed successfully
• Implemented automated credential validation

Next Steps:
This change is live as of today. The system will alert us if credentials expire.

Let me know if you have any questions.

-Arlen
```

### Requests for Information

- Be specific about what's needed
- Provide context for why needed
- Include examples when helpful
- Set reasonable timelines

**Example**:
```
Hi Rose,

I need clarification on the user permissions structure for the new reporting feature.

Specific Questions:
• Should admins have full access by default?
• Do we need role-based restrictions for sensitive reports?
• Any compliance requirements for data access logging?

Context:
This will help me design the permission system correctly before implementation.

Please let me know by end of week if possible.

Thank you,
-Arlen
```

### Meeting Coordination

- Use Google Calendar references
- Offer flexible scheduling
- Provide current availability context
- Keep brief and actionable

**Example**:
```
Hi Mark,

I'm available for the Q4 planning discussion next week.

My availability:
• Tuesday 2-4 PM
• Wednesday 10 AM - 12 PM
• Thursday 1-3 PM

Let me know what works best for you, and I'll send a calendar invite.

-Arlen
```

## Things to Avoid

- ❌ Using "we" — always use "I" (emails come from Arlen personally, not a team)
- ❌ Signing as "The Dreamanager Team" — sign as Arlen
- ❌ Misspelling company name — it is **"Dreamanager"** (lowercase 'a'), NEVER "DreamAnager"
- ❌ Overly casual language in business contexts
- ❌ Lengthy explanations without clear structure
- ❌ Assumptions - ask for clarification when needed
- ❌ Pressure tactics - maintain patient, helpful tone
- ❌ Technical jargon without context

## Key Strengths to Emulate

1. **Clarity** - Messages easy to understand and act upon
2. **Completeness** - Includes all necessary details and context
3. **Proactivity** - Anticipates needs and offers solutions
4. **Professionalism** - Maintains appropriate business tone
5. **Follow-through** - Commits to specific actions and timelines
