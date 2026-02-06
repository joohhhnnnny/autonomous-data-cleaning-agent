from utils.llm import llm

def analyze_dataset(dataset_info: dict, strategy_context: str = ""):
    """Analyze dataset for anomalies, missing values, duplicates, outliers, etc."""
    
    prompt = f"""
You are a data quality analyst. Analyze the dataset information and identify all data quality issues.

Focus on:
1. Missing values (null, NaN, empty strings) - identify patterns and severity
2. Duplicate records - check for exact and partial duplicates
3. Data type inconsistencies - incorrect types for columns
4. Outliers and anomalies - statistical outliers, unrealistic values
5. Formatting issues - inconsistent date formats, string casing, whitespace
6. Referential integrity - relationships between columns
7. Data range issues - values outside expected ranges

If STRATEGY CONTEXT is provided, reference similar issues found in past analyses.

STRATEGY CONTEXT:
{strategy_context}

DATASET INFORMATION:
File: {dataset_info['file_name']}
Rows: {dataset_info['rows']}
Columns: {dataset_info['columns']}
Column Names: {dataset_info['column_names']}
Data Types: {dataset_info['dtypes']}
Missing Values: {dataset_info['missing_values']}
Duplicate Rows: {dataset_info['duplicates']}
Memory Usage: {dataset_info['memory_usage']}

Sample Data (first 5 rows):
{dataset_info['head']}

Basic Statistics:
{dataset_info['statistics']}

Provide a detailed analysis of all data quality issues found.
"""
    return llm.invoke(prompt)
