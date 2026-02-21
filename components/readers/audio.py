"""
Audio/Speech dataset reader component.
Supports: WAV, MP3, OGG, FLAC with optional labels
"""
import streamlit as st
import pandas as pd
from components.icon_utils import icon


def get_audio_info(audio_files):
    """Get information about uploaded audio files."""
    audio_info = []
    for af in audio_files:
        audio_info.append({"Filename": af.name, "Size (KB)": round(af.size / 1024, 2)})
    return pd.DataFrame(audio_info)


def display_audio_preview(audio_files, max_preview=5):
    """Display audio file previews."""
    with st.expander("Preview Audio Files"):
        for af in audio_files[:max_preview]:
            st.write(f"**{af.name}**")
            st.audio(af)


def parse_label_file(label_file):
    """Parse audio label file (CSV or TXT)."""
    if label_file.name.endswith(".csv"):
        return pd.read_csv(label_file)
    else:
        return pd.read_csv(label_file, delimiter="\t", header=None, names=["filename", "label"])


def render_audio_reader():
    """Render the audio/speech dataset reader UI."""
    st.markdown(
        f'<h3>{icon("music")} Audio / Speech Dataset Reader</h3>',
        unsafe_allow_html=True,
    )
    st.write("Upload audio files and their labels.")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Audio Files**")
        audio_files = st.file_uploader(
            "Upload audio files",
            type=["wav", "mp3", "ogg", "flac"],
            accept_multiple_files=True,
            key="audio_files",
        )

    with col2:
        st.write("**Labels (Optional)**")
        label_file = st.file_uploader(
            "Upload labels (CSV/TXT)",
            type=["csv", "txt"],
            key="audio_labels",
        )

    if audio_files:
        st.success(f"Loaded {len(audio_files)} audio files")

        audio_info_df = get_audio_info(audio_files)
        st.dataframe(audio_info_df, use_container_width=True)

        display_audio_preview(audio_files)

        if label_file:
            try:
                labels_df = parse_label_file(label_file)
                st.write("**Labels:**")
                st.dataframe(labels_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error reading labels: {e}")
    else:
        st.info("Please upload audio files.")
