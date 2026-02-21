"""
Shared CSS styles for the Streamlit application.
"""
import streamlit as st


def inject_custom_css():
    """Inject the application-wide custom CSS."""
    st.markdown(
        """
        <style>
        /* ---- global tweaks ---- */
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        h1, h2, h3 { letter-spacing: -0.02em; }

        /* ---- upload zone ---- */
        [data-testid="stFileUploader"] {
            border: 2px dashed #6C63FF;
            border-radius: 12px;
            padding: 1.2rem;
            transition: border-color 0.3s;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: #8B83FF;
        }

        /* ---- metric cards ---- */
        [data-testid="stMetric"] {
            background: #1A1D23;
            border: 1px solid #2A2D35;
            border-radius: 10px;
            padding: 0.8rem 1rem;
        }

        /* ---- agent response area ---- */
        .agent-response {
            background: #161922;
            border: 1px solid #2A2D35;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin-top: 0.5rem;
            font-size: 0.92rem;
            line-height: 1.65;
            max-height: 520px;
            overflow-y: auto;
        }

        /* ---- status badge ---- */
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.03em;
        }
        .badge-idle    { background: #2A2D35; color: #9CA3AF; }
        .badge-running { background: #1E3A5F; color: #60A5FA; }
        .badge-done    { background: #14532D; color: #4ADE80; }
        .badge-error   { background: #7F1D1D; color: #FCA5A5; }

        /* ---- section dividers ---- */
        .section-divider {
            border: none;
            border-top: 1px solid #2A2D35;
            margin: 1.5rem 0;
        }

        /* ---- sidebar branding ---- */
        .sidebar-brand {
            text-align: center;
            padding: 0.5rem 0 1rem 0;
        }
        .sidebar-brand h2 {
            margin: 0;
            font-size: 1.25rem;
            color: #6C63FF;
        }
        .sidebar-brand p {
            margin: 0.2rem 0 0 0;
            font-size: 0.78rem;
            color: #9CA3AF;
        }

        /* ---- tab styling ---- */
        .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 0.5rem 1.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
