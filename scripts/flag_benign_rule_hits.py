#!/usr/bin/env python3
import json
import shutil
from pathlib import Path
from prompthound.flatten import parse_directory
from prompthound.parse import parse_skill
from prompthound.rules import ALL_RULES

ROOT = Path(__file__).resolve().parent.parent
benign_dir = ROOT / "benchmark" / "corpus" / "benign"
pending_dir = ROOT / "benchmark" / "corpus" / "benign_pending_review"
report_path = ROOT / "scripts" / "benign_rule_hits_report.txt"

pending_dir.mkdir(parents=True, exist_ok=True)

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
        hit_ids = list(set([h.rule_id for h in hits]))
        flagged.append((p, hit_ids))

with open(report_path, "w", encoding="utf-8") as f:
    f.write("BENIGN FILES FLAGGED BY RULES (Pending Human Review)\n")
    f.write("=" * 60 + "\n\n")
    
    for path, hits in flagged:
        f.write(f"File/Bundle: {path.name}\n")
        f.write(f"Rule Hits: {', '.join(hits)}\n")
        f.write("-" * 40 + "\n")
        
        # Move the file out of benign
        dest = pending_dir / path.name
        shutil.move(str(path), str(dest))

print(f"Flagged and moved {len(flagged)} files. Report saved to {report_path.name}")
