from utils.llm import llm
from utils.postprocess import strip_model_preamble

def recommend_cleaning_strategies(dataset_info: dict, analysis: str, strategy_context: str = ""):
    """Generate specific, actionable data cleaning recommendations."""
    
    prompt = f"""
You are a data cleaning expert. Based on the dataset analysis, provide specific, actionable cleaning strategies.

STRATEGY CONTEXT (reference similar past strategies):
{strategy_context}

For each identified issue, provide:
1. Priority level (Critical/High/Medium/Low)
2. Specific cleaning method (imputation, removal, transformation, etc.)
3. Python/Pandas code snippet if applicable
4. Expected impact on data quality
5. Potential risks or considerations

Organize recommendations by category:
- Missing Data Handling
- Duplicate Removal
- Data Type Corrections
- Outlier Treatment
- Formatting Standardization
- Validation Rules

Formatting requirements:
- Return ONLY the recommendations.
- Be specific and actionable.
- Include code examples where helpful.

DATASET INFO:
File: {dataset_info['file_name']}
Rows: {dataset_info['rows']}
Columns: {dataset_info['columns']}

ANALYSIS RESULTS:
{analysis}

Provide comprehensive cleaning strategies.
"""
    return strip_model_preamble(llm.invoke(prompt))
