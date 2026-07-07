"""
Shared scan limits — single source of truth.
Imported by both flatten.py (CLI path) and app.py (Streamlit path).
Changing values here propagates everywhere automatically.
"""

MAX_BUNDLE_SIZE: int = 5 * 1024 * 1024  # 5 MB
MAX_FILES: int = 100
