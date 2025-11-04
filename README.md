Repository: Launchpad Pex Stipend Transactions

## Overview
- This repository contains 5 CSV exports of Pex transaction data from FY2022 through FY2026
- **Total data**: Student stipend transactions from the Launchpad program (Foundations, 101, Summer sessions)
- **Workflow**: Merge all fiscal year CSVs → Sort by student name → Export consolidated dataset
- One main Python script automates data processing: `merge_stipends.py`

## Architecture & Data Flow
```
Raw CSVs (5 files in Data/ folder)
    ↓
merge_stipends.py → Data/processed/merged_stipends.csv (consolidated, sorted by name)
```

## Key Files & Patterns
**Input Files** (`Data/` folder):
- `Pex Transactions - FY2022.csv` (61 lines)
- `Pex Transactions - FY2023.csv` (128 lines)
- `Pex Transactions - FY2024.csv` (56 lines)
- `Pex Transactions - FY2025.csv`
- `Pex Transactions - FY2026.csv`

**Scripts** (repository root):
- `merge_stipends.py` - Merges all fiscal year CSVs, filters columns, sorts by student name

**Output Files**:
- `Data/processed/merged_stipends.csv` - Consolidated dataset with Date, Name, Amount columns only

**CSV Header Patterns**:
- **Standard columns**: `Date`, `Name`, `Amount`
- **Excluded columns**: `Created By`, `Method`, `Funding Request`, `Program`, `Business Account Transaction ID`, `Card Funding Transaction ID`, `Request ID`, `Comments`
- **Date format**: MM/DD/YYYY HH:MM AM/PM (e.g., "04/08/2022 11:46 AM")
- **Amount format**: Numeric, may be negative for reversals (e.g., -100)
- **Name format**: First Last (e.g., "Cheyenne Dumas")

## Critical Implementation Details
**Column Selection**:
```python
# Only keep Date, Name, Amount columns
df = df[['Date', 'Name', 'Amount']]
```

**Data Cleaning** (see `clean_amount()` function):
```python
# Remove dollar signs and commas from amounts (FY2024 has formatted numbers)
# Handle: "$12,207,474,172.00" → 12207474172.00
amount_str = str(amount).replace('$', '').replace(',', '').strip()
return float(amount_str)
```

**Sorting Strategy**:
```python
# Sort by Name (alphabetical), then by Date (chronological within each name)
df = df.sort_values(by=['Name', 'Date'])
```

**CSV Parsing** (critical settings):
```python
# Use these pandas settings to handle varying column structures across years
pd.read_csv(file, encoding='utf-8', dtype=str)
```

## Developer Workflows

**Setup** (first time):
```bash
pip install pandas  # Only dependency
```

**Merge All Stipend Data**:
```bash
python merge_stipends.py
# Output: Data/processed/merged_stipends.csv (sorted by student name)
```

**Inspect Headers Quickly**:
```bash
# Bash/Git Bash
head -n 1 Data/"Pex Transactions - FY2022.csv"

# PowerShell
Get-Content "Data\Pex Transactions - FY2022.csv" -TotalCount 1
```

**View Sample Output**:
```bash
# Bash/Git Bash
head -n 20 Data/processed/merged_stipends.csv

# PowerShell
Get-Content Data\processed\merged_stipends.csv -TotalCount 20
```

## Conventions & Gotchas
- **Fiscal year numbering** - Files span FY2022-FY2026; check date ranges for actual chronology
- **Amount formatting varies** - FY2024+ may have dollar signs and commas (e.g., "$12,207,474,172.00")
- **Negative amounts** - Represent reversals/refunds (e.g., automatic fund transfers)
- **Column variations** - FY2022 has `Request ID` and `Comments`; FY2023 may lack them
- **Date sorting within names** - All transactions for one student grouped together chronologically
- **Preserve original CSVs** - Never modify raw data in `Data/` folder; write outputs to `Data/processed/`

## Code Pattern Examples

**Read all fiscal year files**:
```python
import glob
csv_files = glob.glob('Data/Pex Transactions - FY*.csv')
# Returns: ['Data/Pex Transactions - FY2022.csv', 'Data/Pex Transactions - FY2023.csv', ...]
```

**Clean formatted currency values**:
```python
def clean_amount(amount):
    """Remove $ and commas, convert to float"""
    if pd.isna(amount) or amount == '':
        return 0.0
    amount_str = str(amount).replace('$', '').replace(',', '').strip()
    return float(amount_str)

df['Amount'] = df['Amount'].apply(clean_amount)
```

**Sort by name then date**:
```python
# Group all transactions per student, ordered chronologically
df = df.sort_values(by=['Name', 'Date'], ascending=[True, True])
df = df.reset_index(drop=True)
```

## When to Ask the User
- If analysis requires additional columns (e.g., Program, Method)
- If date range filtering is needed (e.g., only FY2024-2025)
- If output format needs to change (e.g., JSON, Excel)
- If amount aggregation per student is desired

## Quality Checks
After running the script, verify:
- `merged_stipends.csv` contains data from all 5 fiscal years
- Output has exactly 3 columns: Date, Name, Amount
- Data is sorted alphabetically by Name (all "Bryan Gunawan" entries together, all "Cheyenne Dumas" entries together, etc.)
- Amounts are clean numeric values (no $ or commas)
- No excluded columns appear (Created By, Comments, etc.)

## Example Output Structure
```csv
Date,Name,Amount
07/25/2023 11:50 AM,Bryan Gunawan,165.0
10/13/2023 10:55 AM,Bryan Gunawan,165.0
04/08/2022 11:46 AM,Cheyenne Dumas,50.0
05/27/2022 10:10 AM,Cheyenne Dumas,100.0
```
