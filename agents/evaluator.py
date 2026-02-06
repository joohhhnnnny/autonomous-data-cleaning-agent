from utils.llm import llm

def evaluate_data_quality(dataset_info: dict, analysis: str, recommendations: str, strategy_context: str = ""):
    """Evaluate the overall data quality and the proposed cleaning strategies."""
    
    prompt = f"""
You are a data quality assessor. Evaluate the dataset's overall quality and the proposed cleaning strategies.

STRATEGY CONTEXT (for comparison with past evaluations):
{strategy_context}

Provide:
1. Overall Data Quality Score (0-100)
   - Completeness score (0-100)
   - Consistency score (0-100)
   - Accuracy score (0-100)
   - Validity score (0-100)

2. Risk Assessment
   - Critical issues that must be addressed
   - Issues that can be deferred
   - Potential data loss from cleaning

3. Strategy Evaluation
   - Are the recommendations comprehensive?
   - Are there any missed issues?
   - Are the strategies appropriate for the data type?

4. Estimated Impact
   - Rows likely to be affected
   - Data quality improvement prediction
   - Time/effort estimation

5. Next Steps
   - Recommended order of operations
   - Additional analysis needed

DATASET INFO:
File: {dataset_info['file_name']}
Rows: {dataset_info['rows']}
Columns: {dataset_info['columns']}
Missing Values: {dataset_info['missing_values']}
Duplicates: {dataset_info['duplicates']}

ANALYSIS:
{analysis}

RECOMMENDATIONS:
{recommendations}

Provide a comprehensive quality assessment.
"""
    return llm.invoke(prompt)
