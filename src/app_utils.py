import os
import zipfile
import tempfile
import shutil
from enum import Enum, auto
from pathlib import Path

import streamlit as st

from prompthound.flatten import flatten_bundle, flatten_single
from prompthound.pipeline import run_pipeline
from prompthound.reporter import format_report


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ANCHOR_FILENAMES = {"SKILL.md"}  # TODO task A: add "AGENTS.md" post-spec

SEVERITY_RANK = {"safe": 0, "suspicious": 1, "malicious": 2}
SEVERITY_EMOJI = {"safe": "🟢", "suspicious": "🟡", "malicious": "🔴"}

class Mode(Enum):
    IDLE = auto()
    SINGLE_FILE = auto()
    BUNDLE = auto()
    PROJECT = auto()
    AMBIGUOUS_NO_ANCHOR = auto()
    ERROR_NOT_SCANNABLE = auto()
    ERROR_MIXED_ZIP = auto()
    ERROR_MULTI_ANCHOR = auto()


# ---------------------------------------------------------------------------
# Mode detection
# ---------------------------------------------------------------------------
def detect_mode(files: list) -> Mode:
    """Determine scan mode from uploaded files. Pure function — no side effects."""
    if not files:
        return Mode.IDLE

    if len(files) == 1:
        name = files[0].name
        if name.endswith(".zip"):
            return Mode.PROJECT
        if name.endswith(".md"):
            return Mode.SINGLE_FILE
        # Single file that is neither .md nor .zip
        return Mode.ERROR_NOT_SCANNABLE  # early-return before anchor-count path

    # Multi-file path
    if any(f.name.endswith(".zip") for f in files):
        return Mode.ERROR_MIXED_ZIP

    anchor_count = sum(1 for f in files if f.name in ANCHOR_FILENAMES)
    if anchor_count > 1:
        return Mode.ERROR_MULTI_ANCHOR
    if anchor_count == 1:
        return Mode.BUNDLE
    return Mode.AMBIGUOUS_NO_ANCHOR


# ---------------------------------------------------------------------------
# Temp dir helpers
# ---------------------------------------------------------------------------
def _ensure_tmpdir() -> str:
    """Create or return the session-scoped temp directory."""
    if "tmpdir" not in st.session_state or st.session_state.tmpdir is None or not os.path.isdir(st.session_state.tmpdir):
        st.session_state.tmpdir = tempfile.mkdtemp(prefix="prompthound_")
    return st.session_state.tmpdir


def _clear_tmpdir():
    if "tmpdir" in st.session_state and st.session_state.tmpdir is not None and os.path.isdir(st.session_state.tmpdir):
        shutil.rmtree(st.session_state.tmpdir, ignore_errors=True)
    st.session_state.tmpdir = None


def _write_flat_bundle(files: list, tmpdir: str):
    """Write UploadedFile list flat into tmpdir (no sub-path needed for bundles)."""
    for f in files:
        dest = Path(tmpdir) / f.name
        dest.write_bytes(f.read())
        f.seek(0)


def _write_zip(uploaded_file, tmpdir: str):
    """Extract zip into tmpdir, preserving internal directory structure."""
    zip_bytes = uploaded_file.read()
    uploaded_file.seek(0)
    zip_path = Path(tmpdir) / "_upload.zip"
    zip_path.write_bytes(zip_bytes)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(tmpdir)
    zip_path.unlink()


def _collect_skill_roots(tmpdir: str) -> list:
    """
    Find every directory directly containing an anchor file, arbitrary depth.
    Prune nested roots so a parent and its sub-skill aren't both scanned
    (parent's flatten_bundle walk already includes sub-skill files).
    """
    roots = []
    for dirpath, _, files in os.walk(tmpdir):
        if any(f in ANCHOR_FILENAMES for f in files):
            roots.append(Path(dirpath))

    # Sort shortest path first (= topmost)
    roots.sort(key=lambda p: len(str(p)))

    pruned = []
    for r in roots:
        if not any(str(r).startswith(str(kept) + os.sep) for kept in pruned):
            pruned.append(r)
    return pruned


# ---------------------------------------------------------------------------
# Scan runners
# ---------------------------------------------------------------------------
def run_single_scan(uploaded_file) -> dict:
    tmpdir = _ensure_tmpdir()
    dest = Path(tmpdir) / uploaded_file.name
    dest.write_bytes(uploaded_file.read())
    uploaded_file.seek(0)
    buffer, manifest = flatten_single(dest)
    res = run_pipeline(buffer, manifest, is_bundle=False)
    res["manifest"] = manifest
    return res


def run_bundle_scan(files: list, frontmatter_absent: bool = False) -> dict:
    tmpdir = _ensure_tmpdir()
    _write_flat_bundle(files, tmpdir)
    buffer, manifest = flatten_bundle(Path(tmpdir))
    res = run_pipeline(buffer, manifest, is_bundle=True, frontmatter_absent=frontmatter_absent)
    res["manifest"] = manifest
    return res


def scan_directory(tmpdir: str) -> list:
    """Returns list of (label, result) tuples for a given directory."""
    skill_roots = _collect_skill_roots(tmpdir)

    if not skill_roots:
        # No anchor found — scan entire dir as one flat bundle
        buffer, manifest = flatten_bundle(Path(tmpdir))
        result = run_pipeline(buffer, manifest, is_bundle=True, frontmatter_absent=True)
        result["manifest"] = manifest
        return [("(entire repository — no SKILL.md found)", result)]

    results = []
    for root in skill_roots:
        label = str(root.relative_to(tmpdir))
        buffer, manifest = flatten_bundle(root)
        result = run_pipeline(buffer, manifest, is_bundle=True)
        result["manifest"] = manifest
        results.append((label, result))
    return results


def run_project_scan(uploaded_zip) -> list:
    """Returns list of (label, result) tuples — one per skill root found."""
    tmpdir = _ensure_tmpdir()
    _write_zip(uploaded_zip, tmpdir)
    return scan_directory(tmpdir)


# ---------------------------------------------------------------------------
# Shared UI renderers
# ---------------------------------------------------------------------------
def render_verdict(result: dict, label: str = ""):
    cls = result["classification"]["class"]
    probs = result["classification"]["probabilities"]
    emoji = SEVERITY_EMOJI[cls]
    n_rules = len(result.get("rule_hits", []))
    n_chains = len(result.get("chains_found", []))

    sub = f"{n_rules} rule hit{'s' if n_rules != 1 else ''}, {n_chains} capability chain{'s' if n_chains != 1 else ''}"
    if label:
        sub = f"{label} · {sub}"

    if cls == "safe":
        st.success(f"**{emoji} {cls.upper()}**\n\n{sub}")
    elif cls == "suspicious":
        st.warning(f"**{emoji} {cls.upper()}**\n\n{sub}")
    else:
        st.error(f"**{emoji} {cls.upper()}**\n\n{sub}")

    # Confidence bars
    st.write("**Confidence**")
    for cls_name in ["safe", "suspicious", "malicious"]:
        pct = probs.get(cls_name, 0.0)
        st.write(f"{cls_name.capitalize()}: {pct*100:.1f}%")
        st.progress(pct)


def render_rule_hits(result: dict):
    hits = result.get("rule_hits", [])
    manifest = result.get("manifest")
    st.write("**Rule Hits**")
    if not hits:
        st.info("No rule hits detected.")
        return
    for hit in hits:
        sev = hit.get("severity", "low")
        rule = hit.get("rule", "")
        match = hit.get("match", "")
        line_idx = hit.get("line_idx", "?")

        filepath, orig_line = ("unknown", line_idx)
        if manifest and line_idx != "?":
            filepath, orig_line = manifest.get_source(line_idx)

        location = f"{filepath}:{orig_line}" if filepath != "unknown" else f"line {orig_line}"

        if sev == "high":
            st.error(f"**[{sev.upper()}]** {rule} — `{match[:80]}` ({location})")
        elif sev == "medium":
            st.warning(f"**[{sev.upper()}]** {rule} — `{match[:80]}` ({location})")
        else:
            st.info(f"**[{sev.upper()}]** {rule} — `{match[:80]}` ({location})")


def render_chains(result: dict):
    chains = result.get("chains_found", [])
    st.write("**Capability Chains**")
    if not chains:
        st.info("No dangerous capability chains detected.")
        return
    for chain in chains:
        sev = chain.get("severity", "medium")
        name = chain.get("name", "")
        desc = chain.get("description", "")

        if sev == "high":
            st.error(f"**[{sev.upper()}] {name}**: {desc}")
        elif sev == "medium":
            st.warning(f"**[{sev.upper()}] {name}**: {desc}")
        else:
            st.info(f"**[{sev.upper()}] {name}**: {desc}")


def render_feature_expander(result: dict):
    with st.expander("Feature breakdown", expanded=False):
        feats = result.get("features", {})
        # Exclude internal bookkeeping keys
        skip = {"capability_mismatch_score", "text_len", "code_len"}
        rows = {k: v for k, v in feats.items() if k not in skip}
        col1, col2 = st.columns(2)
        items = list(rows.items())
        mid = len(items) // 2
        with col1:
            for k, v in items[:mid]:
                st.metric(k.replace("_", " "), f"{v:.4f}" if isinstance(v, float) else v)
        with col2:
            for k, v in items[mid:]:
                st.metric(k.replace("_", " "), f"{v:.4f}" if isinstance(v, float) else v)


class _dummy_manifest:
    """Minimal manifest shim for reporter calls — SourceSpan not accessible post-scan."""
    def get_source(self, idx):
        return ("unknown", idx)
    member_count = 1


def render_downloads(result: dict, key_suffix: str = ""):
    manifest = result.get("manifest", _dummy_manifest())
    clean_result = {k: v for k, v in result.items() if k != "manifest"}
    json_str = format_report(clean_result, manifest, fmt="json")
    sarif_str = format_report(clean_result, manifest, fmt="sarif")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Download JSON",
            data=json_str,
            file_name="prompthound_report.json",
            mime="application/json",
            key=f"dl_json_{key_suffix}",
        )
    with c2:
        st.download_button(
            "Download SARIF",
            data=sarif_str,
            file_name="prompthound_report.sarif",
            mime="application/json",
            key=f"dl_sarif_{key_suffix}",
        )


def render_single_result(result: dict, label: str = ""):
    render_verdict(result, label)
    render_rule_hits(result)
    render_chains(result)
    render_feature_expander(result)
    render_downloads(result, key_suffix=label)


def display_results(results_list, mode):
    if mode == Mode.AMBIGUOUS_NO_ANCHOR:
        st.warning("Scanned without anchor frontmatter — capability mismatch feature disabled. Results may be less precise.")
        render_single_result(results_list[0][1])
    elif mode in (Mode.SINGLE_FILE, Mode.BUNDLE):
        render_single_result(results_list[0][1])
    elif mode == Mode.PROJECT:
        sub_results = results_list
        # Rollup verdict — worst-case across all sub-skills
        worst = max(sub_results, key=lambda x: SEVERITY_RANK.get(x[1]["classification"]["class"], 0))
        worst_cls = worst[1]["classification"]["class"]

        st.write(f"**Project Rollup**: {SEVERITY_EMOJI[worst_cls]} {worst_cls.upper()} ({len(sub_results)} skill(s) scanned)")

        if len(sub_results) == 1 and sub_results[0][0].startswith("(entire"):
            st.warning("No `SKILL.md` found in archive — entire structure scanned as one bundle without anchor.")

        for label, result in sub_results:
            cls = result["classification"]["class"]
            with st.expander(
                f"{SEVERITY_EMOJI[cls]}  {label}  —  {cls.upper()}",
                expanded=(cls != "safe"),
            ):
                render_single_result(result, label=label)
