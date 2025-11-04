"""
Merge Pex Stipend Transaction CSVs

This script consolidates all fiscal year Pex transaction data into a single CSV file,
keeping only Date, Name, and Amount columns, sorted alphabetically by student name.

Input: Data/Pex Transactions - FY*.csv (5 files)
Output: Data/processed/merged_stipends.csv
"""

import pandas as pd
import glob
import os


def clean_amount(amount):
    """
    Clean amount values by removing currency formatting.
    
    Handles cases like:
    - "$12,207,474,172.00" → 12207474172.0
    - "100" → 100.0
    - "-100" → -100.0
    
    Args:
        amount: Raw amount value (str, int, float, or NaN)
    
    Returns:
        float: Cleaned numeric amount
    """
    if pd.isna(amount) or amount == '':
        return 0.0
    
    # Convert to string and remove $ and commas
    amount_str = str(amount).replace('$', '').replace(',', '').strip()
    
    try:
        return float(amount_str)
    except ValueError:
        print(f"Warning: Could not convert amount '{amount}' to float. Using 0.0")
        return 0.0


def merge_stipend_csvs():
    """
    Merge all Pex transaction CSVs from Data/ folder.
    
    Steps:
    1. Find all FY*.csv files
    2. Read each CSV
    3. Keep only Date, Name, Amount columns
    4. Clean amount formatting
    5. Merge all dataframes
    6. Sort by Name (alphabetical), then Date (chronological)
    7. Export to Data/processed/merged_stipends.csv
    """
    
    # Find all fiscal year CSV files
    csv_pattern = 'Data/Pex Transactions - FY*.csv'
    csv_files = sorted(glob.glob(csv_pattern))
    
    if not csv_files:
        print(f"Error: No CSV files found matching pattern '{csv_pattern}'")
        return
    
    print(f"Found {len(csv_files)} CSV files:")
    for file in csv_files:
        print(f"  - {file}")
    
    # Read and process each CSV
    all_dataframes = []
    
    for file in csv_files:
        print(f"\nProcessing {os.path.basename(file)}...")
        
        # Read CSV with all columns as strings initially
        df = pd.read_csv(file, encoding='utf-8', dtype=str)
        
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {list(df.columns)}")
        
        # Check if required columns exist
        required_columns = ['Date', 'Name', 'Amount']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"  Warning: Missing columns {missing_columns}. Skipping this file.")
            continue
        
        # Keep only Date, Name, Amount columns
        df = df[required_columns].copy()
        
        # Clean the Amount column
        df['Amount'] = df['Amount'].apply(clean_amount)
        
        all_dataframes.append(df)
    
    if not all_dataframes:
        print("\nError: No valid dataframes to merge.")
        return
    
    # Merge all dataframes
    print(f"\nMerging {len(all_dataframes)} dataframes...")
    merged_df = pd.concat(all_dataframes, ignore_index=True)
    
    print(f"Total rows before sorting: {len(merged_df)}")
    
    # Sort by Name (alphabetical), then by Date (chronological within each name)
    print("\nSorting by Name and Date...")
    merged_df = merged_df.sort_values(by=['Name', 'Date'], ascending=[True, True])
    merged_df = merged_df.reset_index(drop=True)
    
    # Create output directory if it doesn't exist
    output_dir = 'Data/processed'
    os.makedirs(output_dir, exist_ok=True)
    
    # Export to CSV
    output_file = os.path.join(output_dir, 'merged_stipends.csv')
    merged_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\n✓ Successfully merged {len(merged_df)} transactions")
    print(f"✓ Output saved to: {output_file}")
    
    # Display summary statistics
    print("\n--- Summary Statistics ---")
    print(f"Unique students: {merged_df['Name'].nunique()}")
    print(f"Total amount: ${merged_df['Amount'].sum():,.2f}")
    print(f"Date range: {merged_df['Date'].min()} to {merged_df['Date'].max()}")
    
    # Show first few rows
    print("\n--- First 10 rows (preview) ---")
    print(merged_df.head(10).to_string(index=False))


if __name__ == '__main__':
    merge_stipend_csvs()
