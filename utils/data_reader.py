"""Utility module for reading and analyzing datasets."""

import pandas as pd
from pathlib import Path
from typing import Dict


def read_dataset(file_path: str) -> pd.DataFrame:
    """
    Read a dataset from CSV or XLSX file.
    
    Args:
        file_path: Path to the dataset file
        
    Returns:
        pandas DataFrame containing the dataset
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    if suffix == '.csv':
        # Try different encodings for CSV
        try:
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin-1')
    elif suffix == '.tsv':
        try:
            df = pd.read_csv(file_path, sep='\t')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, sep='\t', encoding='latin-1')
    elif suffix in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    elif suffix == '.parquet':
        df = pd.read_parquet(file_path)
    elif suffix == '.json':
        df = pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    return df


def get_dataset_info(df: pd.DataFrame, file_path: str) -> Dict:
    """
    Extract comprehensive information about the dataset.
    
    Args:
        df: pandas DataFrame
        file_path: Original file path
        
    Returns:
        Dictionary containing dataset information
    """
    # Basic info
    info = {
        'file_name': Path(file_path).name,
        'rows': len(df),
        'columns': len(df.columns),
        'column_names': list(df.columns),
    }
    
    # Data types
    dtypes_str = "\n".join([f"  {col}: {dtype}" for col, dtype in df.dtypes.items()])
    info['dtypes'] = dtypes_str
    
    # Missing values
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_info = []
    for col in df.columns:
        if missing[col] > 0:
            missing_info.append(f"  {col}: {missing[col]} ({missing_pct[col]}%)")
    
    if missing_info:
        info['missing_values'] = "\n".join(missing_info)
    else:
        info['missing_values'] = "  None"
    
    # Duplicates
    info['duplicates'] = df.duplicated().sum()
    
    # Memory usage
    memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
    info['memory_usage'] = f"{memory_mb:.2f} MB"
    
    # Sample data (first 5 rows)
    info['head'] = df.head(5).to_string()
    
    # Basic statistics
    try:
        stats = df.describe(include='all').to_string()
        info['statistics'] = stats
    except Exception:
        info['statistics'] = "Unable to generate statistics"
    
    # Additional checks
    info['numeric_columns'] = list(df.select_dtypes(include=['int64', 'float64']).columns)
    info['categorical_columns'] = list(df.select_dtypes(include=['object', 'category']).columns)
    info['datetime_columns'] = list(df.select_dtypes(include=['datetime64']).columns)
    
    return info
