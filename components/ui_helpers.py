"""
Small UI helper utilities shared across pages.
"""
from __future__ import annotations

import streamlit as st


# ---------------------------------------------------------------------------
# Status badge
# ---------------------------------------------------------------------------
_BADGE_MAP = {
    "idle":    ("badge-idle",    "IDLE"),
    "running": ("badge-running", "RUNNING"),
    "done":    ("badge-done",    "COMPLETE"),
    "error":   ("badge-error",   "ERROR"),
}


def status_badge(status: str) -> str:
    """Return an HTML ``<span>`` badge for the given pipeline status."""
    cls, label = _BADGE_MAP.get(status, ("badge-idle", status.upper()))
    return f'<span class="status-badge {cls}">{label}</span>'


# ---------------------------------------------------------------------------
# HTML / Markdown helpers
# ---------------------------------------------------------------------------
def escape_html(text: str) -> str:
    """Minimal HTML-escaping for rendering plain text in an HTML container."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )


def markdown_to_html(markdown_text: str) -> str:
    """Convert Markdown to basic HTML.

    Uses the ``markdown`` library if available, otherwise falls back to
    simple escaping.
    """
    try:
        import markdown as _md

        return _md.markdown(
            markdown_text,
            extensions=["fenced_code", "tables", "nl2br"],
        )
    except ImportError:
        return escape_html(markdown_text)


# ---------------------------------------------------------------------------
# Section divider shorthand
# ---------------------------------------------------------------------------
def divider():
    """Render a styled horizontal divider."""
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
