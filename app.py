"""
Autonomous Data Cleaning Agent — Streamlit UI
"""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Data Cleaning Agent",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for a polished look
# ---------------------------------------------------------------------------
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
# Helper: read uploaded file into a DataFrame
# ---------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {
    "csv": "CSV",
    "xlsx": "Excel (xlsx)",
    "xls": "Excel (xls)",
    "tsv": "TSV",
    "parquet": "Parquet",
    "json": "JSON",
}


def _read_upload(file) -> pd.DataFrame:
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


def _save_temp(file) -> str:
    """Persist the upload to a temp file so the pipeline can access it by path."""
    suffix = Path(file.name).suffix
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(file.getvalue())
    tmp.close()
    return tmp.name


# ---------------------------------------------------------------------------
# Helper: status badge HTML
# ---------------------------------------------------------------------------
_BADGE_MAP = {
    "idle": ("badge-idle", "IDLE"),
    "running": ("badge-running", "RUNNING"),
    "done": ("badge-done", "COMPLETE"),
    "error": ("badge-error", "ERROR"),
}


def _badge(status: str) -> str:
    cls, label = _BADGE_MAP.get(status, ("badge-idle", status.upper()))
    return f'<span class="status-badge {cls}">{label}</span>'


def _escape_html(text: str) -> str:
    """Minimal HTML escaping for rendering plaintext in an HTML container."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )


def _to_html(markdown_text: str) -> str:
    """Convert markdown text to basic HTML for the report container.

    Uses Streamlit's bundled markdown library if available, otherwise falls
    back to simple escaping.
    """
    try:
        import markdown as _md

        return _md.markdown(
            markdown_text,
            extensions=["fenced_code", "tables", "nl2br"],
        )
    except ImportError:
        return _escape_html(markdown_text)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">'
        "<h2>🧹 Data Cleaning Agent</h2>"
        "<p>Autonomous analysis &amp; recommendations</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

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
            st.session_state.df = _read_upload(uploaded)
            st.session_state.file_path = _save_temp(uploaded)
        except Exception as exc:
            st.session_state.df = None
            st.session_state.file_path = None
            st.session_state.status = "error"
            st.session_state.error_msg = str(exc)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # --- settings ---
    st.markdown("##### Settings")
    show_rag_debug = st.toggle("Show RAG context", value=False, help="Display the retrieval-augmented context used by agents")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.markdown(
        "<div style='text-align:center; font-size:0.72rem; color:#6B7280; padding-top:0.5rem;'>"
        "Powered by Ollama &middot; LangChain<br>chromadb &middot; Streamlit"
        "</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main area header
# ---------------------------------------------------------------------------
col_title, col_badge = st.columns([5, 1])
with col_title:
    st.markdown("## 🧹 Autonomous Data Cleaning Agent")
with col_badge:
    st.markdown(
        f"<div style='text-align:right; padding-top:0.6rem;'>{_badge(st.session_state.status)}</div>",
        unsafe_allow_html=True,
    )

st.caption("Upload a dataset to get AI-powered data quality analysis, anomaly detection, and cleaning recommendations.")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# No file uploaded yet — show landing state
# ---------------------------------------------------------------------------
if st.session_state.df is None:
    if st.session_state.status == "error":
        st.error(f"**Failed to read file:** {st.session_state.error_msg}")
    else:
        st.info("👈  Upload a dataset from the sidebar to get started.", icon="📂")
    st.stop()

# ---------------------------------------------------------------------------
# Dataset preview
# ---------------------------------------------------------------------------
df: pd.DataFrame = st.session_state.df

st.markdown("### 📊 Dataset Preview")

# Metric cards
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Rows", f"{len(df):,}")
c2.metric("Columns", f"{len(df.columns):,}")
c3.metric("Missing Cells", f"{df.isnull().sum().sum():,}")
c4.metric("Duplicate Rows", f"{df.duplicated().sum():,}")
mem_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
c5.metric("Memory", f"{mem_mb:.2f} MB")

# Tabs: preview / dtypes / stats
tab_preview, tab_dtypes, tab_stats, tab_missing = st.tabs(
    ["Preview", "Column Types", "Statistics", "Missing Values"]
)

with tab_preview:
    st.dataframe(df.head(100), width="stretch", height=320)

with tab_dtypes:
    dtype_df = pd.DataFrame(
        {"Column": df.columns, "Type": df.dtypes.astype(str).values}
    ).reset_index(drop=True)
    dtype_df.index += 1
    st.dataframe(dtype_df, width="stretch", height=320)

with tab_stats:
    try:
        st.dataframe(df.describe(include="all").T, width="stretch", height=320)
    except Exception:
        st.warning("Could not generate statistics for this dataset.")

with tab_missing:
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if missing.empty:
        st.success("No missing values detected! ✅")
    else:
        miss_df = pd.DataFrame(
            {
                "Column": missing.index,
                "Missing": missing.values,
                "% Missing": (missing.values / len(df) * 100).round(2),
            }
        ).reset_index(drop=True)
        miss_df.index += 1
        st.dataframe(miss_df, width="stretch", height=320)
        st.bar_chart(miss_df.set_index("Column")["% Missing"])


st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


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
    if st.button(
        "🚀  Run Analysis" if st.session_state.status != "done" else "🔄  Re-run Analysis",
        type="primary",
        width="stretch",
        disabled=run_disabled,
    ):
        with st.spinner("Agents are analyzing your dataset — this may take a minute…"):
            _run_pipeline()
        st.rerun()

with col_info:
    if st.session_state.status == "running":
        st.info("Pipeline is running… please wait.", icon="⏳")
    elif st.session_state.status == "error" and st.session_state.error_msg:
        st.error(f"**Pipeline error:** {st.session_state.error_msg}")
    elif st.session_state.status == "done":
        st.success(f"Analysis completed in **{st.session_state.elapsed:.1f}s**", icon="✅")

if st.session_state.result is None:
    st.stop()


# ---------------------------------------------------------------------------
# Results — agent response panels
# ---------------------------------------------------------------------------
result = st.session_state.result

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 🤖 Agent Responses")

# Optional RAG debug
if show_rag_debug and result.get("strategy_context"):
    with st.expander("📚 RAG Strategy Context", expanded=False):
        st.markdown(
            f'<div class="agent-response">{_escape_html(result["strategy_context"][:2000])}</div>',
            unsafe_allow_html=True,
        )

# Main result tabs
tab_overview, tab_analysis, tab_recs, tab_eval = st.tabs(
    ["📋 Overview", "🔍 Anomaly Analysis", "🛠 Recommendations", "📈 Quality Assessment"]
)


def _render_agent_block(content: str):
    """Render a block of agent text as markdown inside a styled container."""
    st.markdown(content)


with tab_overview:
    _render_agent_block(result.get("overview", ""))

with tab_analysis:
    _render_agent_block(result.get("analysis", ""))

with tab_recs:
    _render_agent_block(result.get("recommendations", ""))

with tab_eval:
    _render_agent_block(result.get("evaluation", ""))


# ---------------------------------------------------------------------------
# Bottom chat-style response area
# ---------------------------------------------------------------------------
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
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
    f'<div class="agent-response">{_to_html(full_report)}</div>',
    unsafe_allow_html=True,
)

# Download report button
col_dl1, col_dl2, _ = st.columns([1, 1, 3])
with col_dl1:
    st.download_button(
        "📥 Download Report (.md)",
        data=full_report,
        file_name=f"cleaning_report_{Path(st.session_state.uploaded_file.name).stem}.md",
        mime="text/markdown",
    )
with col_dl2:
    # Download cleaned recommendations as plain text
    st.download_button(
        "📥 Download Recommendations (.txt)",
        data=result.get("recommendations", ""),
        file_name=f"recommendations_{Path(st.session_state.uploaded_file.name).stem}.txt",
        mime="text/plain",
    )
