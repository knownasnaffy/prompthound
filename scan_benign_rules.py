from pathlib import Path
from prompthound.flatten import parse_directory
from prompthound.parse import parse_skill
from prompthound.rules import ALL_RULES

benign_dir = Path("benchmark/corpus/benign")
flagged = []

for p in benign_dir.iterdir():
    if p.is_dir():
        parsed = parse_directory(str(p))
    else:
        parsed = parse_skill(str(p))
        
    if not parsed.parse_ok:
        continue
        
    hits = []
    for rule in ALL_RULES:
        hits.extend(rule(parsed))
        
    if hits:
        flagged.append((p.name, [h.rule_id for h in hits]))
        
for f, hits in flagged:
    print(f"{f}: {hits}")
print(f"Total flagged: {len(flagged)}")
