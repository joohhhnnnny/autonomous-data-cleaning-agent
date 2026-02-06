import os

from agents.analyzer import analyze_dataset
from agents.rewriter import recommend_cleaning_strategies
from agents.evaluator import evaluate_data_quality
from utils.data_reader import read_dataset, get_dataset_info
from utils.rag import retrieve_strategy_context

def clean_dataset(file_path: str):
    """Main pipeline for analyzing dataset and recommending cleaning strategies."""
    
    # Step 1: Read the dataset
    df = read_dataset(file_path)
    dataset_info = get_dataset_info(df, file_path)
    
    # Step 2: Retrieve similar cleaning strategies from past analyses (RAG)
    query = f"Dataset with {dataset_info['rows']} rows, {dataset_info['columns']} columns. Missing values: {dataset_info['missing_values']}. Duplicates: {dataset_info['duplicates']}."
    strategy_context = retrieve_strategy_context(query, k=5, max_chars=2500)
    
    if os.getenv("RAG_DEBUG") == "1":
        print("\n[RAG] strategy_context chars:", len(strategy_context))
        print("\n[RAG] strategy_context preview:\n")
        print(strategy_context[:800])
    
    # Step 3: Analyze dataset for anomalies
    analysis = analyze_dataset(dataset_info, strategy_context=strategy_context)
    
    # Step 4: Generate cleaning recommendations
    recommendations = recommend_cleaning_strategies(
        dataset_info, 
        analysis, 
        strategy_context=strategy_context
    )
    
    # Step 5: Evaluate data quality and strategies
    evaluation = evaluate_data_quality(
        dataset_info,
        analysis,
        recommendations,
        strategy_context=strategy_context
    )
    
    return {
        "overview": format_dataset_overview(dataset_info),
        "analysis": analysis,
        "recommendations": recommendations,
        "evaluation": evaluation,
        "strategy_context": strategy_context,
    }


def format_dataset_overview(info: dict) -> str:
    """Format dataset information for display."""
    return f"""File: {info['file_name']}
Rows: {info['rows']}
Columns: {info['columns']}
Memory Usage: {info['memory_usage']}

Column Names and Types:
{info['dtypes']}

Missing Values Summary:
{info['missing_values']}

Duplicate Rows: {info['duplicates']}
"""
