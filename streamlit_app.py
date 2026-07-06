"""PromptHound — Streamlit web app.

Mirrors the CLI's ``prompthound scan`` functionality with an interactive UI.
Accepts a skill file via upload or manual paste, runs the full scan pipeline
(Parse → Rules → Features → Classifier → Chains → Reporter), and renders
the three evidence sections (rule hits, classifier score, capability chains)
visibly separate — the same architectural requirement that governs the CLI
reporter (architecture.md §2.6, AGENTS.md §5).

Launch:
    streamlit run streamlit_app.py

Install extras first if not already done:
    pip install -e ".[app]"
"""

from __future__ import annotations

import io
import json
import tempfile
from pathlib import Path

import streamlit as st

# ── Page config must be the first Streamlit call ──────────────────────────────
st.set_page_config(
    page_title="PromptHound",
    page_icon="🐕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Pipeline imports (lazy-style to surface ImportError clearly) ──────────────
try:
    from prompthound.chains import check_chains
    from prompthound.classifier.model import classify
    from prompthound.features import extract_features
    from prompthound.parse import parse_skill
    from prompthound.report import render_json, render_sarif
    from prompthound.rules import ALL_RULES
    from prompthound.schema import ScanResult
except ImportError as exc:
    st.error(
        f"**Import error:** {exc}\n\n"
        "Make sure the package is installed: `pip install -e '.[app]'`"
    )
    st.stop()


# ── Helpers ────────────────────────────────────────────────────────────────────

_SEVERITY_RANK: dict[str, int] = {"benign": 0, "suspicious": 1, "malicious": 2}

_RISK_COLORS: dict[str, str] = {
    "benign": "#2ecc71",
    "suspicious": "#f39c12",
    "malicious": "#e74c3c",
}

_RISK_EMOJIS: dict[str, str] = {
    "benign": "✅",
    "suspicious": "⚠️",
    "malicious": "🚨",
}

_SEVERITY_COLORS: dict[str, str] = {
    "info": "#3498db",
    "warn": "#f39c12",
    "high": "#e74c3c",
}


def _run_scan(content: str, filename: str) -> ScanResult:
    """Write *content* to a temp file, run the full pipeline, return ScanResult.

    Uses a NamedTemporaryFile so parse_skill gets a real path on disk —
    identical to how the CLI receives its ``PATH`` argument.
    """
    suffix = Path(filename).suffix or ".md"
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    parsed = parse_skill(tmp_path)
    # Override the display path so the UI shows the original filename
    parsed.path = filename

    if not parsed.parse_ok:
        return ScanResult(parsed=parsed)

    rule_hits = [hit for rule in ALL_RULES for hit in rule(parsed)]
    features = extract_features(parsed)
    risk = classify(features)
    chain_flags = check_chains(parsed)

    return ScanResult(
        parsed=parsed,
        rule_hits=rule_hits,
        features=features,
        risk=risk,
        chain_flags=chain_flags,
    )


def _score_gauge_html(score: float, label: str) -> str:
    """Return an HTML/CSS circular gauge for the risk score."""
    color = _RISK_COLORS.get(label, "#95a5a6")
    pct = int(score * 100)
    # CSS conic-gradient pie gauge
    return f"""
    <div style="display:flex;align-items:center;gap:24px;margin:8px 0 16px 0;">
      <div style="
          width:110px;height:110px;border-radius:50%;
          background:conic-gradient({color} {pct}%, #ecf0f1 {pct}%);
          display:flex;align-items:center;justify-content:center;
          box-shadow:0 2px 8px rgba(0,0,0,0.15);
      ">
        <div style="
            width:82px;height:82px;border-radius:50%;background:#0e1117;
            display:flex;flex-direction:column;align-items:center;justify-content:center;
        ">
          <span style="font-size:22px;font-weight:700;color:{color};">{score:.2f}</span>
          <span style="font-size:10px;color:#aaa;margin-top:2px;">RISK</span>
        </div>
      </div>
      <div>
        <div style="font-size:28px;font-weight:800;color:{color};">
          {_RISK_EMOJIS.get(label,'')} {label.upper()}
        </div>
        <div style="font-size:13px;color:#aaa;margin-top:4px;">
          Score {score:.4f} · threshold bands: &lt;0.30 benign · 0.30–0.65 suspicious · ≥0.65 malicious
        </div>
      </div>
    </div>
    """


def _importance_bar_html(feature: str, importance: float, max_importance: float) -> str:
    """Single horizontal bar for a feature importance row."""
    pct = (abs(importance) / max(max_importance, 1e-9)) * 100
    color = "#e74c3c" if importance > 0 else "#3498db"
    sign = "+" if importance >= 0 else ""
    return (
        f'<div style="display:flex;align-items:center;gap:8px;margin:3px 0;">'
        f'  <div style="width:180px;font-size:12px;color:#ccc;text-align:right;'
        f'       white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{feature}</div>'
        f'  <div style="flex:1;background:#1e2130;border-radius:3px;height:14px;">'
        f'    <div style="width:{pct:.1f}%;background:{color};height:100%;border-radius:3px;"></div>'
        f'  </div>'
        f'  <div style="width:70px;font-size:12px;color:{color};font-family:monospace;">'
        f'    {sign}{importance:.4f}</div>'
        f'</div>'
    )


# ── UI ─────────────────────────────────────────────────────────────────────────

def main() -> None:
    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
          <span style="font-size:40px;">🐕</span>
          <div>
            <h1 style="margin:0;padding:0;font-size:2rem;">PromptHound</h1>
            <p style="margin:0;padding:0;color:#aaa;font-size:14px;">
              Offline static risk analysis for AI agent skill files
            </p>
          </div>
        </div>
        <hr style="margin:12px 0 20px 0;border-color:#333;">
        """,
        unsafe_allow_html=True,
    )

    # ── Input area ─────────────────────────────────────────────────────────────
    input_col, _ = st.columns([3, 1])
    with input_col:
        input_mode = st.radio(
            "Input method",
            ["Upload a file", "Paste content"],
            horizontal=True,
            label_visibility="collapsed",
        )

    content: str | None = None
    filename: str = "skill.md"

    if input_mode == "Upload a file":
        uploaded = st.file_uploader(
            "Upload a skill file (.md, .txt, or any text file)",
            type=None,
            label_visibility="collapsed",
        )
        if uploaded is not None:
            try:
                content = io.TextIOWrapper(uploaded, encoding="utf-8").read()
            except UnicodeDecodeError:
                st.error("File is not valid UTF-8 text. PromptHound only analyses text files.")
                st.stop()
            filename = uploaded.name

    else:  # Paste
        pasted = st.text_area(
            "Paste skill file content",
            height=220,
            placeholder="# My Skill\n\n---\nname: my-skill\ncapabilities:\n  - read_files\n---\n\nYour skill content here…",
            label_visibility="collapsed",
        )
        if pasted.strip():
            content = pasted
            filename = "pasted_skill.md"

    # ── Scan button ────────────────────────────────────────────────────────────
    scan_col, fail_col = st.columns([2, 2])
    with scan_col:
        scan_clicked = st.button("🔍 Scan", type="primary", use_container_width=True, disabled=content is None)
    with fail_col:
        fail_on = st.selectbox(
            "Fail threshold (for exit-code indicator)",
            ["— none —", "suspicious", "malicious"],
            label_visibility="collapsed",
        )
        fail_on_value: str | None = None if fail_on == "— none —" else fail_on

    if content is None:
        st.info("Upload a file or paste content above, then click **Scan**.")
        return

    if not scan_clicked:
        # Show a preview of the content
        with st.expander("File preview", expanded=False):
            st.code(content[:4000] + ("…" if len(content) > 4000 else ""), language="markdown")
        return

    # ── Run the pipeline ───────────────────────────────────────────────────────
    with st.spinner("Scanning…"):
        try:
            result = _run_scan(content, filename)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unexpected error during scan: {exc}")
            st.exception(exc)
            return

    # ── Parse failure short-circuit ────────────────────────────────────────────
    if not result.parsed.parse_ok:
        st.error("**Could not parse file**")
        st.warning(result.parsed.parse_error or "Unknown parse error.")
        st.info("No further analysis was performed — the file structure is invalid.")
        return

    # ── Overall verdict banner ─────────────────────────────────────────────────
    risk = result.risk
    if risk is not None:
        st.markdown(
            _score_gauge_html(risk.score, risk.label),
            unsafe_allow_html=True,
        )

        # CI exit-code indicator
        if fail_on_value is not None:
            threshold = _SEVERITY_RANK.get(fail_on_value, 1)
            actual = _SEVERITY_RANK.get(risk.label, 0)
            if actual >= threshold:
                st.error(
                    f"🚦 **CI would EXIT 1** — risk label `{risk.label}` "
                    f"meets the `--fail-on {fail_on_value}` threshold."
                )
            else:
                st.success(
                    f"🚦 **CI would EXIT 0** — risk label `{risk.label}` "
                    f"is below the `--fail-on {fail_on_value}` threshold."
                )

    st.markdown("---")

    # ── Three evidence sections ────────────────────────────────────────────────
    # Architecture constraint: rule hits / classifier / chains MUST remain
    # visibly separate (architecture.md §2.6, AGENTS.md §5).

    tab_rules, tab_classifier, tab_chains, tab_export = st.tabs([
        f"🔎 Rule Hits ({len(result.rule_hits)})",
        "🤖 Classifier",
        f"⛓ Capability Chains ({len(result.chain_flags)})",
        "📤 Export",
    ])

    # ── Tab 1: Rule hits ───────────────────────────────────────────────────────
    with tab_rules:
        st.markdown("**Deterministic heuristic rules** (stateless, independent of classifier)")
        if not result.rule_hits:
            st.success("No rule hits detected.")
        else:
            for hit in result.rule_hits:
                color = _SEVERITY_COLORS.get(hit.severity.lower(), "#95a5a6")
                with st.container():
                    sev_badge = f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:700;">{hit.severity.upper()}</span>'
                    st.markdown(
                        f'{sev_badge} &nbsp; <code style="font-size:13px;">{hit.rule_id}</code>'
                        f' &nbsp; <span style="color:#888;font-size:12px;">span ({hit.span[0]}, {hit.span[1]})</span>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"> {hit.message}")
                    st.markdown("")

    # ── Tab 2: Classifier ──────────────────────────────────────────────────────
    with tab_classifier:
        st.markdown("**ML risk score + local feature contributions** (Saabas decomposition)")
        if risk is None:
            st.warning("Classifier was not run (artifact missing or parse failed).")
        else:
            col_score, col_feats = st.columns([1, 2])
            with col_score:
                st.metric("Risk Score", f"{risk.score:.4f}")
                st.metric("Label", risk.label.upper())

            with col_feats:
                st.markdown("**Feature importances**")
                if not risk.feature_importances:
                    st.info("No feature importances available.")
                else:
                    max_imp = max(abs(f["importance"]) for f in risk.feature_importances)
                    bars_html = "".join(
                        _importance_bar_html(f["feature"], f["importance"], max_imp)
                        for f in risk.feature_importances
                    )
                    st.markdown(bars_html, unsafe_allow_html=True)

            # Raw feature vector
            if result.features is not None:
                with st.expander("Raw feature vector", expanded=False):
                    st.json(result.features.values)

    # ── Tab 3: Capability chains ───────────────────────────────────────────────
    with tab_chains:
        st.markdown("**Structural sequence detection** (declared-vs-referenced capability chains)")
        if not result.chain_flags:
            st.success("No dangerous capability chains detected.")
        else:
            for flag in result.chain_flags:
                st.markdown(f"#### ⛓ `{flag.chain_name}`")
                steps_data = [
                    {"Step": i + 1, "Capability": cap, "Line": ln}
                    for i, (cap, ln) in enumerate(flag.steps)
                ]
                st.table(steps_data)

    # ── Tab 4: Export ──────────────────────────────────────────────────────────
    with tab_export:
        st.markdown("**Download the scan result in structured formats**")

        export_col1, export_col2 = st.columns(2)

        with export_col1:
            st.markdown("**JSON**")
            json_output = render_json(result)
            st.download_button(
                "⬇️ Download JSON",
                data=json_output,
                file_name=f"{Path(filename).stem}_prompthound.json",
                mime="application/json",
                use_container_width=True,
            )
            with st.expander("Preview JSON", expanded=False):
                st.code(json_output, language="json")

        with export_col2:
            st.markdown("**SARIF 2.1.0**")
            sarif_output = render_sarif(result)
            st.download_button(
                "⬇️ Download SARIF",
                data=sarif_output,
                file_name=f"{Path(filename).stem}_prompthound.sarif",
                mime="application/json",
                use_container_width=True,
            )
            with st.expander("Preview SARIF", expanded=False):
                st.code(sarif_output, language="json")

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <hr style="margin:32px 0 12px 0;border-color:#333;">
        <p style="text-align:center;color:#555;font-size:12px;">
          PromptHound · offline · no network calls · no data leaves this machine
        </p>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
