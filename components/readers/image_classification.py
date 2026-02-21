"""
Image Classification dataset reader component.
Supports: ZIP/TAR archives with folder structure, individual images, local folder paths
"""
import streamlit as st
import pandas as pd
import zipfile
import tarfile
import base64
import matplotlib.pyplot as plt
from pathlib import Path
from io import BytesIO
from components.icon_utils import icon
from components.readers.upload_utils import persist_streamlit_upload


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif", ".tiff"}
SPLIT_FOLDERS = {"train", "test", "val", "validation", "valid"}


# ---------------------------------------------------------------------------
# Chart helpers
# ---------------------------------------------------------------------------
def create_bar_chart_image(class_df, title="Class Distribution"):
    """Create a bar chart as a downloadable PNG image buffer."""
    fig, ax = plt.subplots(figsize=(10, max(6, len(class_df) * 0.3)))
    colors = plt.cm.viridis([i / len(class_df) for i in range(len(class_df))])
    bars = ax.barh(class_df["Class"], class_df["Image Count"], color=colors)

    ax.set_xlabel("Image Count")
    ax.set_ylabel("Class")
    ax.set_title(title)
    ax.invert_yaxis()

    for bar, count in zip(bars, class_df["Image Count"]):
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            str(count),
            va="center",
            fontsize=8,
        )

    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf


def download_button_with_icon(data, file_name, button_text="Download Chart", icon_name="download"):
    """Create a download button with Font Awesome icon using HTML."""
    if isinstance(data, BytesIO):
        data = data.getvalue()
    b64 = base64.b64encode(data).decode()
    button_html = f"""
    <a href="data:image/png;base64,{b64}" download="{file_name}"
       style="display: inline-flex; align-items: center; padding: 0.4rem 0.8rem;
              background-color: #262730; color: white; text-decoration: none;
              border-radius: 0.5rem; font-size: 14px; border: 1px solid #4a4a5a;
              transition: background-color 0.2s, border-color 0.2s;">
        <i class="fa-solid fa-{icon_name}" style="margin-right: 8px;"></i>{button_text}
    </a>
    """
    st.markdown(button_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Archive processing (cached)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Processing ZIP archive...")
def process_zip_archive(_archive_path: str, _cache_key: str):
    """Process ZIP archive and extract dataset structure (cached)."""
    dataset_structure = {}
    with zipfile.ZipFile(_archive_path, "r") as zf:
        for file_path in zf.namelist():
            if not any(file_path.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                continue
            parts = [p for p in file_path.split("/") if p]
            if len(parts) >= 3:
                potential_split = class_name = None
                for i, part in enumerate(parts[:-1]):
                    if part.lower() in SPLIT_FOLDERS:
                        potential_split = part.lower()
                        if potential_split == "valid":
                            potential_split = "validation"
                        if i + 1 < len(parts) - 1:
                            class_name = parts[i + 1]
                        break
                if potential_split and class_name:
                    dataset_structure.setdefault(potential_split, {}).setdefault(class_name, []).append(file_path)
                    continue
            if len(parts) >= 2:
                class_name = parts[-2]
                if class_name.lower() not in SPLIT_FOLDERS and class_name.lower() not in ["images", "data"]:
                    dataset_structure.setdefault("all", {}).setdefault(class_name, []).append(file_path)
                    continue
            if len(parts) == 1:
                dataset_structure.setdefault("all", {}).setdefault("uncategorized", []).append(file_path)
    return dataset_structure


@st.cache_data(show_spinner="Processing TAR archive...")
def process_tar_archive(_archive_path: str, _cache_key: str, file_ext: str, file_name: str):
    """Process TAR archive and extract dataset structure (cached)."""
    dataset_structure = {}
    mode = "r:gz" if ".gz" in file_name or file_ext == ".tgz" else "r"
    with tarfile.open(_archive_path, mode) as tf:
        for member in tf.getmembers():
            if not member.isfile():
                continue
            if not any(member.name.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                continue
            file_path = member.name
            parts = [p for p in file_path.split("/") if p]
            if len(parts) >= 3:
                potential_split = class_name = None
                for i, part in enumerate(parts[:-1]):
                    if part.lower() in SPLIT_FOLDERS:
                        potential_split = part.lower()
                        if potential_split == "valid":
                            potential_split = "validation"
                        if i + 1 < len(parts) - 1:
                            class_name = parts[i + 1]
                        break
                if potential_split and class_name:
                    dataset_structure.setdefault(potential_split, {}).setdefault(class_name, []).append(file_path)
                    continue
            if len(parts) >= 2:
                class_name = parts[-2]
                if class_name.lower() not in SPLIT_FOLDERS and class_name.lower() not in ["images", "data"]:
                    dataset_structure.setdefault("all", {}).setdefault(class_name, []).append(file_path)
                    continue
            if len(parts) == 1:
                dataset_structure.setdefault("all", {}).setdefault("uncategorized", []).append(file_path)
    return dataset_structure


@st.cache_data(show_spinner=False)
def read_zip_image(_archive_path: str, _cache_key: str, member_path: str) -> bytes:
    with zipfile.ZipFile(_archive_path, "r") as zf:
        return zf.read(member_path)


@st.cache_data(show_spinner=False)
def read_tar_image(_archive_path: str, _cache_key: str, file_ext: str, file_name: str, member_path: str) -> bytes:
    mode = "r:gz" if ".gz" in file_name or file_ext == ".tgz" else "r"
    with tarfile.open(_archive_path, mode) as tf:
        member = tf.getmember(member_path)
        extracted = tf.extractfile(member)
        if extracted is None:
            raise FileNotFoundError(member_path)
        return extracted.read()


@st.cache_data(show_spinner="Scanning local folder...")
def scan_local_folder_cached(folder_path_str):
    """Scan local folder for image classification structure (cached)."""
    folder_path = Path(folder_path_str)
    classes = {}
    for class_folder in folder_path.iterdir():
        if class_folder.is_dir():
            class_name = class_folder.name
            if class_name.startswith(".") or class_name.lower() in [
                "train", "test", "val", "validation", "images", "data", "__pycache__",
            ]:
                continue
            images = [
                str(img) for img in class_folder.iterdir()
                if img.is_file() and img.suffix.lower() in IMAGE_EXTENSIONS
            ]
            if images:
                classes[class_name] = images
    if not classes:
        for split_folder in folder_path.iterdir():
            if split_folder.is_dir() and split_folder.name.lower() in ["train", "test", "val", "validation"]:
                for class_folder in split_folder.iterdir():
                    if class_folder.is_dir() and not class_folder.name.startswith("."):
                        images = [
                            str(img) for img in class_folder.iterdir()
                            if img.is_file() and img.suffix.lower() in IMAGE_EXTENSIONS
                        ]
                        if images:
                            classes.setdefault(class_folder.name, []).extend(images)
    return classes


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------
def display_split_view(dataset_structure, read_image_func):
    """Display dataset with splits (train/test/val)."""
    st.markdown(
        '<h4><i class="fa-solid fa-sitemap" style="margin-right: 8px;"></i>Dataset Splits</h4>',
        unsafe_allow_html=True,
    )
    split_summary = []
    for split_name in ["train", "test", "val", "validation"]:
        if split_name in dataset_structure:
            split_data = dataset_structure[split_name]
            split_images = sum(len(v) for v in split_data.values())
            split_summary.append({"Split": split_name.capitalize(), "Classes": len(split_data), "Images": split_images})
    if split_summary:
        st.dataframe(pd.DataFrame(split_summary), use_container_width=True, hide_index=True)
    split_names = [s for s in ["train", "test", "val", "validation"] if s in dataset_structure]
    if split_names:
        tabs = st.tabs([s.capitalize() for s in split_names])
        for tab, split_name in zip(tabs, split_names):
            with tab:
                split_data = dataset_structure[split_name]
                class_df = pd.DataFrame(
                    {"Class": list(split_data.keys()), "Image Count": [len(v) for v in split_data.values()]}
                ).sort_values("Image Count", ascending=False)
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(class_df, use_container_width=True, hide_index=True)
                with col2:
                    st.bar_chart(class_df.set_index("Class")["Image Count"])
                    chart_buf = create_bar_chart_image(class_df, f"{split_name.capitalize()} Class Distribution")
                    download_button_with_icon(chart_buf, f"{split_name}_class_distribution.png", "Download Chart", "download")
                with st.expander(f"Preview {split_name.capitalize()} Images"):
                    selected_class = st.selectbox("Select class", sorted(list(split_data.keys())), key=f"class_select_{split_name}")
                    sample_images = split_data[selected_class][:10]
                    num_to_show = st.slider("Number of images", 1, min(10, len(sample_images)), 5, key=f"num_preview_{split_name}")
                    cols = st.columns(5)
                    for i, img_path in enumerate(sample_images[:num_to_show]):
                        with cols[i % 5]:
                            st.image(read_image_func(img_path), caption=Path(img_path).name, use_container_width=True)


def display_unified_view(classes, read_image_func=None, is_local=False):
    """Display dataset without splits (unified view)."""
    class_df = pd.DataFrame(
        {"Class": list(classes.keys()), "Image Count": [len(v) for v in classes.values()]}
    ).sort_values("Image Count", ascending=False)
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(class_df, use_container_width=True, hide_index=True)
    with col2:
        st.bar_chart(class_df.set_index("Class")["Image Count"])
        chart_buf = create_bar_chart_image(class_df, "Class Distribution")
        download_button_with_icon(chart_buf, "class_distribution.png", "Download Chart", "download")
    with st.expander("Preview Sample Images"):
        key_suffix = "local" if is_local else "archive"
        selected_class = st.selectbox("Select class to preview", sorted(list(classes.keys())), key=f"class_select_{key_suffix}")
        sample_images = classes[selected_class][:10]
        num_to_show = st.slider("Number of images to preview", 1, min(10, len(sample_images)), 5, key=f"num_preview_{key_suffix}")
        cols = st.columns(5)
        for i, img_path in enumerate(sample_images[:num_to_show]):
            with cols[i % 5]:
                if is_local:
                    st.image(img_path, caption=Path(img_path).name, use_container_width=True)
                else:
                    st.image(read_image_func(img_path), caption=Path(img_path).name, use_container_width=True)


def display_dataset_statistics(dataset_structure, total_images, all_classes, has_splits):
    """Display dataset statistics in an expander."""
    with st.expander("Dataset Statistics"):
        st.write(f"- **Total Classes:** {len(all_classes)}")
        st.write(f"- **Total Images:** {total_images}")
        if has_splits:
            st.write("- **Splits:**")
            for split_name, split_data in dataset_structure.items():
                split_images = sum(len(v) for v in split_data.values())
                st.write(f"  - {split_name.capitalize()}: {split_images} images ({len(split_data)} classes)")
        else:
            classes = dataset_structure.get("all", {})
            if classes:
                st.write(f"- **Average Images per Class:** {total_images / len(classes):.1f}")
                st.write(f"- **Min Images in a Class:** {min(len(v) for v in classes.values())}")
                st.write(f"- **Max Images in a Class:** {max(len(v) for v in classes.values())}")


def display_folder_structure(dataset_structure):
    """Display folder structure visualization."""
    with st.expander("View Folder Structure"):
        structure_html = ""
        for split_name, split_data in sorted(dataset_structure.items()):
            if split_name != "all":
                split_images = sum(len(v) for v in split_data.values())
                structure_html += f'<p><i class="fa-solid fa-folder-open" style="color: #4a9eff;"></i> <strong>{split_name}/</strong> ({split_images} images)</p>'
            for class_name, images in sorted(split_data.items()):
                indent = "margin-left: 20px;" if split_name != "all" else ""
                structure_html += f'<p style="{indent}"><i class="fa-solid fa-folder" style="color: #f0c36d;"></i> <strong>{class_name}/</strong> ({len(images)} images)</p>'
                for img in images[:3]:
                    structure_html += f'<p style="margin-left: {"40px" if split_name != "all" else "20px"};">\u2514\u2500\u2500 {Path(img).name}</p>'
                if len(images) > 3:
                    structure_html += f'<p style="margin-left: {"40px" if split_name != "all" else "20px"};">\u2514\u2500\u2500 ... and {len(images) - 3} more</p>'
        st.markdown(structure_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Upload-mode renderers
# ---------------------------------------------------------------------------
def render_archive_upload():
    """Render ZIP/TAR archive upload interface."""
    st.caption(
        "Note: browser uploads are limited by Streamlit server settings and available RAM. "
        "For multi-GB datasets, prefer 'Local Folder Path' when possible."
    )
    uploaded_archive = st.file_uploader("Upload ZIP or TAR file", type=["zip", "tar", "gz", "tgz"])
    if uploaded_archive is not None:
        file_ext = Path(uploaded_archive.name).suffix.lower()
        file_name = uploaded_archive.name.lower()
        archive_path, archive_md5 = persist_streamlit_upload(uploaded_archive, filename=uploaded_archive.name)
        try:
            if file_ext == ".zip":
                dataset_structure = process_zip_archive(archive_path, archive_md5)
                read_image_func = lambda p: read_zip_image(archive_path, archive_md5, p)
            elif ".tar" in file_name or file_ext == ".tgz":
                dataset_structure = process_tar_archive(archive_path, archive_md5, file_ext, file_name)
                read_image_func = lambda p: read_tar_image(archive_path, archive_md5, file_ext, file_name, p)
            else:
                st.error(f"Unsupported archive format: {file_ext}")
                return
            if dataset_structure:
                total_images = sum(len(imgs) for sd in dataset_structure.values() for imgs in sd.values())
                all_classes = set()
                for sd in dataset_structure.values():
                    all_classes.update(sd.keys())
                has_splits = len(dataset_structure) > 1 or "all" not in dataset_structure
                st.success(f"Found {len(all_classes)} classes with {total_images} total images")
                if has_splits:
                    display_split_view(dataset_structure, read_image_func)
                else:
                    display_unified_view(dataset_structure.get("all", {}), read_image_func, is_local=False)
                display_dataset_statistics(dataset_structure, total_images, all_classes, has_splits)
                display_folder_structure(dataset_structure)
            else:
                st.warning("No valid image folder structure found in archive.")
                st.info("Expected structure: archive/class_name/image.jpg or archive/split/class_name/image.jpg")
        except Exception as e:
            st.error(f"Error reading archive: {e}")


def render_local_folder():
    """Render local folder path interface."""
    st.write("Enter the path to your local dataset folder.")
    st.info("Expected structure: `dataset_folder/class_name/image.jpg`")
    folder_path = st.text_input("Enter folder path", placeholder="/path/to/your/dataset")
    if folder_path and st.button("Load Dataset"):
        folder_path_obj = Path(folder_path)
        if not folder_path_obj.exists():
            st.error(f"Folder does not exist: {folder_path_obj}")
        elif not folder_path_obj.is_dir():
            st.error(f"Path is not a directory: {folder_path_obj}")
        else:
            try:
                classes = scan_local_folder_cached(folder_path)
                if classes:
                    total_images = sum(len(v) for v in classes.values())
                    st.success(f"Found {len(classes)} classes with {total_images} total images")
                    st.session_state["cv_classes"] = classes
                    st.session_state["cv_folder_path"] = folder_path
                    display_unified_view(classes, is_local=True)
                    with st.expander("Dataset Statistics"):
                        st.write(f"- **Total Classes:** {len(classes)}")
                        st.write(f"- **Total Images:** {total_images}")
                        st.write(f"- **Average Images per Class:** {total_images / len(classes):.1f}")
                        st.write(f"- **Min Images in a Class:** {min(len(v) for v in classes.values())}")
                        st.write(f"- **Max Images in a Class:** {max(len(v) for v in classes.values())}")
                    with st.expander("View Folder Structure"):
                        structure_html = ""
                        for class_name, images in sorted(classes.items()):
                            structure_html += f'<p><i class="fa-solid fa-folder" style="color: #f0c36d;"></i> <strong>{class_name}/</strong> ({len(images)} images)</p>'
                            for img in images[:3]:
                                structure_html += f'<p style="margin-left: 20px;">\u2514\u2500\u2500 {Path(img).name}</p>'
                            if len(images) > 3:
                                structure_html += f'<p style="margin-left: 20px;">\u2514\u2500\u2500 ... and {len(images) - 3} more</p>'
                        st.markdown(structure_html, unsafe_allow_html=True)
                else:
                    st.warning("No valid image folder structure found.")
                    st.info("Expected structure: `folder/class_name/image.jpg`")
            except Exception as e:
                st.error(f"Error reading folder: {e}")
    elif "cv_classes" in st.session_state and st.session_state.get("cv_folder_path") == folder_path:
        classes = st.session_state["cv_classes"]
        total_images = sum(len(v) for v in classes.values())
        st.success(f"Loaded {len(classes)} classes with {total_images} total images")


def render_individual_images():
    """Render individual images upload interface."""
    uploaded_images = st.file_uploader(
        "Upload images",
        type=["jpg", "jpeg", "png", "gif", "bmp", "webp"],
        accept_multiple_files=True,
    )
    if uploaded_images:
        st.success(f"Uploaded {len(uploaded_images)} images")
        cols = st.columns(min(5, len(uploaded_images)))
        for i, img in enumerate(uploaded_images[:10]):
            with cols[i % 5]:
                st.image(img, caption=img.name, use_container_width=True)
        if len(uploaded_images) > 10:
            st.info(f"Showing first 10 of {len(uploaded_images)} images.")


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------
def render_image_classification_reader():
    """Render the image classification dataset reader UI."""
    st.markdown(f'<h3>{icon("images")} Image Classification Dataset Reader</h3>', unsafe_allow_html=True)
    st.write("Upload a ZIP/TAR archive containing folders per class, or individual images.")
    st.info("For Computer Vision training: Organize your dataset as folders where each folder name is a class label containing images of that class.")
    upload_mode = st.radio("Upload Mode", ["ZIP/TAR Archive (folders per class)", "Individual Images", "Local Folder Path"])
    if upload_mode == "ZIP/TAR Archive (folders per class)":
        render_archive_upload()
    elif upload_mode == "Local Folder Path":
        render_local_folder()
    else:
        render_individual_images()
