"""
Image Segmentation dataset reader component.
Supports: Original images, mask images, and optional JSON metadata
"""
import streamlit as st
import json
from components.icon_utils import icon


def display_image_mask_pairs(original_images, mask_images, num_preview=3):
    """Display side-by-side image and mask previews."""
    with st.expander("Preview Image-Mask Pairs"):
        num_preview = min(num_preview, len(original_images), len(mask_images))
        for i in range(num_preview):
            cols = st.columns(2)
            with cols[0]:
                st.image(
                    original_images[i],
                    caption=f"Image: {original_images[i].name}",
                    use_container_width=True,
                )
            with cols[1]:
                st.image(
                    mask_images[i],
                    caption=f"Mask: {mask_images[i].name}",
                    use_container_width=True,
                )


def display_metadata(metadata_file):
    """Display JSON metadata."""
    try:
        metadata = json.load(metadata_file)
        with st.expander("Metadata"):
            st.json(metadata)
    except Exception as e:
        st.error(f"Error reading metadata: {e}")


def render_image_segmentation_reader():
    """Render the image segmentation dataset reader UI."""
    st.markdown(
        f'<h3>{icon("layer-group")} Image Segmentation Dataset Reader</h3>',
        unsafe_allow_html=True,
    )
    st.write("Upload images, mask images, and optional JSON metadata.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Original Images**")
        original_images = st.file_uploader(
            "Upload original images",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="seg_original",
        )
    with col2:
        st.write("**Mask Images**")
        mask_images = st.file_uploader(
            "Upload mask images",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="seg_masks",
        )
    with col3:
        st.write("**Metadata (Optional)**")
        metadata_file = st.file_uploader(
            "Upload JSON metadata",
            type=["json"],
            key="seg_metadata",
        )

    if original_images and mask_images:
        st.success(f"Loaded {len(original_images)} images and {len(mask_images)} masks")
        if len(original_images) != len(mask_images):
            st.warning(f"Mismatch: {len(original_images)} images vs {len(mask_images)} masks")
        display_image_mask_pairs(original_images, mask_images)
        if metadata_file:
            display_metadata(metadata_file)
    else:
        st.info("Please upload both original images and mask images.")
