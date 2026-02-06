"""Quick test script to verify the data cleaning agent setup."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.data_reader import read_dataset, get_dataset_info

def test_data_reader():
    """Test the data reader with sample data."""
    sample_file = Path(__file__).parent / "sample_data.csv"
    
    if not sample_file.exists():
        print(f"Error: {sample_file} not found")
        return False
    
    print("Testing data reader...")
    print(f"Reading: {sample_file}\n")
    
    try:
        # Read dataset
        df = read_dataset(str(sample_file))
        print(f"✓ Successfully read dataset")
        print(f"  Shape: {df.shape}")
        
        # Get dataset info
        info = get_dataset_info(df, str(sample_file))
        print(f"✓ Successfully extracted dataset info")
        print(f"  Rows: {info['rows']}")
        print(f"  Columns: {info['columns']}")
        print(f"  Missing values: {info['missing_values']}")
        print(f"  Duplicates: {info['duplicates']}")
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_reader()
    sys.exit(0 if success else 1)
