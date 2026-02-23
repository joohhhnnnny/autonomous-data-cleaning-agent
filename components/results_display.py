"""
Pipeline results display component — agent response panels, full report,
and download buttons.

Extracted from app.py to reduce main-page complexity.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
import streamlit as st

from components.ui_helpers import divider, escape_html, markdown_to_html


# ---------------------------------------------------------------------------
# Quality helpers
# ---------------------------------------------------------------------------
def _assess_quality(df: pd.DataFrame) -> dict:
    """Return quality metrics and a boolean ``has_issues`` flag."""
    missing = int(df.isnull().sum().sum())
    duplicates = int(df.duplicated().sum())
    has_issues = missing > 0 or duplicates > 0
    return {"missing": missing, "duplicates": duplicates, "has_issues": has_issues}


def _quality_class(has_issues: bool) -> str:
    """CSS class for the Quality Assessment section (dynamic)."""
    return "quality-bad" if has_issues else "quality-good"


def _render_section_html(body_md: str, css_class: str) -> None:
    """Render markdown *body_md* inside a styled ``<div>``."""
    html = markdown_to_html(body_md) if body_md else ""
    st.markdown(
        f'<div class="{css_class}">{html}</div>',
        unsafe_allow_html=True,
    )


def render_results(
    result: Dict[str, str],
    *,
    uploaded_file_name: str,
    df: pd.DataFrame,
    show_rag_debug: bool = False,
) -> None:
    """Render all agent-result panels, the combined report, and downloads.

    Variable / column-name colors are **dynamic**:
    - Overview → neutral (blue)
    - Anomaly Analysis → red (problems)
    - Recommendations → amber (action items)
    - Quality Assessment → green if clean, red if issues remain
    """

    quality = _assess_quality(df)
    eval_class = _quality_class(quality["has_issues"])

    divider()
    st.markdown("### Agent Responses")

    # ---- optional RAG debug ----
    if show_rag_debug and result.get("strategy_context"):
        with st.expander(":material/library_books: RAG Strategy Context", expanded=False):
            st.markdown(
                f'<div class="agent-response">{escape_html(result["strategy_context"][:2000])}</div>',
                unsafe_allow_html=True,
            )

    # ---- tabbed agent outputs ----
    tab_overview, tab_analysis, tab_recs, tab_eval = st.tabs(
        [":material/list_alt: Overview", ":material/search: Anomaly Analysis", ":material/build: Recommendations", ":material/trending_up: Quality Assessment"]
    )

    with tab_overview:
        _render_section_html(result.get("overview", ""), "quality-neutral")
    with tab_analysis:
        _render_section_html(result.get("analysis", ""), "quality-bad")
    with tab_recs:
        _render_section_html(result.get("recommendations", ""), "quality-warn")
    with tab_eval:
        _render_section_html(result.get("evaluation", ""), eval_class)

    # ---- combined report ----
    divider()
    st.markdown("### Full Agent Report")
    st.caption("Combined output from all agents in the pipeline.")

    _SECTIONS = [
        ("Dataset Overview", result.get("overview", ""), "quality-neutral"),
        ("Anomaly Analysis", result.get("analysis", ""), "quality-bad"),
        ("Cleaning Recommendations", result.get("recommendations", ""), "quality-warn"),
        ("Quality Assessment", result.get("evaluation", ""), eval_class),
    ]

    full_report_md = ""
    full_report_html = ""
    for title, body, cls in _SECTIONS:
        full_report_md += f"## {title}\n\n{body}\n\n---\n\n"
        full_report_html += f'<div class="{cls}"><h2>{title}</h2>{markdown_to_html(body)}</div><hr>'

    st.markdown(
        f'<div class="agent-response">{full_report_html}</div>',
        unsafe_allow_html=True,
    )

    # ---- download buttons ----
    stem = Path(uploaded_file_name).stem
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            "Download Report (.md)",
            icon=":material/download:",
            data=full_report_md,
            file_name=f"cleaning_report_{stem}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_dl2:
        st.download_button(
            "Download Recommendations (.txt)",
            icon=":material/download:",
            data=result.get("recommendations", ""),
            file_name=f"recommendations_{stem}.txt",
            mime="text/plain",
            use_container_width=True,
        )
