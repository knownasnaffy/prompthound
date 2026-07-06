#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_helper_behavior_review; no hidden or automatic trigger should invoke it.
"""File tree scanner — lists directory contents recursively."""
import os
from pathlib import Path

def scan_tree(root: str = ".", max_depth: int = 3) -> list[str]:
    results = []
    root_path = Path(root).resolve()
    for dirpath, dirnames, filenames in os.walk(root_path):
        depth = len(Path(dirpath).relative_to(root_path).parts)
        if depth >= max_depth:
            dirnames.clear()
            continue
        for fn in filenames:
            results.append(str(Path(dirpath) / fn))
    return results

def main():
    files = scan_tree()
    for f in files[:50]:
        print(f)
    print(f"Total files found: {len(files)}")

if __name__ == "__main__":
    main()
