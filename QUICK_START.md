# Quick Start Guide - Data Cleaning Agent

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Install Ollama and Models
```bash
# Install Ollama from https://ollama.ai (if not installed)

# Pull required models
ollama pull llama3:8b
ollama pull nomic-embed-text
```

### Step 3: Test the Setup
```bash
python test_setup.py
```
Expected output:
```
Testing data reader...
Reading: .../sample_data.csv

✓ Successfully read dataset
  Shape: (15, 8)
✓ Successfully extracted dataset info
  Rows: 15
  Columns: 8
  Missing values: [...]
  Duplicates: 2

✓ All tests passed!
```

### Step 4: Run with Sample Data
```bash
python main.py
```
When prompted, enter:
```
sample_data.csv
```

### Step 5: Run with Your Own Data
```bash
python main.py
```
Enter the path to your CSV or XLSX file:
```
/path/to/your/dataset.csv
```

## 📊 What to Expect

The agent will provide:

1. **Dataset Overview**
   - Basic statistics
   - Column types
   - Missing values summary
   - Duplicate count

2. **Anomaly Analysis**
   - Detailed identification of all data quality issues
   - Pattern recognition
   - Severity assessment

3. **Cleaning Recommendations**
   - Prioritized strategies (Critical → Low)
   - Specific Python/Pandas code
   - Expected impact
   - Risk warnings

4. **Quality Assessment**
   - Overall score (0-100)
   - Completeness, consistency, accuracy, validity scores
   - Next steps recommendations

## 🎯 Example Issues Detected

The agent can identify:
- ❌ Missing values (nulls, empty strings)
- ❌ Duplicate records
- ❌ Invalid dates/formats
- ❌ Data type mismatches
- ❌ Outliers and anomalies
- ❌ Inconsistent formatting
- ❌ Invalid ranges

## 💡 Tips

### Debug Mode
See RAG retrieval details:
```bash
RAG_DEBUG=1 python main.py
```

### Working with Large Files
- The agent loads the entire file into memory
- For very large files (>1GB), consider sampling first
- Optimize data types to reduce memory usage

### Best Practices
1. Start with a small sample to verify behavior
2. Review recommendations before applying them
3. Keep a backup of your original data
4. Test cleaning strategies on a copy first
5. Iterate: clean, analyze, repeat until quality improves

## 🔧 Troubleshooting

### "Ollama connection error"
```bash
# Check if Ollama is running
ollama list

# If not, start it
ollama serve
```

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### "File not found"
- Use absolute paths: `/full/path/to/file.csv`
- Or relative to project root: `./data/file.csv`

### "Memory error with large file"
Consider preprocessing:
```python
import pandas as pd

# Sample 10% of rows
df = pd.read_csv('large_file.csv').sample(frac=0.1)
df.to_csv('sample.csv', index=False)
```

## 📚 Learn More

- See [README.md](README.md) for full documentation
- Check [CONVERSION_SUMMARY.md](CONVERSION_SUMMARY.md) for technical details
- Explore `memory/md/` for cleaning strategy knowledge base

## ✅ Quick Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Ollama installed and running
- [ ] Models downloaded (llama3:8b, nomic-embed-text)
- [ ] Test passed (`python test_setup.py`)
- [ ] Ready to analyze datasets! 🎉

## 🆘 Need Help?

Common issues and solutions:

**Q: Agent is slow**
A: First run builds vector database (one-time). Subsequent runs are faster.

**Q: Recommendations seem generic**
A: Add more specific strategies to `memory/md/` folder.

**Q: Wrong file format detected**
A: Ensure file extension is `.csv`, `.xlsx`, or `.xls`.

**Q: LLM gives incomplete output**
A: Increase temperature in `utils/llm.py` or try different model.

---

Happy data cleaning! 🧹📊
