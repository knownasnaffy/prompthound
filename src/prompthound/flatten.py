import os
from pathlib import Path

from .limits import MAX_BUNDLE_SIZE, MAX_FILES


class SourceSpan:
    def __init__(self):
        # List of tuples: (start_line_in_buffer, end_line_in_buffer, filepath)
        self.ranges = []
        self.member_count = 0

    def add_range(self, start_line, end_line, filepath):
        self.ranges.append((start_line, end_line, filepath))

    def get_source(self, buffer_line):
        """Map a 0-indexed buffer line number to (filepath, original_line_0_indexed)"""
        for start, end, filepath in self.ranges:
            if start <= buffer_line < end:
                original_line = buffer_line - start
                return filepath, original_line
        # If it hits a synthetic fence line, it will return None, None
        return None, None


def read_file_safely(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        return None


def flatten_single(path):
    path_obj = Path(path)
    content = read_file_safely(path_obj)

    if content is None:
        content = ""

    manifest = SourceSpan()
    lines = content.split("\n")
    manifest.add_range(0, len(lines), str(path_obj))
    manifest.member_count = 1

    return content, manifest


def flatten_bundle(directory):
    directory_obj = Path(directory)
    buffer_lines = []
    manifest = SourceSpan()

    all_files = []
    for root, dirs, files in os.walk(directory_obj):
        if "benign_pending_review" in dirs:
            dirs.remove("benign_pending_review")
        for f in files:
            all_files.append(Path(root) / f)

    # Deterministic order by relative path
    all_files.sort(key=lambda p: str(p.relative_to(directory_obj)))

    if len(all_files) > MAX_FILES:
        print(f"Warning: Bundle exceeds max files ({MAX_FILES}), truncating.")
        all_files = all_files[:MAX_FILES]

    current_line = 0
    total_size = 0

    for fpath in all_files:
        rel_path = str(fpath.relative_to(directory_obj))

        try:
            total_size += fpath.stat().st_size
        except OSError:
            pass

        if total_size > MAX_BUNDLE_SIZE:
            print(f"Warning: Bundle size exceeds limit, truncating at {rel_path}.")
            break

        fence_start = f"--- BEGIN MEMBER: {rel_path} ---"
        fence_end = "--- END MEMBER ---"

        content = read_file_safely(fpath)

        buffer_lines.append(fence_start)

        start_line_idx = current_line + 1

        if content is not None:
            file_lines = content.split("\n")
            buffer_lines.extend(file_lines)
            end_line_idx = start_line_idx + len(file_lines)
        else:
            end_line_idx = start_line_idx

        buffer_lines.append(fence_end)

        manifest.add_range(start_line_idx, end_line_idx, rel_path)

        current_line = len(buffer_lines)

    manifest.member_count = len(manifest.ranges)

    return "\n".join(buffer_lines), manifest
