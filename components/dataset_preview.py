"""
Dataset preview component — metric cards, tabs (preview / dtypes / stats / missing).

Extracted from app.py to reduce main-page complexity.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.ui_helpers import divider


def render_dataset_preview(df: pd.DataFrame) -> None:
    """Render the full dataset-preview section for *df*."""

    st.markdown("### Dataset Preview")

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

        # --- Visual statistics support ---
        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        if numeric_cols:
            st.markdown("#### Distribution Overview")

            # -- Histogram for selected column --
            sel_col = st.selectbox(
                "Select a column to visualize",
                numeric_cols,
                key="_stats_hist_col",
            )

            hist_col, box_col = st.columns(2)

            with hist_col:
                fig_hist = px.histogram(
                    df,
                    x=sel_col,
                    nbins=40,
                    title=f"Distribution of {sel_col}",
                    marginal="rug",
                    color_discrete_sequence=["#636EFA"],
                )
                fig_hist.update_layout(
                    height=360,
                    margin=dict(l=40, r=20, t=40, b=40),
                    bargap=0.05,
                )
                st.plotly_chart(fig_hist, use_container_width=True)

            with box_col:
                fig_box = px.box(
                    df,
                    y=sel_col,
                    title=f"Box Plot of {sel_col}",
                    points="outliers",
                    color_discrete_sequence=["#EF553B"],
                )
                fig_box.update_layout(
                    height=360,
                    margin=dict(l=40, r=20, t=40, b=40),
                )
                st.plotly_chart(fig_box, use_container_width=True)

            # -- Correlation heatmap (when ≥ 2 numeric columns) --
            if len(numeric_cols) >= 2:
                st.markdown("#### Correlation Heatmap")
                corr = df[numeric_cols].corr()
                fig_corr = go.Figure(
                    data=go.Heatmap(
                        z=corr.values,
                        x=corr.columns.tolist(),
                        y=corr.index.tolist(),
                        colorscale="RdBu_r",
                        zmin=-1,
                        zmax=1,
                        text=np.round(corr.values, 2),
                        texttemplate="%{text}",
                        hovertemplate="(%{x}, %{y}): %{z:.2f}<extra></extra>",
                    )
                )
                fig_corr.update_layout(
                    height=max(360, 30 * len(numeric_cols) + 120),
                    margin=dict(l=40, r=20, t=20, b=40),
                )
                st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info(
                "No numeric columns detected — statistical charts require at least one numeric feature.",
                icon=":material/info:",
            )

    with tab_missing:
        missing = df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=False)
        if missing.empty:
            st.success("No missing values detected!", icon=":material/check_circle:")
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
