"""
Tabular/ML dataset reader component.
Supports: CSV, TSV, XLSX, JSON, Parquet, TXT
"""
import streamlit as st
import pandas as pd
import hashlib
from pathlib import Path
from components.icon_utils import icon


def get_file_hash(uploaded_file):
    """Generate a hash for the uploaded file to use as cache key."""
    file_bytes = uploaded_file.getvalue()
    return hashlib.md5(file_bytes).hexdigest()


@st.cache_data(show_spinner="Reading CSV file...")
def read_csv_file(_file_bytes, delimiter=","):
    """Read CSV file with custom delimiter (cached)."""
    from io import BytesIO
    return pd.read_csv(BytesIO(_file_bytes), delimiter=delimiter)


@st.cache_data(show_spinner="Reading TSV file...")
def read_tsv_file(_file_bytes):
    """Read TSV file (cached)."""
    from io import BytesIO
    return pd.read_csv(BytesIO(_file_bytes), delimiter="\t")


@st.cache_data(show_spinner="Reading Excel file...")
def read_excel_file(_file_bytes, sheet_name=None):
    """Read Excel file with optional sheet name (cached)."""
    from io import BytesIO
    return pd.read_excel(BytesIO(_file_bytes), sheet_name=sheet_name if sheet_name else 0)


@st.cache_data(show_spinner="Reading JSON file...")
def read_json_file(_file_bytes, orient="records"):
    """Read JSON file with specified orientation (cached)."""
    from io import BytesIO
    return pd.read_json(BytesIO(_file_bytes), orient=orient)


@st.cache_data(show_spinner="Reading Parquet file...")
def read_parquet_file(_file_bytes):
    """Read Parquet file (cached)."""
    from io import BytesIO
    return pd.read_parquet(BytesIO(_file_bytes))


@st.cache_data(show_spinner="Reading TXT file...")
def read_txt_file(_file_bytes, delimiter=","):
    """Read TXT file with custom delimiter (cached)."""
    from io import BytesIO
    return pd.read_csv(BytesIO(_file_bytes), delimiter=delimiter)


def display_dataframe_info(df):
    """Display DataFrame metrics and preview."""
    st.success(f"Dataset loaded! Shape: {df.shape}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rows", df.shape[0])
    with col2:
        st.metric("Columns", df.shape[1])

    st.write("**Preview (first 10 rows):**")
    st.dataframe(df.head(10), use_container_width=True)

    with st.expander("Column Information"):
        col_info = pd.DataFrame(
            {
                "Column": df.columns,
                "Type": df.dtypes.values,
                "Non-Null": df.count().values,
                "Null": df.isnull().sum().values,
            }
        )
        st.dataframe(col_info, use_container_width=True)

    with st.expander("Summary Statistics"):
        st.write(df.describe(include="all"))


def render_tabular_reader():
    """Render the tabular dataset reader UI."""
    st.markdown(f'<h3>{icon("table")} Tabular Data Reader</h3>', unsafe_allow_html=True)
    st.write("Supported formats: CSV, TSV, XLSX, JSON, Parquet, TXT")

    uploaded_file = st.file_uploader(
        "Upload your tabular dataset",
        type=["csv", "tsv", "xlsx", "xls", "json", "parquet", "txt"],
    )

    if uploaded_file is not None:
        file_ext = Path(uploaded_file.name).suffix.lower()
        file_bytes = uploaded_file.getvalue()

        try:
            df = None

            if file_ext == ".csv":
                delimiter = st.text_input("CSV Delimiter", ",")
                df = read_csv_file(file_bytes, delimiter=delimiter)
            elif file_ext == ".tsv":
                df = read_tsv_file(file_bytes)
            elif file_ext in [".xlsx", ".xls"]:
                sheet_name = st.text_input("Sheet name (leave empty for first sheet)", "")
                df = read_excel_file(file_bytes, sheet_name=sheet_name)
            elif file_ext == ".json":
                json_orient = st.selectbox(
                    "JSON Orient",
                    ["records", "columns", "index", "split", "table"],
                )
                df = read_json_file(file_bytes, orient=json_orient)
            elif file_ext == ".parquet":
                df = read_parquet_file(file_bytes)
            elif file_ext == ".txt":
                delimiter = st.text_input("TXT Delimiter", ",")
                df = read_txt_file(file_bytes, delimiter=delimiter)
            else:
                st.error(f"Unsupported file format: {file_ext}")

            if df is not None:
                display_dataframe_info(df)

        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.info("Please upload a tabular dataset file.")
