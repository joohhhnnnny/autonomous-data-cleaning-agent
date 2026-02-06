# Data Cleaning Agent

An intelligent AI-powered agent that analyzes datasets, identifies data quality issues, and recommends cleaning strategies using RAG (Retrieval-Augmented Generation).

## Features

- 📊 **Automatic Dataset Analysis**: Reads CSV and XLSX files and provides comprehensive analysis
- 🔍 **Anomaly Detection**: Identifies missing values, duplicates, outliers, data type issues, and more
- 💡 **Smart Recommendations**: Provides specific, actionable data cleaning strategies with code examples
- 📚 **RAG-Enhanced**: Uses retrieval from a knowledge base of cleaning strategies for context-aware recommendations
- ✅ **Quality Assessment**: Evaluates overall data quality with detailed scoring
- 🤖 **LLM-Powered**: Leverages Ollama with Llama 3 for intelligent analysis

## How It Works

The agent follows a multi-step pipeline:

1. **Data Reading**: Loads CSV/XLSX files using pandas
2. **Dataset Profiling**: Extracts comprehensive information about structure, types, missing values, duplicates, statistics
3. **RAG Retrieval**: Searches knowledge base for relevant cleaning strategies
4. **Anomaly Analysis**: AI analyzes the dataset for quality issues
5. **Strategy Recommendation**: AI generates specific cleaning recommendations with code
6. **Quality Evaluation**: AI assesses data quality and evaluates the recommendations

## Project Structure

```
data-cleaning-agent/
├── main.py                 # Entry point - handles user input and displays results
├── agents/
│   ├── analyzer.py         # Dataset anomaly analysis agent
│   ├── rewriter.py         # Cleaning strategy recommendation agent
│   ├── evaluator.py        # Data quality evaluation agent
├── core/
│   └── controller.py       # Main pipeline controller
├── utils/
│   ├── llm.py              # LLM configuration (Ollama)
│   ├── data_reader.py      # Dataset reading and profiling utilities
│   ├── rag.py              # RAG system for strategy retrieval
│   └── postprocess.py      # LLM output post-processing
└── memory/
    ├── md/                 # Markdown knowledge base with cleaning strategies
    │   ├── missing_values_strategies.md
    │   ├── duplicate_records_strategies.md
    │   ├── outliers_anomalies_strategies.md
    │   └── data_type_corrections.md
    └── chroma/             # Vector database for RAG
```

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Ollama** with Llama 3 model installed
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3:8b
   ollama pull nomic-embed-text  # For embeddings
   ```

### Setup

1. Clone or navigate to the project directory:
   ```bash
   cd /home/johnbenedict/VSCODE/Python/data-cleaning-agent
   ```

2. Install required Python packages:
   ```bash
   pip install pandas openpyxl langchain langchain-ollama langchain-chroma chromadb scikit-learn
   ```

3. (Optional) Build the vector database:
   ```bash
   # The RAG system will auto-build on first run
   # Or force rebuild with:
   RAG_DEBUG=1 python main.py
   ```

## Usage

### Basic Usage

Run the agent:
```bash
python main.py
```

You'll be prompted to enter the path to your dataset:
```
Enter path to dataset (CSV or XLSX): /path/to/your/data.csv
```

### Example Session

```bash
$ python main.py

Enter path to dataset (CSV or XLSX): sales_data.csv

[1/1] Running data cleaning analysis pipeline...

==============================

--- DATASET OVERVIEW ---

==============================
File: sales_data.csv
Rows: 1000
Columns: 8
Memory Usage: 0.06 MB

Column Names and Types:
  order_id: int64
  customer_name: object
  order_date: object
  amount: float64
  product: object
  quantity: int64
  region: object
  is_shipped: object

Missing Values Summary:
  customer_name: 45 (4.5%)
  order_date: 12 (1.2%)
  region: 78 (7.8%)

Duplicate Rows: 23

==============================

--- ANOMALY ANALYSIS ---

==============================
[AI-generated analysis of data quality issues]

==============================

--- CLEANING RECOMMENDATIONS ---

==============================
[AI-generated specific cleaning strategies with code examples]

==============================

--- QUALITY ASSESSMENT ---

==============================
[AI-generated quality scores and evaluation]
```

### Advanced Options

Enable debug mode to see RAG retrieval details:
```bash
RAG_DEBUG=1 python main.py
```

## Supported Data Formats

- **CSV** (`.csv`) - All encodings supported (UTF-8, Latin-1, etc.)
- **Excel** (`.xlsx`, `.xls`) - All sheets readable

## Customization

### Adding New Cleaning Strategies

Add markdown files to `memory/md/` with your cleaning strategies:

```markdown
# Data Cleaning Strategy - Your Topic

## Introduction
Description of the issue...

## Detection Methods
How to identify the problem...

## Handling Strategies
Specific solutions with code examples...

## Best Practices
Guidelines and recommendations...
```

The RAG system will automatically index new files on next run.

### Changing the LLM

Edit [utils/llm.py](utils/llm.py):
```python
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3:8b", temperature=0.7)  # Change model here
```

### Tuning RAG Parameters

Edit [core/controller.py](core/controller.py):
```python
strategy_context = retrieve_strategy_context(query, k=5, max_chars=2500)
# k: number of strategy chunks to retrieve
# max_chars: maximum context length
```

## Key Components

### Data Reader (`utils/data_reader.py`)
- Reads CSV and Excel files
- Handles different encodings automatically
- Extracts comprehensive dataset information:
  - Row/column counts
  - Data types
  - Missing values with percentages
  - Duplicate counts
  - Memory usage
  - Statistical summaries
  - Sample data

### Analyzer Agent (`agents/analyzer.py`)
Analyzes datasets for:
- Missing values patterns and severity
- Duplicate records (exact and partial)
- Data type inconsistencies
- Outliers and anomalies
- Formatting issues
- Referential integrity problems
- Data range issues

### Recommendation Agent (`agents/rewriter.py`)
Generates cleaning strategies:
- Priority levels (Critical/High/Medium/Low)
- Specific methods (imputation, removal, transformation)
- Python/Pandas code snippets
- Expected impact assessment
- Risk considerations

### Evaluation Agent (`agents/evaluator.py`)
Provides quality assessment:
- Overall quality score (0-100)
- Completeness, consistency, accuracy, validity scores
- Risk assessment
- Strategy evaluation
- Impact estimation
- Next steps recommendations

### RAG System (`utils/rag.py`)
- Vector database using ChromaDB
- Embeddings with nomic-embed-text
- Retrieves relevant cleaning strategies
- Provides context for AI recommendations

## Knowledge Base

The `memory/md/` folder contains expert knowledge about data cleaning:

1. **Missing Values Strategies**: Detection, deletion, imputation methods (mean/median/mode, KNN, multiple imputation)
2. **Duplicate Records**: Exact/partial/fuzzy matching, removal strategies, conditional deduplication
3. **Outliers and Anomalies**: Statistical methods (Z-score, IQR), ML methods (Isolation Forest, LOF), handling strategies
4. **Data Type Corrections**: Type conversion, memory optimization, validation

## Requirements

```
pandas>=1.5.0
openpyxl>=3.0.0
langchain>=0.1.0
langchain-ollama>=0.1.0
langchain-chroma>=0.1.0
chromadb>=0.4.0
scikit-learn>=1.0.0
```

## Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve
```

### Memory Issues with Large Files
- Process files in chunks
- Use data type optimization
- Sample large datasets before analysis

### RAG Not Finding Strategies
```bash
# Force rebuild the vector database
RAG_DEBUG=1 python main.py
```

## Future Enhancements

- [ ] Support for more file formats (JSON, Parquet, databases)
- [ ] Automated cleaning execution
- [ ] Data profiling visualizations
- [ ] Export cleaning scripts
- [ ] Batch processing multiple files
- [ ] Interactive cleaning workflow
- [ ] Custom strategy templates
- [ ] Data lineage tracking

## Contributing

Feel free to add more cleaning strategies to `memory/md/` or enhance the agent capabilities!

## License

This project is for educational and research purposes.
