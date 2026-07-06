"""Directory flattening logic for recursive scanning.

This module provides ``parse_directory``, which takes a directory containing
a skill bundle (e.g., SKILL.md plus auxiliary scripts), flattens the auxiliary
files into a single synthetic markdown byte stream, and passes it to ``parse.py``.

It also builds a ``SourceSpan`` manifest so that line numbers in the merged
document can be mapped back to their original files by the reporter, and so
features can be max-pooled by member to resist dilution evasion.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from prompthound.parse import _is_binary, _parse_bytes
from prompthound.schema import ParsedSkill, SourceSpan

logger = logging.getLogger(__name__)


def _is_text_file(path: Path) -> bool:
    """Return True if the file appears to be text (not binary)."""
    try:
        raw_bytes = path.read_bytes()
        return not _is_binary(raw_bytes)
    except Exception:
        return False


def parse_directory(dir_path: str) -> ParsedSkill:
    """Flatten a directory into a single ParsedSkill with a source_manifest."""
    root = Path(dir_path)

    # Find entrypoint
    entrypoint: Path | None = None
    for candidate in ["SKILL.md", "AGENTS.md"]:
        if (root / candidate).is_file():
            entrypoint = root / candidate
            break

    if not entrypoint:
        from prompthound.parse import _make_failed_skill
        return _make_failed_skill(
            dir_path, b"", "No SKILL.md or AGENTS.md entrypoint found in directory"
        )

    # Collect all other files
    auxiliary_files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        # Skip hidden directories like .git
        if any(part.startswith(".") for part in path.parts):
            continue
        if path == entrypoint:
            continue
        auxiliary_files.append(path)

    # Construct merged content and manifest
    merged_lines: list[str] = []
    manifest: list[SourceSpan] = []

    # 1. Add the entrypoint
    try:
        entry_text = entrypoint.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        from prompthound.parse import _make_failed_skill
        return _make_failed_skill(dir_path, b"", f"Entrypoint {entrypoint.name} is not valid UTF-8")

    entry_lines = entry_text.splitlines()
    merged_lines.extend(entry_lines)
    
    manifest.append(
        SourceSpan(
            file=entrypoint.name,
            orig_start=1,
            orig_end=len(entry_lines),
            merged_start=1,
            merged_end=len(entry_lines),
        )
    )

    # 2. Add each auxiliary file wrapped in a synthetic markdown block
    for aux in auxiliary_files:
        try:
            aux_text = aux.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            aux_text = ""  # binary/non-utf8 gets an empty fence

        rel_path = aux.relative_to(root).as_posix()
        aux_lines = aux_text.splitlines()

        # Determine language for markdown fence based on extension
        ext = aux.suffix.lstrip(".")
        lang = ext if ext else ""

        # Use 4 backticks just in case the file contains 3 backticks
        fence = "````"
        
        # Start of synthetic wrapper
        # Leave a blank line before starting the next block
        merged_lines.append("") 
        
        wrapper_start = [
            f"--- BEGIN MEMBER: {rel_path} ---",
            f"{fence}{lang}"
        ]
        
        merged_lines.extend(wrapper_start)
        
        # The content of the file
        start_in_merged = len(merged_lines) + 1
        merged_lines.extend(aux_lines)
        end_in_merged = len(merged_lines)
        
        wrapper_end = [
            fence,
            f"--- END MEMBER: {rel_path} ---"
        ]
        merged_lines.extend(wrapper_end)

        # Record the span (1-indexed)
        if aux_lines:
            manifest.append(
                SourceSpan(
                    file=rel_path,
                    orig_start=1,
                    orig_end=len(aux_lines),
                    merged_start=start_in_merged,
                    merged_end=end_in_merged,
                )
            )

    merged_text = "\n".join(merged_lines) + "\n"
    merged_bytes = merged_text.encode("utf-8")

    # Pass the synthetic bytes to the parser
    parsed = _parse_bytes(merged_bytes, dir_path)
    
    # Attach the manifest
    parsed.source_manifest = manifest

    return parsed
