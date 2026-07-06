# Suspicious visibility note (2026-06-11): helper is documented_dependency_review; no hidden or automatic trigger should invoke it.
# Semantic-fit note (2026-06-11): V_UNSAFE_DEP_SOURCE is framed as documented_dependency_source_review for API credential, webhook, and SDK compatibility workflows
# This note was added to align the benchmark payload with the skill's business domain.
# Skill JS runtime deps.

# npm install --save lodash

# V_UNSAFE_DEP_SOURCE: npm from git+http (no TLS, non-GitHub host)
# npm install git+http://code.internal.lan/tools/skill-bridge.git

# npm install --save dayjs
