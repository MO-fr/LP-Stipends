# Python Script Walkthrough: `merge_stipends.py`

This document provides a detailed explanation of how the `merge_stipends.py` script works, step by step.

---

## 📋 Table of Contents
1. [Script Purpose](#script-purpose)
2. [Imports and Dependencies](#imports-and-dependencies)
3. [Function: `clean_amount()`](#function-clean_amount)
4. [Function: `merge_stipend_csvs()`](#function-merge_stipend_csvs)
5. [Execution Flow](#execution-flow)
6. [Example Output](#example-output)

---

## Script Purpose

The script consolidates 5 fiscal year CSV files containing Pex transaction data into a single CSV file:
- **Input**: `Data/Pex Transactions - FY2022.csv` through `FY2026.csv`
- **Output**: `Data/processed/merged_stipends.csv`
- **Key Operations**: 
  - Keep only Date, Name, Amount columns
  - Clean currency formatting (remove `$` and commas)
  - Sort alphabetically by student name, then chronologically by date

---

## Imports and Dependencies

```python
import pandas as pd
import glob
import os
```

**What each import does:**

| Import | Purpose |
|--------|---------|
| `pandas` | Data manipulation library - reads CSVs, filters columns, sorts data |
| `glob` | File pattern matching - finds all files matching `FY*.csv` pattern |
| `os` | Operating system interface - creates directories, handles file paths |

**Installation required:**
```bash
pip install pandas
```

---

## Function: `clean_amount()`

### Purpose
Converts raw amount values into clean numeric floats, handling various formats.

### Code Breakdown

```python
def clean_amount(amount):
    """
    Clean amount values by removing currency formatting.
    
    Handles cases like:
    - "$12,207,474,172.00" → 12207474172.0
    - "100" → 100.0
    - "-100" → -100.0
    """
```

**Step 1: Handle empty/null values**
```python
if pd.isna(amount) or amount == '':
    return 0.0
```
- If the cell is empty or NaN (Not a Number), return `0.0`
- Prevents errors when processing missing data

**Step 2: Remove currency symbols and commas**
```python
amount_str = str(amount).replace('$', '').replace(',', '').strip()
```
- Convert to string (in case it's already a number)
- Remove all `$` symbols: `"$12,207.00"` → `"12,207.00"`
- Remove all commas: `"12,207.00"` → `"12207.00"`
- Strip whitespace: `" 100 "` → `"100"`

**Step 3: Convert to float with error handling**
```python
try:
    return float(amount_str)
except ValueError:
    print(f"Warning: Could not convert amount '{amount}' to float. Using 0.0")
    return 0.0
```
- Try to convert string to float: `"100"` → `100.0`
- If conversion fails (e.g., `"abc"`), print warning and return `0.0`
- Prevents script from crashing on bad data

### Examples

| Input | Output |
|-------|--------|
| `"$12,207,474,172.00"` | `12207474172.0` |
| `"100"` | `100.0` |
| `"-100"` | `-100.0` |
| `""` (empty) | `0.0` |
| `NaN` | `0.0` |
| `"invalid"` | `0.0` (with warning) |

---

## Function: `merge_stipend_csvs()`

This is the main function that performs the entire merge operation.

### Step 1: Find All CSV Files

```python
csv_pattern = 'Data/Pex Transactions - FY*.csv'
csv_files = sorted(glob.glob(csv_pattern))
```

**What happens:**
- `glob.glob()` searches for files matching the pattern
- `*` is a wildcard that matches anything (e.g., `2022`, `2023`, etc.)
- `sorted()` ensures files are processed in order (FY2022, FY2023, ...)
- Result: `['Data/Pex Transactions - FY2022.csv', 'Data/Pex Transactions - FY2023.csv', ...]`

**Error handling:**
```python
if not csv_files:
    print(f"Error: No CSV files found matching pattern '{csv_pattern}'")
    return
```
- If no files found, print error and exit
- Prevents processing empty list

### Step 2: Process Each CSV File

```python
all_dataframes = []

for file in csv_files:
    print(f"\nProcessing {os.path.basename(file)}...")
```

**What happens:**
- Create empty list to store dataframes
- Loop through each file
- `os.path.basename()` extracts just the filename (not full path)

**Read the CSV:**
```python
df = pd.read_csv(file, encoding='utf-8', dtype=str)
```
- `encoding='utf-8'`: Handle special characters (accents, etc.)
- `dtype=str`: Read all columns as strings initially (prevents auto-conversion issues)
- Creates a pandas DataFrame (table structure)

**Display file info:**
```python
print(f"  Rows: {len(df)}")
print(f"  Columns: {list(df.columns)}")
```
- Shows how many rows and what columns exist
- Helpful for debugging

**Validate required columns:**
```python
required_columns = ['Date', 'Name', 'Amount']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    print(f"  Warning: Missing columns {missing_columns}. Skipping this file.")
    continue
```
- Check if Date, Name, Amount columns exist
- If any are missing, skip this file and continue to next
- List comprehension: `[col for col in ... if ...]` creates filtered list

**Keep only required columns:**
```python
df = df[required_columns].copy()
```
- Filter dataframe to only keep Date, Name, Amount
- `.copy()` creates independent copy (prevents modification warnings)
- Discards: Created By, Method, Comments, etc.

**Clean the amounts:**
```python
df['Amount'] = df['Amount'].apply(clean_amount)
```
- `.apply()` runs `clean_amount()` function on every value in Amount column
- Converts `["$100", "$200"]` → `[100.0, 200.0]`

**Add to list:**
```python
all_dataframes.append(df)
```
- Add processed dataframe to our collection
- Will merge all later

### Step 3: Merge All Dataframes

```python
if not all_dataframes:
    print("\nError: No valid dataframes to merge.")
    return
```
- Safety check: if no valid files were processed, exit

**Concatenate (stack) all dataframes:**
```python
merged_df = pd.concat(all_dataframes, ignore_index=True)
```
- `pd.concat()`: Stacks dataframes vertically (row by row)
- `ignore_index=True`: Renumber rows from 0 to N (don't keep original row numbers)

**Visual representation:**
```
FY2022 DataFrame (60 rows)
+
FY2023 DataFrame (127 rows)  
+
FY2024 DataFrame (55 rows)
+
FY2025 DataFrame (29 rows)
+
FY2026 DataFrame (7 rows)
=
Merged DataFrame (278 rows)
```

### Step 4: Sort the Data

```python
merged_df = merged_df.sort_values(by=['Name', 'Date'], ascending=[True, True])
merged_df = merged_df.reset_index(drop=True)
```

**Sorting logic:**
- Primary sort: `Name` (alphabetical, A→Z)
- Secondary sort: `Date` (chronological within each name)
- `ascending=[True, True]`: Both in ascending order

**Example result:**
```
Ahmed Shamsid-Deen, 01/25/2023
Ahmed Shamsid-Deen, 02/21/2023
Ahmed Shamsid-Deen, 03/22/2023
Amiet Cruz, 02/02/2023
Amiet Cruz, 02/21/2023
Bryan Gunawan, 07/25/2023
Bryan Gunawan, 10/13/2023
```

**Reset index:**
- `reset_index(drop=True)`: Renumber rows 0, 1, 2, 3...
- `drop=True`: Don't keep old index as a new column

### Step 5: Export to CSV

**Create output directory:**
```python
output_dir = 'Data/processed'
os.makedirs(output_dir, exist_ok=True)
```
- `os.makedirs()`: Creates directory (and parent directories if needed)
- `exist_ok=True`: Don't error if directory already exists

**Write CSV file:**
```python
output_file = os.path.join(output_dir, 'merged_stipends.csv')
merged_df.to_csv(output_file, index=False, encoding='utf-8')
```
- `os.path.join()`: Safely combine path parts (handles Windows/Mac/Linux differences)
- `index=False`: Don't write row numbers as first column
- `encoding='utf-8'`: Save with UTF-8 encoding (handles special characters)

### Step 6: Display Summary Statistics

```python
print(f"\n✓ Successfully merged {len(merged_df)} transactions")
print(f"✓ Output saved to: {output_file}")

print("\n--- Summary Statistics ---")
print(f"Unique students: {merged_df['Name'].nunique()}")
print(f"Total amount: ${merged_df['Amount'].sum():,.2f}")
print(f"Date range: {merged_df['Date'].min()} to {merged_df['Date'].max()}")
```

**What each line does:**
- `len(merged_df)`: Total number of rows (transactions)
- `.nunique()`: Count unique values (how many different students)
- `.sum()`: Add all amounts together
- `:,.2f`: Format number with commas and 2 decimal places (`34006.50` → `34,006.50`)
- `.min()` / `.max()`: Earliest and latest dates

**Preview data:**
```python
print("\n--- First 10 rows (preview) ---")
print(merged_df.head(10).to_string(index=False))
```
- `.head(10)`: Get first 10 rows
- `.to_string(index=False)`: Convert to formatted text without row numbers

---

## Execution Flow

### Visual Flowchart

```
START
  ↓
Find all FY*.csv files (glob)
  ↓
Loop through each CSV file
  ↓
  ├─→ Read CSV (pandas)
  ├─→ Check for Date, Name, Amount columns
  ├─→ Keep only those 3 columns
  ├─→ Clean Amount column (remove $ and commas)
  └─→ Add to list of dataframes
  ↓
Merge all dataframes (vertical stack)
  ↓
Sort by Name (A→Z), then Date (chronological)
  ↓
Create Data/processed/ directory
  ↓
Export to merged_stipends.csv
  ↓
Display summary statistics
  ↓
END
```

### Code Execution Order

```python
if __name__ == '__main__':
    merge_stipend_csvs()
```

**What this does:**
- `if __name__ == '__main__'`: Only run if script is executed directly (not imported)
- Calls the `merge_stipend_csvs()` function to start processing

---

## Example Output

### Console Output

```
Found 5 CSV files:
  - Data\Pex Transactions - FY2022.csv
  - Data\Pex Transactions - FY2023.csv
  - Data\Pex Transactions - FY2024.csv
  - Data\Pex Transactions - FY2025.csv
  - Data\Pex Transactions - FY2026.csv

Processing Pex Transactions - FY2022.csv...
  Rows: 60
  Columns: ['Date', 'Name', 'Amount', 'Created By', 'Method', ...]

Processing Pex Transactions - FY2023.csv...
  Rows: 127
  Columns: ['Date', 'Name', 'Amount', 'Created By', 'Method', ...]

[... continues for all files ...]

Merging 5 dataframes...
Total rows before sorting: 278

Sorting by Name and Date...

✓ Successfully merged 278 transactions
✓ Output saved to: Data/processed\merged_stipends.csv

--- Summary Statistics ---
Unique students: 58
Total amount: $34,006.50
Date range: 01/05/2024 8:54 AM to 12/22/2024 12:08 PM

--- First 10 rows (preview) ---
               Date                        Name  Amount
 01/25/2023 17:02PM          Ahmed Shamsid-Deen   75.00
 02/21/2023 18:58PM          Ahmed Shamsid-Deen   75.00
03/22/2023 12:19 AM          Ahmed Shamsid-Deen   75.00
 ...
```

### Output CSV Structure

**File: `Data/processed/merged_stipends.csv`**

```csv
Date,Name,Amount
01/25/2023 17:02PM,Ahmed Shamsid-Deen,75.0
02/21/2023 18:58PM,Ahmed Shamsid-Deen,75.0
03/22/2023 12:19 AM,Ahmed Shamsid-Deen,75.0
05/01/2023 2:34 AM,Ahmed Shamsid-Deen,-0.29
02/02/2023 16:48PM,Amiet Cruz,75.0
02/21/2023 18:59PM,Amiet Cruz,75.0
07/25/2023 11:50 AM,Bryan Gunawan,165.0
10/13/2023 10:55 AM,Bryan Gunawan,165.0
...
```

**Key characteristics:**
- 3 columns only: Date, Name, Amount
- Sorted by Name (alphabetically)
- Within each name, sorted by Date (chronologically)
- All amounts are clean numbers (no $ or commas)
- 278 total transaction rows
- 58 unique students

---

## Key Programming Concepts Used

### 1. **List Comprehension**
```python
missing_columns = [col for col in required_columns if col not in df.columns]
```
Compact way to filter a list based on a condition.

### 2. **Exception Handling**
```python
try:
    return float(amount_str)
except ValueError:
    return 0.0
```
Gracefully handle errors without crashing.

### 3. **Method Chaining**
```python
merged_df = merged_df.sort_values(...).reset_index(...)
```
Call multiple methods in sequence.

### 4. **Lambda Functions (Implicit)**
```python
df['Amount'].apply(clean_amount)
```
Apply function to each element in a column.

### 5. **File Globbing**
```python
glob.glob('Data/Pex Transactions - FY*.csv')
```
Pattern matching to find files.

### 6. **Pandas Operations**
- `read_csv()`: Read CSV into DataFrame
- `concat()`: Combine multiple DataFrames
- `sort_values()`: Sort by column(s)
- `to_csv()`: Write DataFrame to CSV

---

## Common Questions

### Q: Why use `dtype=str` when reading CSVs?
**A:** Prevents pandas from auto-converting values incorrectly. For example, `"$12,207,474,172.00"` might be read as text initially, which we handle manually with `clean_amount()`.

### Q: What if a file has different column names?
**A:** The script checks for required columns and skips files that don't have Date, Name, and Amount.

### Q: Why `ignore_index=True` in concat?
**A:** Without it, you'd have duplicate row numbers (e.g., five row #1's from each file). This renumbers everything sequentially.

### Q: What if there are duplicate transactions?
**A:** The script doesn't remove duplicates—it keeps all rows. This is intentional since the same student might receive multiple stipends.

### Q: Can I sort by amount instead of name?
**A:** Yes! Change this line:
```python
merged_df = merged_df.sort_values(by=['Amount', 'Name'], ascending=[False, True])
```
This would sort by amount (highest first), then by name.

---

## Extending the Script

### Add a Column Filter
To keep additional columns (e.g., Program):
```python
required_columns = ['Date', 'Name', 'Amount', 'Program']
```

### Add Date Filtering
To only keep transactions from 2024:
```python
merged_df['Year'] = pd.to_datetime(merged_df['Date']).dt.year
merged_df = merged_df[merged_df['Year'] == 2024]
```

### Export to Excel Instead
```python
merged_df.to_excel('Data/processed/merged_stipends.xlsx', index=False)
```

### Add Student Totals
```python
student_totals = merged_df.groupby('Name')['Amount'].sum().reset_index()
print(student_totals)
```

---

## Summary

The `merge_stipends.py` script:
1. ✅ Finds all fiscal year CSV files using glob patterns
2. ✅ Reads each CSV with pandas
3. ✅ Filters to keep only Date, Name, Amount columns
4. ✅ Cleans currency formatting from amounts
5. ✅ Merges all data into one DataFrame
6. ✅ Sorts alphabetically by name, then chronologically by date
7. ✅ Exports to `Data/processed/merged_stipends.csv`
8. ✅ Displays helpful statistics and preview

**Result:** One clean, consolidated CSV with 278 transactions from 58 students across 5 fiscal years! 🎉
