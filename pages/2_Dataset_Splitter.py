"""
Dataset Splitter Page
Split a folder-structured image dataset into train / validation / test sets.
"""
import streamlit as st
from pathlib import Path

from components.icon_utils import load_fontawesome, icon
from components.styles import inject_custom_css
from utils.splitter import split_dataset

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dataset Splitter",
    page_icon=":material/content_cut:",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()
load_fontawesome()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    f'<h1>{icon("scissors", "icon-title")} Dataset Splitter</h1>',
    unsafe_allow_html=True,
)
st.caption(
    "Split a folder-structured image dataset into **train / validation / test** sets. "
    "Each sub-folder is treated as a class label."
)

st.divider()

# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    input_dir = st.text_input(
        "Path to dataset folder",
        placeholder="/path/to/dataset",
        help="Root folder containing one sub-folder per class.",
    )
with col2:
    output_dir = st.text_input(
        "Output folder",
        value="output",
        help="Destination for the train/val/test folders.",
    )

st.markdown("##### Split Ratios")
r1, r2, r3 = st.columns(3)
with r1:
    train_ratio = st.slider("Train %", 0.50, 0.90, 0.70, step=0.05)
with r2:
    val_ratio = st.slider("Validation %", 0.05, 0.40, 0.20, step=0.05)
test_ratio = round(1.0 - train_ratio - val_ratio, 2)
with r3:
    st.metric("Test %", f"{test_ratio:.0%}")

st.divider()

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if st.button("Split Dataset", icon=":material/rocket_launch:", type="primary"):
    if test_ratio < 0:
        st.error("Ratios exceed 100 %. Adjust Train and Validation sliders.")
    elif not input_dir or not Path(input_dir).exists():
        st.error("Input path does not exist.")
    else:
        with st.spinner("Splitting dataset …"):
            split_dataset(input_dir, output_dir, train_ratio, val_ratio, test_ratio)
        st.success("Dataset split successfully!", icon=":material/check_circle:")

        # Show output summary
        out_path = Path(output_dir)
        if out_path.exists():
            for split_name in ["train", "val", "test"]:
                split_dir = out_path / split_name
                if split_dir.exists():
                    classes = [d.name for d in split_dir.iterdir() if d.is_dir()]
                    total = sum(len(list((split_dir / c).glob("*"))) for c in classes)
                    st.write(f"**{split_name.capitalize()}**: {len(classes)} classes, {total} files")
