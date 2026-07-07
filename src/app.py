"""
PromptHound Web UI — Streamlit frontend for the scan pipeline.

Launch:
    streamlit run prompthound/app.py

Install deps:
    pip install -e ".[app]"

State machine (st.session_state.stage):
    IDLE → READY | AMBIGUOUS_NO_ANCHOR | ERROR_*
    READY → SCANNING → RESULTS
    AMBIGUOUS_NO_ANCHOR → (user picks radio) → READY
    ERROR_* → (user clears upload) → IDLE

Anchor set: {"SKILL.md"} only.
TODO (task A): Expand anchor set to include AGENTS.md once core-engine
    frontmatter-synthesis spec is written and reviewed. Until then, an
    AGENTS.md-anchored bundle uploaded flat will fall into AMBIGUOUS_NO_ANCHOR
    and the user must manually pick "Bundle (no anchor)" from the radio.
    This is a degraded-UX path, not a silent failure.
"""

import os
import sys
import zipfile
import tempfile
import shutil
from enum import Enum, auto
from pathlib import Path

import streamlit as st


from prompthound.flatten import flatten_bundle, flatten_single
from prompthound.pipeline import run_pipeline
from prompthound.reporter import format_report
from prompthound.limits import MAX_BUNDLE_SIZE, MAX_FILES

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


def run_project_scan(uploaded_zip) -> list:
    """Returns list of (label, result) tuples — one per skill root found."""
    tmpdir = _ensure_tmpdir()
    _write_zip(uploaded_zip, tmpdir)
    skill_roots = _collect_skill_roots(tmpdir)

    if not skill_roots:
        # No anchor found — scan entire zip as one flat bundle
        buffer, manifest = flatten_bundle(Path(tmpdir))
        result = run_pipeline(buffer, manifest, is_bundle=True, frontmatter_absent=True)
        result["manifest"] = manifest
        return [("(entire archive — no SKILL.md found)", result)]

    results = []
    for root in skill_roots:
        label = str(root.relative_to(tmpdir))
        buffer, manifest = flatten_bundle(root)
        result = run_pipeline(buffer, manifest, is_bundle=True)
        result["manifest"] = manifest
        results.append((label, result))
    return results

# ---------------------------------------------------------------------------
# UI helpers
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


class _dummy_manifest:
    """Minimal manifest shim for reporter calls — SourceSpan not accessible post-scan."""
    def get_source(self, idx):
        return ("unknown", idx)
    member_count = 1


def render_single_result(result: dict, label: str = ""):
    render_verdict(result, label)
    render_rule_hits(result)
    render_chains(result)
    render_feature_expander(result)
    render_downloads(result, key_suffix=label)


# ---------------------------------------------------------------------------
# Upload panel
# ---------------------------------------------------------------------------
def render_upload_panel():
    st.info("**How to upload**\n- **Single skill file** — select one `.md` file\n- **Skill bundle** — select `SKILL.md` and all supporting files together\n- **Full project** — zip your project root and upload the `.zip`")

    # --- Initialize dynamic uploader key ---
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    uploaded = st.file_uploader(
        "Drop files here or click to browse",
        accept_multiple_files=True,
        label_visibility="collapsed",
        key=f"uploader_{st.session_state.uploader_key}",
    )

    if not uploaded:
        st.session_state.mode = Mode.IDLE
        st.session_state.ambiguous_choice = None
        _clear_tmpdir()
        return

    mode = detect_mode(uploaded)
    st.session_state.mode = mode

    # --- Mode pill ---
    mode_labels = {
        Mode.SINGLE_FILE: "Single file",
        Mode.BUNDLE: "Skill bundle",
        Mode.PROJECT: "Project scan (.zip)",
        Mode.AMBIGUOUS_NO_ANCHOR: "Ambiguous — no anchor",
        Mode.ERROR_NOT_SCANNABLE: "Error",
        Mode.ERROR_MIXED_ZIP: "Error",
        Mode.ERROR_MULTI_ANCHOR: "Error",
    }
    st.write(f"**Mode**: {mode_labels.get(mode, '')}")

    # --- Binary file notice ---
    text_exts = {".md", ".txt", ".sh", ".py", ".js", ".ts", ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini", ".zip"}
    binary_files = [f.name for f in uploaded if not any(f.name.endswith(e) for e in text_exts)]
    if binary_files:
        st.warning(f"{len(binary_files)} binary file(s) will be treated as empty — matches CLI behaviour: {', '.join(binary_files[:5])}{'…' if len(binary_files) > 5 else ''}")

    # --- Limit warnings ---
    total_size = sum(f.size for f in uploaded)
    if total_size > MAX_BUNDLE_SIZE:
        st.warning(f"Total size {total_size // (1024*1024)} MB exceeds {MAX_BUNDLE_SIZE // (1024*1024)} MB limit — only first {MAX_BUNDLE_SIZE // (1024*1024)} MB will be analysed.")
    if len(uploaded) > MAX_FILES:
        st.warning(f"{len(uploaded)} files uploaded — exceeds {MAX_FILES} file limit. Only first {MAX_FILES} will be analysed.")

    # --- Error states ---
    if mode == Mode.ERROR_NOT_SCANNABLE:
        st.error("File is not scannable. Upload a `.md` skill file or a `.zip` project archive.")
        return

    if mode == Mode.ERROR_MIXED_ZIP:
        st.error("Cannot mix a `.zip` with other files. For project scans, upload only the `.zip`.")
        return

    if mode == Mode.ERROR_MULTI_ANCHOR:
        st.error("Multiple `SKILL.md` files found in a flat upload — cannot determine bundle boundaries. To scan multiple skills, zip the project root and upload it.")
        return

    # --- Ambiguous: no anchor ---
    if mode == Mode.AMBIGUOUS_NO_ANCHOR:
        st.warning("No `SKILL.md` found. How should these files be treated?")
        choice = st.radio(
            "Treat uploaded files as:",
            options=["Bundle (no anchor)", "Cancel upload"],
            key="ambiguous_radio",
            label_visibility="collapsed",
        )
        st.session_state.ambiguous_choice = choice
        if choice == "Cancel upload":
            _clear_tmpdir()
            return

    # --- File count summary ---
    st.caption(f"{len(uploaded)} file(s) selected · {total_size // 1024} KB total")

    # --- Scan & Clear buttons ---
    scan_ready = mode not in (Mode.IDLE, Mode.ERROR_NOT_SCANNABLE, Mode.ERROR_MIXED_ZIP, Mode.ERROR_MULTI_ANCHOR)
    if mode == Mode.AMBIGUOUS_NO_ANCHOR and st.session_state.get("ambiguous_choice") == "Cancel upload":
        scan_ready = False

    st.write("") # spacing

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Scan", disabled=not scan_ready, type="primary", key="scan_btn", use_container_width=True):
            _clear_tmpdir()
            st.session_state.scan_files = uploaded
            st.session_state.scan_mode = mode
            st.session_state.scan_results = None  # Clear previous results to force rescan

    with col2:
        if st.button("Clear", disabled=not uploaded, type="secondary", key="clear_btn", use_container_width=True):
            st.session_state.uploader_key += 1
            _clear_tmpdir()
            st.session_state.scan_results = None
            st.rerun()

# ---------------------------------------------------------------------------
# Results panel
# ---------------------------------------------------------------------------
def render_results_panel():
    mode = st.session_state.get("scan_mode", Mode.IDLE)
    files = st.session_state.get("scan_files", [])

    if mode == Mode.IDLE or not files:
        st.info("🐾 **No scan yet**\n\nUpload files and click Scan")
        return

    # If results are already cached, just render them
    if st.session_state.get("scan_results") is not None:
        _display_results(st.session_state.scan_results, mode)
        return

    with st.spinner("Scanning…"):
        try:
            if mode == Mode.SINGLE_FILE:
                result = run_single_scan(files[0])
                st.session_state.scan_results = [("Single File", result)]

            elif mode == Mode.BUNDLE:
                result = run_bundle_scan(files, frontmatter_absent=False)
                st.session_state.scan_results = [("Bundle", result)]

            elif mode == Mode.AMBIGUOUS_NO_ANCHOR:
                result = run_bundle_scan(files, frontmatter_absent=True)
                st.session_state.scan_results = [("Ambiguous Bundle", result)]

            elif mode == Mode.PROJECT:
                sub_results = run_project_scan(files[0])
                st.session_state.scan_results = sub_results

            _display_results(st.session_state.scan_results, mode)
        except Exception as e:
            st.error(f"Scan failed: {e}")

def _display_results(results_list, mode):
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

        if len(sub_results) == 1 and sub_results[0][0].startswith("(entire archive"):
            st.warning("No `SKILL.md` found in archive — entire zip scanned as one bundle without anchor.")

        for label, result in sub_results:
            cls = result["classification"]["class"]
            with st.expander(
                f"{SEVERITY_EMOJI[cls]}  {label}  —  {cls.upper()}",
                expanded=(cls != "safe"),
            ):
                render_single_result(result, label=label)


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="PromptHound",
        page_icon="🐾",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Header
    st.title("🐾 PromptHound")
    st.caption("Sniffer, not shield · Static risk analysis for AI agent skill files")

    # Two-column layout
    left, right = st.columns([1, 1.6], gap="large")

    with left:
        st.subheader("Upload")
        render_upload_panel()

    with right:
        st.subheader("Results")
        render_results_panel()


if __name__ == "__main__":
    main()
