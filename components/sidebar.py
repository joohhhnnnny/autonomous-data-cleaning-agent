"""
Sidebar component — branding, file upload, settings.

Extracted from app.py to reduce main-page complexity.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Dict

import pandas as pd
import streamlit as st

from components.ui_helpers import divider


# ---------------------------------------------------------------------------
# Supported upload extensions
# ---------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {
    "csv": "CSV",
    "xlsx": "Excel (xlsx)",
    "xls": "Excel (xls)",
    "tsv": "TSV",
    "parquet": "Parquet",
    "json": "JSON",
}


# ---------------------------------------------------------------------------
# File I/O helpers
# ---------------------------------------------------------------------------
def read_upload(file) -> pd.DataFrame:
    """Read an uploaded file into a DataFrame, handling many formats."""
    suffix = Path(file.name).suffix.lower().lstrip(".")
    if suffix == "csv":
        try:
            return pd.read_csv(file)
        except UnicodeDecodeError:
            file.seek(0)
            return pd.read_csv(file, encoding="latin-1")
    elif suffix == "tsv":
        try:
            return pd.read_csv(file, sep="\t")
        except UnicodeDecodeError:
            file.seek(0)
            return pd.read_csv(file, sep="\t", encoding="latin-1")
    elif suffix in ("xlsx", "xls"):
        return pd.read_excel(file)
    elif suffix == "parquet":
        return pd.read_parquet(file)
    elif suffix == "json":
        return pd.read_json(file)
    else:
        raise ValueError(f"Unsupported file type: .{suffix}")


def save_temp(file) -> str:
    """Persist the upload to a temp file so the pipeline can access it by path."""
    suffix = Path(file.name).suffix
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(file.getvalue())
    tmp.close()
    return tmp.name


# ---------------------------------------------------------------------------
# Sidebar renderer
# ---------------------------------------------------------------------------
def render_sidebar() -> bool:
    """Render the sidebar and return the current ``show_rag_debug`` toggle value."""

    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand">'
            "<h2>Data Cleaning Agent</h2>"
            "<p>Autonomous analysis &amp; recommendations</p>"
            "</div>",
            unsafe_allow_html=True,
        )

        divider()

        st.markdown("##### Upload Dataset")
        uploaded = st.file_uploader(
            "Drag & drop or browse",
            type=list(SUPPORTED_EXTENSIONS.keys()),
            help="Supported formats: " + ", ".join(SUPPORTED_EXTENSIONS.values()),
        )

        if uploaded is not None and (
            st.session_state.uploaded_file is None
            or st.session_state.uploaded_file.name != uploaded.name
            or st.session_state.uploaded_file.size != uploaded.size
        ):
            st.session_state.uploaded_file = uploaded
            st.session_state.result = None
            st.session_state.status = "idle"
            st.session_state.error_msg = ""
            try:
                st.session_state.df = read_upload(uploaded)
                st.session_state.file_path = save_temp(uploaded)
            except Exception as exc:
                st.session_state.df = None
                st.session_state.file_path = None
                st.session_state.status = "error"
                st.session_state.error_msg = str(exc)

        divider()

        # Settings
        st.markdown("##### Settings")
        show_rag_debug = st.toggle(
            "Show RAG context",
            value=False,
            help="Display the retrieval-augmented context used by agents",
        )

        divider()

        st.markdown(
            "<div style='text-align:center; font-size:0.72rem; color:#6B7280; padding-top:0.5rem;'>"
            "Powered by Ollama &middot; LangChain<br>chromadb &middot; Streamlit"
            "</div>",
            unsafe_allow_html=True,
        )

    return show_rag_debug
