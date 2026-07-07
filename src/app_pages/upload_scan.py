import streamlit as st

from app_utils import (
    Mode,
    detect_mode,
    _clear_tmpdir,
    run_single_scan,
    run_bundle_scan,
    run_project_scan,
    display_results,
)
from prompthound.limits import MAX_BUNDLE_SIZE, MAX_FILES


# ---------------------------------------------------------------------------
# Upload panel
# ---------------------------------------------------------------------------
def render_upload_panel():
    st.info(
        "**How to upload**\n- **Single skill file** — select one `.md` file\n- **Skill bundle** — select `SKILL.md` and all supporting files together\n- **Full project** — zip your project root and upload the `.zip`"
    )

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
    text_exts = {
        ".md",
        ".txt",
        ".sh",
        ".py",
        ".js",
        ".ts",
        ".yaml",
        ".yml",
        ".json",
        ".toml",
        ".cfg",
        ".ini",
        ".zip",
    }
    binary_files = [
        f.name for f in uploaded if not any(f.name.endswith(e) for e in text_exts)
    ]
    if binary_files:
        st.warning(
            f"{len(binary_files)} binary file(s) will be treated as empty — matches CLI behaviour: {', '.join(binary_files[:5])}{'…' if len(binary_files) > 5 else ''}"
        )

    # --- Limit warnings ---
    total_size = sum(f.size for f in uploaded)
    if total_size > MAX_BUNDLE_SIZE:
        st.warning(
            f"Total size {total_size // (1024*1024)} MB exceeds {MAX_BUNDLE_SIZE // (1024*1024)} MB limit — only first {MAX_BUNDLE_SIZE // (1024*1024)} MB will be analysed."
        )
    if len(uploaded) > MAX_FILES:
        st.warning(
            f"{len(uploaded)} files uploaded — exceeds {MAX_FILES} file limit. Only first {MAX_FILES} will be analysed."
        )

    # --- Error states ---
    if mode == Mode.ERROR_NOT_SCANNABLE:
        st.error(
            "File is not scannable. Upload a `.md` skill file or a `.zip` project archive."
        )
        return

    if mode == Mode.ERROR_MIXED_ZIP:
        st.error(
            "Cannot mix a `.zip` with other files. For project scans, upload only the `.zip`."
        )
        return

    if mode == Mode.ERROR_MULTI_ANCHOR:
        st.error(
            "Multiple `SKILL.md` files found in a flat upload — cannot determine bundle boundaries. To scan multiple skills, zip the project root and upload it."
        )
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
    scan_ready = mode not in (
        Mode.IDLE,
        Mode.ERROR_NOT_SCANNABLE,
        Mode.ERROR_MIXED_ZIP,
        Mode.ERROR_MULTI_ANCHOR,
    )
    if (
        mode == Mode.AMBIGUOUS_NO_ANCHOR
        and st.session_state.get("ambiguous_choice") == "Cancel upload"
    ):
        scan_ready = False

    st.write("")  # spacing

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button(
            "Scan",
            disabled=not scan_ready,
            type="primary",
            key="scan_btn",
            use_container_width=True,
        ):
            _clear_tmpdir()
            st.session_state.scan_files = uploaded
            st.session_state.scan_mode = mode
            st.session_state.scan_results = (
                None  # Clear previous results to force rescan
            )

    with col2:
        if st.button(
            "Clear",
            disabled=not uploaded,
            type="secondary",
            key="clear_btn",
            use_container_width=True,
        ):
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
        display_results(st.session_state.scan_results, mode)
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

            display_results(st.session_state.scan_results, mode)
        except Exception as e:
            st.error(f"Scan failed: {e}")


# Two-column layout
left, right = st.columns([1, 1.6], gap="large")

with left:
    st.subheader("Upload")
    render_upload_panel()

with right:
    st.subheader("Results")
    render_results_panel()
