"""
Autonomous Data Cleaning Agent — Streamlit UI (Home Page)

Components and helpers live in the ``components/`` package.
Additional pages (Dataset Reader, Dataset Splitter) are in ``pages/``.
"""

from __future__ import annotations

import time
from typing import Dict

import pandas as pd
import streamlit as st

from components.styles import inject_custom_css
from components.ui_helpers import status_badge, divider
from components.sidebar import render_sidebar
from components.dataset_preview import render_dataset_preview
from components.results_display import render_results

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Data Cleaning Agent",
    page_icon=":material/mop:",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
_DEFAULTS: Dict[str, object] = {
    "uploaded_file": None,
    "df": None,
    "file_path": None,
    "result": None,
    "status": "idle",          # idle | running | done | error
    "error_msg": "",
    "elapsed": 0.0,
}
for key, val in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------------------------------------------------------------------
# Sidebar (upload + settings)
# ---------------------------------------------------------------------------
show_rag_debug = render_sidebar()

# ---------------------------------------------------------------------------
# Main area header
# ---------------------------------------------------------------------------
col_title, col_badge = st.columns([5, 1])
with col_title:
    st.markdown("## Autonomous Data Cleaning Agent")
with col_badge:
    st.markdown(
        f"<div style='text-align:right; padding-top:0.6rem;'>{status_badge(st.session_state.status)}</div>",
        unsafe_allow_html=True,
    )

st.caption("Upload a dataset to get AI-powered data quality analysis, anomaly detection, and cleaning recommendations.")
divider()

# ---------------------------------------------------------------------------
# No file uploaded yet — show landing state
# ---------------------------------------------------------------------------
if st.session_state.df is None:
    if st.session_state.status == "error":
        st.error(f"**Failed to read file:** {st.session_state.error_msg}")
    else:
        st.info("Upload a dataset from the sidebar to get started.", icon=":material/folder_open:")
    st.stop()

# ---------------------------------------------------------------------------
# Dataset preview (extracted to component)
# ---------------------------------------------------------------------------
render_dataset_preview(st.session_state.df)

# ---------------------------------------------------------------------------
# Run analysis button
# ---------------------------------------------------------------------------
def _run_pipeline():
    """Execute the cleaning pipeline and store results in session state."""
    from core.controller import clean_dataset

    st.session_state.status = "running"
    st.session_state.error_msg = ""
    try:
        start = time.time()
        result = clean_dataset(st.session_state.file_path)
        st.session_state.elapsed = time.time() - start
        st.session_state.result = result
        st.session_state.status = "done"
    except Exception as exc:
        st.session_state.status = "error"
        st.session_state.error_msg = str(exc)


col_btn, col_info = st.columns([1, 4])
with col_btn:
    run_disabled = st.session_state.status == "running"
    _btn_label = "Run Analysis" if st.session_state.status != "done" else "Re-run Analysis"
    _btn_icon = ":material/rocket_launch:" if st.session_state.status != "done" else ":material/refresh:"
    if st.button(
        _btn_label,
        icon=_btn_icon,
        type="primary",
        width="stretch",
        disabled=run_disabled,
    ):
        with st.spinner("Agents are analyzing your dataset — this may take a minute…"):
            _run_pipeline()
        st.rerun()

with col_info:
    if st.session_state.status == "running":
        st.info("Pipeline is running… please wait.", icon=":material/hourglass_top:")
    elif st.session_state.status == "error" and st.session_state.error_msg:
        st.error(f"**Pipeline error:** {st.session_state.error_msg}")
    elif st.session_state.status == "done":
        st.success(f"Analysis completed in **{st.session_state.elapsed:.1f}s**", icon=":material/check_circle:")

if st.session_state.result is None:
    st.stop()

# ---------------------------------------------------------------------------
# Results (extracted to component)
# ---------------------------------------------------------------------------
render_results(
    st.session_state.result,
    uploaded_file_name=st.session_state.uploaded_file.name,
    df=st.session_state.df,
    show_rag_debug=show_rag_debug,
)
