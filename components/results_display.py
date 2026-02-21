"""
Pipeline results display component — agent response panels, full report,
and download buttons.

Extracted from app.py to reduce main-page complexity.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import streamlit as st

from components.ui_helpers import divider, escape_html, markdown_to_html


def render_results(result: Dict[str, str], *, uploaded_file_name: str, show_rag_debug: bool = False) -> None:
    """Render all agent-result panels, the combined report, and downloads."""

    divider()
    st.markdown("### 🤖 Agent Responses")

    # ---- optional RAG debug ----
    if show_rag_debug and result.get("strategy_context"):
        with st.expander("📚 RAG Strategy Context", expanded=False):
            st.markdown(
                f'<div class="agent-response">{escape_html(result["strategy_context"][:2000])}</div>',
                unsafe_allow_html=True,
            )

    # ---- tabbed agent outputs ----
    tab_overview, tab_analysis, tab_recs, tab_eval = st.tabs(
        ["📋 Overview", "🔍 Anomaly Analysis", "🛠 Recommendations", "📈 Quality Assessment"]
    )

    with tab_overview:
        st.markdown(result.get("overview", ""))
    with tab_analysis:
        st.markdown(result.get("analysis", ""))
    with tab_recs:
        st.markdown(result.get("recommendations", ""))
    with tab_eval:
        st.markdown(result.get("evaluation", ""))

    # ---- combined report ----
    divider()
    st.markdown("### 💬 Full Agent Report")
    st.caption("Combined output from all agents in the pipeline.")

    _SECTIONS = [
        ("Dataset Overview", result.get("overview", "")),
        ("Anomaly Analysis", result.get("analysis", "")),
        ("Cleaning Recommendations", result.get("recommendations", "")),
        ("Quality Assessment", result.get("evaluation", "")),
    ]

    full_report = ""
    for title, body in _SECTIONS:
        full_report += f"## {title}\n\n{body}\n\n---\n\n"

    st.markdown(
        f'<div class="agent-response">{markdown_to_html(full_report)}</div>',
        unsafe_allow_html=True,
    )

    # ---- download buttons ----
    stem = Path(uploaded_file_name).stem
    col_dl1, col_dl2, _ = st.columns([1, 1, 3])
    with col_dl1:
        st.download_button(
            "📥 Download Report (.md)",
            data=full_report,
            file_name=f"cleaning_report_{stem}.md",
            mime="text/markdown",
        )
    with col_dl2:
        st.download_button(
            "📥 Download Recommendations (.txt)",
            data=result.get("recommendations", ""),
            file_name=f"recommendations_{stem}.txt",
            mime="text/plain",
        )
