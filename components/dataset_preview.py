"""
Dataset preview component — metric cards, tabs (preview / dtypes / stats / missing).

Extracted from app.py to reduce main-page complexity.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components.ui_helpers import divider


def render_dataset_preview(df: pd.DataFrame) -> None:
    """Render the full dataset-preview section for *df*."""

    st.markdown("### 📊 Dataset Preview")

    # ---- metric cards ----
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Columns", f"{len(df.columns):,}")
    c3.metric("Missing Cells", f"{df.isnull().sum().sum():,}")
    c4.metric("Duplicate Rows", f"{df.duplicated().sum():,}")
    mem_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
    c5.metric("Memory", f"{mem_mb:.2f} MB")

    # ---- tabs ----
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

    divider()
