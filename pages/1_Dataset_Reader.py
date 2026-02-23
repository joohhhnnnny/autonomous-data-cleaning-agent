"""
Dataset Reader Page
Provides UI for reading various dataset types including tabular, image, audio,
and large datasets.
"""
import streamlit as st
from components.icon_utils import load_fontawesome, icon
from components.styles import inject_custom_css
from components.readers import (
    render_tabular_reader,
    render_image_classification_reader,
    render_image_detection_reader,
    render_image_segmentation_reader,
    render_audio_reader,
    render_large_dataset_reader,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dataset Reader",
    page_icon=":material/folder_open:",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()
load_fontawesome()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(f'<h1>{icon("folder", "icon-title")} Dataset Reader</h1>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Dataset type selection
# ---------------------------------------------------------------------------
dataset_type = st.selectbox(
    "Select Dataset Type",
    [
        "Tabular / ML (CSV, TSV, XLSX, JSON, Parquet, TXT)",
        "Image Classification (JPG, PNG, ZIP folder)",
        "Image Detection (Images + Annotations)",
        "Image Segmentation (Images + Masks + JSON)",
        "Audio / Speech (WAV, MP3 + Labels)",
        "Large Datasets (HDF5, Pickle, ZIP/TAR)",
    ],
)

st.divider()

# ---------------------------------------------------------------------------
# Route to appropriate reader
# ---------------------------------------------------------------------------
if dataset_type.startswith("Tabular"):
    render_tabular_reader()

elif dataset_type.startswith("Image Classification"):
    render_image_classification_reader()

elif dataset_type.startswith("Image Detection"):
    render_image_detection_reader()

elif dataset_type.startswith("Image Segmentation"):
    render_image_segmentation_reader()

elif dataset_type.startswith("Audio"):
    render_audio_reader()

elif dataset_type.startswith("Large Datasets"):
    render_large_dataset_reader()
