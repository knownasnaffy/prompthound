"""
PromptHound Web UI — Streamlit frontend for the scan pipeline.

Launch:
    streamlit run src/app.py

Install deps:
    pip install -e ".[app]"
"""

import streamlit as st

st.set_page_config(
    page_title="PromptHound",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
page = st.navigation([
    st.Page("app_pages/upload_scan.py", title="Upload & Scan", icon=":material/upload_file:"),
    st.Page("app_pages/github_scan.py", title="GitHub Scan", icon=":material/code:"),
])

# App-level UI runs before page content
st.sidebar.title("🐾 PromptHound")
st.sidebar.caption("Sniffer, not shield · Static risk analysis for AI agent skill files")

page.run()
