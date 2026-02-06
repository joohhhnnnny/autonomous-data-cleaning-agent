import os
import sys

from core.controller import clean_dataset

if __name__ == "__main__":
    file_path = input("\nEnter path to dataset (CSV or XLSX): ").strip()
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    if not file_path.lower().endswith(('.csv', '.xlsx', '.xls')):
        print("Error: File must be CSV or XLSX format.")
        sys.exit(1)
    
    print("\n[1/1] Running data cleaning analysis pipeline...")
    result = clean_dataset(file_path)

    if os.getenv("RAG_DEBUG") == "1":
        print("\n==============================")
        print("\n--- CLEANING STRATEGIES (DEBUG) ---")
        print("\n==============================")
        print((result.get("strategy_context", "") or "")[:1200])

    print("\n==============================")
    print("\n--- DATASET OVERVIEW ---")
    print("\n==============================")
    print(result["overview"])

    print("\n==============================")
    print("\n--- ANOMALY ANALYSIS ---")
    print("\n==============================")
    print(result["analysis"])

    print("\n==============================")
    print("\n--- CLEANING RECOMMENDATIONS ---")
    print("\n==============================")
    print(result["recommendations"])

    print("\n==============================")
    print("\n--- QUALITY ASSESSMENT ---")
    print("\n==============================")
    print(result["evaluation"])
