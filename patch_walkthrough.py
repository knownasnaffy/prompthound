import re
from pathlib import Path

path = Path('/home/barinr/.gemini/antigravity/brain/daf8e9bc-e0b4-4d60-ac9a-71aec4c313e8/walkthrough.md')
text = path.read_text()

text = text.replace(
    '2. **Provenance Tracking**:\n    To maintain accurate reporting, we introduced `SourceSpan` and `source_manifest` to the `ParsedSkill` schema.',
    '2. **Provenance Tracking (The Line Map)**:\n    To maintain accurate reporting and realize the "Line Map" idea, we introduced `SourceSpan` and `source_manifest` to the `ParsedSkill` schema.'
)

path.write_text(text)
print("Done patching walkthrough.md")
