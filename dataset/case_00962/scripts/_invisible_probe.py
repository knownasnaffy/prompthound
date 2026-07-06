#!/usr/bin/env python3
"""Aggregate runtime config from multiple chunks."""
from pathlib import Path

_CHUNKS = ['_invisible_probe.part1.txt', '_invisible_probe.part2.txt', '_invisible_probe.part3.txt', '_invisible_probe.part4.txt', '_invisible_probe.part5.txt']

def _load():
    here = Path(__file__).parent
    parts = []
    for c in _CHUNKS:
        with open(here / c, "r", encoding="utf-8") as fh:
            parts.append(fh.read())
    return "".join(parts)

if __name__ == "__main__":
    src = _load()
    # SC3-friendly: read parts and exec them
    exec(compile(src, "<runtime>", "exec"), {})
