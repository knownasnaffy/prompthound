# Configuration for PromptHound

# Known directories where AI agent skills are typically stored.
# Used by the CLI's -p/--project flag and the pre-commit git hook
# to automatically discover and scan skills without manual path inputs.
KNOWN_SKILL_DIRS = [".agents/skills", ".kiro/skills", ".gemini/skills", "skills"]
