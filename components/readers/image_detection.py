"""
Image Detection dataset reader component.
Supports: Images with COCO JSON, CSV, or YOLO TXT annotations
"""
import streamlit as st
import pandas as pd
import json
from components.icon_utils import icon


def parse_coco_annotations(annotation_file):
    """Parse COCO format JSON annotations."""
    return json.load(annotation_file)


def parse_csv_annotations(annotation_file):
    """Parse CSV format annotations."""
    return pd.read_csv(annotation_file)


def display_coco_summary(annotations):
    """Display COCO annotation summary."""
    st.write("**COCO Annotation Summary:**")
    if "categories" in annotations:
        st.write(f"- Categories: {len(annotations.get('categories', []))}")
    if "images" in annotations:
        st.write(f"- Images: {len(annotations.get('images', []))}")
    if "annotations" in annotations:
        st.write(f"- Annotations: {len(annotations.get('annotations', []))}")
    with st.expander("Categories"):
        if "categories" in annotations:
            cat_df = pd.DataFrame(annotations["categories"])
            st.dataframe(cat_df, use_container_width=True)


def display_csv_annotations(ann_df):
    """Display CSV annotations."""
    st.write("**Annotation DataFrame:**")
    st.dataframe(ann_df.head(20), use_container_width=True)
    st.write(f"Total annotations: {len(ann_df)}")


def render_image_detection_reader():
    """Render the image detection dataset reader UI."""
    st.markdown(
        f'<h3>{icon("crosshairs")} Image Detection Dataset Reader</h3>',
        unsafe_allow_html=True,
    )
    st.write("Upload images and their annotation files (CSV/JSON).")

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Images**")
        uploaded_images = st.file_uploader(
            "Upload images",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="detection_images",
        )
    with col2:
        st.write("**Annotations**")
        annotation_format = st.selectbox(
            "Annotation Format",
            ["COCO JSON", "CSV (filename,x,y,w,h,label)", "YOLO TXT"],
        )
        annotation_file = st.file_uploader(
            "Upload annotation file",
            type=["json", "csv", "txt"],
            key="detection_annotations",
        )

    if uploaded_images and annotation_file:
        st.success(f"Loaded {len(uploaded_images)} images")
        try:
            if annotation_format == "COCO JSON":
                annotations = parse_coco_annotations(annotation_file)
                display_coco_summary(annotations)
            elif annotation_format == "CSV (filename,x,y,w,h,label)":
                ann_df = parse_csv_annotations(annotation_file)
                display_csv_annotations(ann_df)
        except Exception as e:
            st.error(f"Error reading annotations: {e}")
    elif uploaded_images:
        st.info("Please upload annotation file.")
    else:
        st.info("Please upload images and annotations.")
