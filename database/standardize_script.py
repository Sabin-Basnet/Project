import pandas as pd
import os
import glob

# 1. Automatic Relative Path Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# This tells Python to look into the 'data' sub-folder
DATA_FOLDER = os.path.join(BASE_DIR, 'data')

# Columns to keep
COLUMNS_TO_KEEP = [
    'Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 
    'Percent Change', 'Volume', 'Turn Over'
]

def auto_standardize():
    # Find all CSV files inside the 'data' folder
    csv_pattern = os.path.join(DATA_FOLDER, "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"Error: No CSV files found in {DATA_FOLDER}")
        return

    print(f"Cleaning {len(csv_files)} files inside the 'data' folder...")

    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)
            
            # Handle naming variation
            if 'Turnover' in df.columns and 'Turn Over' not in df.columns:
                df.rename(columns={'Turnover': 'Turn Over'}, inplace=True)
            
            # Filter columns
            available_cols = [c for c in COLUMNS_TO_KEEP if c in df.columns]
            df_final = df[available_cols]
            
            # Overwrite the file in the 'data' folder
            df_final.to_csv(file_path, index=False)
            print(f"Standardized: {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"Failed to process {os.path.basename(file_path)}: {e}")

if __name__ == "__main__":
    auto_standardize()
    print("\n--- All files in 'data/' have been cleaned! ---")