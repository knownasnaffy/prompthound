import io
import urllib.request
import urllib.error
import re
import streamlit as st

from utils import Mode, run_project_scan, display_results, _clear_tmpdir

st.subheader("GitHub Repository Scan")
st.info(
    "Enter a public GitHub repository URL to download its default branch archive and scan it for risks."
)

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
if "github_scan_results" not in st.session_state:
    st.session_state.github_scan_results = None

# ---------------------------------------------------------------------------
# UI Input
# ---------------------------------------------------------------------------
with st.form("github_scan_form"):
    repo_url = st.text_input(
        "GitHub URL", placeholder="https://github.com/knownasnaffy/prompthound"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        scan_btn = st.form_submit_button("Scan Repository", type="primary", use_container_width=True)
    with col2:
        clear_btn = st.form_submit_button("Clear", type="secondary")

if clear_btn:
    st.session_state.github_scan_results = None
    _clear_tmpdir()
    st.rerun()


# ---------------------------------------------------------------------------
# Logic
# ---------------------------------------------------------------------------
def extract_owner_repo(url: str) -> tuple:
    """Extract owner and repo from a GitHub URL."""
    # Match standard github.com URLs
    match = re.search(r"github\.com/([^/]+)/([^/.]+)", url)
    if match:
        return match.group(1), match.group(2)
    return None, None


def download_github_zip(owner: str, repo: str) -> io.BytesIO:
    """Download the zipball for a given GitHub repository using the GitHub API."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
    req = urllib.request.Request(api_url, headers={"User-Agent": "PromptHound-Web"})
    try:
        with urllib.request.urlopen(req) as response:
            zip_bytes = response.read()
            return io.BytesIO(zip_bytes)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API returned {e.code}: {e.reason}")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch repository: {str(e)}")


if scan_btn and repo_url:
    owner, repo = extract_owner_repo(repo_url)
    if not owner or not repo:
        st.error("Invalid GitHub URL. Please enter a valid repository URL.")
    else:
        st.session_state.github_scan_results = None
        _clear_tmpdir()

        with st.spinner(f"Downloading {owner}/{repo}..."):
            try:
                zip_io = download_github_zip(owner, repo)
                download_success = True
            except Exception as e:
                st.error(str(e))
                download_success = False

        if download_success:
            with st.spinner("Scanning repository..."):
                try:
                    # run_project_scan accepts a file-like object with read() and seek(0)
                    results = run_project_scan(zip_io)
                    st.session_state.github_scan_results = results
                except Exception as e:
                    st.error(f"Scan failed: {e}")

# ---------------------------------------------------------------------------
# Results Rendering
# ---------------------------------------------------------------------------
if st.session_state.github_scan_results is not None:
    st.write("---")
    st.subheader("Results")
    display_results(st.session_state.github_scan_results, Mode.PROJECT)
