"""
Large Dataset reader component.
Supports: HDF5, Pickle, ZIP, TAR archives
"""
import streamlit as st
import pandas as pd
import zipfile
import tarfile
import pickle
import os
from pathlib import Path
from components.icon_utils import icon
from components.readers.upload_utils import persist_streamlit_upload


# ---------------------------------------------------------------------------
# HDF5
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Reading HDF5 file structure...")
def get_hdf5_structure(_file_path: str, _cache_key: str):
    """Extract HDF5 file structure (cached)."""
    try:
        import h5py

        with h5py.File(_file_path, "r") as hf:

            def _walk(group, prefix=""):
                items = []
                for key in group.keys():
                    item = group[key]
                    if isinstance(item, h5py.Dataset):
                        items.append(
                            {"Key": prefix + key, "Type": "Dataset", "Shape": str(item.shape), "Dtype": str(item.dtype)}
                        )
                    else:
                        items.extend(_walk(item, prefix + key + "/"))
                return items

            return {"success": True, "structure": _walk(hf)}
    except ImportError:
        return {"success": False, "error": "h5py not installed. Run: pip install h5py"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def read_hdf5_file(file_path: str, cache_key: str):
    """Read and display HDF5 file structure."""
    result = get_hdf5_structure(file_path, cache_key)
    if result["success"]:
        st.success("HDF5 file loaded!")
        st.dataframe(pd.DataFrame(result["structure"]), use_container_width=True)
    else:
        st.error(result["error"])


# ---------------------------------------------------------------------------
# Pickle
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Reading Pickle file...")
def get_pickle_data(_file_bytes):
    """Load Pickle file data (cached)."""
    try:
        data = pickle.loads(_file_bytes)
        result = {"success": True, "type": type(data).__name__}
        if isinstance(data, pd.DataFrame):
            result["is_dataframe"] = True
            result["shape"] = data.shape
            result["head"] = data.head(10)
        elif isinstance(data, dict):
            result["is_dict"] = True
            result["keys"] = list(data.keys())
            result["preview"] = str(data)[:5000]
        elif isinstance(data, (list, tuple)):
            result["is_sequence"] = True
            result["length"] = len(data)
            result["first_type"] = type(data[0]).__name__ if data else "N/A"
        else:
            result["preview"] = str(data)[:1000]
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def read_pickle_file(file_bytes):
    """Read and display Pickle file contents."""
    result = get_pickle_data(file_bytes)
    if not result["success"]:
        st.error(f"Error loading pickle: {result['error']}")
        return
    st.success("Pickle file loaded!")
    st.write(f"**Data type:** {result['type']}")
    if result.get("is_dataframe"):
        st.write(f"**Shape:** {result['shape']}")
        st.dataframe(result["head"], use_container_width=True)
    elif result.get("is_dict"):
        st.write(f"**Keys:** {result['keys']}")
        with st.expander("View Data"):
            st.json(result["preview"])
    elif result.get("is_sequence"):
        st.write(f"**Length:** {result['length']}")
        st.write(f"**First item type:** {result['first_type']}")
    else:
        st.write(result.get("preview", ""))


# ---------------------------------------------------------------------------
# ZIP
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Reading ZIP file contents...")
def get_zip_contents(_file_path: str, _cache_key: str):
    """Extract ZIP file contents info (cached)."""
    with zipfile.ZipFile(_file_path, "r") as zf:
        file_list = zf.namelist()
        file_info = []
        for f in file_list[:100]:
            info = zf.getinfo(f)
            file_info.append(
                {"Filename": f, "Size (KB)": round(info.file_size / 1024, 2), "Compressed (KB)": round(info.compress_size / 1024, 2)}
            )
        return {"total": len(file_list), "info": file_info}


def read_zip_file(file_path: str, cache_key: str):
    """Read and display ZIP file contents."""
    result = get_zip_contents(file_path, cache_key)
    st.success(f"ZIP file loaded! Contains {result['total']} files")
    st.dataframe(pd.DataFrame(result["info"]), use_container_width=True)
    if result["total"] > 100:
        st.info(f"Showing first 100 of {result['total']} files.")


# ---------------------------------------------------------------------------
# TAR
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Reading TAR file contents...")
def get_tar_contents(_file_path: str, _cache_key: str, file_ext: str, file_name: str):
    """Extract TAR file contents info (cached)."""
    mode = "r:gz" if ".gz" in file_name or file_ext == ".tgz" else "r"
    with tarfile.open(_file_path, mode) as tf:
        members = tf.getmembers()
        file_info = []
        for m in members[:100]:
            file_info.append({"Filename": m.name, "Size (KB)": round(m.size / 1024, 2), "Type": "Dir" if m.isdir() else "File"})
        return {"total": len(members), "info": file_info}


def read_tar_file(file_path: str, cache_key: str, file_ext: str, file_name: str):
    """Read and display TAR file contents."""
    result = get_tar_contents(file_path, cache_key, file_ext, file_name)
    st.success(f"TAR file loaded! Contains {result['total']} files")
    st.dataframe(pd.DataFrame(result["info"]), use_container_width=True)
    if result["total"] > 100:
        st.info(f"Showing first 100 of {result['total']} files.")


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------
def render_large_dataset_reader():
    """Render the large dataset reader UI."""
    st.markdown(f'<h3>{icon("box-archive")} Large Dataset Reader</h3>', unsafe_allow_html=True)
    st.write("Supported formats: HDF5, Pickle, ZIP, TAR")
    st.caption(
        "Large uploads are limited by Streamlit server settings and your machine resources. "
        "Even if upload is allowed (e.g., 2GB), loading huge files into RAM may crash the app."
    )

    uploaded_file = st.file_uploader(
        "Upload large dataset file",
        type=["h5", "hdf5", "pkl", "pickle", "zip", "tar", "tar.gz", "tgz"],
    )

    if uploaded_file is not None:
        file_ext = Path(uploaded_file.name).suffix.lower()
        file_name = uploaded_file.name.lower()
        file_path, cache_key = persist_streamlit_upload(uploaded_file, filename=uploaded_file.name)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

        try:
            if file_ext in [".h5", ".hdf5"]:
                read_hdf5_file(file_path, cache_key)
            elif file_ext in [".pkl", ".pickle"]:
                if file_size_mb > 200:
                    st.warning(f"Pickle file is {file_size_mb:.1f} MB. Loading it will consume a lot of RAM and may crash the app.")
                    if not st.checkbox("Load anyway (may be slow / crash)", value=False):
                        return
                with open(file_path, "rb") as f:
                    read_pickle_file(f.read())
            elif file_ext == ".zip":
                read_zip_file(file_path, cache_key)
            elif ".tar" in file_name or file_ext in [".tgz"]:
                read_tar_file(file_path, cache_key, file_ext, file_name)
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.info("Please upload a large dataset file.")
