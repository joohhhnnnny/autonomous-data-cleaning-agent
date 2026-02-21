"""
Reusable FontAwesome icon utilities for Streamlit pages.
"""
import streamlit as st


def load_fontawesome():
    """Load FontAwesome CSS and custom icon styles."""
    st.markdown(
        """
        <link rel="stylesheet"
              href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <style>
        .fa-icon { margin-right: 8px; }
        .icon-title { font-size: 24px; }
        .icon-text  { font-size: 18px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def icon(name: str, size: str = "icon-text") -> str:
    """Return HTML for a FontAwesome icon.

    Args:
        name: FontAwesome icon name (without 'fa-' prefix).
        size: CSS class for size ("icon-title" or "icon-text").

    Returns:
        HTML string for the icon.
    """
    return f'<i class="fa-solid fa-{name} fa-icon {size}"></i>'
